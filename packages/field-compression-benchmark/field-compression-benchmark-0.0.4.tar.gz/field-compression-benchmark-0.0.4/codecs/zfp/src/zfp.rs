#![allow(unsafe_code)] // FFI

use std::marker::PhantomData;

#[derive(Clone, serde::Serialize, serde::Deserialize)]
#[serde(tag = "mode")]
#[serde(deny_unknown_fields)]
pub enum ZfpCompressionMode {
    #[serde(rename = "expert")]
    Expert {
        min_bits: u32,
        max_bits: u32,
        max_prec: u32,
        min_exp: i32,
    },
    #[serde(rename = "fixed-rate")]
    FixedRate { rate: f64 },
    #[serde(rename = "fixed-precision")]
    FixedPrecision { precision: u32 },
    #[serde(rename = "fixed-accuracy")]
    FixedAccuracy { tolerance: f64 },
    #[serde(rename = "reversible")]
    Reversible,
}

pub trait ZfpCompressible: Copy {
    const Z_TYPE: zfp_sys::zfp_type;
    const TY: codecs_core::BufferTy;

    const ZERO: Self;
}

impl ZfpCompressible for i32 {
    const TY: codecs_core::BufferTy = codecs_core::BufferTy::I32;
    const ZERO: Self = 0_i32;
    const Z_TYPE: zfp_sys::zfp_type = zfp_sys::zfp_type_zfp_type_int32;
}

impl ZfpCompressible for i64 {
    const TY: codecs_core::BufferTy = codecs_core::BufferTy::I64;
    const ZERO: Self = 0_i64;
    const Z_TYPE: zfp_sys::zfp_type = zfp_sys::zfp_type_zfp_type_int64;
}

impl ZfpCompressible for f32 {
    const TY: codecs_core::BufferTy = codecs_core::BufferTy::F32;
    const ZERO: Self = 0.0_f32;
    const Z_TYPE: zfp_sys::zfp_type = zfp_sys::zfp_type_zfp_type_float;
}

impl ZfpCompressible for f64 {
    const TY: codecs_core::BufferTy = codecs_core::BufferTy::F64;
    const ZERO: Self = 0.0_f64;
    const Z_TYPE: zfp_sys::zfp_type = zfp_sys::zfp_type_zfp_type_double;
}

pub struct ZfpField<T: ZfpCompressible> {
    field: *mut zfp_sys::zfp_field,
    dims: u32,
    _marker: PhantomData<T>,
}

impl<T: ZfpCompressible> ZfpField<T> {
    pub fn new(data: &[T], shape: &[usize]) -> Result<Self, String> {
        let pointer = data.as_ptr().cast::<std::ffi::c_void>().cast_mut();

        let (field, dims) = match shape {
            [nx] => unsafe {
                let field = zfp_sys::zfp_field_1d(pointer, T::Z_TYPE, *nx);
                zfp_sys::zfp_field_set_stride_1d(field, 1);
                (field, 1)
            },
            [ny, nx] => unsafe {
                let field = zfp_sys::zfp_field_2d(pointer, T::Z_TYPE, *nx, *ny);
                let sy =
                    isize::try_from(*nx).map_err(|err| format!("invalid 2d stride sy: {err}"))?;
                zfp_sys::zfp_field_set_stride_2d(field, 1, sy);
                (field, 2)
            },
            [nz, ny, nx] => unsafe {
                let field = zfp_sys::zfp_field_3d(pointer, T::Z_TYPE, *nx, *ny, *nz);
                let sy =
                    isize::try_from(*nx).map_err(|err| format!("invalid 3d stride sy: {err}"))?;
                let sz = nx
                    .checked_mul(*ny)
                    .ok_or_else(|| String::from("invalid 3d stride sz: exceeds usize"))
                    .and_then(|sz| {
                        isize::try_from(sz).map_err(|err| format!("invalid 3d stride sz: {err}"))
                    })?;
                zfp_sys::zfp_field_set_stride_3d(field, 1, sy, sz);
                (field, 3)
            },
            [nw, nz, ny, nx] => unsafe {
                let field = zfp_sys::zfp_field_4d(pointer, T::Z_TYPE, *nx, *ny, *nz, *nw);
                let sy =
                    isize::try_from(*nx).map_err(|err| format!("invalid 4d stride sy: {err}"))?;
                let sz = nx
                    .checked_mul(*ny)
                    .ok_or_else(|| String::from("invalid 4d stride sz: exceeds usize"))
                    .and_then(|sz| {
                        isize::try_from(sz).map_err(|err| format!("invalid 4d stride sz: {err}"))
                    })?;
                let sw = nx
                    .checked_mul(*ny)
                    .and_then(|s| s.checked_mul(*nz))
                    .ok_or_else(|| String::from("invalid 4d stride sw: exceeds usize"))
                    .and_then(|sz| {
                        isize::try_from(sz).map_err(|err| format!("invalid 4d stride sw: {err}"))
                    })?;
                zfp_sys::zfp_field_set_stride_4d(field, 1, sy, sz, sw);
                (field, 4)
            },
            shape => {
                return Err(format!(
                    "Zfp only supports 1-4-dimensional data, found {shape:?}"
                ))
            },
        };

        Ok(Self {
            field,
            dims,
            _marker: PhantomData::<T>,
        })
    }
}

impl<T: ZfpCompressible> Drop for ZfpField<T> {
    fn drop(&mut self) {
        unsafe { zfp_sys::zfp_field_free(self.field) };
    }
}

pub struct ZfpCompressionStream<T: ZfpCompressible> {
    stream: *mut zfp_sys::zfp_stream,
    _marker: PhantomData<T>,
}

impl<T: ZfpCompressible> ZfpCompressionStream<T> {
    pub fn new(field: &ZfpField<T>, mode: &ZfpCompressionMode) -> Result<Self, String> {
        let stream = unsafe { zfp_sys::zfp_stream_open(std::ptr::null_mut()) };
        let stream = Self {
            stream,
            _marker: PhantomData::<T>,
        };

        match mode {
            ZfpCompressionMode::Expert {
                min_bits,
                max_bits,
                max_prec,
                min_exp,
            } => {
                #[allow(clippy::cast_possible_wrap)]
                const ZFP_TRUE: zfp_sys::zfp_bool = zfp_sys::zfp_true as zfp_sys::zfp_bool;

                if unsafe {
                    zfp_sys::zfp_stream_set_params(
                        stream.stream,
                        *min_bits,
                        *max_bits,
                        *max_prec,
                        *min_exp,
                    )
                } != ZFP_TRUE
                {
                    return Err(String::from("invalid expert mode parameters"));
                }
            },
            ZfpCompressionMode::FixedRate { rate } => {
                let _actual_rate: f64 = unsafe {
                    zfp_sys::zfp_stream_set_rate(stream.stream, *rate, T::Z_TYPE, field.dims, 0)
                };
            },
            ZfpCompressionMode::FixedPrecision { precision } => {
                let _actual_precision: u32 =
                    unsafe { zfp_sys::zfp_stream_set_precision(stream.stream, *precision) };
            },
            ZfpCompressionMode::FixedAccuracy { tolerance } => {
                let _actual_tolerance: f64 =
                    unsafe { zfp_sys::zfp_stream_set_accuracy(stream.stream, *tolerance) };
            },
            ZfpCompressionMode::Reversible => {
                #[allow(clippy::let_unit_value)] // Enforce unit return type
                let () = unsafe { zfp_sys::zfp_stream_set_reversible(stream.stream) };
            },
        }

        Ok(stream)
    }

    #[must_use]
    pub fn with_bitstream(self, field: ZfpField<T>) -> ZfpCompressionStreamWithBitstream<T> {
        let this = std::mem::ManuallyDrop::new(self);
        let field = std::mem::ManuallyDrop::new(field);

        let capacity = unsafe { zfp_sys::zfp_stream_maximum_size(this.stream, field.field) };
        let mut buffer = vec![0_u8; capacity];

        let bitstream = unsafe { zfp_sys::stream_open(buffer.as_mut_ptr().cast(), buffer.len()) };

        unsafe { zfp_sys::zfp_stream_set_bit_stream(this.stream, bitstream) };
        unsafe { zfp_sys::zfp_stream_rewind(this.stream) };

        ZfpCompressionStreamWithBitstream {
            stream: this.stream,
            bitstream,
            field: field.field,
            buffer,
            _marker: PhantomData::<T>,
        }
    }
}

impl<T: ZfpCompressible> Drop for ZfpCompressionStream<T> {
    fn drop(&mut self) {
        unsafe { zfp_sys::zfp_stream_close(self.stream) };
    }
}

pub struct ZfpCompressionStreamWithBitstream<T: ZfpCompressible> {
    stream: *mut zfp_sys::zfp_stream,
    bitstream: *mut zfp_sys::bitstream,
    field: *mut zfp_sys::zfp_field,
    buffer: Vec<u8>,
    _marker: PhantomData<T>,
}

impl<T: ZfpCompressible> ZfpCompressionStreamWithBitstream<T> {
    pub fn write_full_header(
        self,
    ) -> Result<ZfpCompressionStreamWithBitstreamWithHeader<T>, String> {
        if unsafe { zfp_sys::zfp_write_header(self.stream, self.field, zfp_sys::ZFP_HEADER_FULL) }
            == 0
        {
            return Err(String::from(
                "Zfp failed to write the full header to the stream",
            ));
        }

        let mut this = std::mem::ManuallyDrop::new(self);

        Ok(ZfpCompressionStreamWithBitstreamWithHeader {
            stream: this.stream,
            bitstream: this.bitstream,
            field: this.field,
            buffer: std::mem::take(&mut this.buffer),
            _marker: PhantomData::<T>,
        })
    }
}

impl<T: ZfpCompressible> Drop for ZfpCompressionStreamWithBitstream<T> {
    fn drop(&mut self) {
        unsafe { zfp_sys::zfp_field_free(self.field) };
        unsafe { zfp_sys::zfp_stream_close(self.stream) };
        unsafe { zfp_sys::stream_close(self.bitstream) };
    }
}

pub struct ZfpCompressionStreamWithBitstreamWithHeader<T: ZfpCompressible> {
    stream: *mut zfp_sys::zfp_stream,
    bitstream: *mut zfp_sys::bitstream,
    field: *mut zfp_sys::zfp_field,
    buffer: Vec<u8>,
    _marker: PhantomData<T>,
}

impl<T: ZfpCompressible> ZfpCompressionStreamWithBitstreamWithHeader<T> {
    pub fn compress(mut self) -> Result<Vec<u8>, String> {
        let compressed_size = unsafe { zfp_sys::zfp_compress(self.stream, self.field) };

        if compressed_size == 0 {
            return Err(String::from("Zfp failed to compress to the stream"));
        }

        let mut compressed = std::mem::take(&mut self.buffer);
        compressed.truncate(compressed_size);

        Ok(compressed)
    }
}

impl<T: ZfpCompressible> Drop for ZfpCompressionStreamWithBitstreamWithHeader<T> {
    fn drop(&mut self) {
        unsafe { zfp_sys::zfp_field_free(self.field) };
        unsafe { zfp_sys::zfp_stream_close(self.stream) };
        unsafe { zfp_sys::stream_close(self.bitstream) };
    }
}

pub struct ZfpDecompressionStream<'a> {
    stream: *mut zfp_sys::zfp_stream,
    bitstream: *mut zfp_sys::bitstream,
    data: &'a [u8],
}

impl<'a> ZfpDecompressionStream<'a> {
    #[must_use]
    pub fn new(data: &'a [u8]) -> Self {
        let bitstream = unsafe {
            zfp_sys::stream_open(
                data.as_ptr().cast::<std::ffi::c_void>().cast_mut(),
                data.len(),
            )
        };

        let stream = unsafe { zfp_sys::zfp_stream_open(bitstream) };

        Self {
            stream,
            bitstream,
            data,
        }
    }

    pub fn read_full_header(self) -> Result<ZfpDecompressionStreamWithHeader<'a>, String> {
        let this = std::mem::ManuallyDrop::new(self);

        let field = unsafe { zfp_sys::zfp_field_alloc() };

        let stream = ZfpDecompressionStreamWithHeader {
            stream: this.stream,
            bitstream: this.bitstream,
            field,
            _data: this.data,
        };

        if unsafe { zfp_sys::zfp_read_header(this.stream, field, zfp_sys::ZFP_HEADER_FULL) } == 0 {
            return Err(String::from(
                "Zfp failed to read the required decompression header",
            ));
        }

        Ok(stream)
    }
}

impl<'a> Drop for ZfpDecompressionStream<'a> {
    fn drop(&mut self) {
        unsafe { zfp_sys::zfp_stream_close(self.stream) };
        unsafe { zfp_sys::stream_close(self.bitstream) };
    }
}

pub struct ZfpDecompressionStreamWithHeader<'a> {
    stream: *mut zfp_sys::zfp_stream,
    bitstream: *mut zfp_sys::bitstream,
    field: *mut zfp_sys::zfp_field,
    _data: &'a [u8],
}

impl<'a> ZfpDecompressionStreamWithHeader<'a> {
    pub fn decompress(self) -> Result<(codecs_core::BufferVec, Vec<usize>), String> {
        let field_type = match unsafe { (*self.field).type_ } {
            zfp_sys::zfp_type_zfp_type_int32 => codecs_core::BufferTy::I32,
            zfp_sys::zfp_type_zfp_type_int64 => codecs_core::BufferTy::I64,
            zfp_sys::zfp_type_zfp_type_float => codecs_core::BufferTy::F32,
            zfp_sys::zfp_type_zfp_type_double => codecs_core::BufferTy::F64,
            ty => return Err(format!("Zfp decompression found an unknown dtype #{ty}",)),
        };

        let shape = vec![
            unsafe { (*self.field).nw },
            unsafe { (*self.field).nz },
            unsafe { (*self.field).ny },
            unsafe { (*self.field).nx },
        ]
        .into_iter()
        .filter(|s| *s > 0)
        .collect::<Vec<usize>>();

        let mut decompressed =
            codecs_core::BufferVec::zeros_with_ty_len(field_type, shape.iter().product());

        unsafe {
            zfp_sys::zfp_field_set_pointer(
                self.field,
                decompressed
                    .as_slice_mut()
                    .as_bytes_mut()
                    .as_mut_ptr()
                    .cast(),
            );
        }

        if unsafe { zfp_sys::zfp_decompress(self.stream, self.field) } == 0 {
            return Err(String::from("Zfp decompression failed"));
        }

        Ok((decompressed, shape))
    }
}

impl<'a> Drop for ZfpDecompressionStreamWithHeader<'a> {
    fn drop(&mut self) {
        unsafe { zfp_sys::zfp_field_free(self.field) };
        unsafe { zfp_sys::zfp_stream_close(self.stream) };
        unsafe { zfp_sys::stream_close(self.bitstream) };
    }
}
