#![cfg_attr(not(test), no_main)]

#[must_use]
pub fn bit_transpose<T: Float>(data: &[T]) -> Vec<T::Unsigned> {
    // Adapted from Milan Klöwer's BitInformation.jl's bittranspose
    //  (MIT licensed)
    // https://github.com/milankl/BitInformation.jl/blob/9a599e343bc127f73b6b1f77ac497a829d0a4a5f/src/bittranspose.jl#L3-L54

    let mut transposed = vec![T::ZERO; data.len()];

    // Iterate over the data slice first, then change bit-position
    // While the data slice has to be read nbits-times, the bits
    //  are output in append-only order
    (1..=T::NBITS)
        .flat_map(|bi| {
            // Create a mask to extract the bi-th bit
            let mask = T::ONE << (T::NBITS - bi);

            // Iterate over the data slice and extract every bi-th bit
            //  as either 0b0 or 0b1
            data.iter()
                .map(move |d| (T::to_unsigned(*d) & mask) >> (T::NBITS - bi))
        })
        // Accumulate the flattened bit stream into a continuous shift register
        .scan(T::ZERO, |acc, bit| {
            *acc = ((*acc << 1) & T::INV_ONE_MASK) | bit;
            Some(*acc)
        })
        // Read the shift register every nbits, i.e. when a full element has been written
        // Note: we first need to skip nbits-1 to extract every k*nbits where k>0 element
        .skip((T::NBITS as usize) - 1)
        .step_by(T::NBITS as usize)
        // Write the packed elements into the mutable output slice
        .zip(transposed.iter_mut())
        .for_each(|(packed, transposed)| *transposed = packed);

    transposed
}

#[must_use]
pub fn bit_inverse_transpose<T: Float>(data: &[T::Unsigned]) -> Vec<T> {
    // Adapted from Milan Klöwer's BitInformation.jl's bitbacktranspose
    //  (MIT licensed)
    // https://github.com/milankl/BitInformation.jl/blob/9a599e343bc127f73b6b1f77ac497a829d0a4a5f/src/bittranspose.jl#L65-L114

    let mut de_transposed = vec![T::from_unsigned(T::ZERO); data.len()];

    // Iterate over the bit-position first, then the data slice
    // While the output slice has to be written nbits-times, the
    //  packed bits are read in linear order
    data.iter()
        // Iterate over the bitstream of the transposed / packed data slice
        .flat_map(|packed| (1..=T::NBITS).map(|bi| (*packed >> (T::NBITS - bi)) & T::ONE))
        // Zip with iteration over the output slice first and the bit offsets second
        .zip((1..=T::NBITS).flat_map(|bo| (0..data.len()).map(move |idx| (idx, bo))))
        // Re-accumulate each element's bits across nbits passes over the output slice
        .try_for_each(|(bit, (idx, bo))| {
            de_transposed.get_mut(idx).map(|de_transposed| {
                *de_transposed =
                    T::from_unsigned(T::to_unsigned(*de_transposed) | (bit << (T::NBITS - bo)));
            })
        });

    de_transposed
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct BitTransposeCodec {
    // empty
}

impl codecs_core::Codec for BitTransposeCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "bit-transpose";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded = match buf {
            codecs_core::BufferSlice::F32(data) => codecs_core::BufferVec::U32(bit_transpose(data)),
            codecs_core::BufferSlice::F64(data) => codecs_core::BufferVec::U64(bit_transpose(data)),
            buf => {
                return Err(format!(
                    "BitTranspose::encode does not support the buffer dtype `{}`",
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
            codecs_core::BufferSlice::U32(data) => {
                codecs_core::BufferVec::F32(bit_inverse_transpose(data))
            },
            codecs_core::BufferSlice::U64(data) => {
                codecs_core::BufferVec::F64(bit_inverse_transpose(data))
            },
            buf => {
                return Err(format!(
                    "BitTranspose::decode does not support the buffer dtype `{}`",
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
    /// Codec to transpose floating point data to co-locate every i-th bit
    /// of every data element.
    BitTransposeCodec()
}

pub trait Float: Copy {
    type Unsigned: Copy
        + std::ops::Shl<u32, Output = Self::Unsigned>
        + std::ops::Shr<u32, Output = Self::Unsigned>
        + std::ops::BitAnd<Output = Self::Unsigned>
        + std::ops::BitOr<Output = Self::Unsigned>;

    const ZERO: Self::Unsigned;
    const ONE: Self::Unsigned;
    const INV_ONE_MASK: Self::Unsigned;
    const NBITS: u32;

    fn to_unsigned(self) -> Self::Unsigned;
    fn from_unsigned(u: Self::Unsigned) -> Self;
}

impl Float for f32 {
    type Unsigned = u32;

    const INV_ONE_MASK: Self::Unsigned = u32::MAX - 1;
    const NBITS: u32 = u32::BITS;
    const ONE: Self::Unsigned = 1;
    const ZERO: Self::Unsigned = 0;

    fn to_unsigned(self) -> Self::Unsigned {
        self.to_bits()
    }

    fn from_unsigned(u: Self::Unsigned) -> Self {
        Self::from_bits(u)
    }
}

impl Float for f64 {
    type Unsigned = u64;

    const INV_ONE_MASK: Self::Unsigned = u64::MAX - 1;
    const NBITS: u32 = u64::BITS;
    const ONE: Self::Unsigned = 1;
    const ZERO: Self::Unsigned = 0;

    fn to_unsigned(self) -> Self::Unsigned {
        self.to_bits()
    }

    fn from_unsigned(u: Self::Unsigned) -> Self {
        Self::from_bits(u)
    }
}
