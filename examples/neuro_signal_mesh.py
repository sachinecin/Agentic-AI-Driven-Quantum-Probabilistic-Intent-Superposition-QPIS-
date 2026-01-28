"""
Neuro-Signal Mesh Example

Demonstrates the Neuro-Signal Mesh SDK with HRV and haptic processing.
"""

import numpy as np
from qpis.sdk import HRVProcessor, HapticProcessor, SignalMeshCoordinator
from qpis.sdk.haptic.processor import HapticEventType
from qpis.world_models import LatentIntentSynthesizer


def main():
    print("=" * 60)
    print("QPIS Framework - Neuro-Signal Mesh")
    print("=" * 60)
    
    # 1. Initialize processors
    print("\n1. Initializing Signal Processors...")
    hrv_processor = HRVProcessor(sampling_rate=1000.0, window_size=300)
    haptic_processor = HapticProcessor(window_size=5.0)
    mesh_coordinator = SignalMeshCoordinator(hrv_processor, haptic_processor)
    
    print("   ✓ HRV Processor initialized")
    print("   ✓ Haptic Processor initialized")
    print("   ✓ Signal Mesh Coordinator initialized")
    
    # 2. Simulate HRV signals
    print("\n2. Ingesting HRV Signals...")
    # Simulate a heartbeat signal (simplified ECG-like)
    time = np.linspace(0, 10, 10000)  # 10 seconds at 1000 Hz
    heartbeat_signal = np.sin(2 * np.pi * 1.2 * time)  # ~72 BPM
    heartbeat_signal += 0.1 * np.random.randn(len(time))  # Add noise
    
    # Add R-peaks (heartbeats)
    for i in range(0, len(time), 833):  # ~72 BPM
        if i < len(heartbeat_signal):
            heartbeat_signal[i] += 1.5
    
    hrv_processor.ingest_signal(heartbeat_signal)
    
    # Detect heartbeats
    peaks = hrv_processor.detect_heartbeats()
    print(f"   Detected {len(peaks)} heartbeats")
    
    # Compute HRV metrics
    hrv_metrics = None
    if len(peaks) >= 2:
        rr_intervals = hrv_processor.compute_rr_intervals(peaks)
        hrv_metrics = hrv_processor.compute_metrics(rr_intervals)
        
        if hrv_metrics:
            print(f"   HRV Metrics:")
            print(f"      - Mean HR: {hrv_metrics.mean_hr:.1f} BPM")
            print(f"      - SDNN: {hrv_metrics.sdnn:.2f} ms")
            print(f"      - RMSSD: {hrv_metrics.rmssd:.2f} ms")
            print(f"      - Entropy: {hrv_metrics.entropy:.4f}")
            
            arousal = hrv_processor.get_arousal_level(hrv_metrics)
            print(f"      - Arousal level: {arousal:.4f}")
    
    # 3. Simulate haptic interactions
    print("\n3. Ingesting Haptic Events...")
    
    # Simulate user interactions
    haptic_events = [
        (HapticEventType.TAP, 0.8, 0.1),
        (HapticEventType.TAP, 0.7, 0.1),
        (HapticEventType.SWIPE, 0.6, 0.3),
        (HapticEventType.PRESS, 0.9, 0.5),
        (HapticEventType.TAP, 0.8, 0.1),
    ]
    
    for event_type, intensity, duration in haptic_events:
        haptic_processor.ingest_event(
            event_type=event_type,
            intensity=intensity,
            duration=duration
        )
    
    print(f"   Ingested {len(haptic_events)} haptic events")
    
    # Compute haptic metrics
    haptic_metrics = haptic_processor.compute_metrics()
    if haptic_metrics:
        print(f"   Haptic Metrics:")
        print(f"      - Event rate: {haptic_metrics.event_rate:.2f} events/s")
        print(f"      - Mean intensity: {haptic_metrics.mean_intensity:.4f}")
        print(f"      - Entropy: {haptic_metrics.entropy:.4f}")
        print(f"      - Pattern complexity: {haptic_metrics.pattern_complexity:.4f}")
        
        confidence = haptic_processor.get_interaction_confidence(haptic_metrics)
        print(f"      - Interaction confidence: {confidence:.4f}")
    
    # 4. Compute unified mesh state
    print("\n4. Computing Signal Mesh State...")
    mesh_state = mesh_coordinator.compute_mesh_state()
    
    print(f"   Mesh State:")
    print(f"      - Active sources: {[s.value for s in mesh_state.active_sources]}")
    print(f"      - Coherence: {mesh_state.coherence:.4f}")
    print(f"      - Confidence: {mesh_state.confidence:.4f}")
    print(f"      - Entropy vector shape: {mesh_state.entropy_vector.shape}")
    
    # 5. Predict intent state from mesh
    print("\n5. Predicting Intent State...")
    intent_states = mesh_coordinator.predict_intent_state(mesh_state)
    
    print(f"   Intent State Probabilities:")
    for state_name, prob in sorted(intent_states.items(), key=lambda x: x[1], reverse=True):
        print(f"      - {state_name}: {prob:.4f}")
    
    # 6. Synthesize latent intent
    print("\n6. Synthesizing Latent Intent...")
    synthesizer = LatentIntentSynthesizer(latent_dim=128)
    
    # Extract features - use defaults if hrv_metrics is None
    if hrv_metrics:
        hrv_features = hrv_processor.extract_intent_features(hrv_metrics)
    else:
        hrv_features = np.zeros(8)  # Default HRV features
    
    haptic_features = haptic_processor.extract_intent_features(haptic_metrics)
    
    # Synthesize
    latent_intent = synthesizer.synthesize(
        physiological_signals=hrv_features,
        behavioral_signals=haptic_features
    )
    
    print(f"   Latent Intent:")
    print(f"      - Dimensionality: {latent_intent.dimensionality}")
    print(f"      - Source: {latent_intent.source}")
    print(f"      - Confidence: {latent_intent.confidence:.4f}")
    
    # Predict trajectory
    trajectory = synthesizer.predict_trajectory(latent_intent, time_steps=5)
    print(f"      - Predicted trajectory: {len(trajectory)} steps")
    
    # 7. Detect state transitions
    print("\n7. Analyzing State Transitions...")
    
    # Simulate more mesh states
    for _ in range(10):
        mesh_coordinator.compute_mesh_state()
    
    transitions = mesh_coordinator.detect_state_transitions(window_size=10)
    
    if transitions:
        print(f"   Detected {len(transitions)} transitions:")
        for trans in transitions:
            print(f"      - {trans['type']}: {trans['direction']} (magnitude: {trans['magnitude']:.4f})")
    else:
        print("   No significant transitions detected")
    
    print("\n" + "=" * 60)
    print("Neuro-signal mesh example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
