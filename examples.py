"""
QPIS Example Implementation
Demonstrates practical usage of the Quantum-Probabilistic Intent Superposition system
"""

from qpis_core import (
    QPISAgent, 
    PhysiologicalSignal, 
    DigitalMicroGesture,
    IntentState
)
import time
import random


def simulate_focused_work_session():
    """
    Simulates a user working intensely on a project
    Should trigger autonomous execution when focus is high
    """
    print("\n" + "="*70)
    print("SCENARIO 1: Focused Work Session - Project Completion")
    print("="*70)
    print("User is working intensely on completing a project...")
    print()
    
    agent = QPISAgent()
    
    for i in range(15):
        # Simulate increasing focus
        entropy = max(0.1, 0.8 - i * 0.06)  # Entropy decreases (more focused)
        cognitive_load = min(0.9, 0.4 + i * 0.04)  # Load increases
        stress = min(0.5, 0.2 + i * 0.02)  # Mild stress increase
        
        physiological = PhysiologicalSignal(
            timestamp=time.time(),
            heart_rate_variability=0.6 - i * 0.02,
            cognitive_load=cognitive_load,
            entropy=entropy,
            stress_level=stress
        )
        
        gesture = DigitalMicroGesture(
            timestamp=time.time(),
            action_type="typing",
            repetition_count=i + 5,
            velocity=min(0.95, 0.6 + i * 0.03),  # Velocity increases
            precision=min(0.95, 0.7 + i * 0.02),  # Precision increases
            context={"application": "code_editor", "file": "main.py"}
        )
        
        environment = {
            "active_applications": ["code_editor", "terminal", "browser"],
            "open_files": 8,
            "time_in_session": i * 120,  # 2 minutes per step
            "project_status": "near_completion"
        }
        
        result = agent.process_input(physiological, gesture, environment)
        
        dominant_state, prob = result['dominant_intent']
        print(f"Step {i+1:2d}: Intent={dominant_state.value:15s} P={prob:.3f} "
              f"Entropy={entropy:.2f} Focus={cognitive_load:.2f}")
        
        if result['triggered']:
            print(f"\n🎯 TRIGGER FIRED!")
            print(f"   Target State: {result['target_state'].value}")
            print(f"   Action: {result['action']}")
            print(f"   Probability: {prob:.3f}")
            break
    
    print()


def simulate_help_needed_scenario():
    """
    Simulates a user struggling and needing help
    Should trigger help offering when stress is high
    """
    print("\n" + "="*70)
    print("SCENARIO 2: User Needs Help - High Stress Detection")
    print("="*70)
    print("User is struggling with a problem, making errors...")
    print()
    
    agent = QPISAgent()
    
    for i in range(12):
        # Simulate increasing stress and confusion
        entropy = min(0.9, 0.5 + i * 0.04)  # Entropy increases (confused)
        stress = min(0.95, 0.3 + i * 0.06)  # Stress increases significantly
        cognitive_load = min(0.95, 0.5 + i * 0.04)
        
        physiological = PhysiologicalSignal(
            timestamp=time.time(),
            heart_rate_variability=0.4 + random.uniform(-0.1, 0.1),
            cognitive_load=cognitive_load,
            entropy=entropy,
            stress_level=stress
        )
        
        # Erratic gestures
        gesture = DigitalMicroGesture(
            timestamp=time.time(),
            action_type=random.choice(["typing", "clicking", "scrolling"]),
            repetition_count=i,
            velocity=0.3 + random.uniform(-0.2, 0.2),  # Low, erratic velocity
            precision=max(0.2, 0.6 - i * 0.04),  # Precision decreases
            context={"application": "browser", "search_count": i}
        )
        
        environment = {
            "active_applications": ["browser", "editor", "docs"],
            "open_files": 15,
            "failed_attempts": i,
            "time_in_session": i * 90
        }
        
        result = agent.process_input(physiological, gesture, environment)
        
        dominant_state, prob = result['dominant_intent']
        print(f"Step {i+1:2d}: Intent={dominant_state.value:15s} P={prob:.3f} "
              f"Stress={stress:.2f} Entropy={entropy:.2f}")
        
        if result['triggered']:
            print(f"\n🆘 HELP TRIGGERED!")
            print(f"   Target State: {result['target_state'].value}")
            print(f"   Action: {result['action']}")
            print(f"   Cognitive State: {result['cognitive_state']}")
            break
    
    print()


def simulate_exploration_mode():
    """
    Simulates a user in exploration mode
    System should maintain superposition without triggering
    """
    print("\n" + "="*70)
    print("SCENARIO 3: Exploration Mode - No Trigger")
    print("="*70)
    print("User is casually browsing and exploring...")
    print()
    
    agent = QPISAgent()
    
    for i in range(8):
        # High entropy, low stress, varied actions
        physiological = PhysiologicalSignal(
            timestamp=time.time(),
            heart_rate_variability=0.7,
            cognitive_load=0.3 + random.uniform(-0.1, 0.1),
            entropy=0.7 + random.uniform(-0.1, 0.1),  # High entropy
            stress_level=0.2
        )
        
        gesture = DigitalMicroGesture(
            timestamp=time.time(),
            action_type=random.choice(["scrolling", "clicking", "reading"]),
            repetition_count=random.randint(1, 3),
            velocity=0.4 + random.uniform(-0.2, 0.2),
            precision=0.5 + random.uniform(-0.2, 0.2),
            context={"application": random.choice(["browser", "reader", "notes"])}
        )
        
        environment = {
            "active_applications": ["browser", "reader"],
            "open_files": random.randint(2, 5),
            "time_in_session": i * 45
        }
        
        result = agent.process_input(physiological, gesture, environment)
        
        dominant_state, prob = result['dominant_intent']
        print(f"Step {i+1}: Intent={dominant_state.value:15s} P={prob:.3f} "
              f"Mode=Exploration")
        
        # Show all intent probabilities
        if i == 7:  # Last step
            print("\n   Final Intent Superposition:")
            for state in IntentState:
                p = agent.intent_superposition.get_probability(state)
                print(f"     {state.value:15s}: {p:.3f}")
    
    print(f"\n✓ System maintained superposition - No trigger (as expected)")
    print()


def demonstrate_probability_backflow():
    """
    Demonstrates the probability back-flow calculation
    """
    print("\n" + "="*70)
    print("SCENARIO 4: Probability Back-Flow Demonstration")
    print("="*70)
    print("Showing how system reasons backward from goal states...")
    print()
    
    agent = QPISAgent()
    
    # Single focused input
    physiological = PhysiologicalSignal(
        timestamp=time.time(),
        heart_rate_variability=0.5,
        cognitive_load=0.7,
        entropy=0.3,
        stress_level=0.3
    )
    
    gesture = DigitalMicroGesture(
        timestamp=time.time(),
        action_type="typing",
        repetition_count=10,
        velocity=0.8,
        precision=0.85,
        context={"application": "code_editor"}
    )
    
    environment = {
        "active_applications": ["editor", "terminal"],
        "open_files": 5,
        "project_status": "active"
    }
    
    result = agent.process_input(physiological, gesture, environment)
    
    print("Generated Goal States:")
    for goal in result['goal_states']:
        print(f"  • {goal.goal_id:20s} - {goal.description:25s} P={goal.probability:.3f}")
    
    print("\nProbability Back-Flow (which goal user is gravitating toward):")
    for goal_id, prob in sorted(result['probability_flow'].items(), 
                                 key=lambda x: x[1], reverse=True):
        bar = "█" * int(prob * 50)
        print(f"  {goal_id:20s}: {bar:50s} {prob:.3f}")
    
    print("\nResulting Intent Superposition:")
    for state in IntentState:
        p = agent.intent_superposition.get_probability(state)
        if p > 0.1:  # Only show significant probabilities
            bar = "█" * int(p * 50)
            print(f"  {state.value:15s}: {bar:50s} {p:.3f}")
    
    print()


def demonstrate_entanglement():
    """
    Demonstrates intention entanglement between user and environment
    """
    print("\n" + "="*70)
    print("SCENARIO 5: Intention Entanglement Demonstration")
    print("="*70)
    print("Showing entanglement between user cognitive state and environment...")
    print()
    
    agent = QPISAgent()
    
    scenarios = [
        ("Low Load, Simple Environment", 0.3, 2),
        ("Medium Load, Medium Environment", 0.6, 5),
        ("High Load, Complex Environment", 0.9, 10),
    ]
    
    for desc, cognitive_load, env_complexity in scenarios:
        physiological = PhysiologicalSignal(
            timestamp=time.time(),
            heart_rate_variability=0.5,
            cognitive_load=cognitive_load,
            entropy=0.4,
            stress_level=0.3
        )
        
        environment = {
            f"context_{i}": f"value_{i}" for i in range(env_complexity)
        }
        
        agent.entanglement_core.update_user_state(physiological)
        agent.entanglement_core.update_environment(environment)
        
        entangled = agent.entanglement_core.get_entangled_state()
        
        print(f"\n{desc}:")
        print(f"  Cognitive Load:       {cognitive_load:.2f}")
        print(f"  Environment Size:     {env_complexity}")
        print(f"  Entangled State:      ({entangled[0]:.3f}, {entangled[1]:.3f})")
        print(f"  Entanglement Strength: {abs(entangled[0] - cognitive_load):.3f}")
    
    print()


def main():
    """Run all example scenarios"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  QPIS (Quantum-Probabilistic Intent Superposition) Examples".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "="*68 + "╝")
    
    # Run all scenarios
    simulate_focused_work_session()
    simulate_help_needed_scenario()
    simulate_exploration_mode()
    demonstrate_probability_backflow()
    demonstrate_entanglement()
    
    print("\n" + "="*70)
    print("All scenarios completed!")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. System maintains intent as superposition until certainty is high")
    print("  2. Teleological reasoning: works backward from goals to current state")
    print("  3. Physiological signals (entropy, stress) guide autonomous triggering")
    print("  4. User-environment entanglement creates holistic understanding")
    print("  5. Proactive actions occur before explicit user request")
    print()


if __name__ == "__main__":
    main()

