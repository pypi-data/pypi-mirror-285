use std::num::NonZeroUsize;

use core_dataset::dataset::DatasetSettings;

const TEN: NonZeroUsize = NonZeroUsize::MIN.saturating_add(9);
const HUNDRED: NonZeroUsize = NonZeroUsize::MIN.saturating_add(99);
const THOUSAND: NonZeroUsize = NonZeroUsize::MIN.saturating_add(999);

#[derive(Debug, Clone, Default, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
#[serde(default)]
pub struct BenchmarkSettings {
    pub measurements: MeasurementSettings,
    pub datasets: DatasetSettings,
}

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
#[serde(default)]
pub struct MeasurementSettings {
    pub num_repeats: NonZeroUsize,
    pub bootstrap: BootstrapSettings,
    pub error: ErrorSettings,
}

impl Default for MeasurementSettings {
    fn default() -> Self {
        Self {
            num_repeats: TEN,
            bootstrap: BootstrapSettings::default(),
            error: ErrorSettings::default(),
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
#[serde(default)]
pub struct BootstrapSettings {
    pub seed: u64,
    pub samples: Option<NonZeroUsize>,
}

impl Default for BootstrapSettings {
    fn default() -> Self {
        Self {
            seed: 42,
            samples: Some(THOUSAND),
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
#[serde(default)]
pub struct ErrorSettings {
    pub bins: NonZeroUsize,
    pub resamples: NonZeroUsize,
}

impl Default for ErrorSettings {
    fn default() -> Self {
        Self {
            bins: HUNDRED,
            resamples: HUNDRED,
        }
    }
}
