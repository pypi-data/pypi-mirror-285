#![allow(clippy::missing_errors_doc)]
#![cfg_attr(not(test), no_main)]

use std::fmt;

use twofloat::TwoFloat;

pub fn compress<T: Float, Q: Unsigned>(
    data: &[T],
    shape: &[usize],
    quantize: impl Fn(T) -> Q,
) -> Result<Vec<Q>, String> {
    if !data.iter().copied().all(T::is_finite) {
        return Err(String::from("LinearQuantize cannot encode non-finite data"));
    }

    let minimum = data.iter().copied().reduce(T::minimum).unwrap_or(T::ZERO);
    let maximum = data.iter().copied().reduce(T::maximum).unwrap_or(T::ONE);

    let header = postcard::to_extend(
        &CompressionHeader {
            shape: std::borrow::Cow::Borrowed(shape),
            minimum,
            maximum,
        },
        Vec::new(),
    )
    .map_err(|err| format!("LinearQuantize failed to write header: {err}"))?;

    let mut encoded =
        vec![Q::ZERO; (header.len() + std::mem::size_of::<Q>() - 1) / std::mem::size_of::<Q>()];
    #[allow(unsafe_code)]
    // Safety: encoded is at least header.len() bytes long and propely aligned for Q
    unsafe {
        std::ptr::copy_nonoverlapping(header.as_ptr(), encoded.as_mut_ptr().cast(), header.len());
    }
    encoded.reserve(data.len());

    if maximum == minimum {
        let zero = quantize(T::ZERO);
        encoded.extend(data.iter().map(|_x| zero));
    } else {
        encoded.extend(
            data.iter()
                .map(|x| quantize((*x - minimum) / (maximum - minimum))),
        );
    }

    Ok(encoded)
}

pub fn decompress<T: Float, Q: Unsigned>(
    data: &[Q],
    floatify: impl Fn(Q) -> T,
) -> Result<(Vec<T>, Vec<usize>), String> {
    #[allow(unsafe_code)]
    // Safety: data is data.len()*size_of::<Q> bytes long and propely aligned for Q
    let (header, remaining) = postcard::take_from_bytes::<CompressionHeader<T>>(unsafe {
        std::slice::from_raw_parts(data.as_ptr().cast(), std::mem::size_of_val(data))
    })
    .map_err(|err| format!("LinearQuantize failed to read header: {err}"))?;
    let data = data
        .get(data.len() - (remaining.len() / std::mem::size_of::<Q>())..)
        .unwrap_or(&[]);

    let decoded = data
        .iter()
        .map(|x| header.minimum + (floatify(*x) * (header.maximum - header.minimum)))
        .map(|x| x.clamp(header.minimum, header.maximum))
        .collect();

    Ok((decoded, header.shape.into_owned()))
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct LinearQuantizeCodec {
    dtype: DType,
    bits: u8,
}

impl codecs_core::Codec for LinearQuantizeCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "linear-quantize";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        let codec: Self = serde::Deserialize::deserialize(config)?;

        match (codec.dtype, codec.bits) {
            (_, 0) => return Err(serde::de::Error::custom("bits must be positive")),
            (DType::F32, bits @ 33..) => {
                return Err(serde::de::Error::custom(format!(
                    "{bits} bits exceeds the bit width of {}",
                    codecs_core::BufferTy::F32,
                )))
            },
            (DType::F64, bits @ 65..) => {
                return Err(serde::de::Error::custom(format!(
                    "{bits} bits exceeds the bit width of {}",
                    codecs_core::BufferTy::F64,
                )))
            },
            _ => (),
        }

        Ok(codec)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded = match (buf, self.dtype) {
            (codecs_core::BufferSlice::F32(data), DType::F32) => match self.bits {
                bits @ ..=8 => codecs_core::BufferVec::U8(compress(data, shape, |x| {
                    let max = f32::from(u8::MAX >> (8 - bits));
                    let x = (x * f32::scale_for_bits(bits)).clamp(0.0, max);
                    #[allow(unsafe_code)]
                    // Safety: x is clamped beforehand
                    unsafe {
                        x.to_int_unchecked::<u8>()
                    }
                })?),
                bits @ ..=16 => codecs_core::BufferVec::U16(compress(data, shape, |x| {
                    let max = f32::from(u16::MAX >> (16 - bits));
                    let x = (x * f32::scale_for_bits(bits)).clamp(0.0, max);
                    #[allow(unsafe_code)]
                    // Safety: x is clamped beforehand
                    unsafe {
                        x.to_int_unchecked::<u16>()
                    }
                })?),
                bits => codecs_core::BufferVec::U32(compress(data, shape, |x| {
                    // we need to use f64 here to have sufficient precision
                    let max = f64::from(u32::MAX >> (32 - bits));
                    let x = (f64::from(x) * f64::scale_for_bits(bits)).clamp(0.0, max);
                    #[allow(unsafe_code)]
                    // Safety: x is clamped beforehand
                    unsafe {
                        x.to_int_unchecked::<u32>()
                    }
                })?),
            },
            (codecs_core::BufferSlice::F64(data), DType::F64) => match self.bits {
                bits @ ..=8 => codecs_core::BufferVec::U8(compress(data, shape, |x| {
                    let max = f64::from(u8::MAX >> (8 - bits));
                    let x = (x * f64::scale_for_bits(bits)).clamp(0.0, max);
                    #[allow(unsafe_code)]
                    // Safety: x is clamped beforehand
                    unsafe {
                        x.to_int_unchecked::<u8>()
                    }
                })?),
                bits @ ..=16 => codecs_core::BufferVec::U16(compress(data, shape, |x| {
                    let max = f64::from(u16::MAX >> (16 - bits));
                    let x = (x * f64::scale_for_bits(bits)).clamp(0.0, max);
                    #[allow(unsafe_code)]
                    // Safety: x is clamped beforehand
                    unsafe {
                        x.to_int_unchecked::<u16>()
                    }
                })?),
                bits @ ..=32 => codecs_core::BufferVec::U32(compress(data, shape, |x| {
                    let max = f64::from(u32::MAX >> (32 - bits));
                    let x = (x * f64::scale_for_bits(bits)).clamp(0.0, max);
                    #[allow(unsafe_code)]
                    // Safety: x is clamped beforehand
                    unsafe {
                        x.to_int_unchecked::<u32>()
                    }
                })?),
                bits => codecs_core::BufferVec::U64(compress(data, shape, |x| {
                    // we need to use TwoFloat here to have sufficient precision
                    let max = TwoFloat::from(u64::MAX >> (64 - bits));
                    let x = (TwoFloat::from(x) * f64::scale_for_bits(bits))
                        .max(TwoFloat::from(0.0))
                        .min(max);
                    #[allow(unsafe_code)]
                    // Safety: x is clamped beforehand
                    unsafe {
                        u64::try_from(x).unwrap_unchecked()
                    }
                })?),
            },
            (buf, _) => {
                return Err(format!(
                    "LinearQuantize::encode buffer dtype `{}` does not match the configured dtype \
                     `{}`",
                    buf.ty(),
                    self.dtype
                ))
            },
        };

        Ok(codecs_core::ShapedBuffer {
            shape: vec![encoded.as_slice().len()],
            buffer: encoded,
        })
    }

    fn decode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::DecodedBuffer>, String> {
        if !matches!(shape, [_]) {
            return Err(format!(
                "LinearQuantize::decode buffer shape {shape:?} is not one-dimensional"
            ));
        }

        let (decoded, shape) = match (buf, self.dtype) {
            (codecs_core::BufferSlice::U8(data), DType::F32) => {
                let (decoded, shape) =
                    decompress(data, |x| f32::from(x) / f32::scale_for_bits(self.bits))?;
                (codecs_core::BufferVec::F32(decoded), shape)
            },
            (codecs_core::BufferSlice::U16(data), DType::F32) => {
                let (decoded, shape) =
                    decompress(data, |x| f32::from(x) / f32::scale_for_bits(self.bits))?;
                (codecs_core::BufferVec::F32(decoded), shape)
            },
            (codecs_core::BufferSlice::U32(data), DType::F32) => {
                let (decoded, shape) = decompress(data, |x| {
                    // we need to use f64 here to have sufficient precision
                    let x = f64::from(x) / f64::scale_for_bits(self.bits);
                    #[allow(clippy::cast_possible_truncation)]
                    let x = x as f32;
                    x
                })?;
                (codecs_core::BufferVec::F32(decoded), shape)
            },
            (codecs_core::BufferSlice::U8(data), DType::F64) => {
                let (decoded, shape) =
                    decompress(data, |x| f64::from(x) / f64::scale_for_bits(self.bits))?;
                (codecs_core::BufferVec::F64(decoded), shape)
            },
            (codecs_core::BufferSlice::U16(data), DType::F64) => {
                let (decoded, shape) =
                    decompress(data, |x| f64::from(x) / f64::scale_for_bits(self.bits))?;
                (codecs_core::BufferVec::F64(decoded), shape)
            },
            (codecs_core::BufferSlice::U32(data), DType::F64) => {
                let (decoded, shape) =
                    decompress(data, |x| f64::from(x) / f64::scale_for_bits(self.bits))?;
                (codecs_core::BufferVec::F64(decoded), shape)
            },
            (codecs_core::BufferSlice::U64(data), DType::F64) => {
                let (decoded, shape) = decompress(data, |x| {
                    // we need to use TwoFloat here to have sufficient precision
                    let x = TwoFloat::from(x) / f64::scale_for_bits(self.bits);
                    f64::from(x)
                })?;
                (codecs_core::BufferVec::F64(decoded), shape)
            },
            (buf, _) => {
                return Err(format!(
                    "LinearQuantize::decode buffer dtype `{}` does not fit the configured dtype \
                     `{}`",
                    buf.ty(),
                    self.dtype
                ))
            },
        };

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
    /// Lossy codec to reduce the precision of floating point data. The data
    /// is quantized to unsigned integers of the best-fitting type. The range
    /// and shape of the input data is stored in-band.
    ///
    /// Args:
    ///     dtype (dtype): Data type to use for decoded data.
    ///     bits (int): Desired precision (number of binary digits).
    LinearQuantizeCodec(dtype, bits)
}

#[derive(Copy, Clone, serde::Serialize, serde::Deserialize)]
enum DType {
    #[serde(rename = "float32")]
    F32,
    #[serde(rename = "float64")]
    F64,
}

impl fmt::Display for DType {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::F32 => fmt.write_str("float32"),
            Self::F64 => fmt.write_str("float64"),
        }
    }
}

#[derive(serde::Serialize, serde::Deserialize)]
#[serde(bound = "")]
struct CompressionHeader<'a, T: Float> {
    #[serde(borrow)]
    shape: std::borrow::Cow<'a, [usize]>,
    minimum: T,
    maximum: T,
}

pub trait Float:
    Copy
    + serde::Serialize
    + serde::de::DeserializeOwned
    + std::ops::Sub<Self, Output = Self>
    + std::ops::Div<Self, Output = Self>
    + std::ops::Add<Self, Output = Self>
    + std::ops::Mul<Self, Output = Self>
    + PartialEq
{
    const ZERO: Self;
    const ONE: Self;

    #[must_use]
    fn minimum(self, other: Self) -> Self;

    #[must_use]
    fn maximum(self, other: Self) -> Self;

    #[must_use]
    fn clamp(self, min: Self, max: Self) -> Self;

    fn scale_for_bits(bits: u8) -> Self;

    fn is_finite(self) -> bool;
}

impl Float for f32 {
    const ONE: Self = 1.0;
    const ZERO: Self = 0.0;

    fn minimum(self, other: Self) -> Self {
        Self::min(self, other)
    }

    fn maximum(self, other: Self) -> Self {
        Self::max(self, other)
    }

    fn clamp(self, min: Self, max: Self) -> Self {
        Self::clamp(self, min, max)
    }

    fn scale_for_bits(bits: u8) -> Self {
        Self::from(bits).exp2() - 1.0
    }

    fn is_finite(self) -> bool {
        self.is_finite()
    }
}

impl Float for f64 {
    const ONE: Self = 1.0;
    const ZERO: Self = 0.0;

    fn minimum(self, other: Self) -> Self {
        Self::min(self, other)
    }

    fn maximum(self, other: Self) -> Self {
        Self::max(self, other)
    }

    fn clamp(self, min: Self, max: Self) -> Self {
        Self::clamp(self, min, max)
    }

    fn scale_for_bits(bits: u8) -> Self {
        Self::from(bits).exp2() - 1.0
    }

    fn is_finite(self) -> bool {
        self.is_finite()
    }
}

pub trait Unsigned: Copy {
    const ZERO: Self;
}

impl Unsigned for u8 {
    const ZERO: Self = 0;
}

impl Unsigned for u16 {
    const ZERO: Self = 0;
}

impl Unsigned for u32 {
    const ZERO: Self = 0;
}

impl Unsigned for u64 {
    const ZERO: Self = 0;
}

#[cfg(test)]
mod tests {
    use codecs_core::{BufferSlice, Codec};

    use super::*;

    #[test]
    fn exact_roundtrip_f32() -> Result<(), String> {
        for bits in 1..=16 {
            let codec = LinearQuantizeCodec {
                dtype: DType::F32,
                bits,
            };

            let mut data: Vec<f32> = (0..(u16::MAX >> (16 - bits)))
                .step_by(1 << (bits.max(8) - 8))
                .map(f32::from)
                .collect();
            data.push(f32::from(u16::MAX >> (16 - bits)));

            let encoded = codec.encode(BufferSlice::F32(&data), &[data.len()])?;
            let decoded = codec.decode(encoded.buffer.as_slice(), &encoded.shape)?;

            let BufferSlice::F32(decoded) = decoded.buffer.as_slice() else {
                return Err(String::from("wrong decode output type"));
            };

            for (o, d) in data.iter().zip(decoded.iter()) {
                assert_eq!(o.to_bits(), d.to_bits());
            }
        }

        Ok(())
    }

    #[test]
    fn almost_roundtrip_f32() -> Result<(), String> {
        for bits in 17..=32 {
            let codec = LinearQuantizeCodec {
                dtype: DType::F32,
                bits,
            };

            #[allow(clippy::cast_precision_loss)]
            let mut data: Vec<f32> = (0..(u32::MAX >> (32 - bits)))
                .step_by(1 << (bits.max(8) - 8))
                .map(|x| x as f32)
                .collect();
            #[allow(clippy::cast_precision_loss)]
            data.push((u32::MAX >> (32 - bits)) as f32);

            let encoded = codec.encode(BufferSlice::F32(&data), &[data.len()])?;
            let decoded = codec.decode(encoded.buffer.as_slice(), &encoded.shape)?;

            let BufferSlice::F32(decoded) = decoded.buffer.as_slice() else {
                return Err(String::from("wrong decode output type"));
            };

            for (o, d) in data.iter().zip(decoded.iter()) {
                // FIXME: there seem to be some rounding errors
                assert!((o - d).abs() <= 1.0);
            }
        }

        Ok(())
    }

    #[test]
    fn exact_roundtrip_f64() -> Result<(), String> {
        for bits in 1..=32 {
            let codec = LinearQuantizeCodec {
                dtype: DType::F64,
                bits,
            };

            let mut data: Vec<f64> = (0..(u32::MAX >> (32 - bits)))
                .step_by(1 << (bits.max(8) - 8))
                .map(f64::from)
                .collect();
            data.push(f64::from(u32::MAX >> (32 - bits)));

            let encoded = codec.encode(BufferSlice::F64(&data), &[data.len()])?;
            let decoded = codec.decode(encoded.buffer.as_slice(), &encoded.shape)?;

            let BufferSlice::F64(decoded) = decoded.buffer.as_slice() else {
                return Err(String::from("wrong decode output type"));
            };

            for (o, d) in data.iter().zip(decoded.iter()) {
                assert_eq!(o.to_bits(), d.to_bits());
            }
        }

        Ok(())
    }

    #[test]
    fn almost_roundtrip_f64() -> Result<(), String> {
        for bits in 33..=64 {
            let codec = LinearQuantizeCodec {
                dtype: DType::F64,
                bits,
            };

            #[allow(clippy::cast_precision_loss)]
            let mut data: Vec<f64> = (0..(u64::MAX >> (64 - bits)))
                .step_by(1 << (bits.max(8) - 8))
                .map(|x| x as f64)
                .collect();
            #[allow(clippy::cast_precision_loss)]
            data.push((u64::MAX >> (64 - bits)) as f64);

            let encoded = codec.encode(BufferSlice::F64(&data), &[data.len()])?;
            let decoded = codec.decode(encoded.buffer.as_slice(), &encoded.shape)?;

            let BufferSlice::F64(decoded) = decoded.buffer.as_slice() else {
                return Err(String::from("wrong decode output type"));
            };

            for (o, d) in data.iter().zip(decoded.iter()) {
                // FIXME: there seem to be some rounding errors
                assert!((o - d).abs() < 2.0);
            }
        }

        Ok(())
    }

    #[test]
    fn const_data_roundtrip() -> Result<(), String> {
        for bits in 1..=64 {
            let data = [42.0, 42.0, 42.0, 42.0];

            let codec = LinearQuantizeCodec {
                dtype: DType::F64,
                bits,
            };

            let encoded = codec.encode(BufferSlice::F64(&data), &[data.len()])?;
            let decoded = codec.decode(encoded.buffer.as_slice(), &encoded.shape)?;

            let BufferSlice::F64(decoded) = decoded.buffer.as_slice() else {
                return Err(String::from("wrong decode output type"));
            };

            for (o, d) in data.iter().zip(decoded.iter()) {
                assert_eq!(o.to_bits(), d.to_bits());
            }
        }

        Ok(())
    }
}
