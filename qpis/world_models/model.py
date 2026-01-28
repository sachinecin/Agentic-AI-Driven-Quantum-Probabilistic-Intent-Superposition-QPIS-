"""
World Model

Predictive world model for simulating agent behavior and environmental
dynamics in the teleological loop.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorldState:
    """Represents a state in the world model."""
    
    state_id: str
    features: np.ndarray
    timestamp: float
    agents: Dict[str, Any]
    environment: Dict[str, Any]


class WorldModel:
    """
    Predictive World Model
    
    Maintains a learned model of:
    - Agent behaviors and interactions
    - Environmental dynamics
    - Causal relationships
    - Probabilistic transitions
    
    Used for:
    - Predicting future states
    - Planning action sequences
    - Simulating counterfactuals
    - Intent inference
    """
    
    def __init__(
        self,
        state_dim: int = 64,
        action_dim: int = 32
    ):
        """
        Initialize world model.
        
        Args:
            state_dim: Dimensionality of state representation
            action_dim: Dimensionality of action space
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Model parameters (simplified)
        self.transition_matrix = np.eye(state_dim)
        self.state_history: List[WorldState] = []
        
        # Learned dynamics
        self.dynamics = self._initialize_dynamics()
        
        logger.info(f"Initialized WorldModel (state_dim={state_dim}, action_dim={action_dim})")
    
    def predict_next_state(
        self,
        current_state: WorldState,
        action: np.ndarray,
        agent_intents: Optional[Dict[str, Any]] = None
    ) -> WorldState:
        """
        Predict next world state given current state and action.
        
        Args:
            current_state: Current world state
            action: Action to take
            agent_intents: Optional agent intent information
            
        Returns:
            Predicted next state
        """
        # Ensure action is right size
        if len(action) < self.action_dim:
            action_padded = np.zeros(self.action_dim)
            action_padded[:len(action)] = action
            action = action_padded
        else:
            action = action[:self.action_dim]
        
        # Simple transition model: s' = T*s + A*a + noise
        state_vec = current_state.features
        
        # State transition
        next_state_vec = (
            self.transition_matrix @ state_vec +
            0.1 * action +
            np.random.randn(self.state_dim) * 0.01
        )
        
        # Incorporate agent intents if provided
        if agent_intents:
            intent_influence = self._compute_intent_influence(agent_intents)
            next_state_vec += 0.05 * intent_influence
        
        # Create next state
        next_state = WorldState(
            state_id=f"state_{len(self.state_history)}",
            features=next_state_vec,
            timestamp=current_state.timestamp + 1.0,
            agents=current_state.agents.copy(),
            environment=current_state.environment.copy()
        )
        
        self.state_history.append(next_state)
        
        logger.debug(f"Predicted next state: {next_state.state_id}")
        
        return next_state
    
    def simulate_trajectory(
        self,
        initial_state: WorldState,
        actions: List[np.ndarray],
        agent_intents: Optional[Dict[str, Any]] = None
    ) -> List[WorldState]:
        """
        Simulate a trajectory of states given a sequence of actions.
        
        Args:
            initial_state: Starting state
            actions: Sequence of actions
            agent_intents: Agent intents for each step
            
        Returns:
            List of predicted states
        """
        trajectory = [initial_state]
        current = initial_state
        
        for i, action in enumerate(actions):
            next_state = self.predict_next_state(current, action, agent_intents)
            trajectory.append(next_state)
            current = next_state
        
        logger.info(f"Simulated trajectory of {len(actions)} steps")
        
        return trajectory
    
    def evaluate_goal_likelihood(
        self,
        current_state: WorldState,
        goal_state: WorldState,
        horizon: int = 10
    ) -> float:
        """
        Evaluate likelihood of reaching a goal state from current state.
        
        Args:
            current_state: Current world state
            goal_state: Target goal state
            horizon: Planning horizon
            
        Returns:
            Likelihood score (0-1)
        """
        # Distance in state space
        distance = np.linalg.norm(
            current_state.features - goal_state.features
        )
        
        # Normalize by dimensionality
        max_distance = np.sqrt(self.state_dim)
        normalized_distance = distance / max_distance
        
        # Likelihood decreases with distance and horizon
        likelihood = np.exp(-normalized_distance) * np.exp(-horizon * 0.05)
        
        return float(likelihood)
    
    def plan_actions(
        self,
        current_state: WorldState,
        goal_state: WorldState,
        n_steps: int = 10
    ) -> List[np.ndarray]:
        """
        Plan a sequence of actions to reach a goal state.
        
        Uses simple gradient-based planning.
        
        Args:
            current_state: Starting state
            goal_state: Target state
            n_steps: Number of action steps
            
        Returns:
            List of planned actions
        """
        actions = []
        state = current_state
        
        for _ in range(n_steps):
            # Compute gradient toward goal
            gradient = goal_state.features - state.features
            
            # Convert to action (simplified)
            action = gradient[:self.action_dim] / (np.linalg.norm(gradient) + 1e-8)
            action = action * 0.1  # Scale down
            
            actions.append(action)
            
            # Simulate next state
            state = self.predict_next_state(state, action)
        
        logger.debug(f"Planned {n_steps} actions toward goal")
        
        return actions
    
    def update_from_observation(
        self,
        predicted_state: WorldState,
        observed_state: WorldState,
        learning_rate: float = 0.01
    ):
        """
        Update world model based on prediction error.
        
        Args:
            predicted_state: What was predicted
            observed_state: What was observed
            learning_rate: Update rate
        """
        # Compute prediction error
        error = observed_state.features - predicted_state.features
        
        # Update transition matrix
        if len(self.state_history) > 0:
            prev_state = self.state_history[-1]
            
            # Gradient update
            gradient = np.outer(error, prev_state.features)
            self.transition_matrix += learning_rate * gradient
        
        logger.debug(f"Updated model from observation, error: {np.linalg.norm(error):.4f}")
    
    def get_state_distribution(
        self,
        current_state: WorldState,
        n_samples: int = 100
    ) -> List[WorldState]:
        """
        Sample possible next states from the learned distribution.
        
        Args:
            current_state: Current state
            n_samples: Number of samples
            
        Returns:
            List of sampled next states
        """
        samples = []
        
        for i in range(n_samples):
            # Random action
            action = np.random.randn(self.action_dim) * 0.1
            
            # Predict with noise
            next_state = self.predict_next_state(current_state, action)
            samples.append(next_state)
        
        return samples
    
    def _compute_intent_influence(
        self,
        agent_intents: Dict[str, Any]
    ) -> np.ndarray:
        """Compute how agent intents influence world state."""
        influence = np.zeros(self.state_dim)
        
        for agent_id, intent_data in agent_intents.items():
            # Simple encoding: hash agent_id to state dimensions
            agent_hash = hash(agent_id) % self.state_dim
            influence[agent_hash] += 0.1
        
        return influence
    
    def _initialize_dynamics(self) -> Dict[str, Any]:
        """Initialize dynamics model parameters."""
        return {
            "transition_noise": 0.01,
            "observation_noise": 0.02,
            "temporal_discount": 0.95
        }
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get statistics about the world model."""
        return {
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "history_length": len(self.state_history),
            "transition_matrix_norm": float(np.linalg.norm(self.transition_matrix))
        }
    
    def reset(self):
        """Reset world model state."""
        self.state_history.clear()
        logger.debug("Reset world model")
