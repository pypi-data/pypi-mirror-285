use codecs_core::{BufferSlice, BufferVec, OwnedBuffer, OwnedBufferImpl};

use crate::bindings::exports::numcodecs::abc::codec::Buffer as WitBuffer;

#[must_use]
pub fn wit_buffer_to_codecs(buffer: &WitBuffer) -> BufferSlice {
    match buffer {
        WitBuffer::U8(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::U16(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::U32(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::U64(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::I8(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::I16(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::I32(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::I64(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::F32(data) => BufferSlice::from(data.as_slice()),
        WitBuffer::F64(data) => BufferSlice::from(data.as_slice()),
    }
}

pub fn codecs_buffer_to_wit<B: OwnedBuffer>(buffer: BufferVec<B>) -> Result<WitBuffer, String> {
    match buffer {
        BufferVec::U8(data) => Ok(WitBuffer::U8(data.into_vec())),
        BufferVec::U16(data) => Ok(WitBuffer::U16(data.into_vec())),
        BufferVec::U32(data) => Ok(WitBuffer::U32(data.into_vec())),
        BufferVec::U64(data) => Ok(WitBuffer::U64(data.into_vec())),
        BufferVec::I8(data) => Ok(WitBuffer::I8(data.into_vec())),
        BufferVec::I16(data) => Ok(WitBuffer::I16(data.into_vec())),
        BufferVec::I32(data) => Ok(WitBuffer::I32(data.into_vec())),
        BufferVec::I64(data) => Ok(WitBuffer::I64(data.into_vec())),
        BufferVec::F32(data) => Ok(WitBuffer::F32(data.into_vec())),
        BufferVec::F64(data) => Ok(WitBuffer::F64(data.into_vec())),
        buffer => Err(format!(
            "unsupported codecs buffer type {} in WIT bindgen",
            buffer.as_slice().ty()
        )),
    }
}

#[must_use]
pub fn usize_as_u32_vec(vec: Vec<usize>) -> Vec<u32> {
    vec.into_iter()
        .map(codecs_core::casts::usize_as_u32)
        .collect()
}

#[must_use]
pub fn u32_as_usize_vec(vec: Vec<u32>) -> Vec<usize> {
    vec.into_iter()
        .map(codecs_core::casts::u32_as_usize)
        .collect()
}
