# QPIS: Quantum-Probabilistic Intent Superposition Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg)](https://www.rust-lang.org/)

## Overview

**Quantum-Probabilistic Intent Superposition (QPIS)** shifts the engineering focus from tracking *what a user is doing* to calculating the probability of *what a user is becoming* within a teleological loop. In high-agency systems, intent should be maintained as a **superposition of all logically possible outcomes**, collapsing into definite execution only when measurement events provide sufficient probability density.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Run examples
python examples/basic_superposition.py
python examples/teleological_backprop.py
python examples/signal_mesh_demo.py
python examples/complete_system.py
```

## Core Components

### 1. Intent Superposition & Measurement (`qpis/core/`)
- Quantum-inspired superposition of multiple intents
- Measurement events trigger probabilistic collapse
- Multiple collapse strategies (max probability, stochastic, entropy-driven)

### 2. Recursive Teleological Back-Propagation (`qpis/engines/`)
- Python implementation with recursive back-propagation
- Rust implementation for high-performance (10-100x faster)
- Goal-directed evolution via temporal gradient flow

### 3. Neuro-Signal Mesh SDK (`qpis/sdk/`)
- **HRV Processor**: Heart rate variability entropy extraction
- **Haptic Entropy**: Touch interaction uncertainty quantification
- **Signal Mesh**: Multi-modal entropy integration

### 4. World Models & Latent Intent Synthesis (`qpis/world_models/`)
- Synthesize intents from observation sequences
- Predict state transitions and simulate trajectories
- Latent space intent encoding and matching

## Examples

```python
from qpis import IntentSuperposition, Intent, MeasurementEvent, MeasurementCollapse

# Create superposition
intents = [
    Intent(label="purchase", amplitude=0.6),
    Intent(label="browse", amplitude=0.4),
]
superposition = IntentSuperposition(intents)

# Measurement & collapse
measurement = MeasurementEvent(event_type="click", confidence=0.9)
collapse_handler = MeasurementCollapse()
intent = collapse_handler.collapse(superposition, measurement, force=True)

print(f"Collapsed to: {intent.label}")
```

## Documentation

- **[Complete Documentation](docs/README.md)** - Full technical documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design
- **[Examples](examples/)** - Runnable examples and demos

## Structure

```
qpis/
├── core/                  # Intent superposition & measurement
│   ├── intent_superposition.py
│   └── measurement_event.py
├── engines/               # Teleological back-propagation
│   └── teleological_backprop.py
├── sdk/                   # Neuro-signal mesh
│   ├── hrv_processor.py
│   ├── haptic_entropy.py
│   └── signal_mesh.py
├── world_models/          # Latent intent & world models
│   ├── latent_intent_synthesis.py
│   └── world_model.py
└── utils/                 # Utilities

rust_engine/               # High-performance Rust implementation
├── Cargo.toml
└── src/
    └── lib.rs

examples/                  # Example scripts
├── basic_superposition.py
├── teleological_backprop.py
├── signal_mesh_demo.py
└── complete_system.py

docs/                      # Documentation
├── README.md
└── ARCHITECTURE.md
```

## Installation

```bash
# Basic installation
pip install -e .

# Development installation
pip install -e ".[dev]"

# Build Rust engine (optional, for performance)
cd rust_engine
cargo build --release
```

## Testing

```bash
# Python tests
pytest tests/

# Rust tests
cd rust_engine && cargo test
```

## License

MIT License - see LICENSE file

## Citation

```bibtex
@software{qpis2024,
  title={QPIS: Quantum-Probabilistic Intent Superposition Framework},
  author={QPIS Contributors},
  year={2024}
}
```

---

*"In high-agency systems, intent is not a point but a wavefunction."* 
