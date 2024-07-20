use std::path::PathBuf;

use pyo3::{intern, prelude::*, types::PyDict};

use core_error::LocationError;

pub fn import_fcpy(
    py: Python,
    codec_paths: impl IntoIterator<Item = PathBuf>,
) -> Result<(), LocationError<PyErr>> {
    let sys_modules: Bound<PyDict> = py
        .import_bound(intern!(py, "sys"))?
        .getattr(intern!(py, "modules"))?
        .extract()?;

    let fcpy = PyModule::new_bound(py, "fcpy")?;

    let codecs = codecs_frontend::init_codecs(py, fcpy.as_borrowed())?;

    println!("- Loading the WASM codecs");

    for path in codec_paths {
        let codec_class =
            codecs_frontend::WasmCodecTemplate::import_codec_class(py, path.clone(), &codecs)?;
        println!(
            "  - Loaded the {} codec from {path:?}",
            codec_class
                .getattr(intern!(py, "__name__"))?
                .extract::<String>()?
        );
    }

    fcpy.add_submodule(&codecs)?;

    // According to
    // https://pyo3.rs/v0.21.0/python-from-rust/calling-existing-code#want-to-embed-python-in-rust-with-additional-modules
    // manually inserting a module into `sys.modules` is the correct way if the
    // module cannot be inserted with [`pyo3::append_to_inittab`] since it is
    // created after Python is initialised
    sys_modules.set_item(format!("{}.{}", fcpy.name()?, codecs.name()?), codecs)?;
    sys_modules.set_item(fcpy.name()?, fcpy)?;

    Ok(())
}
