#![allow(clippy::missing_errors_doc)]
#![cfg_attr(not(test), no_main)]

pub fn compress(
    buf: codecs_core::BufferSlice,
    shape: &[usize],
    level: ZlibLevel,
) -> Result<Vec<u8>, String> {
    let data = buf.as_bytes();

    let mut encoded = postcard::to_extend(
        &CompressionHeader {
            dtype: buf.ty(),
            shape: std::borrow::Cow::Borrowed(shape),
        },
        Vec::new(),
    )
    .map_err(|err| format!("Zlib::encode failed to write header: {err}"))?;

    let mut in_pos = 0;
    let mut out_pos = encoded.len();

    // The comp flags function sets the zlib flag if the window_bits parameter
    //  is > 0.
    let flags =
        miniz_oxide::deflate::core::create_comp_flags_from_zip_params((level as u8).into(), 1, 0);
    let mut compressor = miniz_oxide::deflate::core::CompressorOxide::new(flags);
    encoded.resize(encoded.len() + (data.len() / 2).max(2), 0);

    loop {
        let (Some(data_left), Some(encoded_left)) =
            (data.get(in_pos..), encoded.get_mut(out_pos..))
        else {
            return Err(String::from(
                "Zlib::encode bug: input or output out of bounds",
            ));
        };

        let (status, bytes_in, bytes_out) = miniz_oxide::deflate::core::compress(
            &mut compressor,
            data_left,
            encoded_left,
            miniz_oxide::deflate::core::TDEFLFlush::Finish,
        );

        out_pos += bytes_out;
        in_pos += bytes_in;

        match status {
            miniz_oxide::deflate::core::TDEFLStatus::Okay => {
                // We need more space, so resize the vector.
                if encoded.len().saturating_sub(out_pos) < 30 {
                    encoded.resize(encoded.len() * 2, 0);
                }
            },
            miniz_oxide::deflate::core::TDEFLStatus::Done => {
                encoded.truncate(out_pos);

                if in_pos != data.len() {
                    return Err(String::from(
                        "Zlib::encode consumed less input than expected",
                    ));
                }

                return Ok(encoded);
            },
            err => return Err(format!("Zlib::encode bug: {err:?}")),
        }
    }
}

pub fn decompress(data: &[u8]) -> Result<(codecs_core::BufferVec, Vec<usize>), String> {
    let (header, data) = postcard::take_from_bytes::<CompressionHeader>(data)
        .map_err(|err| format!("Zlib::decode failed to read header: {err}"))?;

    let mut decoded =
        codecs_core::BufferVec::zeros_with_ty_len(header.dtype, header.shape.iter().product());
    let mut decoded_bytes = decoded.as_slice_mut();
    let decoded_bytes = decoded_bytes.as_bytes_mut();

    let flags = miniz_oxide::inflate::core::inflate_flags::TINFL_FLAG_PARSE_ZLIB_HEADER
        | miniz_oxide::inflate::core::inflate_flags::TINFL_FLAG_USING_NON_WRAPPING_OUTPUT_BUF;

    let mut decomp = Box::<miniz_oxide::inflate::core::DecompressorOxide>::default();

    let (status, in_consumed, out_consumed) =
        miniz_oxide::inflate::core::decompress(&mut decomp, data, decoded_bytes, 0, flags);

    match status {
        miniz_oxide::inflate::TINFLStatus::Done => {
            if in_consumed != data.len() {
                Err(String::from(
                    "Zlib::decode consumed less data than expected",
                ))
            } else if out_consumed == decoded_bytes.len() {
                Ok((decoded, header.shape.into_owned()))
            } else {
                Err(String::from(
                    "Zlib::decode produced more data than expected",
                ))
            }
        },
        miniz_oxide::inflate::TINFLStatus::HasMoreOutput => Err(String::from(
            "Zlib::decode produced less data than expected",
        )),
        _ => Err(format!(
            "{}",
            miniz_oxide::inflate::DecompressError {
                status,
                output: Vec::new()
            }
        )),
    }
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ZlibCodec {
    level: ZlibLevel,
}

impl codecs_core::Codec for ZlibCodec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "zlib";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded = compress(buf, shape, self.level)?;

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
                "Zlib::decode buffer shape {shape:?} is not one-dimensional"
            ));
        }

        let codecs_core::BufferSlice::U8(data) = buf else {
            return Err(format!(
                "Zlib::decode expects buffer dtype `{}` but found `{}`",
                codecs_core::BufferTy::U8,
                buf.ty()
            ));
        };

        let (decoded, shape) = decompress(data)?;

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
    /// Codec providing compression using Codec Zlib.
    ///
    /// Args:
    ///     level (int): compression level (0-9)
    ZlibCodec(level)
}

#[derive(Copy, Clone, serde_repr::Serialize_repr, serde_repr::Deserialize_repr)]
#[repr(u8)]
pub enum ZlibLevel {
    ZNoCompression = 0,
    ZBestSpeed = 1,
    ZLevel2 = 2,
    ZLevel3 = 3,
    ZLevel4 = 4,
    ZLevel5 = 5,
    ZLevel6 = 6,
    ZLevel7 = 7,
    ZLevel8 = 8,
    ZBestCompression = 9,
}

#[derive(serde::Serialize, serde::Deserialize)]
struct CompressionHeader<'a> {
    dtype: codecs_core::BufferTy,
    #[serde(borrow)]
    shape: std::borrow::Cow<'a, [usize]>,
}
