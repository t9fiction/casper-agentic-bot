use odra::prelude::*;
use odra::casper_types::U256;

fn format_metadata_uri(base: &str, token_id: u64) -> String {
    let mut s = String::with_capacity(base.len() + 20);
    s.push_str(base);
    let mut n = token_id;
    let mut buf = [0u8; 20];
    let mut i = buf.len();
    loop {
        i -= 1;
        buf[i] = (n % 10) as u8 + b'0';
        n /= 10;
        if n == 0 {
            break;
        }
    }
    s.push_str(core::str::from_utf8(&buf[i..]).unwrap_or("0"));
    s.push_str(".json");
    s
}

#[odra::odra_type]
pub struct CollectionInfo {
    pub name: String,
    pub symbol: String,
    pub creator: Address,
    pub base_uri: String,
    pub mint_price: U256,
    pub total_supply: u64,
}

#[odra::odra_type]
pub struct NftEntry {
    pub token_id: u64,
    pub collection_id: u32,
    pub owner: Address,
    pub creator: Address,
    pub metadata_uri: String,
    pub listed: bool,
    pub price: U256,
}

#[odra::module]
pub struct CollectionFactory {
    collections: Mapping<u32, CollectionInfo>,
    nfts: Mapping<u64, NftEntry>,
    collection_ids: Mapping<u32, Vec<u64>>,
    next_collection_id: Var<u32>,
    next_token_id: Var<u64>,
}

#[odra::module]
impl CollectionFactory {
    #[odra(init)]
    pub fn init(&self) {}

    pub fn create_collection(&mut self, name: String, symbol: String, base_uri: String, mint_price: U256) -> u32 {
        let caller = self.env().caller();
        let col_id = self.next_collection_id.get_or_default();

        let mut uri = base_uri;
        if !uri.ends_with("/") {
            uri.push_str("/");
        }

        self.collections.set(
            &col_id,
            CollectionInfo {
                name,
                symbol,
                creator: caller,
                base_uri: uri,
                mint_price,
                total_supply: 0,
            },
        );

        self.collection_ids.set(&col_id, Vec::new());
        self.next_collection_id.set(col_id + 1);
        col_id
    }

    pub fn mint_nft(&mut self, collection_id: u32, recipient: Address) -> u64 {
        let caller = self.env().caller();
        let col = self.collections.get(&collection_id).unwrap_or_revert_with(&self.env(), Error::CollectionNotFound);

        let token_id = self.next_token_id.get_or_default();
        let uri = format_metadata_uri(&col.base_uri, token_id);

        self.nfts.set(
            &token_id,
            NftEntry {
                token_id,
                collection_id,
                owner: recipient,
                creator: caller,
                metadata_uri: uri,
                listed: false,
                price: U256::zero(),
            },
        );

        let mut ids = self.collection_ids.get(&collection_id).unwrap_or_default();
        ids.push(token_id);
        self.collection_ids.set(&collection_id, ids);

        let mut col_mut = col;
        col_mut.total_supply += 1;
        self.collections.set(&collection_id, col_mut);
        self.next_token_id.set(token_id + 1);
        token_id
    }

    pub fn transfer_nft(&mut self, token_id: u64, recipient: Address) {
        let caller = self.env().caller();
        let mut entry = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if entry.owner != caller {
            self.env().revert(Error::NotOwner);
        }

        entry.owner = recipient;
        entry.listed = false;
        entry.price = U256::zero();
        self.nfts.set(&token_id, entry);
    }

    pub fn list_nft(&mut self, token_id: u64, price: U256) {
        let caller = self.env().caller();
        let mut entry = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if entry.owner != caller {
            self.env().revert(Error::NotOwner);
        }

        entry.listed = true;
        entry.price = price;
        self.nfts.set(&token_id, entry);
    }

    pub fn unlist_nft(&mut self, token_id: u64) {
        let caller = self.env().caller();
        let mut entry = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if entry.owner != caller {
            self.env().revert(Error::NotOwner);
        }

        entry.listed = false;
        entry.price = U256::zero();
        self.nfts.set(&token_id, entry);
    }

    pub fn buy_nft(&mut self, token_id: u64, buyer: Address) {
        let mut entry = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if !entry.listed {
            self.env().revert(Error::NotListed);
        }

        entry.owner = buyer;
        entry.listed = false;
        entry.price = U256::zero();
        self.nfts.set(&token_id, entry);
    }

    pub fn collection_info(&self, collection_id: u32) -> Option<CollectionInfo> {
        self.collections.get(&collection_id)
    }

    pub fn nft_info(&self, token_id: u64) -> Option<NftEntry> {
        self.nfts.get(&token_id)
    }

    pub fn owner_of(&self, token_id: u64) -> Option<Address> {
        self.nfts.get(&token_id).map(|e| e.owner)
    }

    pub fn total_collections(&self) -> u32 {
        self.next_collection_id.get_or_default()
    }

    pub fn total_nfts_in_collection(&self, collection_id: u32) -> u64 {
        self.collections.get(&collection_id).map(|c| c.total_supply).unwrap_or(0)
    }

    pub fn nfts_by_collection(&self, collection_id: u32, page: u32, page_size: u32) -> Vec<u64> {
        let ids = self.collection_ids.get(&collection_id).unwrap_or_default();
        let start = (page * page_size) as usize;
        let end = core::cmp::min(start + page_size as usize, ids.len());
        if start >= ids.len() {
            return Vec::new();
        }
        ids[start..end].to_vec()
    }

    pub fn metadata_uri(&self, token_id: u64) -> Option<String> {
        self.nfts.get(&token_id).map(|e| e.metadata_uri)
    }
}

#[odra::odra_error]
pub enum Error {
    CollectionNotFound = 1,
    NftNotFound = 2,
    NotOwner = 3,
    NotListed = 4,
}

#[cfg(test)]
mod tests {
    #[test]
    fn placeholder() {
        assert!(true);
    }
}
