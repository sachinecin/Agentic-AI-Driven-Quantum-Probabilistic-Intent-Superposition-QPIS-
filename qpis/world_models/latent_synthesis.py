"""
Latent Intent Synthesizer

Synthesizes latent representations of intent from multi-modal signals
and world model predictions for teleological behavior shaping.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LatentVector:
    """Represents a latent space encoding of intent."""
    
    vector: np.ndarray
    dimensionality: int
    source: str  # 'behavioral', 'physiological', 'environmental', 'synthetic'
    confidence: float = 1.0
    
    def __post_init__(self):
        self.dimensionality = len(self.vector)


class LatentIntentSynthesizer:
    """
    Latent Intent Synthesis Engine
    
    Synthesizes intent representations in latent space by combining:
    - Behavioral signals (actions, interactions)
    - Physiological signals (HRV, haptic feedback)
    - Environmental context
    - World model predictions
    
    The synthesized latent vectors are used to shape agent behavior
    and predict future intent trajectories.
    """
    
    def __init__(
        self,
        latent_dim: int = 128,
        learning_rate: float = 0.001
    ):
        """
        Initialize the latent synthesizer.
        
        Args:
            latent_dim: Dimensionality of latent space
            learning_rate: Learning rate for online updates
        """
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        
        # Latent space parameters
        self.intent_basis = self._initialize_basis(latent_dim)
        self.synthesis_history: List[LatentVector] = []
        
        logger.info(f"Initialized LatentIntentSynthesizer with dim={latent_dim}")
    
    def synthesize(
        self,
        behavioral_signals: Optional[np.ndarray] = None,
        physiological_signals: Optional[np.ndarray] = None,
        environmental_context: Optional[np.ndarray] = None,
        world_model_prediction: Optional[np.ndarray] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> LatentVector:
        """
        Synthesize a latent intent vector from multiple signal sources.
        
        Args:
            behavioral_signals: Behavioral observation vector
            physiological_signals: HRV/haptic signals
            environmental_context: Environmental state
            world_model_prediction: World model prediction
            weights: Weighting for each signal source
            
        Returns:
            Synthesized latent vector
        """
        # Default weights
        if weights is None:
            weights = {
                "behavioral": 0.4,
                "physiological": 0.3,
                "environmental": 0.2,
                "world_model": 0.1
            }
        
        # Initialize latent vector
        latent = np.zeros(self.latent_dim)
        total_weight = 0.0
        sources = []
        
        # Encode behavioral signals
        if behavioral_signals is not None:
            encoded = self._encode_to_latent(behavioral_signals, "behavioral")
            latent += weights["behavioral"] * encoded
            total_weight += weights["behavioral"]
            sources.append("behavioral")
        
        # Encode physiological signals
        if physiological_signals is not None:
            encoded = self._encode_to_latent(physiological_signals, "physiological")
            latent += weights["physiological"] * encoded
            total_weight += weights["physiological"]
            sources.append("physiological")
        
        # Encode environmental context
        if environmental_context is not None:
            encoded = self._encode_to_latent(environmental_context, "environmental")
            latent += weights["environmental"] * encoded
            total_weight += weights["environmental"]
            sources.append("environmental")
        
        # Incorporate world model prediction
        if world_model_prediction is not None:
            encoded = self._encode_to_latent(world_model_prediction, "world_model")
            latent += weights["world_model"] * encoded
            total_weight += weights["world_model"]
            sources.append("world_model")
        
        # Normalize
        if total_weight > 0:
            latent = latent / total_weight
        
        # Create latent vector object
        latent_vec = LatentVector(
            vector=latent,
            dimensionality=self.latent_dim,
            source="+".join(sources),
            confidence=total_weight
        )
        
        # Store in history
        self.synthesis_history.append(latent_vec)
        
        logger.debug(f"Synthesized latent vector from {len(sources)} sources")
        
        return latent_vec
    
    def predict_trajectory(
        self,
        current_latent: LatentVector,
        time_steps: int = 10
    ) -> List[LatentVector]:
        """
        Predict future trajectory in latent space.
        
        Uses learned dynamics to forecast intent evolution.
        
        Args:
            current_latent: Current latent state
            time_steps: Number of steps to predict
            
        Returns:
            List of predicted latent vectors
        """
        trajectory = [current_latent]
        current = current_latent.vector
        
        # Simple autoregressive prediction
        for t in range(time_steps):
            # Predict next step with some noise
            momentum = 0.9 if t > 0 else 0.0
            if t > 0:
                delta = current - trajectory[-2].vector
            else:
                delta = np.zeros_like(current)
            
            noise = np.random.randn(self.latent_dim) * 0.01
            next_vec = current + momentum * delta + noise
            
            # Project onto intent basis
            next_vec = self._project_to_basis(next_vec)
            
            latent = LatentVector(
                vector=next_vec,
                dimensionality=self.latent_dim,
                source="predicted",
                confidence=0.9 ** (t + 1)  # Decay confidence
            )
            
            trajectory.append(latent)
            current = next_vec
        
        logger.debug(f"Predicted trajectory of {time_steps} steps")
        
        return trajectory
    
    def align_with_goal(
        self,
        current_latent: LatentVector,
        goal_latent: LatentVector,
        strength: float = 0.5
    ) -> LatentVector:
        """
        Align a latent vector toward a goal.
        
        Used in teleological optimization to shape intent toward goals.
        
        Args:
            current_latent: Current intent latent
            goal_latent: Target goal latent
            strength: Alignment strength (0-1)
            
        Returns:
            Aligned latent vector
        """
        # Interpolate toward goal
        aligned_vec = (
            (1 - strength) * current_latent.vector +
            strength * goal_latent.vector
        )
        
        # Normalize
        aligned_vec = aligned_vec / (np.linalg.norm(aligned_vec) + 1e-8)
        
        aligned = LatentVector(
            vector=aligned_vec,
            dimensionality=self.latent_dim,
            source="goal_aligned",
            confidence=current_latent.confidence * (1 - 0.1 * strength)
        )
        
        return aligned
    
    def compute_similarity(
        self,
        latent1: LatentVector,
        latent2: LatentVector
    ) -> float:
        """
        Compute similarity between two latent vectors.
        
        Returns:
            Cosine similarity (-1 to 1)
        """
        norm1 = np.linalg.norm(latent1.vector)
        norm2 = np.linalg.norm(latent2.vector)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(latent1.vector, latent2.vector) / (norm1 * norm2)
        
        return float(similarity)
    
    def cluster_intents(
        self,
        latent_vectors: List[LatentVector],
        n_clusters: int = 5
    ) -> Dict[int, List[LatentVector]]:
        """
        Cluster latent vectors to identify intent patterns.
        
        Args:
            latent_vectors: List of latent vectors to cluster
            n_clusters: Number of clusters
            
        Returns:
            Dictionary mapping cluster_id to list of vectors
        """
        if not latent_vectors:
            return {}
        
        # Extract vectors
        vectors = np.array([lv.vector for lv in latent_vectors])
        
        # Simple k-means clustering
        centroids = vectors[np.random.choice(len(vectors), n_clusters, replace=False)]
        
        for _ in range(10):  # Iterations
            # Assign to clusters
            distances = np.array([
                [np.linalg.norm(v - c) for c in centroids]
                for v in vectors
            ])
            assignments = np.argmin(distances, axis=1)
            
            # Update centroids
            for k in range(n_clusters):
                mask = assignments == k
                if np.any(mask):
                    centroids[k] = np.mean(vectors[mask], axis=0)
        
        # Group by cluster
        clusters = {k: [] for k in range(n_clusters)}
        for i, cluster_id in enumerate(assignments):
            clusters[cluster_id].append(latent_vectors[i])
        
        logger.info(f"Clustered {len(latent_vectors)} vectors into {n_clusters} clusters")
        
        return clusters
    
    def _encode_to_latent(
        self,
        signal: np.ndarray,
        source_type: str
    ) -> np.ndarray:
        """
        Encode a signal to latent space.
        
        Uses learned projection matrices (simplified here).
        """
        # Ensure signal is 1D
        if signal.ndim > 1:
            signal = signal.flatten()
        
        # Pad or truncate to latent_dim
        if len(signal) < self.latent_dim:
            encoded = np.zeros(self.latent_dim)
            encoded[:len(signal)] = signal
        else:
            encoded = signal[:self.latent_dim]
        
        # Project onto intent basis
        encoded = self._project_to_basis(encoded)
        
        # Normalize
        norm = np.linalg.norm(encoded)
        if norm > 0:
            encoded = encoded / norm
        
        return encoded
    
    def _project_to_basis(self, vector: np.ndarray) -> np.ndarray:
        """Project a vector onto the intent basis."""
        # Project onto each basis vector and reconstruct
        projection = np.zeros_like(vector)
        
        for basis_vec in self.intent_basis:
            coeff = np.dot(vector, basis_vec)
            projection += coeff * basis_vec
        
        return projection
    
    def _initialize_basis(self, dim: int) -> np.ndarray:
        """Initialize orthonormal basis for latent space."""
        # Create random basis and orthogonalize
        basis = np.random.randn(dim, dim)
        
        # Gram-Schmidt orthogonalization
        for i in range(dim):
            for j in range(i):
                basis[i] -= np.dot(basis[i], basis[j]) * basis[j]
            
            norm = np.linalg.norm(basis[i])
            if norm > 0:
                basis[i] /= norm
        
        return basis
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about synthesis history."""
        if not self.synthesis_history:
            return {"count": 0}
        
        confidences = [lv.confidence for lv in self.synthesis_history]
        
        return {
            "count": len(self.synthesis_history),
            "mean_confidence": float(np.mean(confidences)),
            "latent_dim": self.latent_dim
        }
