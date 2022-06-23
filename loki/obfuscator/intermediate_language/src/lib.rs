extern crate fnv;
extern crate seer_z3;
extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_json;

use fnv::{FnvHashMap, FnvHashSet};
pub type FastHashMap<S, T> = FnvHashMap<S, T>;
pub type FastHashSet<S> = FnvHashSet<S>;

pub mod il;
pub mod symbolic_execution;
pub mod utils;
