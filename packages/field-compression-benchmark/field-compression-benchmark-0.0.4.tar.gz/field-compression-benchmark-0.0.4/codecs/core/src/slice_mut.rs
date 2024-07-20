use crate::{
    map::HigherOrderMap,
    map_with,
    slice::BufferSlice,
    ty::{BufferTy, BufferTyBound},
};

#[allow(clippy::module_name_repetitions)]
#[derive(Debug, PartialEq)]
#[non_exhaustive]
pub enum BufferSliceMut<'a> {
    U8(&'a mut [u8]),
    U16(&'a mut [u16]),
    U32(&'a mut [u32]),
    U64(&'a mut [u64]),
    I8(&'a mut [i8]),
    I16(&'a mut [i16]),
    I32(&'a mut [i32]),
    I64(&'a mut [i64]),
    F32(&'a mut [f32]),
    F64(&'a mut [f64]),
}

impl<'a> BufferSliceMut<'a> {
    #[must_use]
    #[allow(clippy::trait_duplication_in_bounds, clippy::multiple_bound_locations)]
    pub fn map<F: HigherOrderMap, R>(self, map: F) -> R
    where
        F: HigherOrderMap<Args<u8> = &'a mut [u8], Output<u8> = R>
            + HigherOrderMap<Args<u16> = &'a mut [u16], Output<u16> = R>
            + HigherOrderMap<Args<u32> = &'a mut [u32], Output<u32> = R>
            + HigherOrderMap<Args<u64> = &'a mut [u64], Output<u64> = R>
            + HigherOrderMap<Args<i8> = &'a mut [i8], Output<i8> = R>
            + HigherOrderMap<Args<i16> = &'a mut [i16], Output<i16> = R>
            + HigherOrderMap<Args<i32> = &'a mut [i32], Output<i32> = R>
            + HigherOrderMap<Args<i64> = &'a mut [i64], Output<i64> = R>
            + HigherOrderMap<Args<f32> = &'a mut [f32], Output<f32> = R>
            + HigherOrderMap<Args<f64> = &'a mut [f64], Output<f64> = R>,
    {
        match self {
            Self::U8(b) => map.map::<u8>(b),
            Self::U16(b) => map.map::<u16>(b),
            Self::U32(b) => map.map::<u32>(b),
            Self::U64(b) => map.map::<u64>(b),
            Self::I8(b) => map.map::<i8>(b),
            Self::I16(b) => map.map::<i16>(b),
            Self::I32(b) => map.map::<i32>(b),
            Self::I64(b) => map.map::<i64>(b),
            Self::F32(b) => map.map::<f32>(b),
            Self::F64(b) => map.map::<f64>(b),
        }
    }

    #[must_use]
    #[allow(clippy::trait_duplication_in_bounds, clippy::multiple_bound_locations)]
    pub fn map_ref<'b, F: HigherOrderMap, R>(&'b self, map: F) -> R
    where
        F: HigherOrderMap<Args<u8> = &'b [u8], Output<u8> = R>
            + HigherOrderMap<Args<u16> = &'b [u16], Output<u16> = R>
            + HigherOrderMap<Args<u32> = &'b [u32], Output<u32> = R>
            + HigherOrderMap<Args<u64> = &'b [u64], Output<u64> = R>
            + HigherOrderMap<Args<i8> = &'b [i8], Output<i8> = R>
            + HigherOrderMap<Args<i16> = &'b [i16], Output<i16> = R>
            + HigherOrderMap<Args<i32> = &'b [i32], Output<i32> = R>
            + HigherOrderMap<Args<i64> = &'b [i64], Output<i64> = R>
            + HigherOrderMap<Args<f32> = &'b [f32], Output<f32> = R>
            + HigherOrderMap<Args<f64> = &'b [f64], Output<f64> = R>,
    {
        match self {
            Self::U8(b) => map.map::<u8>(b),
            Self::U16(b) => map.map::<u16>(b),
            Self::U32(b) => map.map::<u32>(b),
            Self::U64(b) => map.map::<u64>(b),
            Self::I8(b) => map.map::<i8>(b),
            Self::I16(b) => map.map::<i16>(b),
            Self::I32(b) => map.map::<i32>(b),
            Self::I64(b) => map.map::<i64>(b),
            Self::F32(b) => map.map::<f32>(b),
            Self::F64(b) => map.map::<f64>(b),
        }
    }

    #[must_use]
    #[allow(clippy::trait_duplication_in_bounds, clippy::multiple_bound_locations)]
    pub fn map_ref_mut<'b, F: HigherOrderMap, R>(&'b mut self, map: F) -> R
    where
        F: HigherOrderMap<Args<u8> = &'b mut [u8], Output<u8> = R>
            + HigherOrderMap<Args<u16> = &'b mut [u16], Output<u16> = R>
            + HigherOrderMap<Args<u32> = &'b mut [u32], Output<u32> = R>
            + HigherOrderMap<Args<u64> = &'b mut [u64], Output<u64> = R>
            + HigherOrderMap<Args<i8> = &'b mut [i8], Output<i8> = R>
            + HigherOrderMap<Args<i16> = &'b mut [i16], Output<i16> = R>
            + HigherOrderMap<Args<i32> = &'b mut [i32], Output<i32> = R>
            + HigherOrderMap<Args<i64> = &'b mut [i64], Output<i64> = R>
            + HigherOrderMap<Args<f32> = &'b mut [f32], Output<f32> = R>
            + HigherOrderMap<Args<f64> = &'b mut [f64], Output<f64> = R>,
    {
        match self {
            Self::U8(b) => map.map::<u8>(b),
            Self::U16(b) => map.map::<u16>(b),
            Self::U32(b) => map.map::<u32>(b),
            Self::U64(b) => map.map::<u64>(b),
            Self::I8(b) => map.map::<i8>(b),
            Self::I16(b) => map.map::<i16>(b),
            Self::I32(b) => map.map::<i32>(b),
            Self::I64(b) => map.map::<i64>(b),
            Self::F32(b) => map.map::<f32>(b),
            Self::F64(b) => map.map::<f64>(b),
        }
    }

    #[must_use]
    pub fn as_slice(&self) -> BufferSlice {
        self.map_ref(map_with!(for<'a, T> |v: &'a [T]| -> BufferSlice<'a> {
            BufferSlice::from(v)
        }))
    }

    #[must_use]
    pub fn as_bytes_mut(&mut self) -> &mut [u8] {
        self.map_ref_mut(map_with!(for<'a, T> |v: &'a mut [T]| -> &'a mut [u8] {
            let (data, len) = (v.as_mut_ptr().cast::<u8>(), core::mem::size_of_val(v));
            #[allow(unsafe_code)]
            // Safety:
            // - we have a mutable reference to self
            // - all slice element types can be modified on a per-byte basis
            unsafe {
                core::slice::from_raw_parts_mut(data, len)
            }
        }))
    }

    pub fn copy_from(&mut self, src: BufferSlice) -> Result<(), BufferSliceCopyError> {
        if self.as_slice().len() != src.len() {
            return Err(BufferSliceCopyError::LenMismatch {
                src: src.len(),
                dst: self.as_slice().len(),
            });
        }

        match (self, src) {
            (Self::U8(dst), BufferSlice::U8(src)) => dst.copy_from_slice(src),
            (Self::U16(dst), BufferSlice::U16(src)) => dst.copy_from_slice(src),
            (Self::U32(dst), BufferSlice::U32(src)) => dst.copy_from_slice(src),
            (Self::U64(dst), BufferSlice::U64(src)) => dst.copy_from_slice(src),
            (Self::I8(dst), BufferSlice::I8(src)) => dst.copy_from_slice(src),
            (Self::I16(dst), BufferSlice::I16(src)) => dst.copy_from_slice(src),
            (Self::I32(dst), BufferSlice::I32(src)) => dst.copy_from_slice(src),
            (Self::I64(dst), BufferSlice::I64(src)) => dst.copy_from_slice(src),
            (Self::F32(dst), BufferSlice::F32(src)) => dst.copy_from_slice(src),
            (Self::F64(dst), BufferSlice::F64(src)) => dst.copy_from_slice(src),
            (dst, src) => {
                return Err(BufferSliceCopyError::TypeMismatch {
                    src: src.ty(),
                    dst: dst.as_slice().ty(),
                })
            },
        }

        Ok(())
    }
}

impl<'a, T: BufferTyBound> From<&'a mut [T]> for BufferSliceMut<'a> {
    fn from(slice: &'a mut [T]) -> Self {
        T::into_buffer_slice_mut(slice)
    }
}

#[derive(Debug, thiserror::Error)]
pub enum BufferSliceCopyError {
    #[error("buffer slice expected len {dst} but found {src}")]
    LenMismatch { src: usize, dst: usize },
    #[error("buffer slice expected type {dst} but found {src}")]
    TypeMismatch { src: BufferTy, dst: BufferTy },
}
