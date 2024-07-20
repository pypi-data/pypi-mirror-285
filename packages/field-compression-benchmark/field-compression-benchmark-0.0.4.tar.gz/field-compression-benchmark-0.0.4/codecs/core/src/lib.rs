#![allow(clippy::missing_errors_doc)]

#[doc(hidden)]
pub extern crate core;

mod buffer;
mod slice;
mod slice_mut;
mod ty;

#[doc(hidden)]
pub mod casts;
pub mod map;

pub use crate::{
    buffer::{BufferVec, OwnedBuffer, OwnedBufferImpl, VecBuffer},
    slice::BufferSlice,
    slice_mut::BufferSliceMut,
    ty::{BufferTy, BufferTyBound},
};

pub trait Codec: 'static + Clone {
    const CODEC_ID: &'static str;

    type EncodedBuffer: OwnedBuffer;
    type DecodedBuffer: OwnedBuffer;

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error>;

    fn encode(
        &self,
        buf: BufferSlice,
        shape: &[usize],
    ) -> Result<ShapedBuffer<Self::EncodedBuffer>, String>;

    fn decode(
        &self,
        buf: BufferSlice,
        shape: &[usize],
    ) -> Result<ShapedBuffer<Self::DecodedBuffer>, String>;

    fn get_config<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error>;
}

pub struct ShapedBuffer<B: OwnedBuffer = VecBuffer> {
    pub buffer: BufferVec<B>,
    pub shape: Vec<usize>,
}
