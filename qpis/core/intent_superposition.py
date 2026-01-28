"""
Intent Superposition Module

Maintains intents as quantum-like superpositions of possible outcomes,
each with associated probability amplitudes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import numpy as np
from scipy.special import softmax


@dataclass
class Intent:
    """
    Represents a single possible intent with its associated probability amplitude.
    
    Attributes:
        label: Human-readable intent identifier
        amplitude: Complex probability amplitude (quantum-inspired)
        features: Feature vector describing this intent
        teleological_weight: Weight representing goal-oriented pull
    """
    label: str
    amplitude: complex = 1.0 + 0j
    features: Optional[np.ndarray] = None
    teleological_weight: float = 1.0
    
    @property
    def probability(self) -> float:
        """Calculate probability from amplitude (Born rule)."""
        return abs(self.amplitude) ** 2
    
    def normalize_amplitude(self, total_amplitude: float):
        """Normalize amplitude relative to total."""
        if total_amplitude > 0:
            self.amplitude = self.amplitude / np.sqrt(total_amplitude)


class IntentSuperposition:
    """
    Manages a superposition of multiple possible intents.
    
    This class maintains a quantum-inspired superposition state where multiple
    intents exist simultaneously with probability amplitudes that determine
    likelihood of each intent being the "true" intent upon measurement.
    """
    
    def __init__(self, intents: Optional[List[Intent]] = None):
        """
        Initialize intent superposition.
        
        Args:
            intents: Initial list of Intent objects
        """
        self.intents: List[Intent] = intents or []
        self._collapsed: bool = False
        self._collapsed_intent: Optional[Intent] = None
        self._entropy_history: List[float] = []
    
    def add_intent(self, intent: Intent):
        """Add a new intent to the superposition."""
        if self._collapsed:
            raise RuntimeError("Cannot add intent to collapsed superposition")
        self.intents.append(intent)
        self.normalize()
    
    def normalize(self):
        """Normalize all intent amplitudes so probabilities sum to 1."""
        total_amplitude = sum(abs(intent.amplitude) ** 2 for intent in self.intents)
        for intent in self.intents:
            intent.normalize_amplitude(total_amplitude)
    
    def get_probability_distribution(self) -> Dict[str, float]:
        """
        Get probability distribution over all intents.
        
        Returns:
            Dictionary mapping intent labels to probabilities
        """
        return {intent.label: intent.probability for intent in self.intents}
    
    def apply_phase_shift(self, label: str, phase: float):
        """
        Apply a phase shift to a specific intent (quantum operation).
        
        Args:
            label: Intent label to modify
            phase: Phase shift in radians
        """
        if self._collapsed:
            raise RuntimeError("Cannot modify collapsed superposition")
        
        for intent in self.intents:
            if intent.label == label:
                magnitude = abs(intent.amplitude)
                current_phase = np.angle(intent.amplitude)
                new_phase = current_phase + phase
                intent.amplitude = magnitude * np.exp(1j * new_phase)
    
    def apply_amplitude_damping(self, label: str, damping_factor: float):
        """
        Apply amplitude damping to reduce probability of an intent.
        
        Args:
            label: Intent label to dampen
            damping_factor: Factor between 0 and 1 (0=full damping, 1=no damping)
        """
        if self._collapsed:
            raise RuntimeError("Cannot modify collapsed superposition")
        
        for intent in self.intents:
            if intent.label == label:
                intent.amplitude *= damping_factor
        self.normalize()
    
    def evolve_teleological(self, goal_state: Dict[str, float], time_step: float = 0.1):
        """
        Evolve the superposition based on teleological (goal-directed) forces.
        
        Args:
            goal_state: Target probability distribution for intents
            time_step: Evolution time step
        """
        if self._collapsed:
            return
        
        for intent in self.intents:
            if intent.label in goal_state:
                target_prob = goal_state[intent.label]
                current_prob = intent.probability
                
                # Pull amplitude toward goal
                adjustment = (target_prob - current_prob) * time_step * intent.teleological_weight
                magnitude = abs(intent.amplitude)
                new_magnitude = np.sqrt(max(0, current_prob + adjustment))
                
                if magnitude > 0:
                    phase = np.angle(intent.amplitude)
                    intent.amplitude = new_magnitude * np.exp(1j * phase)
        
        self.normalize()
    
    def calculate_entropy(self) -> float:
        """
        Calculate Shannon entropy of the probability distribution.
        
        Higher entropy means more uncertainty about intent.
        
        Returns:
            Entropy value in nats
        """
        probs = [intent.probability for intent in self.intents]
        probs = [p for p in probs if p > 1e-10]  # Remove near-zero probabilities
        
        if not probs:
            return 0.0
        
        entropy = -sum(p * np.log(p) for p in probs)
        self._entropy_history.append(entropy)
        return entropy
    
    def is_collapsed(self) -> bool:
        """Check if superposition has collapsed."""
        return self._collapsed
    
    def get_collapsed_intent(self) -> Optional[Intent]:
        """Get the collapsed intent if superposition has collapsed."""
        return self._collapsed_intent
    
    def collapse_to_intent(self, intent: Intent):
        """
        Collapse the superposition to a specific intent.
        
        Args:
            intent: The intent to collapse to
        """
        self._collapsed = True
        self._collapsed_intent = intent
    
    def get_dominant_intent(self) -> Optional[Intent]:
        """
        Get the intent with highest probability.
        
        Returns:
            Intent with maximum probability, or None if no intents exist
        """
        if not self.intents:
            return None
        return max(self.intents, key=lambda i: i.probability)
    
    def __repr__(self) -> str:
        """String representation of the superposition."""
        if self._collapsed:
            return f"IntentSuperposition(collapsed={self._collapsed_intent.label})"
        
        prob_dist = self.get_probability_distribution()
        return f"IntentSuperposition({len(self.intents)} intents, entropy={self.calculate_entropy():.3f})"
