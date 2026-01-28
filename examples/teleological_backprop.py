"""
Example: Teleological Back-Propagation

Demonstrates the recursive teleological back-propagation engine
pulling intent evolution toward desired goal states.
"""

import numpy as np
from qpis.core.intent_superposition import IntentSuperposition, Intent
from qpis.engines.teleological_backprop import (
    TeleologicalEngine, TeleologicalGoal
)


def main():
    print("=" * 60)
    print("QPIS Example: Teleological Back-Propagation")
    print("=" * 60)
    
    # Initialize engine
    print("\n1. Initializing Teleological Engine...")
    engine = TeleologicalEngine(learning_rate=0.15, decay_rate=0.9)
    
    # Define goal
    goal = TeleologicalGoal(
        label="purchase_goal",
        target_distribution={
            "add_to_cart": 0.7,
            "continue_shopping": 0.2,
            "exit": 0.1
        },
        importance=1.0,
        horizon=10.0
    )
    engine.add_goal(goal)
    print(f"   Set goal: {goal.label}")
    print(f"   Target distribution: {goal.target_distribution}")
    
    # Create initial superposition
    print("\n2. Creating Initial Intent Superposition...")
    intents = [
        Intent(label="add_to_cart", amplitude=0.3, teleological_weight=1.0),
        Intent(label="continue_shopping", amplitude=0.6, teleological_weight=0.7),
        Intent(label="exit", amplitude=0.1, teleological_weight=0.3),
    ]
    superposition = IntentSuperposition(intents)
    
    print(f"   Initial distribution: {superposition.get_probability_distribution()}")
    print(f"   Initial entropy: {superposition.calculate_entropy():.3f}")
    
    # Run teleological cycles
    print("\n3. Running Teleological Cycles...")
    print("   (Goal: Pull 'add_to_cart' from 0.30 → 0.70)")
    
    for cycle in range(15):
        timestamp = float(cycle)
        
        # Execute teleological cycle
        superposition = engine.execute_teleological_cycle(superposition, timestamp)
        
        prob_dist = superposition.get_probability_distribution()
        entropy = superposition.calculate_entropy()
        
        if cycle % 3 == 0:
            print(f"\n   Cycle {cycle}:")
            print(f"      add_to_cart: {prob_dist['add_to_cart']:.3f}")
            print(f"      continue_shopping: {prob_dist['continue_shopping']:.3f}")
            print(f"      exit: {prob_dist['exit']:.3f}")
            print(f"      Entropy: {entropy:.3f}")
    
    # Show final results
    print("\n4. Final Results...")
    final_dist = superposition.get_probability_distribution()
    print(f"   Final distribution: {final_dist}")
    
    trajectory_summary = engine.get_trajectory_summary()
    print(f"\n   Trajectory Summary:")
    print(f"      States recorded: {trajectory_summary['states']}")
    print(f"      Average entropy: {trajectory_summary['avg_entropy']:.3f}")
    print(f"      Final alignment: {trajectory_summary['final_alignment']:.3f}")
    print(f"      Entropy trend: {trajectory_summary['entropy_trend']:.3f}")
    
    # Compute goal alignment
    alignment = engine.compute_goal_alignment(superposition, goal)
    print(f"\n   Goal alignment score: {alignment:.3f}")
    print(f"   (1.0 = perfect alignment, 0.0 = complete misalignment)")
    
    print("\n" + "=" * 60)
    print("Teleological back-propagation successfully pulled")
    print("intent toward goal state!")
    print("=" * 60)


if __name__ == "__main__":
    main()
