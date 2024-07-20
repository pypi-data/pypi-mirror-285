#![cfg_attr(not(test), no_main)]

// Only used to explicitly enable the `no_wasm_shim` feature in zstd/zstd-sys
use zstd_sys as _;

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ZstdCodec {
    level: ZstdLevel,
}

impl codecs_core::Codec for ZstdCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "zstd";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let mut encoded = postcard::to_extend(
            &CompressionHeader {
                dtype: buf.ty(),
                shape: std::borrow::Cow::Borrowed(shape),
            },
            Vec::new(),
        )
        .map_err(|err| format!("Zstd failed to write header: {err}"))?;

        zstd::stream::copy_encode(buf.as_bytes(), &mut encoded, self.level.into())
            .map_err(|err| format!("{err}"))?;

        Ok(codecs_core::ShapedBuffer {
            shape: vec![encoded.len()],
            buffer: codecs_core::BufferVec::U8(encoded),
        })
    }

    fn decode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::DecodedBuffer>, String> {
        if !matches!(shape, [_]) {
            return Err(format!(
                "Zstd::decode buffer shape {shape:?} is not one-dimensional"
            ));
        }

        let codecs_core::BufferSlice::U8(data) = buf else {
            return Err(format!(
                "Zstd::decode expects buffer dtype `{}` but found `{}`",
                codecs_core::BufferTy::U8,
                buf.ty()
            ));
        };

        let (header, data) = postcard::take_from_bytes::<CompressionHeader>(data)
            .map_err(|err| format!("Zstd failed to read header: {err}"))?;

        let mut decoded =
            codecs_core::BufferVec::zeros_with_ty_len(header.dtype, header.shape.iter().product());
        let mut decoded_bytes = decoded.as_slice_mut();
        let mut decoded_bytes = decoded_bytes.as_bytes_mut();

        zstd::stream::copy_decode(data, &mut decoded_bytes).map_err(|err| format!("{err}"))?;

        if !decoded_bytes.is_empty() {
            return Err(String::from("Zstd::decode did not produce enough data"));
        }

        Ok(codecs_core::ShapedBuffer {
            shape: header.shape.into_owned(),
            buffer: decoded,
        })
    }

    fn get_config<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serde::Serialize::serialize(&self, serializer)
    }
}

codecs_core_wasm::export_codec! {
    /// Codec providing compression using ZSTD.
    ///
    /// Args:
    ///     level (int): compression level (1-22)
    ZstdCodec(level)
}

#[derive(Clone, Copy)]
struct ZstdLevel {
    level: zstd::zstd_safe::CompressionLevel,
}

impl From<ZstdLevel> for zstd::zstd_safe::CompressionLevel {
    fn from(level: ZstdLevel) -> Self {
        level.level
    }
}

impl serde::Serialize for ZstdLevel {
    fn serialize<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        self.level.serialize(serializer)
    }
}

impl<'de> serde::Deserialize<'de> for ZstdLevel {
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        let level = serde::Deserialize::deserialize(deserializer)?;

        let level_range = zstd::compression_level_range();

        if !level_range.contains(&level) {
            return Err(serde::de::Error::custom(format!(
                "level {level} is not in {}..={}",
                level_range.start(),
                level_range.end()
            )));
        }

        Ok(Self { level })
    }
}

#[derive(serde::Serialize, serde::Deserialize)]
struct CompressionHeader<'a> {
    dtype: codecs_core::BufferTy,
    #[serde(borrow)]
    shape: std::borrow::Cow<'a, [usize]>,
}
