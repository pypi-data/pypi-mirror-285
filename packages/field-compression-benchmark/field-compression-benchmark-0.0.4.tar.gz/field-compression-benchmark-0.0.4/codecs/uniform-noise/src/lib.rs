#![cfg_attr(not(test), no_main)]

use std::hash::{Hash, Hasher};

use rand::{
    distributions::{Distribution, Open01},
    SeedableRng,
};
use wyhash::{WyHash, WyRng};

#[must_use]
pub fn add_uniform_noise<T: Float>(data: &[T], shape: &[usize], scale: T, seed: u64) -> Vec<T>
where
    Open01: Distribution<T>,
{
    let mut hasher = WyHash::with_seed(seed);
    // hashing the shape provides a prefix for the flattened data
    shape.hash(&mut hasher);
    data.iter().copied().for_each(|x| x.hash_bits(&mut hasher));
    let seed = hasher.finish();

    let mut rng: WyRng = WyRng::seed_from_u64(seed);

    data.iter()
        .map(|x| Open01.sample(&mut rng).mul_add(scale, *x))
        .collect()
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct UniformNoiseCodec {
    scale: f64,
    seed: u64,
}

impl codecs_core::Codec for UniformNoiseCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "uniform-noise";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded =
            match buf {
                #[allow(clippy::cast_possible_truncation)]
                codecs_core::BufferSlice::F32(data) => codecs_core::BufferVec::F32(
                    add_uniform_noise(data, shape, self.scale as f32, self.seed),
                ),
                codecs_core::BufferSlice::F64(data) => codecs_core::BufferVec::F64(
                    add_uniform_noise(data, shape, self.scale, self.seed),
                ),
                buf => {
                    return Err(format!(
                        "UniformNoise::encode does not support the buffer dtype `{}`",
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
                    "UniformNoise::decode does not support the buffer dtype `{}`",
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
        serde::Serialize::serialize(self, serializer)
    }
}

codecs_core_wasm::export_codec! {
    /// Uniform noise codec which adds U(-scale/2, scale/2) uniform random
    /// noise to the input on encoding and passes through the input unchanged
    /// during decoding.
    ///
    /// This codec first hashes the input and its shape to then seed a pseudo-
    /// random number generator that generates the uniform noise. Therefore,
    /// encoding the same data with the same seed will produce the same noise
    /// and thus the same encoded data.
    ///
    /// Args:
    ///     scale (float): Scale/width of the uniform noise to add on encoding.
    ///     seed (int): Seed for the random number generator.
    UniformNoiseCodec(scale, seed)
}

pub trait Float: Copy {
    #[must_use]
    fn mul_add(self, a: Self, b: Self) -> Self;

    fn hash_bits<H: Hasher>(self, hasher: &mut H);
}

impl Float for f32 {
    fn mul_add(self, a: Self, b: Self) -> Self {
        Self::mul_add(self, a, b)
    }

    fn hash_bits<H: Hasher>(self, hasher: &mut H) {
        hasher.write_u32(self.to_bits());
    }
}

impl Float for f64 {
    fn mul_add(self, a: Self, b: Self) -> Self {
        Self::mul_add(self, a, b)
    }

    fn hash_bits<H: Hasher>(self, hasher: &mut H) {
        hasher.write_u64(self.to_bits());
    }
}
