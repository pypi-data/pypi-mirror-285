use std::{borrow::Cow, fmt};

#[allow(clippy::module_name_repetitions)]
#[derive(serde::Serialize, serde::Deserialize)]
#[serde(rename = "Codec")]
#[serde(bound = "")]
pub struct CodecConfig<'a, C: codecs_core::Codec> {
    #[serde(default = "CodecId::new")]
    pub id: CodecId<C>,
    #[serde(flatten)]
    #[serde(serialize_with = "serialize_codec_config")]
    #[serde(deserialize_with = "deserialize_codec_from_config")]
    pub codec: Cow<'a, C>,
}

#[allow(clippy::trivially_copy_pass_by_ref)]
fn serialize_codec_config<C: codecs_core::Codec, S: serde::Serializer>(
    #[allow(clippy::ptr_arg)] codec: &Cow<C>,
    serializer: S,
) -> Result<S::Ok, S::Error> {
    codecs_core::Codec::get_config(&**codec, serializer)
}

fn deserialize_codec_from_config<'a, 'de, C: codecs_core::Codec, D: serde::Deserializer<'de>>(
    config: D,
) -> Result<Cow<'a, C>, D::Error> {
    codecs_core::Codec::from_config(config).map(Cow::Owned)
}

pub struct CodecId<C: codecs_core::Codec> {
    _marker: core::marker::PhantomData<C>,
}

impl<C: codecs_core::Codec> CodecId<C> {
    #[must_use]
    pub const fn new() -> Self {
        Self {
            _marker: core::marker::PhantomData::<C>,
        }
    }
}

impl<C: codecs_core::Codec> Default for CodecId<C> {
    #[must_use]
    fn default() -> Self {
        Self::new()
    }
}

impl<C: codecs_core::Codec> serde::Serialize for CodecId<C> {
    fn serialize<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_unit_variant("CodecId", 0, C::CODEC_ID)
    }
}

impl<'de, C: codecs_core::Codec> serde::Deserialize<'de> for CodecId<C> {
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct CodecIdIdentifierVisitor<C: codecs_core::Codec> {
            _marker: core::marker::PhantomData<C>,
        }

        impl<'de, C: codecs_core::Codec> serde::de::Visitor<'de> for CodecIdIdentifierVisitor<C> {
            type Value = ();

            fn expecting(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
                fmt.write_str("codec id")
            }

            fn visit_str<E: serde::de::Error>(self, v: &str) -> Result<Self::Value, E> {
                if v == C::CODEC_ID {
                    Ok(())
                } else {
                    Err(serde::de::Error::custom(format!("unknown codec id `{v}`")))
                }
            }

            fn visit_bytes<E: serde::de::Error>(self, v: &[u8]) -> Result<Self::Value, E> {
                if v == C::CODEC_ID.as_bytes() {
                    Ok(())
                } else {
                    let v = String::from_utf8_lossy(v);
                    Err(serde::de::Error::custom(format!("unknown codec id `{v}`")))
                }
            }
        }

        impl<'de, C: codecs_core::Codec> serde::de::DeserializeSeed<'de> for CodecIdIdentifierVisitor<C> {
            type Value = ();

            #[inline]
            fn deserialize<D: serde::Deserializer<'de>>(
                self,
                deserializer: D,
            ) -> Result<Self::Value, D::Error> {
                serde::Deserializer::deserialize_identifier(deserializer, self)
            }
        }

        struct CodecIdVisitor<C: codecs_core::Codec> {
            _marker: core::marker::PhantomData<C>,
        }

        impl<'de, C: codecs_core::Codec> serde::de::Visitor<'de> for CodecIdVisitor<C> {
            type Value = CodecId<C>;

            fn expecting(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
                fmt.write_str("codec id")
            }

            fn visit_enum<A: serde::de::EnumAccess<'de>>(
                self,
                data: A,
            ) -> Result<Self::Value, A::Error> {
                let ((), variant) = serde::de::EnumAccess::variant_seed(
                    data,
                    CodecIdIdentifierVisitor {
                        _marker: core::marker::PhantomData::<C>,
                    },
                )?;
                serde::de::VariantAccess::unit_variant(variant)?;

                Ok(CodecId {
                    _marker: core::marker::PhantomData::<C>,
                })
            }
        }

        serde::Deserializer::deserialize_enum(
            deserializer,
            "CodecId",
            &[C::CODEC_ID],
            CodecIdVisitor {
                _marker: core::marker::PhantomData::<C>,
            },
        )
    }
}
