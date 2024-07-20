#![allow(clippy::missing_errors_doc)]
#![cfg_attr(not(test), no_main)]

use std::fmt;

// Only included to explicitly enable the `no_wasm_shim` feature for
// sz3-sys/zstd-sys
use zstd_sys as _;

pub fn compress<T: Sz3Element>(
    data: &[T],
    shape: &[usize],
    bound: &ErrorBound,
) -> Result<Vec<u8>, String> {
    let mut encoded = postcard::to_extend(
        &CompressionHeader {
            dtype: <T as Sz3Element>::TY,
            shape: std::borrow::Cow::Borrowed(shape),
        },
        Vec::new(),
    )
    .map_err(|err| format!("Sz3 failed to write header: {err}"))?;

    // sz3::DimensionedDataBuilder cannot handle zero-length dimensions
    if data.is_empty() {
        return Ok(encoded);
    }

    let mut builder = sz3::DimensionedData::build(&data);

    for length in shape {
        // Sz3 ignores dimensions of length 1 and panics on length zero
        // Since they carry no information for Sz3 and we already encode them
        //  in our custom header, we just skip them here
        if *length > 1 {
            builder = builder.dim(*length).map_err(|err| format!("{err}"))?;
        }
    }

    if data.len() == 1 {
        // If there is only one element, all dimensions will have been skipped,
        //  so we explicitly encode one dimension of size 1 here
        builder = builder.dim(1).map_err(|err| format!("{err}"))?;
    }

    let data = builder.finish().map_err(|err| format!("{err}"))?;

    let error_bound = match bound {
        ErrorBound::AbsoluteAndRelative { abs, rel } => sz3::ErrorBound::AbsoluteAndRelative {
            absolute_bound: *abs,
            relative_bound: *rel,
        },
        ErrorBound::AbsoluteOrRelative { abs, rel } => sz3::ErrorBound::AbsoluteOrRelative {
            absolute_bound: *abs,
            relative_bound: *rel,
        },
        ErrorBound::Absolute { abs } => sz3::ErrorBound::Absolute(*abs),
        ErrorBound::Relative { rel } => sz3::ErrorBound::Relative(*rel),
        ErrorBound::PS2NR { psnr } => sz3::ErrorBound::PSNR(*psnr),
        ErrorBound::L2Norm { l2 } => sz3::ErrorBound::L2Norm(*l2),
    };

    // FIXME: Sz3 seems to have a UB bug that impacts the last few bytes but is
    //        somehow gone if we use stdio first ... aaaaaaaah
    std::mem::drop(std::io::Read::read(&mut std::io::stdin(), &mut []));

    // TODO: avoid extra allocation here
    let compressed = sz3::compress(&data, error_bound).map_err(|err| format!("{err}"))?;
    encoded.extend_from_slice(&compressed);

    Ok(encoded)
}

pub fn decompress(data: &[u8]) -> Result<codecs_core::ShapedBuffer, String> {
    let (header, data) = postcard::take_from_bytes::<CompressionHeader>(data)
        .map_err(|err| format!("Sz3 failed to read header: {err}"))?;

    let decoded = if header.shape.iter().copied().product::<usize>() == 0 {
        match header.dtype {
            DType::I32 => codecs_core::BufferVec::I32(Vec::new()),
            DType::I64 => codecs_core::BufferVec::I64(Vec::new()),
            DType::F32 => codecs_core::BufferVec::F32(Vec::new()),
            DType::F64 => codecs_core::BufferVec::F64(Vec::new()),
        }
    } else {
        // TODO: avoid extra allocation here
        match header.dtype {
            DType::I32 => codecs_core::BufferVec::I32(Vec::from(sz3::decompress(data).1.data())),
            DType::I64 => codecs_core::BufferVec::I64(Vec::from(sz3::decompress(data).1.data())),
            DType::F32 => codecs_core::BufferVec::F32(Vec::from(sz3::decompress(data).1.data())),
            DType::F64 => codecs_core::BufferVec::F64(Vec::from(sz3::decompress(data).1.data())),
        }
    };

    Ok(codecs_core::ShapedBuffer {
        shape: header.shape.into_owned(),
        buffer: decoded,
    })
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct Sz3Codec {
    #[serde(flatten)]
    error: ErrorBound,
}

impl codecs_core::Codec for Sz3Codec {
    type DecodedBuffer = codecs_core::VecBuffer;
    type EncodedBuffer = codecs_core::VecBuffer;

    const CODEC_ID: &'static str = "sz3";

    fn from_config<'de, D: serde::Deserializer<'de>>(config: D) -> Result<Self, D::Error> {
        serde::Deserialize::deserialize(config)
    }

    fn encode(
        &self,
        buf: codecs_core::BufferSlice,
        shape: &[usize],
    ) -> Result<codecs_core::ShapedBuffer<Self::EncodedBuffer>, String> {
        let encoded = match buf {
            codecs_core::BufferSlice::I32(data) => compress(data, shape, &self.error)?,
            codecs_core::BufferSlice::I64(data) => compress(data, shape, &self.error)?,
            codecs_core::BufferSlice::F32(data) => compress(data, shape, &self.error)?,
            codecs_core::BufferSlice::F64(data) => compress(data, shape, &self.error)?,
            buf => {
                return Err(format!(
                    "Sz3::encode does not support the buffer dtype `{}`",
                    buf.ty(),
                ))
            },
        };

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
                "Sz3::decode buffer shape {shape:?} is not one-dimensional"
            ));
        }

        let codecs_core::BufferSlice::U8(data) = buf else {
            return Err(format!(
                "Sz3::decode expects buffer dtype `{}` but found `{}`",
                codecs_core::BufferTy::U8,
                buf.ty()
            ));
        };

        decompress(data)
    }

    fn get_config<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serde::Serialize::serialize(&self, serializer)
    }
}

codecs_core_wasm::export_codec! {
    /// Codec providing compression using SZ3.
    ///
    /// Args:
    ///     eb_mode (Literal[
    ///         "abs", "rel", "abs-and-rel", "abs-or-rel", "psnr", "l2",
    ///     ]): SZ3 error bound mode.
    ///     eb_abs (double, optional): absolute error bound.
    ///     eb_rel (double, optional): relative error bound.
    ///     eb_psnr (double, optional): peak signal to noise ratio error bound.
    ///     eb_l2 (double, optional): peak L2 norm error bound.
    Sz3Codec(eb_mode, eb_abs=None, eb_rel=None, eb_psnr=None, eb_l2=None)
}

#[derive(Copy, Clone, serde::Serialize, serde::Deserialize)]
#[repr(u8)]
pub enum DType {
    #[serde(rename = "int32")]
    I32 = 32 | 1,
    #[serde(rename = "int64")]
    I64 = 64 | 1,
    #[serde(rename = "float32")]
    F32 = 32 | 2,
    #[serde(rename = "float64")]
    F64 = 64 | 2,
}

impl fmt::Display for DType {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::I32 => fmt.write_str("int32"),
            Self::I64 => fmt.write_str("int64"),
            Self::F32 => fmt.write_str("float32"),
            Self::F64 => fmt.write_str("float64"),
        }
    }
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
#[serde(tag = "eb_mode")]
#[serde(deny_unknown_fields)]
pub enum ErrorBound {
    #[serde(rename = "abs-and-rel")]
    AbsoluteAndRelative {
        #[serde(rename = "eb_abs")]
        abs: f64,
        #[serde(rename = "eb_rel")]
        rel: f64,
    },
    #[serde(rename = "abs-or-rel")]
    AbsoluteOrRelative {
        #[serde(rename = "eb_abs")]
        abs: f64,
        #[serde(rename = "eb_rel")]
        rel: f64,
    },
    #[serde(rename = "abs")]
    Absolute {
        #[serde(rename = "eb_abs")]
        abs: f64,
    },
    #[serde(rename = "rel")]
    Relative {
        #[serde(rename = "eb_rel")]
        rel: f64,
    },
    #[serde(rename = "psnr")]
    PS2NR {
        #[serde(rename = "eb_psnr")]
        psnr: f64,
    },
    #[serde(rename = "l2")]
    L2Norm {
        #[serde(rename = "eb_l2")]
        l2: f64,
    },
}

#[derive(serde::Serialize, serde::Deserialize)]
struct CompressionHeader<'a> {
    dtype: DType,
    #[serde(borrow)]
    shape: std::borrow::Cow<'a, [usize]>,
}

pub trait Sz3Element: codecs_core::BufferTyBound + sz3::SZ3Compressible {
    const TY: DType;
}

impl Sz3Element for i32 {
    const TY: DType = DType::I32;
}

impl Sz3Element for i64 {
    const TY: DType = DType::I64;
}

impl Sz3Element for f32 {
    const TY: DType = DType::F32;
}

impl Sz3Element for f64 {
    const TY: DType = DType::F64;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_length() -> Result<(), String> {
        let encoded = compress::<f32>(&[], &[1, 27, 0], &ErrorBound::L2Norm { l2: 27.0 })?;
        let decoded = decompress(&encoded)?;

        assert_eq!(decoded.buffer.as_slice().ty(), codecs_core::BufferTy::F32);
        assert!(decoded.buffer.as_slice().is_empty());
        assert_eq!(decoded.shape, vec![1, 27, 0]);

        Ok(())
    }

    #[test]
    fn one_dimensions() -> Result<(), String> {
        let encoded = compress::<i32>(
            &[1, 2, 3, 4],
            &[2, 1, 2, 1],
            &ErrorBound::Absolute { abs: 0.0 },
        )?;
        let decoded = decompress(&encoded)?;

        assert_eq!(decoded.buffer.as_slice().ty(), codecs_core::BufferTy::I32);
        assert_eq!(
            decoded.buffer.as_slice(),
            codecs_core::BufferSlice::I32(&[1, 2, 3, 4])
        );
        assert_eq!(decoded.shape, vec![2, 1, 2, 1]);

        Ok(())
    }

    #[test]
    fn small_state() -> Result<(), String> {
        for data in [
            &[][..],
            &[0.0],
            &[0.0, 1.0],
            &[0.0, 1.0, 0.0],
            &[0.0, 1.0, 0.0, 1.0],
        ] {
            let encoded = compress::<f64>(data, &[data.len()], &ErrorBound::Absolute { abs: 0.0 })?;
            let decoded = decompress(&encoded)?;

            assert_eq!(decoded.buffer.as_slice().ty(), codecs_core::BufferTy::F64);
            assert_eq!(
                decoded.buffer.as_slice(),
                codecs_core::BufferSlice::F64(data)
            );
            assert_eq!(decoded.shape, vec![data.len()]);
        }

        Ok(())
    }
}
