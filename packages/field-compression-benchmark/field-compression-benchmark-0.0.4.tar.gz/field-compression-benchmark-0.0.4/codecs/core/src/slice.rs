use std::alloc::Layout;

use crate::{
    buffer::BufferVec,
    map::HigherOrderMap,
    map_with,
    ty::{BufferTy, BufferTyBound},
};

#[allow(clippy::module_name_repetitions)]
#[derive(Copy, Clone, Debug, PartialEq)]
#[non_exhaustive]
pub enum BufferSlice<'a> {
    U8(&'a [u8]),
    U16(&'a [u16]),
    U32(&'a [u32]),
    U64(&'a [u64]),
    I8(&'a [i8]),
    I16(&'a [i16]),
    I32(&'a [i32]),
    I64(&'a [i64]),
    F32(&'a [f32]),
    F64(&'a [f64]),
}

impl<'a> BufferSlice<'a> {
    #[must_use]
    #[allow(clippy::trait_duplication_in_bounds, clippy::multiple_bound_locations)]
    pub fn map<F: HigherOrderMap, R>(self, map: F) -> R
    where
        F: HigherOrderMap<Args<u8> = &'a [u8], Output<u8> = R>
            + HigherOrderMap<Args<u16> = &'a [u16], Output<u16> = R>
            + HigherOrderMap<Args<u32> = &'a [u32], Output<u32> = R>
            + HigherOrderMap<Args<u64> = &'a [u64], Output<u64> = R>
            + HigherOrderMap<Args<i8> = &'a [i8], Output<i8> = R>
            + HigherOrderMap<Args<i16> = &'a [i16], Output<i16> = R>
            + HigherOrderMap<Args<i32> = &'a [i32], Output<i32> = R>
            + HigherOrderMap<Args<i64> = &'a [i64], Output<i64> = R>
            + HigherOrderMap<Args<f32> = &'a [f32], Output<f32> = R>
            + HigherOrderMap<Args<f64> = &'a [f64], Output<f64> = R>,
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
    pub fn ty(&self) -> BufferTy {
        self.map(map_with!(for<'a, T> |_v: &'a [T]| -> BufferTy { T::TY }))
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.map(map_with!(for<'a, T> |v: &'a [T]| -> usize { v.len() }))
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.map(map_with!(for<'a, T> |v: &'a [T]| -> bool { v.is_empty() }))
    }

    #[must_use]
    pub fn layout(&self) -> Layout {
        self.map(map_with!(for<'a, T> |v: &'a [T]| -> Layout {
            Layout::for_value(v)
        }))
    }

    #[must_use]
    pub fn as_bytes(&self) -> &'a [u8] {
        self.map(map_with!(for<'a, T> |v: &'a [T]| -> &'a [u8] {
            let (data, len) = (v.as_ptr().cast::<u8>(), core::mem::size_of_val(v));
            #[allow(unsafe_code)]
            // Safety:
            // - we have a reference to self
            // - all slice element types can be modified on a per-byte basis
            unsafe {
                core::slice::from_raw_parts(data, len)
            }
        }))
    }

    #[must_use]
    pub fn to_vec(&self) -> BufferVec {
        self.map(map_with!(for<'a, T> |v: &'a [T]| -> BufferVec {
            BufferVec::from(Vec::from(v))
        }))
    }
}

impl<'a, T: BufferTyBound> From<&'a [T]> for BufferSlice<'a> {
    fn from(slice: &'a [T]) -> Self {
        T::into_buffer_slice(slice)
    }
}
