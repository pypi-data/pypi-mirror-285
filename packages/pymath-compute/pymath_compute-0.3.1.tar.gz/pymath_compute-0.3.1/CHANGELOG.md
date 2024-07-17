# Changelog

## [0.3.1] - 16/07/2024

### Added

- [Classifiers]: Add the classifiers for the project, including homepages and more stuff
- [Maturin]: Add information for the correct Rust/Python project be implemented
- [Tests]: Include the Engine and the solver tests
- [Variable]: Now, you can directly include the initial value of the variable in their definition
- [Variable]: Now, in the setter, the value set is going to be the closes bound if the expected value is outside the bound

### Fixed

- [Engine]: The engine now it updates the value using the setting method `value`, instead of going directly for the `_value`.

## [0.3.0] - 15/07/2024

### Added

- [Engine]: The engine for mathematical calculations, made it on Rust
- [OptSolver]: A Python solver written directly on Python that include an interface for easier implementation of different mathematical problems.
- [Examples]: Some examples of how to use this package in mathematical problems.

## [0.2.0] - 09/07/2024

### Added

- [Models]: Include the `.to_expression` and `.graph` methods.
- [MathFunction]: Allow to use `MathExpression` in it.

### Fixed

- [Typing]: Fix several typing modifications involving the MathExpression and MathFunction
- [Variable]: Fix the way to represent it
- [MathExpression]: Fix the way in how it search around some values to evaluate the expression

## [0.1.0] - XX/XX/2024

### Added

- [Models]: Include all the Mathematical models and include several interactions between them