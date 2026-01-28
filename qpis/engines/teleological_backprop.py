"""
Recursive Teleological Back-Propagation Engine

This engine implements a recursive algorithm that propagates goal-oriented
(teleological) signals backward through time to influence present intent
superpositions.
"""

from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass, field
import numpy as np
from qpis.core.intent_superposition import IntentSuperposition, Intent


@dataclass
class TeleologicalState:
    """
    Represents a state in the teleological trajectory.
    
    Attributes:
        timestamp: Time point of this state
        superposition: Intent superposition at this state
        goal_alignment: How well this state aligns with end goal (0-1)
        entropy: Entropy at this state
        gradient: Teleological gradient for back-propagation
    """
    timestamp: float
    superposition: IntentSuperposition
    goal_alignment: float = 0.0
    entropy: float = 0.0
    gradient: Optional[np.ndarray] = None


@dataclass  
class TeleologicalGoal:
    """
    Represents a teleological goal (end state) to guide the system.
    
    Attributes:
        label: Goal identifier
        target_distribution: Desired probability distribution over intents
        importance: Importance weight of this goal (0-1)
        horizon: Time horizon for achieving goal
    """
    label: str
    target_distribution: Dict[str, float]
    importance: float = 1.0
    horizon: float = 1.0


class TeleologicalEngine:
    """
    Recursive Teleological Back-Propagation Engine.
    
    This engine uses recursive back-propagation from future goal states to
    present states, creating a "pull" effect that guides intent evolution
    toward desired outcomes.
    """
    
    def __init__(self, learning_rate: float = 0.1, decay_rate: float = 0.95):
        """
        Initialize the teleological engine.
        
        Args:
            learning_rate: Rate at which teleological forces affect state
            decay_rate: Exponential decay of influence over time
        """
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        self.trajectory: List[TeleologicalState] = []
        self.goals: List[TeleologicalGoal] = []
    
    def add_goal(self, goal: TeleologicalGoal):
        """Add a teleological goal to guide the system."""
        self.goals.append(goal)
    
    def record_state(self, timestamp: float, superposition: IntentSuperposition):
        """
        Record a state in the trajectory for later back-propagation.
        
        Args:
            timestamp: Time point of the state
            superposition: Intent superposition at this state
        """
        state = TeleologicalState(
            timestamp=timestamp,
            superposition=superposition,
            entropy=superposition.calculate_entropy()
        )
        self.trajectory.append(state)
    
    def compute_goal_alignment(
        self,
        superposition: IntentSuperposition,
        goal: TeleologicalGoal
    ) -> float:
        """
        Compute how well a superposition aligns with a goal.
        
        Args:
            superposition: Current intent superposition
            goal: Target goal
            
        Returns:
            Alignment score between 0 and 1
        """
        current_dist = superposition.get_probability_distribution()
        
        # Compute KL divergence (lower is better)
        kl_divergence = 0.0
        for label, target_prob in goal.target_distribution.items():
            current_prob = current_dist.get(label, 1e-10)
            if target_prob > 0:
                kl_divergence += target_prob * np.log(target_prob / current_prob)
        
        # Convert to alignment score (higher is better)
        alignment = np.exp(-kl_divergence)
        return alignment
    
    def recursive_backprop(
        self,
        depth: int = 0,
        max_depth: int = 10
    ) -> Dict[str, np.ndarray]:
        """
        Recursively back-propagate teleological gradients.
        
        This is the core recursive algorithm that propagates goal information
        backward through the trajectory.
        
        Args:
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            
        Returns:
            Dictionary of gradients for each intent label
        """
        if depth >= max_depth or not self.trajectory:
            return {}
        
        gradients = {}
        
        # Base case: compute gradients for most recent state
        if depth == 0:
            latest_state = self.trajectory[-1]
            
            for goal in self.goals:
                alignment = self.compute_goal_alignment(
                    latest_state.superposition, 
                    goal
                )
                latest_state.goal_alignment = alignment
                
                # Compute gradient toward goal
                current_dist = latest_state.superposition.get_probability_distribution()
                
                for label, target_prob in goal.target_distribution.items():
                    current_prob = current_dist.get(label, 0.0)
                    gradient = (target_prob - current_prob) * goal.importance
                    
                    if label not in gradients:
                        gradients[label] = np.array([gradient])
                    else:
                        gradients[label] = np.append(gradients[label], gradient)
        
        # Recursive case: back-propagate to earlier states
        if len(self.trajectory) > 1:
            # Get gradients from deeper recursion
            future_gradients = self.recursive_backprop(depth + 1, max_depth)
            
            # Propagate gradients backward with decay
            state_idx = len(self.trajectory) - depth - 1
            if state_idx >= 0:
                state = self.trajectory[state_idx]
                
                for label, future_grad in future_gradients.items():
                    # Apply temporal decay
                    decayed_grad = future_grad * self.decay_rate
                    
                    if label not in gradients:
                        gradients[label] = decayed_grad
                    else:
                        gradients[label] = np.concatenate([gradients[label], decayed_grad])
        
        return gradients
    
    def apply_teleological_update(
        self,
        superposition: IntentSuperposition,
        gradients: Dict[str, np.ndarray]
    ):
        """
        Apply computed teleological gradients to update superposition.
        
        Args:
            superposition: Intent superposition to update
            gradients: Computed gradients from back-propagation
        """
        for intent in superposition.intents:
            if intent.label in gradients:
                # Average the gradients
                gradient = np.mean(gradients[intent.label])
                
                # Update probability amplitude
                current_prob = intent.probability
                adjustment = gradient * self.learning_rate * intent.teleological_weight
                new_prob = np.clip(current_prob + adjustment, 0.0, 1.0)
                
                # Update amplitude (maintain phase)
                if abs(intent.amplitude) > 0:
                    phase = np.angle(intent.amplitude)
                    intent.amplitude = np.sqrt(new_prob) * np.exp(1j * phase)
                else:
                    intent.amplitude = np.sqrt(new_prob)
        
        superposition.normalize()
    
    def execute_teleological_cycle(
        self,
        current_superposition: IntentSuperposition,
        timestamp: float
    ) -> IntentSuperposition:
        """
        Execute one full cycle of teleological back-propagation.
        
        This is the main method to call for updating a superposition based on
        teleological goals.
        
        Args:
            current_superposition: Current intent superposition
            timestamp: Current time point
            
        Returns:
            Updated intent superposition
        """
        # Record current state
        self.record_state(timestamp, current_superposition)
        
        # Perform recursive back-propagation
        gradients = self.recursive_backprop(max_depth=min(10, len(self.trajectory)))
        
        # Apply teleological updates
        self.apply_teleological_update(current_superposition, gradients)
        
        return current_superposition
    
    def reset_trajectory(self):
        """Clear the trajectory history."""
        self.trajectory = []
    
    def get_trajectory_summary(self) -> Dict:
        """
        Get summary statistics of the trajectory.
        
        Returns:
            Dictionary with trajectory statistics
        """
        if not self.trajectory:
            return {"states": 0}
        
        return {
            "states": len(self.trajectory),
            "avg_entropy": np.mean([s.entropy for s in self.trajectory]),
            "final_alignment": self.trajectory[-1].goal_alignment if self.trajectory else 0.0,
            "entropy_trend": self.trajectory[-1].entropy - self.trajectory[0].entropy if len(self.trajectory) > 1 else 0.0
        }
