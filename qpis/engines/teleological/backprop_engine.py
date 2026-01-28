"""
Teleological Back-Propagation Engine

Implements recursive back-propagation from future desired states to current
intent configurations, enabling agents to shape present behavior based on 
teleological goals.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TeleologicalGradient:
    """Represents gradient information for back-propagation."""
    
    state_id: str
    gradient: np.ndarray
    timestamp: float
    goal_contribution: float


class TeleologicalBackPropEngine:
    """
    Recursive Teleological Back-Propagation Engine
    
    Propagates desired future states backward through time to influence
    current intent superpositions. This implements the teleological loop
    where future goals shape present behavior.
    
    The engine uses gradient-based optimization to adjust probability
    amplitudes of intent states based on their contribution to achieving
    teleological goals.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        decay_factor: float = 0.95,
        max_iterations: int = 100
    ):
        """
        Initialize the back-propagation engine.
        
        Args:
            learning_rate: Step size for gradient updates
            decay_factor: Temporal decay for gradients
            max_iterations: Maximum recursive depth
        """
        self.learning_rate = learning_rate
        self.decay_factor = decay_factor
        self.max_iterations = max_iterations
        self.gradient_history: List[TeleologicalGradient] = []
        
        logger.info("Initialized TeleologicalBackPropEngine")
    
    def compute_teleological_gradient(
        self,
        current_state: Dict[str, Any],
        target_state: Dict[str, Any],
        time_horizon: float
    ) -> np.ndarray:
        """
        Compute gradient from target state back to current state.
        
        Args:
            current_state: Current system state
            target_state: Desired future state
            time_horizon: Time distance to target
            
        Returns:
            Gradient array indicating direction of optimization
        """
        # Convert states to numerical vectors
        current_vector = self._state_to_vector(current_state)
        target_vector = self._state_to_vector(target_state)
        
        # Compute difference vector (error)
        error = target_vector - current_vector
        
        # Apply temporal decay based on time horizon
        temporal_weight = np.exp(-time_horizon / self.decay_factor)
        
        # Gradient is weighted error direction
        gradient = temporal_weight * error
        
        logger.debug(f"Computed gradient with magnitude {np.linalg.norm(gradient):.4f}")
        
        return gradient
    
    def back_propagate(
        self,
        intent_superposition: Any,  # IntentSuperposition
        target_goal: Dict[str, Any],
        time_horizon: float = 1.0,
        recursive_depth: int = 0
    ) -> Dict[str, float]:
        """
        Recursively back-propagate goal influence to intent states.
        
        This is the core recursive algorithm that propagates teleological
        influence backward through the intent state space.
        
        Args:
            intent_superposition: The IntentSuperposition to optimize
            target_goal: Target goal to achieve
            time_horizon: Time to goal achievement
            recursive_depth: Current recursion depth
            
        Returns:
            Dictionary of state adjustments (state_id -> amplitude adjustment)
        """
        if recursive_depth >= self.max_iterations:
            logger.warning(f"Max recursion depth reached: {self.max_iterations}")
            return {}
        
        adjustments = {}
        
        # Get current state distribution
        state_probs = intent_superposition.get_state_probabilities()
        
        if not state_probs:
            return adjustments
        
        # Evaluate each state's contribution to goal
        for state_id, current_prob in state_probs.items():
            state = intent_superposition.states[state_id]
            
            # Compute how well this state aligns with goal
            alignment_score = self._evaluate_goal_alignment(
                state.parameters, 
                target_goal
            )
            
            # Compute gradient contribution
            gradient_contribution = alignment_score - current_prob
            
            # Apply learning rate and temporal decay
            adjustment = (
                self.learning_rate * 
                gradient_contribution * 
                np.exp(-recursive_depth * 0.1)
            )
            
            adjustments[state_id] = adjustment
            
            # Record gradient
            gradient = TeleologicalGradient(
                state_id=state_id,
                gradient=np.array([adjustment]),
                timestamp=time_horizon - recursive_depth * 0.1,
                goal_contribution=alignment_score
            )
            self.gradient_history.append(gradient)
        
        # Recursive call: propagate to next temporal layer
        if recursive_depth < self.max_iterations - 1:
            # Simulate time step forward
            intent_superposition.evolve(0.1)
            
            # Recursive back-propagation
            deeper_adjustments = self.back_propagate(
                intent_superposition,
                target_goal,
                time_horizon + 0.1,
                recursive_depth + 1
            )
            
            # Combine adjustments
            for state_id, adj in deeper_adjustments.items():
                if state_id in adjustments:
                    adjustments[state_id] += adj * self.decay_factor
                else:
                    adjustments[state_id] = adj * self.decay_factor
        
        logger.debug(
            f"Back-propagation depth {recursive_depth}: "
            f"{len(adjustments)} states adjusted"
        )
        
        return adjustments
    
    def apply_gradients(
        self,
        intent_superposition: Any,  # IntentSuperposition
        adjustments: Dict[str, float]
    ):
        """
        Apply computed gradient adjustments to intent state amplitudes.
        
        Args:
            intent_superposition: Target superposition to update
            adjustments: State amplitude adjustments from back-propagation
        """
        for state_id, adjustment in adjustments.items():
            if state_id in intent_superposition.states:
                state = intent_superposition.states[state_id]
                
                # Adjust probability amplitude
                current_amp = state.probability_amplitude
                phase = np.angle(current_amp)
                magnitude = abs(current_amp)
                
                # Update magnitude based on adjustment
                new_magnitude = max(0.01, magnitude + adjustment)
                
                # Reconstruct complex amplitude
                state.probability_amplitude = new_magnitude * np.exp(1j * phase)
        
        # Re-normalize
        intent_superposition._normalize_amplitudes()
        
        logger.info(f"Applied {len(adjustments)} gradient adjustments")
    
    def optimize_for_goal(
        self,
        intent_superposition: Any,  # IntentSuperposition
        target_goal: Dict[str, Any],
        iterations: int = 10
    ):
        """
        Optimize intent superposition for a teleological goal.
        
        Runs multiple back-propagation iterations to shape the
        intent probability distribution toward goal achievement.
        
        Args:
            intent_superposition: Superposition to optimize
            target_goal: Target goal to achieve
            iterations: Number of optimization iterations
        """
        logger.info(f"Starting teleological optimization for {iterations} iterations")
        
        for i in range(iterations):
            # Compute gradients via back-propagation
            adjustments = self.back_propagate(
                intent_superposition,
                target_goal,
                time_horizon=1.0
            )
            
            # Apply gradients
            self.apply_gradients(intent_superposition, adjustments)
            
            # Evaluate convergence
            convergence = np.mean([abs(adj) for adj in adjustments.values()])
            logger.debug(f"Iteration {i+1}: convergence = {convergence:.6f}")
            
            if convergence < 0.001:
                logger.info(f"Converged at iteration {i+1}")
                break
        
        logger.info("Teleological optimization complete")
    
    def _evaluate_goal_alignment(
        self,
        state_params: Dict[str, Any],
        target_goal: Dict[str, Any]
    ) -> float:
        """
        Evaluate how well a state aligns with a goal.
        
        Returns:
            Alignment score between 0 and 1
        """
        # Simple cosine similarity for numerical parameters
        state_vec = self._state_to_vector(state_params)
        goal_vec = self._state_to_vector(target_goal)
        
        # Avoid division by zero
        state_norm = np.linalg.norm(state_vec)
        goal_norm = np.linalg.norm(goal_vec)
        
        if state_norm == 0 or goal_norm == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(state_vec, goal_vec) / (state_norm * goal_norm)
        
        # Map to [0, 1]
        alignment = (similarity + 1) / 2
        
        return float(alignment)
    
    def _state_to_vector(self, state: Dict[str, Any]) -> np.ndarray:
        """Convert state dictionary to numerical vector."""
        # Extract numerical values
        values = []
        for key in sorted(state.keys()):
            val = state[key]
            if isinstance(val, (int, float)):
                values.append(float(val))
            elif isinstance(val, bool):
                values.append(float(val))
            elif isinstance(val, str):
                # Hash string to number
                values.append(float(hash(val) % 1000) / 1000)
        
        if not values:
            values = [0.0]
        
        return np.array(values)
    
    def get_gradient_statistics(self) -> Dict[str, Any]:
        """Get statistics about gradient history."""
        if not self.gradient_history:
            return {"count": 0}
        
        gradients = [g.gradient[0] for g in self.gradient_history]
        
        return {
            "count": len(self.gradient_history),
            "mean_magnitude": float(np.mean(np.abs(gradients))),
            "max_magnitude": float(np.max(np.abs(gradients))),
            "std_magnitude": float(np.std(np.abs(gradients)))
        }
    
    def reset(self):
        """Reset gradient history."""
        self.gradient_history.clear()
        logger.debug("Reset gradient history")
