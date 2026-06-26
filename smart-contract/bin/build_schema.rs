#![allow(unused_imports, redundant_imports)]
#![allow(clippy::single_component_path_imports)]

#[cfg(not(target_arch = "wasm32"))]
fn main() {
    use casper_agentic_token_factory;

    #[cfg(not(odra_module = ""))]
    extern "Rust" {
        fn module_schema() -> odra::contract_def::ContractBlueprint;
        fn casper_contract_schema() -> odra::schema::casper_contract_schema::ContractSchema;
    }

    #[cfg(not(odra_module = ""))]
    {
        odra_build::schema(unsafe { module_schema() }, unsafe {
            casper_contract_schema()
        });
    }
}

#[cfg(target_arch = "wasm32")]
fn main() {}
