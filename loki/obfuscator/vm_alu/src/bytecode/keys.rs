use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ALUKeys {
    keys: Vec<u64>,
    used_keys: HashSet<u64>,
    additional_keys: HashMap<usize, u64>,
}

impl ALUKeys {
    pub fn new() -> ALUKeys {
        ALUKeys {
            keys: vec![],
            used_keys: HashSet::new(),
            additional_keys: HashMap::new(),
        }
    }

    pub fn get(&self, index: usize) -> u64 {
        *self
            .keys
            .get(index)
            .expect(&format!("Could not access key index {} {:#?}", index, self))
    }

    pub fn get_additional_key(&self, index: usize) -> u64 {
        *self
            .additional_keys
            .get(&index)
            .expect("Could not find key.")
    }

    pub fn push(&mut self, value: u64) {
        self.keys.push(value);
        self.used_keys.insert(value);
    }

    pub fn insert_additional_key(&mut self, index: usize, value: u64) {
        self.additional_keys.insert(index, value);
        self.used_keys.insert(value);
    }

    pub fn iter(&self) -> impl Iterator<Item = &u64> {
        self.keys.iter()
    }

    pub fn iter_additional_keys(&self) -> impl Iterator<Item = &u64> {
        self.additional_keys.values()
    }

    pub fn contains(&self, k: u64) -> bool {
        self.used_keys.contains(&k)
    }

    pub fn contains_additional_key(&self, index: usize) -> bool {
        self.additional_keys.contains_key(&index)
    }

    pub fn len(&self) -> usize {
        self.keys.len()
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MetaALUKeys(HashMap<usize, ALUKeys>);

impl MetaALUKeys {
    pub fn new() -> MetaALUKeys {
        MetaALUKeys(HashMap::new())
    }

    pub fn insert(&mut self, index: usize, keys: ALUKeys) {
        self.0.insert(index, keys);
    }

    pub fn get(&self, index: &usize) -> Option<&ALUKeys> {
        self.0.get(index)
    }
}
