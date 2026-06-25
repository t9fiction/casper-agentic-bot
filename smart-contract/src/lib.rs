use odra::prelude::*;

#[odra::module]
pub struct Greeter {
    greeting: Var<String>,
    greet_count: Var<u32>,
}

#[odra::module]
impl Greeter {
    #[odra(init)]
    pub fn init(&mut self, greeting: String) {
        self.greeting.set(greeting);
        self.greet_count.set(0);
    }

    pub fn set_greeting(&mut self, greeting: String) {
        self.greeting.set(greeting);
    }

    pub fn greet(&mut self) -> String {
        let count = self.greet_count.get_or_default();
        self.greet_count.set(count + 1);
        let greeting = self.greeting.get().unwrap_or_default();
        format!("{}! You've been greeted {} times.", greeting, count + 1)
    }

    pub fn get_greeting(&self) -> String {
        self.greeting.get().unwrap_or_default()
    }

    pub fn get_greet_count(&self) -> u32 {
        self.greet_count.get_or_default()
    }
}
