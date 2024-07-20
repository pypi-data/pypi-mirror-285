#![allow(clippy::missing_errors_doc)] // FIXME
#![cfg_attr(any(test, not(single_wasm_runtime)), allow(unused_crate_dependencies))]

#[macro_use]
extern crate log;

use core_error::LocationError;

mod codec;
mod engine;
mod error;
mod logging;
mod stdio;
mod template;
mod transform;

pub use codec::WasmCodec;
pub use error::PyLocationErr;
pub use template::WasmCodecTemplate;

#[derive(Debug, thiserror::Error)]
pub enum WasmCodecError {
    #[error(transparent)]
    Wasm(LocationError<codecs_core_host::Error>),
    #[error(transparent)]
    IO(std::io::Error),
    #[error("{0}")]
    Message(String),
}

#[cfg(single_wasm_runtime)]
pub fn init_codecs<'py>(
    py: pyo3::Python<'py>,
    module: pyo3::Borrowed<'_, 'py, pyo3::types::PyModule>,
) -> Result<pyo3::Bound<'py, pyo3::types::PyModule>, LocationError<pyo3::PyErr>> {
    use pyo3::{prelude::*, PyTypeInfo};

    let codecs = pyo3::types::PyModule::new_bound(py, "codecs")?;

    codecs.add_class::<WasmCodecTemplate>()?;
    codecs.add_class::<WasmCodec>()?;

    // FIXME: the __module__ is wrong in fcbench and the benchmark suite
    let __module__ = pyo3::intern!(py, "__module__");
    let module_str = format!("{}.{}", module.name()?, codecs.name()?);

    WasmCodecTemplate::type_object_bound(py).setattr(__module__, &module_str)?;
    WasmCodec::type_object_bound(py).setattr(__module__, module_str)?;

    module.add_submodule(&codecs)?;

    Ok(codecs)
}
