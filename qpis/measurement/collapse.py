"""
Measurement Collapse

Implements measurement event logic to collapse intent superpositions
into concrete execution paths based on probability density functions.
"""

import numpy as np
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MeasurementType(Enum):
    """Types of measurement events."""
    OBSERVATION = "observation"
    INTERACTION = "interaction"
    SIGNAL = "signal"
    TEMPORAL = "temporal"
    ENTROPY_THRESHOLD = "entropy_threshold"


@dataclass
class MeasurementEvent:
    """Represents a measurement event that triggers collapse."""
    
    event_type: MeasurementType
    timestamp: float
    context: Dict[str, Any]
    outcome: Optional[str] = None
    probability: Optional[float] = None


class MeasurementCollapse:
    """
    Measurement Event Logic for Intent Collapse
    
    Handles the transition from quantum-like superposition to classical
    execution through measurement events. Uses probability density functions
    to determine collapse outcomes.
    """
    
    def __init__(self, collapse_threshold: float = 0.1):
        """
        Initialize measurement collapse handler.
        
        Args:
            collapse_threshold: Minimum probability for a state to be considered
        """
        self.collapse_threshold = collapse_threshold
        self.measurement_events: List[MeasurementEvent] = []
        self.collapse_operators: Dict[MeasurementType, Callable] = {}
        
        # Register default collapse operators
        self._register_default_operators()
        
        logger.info("Initialized MeasurementCollapse")
    
    def register_collapse_operator(
        self,
        measurement_type: MeasurementType,
        operator: Callable
    ):
        """
        Register a custom collapse operator for a measurement type.
        
        Args:
            measurement_type: Type of measurement
            operator: Function that modifies probability distribution
        """
        self.collapse_operators[measurement_type] = operator
        logger.debug(f"Registered collapse operator for {measurement_type.value}")
    
    def measure(
        self,
        intent_superposition: Any,  # IntentSuperposition
        measurement_type: MeasurementType = MeasurementType.OBSERVATION,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:  # IntentState
        """
        Perform a measurement and collapse the superposition.
        
        Args:
            intent_superposition: The superposition to measure
            measurement_type: Type of measurement event
            context: Additional measurement context
            
        Returns:
            The collapsed IntentState
        """
        context = context or {}
        
        # Apply measurement operator if registered
        if measurement_type in self.collapse_operators:
            operator = self.collapse_operators[measurement_type]
            operator(intent_superposition, context)
        
        # Perform the actual measurement/collapse
        collapsed_state = intent_superposition.measure(context=context)
        
        # Record measurement event
        event = MeasurementEvent(
            event_type=measurement_type,
            timestamp=float(np.datetime64("now").astype(float)),
            context=context,
            outcome=collapsed_state.state_id,
            probability=collapsed_state.probability
        )
        self.measurement_events.append(event)
        
        logger.info(
            f"Measurement ({measurement_type.value}) collapsed to "
            f"'{collapsed_state.state_id}' with P={collapsed_state.probability:.4f}"
        )
        
        return collapsed_state
    
    def should_collapse(
        self,
        intent_superposition: Any,  # IntentSuperposition
        entropy_threshold: Optional[float] = None
    ) -> bool:
        """
        Determine if a superposition should be collapsed based on criteria.
        
        Args:
            intent_superposition: Superposition to evaluate
            entropy_threshold: Custom entropy threshold
            
        Returns:
            True if collapse should occur
        """
        # Already collapsed
        if intent_superposition.collapsed_state:
            return False
        
        # Check entropy
        probs = list(intent_superposition.get_state_probabilities().values())
        if probs:
            probs = np.array(probs)
            probs = probs[probs > 0]
            entropy = -np.sum(probs * np.log2(probs + 1e-10))
            
            threshold = entropy_threshold or 1.0
            if entropy < threshold:
                logger.debug(f"Low entropy ({entropy:.4f}) triggers collapse")
                return True
        
        # Check if one state is dominant
        dominant = intent_superposition.get_dominant_state()
        if dominant and dominant.probability > 0.8:
            logger.debug(f"Dominant state ({dominant.probability:.4f}) triggers collapse")
            return True
        
        # Check coherence
        if intent_superposition.coherence < 0.3:
            logger.debug(f"Low coherence ({intent_superposition.coherence:.4f}) triggers collapse")
            return True
        
        return False
    
    def conditional_measure(
        self,
        intent_superposition: Any,  # IntentSuperposition
        condition: Callable[[Any], bool],
        measurement_type: MeasurementType = MeasurementType.OBSERVATION,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:  # Optional[IntentState]
        """
        Conditionally measure based on a custom condition.
        
        Args:
            intent_superposition: Superposition to potentially measure
            condition: Function that returns True if measurement should occur
            measurement_type: Type of measurement
            context: Measurement context
            
        Returns:
            Collapsed state if condition met, None otherwise
        """
        if condition(intent_superposition):
            return self.measure(intent_superposition, measurement_type, context)
        return None
    
    def force_collapse_to_state(
        self,
        intent_superposition: Any,  # IntentSuperposition
        target_state_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:  # Optional[IntentState]
        """
        Force collapse to a specific state (bypassing probability).
        
        Useful for deterministic execution requirements.
        
        Args:
            intent_superposition: Superposition to collapse
            target_state_id: Desired state to collapse to
            context: Measurement context
            
        Returns:
            The collapsed state if successful
        """
        if target_state_id not in intent_superposition.states:
            logger.error(f"Cannot force collapse: state '{target_state_id}' not found")
            return None
        
        # Set target state amplitude to 1, others to near-zero
        for state_id in intent_superposition.states:
            if state_id == target_state_id:
                intent_superposition.states[state_id].probability_amplitude = 1.0
            else:
                intent_superposition.states[state_id].probability_amplitude = 0.01
        
        intent_superposition._normalize_amplitudes()
        
        # Now measure (will collapse to target with high probability)
        collapsed = self.measure(
            intent_superposition,
            MeasurementType.INTERACTION,
            context or {}
        )
        
        logger.info(f"Forced collapse to state '{target_state_id}'")
        return collapsed
    
    def get_measurement_history(
        self,
        measurement_type: Optional[MeasurementType] = None
    ) -> List[MeasurementEvent]:
        """
        Get history of measurement events.
        
        Args:
            measurement_type: Filter by measurement type (optional)
            
        Returns:
            List of measurement events
        """
        if measurement_type:
            return [
                event for event in self.measurement_events
                if event.event_type == measurement_type
            ]
        return self.measurement_events
    
    def get_collapse_statistics(self) -> Dict[str, Any]:
        """Get statistics about collapse events."""
        if not self.measurement_events:
            return {"total_measurements": 0}
        
        type_counts = {}
        for event in self.measurement_events:
            event_type = event.event_type.value
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        probabilities = [
            event.probability for event in self.measurement_events
            if event.probability is not None
        ]
        
        return {
            "total_measurements": len(self.measurement_events),
            "by_type": type_counts,
            "mean_probability": float(np.mean(probabilities)) if probabilities else 0.0,
            "min_probability": float(np.min(probabilities)) if probabilities else 0.0,
            "max_probability": float(np.max(probabilities)) if probabilities else 0.0,
        }
    
    def _register_default_operators(self):
        """Register default collapse operators."""
        
        def entropy_operator(superposition, context):
            """Boost high-entropy states for observation measurements."""
            probs = list(superposition.get_state_probabilities().values())
            if not probs:
                return
            
            entropy = -np.sum([p * np.log2(p + 1e-10) for p in probs if p > 0])
            boost_factor = 1.0 + 0.1 * entropy
            
            for state in superposition.states.values():
                state.probability_amplitude *= boost_factor
            
            superposition._normalize_amplitudes()
        
        def interaction_operator(superposition, context):
            """Bias toward states mentioned in interaction context."""
            if "preferred_states" in context:
                preferred = context["preferred_states"]
                for state_id in preferred:
                    if state_id in superposition.states:
                        superposition.states[state_id].probability_amplitude *= 1.5
                
                superposition._normalize_amplitudes()
        
        self.register_collapse_operator(MeasurementType.OBSERVATION, entropy_operator)
        self.register_collapse_operator(MeasurementType.INTERACTION, interaction_operator)
    
    def reset(self):
        """Reset measurement history."""
        self.measurement_events.clear()
        logger.debug("Reset measurement history")
