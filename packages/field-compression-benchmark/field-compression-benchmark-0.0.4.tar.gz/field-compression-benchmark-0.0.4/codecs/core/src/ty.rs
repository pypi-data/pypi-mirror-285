use std::{alloc::Layout, fmt};

use crate::{
    buffer::{BufferVec, OwnedBufferImpl},
    map::HigherOrderMap,
    map_with,
    slice::BufferSlice,
    slice_mut::BufferSliceMut,
};

#[allow(clippy::module_name_repetitions)]
#[derive(Copy, Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[non_exhaustive]
#[repr(u8)]
pub enum BufferTy {
    #[serde(rename = "uint8")]
    U8 = 8,
    #[serde(rename = "uint16")]
    U16 = 16,
    #[serde(rename = "uint32")]
    U32 = 32,
    #[serde(rename = "uint64")]
    U64 = 64,
    #[serde(rename = "int8")]
    I8 = 8 | 1,
    #[serde(rename = "int16")]
    I16 = 16 | 1,
    #[serde(rename = "int32")]
    I32 = 32 | 1,
    #[serde(rename = "int64")]
    I64 = 64 | 1,
    #[serde(rename = "float32")]
    F32 = 32 | 2,
    #[serde(rename = "float64")]
    F64 = 64 | 2,
}

impl BufferTy {
    #[must_use]
    pub const fn new<T: BufferTyBound>() -> Self {
        T::TY
    }

    #[must_use]
    #[allow(clippy::trait_duplication_in_bounds, clippy::multiple_bound_locations)]
    pub fn map<F: HigherOrderMap, R>(self, map: F) -> R
    where
        F: HigherOrderMap<Args<u8> = (), Output<u8> = R>
            + HigherOrderMap<Args<u16> = (), Output<u16> = R>
            + HigherOrderMap<Args<u32> = (), Output<u32> = R>
            + HigherOrderMap<Args<u64> = (), Output<u64> = R>
            + HigherOrderMap<Args<i8> = (), Output<i8> = R>
            + HigherOrderMap<Args<i16> = (), Output<i16> = R>
            + HigherOrderMap<Args<i32> = (), Output<i32> = R>
            + HigherOrderMap<Args<i64> = (), Output<i64> = R>
            + HigherOrderMap<Args<f32> = (), Output<f32> = R>
            + HigherOrderMap<Args<f64> = (), Output<f64> = R>,
    {
        match self {
            Self::U8 => map.map::<u8>(()),
            Self::U16 => map.map::<u16>(()),
            Self::U32 => map.map::<u32>(()),
            Self::U64 => map.map::<u64>(()),
            Self::I8 => map.map::<i8>(()),
            Self::I16 => map.map::<i16>(()),
            Self::I32 => map.map::<i32>(()),
            Self::I64 => map.map::<i64>(()),
            Self::F32 => map.map::<f32>(()),
            Self::F64 => map.map::<f64>(()),
        }
    }

    #[must_use]
    pub fn layout(self) -> Layout {
        self.map(map_with!(for<T> || -> Layout { Layout::new::<T>() }))
    }
}

pub struct TryBufferTyFromU32Error;

impl From<BufferTy> for u32 {
    fn from(value: BufferTy) -> Self {
        value as Self
    }
}

impl TryFrom<u32> for BufferTy {
    type Error = TryBufferTyFromU32Error;

    fn try_from(value: u32) -> Result<Self, Self::Error> {
        const U8: u32 = BufferTy::U8 as u32;
        const U16: u32 = BufferTy::U16 as u32;
        const U32: u32 = BufferTy::U32 as u32;
        const U64: u32 = BufferTy::U64 as u32;
        const I8: u32 = BufferTy::I8 as u32;
        const I16: u32 = BufferTy::I16 as u32;
        const I32: u32 = BufferTy::I32 as u32;
        const I64: u32 = BufferTy::I64 as u32;
        const F32: u32 = BufferTy::F32 as u32;
        const F64: u32 = BufferTy::F64 as u32;

        match value {
            U8 => Ok(Self::U8),
            U16 => Ok(Self::U16),
            U32 => Ok(Self::U32),
            U64 => Ok(Self::U64),
            I8 => Ok(Self::I8),
            I16 => Ok(Self::I16),
            I32 => Ok(Self::I32),
            I64 => Ok(Self::I64),
            F32 => Ok(Self::F32),
            F64 => Ok(Self::F64),
            _ => Err(TryBufferTyFromU32Error),
        }
    }
}

impl fmt::Display for BufferTy {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        let str = match self {
            Self::U8 => "uint8",
            Self::U16 => "uint16",
            Self::U32 => "uint32",
            Self::U64 => "uint64",
            Self::I8 => "int8",
            Self::I16 => "int16",
            Self::I32 => "int32",
            Self::I64 => "int64",
            Self::F32 => "float32",
            Self::F64 => "float64",
        };

        fmt.write_str(str)
    }
}

pub trait BufferTyBound: 'static + Copy + sealed::Sealed {
    const TY: BufferTy;
    const ZERO: Self;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice;
    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut;

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider>;
}

impl BufferTyBound for u8 {
    const TY: BufferTy = BufferTy::U8;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::U8(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::U8(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::U8(buffer)
    }
}

impl BufferTyBound for u16 {
    const TY: BufferTy = BufferTy::U16;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::U16(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::U16(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::U16(buffer)
    }
}

impl BufferTyBound for u32 {
    const TY: BufferTy = BufferTy::U32;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::U32(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::U32(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::U32(buffer)
    }
}

impl BufferTyBound for u64 {
    const TY: BufferTy = BufferTy::U64;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::U64(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::U64(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::U64(buffer)
    }
}

impl BufferTyBound for i8 {
    const TY: BufferTy = BufferTy::I8;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::I8(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::I8(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::I8(buffer)
    }
}

impl BufferTyBound for i16 {
    const TY: BufferTy = BufferTy::I16;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::I16(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::I16(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::I16(buffer)
    }
}

impl BufferTyBound for i32 {
    const TY: BufferTy = BufferTy::I32;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::I32(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::I32(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::I32(buffer)
    }
}

impl BufferTyBound for i64 {
    const TY: BufferTy = BufferTy::I64;
    const ZERO: Self = 0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::I64(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::I64(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::I64(buffer)
    }
}

impl BufferTyBound for f32 {
    const TY: BufferTy = BufferTy::F32;
    const ZERO: Self = 0.0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::F32(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::F32(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::F32(buffer)
    }
}

impl BufferTyBound for f64 {
    const TY: BufferTy = BufferTy::F64;
    const ZERO: Self = 0.0;

    fn into_buffer_slice(slice: &[Self]) -> BufferSlice {
        BufferSlice::F64(slice)
    }

    fn into_buffer_slice_mut(slice: &mut [Self]) -> BufferSliceMut {
        BufferSliceMut::F64(slice)
    }

    fn into_buffer_vec<B: OwnedBufferImpl<Item = Self>>(buffer: B) -> BufferVec<B::Provider> {
        BufferVec::F64(buffer)
    }
}

mod sealed {
    pub trait Sealed {}

    impl Sealed for u8 {}
    impl Sealed for u16 {}
    impl Sealed for u32 {}
    impl Sealed for u64 {}
    impl Sealed for i8 {}
    impl Sealed for i16 {}
    impl Sealed for i32 {}
    impl Sealed for i64 {}
    impl Sealed for f32 {}
    impl Sealed for f64 {}
}
