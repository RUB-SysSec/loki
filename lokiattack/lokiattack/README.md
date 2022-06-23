# LokiAttack

Base tooling to attack Loki's handlers for the purpose of our evaluation. This is intended to be used in combination with plugins.

In essence, attack a VM requires to (1) identify specific handlers and (2) attacking/simplifying this specific handler. LokiAttack automated step 1: It identifies all VM handlers and provides an attacker (for each handler) with the handler parameters (x, y, c, and k) as well as concrete values (for dynamic attackers). Using symbolic execution, it obtains all code paths through the intermediate representation (IR) of the O3-optimized VM code. Using a plugin system, an attacker can then mount an attack using a specific technique such as symbolic execution or program synthesis for each path.

