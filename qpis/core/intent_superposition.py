"""
Intent Superposition

Maintains intent as a quantum-like superposition of all logically possible 
outcomes until a measurement event causes collapse into a specific execution path.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class IntentState:
    """Represents a single possible intent state in the superposition."""
    
    state_id: str
    description: str
    probability_amplitude: complex
    parameters: Dict[str, Any] = field(default_factory=dict)
    entangled_states: List[str] = field(default_factory=list)
    
    @property
    def probability(self) -> float:
        """Calculate probability from amplitude (Born rule)."""
        return abs(self.probability_amplitude) ** 2
    
    def normalize_amplitude(self, total_prob: float):
        """Normalize amplitude to ensure probability sum = 1."""
        current_prob = self.probability
        if current_prob > 0:
            scale_factor = np.sqrt(total_prob / current_prob)
            self.probability_amplitude *= scale_factor


class IntentSuperposition:
    """
    Quantum-Probabilistic Intent Superposition
    
    Maintains intent as a superposition of multiple possible states,
    each with a complex probability amplitude. Measurement events
    cause the superposition to collapse into a single execution path.
    
    This shifts engineering focus from tracking what a user IS doing 
    to calculating the probability of what they are BECOMING.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize an intent superposition for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
        """
        self.agent_id = agent_id
        self.states: Dict[str, IntentState] = {}
        self.collapsed_state: Optional[IntentState] = None
        self.measurement_history: List[Dict[str, Any]] = []
        self.coherence: float = 1.0  # Quantum coherence measure
        
        logger.info(f"Initialized IntentSuperposition for agent {agent_id}")
    
    def add_state(
        self, 
        state_id: str, 
        description: str, 
        amplitude: complex = 1.0+0j,
        parameters: Optional[Dict[str, Any]] = None
    ) -> IntentState:
        """
        Add a new possible intent state to the superposition.
        
        Args:
            state_id: Unique identifier for this state
            description: Human-readable description
            amplitude: Complex probability amplitude
            parameters: Additional state parameters
            
        Returns:
            The created IntentState
        """
        state = IntentState(
            state_id=state_id,
            description=description,
            probability_amplitude=amplitude,
            parameters=parameters or {}
        )
        self.states[state_id] = state
        self._normalize_amplitudes()
        
        logger.debug(f"Added state {state_id} with probability {state.probability:.4f}")
        return state
    
    def entangle_states(self, state_id1: str, state_id2: str):
        """
        Create quantum entanglement between two intent states.
        
        Entangled states influence each other's probabilities.
        """
        if state_id1 in self.states and state_id2 in self.states:
            self.states[state_id1].entangled_states.append(state_id2)
            self.states[state_id2].entangled_states.append(state_id1)
            logger.debug(f"Entangled states {state_id1} and {state_id2}")
    
    def evolve(self, time_delta: float, hamiltonian: Optional[np.ndarray] = None):
        """
        Evolve the intent superposition through time.
        
        Uses Schrödinger-like evolution to update probability amplitudes
        based on the system's Hamiltonian.
        
        Args:
            time_delta: Time step for evolution
            hamiltonian: Energy operator (if None, uses default)
        """
        if not self.states:
            return
        
        # Convert states to vector representation
        state_ids = list(self.states.keys())
        amplitudes = np.array([self.states[sid].probability_amplitude for sid in state_ids])
        
        # Default Hamiltonian (identity with small perturbations)
        if hamiltonian is None:
            n = len(state_ids)
            hamiltonian = np.eye(n) + 0.1 * np.random.randn(n, n)
            hamiltonian = (hamiltonian + hamiltonian.T) / 2  # Make Hermitian
        
        # Evolve: |ψ(t+dt)⟩ = exp(-iHdt)|ψ(t)⟩
        evolution_operator = np.exp(-1j * hamiltonian * time_delta)
        new_amplitudes = evolution_operator @ amplitudes
        
        # Update state amplitudes
        for i, state_id in enumerate(state_ids):
            self.states[state_id].probability_amplitude = new_amplitudes[i]
        
        # Decoherence: reduce coherence over time
        self.coherence *= np.exp(-0.01 * time_delta)
        
        logger.debug(f"Evolved superposition, coherence: {self.coherence:.4f}")
    
    def measure(
        self, 
        measurement_operator: Optional[Callable] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentState:
        """
        Perform a measurement, collapsing the superposition.
        
        This is the key operation where quantum-like intent superposition
        collapses into a single execution path based on probability density.
        
        Args:
            measurement_operator: Custom measurement logic
            context: Additional context for measurement
            
        Returns:
            The collapsed IntentState
        """
        if self.collapsed_state:
            logger.warning("Superposition already collapsed")
            return self.collapsed_state
        
        if not self.states:
            raise ValueError("No states in superposition to measure")
        
        # Apply measurement operator if provided
        if measurement_operator:
            measurement_operator(self, context or {})
        
        # Calculate probabilities
        state_ids = list(self.states.keys())
        probabilities = np.array([self.states[sid].probability for sid in state_ids])
        
        # Normalize probabilities
        probabilities = probabilities / np.sum(probabilities)
        
        # Collapse according to probability distribution
        chosen_idx = np.random.choice(len(state_ids), p=probabilities)
        chosen_state_id = state_ids[chosen_idx]
        self.collapsed_state = self.states[chosen_state_id]
        
        # Record measurement
        self.measurement_history.append({
            "timestamp": np.datetime64("now"),
            "collapsed_to": chosen_state_id,
            "probability": probabilities[chosen_idx],
            "context": context or {}
        })
        
        logger.info(
            f"Measurement collapsed to state '{chosen_state_id}' "
            f"with probability {probabilities[chosen_idx]:.4f}"
        )
        
        return self.collapsed_state
    
    def get_state_probabilities(self) -> Dict[str, float]:
        """Get current probability distribution over all states."""
        return {
            state_id: state.probability 
            for state_id, state in self.states.items()
        }
    
    def get_dominant_state(self) -> Optional[IntentState]:
        """Get the state with highest probability (without collapsing)."""
        if not self.states:
            return None
        return max(self.states.values(), key=lambda s: s.probability)
    
    def reset(self):
        """Reset the superposition for a new measurement cycle."""
        self.collapsed_state = None
        self.coherence = 1.0
        logger.debug(f"Reset superposition for agent {self.agent_id}")
    
    def _normalize_amplitudes(self):
        """Ensure all probability amplitudes sum to probability 1."""
        if not self.states:
            return
        
        total_prob = sum(state.probability for state in self.states.values())
        
        if total_prob > 0:
            for state in self.states.values():
                state.normalize_amplitude(total_prob)
    
    def __repr__(self) -> str:
        state_count = len(self.states)
        collapsed = "collapsed" if self.collapsed_state else "superposed"
        return f"IntentSuperposition(agent={self.agent_id}, states={state_count}, {collapsed})"
