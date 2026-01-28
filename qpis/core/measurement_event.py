"""
Measurement Event Module

Handles the collapse of intent superpositions based on measurement events
and probability densities.
"""

from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
from enum import Enum
import numpy as np

from qpis.core.intent_superposition import IntentSuperposition, Intent


class CollapseStrategy(Enum):
    """Strategies for collapsing intent superpositions."""
    MAXIMUM_PROBABILITY = "max_prob"
    STOCHASTIC_SAMPLING = "stochastic"
    THRESHOLD_BASED = "threshold"
    ENTROPY_DRIVEN = "entropy"


@dataclass
class MeasurementEvent:
    """
    Represents a measurement event that can trigger superposition collapse.
    
    Attributes:
        event_type: Type of measurement (e.g., 'click', 'gaze', 'hrv_spike')
        confidence: Confidence level of the measurement (0-1)
        features: Feature vector associated with the measurement
        metadata: Additional metadata about the measurement
    """
    event_type: str
    confidence: float = 1.0
    features: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


class MeasurementCollapse:
    """
    Handles the collapse of intent superpositions into definite execution states.
    
    The collapse process is triggered by measurement events and uses probability
    density calculations to determine which intent becomes "real".
    """
    
    def __init__(self, strategy: CollapseStrategy = CollapseStrategy.MAXIMUM_PROBABILITY):
        """
        Initialize measurement collapse handler.
        
        Args:
            strategy: Strategy to use for collapsing superpositions
        """
        self.strategy = strategy
        self.collapse_history = []
    
    def should_collapse(
        self, 
        superposition: IntentSuperposition,
        measurement: MeasurementEvent,
        threshold: float = 0.7
    ) -> bool:
        """
        Determine if a measurement should trigger collapse.
        
        Args:
            superposition: The intent superposition to evaluate
            measurement: The measurement event
            threshold: Threshold for collapse decision
            
        Returns:
            True if superposition should collapse
        """
        if superposition.is_collapsed():
            return False
        
        # Check if dominant intent has high enough probability
        dominant = superposition.get_dominant_intent()
        if dominant and dominant.probability >= threshold:
            return True
        
        # Check entropy - low entropy suggests convergence
        entropy = superposition.calculate_entropy()
        max_entropy = np.log(len(superposition.intents)) if superposition.intents else 0
        
        if max_entropy > 0 and entropy / max_entropy < (1 - threshold):
            return True
        
        # High confidence measurements can trigger collapse
        if measurement.confidence >= threshold:
            return True
        
        return False
    
    def collapse(
        self,
        superposition: IntentSuperposition,
        measurement: MeasurementEvent,
        force: bool = False
    ) -> Optional[Intent]:
        """
        Collapse the superposition into a single intent.
        
        Args:
            superposition: The intent superposition to collapse
            measurement: The triggering measurement event
            force: Force collapse even if conditions not met
            
        Returns:
            The collapsed intent, or None if collapse didn't occur
        """
        if superposition.is_collapsed():
            return superposition.get_collapsed_intent()
        
        if not force and not self.should_collapse(superposition, measurement):
            return None
        
        # Select intent based on strategy
        if self.strategy == CollapseStrategy.MAXIMUM_PROBABILITY:
            collapsed_intent = self._collapse_max_probability(superposition)
        elif self.strategy == CollapseStrategy.STOCHASTIC_SAMPLING:
            collapsed_intent = self._collapse_stochastic(superposition)
        elif self.strategy == CollapseStrategy.THRESHOLD_BASED:
            collapsed_intent = self._collapse_threshold(superposition, measurement)
        elif self.strategy == CollapseStrategy.ENTROPY_DRIVEN:
            collapsed_intent = self._collapse_entropy_driven(superposition)
        else:
            collapsed_intent = self._collapse_max_probability(superposition)
        
        if collapsed_intent:
            superposition.collapse_to_intent(collapsed_intent)
            self.collapse_history.append({
                'intent': collapsed_intent.label,
                'probability': collapsed_intent.probability,
                'measurement': measurement.event_type,
                'confidence': measurement.confidence
            })
        
        return collapsed_intent
    
    def _collapse_max_probability(self, superposition: IntentSuperposition) -> Optional[Intent]:
        """Collapse to intent with maximum probability."""
        return superposition.get_dominant_intent()
    
    def _collapse_stochastic(self, superposition: IntentSuperposition) -> Optional[Intent]:
        """
        Collapse using stochastic sampling weighted by probabilities.
        
        This mimics quantum measurement where outcomes are probabilistic.
        """
        if not superposition.intents:
            return None
        
        probabilities = [intent.probability for intent in superposition.intents]
        # Normalize in case of numerical errors
        probabilities = np.array(probabilities)
        probabilities /= probabilities.sum()
        
        chosen_idx = np.random.choice(len(superposition.intents), p=probabilities)
        return superposition.intents[chosen_idx]
    
    def _collapse_threshold(
        self, 
        superposition: IntentSuperposition,
        measurement: MeasurementEvent
    ) -> Optional[Intent]:
        """
        Collapse to first intent exceeding probability threshold,
        weighted by measurement confidence.
        """
        threshold = 0.5 * measurement.confidence
        
        for intent in sorted(superposition.intents, key=lambda i: i.probability, reverse=True):
            if intent.probability >= threshold:
                return intent
        
        return superposition.get_dominant_intent()
    
    def _collapse_entropy_driven(self, superposition: IntentSuperposition) -> Optional[Intent]:
        """
        Collapse based on entropy considerations.
        
        Weights intents by both probability and their contribution to entropy reduction.
        """
        if not superposition.intents:
            return None
        
        # Calculate entropy contribution of each intent
        scores = []
        for intent in superposition.intents:
            # Higher probability and lower local entropy = higher score
            p = intent.probability
            local_entropy = -p * np.log(p + 1e-10)
            score = p * (1 - local_entropy)
            scores.append(score)
        
        # Select intent with highest score
        max_idx = np.argmax(scores)
        return superposition.intents[max_idx]
    
    def calculate_collapse_probability_density(
        self,
        superposition: IntentSuperposition,
        measurement: MeasurementEvent
    ) -> Dict[str, float]:
        """
        Calculate probability density for collapse for each intent.
        
        This computes how likely each intent is to be the result of collapse,
        taking into account both the superposition state and measurement features.
        
        Args:
            superposition: The intent superposition
            measurement: The measurement event
            
        Returns:
            Dictionary mapping intent labels to collapse probability densities
        """
        densities = {}
        
        for intent in superposition.intents:
            # Base probability from superposition
            base_prob = intent.probability
            
            # Measurement confidence factor
            confidence_factor = measurement.confidence
            
            # Feature similarity (if features available)
            feature_similarity = 1.0
            if measurement.features is not None and intent.features is not None:
                # Compute cosine similarity
                dot_product = np.dot(measurement.features, intent.features)
                norm_product = (np.linalg.norm(measurement.features) * 
                              np.linalg.norm(intent.features))
                if norm_product > 0:
                    feature_similarity = (dot_product / norm_product + 1) / 2  # Normalize to [0,1]
            
            # Combined probability density
            density = base_prob * confidence_factor * feature_similarity
            densities[intent.label] = density
        
        # Normalize densities
        total = sum(densities.values())
        if total > 0:
            densities = {k: v / total for k, v in densities.items()}
        
        return densities
