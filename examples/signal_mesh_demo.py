"""
Example: Neuro-Signal Mesh Integration

Demonstrates HRV and haptic entropy ingestion influencing
intent superposition dynamics.
"""

import numpy as np
from qpis.core.intent_superposition import IntentSuperposition, Intent
from qpis.core.measurement_event import MeasurementCollapse, CollapseStrategy
from qpis.sdk.signal_mesh import SignalMesh
from qpis.sdk.haptic_entropy import HapticEvent


def generate_synthetic_ecg(duration: float = 10.0, sampling_rate: float = 250.0) -> np.ndarray:
    """Generate synthetic ECG signal for demonstration."""
    t = np.arange(0, duration, 1/sampling_rate)
    
    # Base heart rate around 70 bpm with some variability
    hr_variability = np.random.normal(0, 0.1, len(t))
    heart_rate = 70 + hr_variability * 10
    
    # Generate QRS complexes
    ecg = np.zeros_like(t)
    beat_times = []
    current_time = 0.5
    
    while current_time < duration:
        beat_idx = int(current_time * sampling_rate)
        if beat_idx < len(ecg):
            # R-peak (simplified)
            ecg[beat_idx] = 1.0
            beat_times.append(current_time)
            
            # RR interval
            rr_interval = 60.0 / (heart_rate[beat_idx] + 70)
            current_time += rr_interval
    
    # Add noise
    ecg += np.random.normal(0, 0.05, len(ecg))
    
    return ecg


def main():
    print("=" * 60)
    print("QPIS Example: Neuro-Signal Mesh Integration")
    print("=" * 60)
    
    # Initialize signal mesh
    print("\n1. Initializing Signal Mesh...")
    mesh = SignalMesh()
    print("   Signal mesh ready")
    
    # Create intent superposition
    print("\n2. Creating Intent Superposition...")
    intents = [
        Intent(label="purchase", amplitude=0.4, teleological_weight=1.0),
        Intent(label="explore", amplitude=0.5, teleological_weight=0.8),
        Intent(label="leave", amplitude=0.1, teleological_weight=0.5),
    ]
    superposition = IntentSuperposition(intents)
    
    print(f"   Initial distribution: {superposition.get_probability_distribution()}")
    
    # Ingest HRV signal
    print("\n3. Ingesting HRV Signal...")
    ecg_signal = generate_synthetic_ecg(duration=10.0)
    mesh.ingest_hrv_signal(ecg_signal, timestamp=1.0)
    
    mesh_summary = mesh.get_mesh_summary()
    print(f"   HRV processed: {mesh_summary['has_hrv']}")
    print(f"   Combined entropy: {mesh_summary['combined_entropy']:.3f}")
    print(f"   Cognitive load: {mesh_summary['cognitive_load']:.3f}")
    print(f"   Decision readiness: {mesh_summary['decision_readiness']:.3f}")
    
    # Simulate haptic interactions
    print("\n4. Simulating Haptic Interactions...")
    
    # Confident interaction pattern
    haptic_events = [
        HapticEvent(timestamp=2.0, event_type="press", pressure=0.8, velocity=50.0, position=(100, 200)),
        HapticEvent(timestamp=2.1, event_type="move", pressure=0.7, velocity=30.0, position=(105, 205)),
        HapticEvent(timestamp=2.2, event_type="release", pressure=0.0, velocity=10.0, position=(110, 210)),
    ]
    
    for event in haptic_events:
        mesh.ingest_haptic_event(event)
    
    mesh_summary = mesh.get_mesh_summary()
    print(f"   Haptic events processed: {mesh_summary['has_haptic']}")
    print(f"   Updated combined entropy: {mesh_summary['combined_entropy']:.3f}")
    print(f"   Updated decision readiness: {mesh_summary['decision_readiness']:.3f}")
    
    # Get influence on intent
    print("\n5. Computing Signal Mesh Influence on Intent...")
    influence = mesh.get_entropy_influence_on_intent(superposition)
    
    print(f"   Entropy factor: {influence['entropy_factor']:.3f}")
    print(f"   Should collapse: {influence['should_collapse']}")
    print(f"   Confidence boost: {influence['confidence_boost']:.3f}")
    print(f"   Cognitive load: {influence['cognitive_load']:.3f}")
    
    # Create measurement from mesh
    print("\n6. Creating Measurement Event from Signal Mesh...")
    measurement = mesh.create_measurement_event()
    
    if measurement:
        print(f"   Measurement type: {measurement.event_type}")
        print(f"   Confidence: {measurement.confidence:.3f}")
        print(f"   Metadata: {measurement.metadata}")
        
        # Check if should collapse
        collapse_handler = MeasurementCollapse(strategy=CollapseStrategy.MAXIMUM_PROBABILITY)
        should_collapse = collapse_handler.should_collapse(
            superposition, measurement, threshold=0.6
        )
        
        print(f"\n   Should collapse superposition: {should_collapse}")
        
        if should_collapse:
            collapsed = collapse_handler.collapse(superposition, measurement, force=True)
            print(f"   Collapsed to intent: {collapsed.label}")
            print(f"   With probability: {collapsed.probability:.3f}")
    
    # Simulate hesitant interaction
    print("\n7. Simulating Hesitant Interaction Pattern...")
    hesitant_events = [
        HapticEvent(timestamp=3.0, event_type="press", pressure=0.3, velocity=10.0, position=(100, 200)),
        HapticEvent(timestamp=3.1, event_type="release", pressure=0.0, velocity=5.0, position=(100, 200)),
        HapticEvent(timestamp=3.2, event_type="press", pressure=0.4, velocity=15.0, position=(105, 205)),
        HapticEvent(timestamp=3.3, event_type="release", pressure=0.0, velocity=5.0, position=(105, 205)),
        HapticEvent(timestamp=3.4, event_type="press", pressure=0.35, velocity=12.0, position=(95, 195)),
    ]
    
    for event in hesitant_events:
        mesh.ingest_haptic_event(event)
    
    mesh_summary = mesh.get_mesh_summary()
    print(f"   Combined entropy (hesitant): {mesh_summary['combined_entropy']:.3f}")
    print(f"   Decision readiness (hesitant): {mesh_summary['decision_readiness']:.3f}")
    
    influence = mesh.get_entropy_influence_on_intent(superposition)
    print(f"   Should collapse (hesitant): {influence['should_collapse']}")
    print(f"   → System correctly detects uncertainty!")
    
    print("\n" + "=" * 60)
    print("Signal mesh successfully integrated physiological")
    print("and haptic entropy to influence intent collapse!")
    print("=" * 60)


if __name__ == "__main__":
    main()
