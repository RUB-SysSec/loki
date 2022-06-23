# Obfucsator

Our Rust component responsible for processing the lifted input function by applying obfuscating transformations.

# Approach

1. Parse and rewrite `lifted_input.txt`
2. Generate handler table `MetaAlu` with hardened and keyed `ALU`s as handler
3. Write bytecode file

