#![allow(clippy::missing_errors_doc)]
#![cfg_attr(not(test), no_main)]

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ReinterpretCodec {
    encode_dtype: codecs_core::BufferTy,
    decode_dtype: codecs_core::BufferTy,
}

impl codecs_core::Codec for ReinterpretCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "reinterpret";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        let codec: Self = serde::Deserialize::deserialize(config)?;

        #[allow(clippy::match_same_arms)]
        match (codec.decode_dtype, codec.encode_dtype) {
            // performing no conversion always works
            (ty_a, ty_b) if ty_a == ty_b => (),
            // converting to bytes always works
            (_, codecs_core::BufferTy::U8) => (),
            // converting from signed / floating to same-size binary always works
            (codecs_core::BufferTy::I16, codecs_core::BufferTy::U16)
            | (
                codecs_core::BufferTy::I32 | codecs_core::BufferTy::F32,
                codecs_core::BufferTy::U32,
            )
            | (
                codecs_core::BufferTy::I64 | codecs_core::BufferTy::F64,
                codecs_core::BufferTy::U64,
            ) => (),
            _ => {
                return Err(serde::de::Error::custom(format!(
                    "reinterpreting {} as {} is not allowed",
                    codec.decode_dtype, codec.encode_dtype,
                )))
            },
        };

        Ok(codec)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        if buf.ty() != self.decode_dtype {
            return Err(format!(
                "Reinterpret::encode buffer dtype `{}` does not match the configured decode_dtype \
                 `{}`",
                buf.ty(),
                self.decode_dtype
            ));
        }

        let (encoded, shape) = match (&buf, self.encode_dtype) {
            (buf, ty) if buf.ty() == ty => (buf.to_vec(), Vec::from(shape)),
            (buf, codecs_core::BufferTy::U8) => {
                let mut shape = Vec::from(shape);
                if let Some(last) = shape.last_mut() {
                    *last *= buf.ty().layout().size();
                }
                (codecs_core::BufferVec::U8(buf.as_bytes().to_vec()), shape)
            },
            (codecs_core::BufferSlice::I16(v), codecs_core::BufferTy::U16) => (
                codecs_core::BufferVec::U16(
                    v.iter()
                        .map(|x| u16::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::I32(v), codecs_core::BufferTy::U32) => (
                codecs_core::BufferVec::U32(
                    v.iter()
                        .map(|x| u32::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::F32(v), codecs_core::BufferTy::U32) => (
                codecs_core::BufferVec::U32(
                    v.iter()
                        .map(|x| u32::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::I64(v), codecs_core::BufferTy::U64) => (
                codecs_core::BufferVec::U64(
                    v.iter()
                        .map(|x| u64::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::F64(v), codecs_core::BufferTy::U64) => (
                codecs_core::BufferVec::U64(
                    v.iter()
                        .map(|x| u64::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (buf, ty) => {
                return Err(format!(
                    "Reinterpret::encode reinterpreting buffer dtype `{}` as `{ty}` is not allowed",
                    buf.ty(),
                ));
            },
        };

        Ok(codecs_core::ShapedBuffer {
            shape,
            buffer: encoded,
        })
    }

    fn decode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::DecodedBuffer>, String> {
        if buf.ty() != self.encode_dtype {
            return Err(format!(
                "Reinterpret::decode buffer dtype `{}` does not match the configured encode_dtype \
                 `{}`",
                buf.ty(),
                self.encode_dtype
            ));
        }

        let (decoded, shape) = match (&buf, self.decode_dtype) {
            (buf, ty) if buf.ty() == ty => (buf.to_vec(), Vec::from(shape)),
            (codecs_core::BufferSlice::U8(v), ty) => {
                let mut shape = Vec::from(shape);
                if let Some(last) = shape.last_mut() {
                    if *last % ty.layout().size() != 0 {
                        return Err(format!(
                            "Reinterpret::decode byte buffer with shape {shape:?} cannot be \
                             reinterpreted as {ty}"
                        ));
                    }

                    *last /= ty.layout().size();
                }
                let mut buffer =
                    codecs_core::BufferVec::zeros_with_ty_len(ty, v.len() / ty.layout().size());
                #[allow(unsafe_code)]
                // Safety: buffer is v.len() bytes long and propely aligned for ty
                unsafe {
                    std::ptr::copy_nonoverlapping(
                        v.as_ptr(),
                        buffer.as_slice_mut().as_bytes_mut().as_mut_ptr().cast(),
                        v.len(),
                    );
                }
                (buffer, shape)
            },
            (codecs_core::BufferSlice::U16(v), codecs_core::BufferTy::I16) => (
                codecs_core::BufferVec::I16(
                    v.iter()
                        .map(|x| i16::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::U32(v), codecs_core::BufferTy::I32) => (
                codecs_core::BufferVec::I32(
                    v.iter()
                        .map(|x| i32::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::U32(v), codecs_core::BufferTy::F32) => (
                codecs_core::BufferVec::F32(
                    v.iter()
                        .map(|x| f32::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::U64(v), codecs_core::BufferTy::I64) => (
                codecs_core::BufferVec::I64(
                    v.iter()
                        .map(|x| i64::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (codecs_core::BufferSlice::U64(v), codecs_core::BufferTy::F64) => (
                codecs_core::BufferVec::F64(
                    v.iter()
                        .map(|x| f64::from_ne_bytes(x.to_ne_bytes()))
                        .collect(),
                ),
                Vec::from(shape),
            ),
            (buf, ty) => {
                return Err(format!(
                    "Reinterpret::decode reinterpreting buffer dtype `{}` as `{ty}` is not allowed",
                    buf.ty(),
                ));
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
    /// Codec to reinterpret data between different compatible types.
    /// Note that no conversion happens, only the meaning of the bits changes.
    ///
    /// Args:
    ///     encode_dtype (dtype): Data type to use for encoded data.
    ///     decode_dtype (dtype): Data type to use for decoded data.
    ReinterpretCodec(encode_dtype, decode_dtype)
}
