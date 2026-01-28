"""
World Model Module

Implements a world model that predicts future states and outcomes based on
current intents and actions.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class WorldState:
    """
    Represents a state in the world model.
    
    Attributes:
        state_vector: Vector representation of world state
        timestamp: Time of this state
        metadata: Additional state information
    """
    state_vector: np.ndarray
    timestamp: float
    metadata: Optional[Dict] = None


@dataclass
class Transition:
    """
    Represents a state transition in the world model.
    
    Attributes:
        from_state: Initial state
        action: Action taken
        to_state: Resulting state
        reward: Reward received
        probability: Probability of this transition
    """
    from_state: WorldState
    action: str
    to_state: WorldState
    reward: float
    probability: float = 1.0


class WorldModel:
    """
    World Model for predicting state transitions and outcomes.
    
    The world model learns dynamics of the environment and can be used to
    simulate future trajectories given intents and actions.
    """
    
    def __init__(self, state_dim: int = 128):
        """
        Initialize world model.
        
        Args:
            state_dim: Dimensionality of state vectors
        """
        self.state_dim = state_dim
        self.current_state: Optional[WorldState] = None
        self.transition_history: List[Transition] = []
        self.transition_model: Dict[Tuple[str, str], List[Transition]] = {}
    
    def encode_state(self, observation: Dict) -> np.ndarray:
        """
        Encode an observation into a state vector.
        
        Args:
            observation: Observation dictionary
            
        Returns:
            State vector
        """
        state_vector = np.zeros(self.state_dim)
        
        # Simple encoding (in practice, would use learned encoder)
        for i, (key, value) in enumerate(observation.items()):
            idx = (hash(key) + i) % self.state_dim
            if isinstance(value, (int, float)):
                state_vector[idx] = float(value)
            elif isinstance(value, str):
                state_vector[idx] = hash(value) % 100 / 100.0
        
        # Normalize
        norm = np.linalg.norm(state_vector)
        if norm > 0:
            state_vector = state_vector / norm
        
        return state_vector
    
    def update_state(self, observation: Dict, timestamp: float):
        """
        Update current world state from observation.
        
        Args:
            observation: Current observation
            timestamp: Current time
        """
        state_vector = self.encode_state(observation)
        self.current_state = WorldState(
            state_vector=state_vector,
            timestamp=timestamp,
            metadata=observation
        )
    
    def record_transition(
        self,
        from_state: WorldState,
        action: str,
        to_state: WorldState,
        reward: float
    ):
        """
        Record a state transition for learning.
        
        Args:
            from_state: Initial state
            action: Action taken
            to_state: Resulting state
            reward: Reward received
        """
        transition = Transition(
            from_state=from_state,
            action=action,
            to_state=to_state,
            reward=reward
        )
        
        self.transition_history.append(transition)
        
        # Update transition model
        # Discretize states for lookup (simple binning)
        from_key = self._discretize_state(from_state.state_vector)
        
        key = (from_key, action)
        if key not in self.transition_model:
            self.transition_model[key] = []
        self.transition_model[key].append(transition)
    
    def _discretize_state(self, state_vector: np.ndarray, bins: int = 10) -> str:
        """
        Discretize continuous state vector for model lookup.
        
        Args:
            state_vector: Continuous state vector
            bins: Number of bins per dimension
            
        Returns:
            String key for state
        """
        # Use first few dimensions for discretization
        dims_to_use = min(5, len(state_vector))
        discrete = np.digitize(state_vector[:dims_to_use], 
                              bins=np.linspace(-1, 1, bins))
        return str(discrete.tolist())
    
    def predict_next_state(
        self,
        current_state: WorldState,
        action: str
    ) -> Tuple[WorldState, float]:
        """
        Predict next state given current state and action.
        
        Args:
            current_state: Current state
            action: Action to take
            
        Returns:
            Tuple of (predicted_state, confidence)
        """
        state_key = self._discretize_state(current_state.state_vector)
        lookup_key = (state_key, action)
        
        # Look up similar transitions
        if lookup_key in self.transition_model:
            transitions = self.transition_model[lookup_key]
            
            # Average the outcomes (simple approach)
            avg_state = np.mean([t.to_state.state_vector for t in transitions], axis=0)
            confidence = min(1.0, len(transitions) / 10)  # More examples = more confidence
            
            predicted_state = WorldState(
                state_vector=avg_state,
                timestamp=current_state.timestamp + 1.0,
                metadata={"prediction": True, "action": action}
            )
            
            return predicted_state, confidence
        
        # No similar transitions found - predict minimal change
        predicted_state = WorldState(
            state_vector=current_state.state_vector.copy(),
            timestamp=current_state.timestamp + 1.0,
            metadata={"prediction": True, "action": action, "novel": True}
        )
        
        return predicted_state, 0.1  # Low confidence
    
    def simulate_trajectory(
        self,
        initial_state: WorldState,
        action_sequence: List[str],
        max_steps: int = 10
    ) -> List[WorldState]:
        """
        Simulate a trajectory through the world model.
        
        Args:
            initial_state: Starting state
            action_sequence: Sequence of actions to simulate
            max_steps: Maximum simulation steps
            
        Returns:
            List of predicted states
        """
        trajectory = [initial_state]
        current = initial_state
        
        for i, action in enumerate(action_sequence[:max_steps]):
            next_state, _ = self.predict_next_state(current, action)
            trajectory.append(next_state)
            current = next_state
        
        return trajectory
    
    def evaluate_trajectory(
        self,
        trajectory: List[WorldState],
        goal_state: Optional[WorldState] = None
    ) -> float:
        """
        Evaluate quality of a trajectory.
        
        Args:
            trajectory: List of states
            goal_state: Optional goal state to compare against
            
        Returns:
            Quality score (higher is better)
        """
        if not trajectory:
            return 0.0
        
        # If goal state provided, evaluate proximity to goal
        if goal_state is not None:
            final_state = trajectory[-1]
            distance = np.linalg.norm(
                final_state.state_vector - goal_state.state_vector
            )
            # Convert distance to quality (closer = better)
            quality = np.exp(-distance)
            return quality
        
        # Otherwise, evaluate based on accumulated rewards from history
        quality = 0.0
        for i, state in enumerate(trajectory[:-1]):
            # Look for matching transitions in history
            state_key = self._discretize_state(state.state_vector)
            
            for transitions in self.transition_model.values():
                for trans in transitions:
                    if self._discretize_state(trans.from_state.state_vector) == state_key:
                        quality += trans.reward * (0.9 ** i)  # Discount factor
        
        return quality / max(1, len(trajectory))
    
    def get_model_summary(self) -> Dict:
        """
        Get summary of world model state.
        
        Returns:
            Dictionary with model statistics
        """
        return {
            "transitions_recorded": len(self.transition_history),
            "unique_state_action_pairs": len(self.transition_model),
            "has_current_state": self.current_state is not None,
            "avg_transitions_per_state": (
                len(self.transition_history) / max(1, len(self.transition_model))
            )
        }
