use numpy::{
    PyArray, PyArray1, PyArrayDescrMethods, PyArrayDyn, PyArrayMethods, PyUntypedArray,
    PyUntypedArrayMethods,
};
use pyo3::{
    exceptions::{PyRuntimeError, PyTypeError, PyValueError},
    intern,
    prelude::*,
    types::{PyDict, PyType},
};

use core_error::LocationError;

use crate::{WasmCodecError, WasmCodecTemplate};

#[pyclass(subclass)]
// not frozen as the codec is mutated when WASM is called
pub struct WasmCodec {
    cls_module: String,
    cls_name: String,
    codec: codecs_core_host::WasmCodec,
}

#[pymethods]
impl WasmCodec {
    #[new]
    #[classmethod]
    #[pyo3(signature = (**kwargs))]
    fn new<'py>(
        cls: &Bound<'py, PyType>,
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<Self, PyErr> {
        fn new_inner(
            template: &WasmCodecTemplate,
            kwargs: &str,
            cls_module: &str,
            cls_name: &str,
        ) -> Result<WasmCodec, LocationError<WasmCodecError>> {
            let plugin = template.instantiate_plugin()?;

            let codec = codecs_core_host::CodecPlugin::from_config(plugin, kwargs)
                .map_err(WasmCodecError::Wasm)?
                .map_err(WasmCodecError::Message)?;

            Ok(WasmCodec {
                codec,
                cls_module: String::from(cls_module),
                cls_name: String::from(cls_name),
            })
        }

        let cls: &Bound<numcodecs_python::CodecClass> = cls.downcast()?;
        let cls_module: String = cls.getattr(intern!(py, "__module__"))?.extract()?;
        let cls_name: String = cls.getattr(intern!(py, "__name__"))?.extract()?;

        let template: Bound<WasmCodecTemplate> = cls
            .getattr(intern!(py, "_template"))
            .map_err(|_| {
                PyValueError::new_err(format!(
                    "{cls_module}.{cls_name} is not linked to a WASM codec template, use \
                     WasmCodecTemplate::create_codec_class to create a new WASM codec class with \
                     a template"
                ))
            })?
            .extract()?;
        let template: PyRef<WasmCodecTemplate> = template.try_borrow()?;

        let json_dumps = py
            .import_bound(intern!(py, "json"))?
            .getattr(intern!(py, "dumps"))?;
        let kwargs: Option<String> = kwargs
            .map(|kwargs| json_dumps.call1((kwargs,)).and_then(|c| c.extract()))
            .transpose()?;
        let kwargs = kwargs.unwrap_or_else(|| String::from("{}"));

        new_inner(&template, &kwargs, &cls_module, &cls_name).map_err(|err| {
            PyValueError::new_err(format!(
                "{cls_module}.{cls_name}::from_config(config={kwargs}) failed with:\n{err:#}"
            ))
        })
    }

    pub fn encode<'py>(
        &mut self,
        py: Python<'py>,
        buf: &Bound<'py, PyAny>,
    ) -> Result<Bound<'py, PyAny>, PyErr> {
        self.process(
            py,
            buf.as_borrowed(),
            codecs_core_host::WasmCodec::encode,
            &format!("{}.{}::encode", self.cls_module, self.cls_name),
        )
        .map(Bound::into_any)
    }

    pub fn decode<'py>(
        &mut self,
        py: Python<'py>,
        buf: &Bound<'py, PyAny>,
        out: Option<Bound<'py, PyAny>>,
    ) -> Result<Bound<'py, PyAny>, PyErr> {
        let class_method = &format!("{}.{}::decode", self.cls_module, self.cls_name);
        if let Some(out) = out {
            self.process_into(
                py,
                buf.as_borrowed(),
                out.as_borrowed(),
                codecs_core_host::WasmCodec::decode_into,
                class_method,
            )?;
            Ok(out)
        } else {
            self.process(
                py,
                buf.as_borrowed(),
                codecs_core_host::WasmCodec::decode,
                class_method,
            )
            .map(Bound::into_any)
        }
    }

    pub fn get_config<'py>(&mut self, py: Python<'py>) -> Result<Bound<'py, PyDict>, PyErr> {
        let json_loads = py
            .import_bound(intern!(py, "json"))?
            .getattr(intern!(py, "loads"))?;

        let config = self
            .codec
            .get_config()
            .map_err(|err| PyValueError::new_err(format!("{err}")))?
            .map_err(PyValueError::new_err)?;

        json_loads.call1((config,))?.extract()
    }

    #[classmethod]
    pub fn from_config<'py>(
        cls: &Bound<'py, PyType>,
        config: &Bound<'py, PyDict>,
    ) -> Result<Bound<'py, numcodecs_python::Codec>, PyErr> {
        let cls: Bound<numcodecs_python::CodecClass> = cls.extract()?;

        // Ensures that cls(**config) is called and an instance of cls is returned
        cls.call((), Some(config))?.extract()
    }

    pub fn __repr__(mut this: PyRefMut<Self>, py: Python) -> Result<String, PyErr> {
        let config = this.get_config(py)?;
        let py_this: Py<PyAny> = this.into_py(py);

        let mut repr = py_this.bind(py).get_type().name()?.into_owned();
        repr.push('(');

        let mut first = true;

        for parameter in config.call_method0(intern!(py, "items"))?.iter()? {
            let (name, value): (String, Bound<PyAny>) = parameter?.extract()?;

            if name == "id" {
                // Exclude the id config parameter from the repr
                continue;
            }

            let value_repr: String = value.repr()?.extract()?;

            if !first {
                repr.push_str(", ");
            }
            first = false;

            repr.push_str(&name);
            repr.push('=');
            repr.push_str(&value_repr);
        }

        repr.push(')');

        Ok(repr)
    }

    #[getter]
    #[must_use]
    pub const fn instruction_counter(&self) -> u64 {
        self.codec.instruction_counter()
    }
}

impl WasmCodec {
    fn process<'py>(
        &mut self,
        py: Python<'py>,
        buf: Borrowed<'_, 'py, PyAny>,
        process: impl for<'a> Fn(
            &'a mut codecs_core_host::WasmCodec,
            codecs_core::BufferSlice,
            &[usize],
        ) -> Result<
            Result<codecs_core::ShapedBuffer<codecs_core::VecBuffer>, String>,
            LocationError<codecs_core_host::Error>,
        >,
        class_method: &str,
    ) -> Result<Bound<'py, PyUntypedArray>, PyErr> {
        Self::with_pyarray_as_buffer_slice(py, buf, class_method, |data, shape| {
            let processed = process(&mut self.codec, data, shape)
                .map_err(|err| {
                    PyRuntimeError::new_err(format!("{class_method} failed with: {err}"))
                })?
                .map_err(WasmCodecError::Message)
                .map_err(|err| {
                    PyRuntimeError::new_err(format!("{class_method} failed with: {err}"))
                })?;

            Self::shaped_buffer_into_pyarray(py, processed, class_method)
        })
    }

    fn process_into<'py>(
        &mut self,
        py: Python<'py>,
        buf: Borrowed<'_, 'py, PyAny>,
        out: Borrowed<'_, 'py, PyAny>,
        process: impl for<'a> Fn(
            &'a mut codecs_core_host::WasmCodec,
            codecs_core::BufferSlice,
            &[usize],
            codecs_core::BufferSliceMut,
            &[usize],
        )
            -> Result<Result<(), String>, LocationError<codecs_core_host::Error>>,
        class_method: &str,
    ) -> Result<(), PyErr> {
        Self::with_pyarray_as_buffer_slice(py, buf, class_method, |data, shape| {
            Self::with_pyarray_as_buffer_slice_mut(py, out, class_method, |data_out, shape_out| {
                process(&mut self.codec, data, shape, data_out, shape_out)
                    .map_err(|err| {
                        PyRuntimeError::new_err(format!("{class_method} failed with: {err}"))
                    })?
                    .map_err(WasmCodecError::Message)
                    .map_err(|err| {
                        PyRuntimeError::new_err(format!("{class_method} failed with: {err}"))
                    })
            })
        })
    }

    fn with_pyarray_as_buffer_slice<'py, O>(
        py: Python<'py>,
        buf: Borrowed<'_, 'py, PyAny>,
        class_method: &str,
        with: impl for<'a> FnOnce(codecs_core::BufferSlice<'a>, &[usize]) -> Result<O, PyErr>,
    ) -> Result<O, PyErr> {
        fn with_pyarray_as_buffer_slice_inner<T: numpy::Element + codecs_core::BufferTyBound, O>(
            data: Borrowed<PyArrayDyn<T>>,
            with: impl for<'a> FnOnce(codecs_core::BufferSlice<'a>, &[usize]) -> Result<O, PyErr>,
        ) -> Result<O, PyErr> {
            let readonly_data = data.try_readonly()?;
            let data_slice = readonly_data.as_slice()?;
            with(codecs_core::BufferSlice::from(data_slice), data.shape())
        }

        let ensure_ndarray_like = py
            .import_bound(intern!(py, "numcodecs"))?
            .getattr(intern!(py, "compat"))?
            .getattr(intern!(py, "ensure_ndarray_like"))?;

        let data: Bound<PyUntypedArray> = ensure_ndarray_like.call1((buf,))?.extract()?;
        let dtype = data.dtype();

        if dtype.is_equiv_to(&numpy::dtype_bound::<u8>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<u8>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<u16>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<u16>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<u32>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<u32>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<u64>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<u64>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i8>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<i8>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i16>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<i16>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i32>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<i32>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i64>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<i64>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<f32>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<f32>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<f64>(py)) {
            with_pyarray_as_buffer_slice_inner(data.downcast::<PyArrayDyn<f64>>()?.into(), with)
        } else {
            Err(PyTypeError::new_err(format!(
                "{class_method} received buffer of unsupported dtype `{dtype}`",
            )))
        }
    }

    fn with_pyarray_as_buffer_slice_mut<'py, O>(
        py: Python<'py>,
        buf: Borrowed<'_, 'py, PyAny>,
        class_method: &str,
        with: impl for<'a> FnOnce(codecs_core::BufferSliceMut<'a>, &[usize]) -> Result<O, PyErr>,
    ) -> Result<O, PyErr> {
        fn with_pyarray_as_buffer_slice_mut_inner<
            T: numpy::Element + codecs_core::BufferTyBound,
            O,
        >(
            data: Borrowed<PyArrayDyn<T>>,
            with: impl for<'a> FnOnce(codecs_core::BufferSliceMut<'a>, &[usize]) -> Result<O, PyErr>,
        ) -> Result<O, PyErr> {
            let mut readwrite_data = data.try_readwrite()?;
            let data_slice = readwrite_data.as_slice_mut()?;
            with(codecs_core::BufferSliceMut::from(data_slice), data.shape())
        }

        let ensure_ndarray_like = py
            .import_bound(intern!(py, "numcodecs"))?
            .getattr(intern!(py, "compat"))?
            .getattr(intern!(py, "ensure_ndarray_like"))?;

        let data: Bound<PyUntypedArray> = ensure_ndarray_like.call1((buf,))?.extract()?;
        let dtype = data.dtype();

        if dtype.is_equiv_to(&numpy::dtype_bound::<u8>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<u8>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<u16>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<u16>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<u32>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<u32>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<u64>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<u64>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i8>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<i8>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i16>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<i16>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i32>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<i32>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<i64>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<i64>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<f32>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<f32>>()?.into(), with)
        } else if dtype.is_equiv_to(&numpy::dtype_bound::<f64>(py)) {
            with_pyarray_as_buffer_slice_mut_inner(data.downcast::<PyArrayDyn<f64>>()?.into(), with)
        } else {
            Err(PyTypeError::new_err(format!(
                "{class_method} received buffer of unsupported dtype `{dtype}`",
            )))
        }
    }

    fn shaped_buffer_into_pyarray<'py>(
        py: Python<'py>,
        buffer: codecs_core::ShapedBuffer,
        class_method: &str,
    ) -> Result<Bound<'py, PyUntypedArray>, PyErr> {
        trait PyArrayExt<'py> {
            fn into_untyped(self) -> Bound<'py, PyUntypedArray>;
        }

        impl<'py, T, D> PyArrayExt<'py> for Bound<'py, PyArray<T, D>> {
            fn into_untyped(self) -> Bound<'py, PyUntypedArray> {
                // Safety: follows from a.as_untyped
                #[allow(unsafe_code)]
                unsafe {
                    self.into_any().downcast_into_unchecked()
                }
            }
        }

        match buffer.buffer {
            codecs_core::BufferVec::U8(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::U16(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::U32(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::U64(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::I8(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::I16(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::I32(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::I64(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::F32(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            codecs_core::BufferVec::F64(v) => Ok(PyArray1::from_vec_bound(py, v)
                .reshape(buffer.shape)?
                .into_untyped()),
            buf => Err(PyTypeError::new_err(format!(
                "{class_method} returned unsupported dtype `{}`",
                buf.as_slice().ty()
            ))),
        }
    }
}
