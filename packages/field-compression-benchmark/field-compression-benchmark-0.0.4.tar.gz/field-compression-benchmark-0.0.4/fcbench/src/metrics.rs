use numpy::PyArray1;
use pyo3::prelude::*;

pub fn create_module(py: Python) -> Result<Bound<PyModule>, PyErr> {
    let module = PyModule::new_bound(py, "metrics")?;

    module.add_class::<BitInformation>()?;

    Ok(module)
}

#[pyclass(module = "fcbench.metrics", frozen)]
pub struct BitInformation {
    _inner: (),
}

#[pymethods]
impl BitInformation {
    #[staticmethod]
    /// [SIGNATURE]: # "(a: Union[numpy.array, xarray.DataArray], /, *, set_zero_insignificant_confidence: Optional[float] = 0.99) -> numpy.array"
    #[pyo3(signature = (a, /, *, set_zero_insignificant_confidence=Some(0.99)))]
    pub fn bit_information<'py>(
        py: Python<'py>,
        a: &Bound<'py, PyAny>,
        set_zero_insignificant_confidence: Option<f64>,
    ) -> Result<Bound<'py, PyArray1<f64>>, PyErr> {
        #[allow(clippy::option_if_let_else)]
        let bit_information = if let Ok(a) = a.downcast() {
            core_goodness::bit_information::DataArrayBitInformation::bit_information_array(
                py,
                a.into(),
                set_zero_insignificant_confidence,
            )
        } else {
            core_goodness::bit_information::DataArrayBitInformation::bit_information(
                py,
                a.into(),
                set_zero_insignificant_confidence,
            )
        }
        .map_err(core_error::LocationError::into_error)?;

        Ok(bit_information)
    }

    #[staticmethod]
    /// [SIGNATURE]: # "(a: Union[numpy.array, xarray.DataArray], /, *, set_zero_insignificant_confidence: Optional[float] = 0.99) -> float"
    #[pyo3(signature = (a, /, *, set_zero_insignificant_confidence=Some(0.99)))]
    pub fn information_content(
        py: Python,
        a: &Bound<PyAny>,
        set_zero_insignificant_confidence: Option<f64>,
    ) -> Result<f64, PyErr> {
        #[allow(clippy::option_if_let_else)]
        let information_content = if let Ok(a) = a.downcast() {
            core_goodness::bit_information::DataArrayBitInformation::information_content_array(
                py,
                a.into(),
                set_zero_insignificant_confidence,
            )
        } else {
            core_goodness::bit_information::DataArrayBitInformation::information_content(
                py,
                a.into(),
                set_zero_insignificant_confidence,
            )
        }
        .map_err(core_error::LocationError::into_error)?;

        Ok(information_content)
    }

    #[staticmethod]
    /// [SIGNATURE]: # "(a: Union[numpy.array, xarray.DataArray], /, information_ratio: float, *, set_zero_insignificant_confidence: Optional[float] = 0.99) -> int"
    #[pyo3(signature = (a, /, information_ratio, *, set_zero_insignificant_confidence=Some(0.99)))]
    pub fn required_bits(
        py: Python,
        a: &Bound<PyAny>,
        information_ratio: f64,
        set_zero_insignificant_confidence: Option<f64>,
    ) -> Result<usize, PyErr> {
        #[allow(clippy::option_if_let_else)]
        let required_bits = if let Ok(a) = a.downcast() {
            core_goodness::bit_information::DataArrayBitInformation::required_bits_array(
                py,
                a.into(),
                information_ratio,
                set_zero_insignificant_confidence,
            )
        } else {
            core_goodness::bit_information::DataArrayBitInformation::required_bits(
                py,
                a.into(),
                information_ratio,
                set_zero_insignificant_confidence,
            )
        }
        .map_err(core_error::LocationError::into_error)?;

        Ok(required_bits)
    }
}
