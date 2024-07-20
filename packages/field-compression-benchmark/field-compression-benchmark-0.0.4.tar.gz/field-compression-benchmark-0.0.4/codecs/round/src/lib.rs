#![cfg_attr(not(test), no_main)]

use std::ops::{Div, Mul};

#[must_use]
pub fn round<T: Float>(data: &[T], precision: Positive<T>) -> Vec<T> {
    data.iter()
        .copied()
        .map(|x| (x / precision.0).round() * precision.0)
        .collect()
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct RoundCodec {
    precision: Positive<f64>,
}

impl codecs_core::Codec for RoundCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "round";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded = match buf {
            #[allow(clippy::cast_possible_truncation)]
            codecs_core::BufferSlice::F32(data) => {
                codecs_core::BufferVec::F32(round(data, Positive(self.precision.0 as f32)))
            },
            codecs_core::BufferSlice::F64(data) => {
                codecs_core::BufferVec::F64(round(data, self.precision))
            },
            buf => {
                return Err(format!(
                    "Round::encode does not support the buffer dtype `{}`",
                    buf.ty(),
                ))
            },
        };

        Ok(codecs_core::ShapedBuffer {
            shape: Vec::from(shape),
            buffer: encoded,
        })
    }

    fn decode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::DecodedBuffer>, String> {
        let decoded = match buf {
            codecs_core::BufferSlice::F32(data) => codecs_core::BufferVec::F32(Vec::from(data)),
            codecs_core::BufferSlice::F64(data) => codecs_core::BufferVec::F64(Vec::from(data)),
            buf => {
                return Err(format!(
                    "Round::decode does not support the buffer dtype `{}`",
                    buf.ty(),
                ))
            },
        };

        Ok(codecs_core::ShapedBuffer {
            shape: Vec::from(shape),
            buffer: decoded,
        })
    }

    fn get_config<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serde::Serialize::serialize(&self, serializer)
    }
}

codecs_core_wasm::export_codec! {
    /// Rounding codec which calculates c = round(x / precision) * precision on
    /// encoding and passes through the input unchanged during decoding.
    ///
    /// The codec only supports floating point data.
    ///
    /// Args:
    ///     precision (float): Precision of the rounding, must be positive.
    RoundCodec(precision)
}

pub trait Float: Copy + Mul<Self, Output = Self> + Div<Self, Output = Self> {
    #[must_use]
    fn round(self) -> Self;
}

impl Float for f32 {
    fn round(self) -> Self {
        Self::round(self)
    }
}

impl Float for f64 {
    fn round(self) -> Self {
        Self::round(self)
    }
}

#[allow(clippy::derive_partial_eq_without_eq)] // floats are not Eq
#[derive(Copy, Clone, PartialEq, PartialOrd, Hash)]
pub struct Positive<T: Float>(T);

impl serde::Serialize for Positive<f64> {
    fn serialize<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_f64(self.0)
    }
}

impl<'de> serde::Deserialize<'de> for Positive<f64> {
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        let x = f64::deserialize(deserializer)?;

        if x > 0.0 {
            Ok(Self(x))
        } else {
            Err(serde::de::Error::invalid_value(
                serde::de::Unexpected::Float(x),
                &"a positive value",
            ))
        }
    }
}
