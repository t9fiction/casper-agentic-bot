#[cfg(not(target_arch = "wasm32"))]
mod cli_impl {
    use casper_agentic_token_factory::token_factory::TokenFactory;
    use odra::host::{HostEnv, NoArgs};
    use odra_cli::{deploy::DeployScript, scenario::Scenario, ContractProvider, DeployedContractsContainer, DeployerExt, OdraCli};

    pub struct TokenFactoryDeployScript;

    impl DeployScript for TokenFactoryDeployScript {
        fn deploy(&self, env: &HostEnv, container: &mut DeployedContractsContainer) -> Result<(), odra_cli::deploy::Error> {
            let _factory = TokenFactory::load_or_deploy(&env, NoArgs, container, 350_000_000_000)?;
            Ok(())
        }
    }

    pub fn main() {
        OdraCli::new()
            .about("CLI tool for casper-agentic-token-factory")
            .deploy(TokenFactoryDeployScript)
            .contract::<TokenFactory>()
            .build()
            .run();
    }
}

#[cfg(not(target_arch = "wasm32"))]
fn main() {
    cli_impl::main();
}

#[cfg(target_arch = "wasm32")]
fn main() {}
