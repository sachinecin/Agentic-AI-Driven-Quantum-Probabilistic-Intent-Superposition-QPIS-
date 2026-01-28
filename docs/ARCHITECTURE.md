# Architecture Documentation

## System Components

### 1. Core Layer

#### Intent Superposition (`qpis/core/intent_superposition.py`)
- Maintains quantum-inspired superposition of intents
- Each intent has complex probability amplitude
- Supports quantum operations (phase shifts, amplitude damping)
- Calculates entropy and probability distributions

#### Measurement & Collapse (`qpis/core/measurement_event.py`)
- Defines measurement events that trigger collapse
- Multiple collapse strategies (max probability, stochastic, entropy-driven)
- Calculates probability density for collapse decisions
- Records collapse history

### 2. Engines Layer

#### Teleological Back-Propagation (`qpis/engines/teleological_backprop.py`)
- Recursive algorithm propagating goal information backward through time
- Records trajectory of intent states
- Computes gradients from goal alignment
- Applies temporal decay to back-propagated signals
- Available in both Python and Rust implementations

### 3. SDK Layer

#### HRV Processor (`qpis/sdk/hrv_processor.py`)
- Detects R-peaks in ECG signals
- Computes time-domain metrics (SDNN, RMSSD, pNN50)
- Computes frequency-domain metrics (LF/HF power, ratio)
- Calculates sample entropy
- Extracts cognitive state indicators

#### Haptic Entropy (`qpis/sdk/haptic_entropy.py`)
- Processes haptic interaction events
- Computes temporal, pressure, velocity, and spatial entropy
- Calculates hesitation and confidence scores
- Provides intent influence factors

#### Signal Mesh (`qpis/sdk/signal_mesh.py`)
- Integrates multiple signal sources
- Maintains unified signal state
- Computes combined entropy
- Estimates cognitive load and decision readiness
- Creates measurement events from signal state

### 4. World Models Layer

#### Latent Intent Synthesis (`qpis/world_models/latent_intent_synthesis.py`)
- Encodes observations into latent space
- Registers intent templates
- Synthesizes latent intents from observation sequences
- Creates superpositions from latent intents
- Supports intent refinement

#### World Model (`qpis/world_models/world_model.py`)
- Maintains state representation
- Records state transitions
- Predicts next states given actions
- Simulates trajectories
- Evaluates trajectory quality

## Data Flow

```
Observations → Latent Synthesis → Intent Superposition
                                         ↓
                                   Teleological Evolution
                                         ↓
                                   Signal Mesh Influence
                                         ↓
                                   Measurement & Collapse
                                         ↓
                                   Execution
```

## Key Algorithms

### Recursive Teleological Back-Propagation

```
function recursive_backprop(depth, max_depth):
    if depth >= max_depth:
        return {}
    
    gradients = {}
    
    if depth == 0:
        # Base case: compute gradients from goal
        for intent in latest_state.intents:
            gradient = (target_prob - current_prob) * importance
            gradients[intent.label] = [gradient]
    
    if len(trajectory) > 1:
        # Recursive case: back-propagate
        future_gradients = recursive_backprop(depth + 1, max_depth)
        
        for label, future_grad in future_gradients.items():
            decayed_grad = future_grad * decay_rate
            gradients[label].extend(decayed_grad)
    
    return gradients
```

### Probability Density Calculation

```
function calculate_collapse_probability_density(superposition, measurement):
    for intent in superposition.intents:
        base_prob = intent.probability
        confidence_factor = measurement.confidence
        
        if features available:
            feature_similarity = cosine_similarity(
                measurement.features,
                intent.features
            )
        
        density = base_prob * confidence_factor * feature_similarity
    
    return normalize(densities)
```

## Performance Considerations

### Python vs Rust

- **Python**: Flexible, easy integration, good for prototyping
- **Rust**: 10-100x faster for large trajectories, memory efficient
- **Strategy**: Use Python for high-level logic, Rust for compute-intensive operations

### Optimization Tips

1. **Batch Processing**: Process multiple measurements together
2. **Caching**: Cache frequently computed values (entropy, similarities)
3. **Lazy Evaluation**: Defer expensive computations until needed
4. **Parallel Processing**: Process independent intents in parallel (Rust)

## Extension Points

### Custom Collapse Strategies

```python
class CustomCollapseStrategy(MeasurementCollapse):
    def _collapse_custom(self, superposition, measurement):
        # Implement custom logic
        return selected_intent
```

### Custom Signal Sources

```python
class CustomSignalProcessor:
    def process_signal(self, signal):
        # Extract entropy/features
        return metrics
    
    def get_influence(self, metrics):
        # Return influence factors
        return {"collapse_readiness": value}
```

### Custom Intent Templates

```python
# Register domain-specific intents
synthesizer.register_intent_template(
    "custom_intent",
    learned_template_vector,
    complexity=estimated_complexity
)
```
