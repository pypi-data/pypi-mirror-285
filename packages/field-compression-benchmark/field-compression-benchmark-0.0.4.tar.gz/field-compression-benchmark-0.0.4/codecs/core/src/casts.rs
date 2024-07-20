#[cfg(any(target_pointer_width = "32", target_pointer_width = "64"))]
#[must_use]
pub const fn u32_as_usize(x: u32) -> usize {
    x as usize
}

#[cfg(any(target_pointer_width = "16", target_pointer_width = "32"))]
#[must_use]
#[allow(clippy::cast_possible_truncation)]
pub const fn usize_as_u32(x: usize) -> u32 {
    x as u32
}

#[must_use]
pub fn ptr_addr(ptr: *const u8) -> usize {
    ptr as usize
}
