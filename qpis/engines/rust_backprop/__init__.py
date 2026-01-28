"""
Rust Back-Propagation Engine Bindings

Python interface to the high-performance Rust back-propagation engine.
Falls back to Python implementation if Rust extension is not available.
"""

import logging

logger = logging.getLogger(__name__)

# Try to import Rust extension
try:
    from qpis_rust_backprop import RustBackPropEngine, TeleologicalState
    RUST_AVAILABLE = True
    logger.info("Rust back-propagation engine loaded successfully")
except ImportError:
    RUST_AVAILABLE = False
    logger.warning("Rust back-propagation engine not available, using Python fallback")
    
    # Python fallback
    class RustBackPropEngine:
        """Python fallback for Rust engine."""
        
        def __init__(self, learning_rate=0.01, decay_factor=0.95, max_depth=100):
            self.learning_rate = learning_rate
            self.decay_factor = decay_factor
            self.max_depth = max_depth
        
        def compute_gradients(self, current_features, goal_features, time_horizon):
            """Fallback gradient computation."""
            import numpy as np
            current = np.array(current_features)
            goal = np.array(goal_features)
            error = goal - current
            temporal_weight = np.exp(-time_horizon / self.decay_factor)
            gradient = temporal_weight * error
            return gradient.tolist()
        
        def compute_alignment(self, state_features, goal_features):
            """Fallback alignment computation."""
            import numpy as np
            state = np.array(state_features)
            goal = np.array(goal_features)
            
            state_norm = np.linalg.norm(state)
            goal_norm = np.linalg.norm(goal)
            
            if state_norm == 0 or goal_norm == 0:
                return 0.0
            
            similarity = np.dot(state, goal) / (state_norm * goal_norm)
            return (similarity + 1.0) / 2.0
        
        def __repr__(self):
            return f"RustBackPropEngine(Python fallback)"
    
    class TeleologicalState:
        """Python fallback for TeleologicalState."""
        
        def __init__(self, state_id, features):
            self.state_id = state_id
            self.features = features
            self.gradient = [0.0] * len(features)
            self.goal_distance = float('inf')
        
        def __repr__(self):
            return f"TeleologicalState(id={self.state_id}, dims={len(self.features)})"


__all__ = ["RustBackPropEngine", "TeleologicalState", "RUST_AVAILABLE"]
