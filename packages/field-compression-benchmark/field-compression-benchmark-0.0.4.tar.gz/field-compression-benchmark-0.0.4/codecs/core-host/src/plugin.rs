use std::{borrow::BorrowMut, sync::OnceLock};

use semver::Version;
use wasm_component_layer::{
    ComponentList, ExportInstance, Func, Instance, InterfaceIdentifier, PackageIdentifier,
    PackageName, Store, TypedFunc, Value,
};
use wasm_runtime_layer::backend::WasmEngine;

use core_error::LocationError;

use crate::{codec::WasmCodec, store::ErasedWasmStore, Error};

#[allow(clippy::type_complexity, clippy::module_name_repetitions)]
pub struct CodecPlugin {
    // FIXME: make typed instead
    from_config: Func,
    pub(crate) encode: Func,
    pub(crate) decode: Func,
    codec_id: TypedFunc<(), String>,
    signature: TypedFunc<(), String>,
    documentation: TypedFunc<(), String>,
    pub(crate) get_config: Func,
    pub(crate) instruction_counter: TypedFunc<(), u64>,
    instance: Instance,
    pub(crate) ctx: Box<dyn Send + Sync + ErasedWasmStore>,
}

impl CodecPlugin {
    pub fn new<E: WasmEngine>(
        instance: Instance,
        ctx: Store<(), E>,
    ) -> Result<Self, LocationError<Error>>
    where
        Store<(), E>: Send + Sync,
    {
        fn load_func(interface: &ExportInstance, name: &str) -> Result<Func, LocationError<Error>> {
            let Some(func) = interface.func(name) else {
                return Err(LocationError::from2(anyhow::Error::msg(format!(
                    "WASM component interface does not contain a function named `{name}`"
                ))));
            };

            Ok(func)
        }

        fn load_typed_func<P: ComponentList, R: ComponentList>(
            interface: &ExportInstance,
            name: &str,
        ) -> Result<TypedFunc<P, R>, LocationError<Error>> {
            load_func(interface, name)?
                .typed()
                .map_err(LocationError::from2)
        }

        let interfaces = CodecPluginInterfaces::get();

        let Some(codecs_interface) = instance.exports().instance(&interfaces.codecs) else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "WASM component does not contain an interface named `{}`",
                interfaces.codecs
            ))));
        };
        let Some(perf_interface) = instance.exports().instance(&interfaces.perf) else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "WASM component does not contain an interface named `{}`",
                interfaces.perf
            ))));
        };

        Ok(Self {
            from_config: load_func(codecs_interface, "[static]codec.from-config")?,
            encode: load_func(codecs_interface, "[method]codec.encode")?,
            decode: load_func(codecs_interface, "[method]codec.decode")?,
            codec_id: load_typed_func(codecs_interface, "codec-id")?,
            signature: load_typed_func(codecs_interface, "signature")?,
            documentation: load_typed_func(codecs_interface, "documentation")?,
            get_config: load_func(codecs_interface, "[method]codec.get-config")?,
            instruction_counter: load_typed_func(perf_interface, &interfaces.instruction_counter)?,
            instance,
            ctx: Box::new(ctx),
        })
    }

    pub fn codec_id(&mut self) -> Result<String, LocationError<Error>> {
        self.ctx
            .call_typed_str_func(&self.codec_id)
            .map_err(LocationError::from2)
    }

    pub fn signature(&mut self) -> Result<String, LocationError<Error>> {
        self.ctx
            .call_typed_str_func(&self.signature)
            .map_err(LocationError::from2)
    }

    pub fn documentation(&mut self) -> Result<String, LocationError<Error>> {
        self.ctx
            .call_typed_str_func(&self.documentation)
            .map_err(LocationError::from2)
    }

    #[allow(clippy::type_complexity)]
    pub fn from_config<P: BorrowMut<Self>>(
        mut plugin: P,
        config: &str,
    ) -> Result<Result<WasmCodec<P>, String>, LocationError<Error>> {
        let plugin_borrow: &mut Self = plugin.borrow_mut();

        let args = Value::String(config.into());
        let mut result = Value::U8(0);

        plugin_borrow
            .ctx
            .call_func(
                &plugin_borrow.from_config,
                std::slice::from_ref(&args),
                std::slice::from_mut(&mut result),
            )
            .map_err(LocationError::from2)?;

        match result {
            Value::Result(result) => match &*result {
                Ok(Some(Value::Own(resource))) => Ok(Ok(WasmCodec {
                    resource: resource.clone(),
                    plugin,
                    instruction_counter: 0,
                })),
                Err(Some(Value::String(err))) => Ok(Err(String::from(&**err))),
                result => Err(LocationError::from2(anyhow::Error::msg(format!(
                    "unexpected from-config result value {result:?}"
                )))),
            },
            value => Err(LocationError::from2(anyhow::Error::msg(format!(
                "unexpected from-config result value {value:?}"
            )))),
        }
    }

    pub fn drop(mut self) -> Result<(), LocationError<Error>> {
        let result = self
            .ctx
            .drop_instance(&self.instance)
            .map_err(LocationError::from2);

        // We need to forget here instead of using ManuallyDrop since we need
        //  both a mutable borrow to self.plugin and an immutable borrow to
        //  self.resource at the same time
        std::mem::forget(self);

        let errors = result?;
        if errors.is_empty() {
            return Ok(());
        }

        Err(LocationError::from2(anyhow::Error::msg(format!(
            "dropping instance and all of its resources failed: {}",
            errors
                .into_iter()
                .map(|err| format!("{err:#}"))
                .collect::<Vec<_>>()
                .join(" || "),
        ))))
    }
}

impl Drop for CodecPlugin {
    fn drop(&mut self) {
        std::mem::drop(self.ctx.drop_instance(&self.instance));
    }
}

#[non_exhaustive]
pub struct CodecPluginInterfaces {
    pub codecs: InterfaceIdentifier,
    pub perf: InterfaceIdentifier,
    pub instruction_counter: String,
}

impl CodecPluginInterfaces {
    #[must_use]
    pub fn get() -> &'static Self {
        static CODEC_PLUGIN_INTERFACES: OnceLock<CodecPluginInterfaces> = OnceLock::new();

        CODEC_PLUGIN_INTERFACES.get_or_init(|| Self {
            codecs: InterfaceIdentifier::new(
                PackageIdentifier::new(
                    PackageName::new("numcodecs", "abc"),
                    Some(Version::new(0, 1, 0)),
                ),
                "codec",
            ),
            perf: InterfaceIdentifier::new(
                PackageIdentifier::new(
                    PackageName::new("fcbench", "perf"),
                    Some(Version::new(0, 1, 0)),
                ),
                "perf",
            ),
            instruction_counter: String::from("instruction-counter"),
        })
    }
}
