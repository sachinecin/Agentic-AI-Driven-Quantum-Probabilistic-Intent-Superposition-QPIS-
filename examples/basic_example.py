"""
Basic QPIS Example

Demonstrates the fundamental concepts of the QPIS framework:
- Intent superposition
- Measurement collapse
- Teleological back-propagation
"""

import numpy as np
from qpis import (
    IntentSuperposition,
    AgenticCoordinator,
    TeleologicalBackPropEngine,
    MeasurementCollapse,
    LatentIntentSynthesizer
)
from qpis.measurement import MeasurementType


def main():
    print("=" * 60)
    print("QPIS Framework - Basic Example")
    print("=" * 60)
    
    # 1. Create an intent superposition
    print("\n1. Creating Intent Superposition...")
    intent = IntentSuperposition(agent_id="user_001")
    
    # Add possible intent states
    intent.add_state(
        state_id="explore",
        description="User is exploring options",
        amplitude=0.6+0.2j,
        parameters={"confidence": 0.3, "cognitive_load": 0.7}
    )
    
    intent.add_state(
        state_id="decide",
        description="User is ready to make a decision",
        amplitude=0.4+0.1j,
        parameters={"confidence": 0.8, "cognitive_load": 0.4}
    )
    
    intent.add_state(
        state_id="abandon",
        description="User is considering abandoning the task",
        amplitude=0.2+0.05j,
        parameters={"confidence": 0.5, "cognitive_load": 0.6}
    )
    
    print(f"   Created superposition with {len(intent.states)} states")
    print(f"   Current probabilities:")
    for state_id, prob in intent.get_state_probabilities().items():
        print(f"      - {state_id}: {prob:.4f}")
    
    # 2. Evolve the superposition through time
    print("\n2. Evolving Superposition...")
    intent.evolve(time_delta=1.0)
    print(f"   Coherence after evolution: {intent.coherence:.4f}")
    print(f"   Updated probabilities:")
    for state_id, prob in intent.get_state_probabilities().items():
        print(f"      - {state_id}: {prob:.4f}")
    
    # 3. Teleological back-propagation
    print("\n3. Applying Teleological Back-Propagation...")
    backprop_engine = TeleologicalBackPropEngine(
        learning_rate=0.05,
        decay_factor=0.9
    )
    
    # Define a goal: we want user to decide
    goal = {
        "confidence": 0.9,
        "cognitive_load": 0.3
    }
    
    adjustments = backprop_engine.back_propagate(
        intent,
        target_goal=goal,
        time_horizon=2.0,
        recursive_depth=0
    )
    
    print(f"   Computed {len(adjustments)} gradient adjustments")
    print(f"   Top adjustments:")
    for state_id, adj in sorted(adjustments.items(), key=lambda x: abs(x[1]), reverse=True):
        print(f"      - {state_id}: {adj:+.4f}")
    
    # Apply gradients
    backprop_engine.apply_gradients(intent, adjustments)
    
    print(f"   Probabilities after optimization:")
    for state_id, prob in intent.get_state_probabilities().items():
        print(f"      - {state_id}: {prob:.4f}")
    
    # 4. Measurement and collapse
    print("\n4. Performing Measurement...")
    collapse_handler = MeasurementCollapse()
    
    collapsed_state = collapse_handler.measure(
        intent,
        measurement_type=MeasurementType.OBSERVATION,
        context={"sensor": "interaction_pattern"}
    )
    
    print(f"   Superposition collapsed to: '{collapsed_state.description}'")
    print(f"   Collapse probability: {collapsed_state.probability:.4f}")
    print(f"   State parameters: {collapsed_state.parameters}")
    
    # 5. Latent intent synthesis
    print("\n5. Latent Intent Synthesis...")
    synthesizer = LatentIntentSynthesizer(latent_dim=64)
    
    # Simulate some signals
    behavioral_signals = np.random.randn(32) * 0.5
    physiological_signals = np.random.randn(16) * 0.3
    
    latent_vec = synthesizer.synthesize(
        behavioral_signals=behavioral_signals,
        physiological_signals=physiological_signals
    )
    
    print(f"   Synthesized latent vector:")
    print(f"      - Dimensionality: {latent_vec.dimensionality}")
    print(f"      - Source: {latent_vec.source}")
    print(f"      - Confidence: {latent_vec.confidence:.4f}")
    print(f"      - Vector norm: {np.linalg.norm(latent_vec.vector):.4f}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
