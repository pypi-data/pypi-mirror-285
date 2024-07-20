#![allow(clippy::missing_errors_doc)]
#![cfg_attr(not(test), no_main)]

pub mod zfp;

pub fn compress<T: zfp::ZfpCompressible>(
    data: &[T],
    shape: &[usize],
    mode: &zfp::ZfpCompressionMode,
) -> Result<Vec<u8>, String> {
    // Setup zfp structs to begin compression
    let field = zfp::ZfpField::new(data, shape)?;
    let stream = zfp::ZfpCompressionStream::new(&field, mode)?;

    // Allocate space based on the maximum size potentially required by zfp to
    //  store the compressed array
    let stream = stream.with_bitstream(field);

    // Write the full header so we can reconstruct the array on decompression
    let stream = stream.write_full_header()?;

    // Compress the field into the allocated output array
    stream.compress()
}

pub fn decompress(data: &[u8]) -> Result<(codecs_core::BufferVec, Vec<usize>), String> {
    // Setup zfp structs to begin decompression
    let stream = zfp::ZfpDecompressionStream::new(data);

    // Read the full header to verify the decompression dtype
    let stream = stream.read_full_header()?;

    // Decompress the field into a newly allocated output array
    stream.decompress()
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ZfpCodec {
    #[serde(flatten)]
    mode: zfp::ZfpCompressionMode,
}

impl codecs_core::Codec for ZfpCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "zfp";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        if matches!(
            buf.ty(),
            codecs_core::BufferTy::I32 | codecs_core::BufferTy::I64
        ) && matches!(
            self.mode,
            zfp::ZfpCompressionMode::FixedAccuracy { tolerance: _ }
        ) {
            return Err(String::from(
                "Zfp's fixed accuracy mode is not supported for integer data",
            ));
        }

        let encoded = match buf {
            codecs_core::BufferSlice::I32(data) => compress(data, shape, &self.mode)?,
            codecs_core::BufferSlice::I64(data) => compress(data, shape, &self.mode)?,
            codecs_core::BufferSlice::F32(data) => compress(data, shape, &self.mode)?,
            codecs_core::BufferSlice::F64(data) => compress(data, shape, &self.mode)?,
            buf => {
                return Err(format!(
                    "Zfp::encode does not support the buffer dtype `{}`",
                    buf.ty(),
                ))
            },
        };

        Ok(codecs_core::ShapedBuffer {
            shape: vec![encoded.len()],
            buffer: codecs_core::BufferVec::U8(encoded),
        })
    }

    fn decode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::DecodedBuffer>, String> {
        if !matches!(shape, [_]) {
            return Err(format!(
                "Zfp::decode buffer shape {shape:?} is not one-dimensional"
            ));
        }

        let codecs_core::BufferSlice::U8(data) = buf else {
            return Err(format!(
                "Zfp::decode expects buffer dtype `{}` but found `{}`",
                codecs_core::BufferTy::U8,
                buf.ty()
            ));
        };

        let (decoded, shape) = decompress(data)?;

        Ok(codecs_core::ShapedBuffer {
            shape,
            buffer: decoded,
        })
    }

    fn get_config<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serde::Serialize::serialize(&self, serializer)
    }
}

codecs_core_wasm::export_codec! {
    /// Codec providing compression using ZFP.
    ///
    /// Args:
    ///     mode (Literal[
    ///         "expert", "fixed-rate", "fixed-precision",
    ///         "fixed-accuracy", "reversible",
    ///     ]): ZFP compression mode.
    ///     min_bits (int, optional): minimum number of compressed
    ///         bits used to represent a block in expert mode.
    ///     max_bits (int, optional): maximum number of bits used
    ///         to represent a block in expert mode.
    ///     max_prec (int, optional): maximum number of bit planes
    ///         encoded in expert mode.
    ///     min_exp (int, optional): smallest absolute bit plane
    ///         number encoded (applies to floating-point data only;
    ///         this parameter is ignored for integer data) in
    ///         expert mode.
    ///     rate (double, optional): rate in bits per value in fixed
    ///         rate mode.
    ///     precision (int, optional): number of bit planes encoded
    ///         in fixed precision mode.
    ///     tolerance (double, optional): absolute error tolerance
    ///         in fixed accuracy mode.
    ZfpCodec(
        mode,
        min_bits=None, max_bits=None, max_prec=None, min_exp=None,
        rate=None, precision=None, tolerance=None
    )
}
