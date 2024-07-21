mod action;
mod agent_helper;
mod getter;
mod item;
mod obs_repr;
mod player_state;
mod update;

#[cfg(test)]
mod test;

use crate::py_helper::add_submodule;
pub use action::ActionCandidate;
pub use player_state::PlayerState;

use pyo3::prelude::*;

pub(crate) fn register_module(py: Python<'_>, prefix: &str, super_mod: &PyModule) -> PyResult<()> {
    let m = PyModule::new(py, "state")?;
    m.add_class::<ActionCandidate>()?;
    m.add_class::<PlayerState>()?;
    add_submodule(py, prefix, super_mod, m)
}
