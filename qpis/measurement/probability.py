"""
Probability Density Functions

Utilities for computing and manipulating probability densities
in intent superpositions.
"""

import numpy as np
from typing import Callable, List, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class ProbabilityDensity:
    """
    Probability Density Function utilities for intent collapse.
    
    Provides various probability distributions and density functions
    for shaping measurement outcomes.
    """
    
    @staticmethod
    def gaussian(mean: float, std: float, x: float) -> float:
        """
        Gaussian/normal probability density.
        
        Args:
            mean: Distribution mean
            std: Standard deviation
            x: Point to evaluate
            
        Returns:
            Probability density at x
        """
        return float(stats.norm.pdf(x, loc=mean, scale=std))
    
    @staticmethod
    def maxwell_boltzmann(
        temperature: float,
        energy: float
    ) -> float:
        """
        Maxwell-Boltzmann distribution for thermodynamic analogies.
        
        Args:
            temperature: System temperature (analogous parameter)
            energy: State energy
            
        Returns:
            Probability density
        """
        if temperature <= 0:
            return 0.0
        
        k_b = 1.0  # Boltzmann constant (normalized)
        return np.exp(-energy / (k_b * temperature))
    
    @staticmethod
    def softmax(
        logits: np.ndarray,
        temperature: float = 1.0
    ) -> np.ndarray:
        """
        Softmax probability distribution (common in ML).
        
        Args:
            logits: Input logits/scores
            temperature: Temperature parameter (higher = more uniform)
            
        Returns:
            Probability distribution
        """
        scaled_logits = logits / temperature
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
        return exp_logits / np.sum(exp_logits)
    
    @staticmethod
    def power_law(x: float, alpha: float, x_min: float = 1.0) -> float:
        """
        Power-law distribution (common in complex systems).
        
        Args:
            x: Point to evaluate
            alpha: Power-law exponent
            x_min: Minimum x value
            
        Returns:
            Probability density
        """
        if x < x_min:
            return 0.0
        
        normalization = (alpha - 1) / x_min
        return normalization * (x / x_min) ** (-alpha)
    
    @staticmethod
    def quantum_probability(amplitude: complex) -> float:
        """
        Born rule: probability from quantum amplitude.
        
        Args:
            amplitude: Complex probability amplitude
            
        Returns:
            Probability (|amplitude|²)
        """
        return abs(amplitude) ** 2
    
    @staticmethod
    def entropy(probabilities: np.ndarray) -> float:
        """
        Shannon entropy of probability distribution.
        
        Args:
            probabilities: Probability distribution
            
        Returns:
            Entropy in bits
        """
        probs = probabilities[probabilities > 0]
        return float(-np.sum(probs * np.log2(probs)))
    
    @staticmethod
    def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
        """
        Kullback-Leibler divergence between distributions.
        
        Args:
            p: True distribution
            q: Approximate distribution
            
        Returns:
            KL divergence D_KL(P||Q)
        """
        # Filter zeros
        mask = (p > 0) & (q > 0)
        p_filtered = p[mask]
        q_filtered = q[mask]
        
        if len(p_filtered) == 0:
            return 0.0
        
        return float(np.sum(p_filtered * np.log(p_filtered / q_filtered)))
    
    @staticmethod
    def normalize(values: np.ndarray) -> np.ndarray:
        """
        Normalize values to form probability distribution.
        
        Args:
            values: Input values
            
        Returns:
            Normalized probabilities
        """
        total = np.sum(values)
        if total == 0:
            return np.ones_like(values) / len(values)
        return values / total
    
    @staticmethod
    def compute_cumulative(probabilities: np.ndarray) -> np.ndarray:
        """
        Compute cumulative distribution function.
        
        Args:
            probabilities: Probability distribution
            
        Returns:
            Cumulative probabilities
        """
        return np.cumsum(probabilities)
    
    @staticmethod
    def sample_from_pdf(
        pdf: Callable[[float], float],
        x_range: Tuple[float, float],
        n_samples: int = 1000
    ) -> np.ndarray:
        """
        Sample values from a probability density function.
        
        Args:
            pdf: Probability density function
            x_range: Range to sample from (min, max)
            n_samples: Number of samples
            
        Returns:
            Array of sampled values
        """
        x_min, x_max = x_range
        
        # Discretize the range
        x_values = np.linspace(x_min, x_max, 1000)
        pdf_values = np.array([pdf(x) for x in x_values])
        
        # Normalize to probabilities
        probabilities = ProbabilityDensity.normalize(pdf_values)
        
        # Sample
        samples = np.random.choice(x_values, size=n_samples, p=probabilities)
        
        return samples
