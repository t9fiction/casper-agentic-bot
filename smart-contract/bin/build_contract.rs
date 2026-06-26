#![cfg_attr(target_arch = "wasm32", no_std)]
#![cfg_attr(target_arch = "wasm32", no_main)]
#![allow(unused_imports, clippy::single_component_path_imports)]

#[cfg(target_arch = "wasm32")]
use casper_agentic_token_factory;

#[cfg(target_arch = "wasm32")]
fn main() {}

#[cfg(not(target_arch = "wasm32"))]
fn main() {
    // Trigger library compilation on host
    let _ = casper_agentic_token_factory::token_factory::TokenFactory;
}
