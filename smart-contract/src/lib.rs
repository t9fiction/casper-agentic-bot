#![cfg_attr(not(test), no_std)]
#![cfg_attr(not(test), no_main)]

#[cfg(not(test))]
extern crate alloc;

pub mod token_factory;
pub mod nft_marketplace;
pub mod collection_factory;
