use crate::{
    map::HigherOrderMap,
    map_with,
    slice::BufferSlice,
    slice_mut::BufferSliceMut,
    ty::{BufferTy, BufferTyBound},
};

#[allow(clippy::module_name_repetitions)]
#[non_exhaustive]
pub enum BufferVec<B: OwnedBuffer = VecBuffer> {
    U8(B::Buffer<u8>),
    U16(B::Buffer<u16>),
    U32(B::Buffer<u32>),
    U64(B::Buffer<u64>),
    I8(B::Buffer<i8>),
    I16(B::Buffer<i16>),
    I32(B::Buffer<i32>),
    I64(B::Buffer<i64>),
    F32(B::Buffer<f32>),
    F64(B::Buffer<f64>),
}

impl<B: OwnedBuffer> BufferVec<B> {
    #[must_use]
    #[allow(clippy::trait_duplication_in_bounds, clippy::multiple_bound_locations)]
    pub fn map<F: HigherOrderMap, R>(self, map: F) -> R
    where
        F: HigherOrderMap<Args<u8> = B::Buffer<u8>, Output<u8> = R>
            + HigherOrderMap<Args<u16> = B::Buffer<u16>, Output<u16> = R>
            + HigherOrderMap<Args<u32> = B::Buffer<u32>, Output<u32> = R>
            + HigherOrderMap<Args<u64> = B::Buffer<u64>, Output<u64> = R>
            + HigherOrderMap<Args<i8> = B::Buffer<i8>, Output<i8> = R>
            + HigherOrderMap<Args<i16> = B::Buffer<i16>, Output<i16> = R>
            + HigherOrderMap<Args<i32> = B::Buffer<i32>, Output<i32> = R>
            + HigherOrderMap<Args<i64> = B::Buffer<i64>, Output<i64> = R>
            + HigherOrderMap<Args<f32> = B::Buffer<f32>, Output<f32> = R>
            + HigherOrderMap<Args<f64> = B::Buffer<f64>, Output<f64> = R>,
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
    pub fn map_ref<'a, F: HigherOrderMap, R>(&'a self, map: F) -> R
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
    pub fn as_slice(&self) -> BufferSlice {
        self.map_ref(map_with!(for<'a, T> |v: &'a [T]| -> BufferSlice<'a> {
            BufferSlice::from(v)
        }))
    }
}

impl<B: OwnedBuffer> BufferVec<B>
where
    B::Buffer<u8>: core::ops::DerefMut<Target = [u8]>,
    B::Buffer<u16>: core::ops::DerefMut<Target = [u16]>,
    B::Buffer<u32>: core::ops::DerefMut<Target = [u32]>,
    B::Buffer<u64>: core::ops::DerefMut<Target = [u64]>,
    B::Buffer<i8>: core::ops::DerefMut<Target = [i8]>,
    B::Buffer<i16>: core::ops::DerefMut<Target = [i16]>,
    B::Buffer<i32>: core::ops::DerefMut<Target = [i32]>,
    B::Buffer<i64>: core::ops::DerefMut<Target = [i64]>,
    B::Buffer<f32>: core::ops::DerefMut<Target = [f32]>,
    B::Buffer<f64>: core::ops::DerefMut<Target = [f64]>,
{
    #[must_use]
    #[allow(clippy::trait_duplication_in_bounds, clippy::multiple_bound_locations)]
    pub fn map_ref_mut<'a, F: HigherOrderMap, R>(&'a mut self, map: F) -> R
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
    pub fn as_slice_mut(&mut self) -> BufferSliceMut {
        self.map_ref_mut(map_with!(
            for<'a, T> |v: &'a mut [T]| -> BufferSliceMut<'a> { BufferSliceMut::from(v) }
        ))
    }
}

impl BufferVec<VecBuffer> {
    #[must_use]
    pub fn zeros_with_ty_len(ty: BufferTy, len: usize) -> Self {
        ty.map(
            map_with!(for<T> move(len: usize) || -> BufferVec<VecBuffer> {
                BufferVec::from(vec![T::ZERO; len])
            }),
        )
    }
}

impl<B: OwnedBufferImpl> From<B> for BufferVec<B::Provider> {
    fn from(buffer: B) -> Self {
        <B::Item as BufferTyBound>::into_buffer_vec(buffer)
    }
}

#[allow(clippy::module_name_repetitions)]
pub trait OwnedBuffer {
    type Buffer<T: BufferTyBound>: OwnedBufferImpl<Item = T, Provider = Self>;
}

pub trait OwnedBufferImpl: core::ops::Deref<Target = [Self::Item]> {
    type Item: BufferTyBound;
    type Provider: OwnedBuffer<Buffer<Self::Item> = Self>;

    fn into_vec(self) -> Vec<Self::Item>;
}

#[allow(clippy::module_name_repetitions)]
pub enum VecBuffer {}

impl OwnedBuffer for VecBuffer {
    type Buffer<T: BufferTyBound> = Vec<T>;
}

impl<T: BufferTyBound> OwnedBufferImpl for Vec<T> {
    type Item = T;
    type Provider = VecBuffer;

    fn into_vec(self) -> Vec<Self::Item> {
        self
    }
}
