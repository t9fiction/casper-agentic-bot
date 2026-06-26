use casper_agentic_greeter::greeter::Greeter;
use odra::host::{HostEnv, NoArgs};
use odra_cli::{deploy::DeployScript, scenario::Scenario, ContractProvider, DeployedContractsContainer, DeployerExt, OdraCli};

pub struct GreeterDeployScript;

impl DeployScript for GreeterDeployScript {
    fn deploy(&self, env: &HostEnv, container: &mut DeployedContractsContainer) -> Result<(), odra_cli::deploy::Error> {
        let _greeter = Greeter::load_or_deploy(&env, NoArgs, container, 350_000_000_000)?;
        Ok(())
    }
}

pub fn main() {
    OdraCli::new()
        .about("CLI tool for casper-agentic-greeter")
        .deploy(GreeterDeployScript)
        .contract::<Greeter>()
        .build()
        .run();
}
