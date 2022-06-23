use glob::glob;
use intermediate_language::il::linearized_expressions::{LinearExpr, LinearizedExpr};
use intermediate_language::{FastHashMap, FastHashSet};
use rmp_serde;
use serde::{Deserialize, Serialize};
use std::fs;
use std::fs::File;
use std::io::Write;

#[derive(Serialize, Deserialize, Debug)]
pub struct SemanticsMap(pub FastHashMap<LinearizedExpr, Vec<LinearizedExpr>>);

impl SemanticsMap {
    pub fn new() -> SemanticsMap {
        SemanticsMap(FastHashMap::default())
    }

    pub fn new_from_parameter(
        map: FastHashMap<LinearizedExpr, Vec<LinearizedExpr>>,
    ) -> SemanticsMap {
        SemanticsMap(map)
    }

    pub fn insert(&mut self, key: LinearizedExpr, value: Vec<LinearizedExpr>) {
        self.0.insert(key, value);
    }

    pub fn iter(&self) -> impl Iterator<Item = (&LinearizedExpr, &Vec<LinearizedExpr>)> {
        self.0.iter()
    }

    pub fn into_iter(self) -> impl IntoIterator<Item = (LinearizedExpr, Vec<LinearizedExpr>)> {
        self.0.into_iter()
    }

    pub fn to_string(&self) -> String {
        let mut ret = String::new();

        for (representative, equiv_class) in self.iter() {
            ret.push_str(&format!("representative: {}\n", representative.to_string()));
            for expr in equiv_class.iter() {
                ret.push_str(&format!("{}\n", expr.to_string()));
            }
            ret.push_str("\n\n");
        }

        ret
    }

    pub fn dump_to_file(&self) {
        let mut file = File::create("semantics_map.txt").unwrap();
        write!(&mut file, "{}", self.to_string()).unwrap();
    }

    pub fn serialize_to_file(&self, file_path: &String) {
        let content = rmp_serde::to_vec(&self).expect("Could not serialize SemanticsMap");
        let mut file = File::create(&file_path).unwrap();
        file.write_all(&content)
            .expect(&format!("Could not write to {}", file_path));
    }

    pub fn deserialize_from_file(file_path: &String) -> SemanticsMap {
        let content = fs::read(&file_path).expect(&format!("File {} not found!", &file_path));
        rmp_serde::from_read(content.as_slice())
            .expect(&format!("Could not deserialize file {}.", &file_path))
    }

    pub fn unify_from_files(path: &String) -> SemanticsMap {
        let pattern = format!("{}/*", path);
        let paths: Vec<String> = glob(&pattern)
            .unwrap()
            .map(|p| p.unwrap().to_str().unwrap().to_string())
            .collect();
        let mut map: FastHashMap<LinearizedExpr, FastHashSet<LinearizedExpr>> =
            FastHashMap::default();

        for path in paths {
            let tmp_map = SemanticsMap::deserialize_from_file(&path);
            for (representative, equiv_class) in tmp_map.into_iter() {
                map.entry(representative)
                    .or_insert(FastHashSet::default())
                    .extend(equiv_class.into_iter());
            }
        }
        SemanticsMap::from_merged_maps(map)
    }

    pub fn from_merged_maps(
        map: FastHashMap<LinearizedExpr, FastHashSet<LinearizedExpr>>,
    ) -> SemanticsMap {
        SemanticsMap(
            map.into_iter()
                .map(|(k, v)| (k, v.into_iter().collect::<Vec<_>>()))
                .collect(),
        )
    }

    pub fn gen_rules_map(&self) -> FastHashMap<LinearExpr, Vec<LinearizedExpr>> {
        self.0
            .iter()
            .map(|(k, v)| (k.op().clone(), v.clone()))
            .collect()
    }
}
