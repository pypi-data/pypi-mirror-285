# Chiklisp Builder

Use this wheel in conjunction with `runtime_builder` to manage building of chiklisp at build time or during development.

# Use

Add `chiklisp_builder` as a buildtime dependency and a development-time dependency. Don't add it as a runtime dependency, as the klvm `.hex` files should be built and included with the wheel. The source does not need to be.

Add `chiklisp_loader` as a runtime dependency to get the `load_program` function, which will call the building function if present (as it should be at development time.)

# FAQ

Why isn't this included as part of `runtime_builder`?

The `runtime_builder` wheel is intended to provide a general solution for non-python artifacts. Although Chiklisp build was the inspiration for `runtime_builder`, it's just one potential use. This wheel is the specific implementation of chiklisp builds for use with `runtime_builder`.
