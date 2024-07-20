use std::{
    borrow::Cow,
    collections::{hash_map::Entry, HashMap},
    marker::PhantomData,
    ops::Deref,
};

use convert_case::{Case, Casing};
use nonempty::NonEmpty;
use pyo3::{
    exceptions::PyValueError,
    intern,
    prelude::*,
    types::{
        IntoPyDict, PyBool, PyBytes, PyDict, PyFloat, PyInt, PyList, PyMapping, PyString, PyTuple,
        PyType,
    },
    PyTypeInfo,
};
use pythonize::{PythonizeDictType, PythonizeTypes};

mod de;
mod ser;

pub struct Dataclass<T: serde::Serialize> {
    data: T,
}

impl<T: serde::Serialize> Dataclass<T> {
    #[must_use]
    pub const fn new(data: T) -> Self {
        Self { data }
    }

    #[must_use]
    pub fn into_data(self) -> T {
        self.data
    }

    pub fn output(&self, py: Python) -> Result<DataclassOut<T>, PyErr> {
        DataclassOut::new(&self.data, py)
    }

    pub fn output_frozen(&self, py: Python) -> Result<DataclassOutFrozen<T>, PyErr> {
        DataclassOutFrozen::new(&self.data, py)
    }
}

impl<T: serde::Serialize> Deref for Dataclass<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.data
    }
}

impl<'py, T: serde::Serialize + serde::Deserialize<'py>> FromPyObject<'py> for Dataclass<T> {
    fn extract_bound(obj: &Bound<'py, PyAny>) -> Result<Self, PyErr> {
        let mut depythonizer = pythonize::Depythonizer::from_object_bound(obj.clone());

        match serde_path_to_error::deserialize(&mut depythonizer) {
            Ok(data) => Ok(Self { data }),
            Err(err) => {
                let err_with_path =
                    PyValueError::new_err(format!("failed to extract at {}", err.path()));
                err_with_path.set_cause(obj.py(), Some(PyErr::from(err.into_inner())));
                Err(err_with_path)
            },
        }
    }
}

// TODO: unite with Dataclass once there is a fallible IntoPy
pub struct DataclassOut<T: serde::Serialize> {
    data: Py<PyAny>,
    inner: PhantomData<fn(T)>,
}

impl<T: serde::Serialize> DataclassOut<T> {
    pub fn new(data: &T, py: Python) -> Result<Self, PyErr> {
        match pythonize::pythonize_custom::<PythonizeNamespace, T>(py, data) {
            Ok(data) => Ok(Self {
                data,
                inner: PhantomData::<fn(T)>,
            }),
            Err(err) => Err(PyErr::from(err)),
        }
    }
}

impl<T: serde::Serialize> IntoPy<Py<PyAny>> for DataclassOut<T> {
    fn into_py(self, _py: Python) -> Py<PyAny> {
        self.data
    }
}

pub struct DataclassOutFrozen<T: serde::Serialize> {
    data: Py<PyAny>,
    inner: PhantomData<T>,
}

impl<T: serde::Serialize> DataclassOutFrozen<T> {
    pub fn new(data: &T, py: Python) -> Result<Self, PyErr> {
        match pythonize::pythonize_custom::<PythonizeFrozenDataclass, T>(py, data) {
            Ok(data) => Ok(Self {
                data,
                inner: PhantomData::<T>,
            }),
            Err(err) => Err(PyErr::from(err)),
        }
    }
}

pub struct DataclassRegistry {
    tracer: serde_reflection::Tracer,
    samples: serde_reflection::Samples,
    names: HashMap<&'static str, &'static str>,
}

impl DataclassRegistry {
    #[must_use]
    pub fn new() -> Self {
        Self {
            tracer: serde_reflection::Tracer::new(
                serde_reflection::TracerConfig::default()
                    // prefer binary inputs over human-readable string inputs,
                    //  which often require more validation
                    .is_human_readable(false)
                    // record all types of containers
                    .record_samples_for_newtype_structs(true)
                    .record_samples_for_structs(true)
                    .record_samples_for_tuple_structs(true)
                    // allow tracing NonZero* integer types
                    .default_u8_value(1)
                    .default_u16_value(1)
                    .default_u32_value(1)
                    .default_u64_value(1)
                    .default_u128_value(1)
                    .default_i8_value(1)
                    .default_i16_value(1)
                    .default_i32_value(1)
                    .default_i64_value(1)
                    .default_i128_value(1),
            ),
            samples: serde_reflection::Samples::new(),
            names: HashMap::new(),
        }
    }

    pub fn insert<'a, T: serde::Serialize + serde::Deserialize<'a>>(&'a mut self) {
        #[allow(clippy::expect_used)]
        let (_format, _guesses) = de::DeserializeSeed::<T>::with(&mut self.names, |seed| {
            self.tracer.trace_type_with_seed(&self.samples, seed)
        })
        .expect("DataclassRegistry::insert failed");
    }

    pub fn insert_with_sample<'a, T: serde::Serialize + serde::Deserialize<'a>>(
        &'a mut self,
        sample: &T,
    ) {
        #[allow(clippy::expect_used)]
        ser::Serialize::with(sample, &mut self.names, |sample| {
            self.tracer.trace_value(&mut self.samples, sample)
        })
        .expect("DataclassRegistry::insert_with_sample failed on sample");
    }

    #[allow(clippy::too_many_lines)]
    pub fn export<'py>(
        self,
        py: Python<'py>,
        module: Borrowed<'_, 'py, PyModule>,
    ) -> Result<(), PyErr> {
        #[allow(clippy::expect_used)]
        let mut registry = self
            .tracer
            .registry()
            .expect("DataclassRegistry::export failed with incomplete types");

        let mut unique_to_name = self
            .names
            .into_iter()
            .map(|(unique, name)| (unique, Cow::Borrowed(name)))
            .collect::<HashMap<_, _>>();
        let mut name_to_unique = HashMap::with_capacity(unique_to_name.len());
        for (&unique, name) in &unique_to_name {
            match name_to_unique.entry(name.clone()) {
                Entry::Vacant(entry) => {
                    entry.insert(NonEmpty::new(unique));
                },
                Entry::Occupied(mut entry) => entry.get_mut().push(unique),
            }
        }

        let mut extra_containers = Vec::new();
        for (name, format) in &mut registry {
            if let serde_reflection::ContainerFormat::Enum(variants) = format {
                let enum_name = Self::normalise_type_name(name, &unique_to_name, &name_to_unique);
                for format in variants.values_mut() {
                    let variant_type_name = format!(
                        "{}_{}",
                        enum_name.name,
                        format.name.to_case(Case::UpperCamel)
                    );
                    match &format.value {
                        #[allow(clippy::unreachable)]
                        serde_reflection::VariantFormat::Variable(_) => {
                            unreachable!("{name}::{} is an unresolved variant type", format.name)
                        },
                        serde_reflection::VariantFormat::Unit => (),
                        serde_reflection::VariantFormat::NewType(newtype) => {
                            if let serde_reflection::Format::TypeName(inner_name) = &**newtype {
                                if Self::normalise_type_name(
                                    inner_name,
                                    &unique_to_name,
                                    &name_to_unique,
                                )
                                .name
                                    == format.name
                                {
                                    continue;
                                }
                            }

                            extra_containers.push((
                                variant_type_name.clone(),
                                serde_reflection::ContainerFormat::Struct(vec![
                                    serde_reflection::Named {
                                        name: format.name.clone(),
                                        value: (**newtype).clone(),
                                    },
                                ]),
                            ));
                            format.value = serde_reflection::VariantFormat::NewType(Box::new(
                                serde_reflection::Format::TypeName(variant_type_name),
                            ));
                        },
                        #[allow(clippy::unreachable)]
                        serde_reflection::VariantFormat::Tuple(_) => {
                            unreachable!("{name}::{} is an unsupported tuple variant", format.name)
                        },
                        serde_reflection::VariantFormat::Struct(fields) => {
                            extra_containers.push((
                                variant_type_name.clone(),
                                serde_reflection::ContainerFormat::Struct(fields.clone()),
                            ));
                            format.value = serde_reflection::VariantFormat::NewType(Box::new(
                                serde_reflection::Format::TypeName(variant_type_name),
                            ));
                        },
                    }
                }
            }
        }
        registry.extend(extra_containers);

        let mut newly_unique_names = Vec::new();
        for (name, clashes) in &name_to_unique {
            let type_name =
                Self::normalise_type_name(clashes.head, &unique_to_name, &name_to_unique);
            if !type_name.generics.is_empty() || clashes.tail.is_empty() {
                continue;
            }

            for &unique in clashes {
                #[allow(clippy::panic)]
                let Some(ty) = registry.remove(unique) else {
                    panic!("registry is missing non-generic non-unique type {unique}");
                };

                #[allow(clippy::panic)]
                let serde_reflection::ContainerFormat::Enum(variants) = &ty
                else {
                    panic!("only non-generic non-unique enums are supported");
                };

                assert!(
                    variants.len() == 1,
                    "only single-variant non-generic non-unique enums are supported"
                );
                #[allow(clippy::panic)]
                let Some((_, variant)) = variants.first_key_value() else {
                    panic!("only single-variant non-generic non-unique enums are supported");
                };

                let variant_type_name =
                    format!("{}_{}", name, variant.name.to_case(Case::UpperCamel));
                newly_unique_names.push((unique, variant_type_name));
                registry.insert(String::from(unique), ty);
            }
        }
        for (unique, name) in newly_unique_names {
            unique_to_name.insert(unique, Cow::Owned(name.clone()));
            name_to_unique.insert(Cow::Owned(name), NonEmpty::new(unique));
        }

        for (name, format) in &registry {
            if let serde_reflection::ContainerFormat::Struct(_)
            | serde_reflection::ContainerFormat::Enum(_) = format
            {
                let generics =
                    Self::normalise_type_name(name, &unique_to_name, &name_to_unique).generics;
                for i in 0..generics.len() {
                    let param = if i == 0 {
                        String::from("T")
                    } else {
                        format!("T{}", i + 1)
                    };
                    if !module.hasattr(param.as_str())? {
                        module.add(
                            param.as_str(),
                            py.import_bound(intern!(py, "typing"))?
                                .getattr(intern!(py, "TypeVar"))?
                                .call1((param.as_str(),))?,
                        )?;
                    }
                }
            }
        }

        for (name, format) in &registry {
            if let serde_reflection::ContainerFormat::Struct(_)
            | serde_reflection::ContainerFormat::Enum(_) = format
            {
                let generic_name =
                    Self::normalise_type_name(name, &unique_to_name, &name_to_unique).name;
                if !module.hasattr(&*generic_name)? {
                    let ty = Self::container_type_hint(
                        py,
                        name,
                        format,
                        &registry,
                        &unique_to_name,
                        &name_to_unique,
                        &[],
                    )?;
                    module.add(&*generic_name, ty)?;
                }
            }
        }

        Ok(())
    }

    fn normalise_type_name<'a>(
        unique: &'a str,
        unique_to_name: &HashMap<&'static str, Cow<'static, str>>,
        name_to_unique: &HashMap<Cow<'static, str>, NonEmpty<&'static str>>,
    ) -> TypeName<'a> {
        let Some(name) = unique_to_name.get(unique).cloned() else {
            return TypeName {
                name: Cow::Borrowed(unique),
                generics: Vec::new(),
            };
        };

        #[allow(clippy::expect_used)]
        let clashes = name_to_unique
            .get(&name)
            .expect("container type name should not be dangling");

        if clashes.tail.is_empty() && clashes.head == unique {
            return TypeName {
                name,
                generics: Vec::new(),
            };
        }

        let generics = unique
            .split(&['<', '>', ','])
            .skip(1)
            .filter_map(|generic| {
                if generic.trim().is_empty() {
                    return None;
                }

                #[allow(clippy::expect_used)]
                let generic = unique_to_name
                    .get(generic.trim())
                    .cloned()
                    .expect("generic should resolve to a name");
                Some(generic)
            })
            .collect::<Vec<_>>();

        TypeName { name, generics }
    }

    #[allow(clippy::too_many_lines)]
    fn container_type_hint<'py>(
        py: Python<'py>,
        name: &str,
        format: &serde_reflection::ContainerFormat,
        registry: &serde_reflection::Registry,
        unique_to_name: &HashMap<&'static str, Cow<'static, str>>,
        name_to_unique: &HashMap<Cow<'static, str>, NonEmpty<&'static str>>,
        generics: &[Cow<'static, str>],
    ) -> Result<Bound<'py, PyAny>, PyErr> {
        match format {
            serde_reflection::ContainerFormat::UnitStruct => Ok(py.None().into_bound(py)),
            serde_reflection::ContainerFormat::NewTypeStruct(inner) => Self::format_type_hint(
                py,
                name,
                Field::Tuple(0),
                inner,
                registry,
                unique_to_name,
                name_to_unique,
                generics,
            ),
            serde_reflection::ContainerFormat::TupleStruct(fields) => {
                Ok(PyTuple::type_object_bound(py).get_item(PyTuple::new_bound(
                    py,
                    fields
                        .iter()
                        .enumerate()
                        .map(|(i, field)| {
                            Self::format_type_hint(
                                py,
                                name,
                                Field::Tuple(i),
                                field,
                                registry,
                                unique_to_name,
                                name_to_unique,
                                generics,
                            )
                        })
                        .collect::<Result<Vec<_>, _>>()?,
                ))?)
            },
            serde_reflection::ContainerFormat::Struct(fields) => {
                let type_name = Self::normalise_type_name(name, unique_to_name, name_to_unique);
                let generics = type_name
                    .generics
                    .iter()
                    .enumerate()
                    .map(|(i, _generic)| -> Result<_, PyErr> {
                        py.import_bound(intern!(py, "typing"))?
                            .getattr(intern!(py, "TypeVar"))?
                            .call1((if i == 0 {
                                String::from("T")
                            } else {
                                format!("T{}", i + 1)
                            },))
                    })
                    .collect::<Result<Vec<_>, _>>()?;
                let mut bases = vec![py
                    .import_bound(intern!(py, "collections"))?
                    .getattr(intern!(py, "abc"))?
                    .getattr(intern!(py, "Mapping"))?];
                if !generics.is_empty() {
                    bases.push(
                        py.import_bound(intern!(py, "typing"))?
                            .getattr(intern!(py, "Generic"))?
                            .get_item(PyTuple::new_bound(py, generics))?,
                    );
                }
                Ok(py
                    .import_bound(intern!(py, "dataclasses"))?
                    .getattr(intern!(py, "make_dataclass"))?
                    .call(
                        (
                            type_name.name,
                            PyTuple::new_bound(
                                py,
                                fields
                                    .iter()
                                    .map(|field| -> Result<_, PyErr> {
                                        Ok((
                                            field.name.as_str(),
                                            Self::format_type_hint(
                                                py,
                                                name,
                                                Field::Struct(&field.name),
                                                &field.value,
                                                registry,
                                                unique_to_name,
                                                name_to_unique,
                                                &type_name.generics,
                                            )?,
                                        ))
                                    })
                                    .collect::<Result<Vec<_>, _>>()?,
                            ),
                        ),
                        Some(
                            &[
                                (intern!(py, "bases"), PyTuple::new_bound(py, bases).as_any()),
                                (intern!(py, "kw_only"), PyBool::new_bound(py, true).as_any()),
                            ]
                            .into_py_dict_bound(py),
                        ),
                    )?)
            },
            serde_reflection::ContainerFormat::Enum(variants) => {
                let type_name = Self::normalise_type_name(name, unique_to_name, name_to_unique);
                let generics = type_name
                    .generics
                    .iter()
                    .enumerate()
                    .map(|(i, _generic)| -> Result<_, PyErr> {
                        py.import_bound(intern!(py, "typing"))?
                            .getattr(intern!(py, "TypeVar"))?
                            .call1((if i == 0 {
                                String::from("T")
                            } else {
                                format!("T{}", i + 1)
                            },))
                    })
                    .collect::<Result<Vec<_>, _>>()?;
                let mut bases = Vec::with_capacity(1);
                if !generics.is_empty() {
                    bases.push(
                        py.import_bound(intern!(py, "typing"))?
                            .getattr(intern!(py, "Generic"))?
                            .get_item(PyTuple::new_bound(py, generics))?,
                    );
                }
                let bases = PyTuple::new_bound(py, bases);
                let namespace = variants
                    .values()
                    .map(|variant| -> Result<_, PyErr> {
                        Ok((
                            variant.name.to_case(Case::UpperCamel),
                            Self::variant_type_hint(
                                py,
                                name,
                                variant,
                                registry,
                                unique_to_name,
                                name_to_unique,
                                &type_name.generics,
                            )?,
                        ))
                    })
                    .collect::<Result<Vec<_>, _>>()?
                    .into_py_dict_bound(py);

                PyType::type_object_bound(py).call1((type_name.name, bases, namespace))
            },
        }
    }

    fn variant_type_hint<'py>(
        py: Python<'py>,
        name: &str,
        variant: &serde_reflection::Named<serde_reflection::VariantFormat>,
        registry: &serde_reflection::Registry,
        unique_to_name: &HashMap<&'static str, Cow<'static, str>>,
        name_to_unique: &HashMap<Cow<'static, str>, NonEmpty<&'static str>>,
        generics: &[Cow<'static, str>],
    ) -> Result<Bound<'py, PyAny>, PyErr> {
        let typing = py.import_bound(intern!(py, "typing"))?;

        match &variant.value {
            #[allow(clippy::unreachable)]
            serde_reflection::VariantFormat::Variable(_) => {
                unreachable!("{name}::{} is an unresolved variant type", variant.name)
            },
            serde_reflection::VariantFormat::Unit => Ok(typing
                .getattr(intern!(py, "Literal"))?
                .get_item(&variant.name)?),
            // FIXME: test matching format in the unit tests
            serde_reflection::VariantFormat::NewType(newtype) => {
                if let serde_reflection::Format::TypeName(newtype) = &**newtype {
                    Self::type_name_hint(
                        py,
                        newtype,
                        registry,
                        unique_to_name,
                        name_to_unique,
                        generics,
                    )
                } else {
                    #[allow(clippy::unreachable)]
                    {
                        unreachable!(
                            "{name}::{} is an unsupported newtype variant - should be handled \
                             earlier",
                            variant.name,
                        )
                    }
                }
            },
            #[allow(clippy::unreachable)]
            serde_reflection::VariantFormat::Tuple(_) => {
                unreachable!("{name}::{} is an unsupported tuple variant", variant.name)
            },
            #[allow(clippy::unreachable)]
            serde_reflection::VariantFormat::Struct(_) => {
                unreachable!(
                    "{name}::{} is an unsupported struct variant - should be handled earlier",
                    variant.name
                )
            },
        }
    }

    #[allow(clippy::too_many_lines, clippy::too_many_arguments)] // FIXME
    fn format_type_hint<'py>(
        py: Python<'py>,
        name: &str,
        field: Field,
        format: &serde_reflection::Format,
        registry: &serde_reflection::Registry,
        unique_to_name: &HashMap<&'static str, Cow<'static, str>>,
        name_to_unique: &HashMap<Cow<'static, str>, NonEmpty<&'static str>>,
        generics: &[Cow<'static, str>],
    ) -> Result<Bound<'py, PyAny>, PyErr> {
        let typing = py.import_bound(intern!(py, "typing"))?;
        let collections_abc = py
            .import_bound(intern!(py, "collections"))?
            .getattr(intern!(py, "abc"))?;

        match format {
            #[allow(clippy::unreachable)]
            serde_reflection::Format::Variable(_) => {
                unreachable!("{name}.{field} is an unresolved field type")
            },
            serde_reflection::Format::TypeName(ty) => {
                Self::type_name_hint(py, ty, registry, unique_to_name, name_to_unique, generics)
            },
            serde_reflection::Format::Unit => Ok(py.None().into_bound(py)),
            serde_reflection::Format::Bool => Ok(PyBool::type_object_bound(py).into_any()),
            serde_reflection::Format::I8
            | serde_reflection::Format::I16
            | serde_reflection::Format::I32
            | serde_reflection::Format::I64
            | serde_reflection::Format::I128
            | serde_reflection::Format::U8
            | serde_reflection::Format::U16
            | serde_reflection::Format::U32
            | serde_reflection::Format::U64
            | serde_reflection::Format::U128 => Ok(PyInt::type_object_bound(py).into_any()),
            serde_reflection::Format::F32 | serde_reflection::Format::F64 => {
                Ok(PyFloat::type_object_bound(py).into_any())
            },
            serde_reflection::Format::Char | serde_reflection::Format::Str => {
                Ok(PyString::type_object_bound(py).into_any())
            },
            serde_reflection::Format::Bytes => Ok(PyBytes::type_object_bound(py).into_any()),
            serde_reflection::Format::Option(inner) => Ok(typing
                .getattr(intern!(py, "Optional"))?
                .get_item(Self::format_type_hint(
                    py,
                    name,
                    field,
                    inner,
                    registry,
                    unique_to_name,
                    name_to_unique,
                    generics,
                )?)?),
            serde_reflection::Format::Seq(elem) => Ok(collections_abc
                .getattr(intern!(py, "Sequence"))?
                .get_item(Self::format_type_hint(
                    py,
                    name,
                    field,
                    elem,
                    registry,
                    unique_to_name,
                    name_to_unique,
                    generics,
                )?)?),
            serde_reflection::Format::Map { key, value } => {
                Ok(collections_abc.getattr(intern!(py, "Mapping"))?.get_item((
                    Self::format_type_hint(
                        py,
                        name,
                        field,
                        key,
                        registry,
                        unique_to_name,
                        name_to_unique,
                        generics,
                    )?,
                    Self::format_type_hint(
                        py,
                        name,
                        field,
                        value,
                        registry,
                        unique_to_name,
                        name_to_unique,
                        generics,
                    )?,
                ))?)
            },
            serde_reflection::Format::Tuple(elems) => Ok(PyTuple::type_object_bound(py).get_item(
                elems
                    .iter()
                    .map(|elem| {
                        Self::format_type_hint(
                            py,
                            name,
                            field,
                            elem,
                            registry,
                            unique_to_name,
                            name_to_unique,
                            generics,
                        )
                    })
                    .collect::<Result<Vec<_>, _>>()?,
            )?),
            serde_reflection::Format::TupleArray { content, size } => {
                let elem = Self::format_type_hint(
                    py,
                    name,
                    field,
                    content,
                    registry,
                    unique_to_name,
                    name_to_unique,
                    generics,
                )?;
                Ok(PyTuple::type_object_bound(py)
                    .get_item(PyTuple::new_bound(py, (0..*size).map(|_| &elem)))?)
            },
        }
    }

    fn type_name_hint<'py>(
        py: Python<'py>,
        name: &str,
        registry: &serde_reflection::Registry,
        unique_to_name: &HashMap<&'static str, Cow<'static, str>>,
        name_to_unique: &HashMap<Cow<'static, str>, NonEmpty<&'static str>>,
        generics: &[Cow<'static, str>],
    ) -> Result<Bound<'py, PyAny>, PyErr> {
        match registry.get(name) {
            Some(
                serde_reflection::ContainerFormat::Struct(_)
                | serde_reflection::ContainerFormat::Enum(_),
            ) => {
                let type_name = Self::normalise_type_name(name, unique_to_name, name_to_unique);
                let mut generic_type_name = String::from(type_name.name);
                if let Some(j) = generics.iter().position(|g| g == &generic_type_name) {
                    assert!(
                        type_name.generics.is_empty(),
                        "unsupported deeply generic struct or enum type"
                    );
                    generic_type_name.clear();
                    generic_type_name.push('T');
                    if j > 0 {
                        generic_type_name.push_str(&format!("{}", j + 1));
                    }
                } else if !type_name.generics.is_empty() {
                    generic_type_name.push('[');
                    for (i, generic) in type_name.generics.into_iter().enumerate() {
                        if i > 0 {
                            generic_type_name.push_str(", ");
                        }
                        if let Some(j) = generics.iter().position(|g| g == &generic) {
                            generic_type_name.push('T');
                            if j > 0 {
                                generic_type_name.push_str(&format!("{}", j + 1));
                            }
                        } else {
                            generic_type_name.push_str(&generic);
                        }
                    }
                    generic_type_name.push(']');
                }
                py.import_bound(intern!(py, "typing"))?
                    .getattr(intern!(py, "ForwardRef"))?
                    .call1((generic_type_name,))
            },
            Some(format) => Self::container_type_hint(
                py,
                name,
                format,
                registry,
                unique_to_name,
                name_to_unique,
                generics,
            ),
            #[allow(clippy::panic)]
            None => panic!("{name} is an unresolved type"),
        }
    }
}

struct TypeName<'a> {
    name: Cow<'a, str>,
    generics: Vec<Cow<'static, str>>,
}

#[derive(Clone, Copy)]
enum Field<'a> {
    Tuple(usize),
    Struct(&'a str),
}

impl<'a> std::fmt::Display for Field<'a> {
    fn fmt(&self, fmt: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Field::Tuple(idx) => fmt.write_fmt(format_args!("{idx}")),
            Field::Struct(name) => fmt.write_str(name),
        }
    }
}

impl<T: serde::Serialize> IntoPy<Py<PyAny>> for DataclassOutFrozen<T> {
    fn into_py(self, _py: Python) -> Py<PyAny> {
        self.data
    }
}

pub enum PythonizeNamespace {}

impl PythonizeTypes for PythonizeNamespace {
    type List = PyList;
    type Map = Self;
}

impl PythonizeDictType for PythonizeNamespace {
    fn create_mapping(py: Python) -> Result<Bound<PyMapping>, PyErr> {
        Ok(PyDict::new_bound(py).into_mapping())
    }

    fn create_mapping_with_items<
        K: ToPyObject,
        V: ToPyObject,
        U: ExactSizeIterator<Item = (K, V)>,
    >(
        py: Python,
        items: impl IntoIterator<Item = (K, V), IntoIter = U>,
    ) -> PyResult<Bound<PyMapping>> {
        Ok(items.into_py_dict_bound(py).into_mapping())
    }

    fn create_mapping_with_items_name<
        'py,
        K: ToPyObject,
        V: ToPyObject,
        U: ExactSizeIterator<Item = (K, V)>,
    >(
        py: Python<'py>,
        name: &str,
        items: impl IntoIterator<Item = (K, V), IntoIter = U>,
    ) -> Result<Bound<'py, PyMapping>, PyErr> {
        let items = items.into_py_dict_bound(py);

        let bases = (
            py.import_bound(intern!(py, "types"))?
                .getattr(intern!(py, "SimpleNamespace"))?,
            py.import_bound(intern!(py, "collections"))?
                .getattr(intern!(py, "abc"))?
                .getattr(intern!(py, "Mapping"))?,
        );

        let namespace: Bound<PyDict> = py
            .eval_bound(
                "dict(
            __len__ = lambda self: self.__dict__.__len__(),
            __getitem__ = lambda self, key: self.__dict__.__getitem__(key),
            __iter__ = lambda self: self.__dict__.__iter__(),
        )",
                None,
                None,
            )?
            .extract()?;

        let class = PyType::type_object_bound(py).call1((name, bases, namespace))?;

        class
            .call((), Some(&items.into_py_dict_bound(py)))?
            .extract()
    }
}

pub enum PythonizeFrozenDataclass {}

impl PythonizeTypes for PythonizeFrozenDataclass {
    type List = PyTuple;
    type Map = Self;
}

impl PythonizeDictType for PythonizeFrozenDataclass {
    fn create_mapping(py: Python) -> Result<Bound<PyMapping>, PyErr> {
        py.import_bound(intern!(py, "types"))?
            .getattr(intern!(py, "MappingProxyType"))?
            .call1((PyDict::new_bound(py),))?
            .extract()
    }

    fn create_mapping_with_items<
        K: ToPyObject,
        V: ToPyObject,
        U: ExactSizeIterator<Item = (K, V)>,
    >(
        py: Python,
        items: impl IntoIterator<Item = (K, V), IntoIter = U>,
    ) -> PyResult<Bound<PyMapping>> {
        py.import_bound(intern!(py, "types"))?
            .getattr(intern!(py, "MappingProxyType"))?
            .call1((items.into_py_dict_bound(py),))?
            .extract()
    }

    fn create_mapping_with_items_name<
        'py,
        K: ToPyObject,
        V: ToPyObject,
        U: ExactSizeIterator<Item = (K, V)>,
    >(
        py: Python<'py>,
        name: &str,
        items: impl IntoIterator<Item = (K, V), IntoIter = U>,
    ) -> Result<Bound<'py, PyMapping>, PyErr> {
        let items = items.into_py_dict_bound(py);

        let bases = (
            py.import_bound(intern!(py, "collections"))?
                .getattr(intern!(py, "namedtuple"))?
                .call1((name, items.keys()))?,
            py.import_bound(intern!(py, "collections"))?
                .getattr(intern!(py, "abc"))?
                .getattr(intern!(py, "Mapping"))?,
        );

        let namespace: Bound<PyDict> = py
            .eval_bound(
                "dict(
            __slots__ = (),
            __contains__ = lambda self, key: self._fields.__contains__(key),
            __getitem__ = lambda self, key: self._asdict().__getitem__(key),
            __iter__ = lambda self: self._fields.__iter__(),
            _asdict = lambda self: { f: v for f, v in zip(self._fields, \
                 type(self).__bases__[0].__iter__(self)) },
        )",
                None,
                None,
            )?
            .extract()?;

        let class = PyType::type_object_bound(py).call1((name, bases, namespace))?;

        class
            .call((), Some(&items.into_py_dict_bound(py)))?
            .extract()
    }
}
