"""
Example: Complete QPIS System

Integrates all components: Latent Intent Synthesis, World Models,
Teleological Back-Propagation, and Signal Mesh.
"""

import numpy as np
from qpis.core.intent_superposition import IntentSuperposition, Intent
from qpis.core.measurement_event import MeasurementCollapse, CollapseStrategy
from qpis.engines.teleological_backprop import TeleologicalEngine, TeleologicalGoal
from qpis.world_models.latent_intent_synthesis import LatentIntentSynthesizer
from qpis.world_models.world_model import WorldModel
from qpis.sdk.signal_mesh import SignalMesh
from qpis.sdk.haptic_entropy import HapticEvent


def main():
    print("=" * 70)
    print("QPIS Complete System Integration Example")
    print("=" * 70)
    
    # 1. Initialize all components
    print("\n1. Initializing QPIS System Components...")
    
    synthesizer = LatentIntentSynthesizer(latent_dim=32)
    world_model = WorldModel(state_dim=64)
    teleological_engine = TeleologicalEngine(learning_rate=0.1, decay_rate=0.9)
    signal_mesh = SignalMesh()
    collapse_handler = MeasurementCollapse(strategy=CollapseStrategy.ENTROPY_DRIVEN)
    
    print("   ✓ Latent Intent Synthesizer")
    print("   ✓ World Model")
    print("   ✓ Teleological Engine")
    print("   ✓ Signal Mesh")
    print("   ✓ Measurement Collapse Handler")
    
    # 2. Register intent templates
    print("\n2. Registering Intent Templates...")
    
    templates = {
        "purchase": np.random.randn(32) * 0.5 + np.array([1.0] * 32),
        "browse": np.random.randn(32) * 0.5,
        "compare": np.random.randn(32) * 0.5 - np.array([0.5] * 32),
        "exit": np.random.randn(32) * 0.5 - np.array([1.0] * 32),
    }
    
    for label, template in templates.items():
        template = template / np.linalg.norm(template)  # Normalize
        complexity = {"purchase": 0.7, "browse": 0.3, "compare": 0.5, "exit": 0.2}[label]
        synthesizer.register_intent_template(label, template, complexity)
        print(f"   Registered: {label} (complexity={complexity})")
    
    # 3. Simulate observations and synthesize intents
    print("\n3. Observing User Behavior and Synthesizing Intents...")
    
    observations = [
        {"action": "view_product", "duration": 15.0, "scroll_depth": 0.6},
        {"action": "view_product", "duration": 22.0, "scroll_depth": 0.8},
        {"action": "add_to_cart_hover", "duration": 3.0, "scroll_depth": 0.9},
        {"action": "view_reviews", "duration": 30.0, "scroll_depth": 0.7},
    ]
    
    print(f"   Processing {len(observations)} observations...")
    latent_intents = synthesizer.synthesize_intents(observations, top_k=4)
    
    print(f"\n   Synthesized Intents:")
    for li in latent_intents:
        print(f"      {li.label}: confidence={li.confidence:.3f}, complexity={li.complexity:.2f}")
    
    # 4. Create intent superposition
    print("\n4. Creating Intent Superposition...")
    superposition = synthesizer.create_superposition_from_latent(latent_intents)
    
    prob_dist = superposition.get_probability_distribution()
    entropy = superposition.calculate_entropy()
    print(f"   Probability distribution: {prob_dist}")
    print(f"   Entropy: {entropy:.3f}")
    
    # 5. Set teleological goal
    print("\n5. Setting Teleological Goal...")
    goal = TeleologicalGoal(
        label="conversion_goal",
        target_distribution={"purchase": 0.8, "browse": 0.1, "compare": 0.05, "exit": 0.05},
        importance=1.0,
        horizon=10.0
    )
    teleological_engine.add_goal(goal)
    print(f"   Goal: {goal.label}")
    print(f"   Target: {goal.target_distribution}")
    
    # 6. Update world model
    print("\n6. Updating World Model...")
    world_model.update_state(observations[0], timestamp=0.0)
    print(f"   World state initialized")
    
    # 7. Run integrated simulation
    print("\n7. Running Integrated Simulation...")
    print("   (Combining: Teleology + World Model + Signal Mesh)")
    
    for step in range(10):
        timestamp = float(step)
        
        # Evolve with teleological engine
        superposition = teleological_engine.execute_teleological_cycle(
            superposition, timestamp
        )
        
        # Simulate haptic interaction
        if step % 3 == 0:
            # Increasingly confident interactions
            pressure = 0.4 + step * 0.05
            event = HapticEvent(
                timestamp=timestamp,
                event_type="press",
                pressure=min(1.0, pressure),
                velocity=20.0 + step * 5,
                position=(100 + step * 10, 200)
            )
            signal_mesh.ingest_haptic_event(event)
        
        # Update world model
        if step < len(observations):
            world_model.update_state(observations[step % len(observations)], timestamp)
        
        # Check status every few steps
        if step % 3 == 0:
            prob_dist = superposition.get_probability_distribution()
            entropy = superposition.calculate_entropy()
            
            mesh_summary = signal_mesh.get_mesh_summary()
            influence = signal_mesh.get_entropy_influence_on_intent(superposition)
            
            print(f"\n   Step {step}:")
            print(f"      Purchase probability: {prob_dist.get('purchase', 0):.3f}")
            print(f"      Entropy: {entropy:.3f}")
            print(f"      Decision readiness: {mesh_summary.get('decision_readiness', 0):.3f}")
            print(f"      Should collapse: {influence.get('should_collapse', False)}")
    
    # 8. Final measurement and collapse
    print("\n8. Final Measurement and Collapse Decision...")
    
    measurement = signal_mesh.create_measurement_event()
    if measurement:
        print(f"   Measurement confidence: {measurement.confidence:.3f}")
        
        should_collapse = collapse_handler.should_collapse(
            superposition, measurement, threshold=0.6
        )
        print(f"   Should collapse: {should_collapse}")
        
        if should_collapse:
            collapsed_intent = collapse_handler.collapse(
                superposition, measurement, force=True
            )
            print(f"\n   ✓ COLLAPSED TO: {collapsed_intent.label}")
            print(f"   ✓ Probability: {collapsed_intent.probability:.3f}")
        else:
            print(f"   Maintaining superposition (more observation needed)")
    
    # 9. System summary
    print("\n9. System Summary...")
    
    tele_summary = teleological_engine.get_trajectory_summary()
    synth_summary = synthesizer.get_synthesis_summary()
    world_summary = world_model.get_model_summary()
    mesh_summary = signal_mesh.get_mesh_summary()
    
    print(f"\n   Teleological Engine:")
    print(f"      States: {tele_summary['states']}")
    print(f"      Final alignment: {tele_summary['final_alignment']:.3f}")
    
    print(f"\n   Intent Synthesizer:")
    print(f"      Total syntheses: {synth_summary['total_syntheses']}")
    print(f"      Recent top intent: {synth_summary['recent_top_intent']}")
    
    print(f"\n   World Model:")
    print(f"      Transitions recorded: {world_summary['transitions_recorded']}")
    
    print(f"\n   Signal Mesh:")
    print(f"      Combined entropy: {mesh_summary['combined_entropy']:.3f}")
    print(f"      Decision readiness: {mesh_summary['decision_readiness']:.3f}")
    
    print("\n" + "=" * 70)
    print("Complete QPIS system successfully demonstrated!")
    print("All components working together to synthesize, evolve,")
    print("and collapse intent superpositions.")
    print("=" * 70)


if __name__ == "__main__":
    main()
