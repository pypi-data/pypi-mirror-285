use pyo3::prelude::*;

use core_error::LocationError;

pub struct PyLocationErr(LocationError<PyErr>);

impl From<PyErr> for PyLocationErr {
    #[track_caller]
    fn from(err: PyErr) -> Self {
        Self(LocationError::new(err))
    }
}

impl From<LocationError<PyErr>> for PyLocationErr {
    fn from(err: LocationError<PyErr>) -> Self {
        Self(err)
    }
}

impl From<PyLocationErr> for PyErr {
    fn from(err: PyLocationErr) -> Self {
        err.0.into_error()
    }
}

impl From<PyLocationErr> for LocationError<PyErr> {
    fn from(err: PyLocationErr) -> Self {
        err.0
    }
}
