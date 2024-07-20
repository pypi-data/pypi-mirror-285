use std::{borrow::Cow, fmt, ops::ControlFlow};

use pyo3::{
    prelude::*,
    types::{IntoPyDict, PyDict},
};
use vecmap::VecMap;

use core_error::LocationError;

use crate::parameter::{
    ConcreteParameter, ConcreteParameterSummary, Parameter, ParameterEvalContext,
    ParameterEvalError, ParameterIterator,
};

mod config;
pub(super) use config::CodecSeed;

#[derive(Debug, Clone)]
pub struct Codec {
    name: String,
    import_path: String,
    kind: CodecKind,
    parameters: VecMap<String, Parameter>,
}

impl Codec {
    pub fn import_py<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, numcodecs_python::CodecClass>, LocationError<PyErr>> {
        let mut locals = Vec::new();
        for (pos, c) in self.import_path.char_indices() {
            if c == '.' {
                if let Some(module) = self.import_path.get(..pos) {
                    locals.push((module, py.import_bound(module)?));
                }
            }
        }
        let locals = locals.into_py_dict_bound(py);

        py.eval_bound(&self.import_path, None, Some(&locals))?
            .extract()
            .map_err(LocationError::new)
    }

    #[must_use]
    pub fn cyclic_iter_concrete(&self) -> ConcreteCodecIterator {
        let parameters = self
            .parameters
            .values()
            .map(Parameter::cyclic_iter)
            .collect::<Vec<_>>();

        ConcreteCodecIterator {
            codec: self,
            parameters,
        }
    }

    pub fn minimise(&mut self) {
        self.parameters.values_mut().for_each(Parameter::minimise);
    }

    #[must_use]
    pub fn name(&self) -> &str {
        &self.name
    }

    #[must_use]
    pub fn import_path(&self) -> &str {
        &self.import_path
    }

    #[must_use]
    pub const fn kind(&self) -> CodecKind {
        self.kind
    }
}

impl fmt::Display for Codec {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        let name = match self.import_path.rsplit_once('.') {
            Some((_, name)) => name,
            None => &*self.import_path,
        };

        fmt.write_fmt(format_args!("{name}("))?;

        for (i, (name, value)) in self.parameters.iter().enumerate() {
            if i > 0 {
                fmt.write_str(", ")?;
            }

            fmt.write_fmt(format_args!("{name}={value}"))?;
        }

        fmt.write_str(")")
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum CodecKind {
    BinaryLossless,
    SymbolicLossless,
    Lossy,
}

impl fmt::Display for CodecKind {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::BinaryLossless => fmt.write_str("binary-lossless"),
            Self::SymbolicLossless => fmt.write_str("symbolic-lossless"),
            Self::Lossy => fmt.write_str("lossy"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct ConcreteCodec<'a> {
    codec: &'a Codec,
    parameters: Vec<ConcreteParameter<'a>>,
}

impl<'a> ConcreteCodec<'a> {
    pub fn build_py<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, numcodecs_python::Codec>, LocationError<PyErr>> {
        let py_codec = self.codec.import_py(py)?;

        let config = PyDict::new_bound(py);

        for (name, parameter) in self.codec.parameters.keys().zip(self.parameters.iter()) {
            match parameter {
                ConcreteParameter::Int { value } => {
                    config.set_item(name, *value)?;
                },
                ConcreteParameter::Float { value } => {
                    config.set_item(name, *value)?;
                },
                ConcreteParameter::Str { value } => {
                    config.set_item(name, value)?;
                },
            }
        }

        numcodecs_python::CodecClassMethods::codec_from_config(&py_codec, config.as_borrowed())
            .map_err(LocationError::new)
    }

    #[must_use]
    pub fn import_path(&self) -> &str {
        self.codec.import_path()
    }

    #[must_use]
    pub const fn kind(&self) -> CodecKind {
        self.codec.kind()
    }

    pub fn parameters(&self) -> impl Iterator<Item = (&str, &ConcreteParameter<'a>)> {
        self.codec
            .parameters
            .iter()
            .zip(self.parameters.iter())
            .map(|((name, _), concrete)| (&**name, concrete))
    }

    #[must_use]
    pub fn summary(&self) -> ConcreteCodecSummary<'a> {
        ConcreteCodecSummary {
            import_path: Cow::Borrowed(self.codec.import_path.as_str()),
            kind: self.codec.kind,
            parameters: self
                .codec
                .parameters
                .keys()
                .map(|name| Cow::Borrowed(name.as_str()))
                .zip(self.parameters.iter().map(ConcreteParameter::summary))
                .collect(),
        }
    }
}

impl<'a> fmt::Display for ConcreteCodec<'a> {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        let name = match self.codec.import_path.rsplit_once('.') {
            Some((_, name)) => name,
            None => &*self.codec.import_path,
        };

        fmt.write_fmt(format_args!("{name}("))?;

        for (i, (name, value)) in self
            .codec
            .parameters
            .keys()
            .zip(self.parameters.iter())
            .enumerate()
        {
            if i > 0 {
                fmt.write_str(", ")?;
            }

            fmt.write_fmt(format_args!("{name}={value}"))?;
        }

        fmt.write_str(")")
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
#[serde(rename = "Codec")]
#[serde(deny_unknown_fields)]
pub struct ConcreteCodecSummary<'a> {
    #[serde(borrow)]
    import_path: Cow<'a, str>,
    kind: CodecKind,
    #[serde(borrow)]
    parameters: VecMap<Cow<'a, str>, ConcreteParameterSummary<'a>>,
}

pub struct ConcreteCodecIterator<'a> {
    codec: &'a Codec,
    parameters: Vec<ParameterIterator<'a>>,
}

impl<'a> ConcreteCodecIterator<'a> {
    pub fn next(
        &mut self,
        eval_context: &mut ParameterEvalContext,
    ) -> Result<ControlFlow<ConcreteCodec<'a>, ConcreteCodec<'a>>, ParameterEvalError> {
        let mut all_done = true;

        #[allow(clippy::needless_collect)]
        // we must not short-circuit early to ensure further iteration is not broken
        let parameters = self
            .codec
            .parameters
            .keys()
            .zip(self.parameters.iter_mut())
            .map(|(name, param)| -> Result<_, ParameterEvalError> {
                let param = if all_done {
                    match param.next(self.codec.name(), name, eval_context)? {
                        ControlFlow::Break(value) => value,
                        ControlFlow::Continue(value) => {
                            all_done = false;
                            value
                        },
                    }
                } else {
                    param.get(self.codec.name(), name, eval_context)?
                };

                eval_context.set_value(self.codec.name(), name, &param)?;

                Ok(param)
            })
            .collect::<Vec<_>>();

        let iter = ConcreteCodec {
            codec: self.codec,
            parameters: parameters.into_iter().collect::<Result<Vec<_>, _>>()?,
        };

        if all_done {
            Ok(ControlFlow::Break(iter))
        } else {
            Ok(ControlFlow::Continue(iter))
        }
    }

    pub fn get(
        &self,
        eval_context: &mut ParameterEvalContext,
    ) -> Result<ConcreteCodec<'a>, ParameterEvalError> {
        let parameters = self
            .codec
            .parameters
            .keys()
            .zip(self.parameters.iter())
            .map(|(name, param)| -> Result<_, ParameterEvalError> {
                let param = ParameterIterator::get(param, self.codec.name(), name, eval_context)?;

                eval_context.set_value(self.codec.name(), name, &param)?;

                Ok(param)
            })
            .collect::<Result<Vec<_>, _>>()?;

        Ok(ConcreteCodec {
            codec: self.codec,
            parameters,
        })
    }
}
