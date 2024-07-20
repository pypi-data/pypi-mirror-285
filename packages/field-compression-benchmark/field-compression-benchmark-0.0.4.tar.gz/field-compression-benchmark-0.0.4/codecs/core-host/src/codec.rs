use std::borrow::BorrowMut;

use wasm_component_layer::{
    List, ListType, Record, RecordType, ResourceOwn, Value, ValueType, Variant, VariantCase,
    VariantType,
};

use codecs_core::{casts::u32_as_usize, BufferSlice, BufferSliceMut, ShapedBuffer, VecBuffer};
use core_error::LocationError;

use crate::{plugin::CodecPlugin, Error};

#[allow(clippy::module_name_repetitions)]
pub struct WasmCodec<P: BorrowMut<CodecPlugin> = CodecPlugin> {
    pub(crate) resource: ResourceOwn,
    pub(crate) plugin: P,
    pub(crate) instruction_counter: u64,
}

impl<P: BorrowMut<CodecPlugin>> WasmCodec<P> {
    #[must_use]
    pub const fn instruction_counter(&self) -> u64 {
        self.instruction_counter
    }

    #[allow(clippy::type_complexity)]
    pub fn encode(
        &mut self,
        buf: BufferSlice,
        shape: &[usize],
    ) -> Result<Result<ShapedBuffer<VecBuffer>, String>, LocationError<Error>> {
        self.process(
            buf,
            shape,
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.encode, arguments, results),
            |buffer, shape| {
                Ok(ShapedBuffer {
                    buffer: buffer.to_vec(),
                    shape,
                })
            },
        )
    }

    #[allow(clippy::type_complexity)]
    pub fn encode_into(
        &mut self,
        buf: BufferSlice,
        shape: &[usize],
        mut buf_out: BufferSliceMut,
        shape_out: &[usize],
    ) -> Result<Result<(), String>, LocationError<Error>> {
        self.process(
            buf,
            shape,
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.encode, arguments, results),
            |buffer, shape| {
                if shape != shape_out {
                    return Err(LocationError::from2(anyhow::Error::msg(format!(
                        "encode result has shape {shape:?} but expected {shape_out:?}"
                    ))));
                }
                buf_out
                    .copy_from(buffer)
                    .map_err(anyhow::Error::new)
                    .map_err(LocationError::from2)?;
                Ok(())
            },
        )
    }

    #[allow(clippy::type_complexity)]
    pub fn decode(
        &mut self,
        buf: BufferSlice,
        shape: &[usize],
    ) -> Result<Result<ShapedBuffer<VecBuffer>, String>, LocationError<Error>> {
        self.process(
            buf,
            shape,
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.decode, arguments, results),
            |buffer, shape| {
                Ok(ShapedBuffer {
                    buffer: buffer.to_vec(),
                    shape,
                })
            },
        )
    }

    #[allow(clippy::type_complexity)]
    pub fn decode_into(
        &mut self,
        buf: BufferSlice,
        shape: &[usize],
        mut buf_out: BufferSliceMut,
        shape_out: &[usize],
    ) -> Result<Result<(), String>, LocationError<Error>> {
        self.process(
            buf,
            shape,
            |plugin, arguments, results| plugin.ctx.call_func(&plugin.decode, arguments, results),
            |buffer, shape| {
                if shape != shape_out {
                    return Err(LocationError::from2(anyhow::Error::msg(format!(
                        "decode result has shape {shape:?} but expected {shape_out:?}"
                    ))));
                }
                buf_out
                    .copy_from(buffer)
                    .map_err(anyhow::Error::new)
                    .map_err(LocationError::from2)?;
                Ok(())
            },
        )
    }

    pub fn get_config(&mut self) -> Result<Result<String, String>, LocationError<Error>> {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        let resource = plugin
            .ctx
            .borrow_resource(&self.resource)
            .map_err(LocationError::from2)?;

        let arg = Value::Borrow(resource);
        let mut result = Value::U8(0);

        plugin
            .ctx
            .call_func(
                &plugin.get_config,
                std::slice::from_ref(&arg),
                std::slice::from_mut(&mut result),
            )
            .map_err(LocationError::from2)?;

        match result {
            Value::Result(result) => match &*result {
                Ok(Some(Value::String(config))) => Ok(Ok(String::from(&**config))),
                Err(Some(Value::String(err))) => Ok(Err(String::from(&**err))),
                result => Err(LocationError::from2(anyhow::Error::msg(format!(
                    "unexpected get-config result value {result:?}"
                )))),
            },
            value => Err(LocationError::from2(anyhow::Error::msg(format!(
                "unexpected get-config result value {value:?}"
            )))),
        }
    }

    pub fn drop(mut self) -> Result<(), LocationError<Error>> {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        let result = plugin
            .ctx
            .drop_resource(&self.resource)
            .map_err(LocationError::from2);

        // We need to forget here instead of using ManuallyDrop since we need
        //  both a mutable borrow to self.plugin and an immutable borrow to
        //  self.resource at the same time
        std::mem::forget(self);

        result
    }
}

impl<P: BorrowMut<CodecPlugin>> WasmCodec<P> {
    #[allow(clippy::type_complexity)]
    fn process<O>(
        &mut self,
        buf: BufferSlice,
        shape: &[usize],
        process: impl FnOnce(&mut CodecPlugin, &[Value], &mut [Value]) -> anyhow::Result<()>,
        with_result: impl for<'a> FnOnce(BufferSlice<'a>, Vec<usize>) -> Result<O, LocationError<Error>>,
    ) -> Result<Result<O, String>, LocationError<Error>> {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        let resource = plugin
            .ctx
            .borrow_resource(&self.resource)
            .map_err(LocationError::from2)?;

        let buffer_ty = Self::buffer_ty()?;
        let buffer = Self::buffer_slice_into_wasm_variant(buf, buffer_ty.clone())?;
        let shape = Self::shape_into_wasm_list(shape)?;

        let instruction_counter_pre = plugin
            .ctx
            .call_typed_u64_func(&plugin.instruction_counter)
            .map_err(LocationError::from2)?;

        let mut result = Value::U8(0);

        process(
            plugin,
            &[
                Value::Borrow(resource),
                Value::Variant(buffer),
                Value::List(shape),
            ],
            std::slice::from_mut(&mut result),
        )
        .map_err(LocationError::from2)?;

        let instruction_counter_post = plugin
            .ctx
            .call_typed_u64_func(&plugin.instruction_counter)
            .map_err(LocationError::from2)?;
        self.instruction_counter += instruction_counter_post - instruction_counter_pre;

        match result {
            Value::Result(result) => match &*result {
                Ok(Some(Value::Record(record)))
                    if record.ty() == Self::shaped_buffer_ty(buffer_ty)? =>
                {
                    Self::with_buffer_slice_from_wasm_record(record, |buffer| {
                        Ok(Ok(with_result(
                            buffer,
                            Self::shape_from_wasm_record(record)?,
                        )?))
                    })
                },
                Err(Some(Value::String(err))) => Ok(Err(String::from(&**err))),
                result => Err(LocationError::from2(anyhow::Error::msg(format!(
                    "unexpected process result value {result:?}"
                )))),
            },
            value => Err(LocationError::from2(anyhow::Error::msg(format!(
                "unexpected process result value {value:?}"
            )))),
        }
    }

    fn buffer_ty() -> Result<VariantType, LocationError<Error>> {
        let buffer_ty = VariantType::new(
            None,
            [
                VariantCase::new("u8", Some(ValueType::List(ListType::new(ValueType::U8)))),
                VariantCase::new("u16", Some(ValueType::List(ListType::new(ValueType::U16)))),
                VariantCase::new("u32", Some(ValueType::List(ListType::new(ValueType::U32)))),
                VariantCase::new("u64", Some(ValueType::List(ListType::new(ValueType::U64)))),
                VariantCase::new("i8", Some(ValueType::List(ListType::new(ValueType::S8)))),
                VariantCase::new("i16", Some(ValueType::List(ListType::new(ValueType::S16)))),
                VariantCase::new("i32", Some(ValueType::List(ListType::new(ValueType::S32)))),
                VariantCase::new("i64", Some(ValueType::List(ListType::new(ValueType::S64)))),
                VariantCase::new("f32", Some(ValueType::List(ListType::new(ValueType::F32)))),
                VariantCase::new("f64", Some(ValueType::List(ListType::new(ValueType::F64)))),
            ],
        )
        .map_err(LocationError::from2)?;

        Ok(buffer_ty)
    }

    fn shaped_buffer_ty(buffer_ty: VariantType) -> Result<RecordType, LocationError<Error>> {
        let shaped_buffer_ty = RecordType::new(
            None,
            [
                ("buffer", ValueType::Variant(buffer_ty)),
                ("shape", ValueType::List(ListType::new(ValueType::U32))),
            ],
        )
        .map_err(LocationError::from2)?;

        Ok(shaped_buffer_ty)
    }

    fn buffer_slice_into_wasm_variant(
        buf: BufferSlice,
        buffer_ty: VariantType,
    ) -> Result<Variant, LocationError<Error>> {
        let buffer = match buf {
            BufferSlice::U8(buf) => Variant::new(buffer_ty, 0, Some(Value::List(List::from(buf)))),
            BufferSlice::U16(buf) => Variant::new(buffer_ty, 1, Some(Value::List(List::from(buf)))),
            BufferSlice::U32(buf) => Variant::new(buffer_ty, 2, Some(Value::List(List::from(buf)))),
            BufferSlice::U64(buf) => Variant::new(buffer_ty, 3, Some(Value::List(List::from(buf)))),
            BufferSlice::I8(buf) => Variant::new(buffer_ty, 4, Some(Value::List(List::from(buf)))),
            BufferSlice::I16(buf) => Variant::new(buffer_ty, 5, Some(Value::List(List::from(buf)))),
            BufferSlice::I32(buf) => Variant::new(buffer_ty, 6, Some(Value::List(List::from(buf)))),
            BufferSlice::I64(buf) => Variant::new(buffer_ty, 7, Some(Value::List(List::from(buf)))),
            BufferSlice::F32(buf) => Variant::new(buffer_ty, 8, Some(Value::List(List::from(buf)))),
            BufferSlice::F64(buf) => Variant::new(buffer_ty, 9, Some(Value::List(List::from(buf)))),
            buf => Err(anyhow::Error::msg(format!(
                "unknown buffer type {}",
                buf.ty()
            ))),
        }
        .map_err(LocationError::from2)?;

        Ok(buffer)
    }

    fn shape_into_wasm_list(shape: &[usize]) -> Result<List, LocationError<Error>> {
        let shape = shape
            .iter()
            .map(|s| u32::try_from(*s).map_err(anyhow::Error::new))
            .collect::<Result<Vec<_>, _>>()
            .map_err(LocationError::from2)?;
        Ok(List::from(shape.as_slice()))
    }

    fn shape_from_wasm_record(record: &Record) -> Result<Vec<usize>, LocationError<Error>> {
        let Some(Value::List(shape)) = record.field("shape") else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "process result record {record:?} is missing shape field"
            ))));
        };
        let shape = shape
            .typed::<u32>()
            .map_err(LocationError::from2)?
            .iter()
            .copied()
            .map(u32_as_usize)
            .collect::<Vec<_>>();
        Ok(shape)
    }

    fn with_buffer_slice_from_wasm_record<O>(
        record: &Record,
        with: impl for<'a> FnOnce(BufferSlice<'a>) -> Result<O, LocationError<Error>>,
    ) -> Result<O, LocationError<Error>> {
        let Some(Value::Variant(variant)) = record.field("buffer") else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "process result record {record:?} is missing buffer field"
            ))));
        };
        let Some(Value::List(list)) = variant.value() else {
            return Err(LocationError::from2(anyhow::Error::msg(format!(
                "process result buffer has an invalid variant type {:?}",
                variant.value().map(|v| v.ty())
            ))));
        };

        let buffer = match variant.discriminant() {
            0 => BufferSlice::from(list.typed::<u8>().map_err(LocationError::from2)?),
            1 => BufferSlice::from(list.typed::<u16>().map_err(LocationError::from2)?),
            2 => BufferSlice::from(list.typed::<u32>().map_err(LocationError::from2)?),
            3 => BufferSlice::from(list.typed::<u64>().map_err(LocationError::from2)?),
            4 => BufferSlice::from(list.typed::<i8>().map_err(LocationError::from2)?),
            5 => BufferSlice::from(list.typed::<i16>().map_err(LocationError::from2)?),
            6 => BufferSlice::from(list.typed::<i32>().map_err(LocationError::from2)?),
            7 => BufferSlice::from(list.typed::<i64>().map_err(LocationError::from2)?),
            8 => BufferSlice::from(list.typed::<f32>().map_err(LocationError::from2)?),
            9 => BufferSlice::from(list.typed::<f64>().map_err(LocationError::from2)?),
            discriminant => {
                return Err(LocationError::from2(anyhow::Error::msg(format!(
                    "process result buffer has an invalid variant [{discriminant}]:{:?}",
                    variant.value().map(|v| v.ty())
                ))))
            },
        };

        with(buffer)
    }
}

impl<P: BorrowMut<CodecPlugin>> Drop for WasmCodec<P> {
    fn drop(&mut self) {
        let plugin: &mut CodecPlugin = self.plugin.borrow_mut();

        std::mem::drop(plugin.ctx.drop_resource(&self.resource));
    }
}
