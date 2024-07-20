use std::{borrow::Cow, convert::Infallible, fmt};

use pyo3::{
    exceptions::{PyKeyboardInterrupt, PyRuntimeError},
    prelude::*,
};
use thiserror::Error;

use core_error::LocationError;
use core_measure::stats::AnalysisError;

#[derive(Debug, thiserror::Error)]
pub enum BenchmarkSingleCaseError {
    #[error("failed to execute Python code")]
    Python(#[source] LocationError<PyErr>),
    #[error("failed to analyse some measurements")]
    Analysis(#[source] LocationError<AnalysisError>),
}

impl From<PyErr> for BenchmarkSingleCaseError {
    #[track_caller]
    fn from(err: PyErr) -> Self {
        Self::Python(err.into())
    }
}

impl From<AnalysisError> for BenchmarkSingleCaseError {
    #[track_caller]
    fn from(err: AnalysisError) -> Self {
        Self::Analysis(err.into())
    }
}

impl From<Infallible> for BenchmarkSingleCaseError {
    fn from(err: Infallible) -> Self {
        match err {}
    }
}

impl From<LocationError<PyErr>> for BenchmarkSingleCaseError {
    fn from(err: LocationError<PyErr>) -> Self {
        Self::Python(err)
    }
}

impl From<LocationError<AnalysisError>> for BenchmarkSingleCaseError {
    fn from(err: LocationError<AnalysisError>) -> Self {
        Self::Analysis(err)
    }
}

impl From<LocationError<Infallible>> for BenchmarkSingleCaseError {
    fn from(err: LocationError<Infallible>) -> Self {
        err.infallible()
    }
}

impl From<BenchmarkSingleCaseError> for PyErr {
    fn from(err: BenchmarkSingleCaseError) -> Self {
        match err {
            BenchmarkSingleCaseError::Analysis(analysis) => Python::with_gil(|py| {
                let err = PyRuntimeError::new_err("failed to analyse the measurments");
                err.set_cause(py, Some(PyRuntimeError::new_err(format!("{analysis:?}"))));
                err
            }),
            BenchmarkSingleCaseError::Python(python) => Python::with_gil(|py| {
                let err = PyRuntimeError::new_err("failed to execute Python code");
                err.set_cause(py, Some(python.into_error()));
                err
            }),
        }
    }
}

#[derive(Debug, Clone, Error)]
pub enum BenchmarkCaseError {
    #[error("failed to execute Python code")]
    Python(#[source] LocationError<PyErrString>),
    #[error("failed to analyse some measurements")]
    Analysis(#[source] LocationError<StringifiedError>),
    #[error("failed to distribute a benchmark case")]
    Distributed(#[source] LocationError<StringifiedError>),
}

// FIXME: eliminate extraneous clones
impl serde::Serialize for BenchmarkCaseError {
    fn serialize<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        if serializer.is_human_readable() {
            match self {
                Self::Python(source) => BenchmarkCaseErrorHumanReadable::Python(source.clone()),
                Self::Analysis(source) => BenchmarkCaseErrorHumanReadable::Analysis(source.clone()),
                Self::Distributed(source) => {
                    BenchmarkCaseErrorHumanReadable::Distributed(source.clone())
                },
            }
            .serialize(serializer)
        } else {
            match self {
                Self::Python(source) => BenchmarkCaseErrorBinary::Python {
                    python: source.clone(),
                },
                Self::Analysis(source) => BenchmarkCaseErrorBinary::Analysis {
                    analysis: source.clone(),
                },
                Self::Distributed(source) => BenchmarkCaseErrorBinary::Distributed {
                    distributed: source.clone(),
                },
            }
            .serialize(serializer)
        }
    }
}

impl<'de> serde::Deserialize<'de> for BenchmarkCaseError {
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        if deserializer.is_human_readable() {
            match BenchmarkCaseErrorHumanReadable::deserialize(deserializer)? {
                BenchmarkCaseErrorHumanReadable::Python(source) => Ok(Self::Python(source)),
                BenchmarkCaseErrorHumanReadable::Analysis(source) => Ok(Self::Analysis(source)),
                BenchmarkCaseErrorHumanReadable::Distributed(source) => {
                    Ok(Self::Distributed(source))
                },
            }
        } else {
            match BenchmarkCaseErrorBinary::deserialize(deserializer)? {
                BenchmarkCaseErrorBinary::Python { python } => Ok(Self::Python(python)),
                BenchmarkCaseErrorBinary::Analysis { analysis } => Ok(Self::Analysis(analysis)),
                BenchmarkCaseErrorBinary::Distributed { distributed } => {
                    Ok(Self::Distributed(distributed))
                },
            }
        }
    }
}

#[derive(serde::Serialize, serde::Deserialize)]
#[serde(rename = "BenchmarkCaseError")]
#[serde(rename_all = "kebab-case")]
enum BenchmarkCaseErrorHumanReadable {
    Python(LocationError<PyErrString>),
    Analysis(LocationError<StringifiedError>),
    Distributed(LocationError<StringifiedError>),
}

#[derive(serde::Serialize, serde::Deserialize)]
#[serde(rename = "BenchmarkCaseError")]
enum BenchmarkCaseErrorBinary {
    Python {
        python: LocationError<PyErrString>,
    },
    Analysis {
        analysis: LocationError<StringifiedError>,
    },
    Distributed {
        distributed: LocationError<StringifiedError>,
    },
}

#[derive(Debug, Clone, Error, serde::Serialize, serde::Deserialize)]
#[serde(transparent)]
#[error("{0}")]
pub struct StringError(pub String);

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct StringifiedError {
    message: String,
    source: Option<StringError>,
}

impl StringifiedError {
    #[must_use]
    pub const fn from_string(message: String) -> Self {
        Self {
            message,
            source: None,
        }
    }

    #[must_use]
    pub fn from_err<E: std::error::Error>(err: E) -> Self {
        let message = format!("{err}");
        let source =
            std::error::Error::source(&err).map(|source| StringError(format!("{source:#}")));

        Self { message, source }
    }
}

impl fmt::Display for StringifiedError {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        fmt.write_str(&self.message)
    }
}

impl std::error::Error for StringifiedError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        #[allow(clippy::option_if_let_else)]
        match &self.source {
            None => None,
            Some(source) => Some(source),
        }
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
#[serde(rename = "PyErr")]
#[serde(deny_unknown_fields)]
pub struct PyErrString {
    pub r#type: String,
    pub message: String,
    pub traceback: Option<StringError>,
}

impl fmt::Display for PyErrString {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        write!(fmt, "{}: {}", self.r#type, self.message)
    }
}

impl std::error::Error for PyErrString {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        self.traceback
            .as_ref()
            .map(|err| err as &dyn std::error::Error)
    }
}

impl From<BenchmarkSingleCaseError> for BenchmarkCaseError {
    fn from(err: BenchmarkSingleCaseError) -> Self {
        match err {
            BenchmarkSingleCaseError::Python(err) => Python::with_gil(|py| {
                let err = err.map(|err| {
                    let value = err.value_bound(py);

                    let r#type = String::from(
                        value
                            .get_type()
                            .name()
                            .unwrap_or(Cow::Borrowed("<exception type() failed>")),
                    );
                    let message = value.str().map_or_else(
                        |_| String::from("<exception str() failed>"),
                        |s| s.to_string_lossy().into_owned(),
                    );
                    let traceback = if err.is_instance_of::<PyKeyboardInterrupt>(py) {
                        None
                    } else {
                        err.traceback_bound(py).map(|t| {
                            t.format()
                                .unwrap_or_else(|_| String::from("<exception traceback() failed>"))
                        })
                    };

                    PyErrString {
                        r#type,
                        message,
                        traceback: traceback.map(StringError),
                    }
                });

                Self::Python(err)
            }),
            BenchmarkSingleCaseError::Analysis(err) => {
                Self::Analysis(err.map(StringifiedError::from_err))
            },
        }
    }
}
