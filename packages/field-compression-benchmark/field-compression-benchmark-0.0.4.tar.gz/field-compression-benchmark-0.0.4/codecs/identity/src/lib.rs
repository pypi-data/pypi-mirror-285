#![cfg_attr(not(test), no_main)]

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct IdentityCodec {
    // empty
}

impl codecs_core::Codec for IdentityCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "identity";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        Ok(codecs_core::ShapedBuffer {
            shape: Vec::from(shape),
            buffer: buf.to_vec(),
        })
    }

    fn decode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::DecodedBuffer>, String> {
        Ok(codecs_core::ShapedBuffer {
            shape: Vec::from(shape),
            buffer: buf.to_vec(),
        })
    }

    fn get_config<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serde::Serialize::serialize(&self, serializer)
    }
}

codecs_core_wasm::export_codec! {
    /// Identity codec which passes through the input unchanged
    /// during encoding and decoding.
    IdentityCodec()
}
