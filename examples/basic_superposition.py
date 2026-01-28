"""
Example: Basic Intent Superposition and Measurement

Demonstrates core QPIS concepts: creating intent superpositions,
evolving them, and collapsing based on measurements.
"""

import numpy as np
from qpis.core.intent_superposition import IntentSuperposition, Intent
from qpis.core.measurement_event import MeasurementEvent, MeasurementCollapse, CollapseStrategy


def main():
    print("=" * 60)
    print("QPIS Example: Intent Superposition and Measurement")
    print("=" * 60)
    
    # Create initial intent superposition
    print("\n1. Creating Intent Superposition...")
    intents = [
        Intent(label="browse_products", amplitude=0.5 + 0.1j, teleological_weight=0.8),
        Intent(label="checkout", amplitude=0.3 + 0.2j, teleological_weight=1.0),
        Intent(label="search", amplitude=0.4 + 0.0j, teleological_weight=0.9),
        Intent(label="exit", amplitude=0.2 + 0.1j, teleological_weight=0.5),
    ]
    
    superposition = IntentSuperposition(intents)
    
    print(f"   Created superposition with {len(superposition.intents)} intents")
    print(f"   Probability distribution: {superposition.get_probability_distribution()}")
    print(f"   Initial entropy: {superposition.calculate_entropy():.3f}")
    
    # Apply phase shifts (quantum operation)
    print("\n2. Applying Phase Shifts...")
    superposition.apply_phase_shift("checkout", np.pi / 4)
    print(f"   Applied phase shift to 'checkout'")
    print(f"   Updated distribution: {superposition.get_probability_distribution()}")
    
    # Evolve toward a goal state
    print("\n3. Teleological Evolution...")
    goal_state = {
        "browse_products": 0.2,
        "checkout": 0.6,
        "search": 0.1,
        "exit": 0.1
    }
    
    print(f"   Goal state: {goal_state}")
    
    for step in range(5):
        superposition.evolve_teleological(goal_state, time_step=0.2)
        entropy = superposition.calculate_entropy()
        print(f"   Step {step + 1}: entropy={entropy:.3f}, "
              f"checkout_prob={superposition.get_probability_distribution()['checkout']:.3f}")
    
    # Create measurement events
    print("\n4. Measurement Events...")
    
    # Low confidence measurement - shouldn't collapse
    measurement1 = MeasurementEvent(
        event_type="mouse_hover",
        confidence=0.4,
        features=np.array([0.5, 0.3, 0.7])
    )
    
    collapse_handler = MeasurementCollapse(strategy=CollapseStrategy.MAXIMUM_PROBABILITY)
    
    should_collapse = collapse_handler.should_collapse(superposition, measurement1)
    print(f"   Low confidence measurement (0.4) -> Should collapse: {should_collapse}")
    
    # High confidence measurement - should collapse
    measurement2 = MeasurementEvent(
        event_type="button_click",
        confidence=0.9,
        features=np.array([0.8, 0.9, 0.6])
    )
    
    should_collapse = collapse_handler.should_collapse(superposition, measurement2, threshold=0.6)
    print(f"   High confidence measurement (0.9) -> Should collapse: {should_collapse}")
    
    # Calculate collapse probability density
    print("\n5. Probability Density Calculation...")
    densities = collapse_handler.calculate_collapse_probability_density(
        superposition, measurement2
    )
    print(f"   Collapse probability densities:")
    for label, density in sorted(densities.items(), key=lambda x: x[1], reverse=True):
        print(f"      {label}: {density:.3f}")
    
    # Perform collapse
    print("\n6. Collapsing Superposition...")
    collapsed_intent = collapse_handler.collapse(superposition, measurement2, force=True)
    
    print(f"   Collapsed to: {collapsed_intent.label}")
    print(f"   Probability: {collapsed_intent.probability:.3f}")
    print(f"   Superposition is collapsed: {superposition.is_collapsed()}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
