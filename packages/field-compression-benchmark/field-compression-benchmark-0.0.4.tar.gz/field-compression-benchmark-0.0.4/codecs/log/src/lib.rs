#![allow(clippy::missing_errors_doc)]
#![cfg_attr(not(test), no_main)]

pub fn ln_1p<T: Float>(data: &[T]) -> Result<Vec<T>, String> {
    if data.iter().copied().any(T::is_negative) {
        return Err(String::from("Log cannot encode negative data"));
    }

    if !data.iter().copied().all(T::is_finite) {
        return Err(String::from("Log cannot encode non-finite data"));
    }

    Ok(data.iter().copied().map(T::ln_1p).collect())
}

pub fn exp_m1<T: Float>(data: &[T]) -> Result<Vec<T>, String> {
    if data.iter().copied().any(T::is_negative) {
        return Err(String::from("Log cannot decode negative data"));
    }

    if !data.iter().copied().all(T::is_finite) {
        return Err(String::from("Log cannot decode non-finite data"));
    }

    Ok(data.iter().copied().map(T::exp_m1).collect())
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct LogCodec {
    // empty
}

impl codecs_core::Codec for LogCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "log";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded = match buf {
            codecs_core::BufferSlice::F32(data) => codecs_core::BufferVec::F32(ln_1p(data)?),
            codecs_core::BufferSlice::F64(data) => codecs_core::BufferVec::F64(ln_1p(data)?),
            buf => {
                return Err(format!(
                    "Log::encode does not support the buffer dtype `{}`",
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
            codecs_core::BufferSlice::F32(data) => codecs_core::BufferVec::F32(exp_m1(data)?),
            codecs_core::BufferSlice::F64(data) => codecs_core::BufferVec::F64(exp_m1(data)?),
            buf => {
                return Err(format!(
                    "Log::decode does not support the buffer dtype `{}`",
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
    /// Log codec which calculates c = log(1+x) on encoding and
    /// d = exp(c)-1 on decoding. The codec only supports
    /// non-negative floating point numbers.
    LogCodec()
}

pub trait Float: Copy {
    #[must_use]
    fn ln_1p(self) -> Self;

    #[must_use]
    fn exp_m1(self) -> Self;

    fn is_negative(self) -> bool;
    fn is_finite(self) -> bool;
}

impl Float for f32 {
    fn ln_1p(self) -> Self {
        self.ln_1p()
    }

    fn exp_m1(self) -> Self {
        self.exp_m1()
    }

    fn is_negative(self) -> bool {
        self < 0.0
    }

    fn is_finite(self) -> bool {
        self.is_finite()
    }
}

impl Float for f64 {
    fn ln_1p(self) -> Self {
        self.ln_1p()
    }

    fn exp_m1(self) -> Self {
        self.exp_m1()
    }

    fn is_negative(self) -> bool {
        self < 0.0
    }

    fn is_finite(self) -> bool {
        self.is_finite()
    }
}
