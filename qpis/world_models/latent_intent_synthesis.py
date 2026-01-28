"""
Latent Intent Synthesis Module

Synthesizes latent intents from observations and world model predictions,
creating intent superpositions that capture possible user goals.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from qpis.core.intent_superposition import IntentSuperposition, Intent


@dataclass
class LatentIntent:
    """
    Represents a latent (hidden) intent inferred from observations.
    
    Attributes:
        label: Intent identifier
        latent_vector: Embedding in latent space
        confidence: Confidence in this inference
        evidence: Supporting evidence features
        complexity: Estimated complexity (0=simple, 1=complex)
    """
    label: str
    latent_vector: np.ndarray
    confidence: float = 0.5
    evidence: Optional[Dict] = None
    complexity: float = 0.5


class LatentIntentSynthesizer:
    """
    Synthesizes latent intents from observations using world model representations.
    
    This component bridges the gap between raw observations and intent superpositions
    by inferring hidden goals from behavioral patterns and context.
    """
    
    def __init__(self, latent_dim: int = 64):
        """
        Initialize latent intent synthesizer.
        
        Args:
            latent_dim: Dimensionality of latent intent space
        """
        self.latent_dim = latent_dim
        self.intent_library: Dict[str, LatentIntent] = {}
        self.synthesis_history: List[Dict] = []
    
    def register_intent_template(
        self,
        label: str,
        template_vector: np.ndarray,
        complexity: float = 0.5
    ):
        """
        Register a template for a known intent type.
        
        Args:
            label: Intent identifier
            template_vector: Template vector in latent space
            complexity: Complexity score for this intent
        """
        if len(template_vector) != self.latent_dim:
            raise ValueError(f"Template vector must have dimension {self.latent_dim}")
        
        self.intent_library[label] = LatentIntent(
            label=label,
            latent_vector=template_vector,
            complexity=complexity
        )
    
    def encode_observation(self, observation: Dict) -> np.ndarray:
        """
        Encode an observation into latent space.
        
        In a full implementation, this would use a learned encoder (e.g., VAE).
        Here we provide a simple deterministic encoding.
        
        Args:
            observation: Dictionary of observation features
            
        Returns:
            Latent vector representation
        """
        # Simple encoding: hash features into latent space
        latent_vector = np.zeros(self.latent_dim)
        
        for key, value in observation.items():
            # Create a simple hash-based encoding
            key_hash = hash(key) % self.latent_dim
            
            if isinstance(value, (int, float)):
                latent_vector[key_hash] += float(value)
            elif isinstance(value, str):
                str_hash = hash(value) % self.latent_dim
                latent_vector[str_hash] += 1.0
            elif isinstance(value, (list, tuple)) and value:
                latent_vector[key_hash] += len(value)
        
        # Normalize
        norm = np.linalg.norm(latent_vector)
        if norm > 0:
            latent_vector = latent_vector / norm
        
        return latent_vector
    
    def compute_intent_similarity(
        self,
        observation_vector: np.ndarray,
        intent: LatentIntent
    ) -> float:
        """
        Compute similarity between observation and intent template.
        
        Args:
            observation_vector: Encoded observation
            intent: Intent template
            
        Returns:
            Similarity score (0-1)
        """
        # Cosine similarity
        dot_product = np.dot(observation_vector, intent.latent_vector)
        norm_product = (np.linalg.norm(observation_vector) *
                       np.linalg.norm(intent.latent_vector))
        
        if norm_product == 0:
            return 0.0
        
        similarity = (dot_product / norm_product + 1) / 2  # Normalize to [0,1]
        return similarity
    
    def synthesize_intents(
        self,
        observations: List[Dict],
        top_k: int = 5
    ) -> List[LatentIntent]:
        """
        Synthesize latent intents from a sequence of observations.
        
        Args:
            observations: List of observation dictionaries
            top_k: Number of top intents to return
            
        Returns:
            List of synthesized latent intents
        """
        if not observations:
            return []
        
        # Encode all observations
        observation_vectors = [self.encode_observation(obs) for obs in observations]
        
        # Aggregate observations (temporal averaging with recency bias)
        weights = np.exp(np.linspace(-1, 0, len(observation_vectors)))
        weights = weights / weights.sum()
        
        aggregated_vector = sum(w * v for w, v in zip(weights, observation_vectors))
        
        # Compute similarities to all intent templates
        intent_scores = []
        
        for intent in self.intent_library.values():
            similarity = self.compute_intent_similarity(aggregated_vector, intent)
            
            # Adjust for complexity (complex intents need higher threshold)
            confidence = similarity * (1 - intent.complexity * 0.3)
            
            intent_scores.append((intent, confidence))
        
        # Sort by confidence and take top k
        intent_scores.sort(key=lambda x: x[1], reverse=True)
        
        synthesized = []
        for intent, confidence in intent_scores[:top_k]:
            # Create a new LatentIntent with updated confidence
            synthesized_intent = LatentIntent(
                label=intent.label,
                latent_vector=intent.latent_vector.copy(),
                confidence=confidence,
                evidence={"observations": len(observations)},
                complexity=intent.complexity
            )
            synthesized.append(synthesized_intent)
        
        # Record synthesis
        self.synthesis_history.append({
            "num_observations": len(observations),
            "num_synthesized": len(synthesized),
            "top_intent": synthesized[0].label if synthesized else None,
            "top_confidence": synthesized[0].confidence if synthesized else 0.0
        })
        
        return synthesized
    
    def create_superposition_from_latent(
        self,
        latent_intents: List[LatentIntent]
    ) -> IntentSuperposition:
        """
        Create an intent superposition from synthesized latent intents.
        
        Args:
            latent_intents: List of latent intents
            
        Returns:
            IntentSuperposition object
        """
        intents = []
        
        for latent_intent in latent_intents:
            # Convert confidence to probability amplitude
            amplitude = np.sqrt(latent_intent.confidence)
            
            intent = Intent(
                label=latent_intent.label,
                amplitude=amplitude,
                features=latent_intent.latent_vector,
                teleological_weight=1.0 - latent_intent.complexity  # Simpler intents have higher weight
            )
            intents.append(intent)
        
        superposition = IntentSuperposition(intents)
        superposition.normalize()
        
        return superposition
    
    def refine_latent_intent(
        self,
        intent: LatentIntent,
        new_observation: Dict,
        learning_rate: float = 0.1
    ) -> LatentIntent:
        """
        Refine a latent intent based on new observations.
        
        Args:
            intent: Existing latent intent
            new_observation: New observation to incorporate
            learning_rate: How much to update based on new observation
            
        Returns:
            Refined latent intent
        """
        # Encode new observation
        obs_vector = self.encode_observation(new_observation)
        
        # Update latent vector (moving average)
        updated_vector = (1 - learning_rate) * intent.latent_vector + \
                        learning_rate * obs_vector
        
        # Renormalize
        norm = np.linalg.norm(updated_vector)
        if norm > 0:
            updated_vector = updated_vector / norm
        
        # Update confidence based on consistency
        consistency = self.compute_intent_similarity(obs_vector, intent)
        updated_confidence = (1 - learning_rate) * intent.confidence + \
                            learning_rate * consistency
        
        return LatentIntent(
            label=intent.label,
            latent_vector=updated_vector,
            confidence=updated_confidence,
            evidence=intent.evidence,
            complexity=intent.complexity
        )
    
    def predict_next_intent(
        self,
        current_superposition: IntentSuperposition,
        context: Optional[Dict] = None
    ) -> Tuple[str, float]:
        """
        Predict the most likely next intent based on current superposition.
        
        Args:
            current_superposition: Current intent superposition
            context: Optional context information
            
        Returns:
            Tuple of (predicted_intent_label, confidence)
        """
        if not current_superposition.intents:
            return ("unknown", 0.0)
        
        # Get dominant intent
        dominant = current_superposition.get_dominant_intent()
        
        if dominant is None:
            return ("unknown", 0.0)
        
        # Simple prediction: assume continuation of dominant intent
        # In practice, would use a learned model
        confidence = dominant.probability
        
        return (dominant.label, confidence)
    
    def get_synthesis_summary(self) -> Dict:
        """
        Get summary of synthesis activity.
        
        Returns:
            Dictionary with synthesis statistics
        """
        if not self.synthesis_history:
            return {"total_syntheses": 0}
        
        return {
            "total_syntheses": len(self.synthesis_history),
            "avg_observations": np.mean([h["num_observations"] for h in self.synthesis_history]),
            "avg_intents_per_synthesis": np.mean([h["num_synthesized"] for h in self.synthesis_history]),
            "recent_top_intent": self.synthesis_history[-1]["top_intent"] if self.synthesis_history else None,
            "recent_confidence": self.synthesis_history[-1]["top_confidence"] if self.synthesis_history else 0.0
        }
