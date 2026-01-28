"""
Signal Mesh Coordinator

Coordinates multiple signal sources (HRV, haptic, etc.) into a unified
entropy mesh for comprehensive intent inference.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from qpis.sdk.hrv.processor import HRVProcessor, HRVMetrics
from qpis.sdk.haptic.processor import HapticProcessor, HapticMetrics

logger = logging.getLogger(__name__)


class SignalSource(Enum):
    """Types of signal sources."""
    HRV = "hrv"
    HAPTIC = "haptic"
    GAZE = "gaze"
    VOICE = "voice"
    MOTION = "motion"
    ENVIRONMENTAL = "environmental"


@dataclass
class MeshState:
    """Represents the current state of the signal mesh."""
    
    timestamp: float
    active_sources: List[SignalSource]
    entropy_vector: np.ndarray
    coherence: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "active_sources": [s.value for s in self.active_sources],
            "entropy_vector": self.entropy_vector.tolist(),
            "coherence": self.coherence,
            "confidence": self.confidence
        }


class SignalMeshCoordinator:
    """
    Neuro-Signal Mesh Coordinator
    
    Integrates multiple physiological and behavioral signal sources
    into a unified entropy mesh. This mesh provides a holistic view
    of user state for intent inference.
    
    The mesh coordinates:
    - HRV (physiological arousal/load)
    - Haptic feedback (interaction patterns)
    - Additional modalities (extensible)
    
    Outputs a unified entropy vector that captures multi-modal
    user state for latent intent synthesis.
    """
    
    def __init__(
        self,
        hrv_processor: Optional[HRVProcessor] = None,
        haptic_processor: Optional[HapticProcessor] = None
    ):
        """
        Initialize signal mesh coordinator.
        
        Args:
            hrv_processor: HRV processor instance
            haptic_processor: Haptic processor instance
        """
        self.hrv_processor = hrv_processor or HRVProcessor()
        self.haptic_processor = haptic_processor or HapticProcessor()
        
        # Additional processors (extensible)
        self.processors: Dict[SignalSource, Any] = {
            SignalSource.HRV: self.hrv_processor,
            SignalSource.HAPTIC: self.haptic_processor
        }
        
        self.mesh_history: List[MeshState] = []
        self.entropy_weights: Dict[SignalSource, float] = {
            SignalSource.HRV: 0.4,
            SignalSource.HAPTIC: 0.4,
            SignalSource.GAZE: 0.1,
            SignalSource.VOICE: 0.1
        }
        
        logger.info("Initialized SignalMeshCoordinator")
    
    def register_processor(
        self,
        source: SignalSource,
        processor: Any
    ):
        """
        Register a new signal processor.
        
        Args:
            source: Signal source type
            processor: Processor instance
        """
        self.processors[source] = processor
        logger.info(f"Registered processor for {source.value}")
    
    def set_entropy_weights(self, weights: Dict[SignalSource, float]):
        """
        Set weighting for different entropy sources.
        
        Args:
            weights: Dictionary mapping sources to weights
        """
        self.entropy_weights.update(weights)
        logger.debug(f"Updated entropy weights")
    
    def compute_mesh_state(self) -> MeshState:
        """
        Compute current signal mesh state.
        
        Integrates all active signal sources into unified representation.
        
        Returns:
            Current MeshState
        """
        active_sources = []
        entropy_components = []
        confidences = []
        
        # Process HRV signals
        if SignalSource.HRV in self.processors:
            hrv_metrics = self.hrv_processor.compute_metrics()
            if hrv_metrics:
                hrv_features = self.hrv_processor.extract_intent_features(hrv_metrics)
                entropy_components.append(
                    self.entropy_weights.get(SignalSource.HRV, 1.0) * hrv_features
                )
                active_sources.append(SignalSource.HRV)
                confidences.append(0.9)  # HRV is reliable
        
        # Process haptic signals
        if SignalSource.HAPTIC in self.processors:
            haptic_metrics = self.haptic_processor.compute_metrics()
            if haptic_metrics:
                haptic_features = self.haptic_processor.extract_intent_features(haptic_metrics)
                entropy_components.append(
                    self.entropy_weights.get(SignalSource.HAPTIC, 1.0) * haptic_features
                )
                active_sources.append(SignalSource.HAPTIC)
                confidences.append(
                    self.haptic_processor.get_interaction_confidence(haptic_metrics)
                )
        
        # Combine entropy components
        if entropy_components:
            # Pad to same size
            max_len = max(len(e) for e in entropy_components)
            padded = []
            for comp in entropy_components:
                if len(comp) < max_len:
                    padded_comp = np.zeros(max_len)
                    padded_comp[:len(comp)] = comp
                    padded.append(padded_comp)
                else:
                    padded.append(comp)
            
            entropy_vector = np.sum(padded, axis=0)
            
            # Normalize
            norm = np.linalg.norm(entropy_vector)
            if norm > 0:
                entropy_vector = entropy_vector / norm
        else:
            entropy_vector = np.zeros(8)  # Default size
        
        # Compute coherence (how well signals agree)
        coherence = self._compute_coherence(entropy_components)
        
        # Overall confidence
        confidence = np.mean(confidences) if confidences else 0.0
        
        # Create mesh state
        mesh_state = MeshState(
            timestamp=float(np.datetime64("now").astype(float)),
            active_sources=active_sources,
            entropy_vector=entropy_vector,
            coherence=coherence,
            confidence=confidence
        )
        
        self.mesh_history.append(mesh_state)
        
        logger.debug(
            f"Computed mesh state: {len(active_sources)} sources, "
            f"coherence={coherence:.4f}"
        )
        
        return mesh_state
    
    def get_unified_entropy(self) -> np.ndarray:
        """
        Get unified entropy vector from all sources.
        
        Returns:
            Combined entropy vector
        """
        mesh_state = self.compute_mesh_state()
        return mesh_state.entropy_vector
    
    def predict_intent_state(
        self,
        mesh_state: Optional[MeshState] = None
    ) -> Dict[str, float]:
        """
        Predict high-level intent state from mesh.
        
        Args:
            mesh_state: Mesh state to analyze (computes current if None)
            
        Returns:
            Dictionary of intent state probabilities
        """
        if mesh_state is None:
            mesh_state = self.compute_mesh_state()
        
        entropy_vec = mesh_state.entropy_vector
        
        # Simple heuristic classification
        # In production, use trained models
        
        # High entropy -> exploratory/uncertain
        # Low entropy -> focused/decisive
        total_entropy = np.sum(entropy_vec)
        
        # High magnitude -> active/engaged
        # Low magnitude -> passive/disengaged
        magnitude = np.linalg.norm(entropy_vec)
        
        intent_states = {
            "exploratory": float(np.clip(total_entropy, 0, 1)),
            "decisive": float(np.clip(1.0 - total_entropy, 0, 1)),
            "engaged": float(np.clip(magnitude, 0, 1)),
            "passive": float(np.clip(1.0 - magnitude, 0, 1)),
            "confident": mesh_state.confidence,
            "uncertain": 1.0 - mesh_state.confidence
        }
        
        # Normalize
        total = sum(intent_states.values())
        if total > 0:
            intent_states = {k: v / total for k, v in intent_states.items()}
        
        return intent_states
    
    def detect_state_transitions(
        self,
        window_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Detect significant transitions in mesh state.
        
        Args:
            window_size: Number of past states to analyze
            
        Returns:
            List of detected transitions
        """
        if len(self.mesh_history) < window_size:
            return []
        
        recent_states = self.mesh_history[-window_size:]
        transitions = []
        
        # Analyze entropy changes
        entropies = [np.sum(s.entropy_vector) for s in recent_states]
        entropy_change = entropies[-1] - entropies[0]
        
        if abs(entropy_change) > 0.3:
            transitions.append({
                "type": "entropy_shift",
                "direction": "increase" if entropy_change > 0 else "decrease",
                "magnitude": abs(entropy_change)
            })
        
        # Analyze coherence changes
        coherences = [s.coherence for s in recent_states]
        coherence_change = coherences[-1] - coherences[0]
        
        if abs(coherence_change) > 0.2:
            transitions.append({
                "type": "coherence_shift",
                "direction": "increase" if coherence_change > 0 else "decrease",
                "magnitude": abs(coherence_change)
            })
        
        # Analyze confidence changes
        confidences = [s.confidence for s in recent_states]
        confidence_change = confidences[-1] - confidences[0]
        
        if abs(confidence_change) > 0.3:
            transitions.append({
                "type": "confidence_shift",
                "direction": "increase" if confidence_change > 0 else "decrease",
                "magnitude": abs(confidence_change)
            })
        
        return transitions
    
    def _compute_coherence(
        self,
        entropy_components: List[np.ndarray]
    ) -> float:
        """
        Compute coherence between signal sources.
        
        High coherence: signals agree
        Low coherence: signals conflict
        
        Returns:
            Coherence score (0-1)
        """
        if len(entropy_components) < 2:
            return 1.0  # Single source always coherent
        
        # Compute pairwise cosine similarities
        similarities = []
        for i in range(len(entropy_components)):
            for j in range(i + 1, len(entropy_components)):
                vec1 = entropy_components[i]
                vec2 = entropy_components[j]
                
                # Pad to same length
                max_len = max(len(vec1), len(vec2))
                if len(vec1) < max_len:
                    padded1 = np.zeros(max_len)
                    padded1[:len(vec1)] = vec1
                    vec1 = padded1
                if len(vec2) < max_len:
                    padded2 = np.zeros(max_len)
                    padded2[:len(vec2)] = vec2
                    vec2 = padded2
                
                # Cosine similarity
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = np.dot(vec1, vec2) / (norm1 * norm2)
                    # Map to [0, 1]
                    similarity = (similarity + 1) / 2
                    similarities.append(similarity)
        
        if not similarities:
            return 0.5  # Neutral
        
        # Average similarity
        coherence = np.mean(similarities)
        
        return float(coherence)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the signal mesh."""
        active_sources = list(self.processors.keys())
        
        return {
            "active_sources": [s.value for s in active_sources],
            "mesh_history_length": len(self.mesh_history),
            "entropy_weights": {
                k.value: v for k, v in self.entropy_weights.items()
            }
        }
    
    def reset(self):
        """Reset all processors and mesh state."""
        for processor in self.processors.values():
            if hasattr(processor, 'reset'):
                processor.reset()
        
        self.mesh_history.clear()
        logger.debug("Reset signal mesh coordinator")
