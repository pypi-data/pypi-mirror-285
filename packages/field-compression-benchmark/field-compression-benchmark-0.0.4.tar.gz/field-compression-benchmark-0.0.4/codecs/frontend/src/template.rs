use std::path::PathBuf;

use pyo3::{
    exceptions::PyRuntimeError,
    intern,
    prelude::*,
    types::{IntoPyDict, PyString, PyType},
    PyTypeInfo,
};
use wasm_component_layer::{Component, Linker, Store};
use wasm_runtime_layer::{backend::WasmEngine, Engine};

use core_error::LocationError;

use crate::{
    codec::WasmCodec, engine::ValidatedEngine, error::PyLocationErr, logging, stdio,
    transform::load_and_transform_wasm_module, WasmCodecError,
};

#[pyclass(frozen)]
pub struct WasmCodecTemplate {
    _path: PathBuf,
    component: Component,
    #[allow(clippy::type_complexity)]
    plugin_instantiater: Box<
        dyn Send + Sync + Fn(&Component) -> Result<codecs_core_host::CodecPlugin, WasmCodecError>,
    >,
}

#[pymethods]
impl WasmCodecTemplate {
    #[cfg(single_wasm_runtime)]
    #[staticmethod]
    pub fn load(_py: Python, path: PathBuf) -> Result<Self, PyLocationErr> {
        Self::new_with_default_engine(path).map_err(|err| {
            err.map(|err| PyRuntimeError::new_err(format!("{err:#}")))
                .into()
        })
    }

    pub fn create_codec_class<'py>(
        this: PyRef<'py, Self>,
        py: Python<'py>,
        module: &Bound<'py, PyModule>,
    ) -> Result<Bound<'py, numcodecs_python::CodecClass>, PyLocationErr> {
        let (codec_id, signature, documentation) =
            (|| -> Result<(String, String, String), LocationError<WasmCodecError>> {
                let mut plugin = this.instantiate_plugin()?;
                let codec_id = plugin.codec_id().map_err(WasmCodecError::Wasm)?;
                let signature = plugin.signature().map_err(WasmCodecError::Wasm)?;
                let documentation = plugin.documentation().map_err(WasmCodecError::Wasm)?;
                Ok((codec_id, signature, documentation))
            })()
            .map_err(|err| err.map(|err| PyRuntimeError::new_err(format!("{err:#}"))))?;
        let codec_class_name = convert_case::Casing::to_case(&codec_id, convert_case::Case::Pascal);

        let codec_class_bases = (
            WasmCodec::type_object_bound(py),
            numcodecs_python::Codec::type_object_bound(py),
        );

        let codec_class_namespace = [
            (
                intern!(py, "__doc__"),
                PyString::new_bound(py, &documentation).as_any(),
            ),
            (
                intern!(py, "codec_id"),
                PyString::new_bound(py, &codec_id).as_any(),
            ),
            (
                intern!(py, "__init__"),
                &py.eval_bound(&format!("lambda self, {signature}: None"), None, None)?,
            ),
        ]
        .into_py_dict_bound(py);

        let codec_class: Bound<numcodecs_python::CodecClass> = PyType::type_object_bound(py)
            .call1((&codec_class_name, codec_class_bases, codec_class_namespace))?
            .extract()?;
        codec_class.setattr(intern!(py, "_template"), this.into_py(py))?;
        codec_class.setattr(intern!(py, "__module__"), module.name()?)?;

        module.add(codec_class_name.as_str(), &codec_class)?;

        numcodecs_python::Registry::register_codec(codec_class.as_borrowed(), None)?;

        Ok(codec_class)
    }

    #[cfg(single_wasm_runtime)]
    #[staticmethod]
    pub fn import_codec_class<'py>(
        py: Python<'py>,
        path: PathBuf,
        module: &Bound<'py, PyModule>,
    ) -> Result<Bound<'py, numcodecs_python::CodecClass>, PyLocationErr> {
        let template = Self::load(py, path)?;
        let template = Bound::new(py, template)?;

        Self::create_codec_class(template.borrow(), py, module)
    }
}

impl WasmCodecTemplate {
    pub fn new<E: Send + Sync + WasmEngine>(
        path: PathBuf,
        engine: E,
    ) -> Result<Self, LocationError<WasmCodecError>>
    where
        Store<(), ValidatedEngine<E>>: Send + Sync,
    {
        let wasm_module = load_and_transform_wasm_module(&path)?;

        let engine = Engine::new(ValidatedEngine::new(engine));
        let component = Component::new(&engine, &wasm_module)
            .map_err(LocationError::from2)
            .map_err(WasmCodecError::Wasm)?;

        Ok(Self {
            _path: path,
            component,
            plugin_instantiater: Box::new(move |component: &Component| {
                let mut ctx = Store::new(&engine, ());

                let mut linker = Linker::default();
                stdio::add_to_linker(&mut linker, &mut ctx)
                    .map_err(LocationError::from2)
                    .map_err(WasmCodecError::Wasm)?;
                logging::add_to_linker(&mut linker, &mut ctx)
                    .map_err(LocationError::from2)
                    .map_err(WasmCodecError::Wasm)?;

                let instance = linker
                    .instantiate(&mut ctx, component)
                    .map_err(LocationError::from2)
                    .map_err(WasmCodecError::Wasm)?;

                codecs_core_host::CodecPlugin::new(instance, ctx).map_err(WasmCodecError::Wasm)
            }),
        })
    }

    #[cfg(single_wasm_runtime)]
    pub fn new_with_default_engine(path: PathBuf) -> Result<Self, LocationError<WasmCodecError>> {
        let engine = Self::default_engine(&path)?;

        Self::new(path, engine)
    }

    pub fn instantiate_plugin(&self) -> Result<codecs_core_host::CodecPlugin, WasmCodecError> {
        (self.plugin_instantiater)(&self.component)
    }
}

#[cfg(all(single_wasm_runtime, feature = "wasmtime"))]
impl WasmCodecTemplate {
    // codecs don't need to preallocate the full 4GB wasm32 memory space, but
    //  still give them a reasonable static allocation for better codegen
    const DYNAMIC_MEMORY_GUARD_SIZE: u32 = Self::WASM_PAGE_SIZE /* 64kiB */;
    const DYNAMIC_MEMORY_RESERVED_FOR_GROWTH: u32 = Self::WASM_PAGE_SIZE * 16 * 64 /* 64MiB */;
    const STATIC_MEMORY_GUARD_SIZE: u32 = Self::WASM_PAGE_SIZE * 16 * 64 /* 64MiB */;
    const STATIC_MEMORY_MAXIMUM_SIZE: u32 = Self::WASM_PAGE_SIZE * 16 * 64 /* 64MiB */;
    const WASM_PAGE_SIZE: u32 = 0x10000 /* 64kiB */;

    fn default_engine(
        path: &std::path::Path,
    ) -> Result<wasmtime_runtime_layer::Engine, LocationError<WasmCodecError>> {
        let mut config = wasmtime::Config::new();
        config
            .cranelift_nan_canonicalization(true)
            .cranelift_opt_level(wasmtime::OptLevel::Speed)
            .static_memory_maximum_size(u64::from(Self::STATIC_MEMORY_MAXIMUM_SIZE))
            .static_memory_guard_size(u64::from(Self::STATIC_MEMORY_GUARD_SIZE))
            .dynamic_memory_guard_size(u64::from(Self::DYNAMIC_MEMORY_GUARD_SIZE))
            .dynamic_memory_reserved_for_growth(u64::from(Self::DYNAMIC_MEMORY_RESERVED_FOR_GROWTH))
            // TODO: allow configuration to be taken from somewhere else
            .cache_config_load(path.with_file_name("wasmtime.toml"))
            .map_err(LocationError::from2)
            .map_err(WasmCodecError::Wasm)?
            // WASM feature restrictions, follows the feature validation in
            //  ValidatedModule::new
            .wasm_bulk_memory(true)
            .wasm_component_model(false)
            .wasm_function_references(false)
            .wasm_gc(false)
            .wasm_memory64(false)
            .wasm_multi_memory(true)
            .wasm_multi_value(true)
            .wasm_reference_types(false)
            .wasm_relaxed_simd(false)
            .wasm_simd(false)
            .wasm_tail_call(false)
            // wasmtime is compiled without the `threads` feature
            // .wasm_threads(false)
            ;
        let engine = wasmtime::Engine::new(&config)
            .map_err(LocationError::from2)
            .map_err(WasmCodecError::Wasm)?;
        Ok(wasmtime_runtime_layer::Engine::new(engine))
    }
}

#[cfg(all(single_wasm_runtime, feature = "pyodide"))]
impl WasmCodecTemplate {
    #[allow(clippy::unnecessary_wraps)]
    fn default_engine(
        _path: &std::path::Path,
    ) -> Result<pyodide_webassembly_runtime_layer::Engine, LocationError<WasmCodecError>> {
        Ok(pyodide_webassembly_runtime_layer::Engine::default())
    }
}
