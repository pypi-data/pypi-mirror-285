#![cfg_attr(test, allow(clippy::unwrap_used))]
#![allow(clippy::missing_errors_doc)]
#![cfg_attr(not(test), no_main)]

pub fn bit_round<T: Float>(data: &[T], keepbits: u8) -> Result<Vec<T>, String> {
    if u32::from(keepbits) > T::MANITSSA_BITS {
        return Err(format!(
            "{keepbits} bits exceed the mantissa size for {}",
            T::TY
        ));
    }

    // Early return if no bit rounding needs to happen
    // - required since the ties to even impl does not work in this case
    if u32::from(keepbits) == T::MANITSSA_BITS {
        return Ok(Vec::from(data));
    }

    // half of unit in last place (ulp)
    let ulp_half = T::MANTISSA_MASK >> (u32::from(keepbits) + 1);
    // mask to zero out trailing mantissa bits
    let keep_mask = !(T::MANTISSA_MASK >> u32::from(keepbits));
    // shift to extract the least significant bit of the exponent
    let shift = T::MANITSSA_BITS - u32::from(keepbits);

    let rounded = data
        .iter()
        .map(|x| {
            let mut bits = T::to_unsigned(*x);

            // add ulp/2 with ties to even
            bits += ulp_half + ((bits >> shift) & T::BINARY_ONE);

            // set the trailing bits to zero
            bits &= keep_mask;

            T::from_unsigned(bits)
        })
        .collect();

    Ok(rounded)
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct BitRoundCodec {
    keepbits: u8,
}

impl codecs_core::Codec for BitRoundCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "bit-round";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded = match buf {
            codecs_core::BufferSlice::F32(data) => {
                codecs_core::BufferVec::F32(bit_round(data, self.keepbits)?)
            },
            codecs_core::BufferSlice::F64(data) => {
                codecs_core::BufferVec::F64(bit_round(data, self.keepbits)?)
            },
            buf => {
                return Err(format!(
                    "BitRound::encode does not support the buffer dtype `{}`",
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
        // Unfortunately we need to copy the data here
        let decoded = match buf {
            codecs_core::BufferSlice::F32(data) => codecs_core::BufferVec::F32(Vec::from(data)),
            codecs_core::BufferSlice::F64(data) => codecs_core::BufferVec::F64(Vec::from(data)),
            buf => {
                return Err(format!(
                    "BitRound::decode does not support the buffer dtype `{}`",
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
    /// Codec providing floating-point bit rounding.
    ///
    /// Drops the specified number of bits from the floating point mantissa,
    /// leaving an array that is more amenable to compression. The number of
    /// bits to keep should be determined by information analysis of the data
    /// to be compressed.
    ///
    /// The approach is based on the paper by Klöwer et al. 2021
    /// (https://www.nature.com/articles/s43588-021-00156-2).
    ///
    /// See https://github.com/milankl/BitInformation.jl for the the original
    /// implementation in Julia.
    ///
    /// Args:
    ///     keepbits (int): the number of bits of the mantissa to keep. The
    ///         valid range depends on the dtype of the input data. If
    ///         keepbits is equal to the bitlength of the dtype's mantissa,
    ///         no transformation is performed.
    BitRoundCodec(keepbits)
}

pub trait Float: Sized + Copy {
    const MANITSSA_BITS: u32;
    const MANTISSA_MASK: Self::Unsigned;
    const BINARY_ONE: Self::Unsigned;

    const TY: codecs_core::BufferTy;

    type Unsigned: Copy
        + std::ops::Not<Output = Self::Unsigned>
        + std::ops::Shr<u32, Output = Self::Unsigned>
        + std::ops::Add<Self::Unsigned, Output = Self::Unsigned>
        + std::ops::AddAssign<Self::Unsigned>
        + std::ops::BitAnd<Self::Unsigned, Output = Self::Unsigned>
        + std::ops::BitAndAssign<Self::Unsigned>;

    fn to_unsigned(self) -> Self::Unsigned;
    fn from_unsigned(u: Self::Unsigned) -> Self;
}

impl Float for f32 {
    type Unsigned = u32;

    const BINARY_ONE: Self::Unsigned = 1;
    const MANITSSA_BITS: u32 = Self::MANTISSA_DIGITS - 1;
    const MANTISSA_MASK: Self::Unsigned = (1 << Self::MANITSSA_BITS) - 1;
    const TY: codecs_core::BufferTy = codecs_core::BufferTy::F32;

    fn to_unsigned(self) -> Self::Unsigned {
        self.to_bits()
    }

    fn from_unsigned(u: Self::Unsigned) -> Self {
        Self::from_bits(u)
    }
}

impl Float for f64 {
    type Unsigned = u64;

    const BINARY_ONE: Self::Unsigned = 1;
    const MANITSSA_BITS: u32 = Self::MANTISSA_DIGITS - 1;
    const MANTISSA_MASK: Self::Unsigned = (1 << Self::MANITSSA_BITS) - 1;
    const TY: codecs_core::BufferTy = codecs_core::BufferTy::F64;

    fn to_unsigned(self) -> Self::Unsigned {
        self.to_bits()
    }

    fn from_unsigned(u: Self::Unsigned) -> Self {
        Self::from_bits(u)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_mantissa() {
        assert_eq!(bit_round(&[0.0_f32], 0).unwrap(), vec![0.0_f32]);
        assert_eq!(bit_round(&[1.0_f32], 0).unwrap(), vec![1.0_f32]);
        // tie to even rounds up as the offset exponent is odd
        assert_eq!(bit_round(&[1.5_f32], 0).unwrap(), vec![2.0_f32]);
        assert_eq!(bit_round(&[2.0_f32], 0).unwrap(), vec![2.0_f32]);
        assert_eq!(bit_round(&[2.5_f32], 0).unwrap(), vec![2.0_f32]);
        // tie to even rounds down as the offset exponent is even
        assert_eq!(bit_round(&[3.0_f32], 0).unwrap(), vec![2.0_f32]);
        assert_eq!(bit_round(&[3.5_f32], 0).unwrap(), vec![4.0_f32]);
        assert_eq!(bit_round(&[4.0_f32], 0).unwrap(), vec![4.0_f32]);
        assert_eq!(bit_round(&[5.0_f32], 0).unwrap(), vec![4.0_f32]);
        // tie to even rounds up as the offset exponent is odd
        assert_eq!(bit_round(&[6.0_f32], 0).unwrap(), vec![8.0_f32]);
        assert_eq!(bit_round(&[7.0_f32], 0).unwrap(), vec![8.0_f32]);
        assert_eq!(bit_round(&[8.0_f32], 0).unwrap(), vec![8.0_f32]);

        assert_eq!(bit_round(&[0.0_f64], 0).unwrap(), vec![0.0_f64]);
        assert_eq!(bit_round(&[1.0_f64], 0).unwrap(), vec![1.0_f64]);
        // tie to even rounds up as the offset exponent is odd
        assert_eq!(bit_round(&[1.5_f64], 0).unwrap(), vec![2.0_f64]);
        assert_eq!(bit_round(&[2.0_f64], 0).unwrap(), vec![2.0_f64]);
        assert_eq!(bit_round(&[2.5_f64], 0).unwrap(), vec![2.0_f64]);
        // tie to even rounds down as the offset exponent is even
        assert_eq!(bit_round(&[3.0_f64], 0).unwrap(), vec![2.0_f64]);
        assert_eq!(bit_round(&[3.5_f64], 0).unwrap(), vec![4.0_f64]);
        assert_eq!(bit_round(&[4.0_f64], 0).unwrap(), vec![4.0_f64]);
        assert_eq!(bit_round(&[5.0_f64], 0).unwrap(), vec![4.0_f64]);
        // tie to even rounds up as the offset exponent is odd
        assert_eq!(bit_round(&[6.0_f64], 0).unwrap(), vec![8.0_f64]);
        assert_eq!(bit_round(&[7.0_f64], 0).unwrap(), vec![8.0_f64]);
        assert_eq!(bit_round(&[8.0_f64], 0).unwrap(), vec![8.0_f64]);
    }

    #[test]
    #[allow(clippy::cast_possible_truncation)]
    fn full_mantissa() {
        fn full<T: Float>(x: T) -> T {
            T::from_unsigned(T::to_unsigned(x) + T::MANTISSA_MASK)
        }

        for v in [0.0_f32, 1.0_f32, 2.0_f32, 3.0_f32, 4.0_f32] {
            assert_eq!(
                bit_round(&[full(v)], f32::MANITSSA_BITS as u8).unwrap(),
                vec![full(v)]
            );
        }

        for v in [0.0_f64, 1.0_f64, 2.0_f64, 3.0_f64, 4.0_f64] {
            assert_eq!(
                bit_round(&[full(v)], f64::MANITSSA_BITS as u8).unwrap(),
                vec![full(v)]
            );
        }
    }
}
