# QPIS Quick Start Guide

## Installation

```bash
git clone <repository-url>
cd Agentic-AI-Driven-Quantum-Probabilistic-Intent-Superposition-QPIS-
pip install -e .
```

## 5-Minute Tutorial

### 1. Create an Intent Superposition

```python
from qpis import IntentSuperposition, Intent

# Create intents with probability amplitudes
intents = [
    Intent(label="purchase", amplitude=0.6),
    Intent(label="browse", amplitude=0.4),
]

# Create superposition
superposition = IntentSuperposition(intents)

# View probability distribution
print(superposition.get_probability_distribution())
# Output: {'purchase': 0.69, 'browse': 0.31}
```

### 2. Evolve Toward a Goal

```python
from qpis import TeleologicalEngine, TeleologicalGoal

# Create engine
engine = TeleologicalEngine(learning_rate=0.1)

# Define goal
goal = TeleologicalGoal(
    label="conversion",
    target_distribution={"purchase": 0.9, "browse": 0.1}
)
engine.add_goal(goal)

# Evolve over time
for t in range(10):
    superposition = engine.execute_teleological_cycle(superposition, float(t))
    
print(superposition.get_probability_distribution())
# Output: {'purchase': 0.87, 'browse': 0.13}  # Moved toward goal!
```

### 3. Integrate Physiological Signals

```python
from qpis.sdk import SignalMesh, HapticEvent

mesh = SignalMesh()

# Simulate confident user interaction
event = HapticEvent(
    timestamp=1.0,
    event_type="press",
    pressure=0.9,      # High pressure = confidence
    velocity=100.0,
    position=(100, 200)
)
mesh.ingest_haptic_event(event)

# Check decision readiness
influence = mesh.get_entropy_influence_on_intent(superposition)
print(f"Should collapse: {influence['should_collapse']}")
# Output: Should collapse: True
```

### 4. Collapse Superposition

```python
from qpis import MeasurementEvent, MeasurementCollapse

# Create measurement from signal mesh
measurement = mesh.create_measurement_event()

# Collapse superposition
collapse_handler = MeasurementCollapse()
collapsed_intent = collapse_handler.collapse(
    superposition, 
    measurement, 
    force=True
)

print(f"Final intent: {collapsed_intent.label}")
# Output: Final intent: purchase
```

## Run Complete Examples

```bash
# Basic superposition and measurement
python examples/basic_superposition.py

# Teleological back-propagation
python examples/teleological_backprop.py

# Signal mesh integration
python examples/signal_mesh_demo.py

# Complete system
python examples/complete_system.py
```

## Key Concepts

### Intent Superposition
Multiple possible intents exist simultaneously, each with a probability amplitude. Like Schrödinger's cat, but for user intent!

### Teleological Evolution
Future goals "pull" the present state toward desired outcomes through recursive back-propagation.

### Signal Mesh
Physiological signals (HRV, haptic) provide entropy measures that influence when to collapse the superposition.

### Measurement Collapse
When sufficient evidence accumulates, the superposition "collapses" into a single definite intent for execution.

## Next Steps

1. Read the [full documentation](README.md)
2. Explore the [architecture](ARCHITECTURE.md)
3. Check the [implementation summary](IMPLEMENTATION_SUMMARY.md)
4. Experiment with the examples
5. Build your own applications!

## Common Use Cases

- **E-commerce**: Predict purchase intent before explicit action
- **UX/UI**: Adapt interfaces based on latent intent
- **Gaming**: Anticipate player actions in real-time
- **Assistive Tech**: Improve brain-computer interfaces
- **Robotics**: Better human-robot collaboration

---

*"The best systems don't wait for you to decide—they understand what you're becoming."*
