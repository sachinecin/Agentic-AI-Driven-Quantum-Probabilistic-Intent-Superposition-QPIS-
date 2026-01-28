# QPIS Rust Back-Propagation Engine

High-performance recursive teleological back-propagation engine implemented in Rust.

## Building

To build the Rust extension:

```bash
cd qpis/engines/rust_backprop
cargo build --release
```

## Python Integration

The engine provides FFI bindings via PyO3 and automatically falls back to Python implementation if the Rust extension is not available.

## Features

- Parallel gradient computation using Rayon
- High-performance recursive back-propagation
- Zero-copy data transfer where possible
- Automatic fallback to Python implementation
