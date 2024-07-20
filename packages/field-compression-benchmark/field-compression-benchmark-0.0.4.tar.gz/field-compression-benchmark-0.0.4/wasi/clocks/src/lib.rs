#![cfg_attr(not(test), no_main)]

use std::sync::atomic::{AtomicU64, Ordering};

use crate::bindings::{
    exports::wasi::clocks::{
        monotonic_clock::{Duration, Guest as WasiClocksMonotonicClock, Instant},
        wall_clock::{Datetime, Guest as WasiClocksWallClock},
    },
    wasi::{io::poll::Pollable, null::io::ready_pollable},
};

#[allow(clippy::missing_safety_doc, clippy::transmute_int_to_bool)]
mod bindings {
    wit_bindgen::generate!({
        world: "fcbench:wasi/virtual-clocks@0.2.0",
        with: {
            "wasi:clocks/monotonic-clock@0.2.0": generate,
            "wasi:clocks/wall-clock@0.2.0": generate,

            // direct dependencies
            "wasi:io/error@0.2.0": generate,
            "wasi:io/poll@0.2.0": generate,
            "wasi:io/streams@0.2.0": generate,

            "wasi:null/io@0.2.0": generate,
        },
    });
}

pub enum VirtClock {}

#[cfg(target_arch = "wasm32")]
#[allow(unsafe_code)]
mod export {
    use crate::VirtClock;
    crate::bindings::export!(VirtClock with_types_in crate::bindings);
}

static CLOCK_NS: AtomicU64 = AtomicU64::new(0);

impl WasiClocksMonotonicClock for VirtClock {
    fn now() -> Instant {
        CLOCK_NS.load(Ordering::SeqCst)
    }

    fn resolution() -> Duration {
        1 // ns
    }

    fn subscribe_instant(when: Instant) -> Pollable {
        CLOCK_NS.fetch_max(when, Ordering::SeqCst);
        ready_pollable()
    }

    fn subscribe_duration(when: Duration) -> Pollable {
        CLOCK_NS.fetch_add(when, Ordering::SeqCst);
        ready_pollable()
    }
}

impl WasiClocksWallClock for VirtClock {
    fn now() -> Datetime {
        const NANOSECONDS: u32 = 1_000_000_000;

        let now_ns = CLOCK_NS.load(Ordering::SeqCst);

        #[allow(clippy::cast_possible_truncation)]
        let nanoseconds = (now_ns % u64::from(NANOSECONDS)) as u32;
        let seconds = now_ns / u64::from(NANOSECONDS);

        Datetime {
            seconds,
            nanoseconds,
        }
    }

    fn resolution() -> Datetime {
        Datetime {
            seconds: 0,
            nanoseconds: 1,
        }
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn check_wit_deps() -> check_wit_deps::Result<()> {
        check_wit_deps::check_is_locked("wit")
    }
}
