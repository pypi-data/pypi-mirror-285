#![allow(clippy::missing_errors_doc)]

mod codec;
mod plugin;
mod store;

pub use codec::WasmCodec;
pub use plugin::{CodecPlugin, CodecPluginInterfaces};

#[derive(Debug, thiserror::Error)]
#[error(transparent)]
pub struct Error(#[from] anyhow::Error);
