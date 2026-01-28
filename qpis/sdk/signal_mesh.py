"""
Signal Mesh Integration

Integrates multiple neuro-signal sources (HRV, haptic, etc.) into a unified
entropy mesh that influences intent superpositions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np

from qpis.sdk.hrv_processor import HRVProcessor, HRVMetrics
from qpis.sdk.haptic_entropy import HapticEntropyProcessor, HapticEntropyMetrics
from qpis.core.intent_superposition import IntentSuperposition
from qpis.core.measurement_event import MeasurementEvent


@dataclass
class SignalMeshState:
    """
    Current state of the signal mesh.
    
    Attributes:
        timestamp: Current time
        hrv_metrics: Current HRV metrics
        haptic_metrics: Current haptic metrics
        combined_entropy: Combined entropy from all signals
        cognitive_load: Estimated cognitive load (0-1)
        decision_readiness: Readiness to make decision (0-1)
    """
    timestamp: float
    hrv_metrics: Optional[HRVMetrics] = None
    haptic_metrics: Optional[HapticEntropyMetrics] = None
    combined_entropy: float = 0.0
    cognitive_load: float = 0.0
    decision_readiness: float = 0.5


class SignalMesh:
    """
    Neuro-Signal Mesh that integrates multiple entropy sources.
    
    The mesh continuously ingests signals from various sources and computes
    a unified entropy measure that influences intent superposition dynamics.
    """
    
    def __init__(self):
        """Initialize the signal mesh."""
        self.hrv_processor = HRVProcessor()
        self.haptic_processor = HapticEntropyProcessor()
        self.state_history: List[SignalMeshState] = []
        self.current_state: Optional[SignalMeshState] = None
    
    def ingest_hrv_signal(self, ecg_signal: np.ndarray, timestamp: float):
        """
        Ingest and process HRV signal.
        
        Args:
            ecg_signal: Raw ECG signal
            timestamp: Current timestamp
        """
        metrics = self.hrv_processor.process_hrv(ecg_signal)
        
        if self.current_state is None:
            self.current_state = SignalMeshState(timestamp=timestamp)
        
        self.current_state.hrv_metrics = metrics
        self.current_state.timestamp = timestamp
        self._update_combined_metrics()
    
    def ingest_haptic_event(self, event: Any):
        """
        Ingest haptic event.
        
        Args:
            event: Haptic event object
        """
        self.haptic_processor.add_event(event)
        
        if self.current_state is None:
            self.current_state = SignalMeshState(timestamp=event.timestamp)
        
        metrics = self.haptic_processor.process_haptic_entropy()
        self.current_state.haptic_metrics = metrics
        self.current_state.timestamp = event.timestamp
        self._update_combined_metrics()
    
    def _update_combined_metrics(self):
        """Update combined entropy and state metrics."""
        if not self.current_state:
            return
        
        # Combine entropy from different sources
        entropy_components = []
        
        if self.current_state.hrv_metrics:
            # HRV sample entropy normalized
            hrv_entropy = self.current_state.hrv_metrics.sample_entropy / 2.0
            entropy_components.append(hrv_entropy)
        
        if self.current_state.haptic_metrics:
            # Haptic total entropy normalized
            haptic_entropy = self.current_state.haptic_metrics.total_entropy / 3.0
            entropy_components.append(haptic_entropy)
        
        # Combined entropy (weighted average)
        if entropy_components:
            self.current_state.combined_entropy = np.mean(entropy_components)
        
        # Estimate cognitive load
        cognitive_load = 0.5  # Default
        if self.current_state.hrv_metrics:
            hrv_state = self.hrv_processor.extract_cognitive_state(
                self.current_state.hrv_metrics
            )
            cognitive_load = hrv_state["stress_level"]
        
        self.current_state.cognitive_load = cognitive_load
        
        # Estimate decision readiness
        decision_readiness = 0.5  # Default
        
        if self.current_state.hrv_metrics and self.current_state.haptic_metrics:
            # Both signals available
            hrv_state = self.hrv_processor.extract_cognitive_state(
                self.current_state.hrv_metrics
            )
            haptic_influence = self.haptic_processor.extract_intent_influence(
                self.current_state.haptic_metrics
            )
            
            decision_readiness = (
                hrv_state["decision_readiness"] * 0.6 +
                haptic_influence["collapse_readiness"] * 0.4
            )
        elif self.current_state.hrv_metrics:
            hrv_state = self.hrv_processor.extract_cognitive_state(
                self.current_state.hrv_metrics
            )
            decision_readiness = hrv_state["decision_readiness"]
        elif self.current_state.haptic_metrics:
            haptic_influence = self.haptic_processor.extract_intent_influence(
                self.current_state.haptic_metrics
            )
            decision_readiness = haptic_influence["collapse_readiness"]
        
        self.current_state.decision_readiness = decision_readiness
        
        # Save to history
        self.state_history.append(self.current_state)
    
    def get_entropy_influence_on_intent(
        self,
        superposition: IntentSuperposition
    ) -> Dict[str, float]:
        """
        Compute how mesh entropy should influence intent superposition.
        
        Args:
            superposition: Current intent superposition
            
        Returns:
            Dictionary with influence factors
        """
        if not self.current_state:
            return {
                "entropy_factor": 1.0,
                "should_collapse": False,
                "confidence_boost": 0.0
            }
        
        # High combined entropy suggests keeping superposition open
        entropy_factor = np.exp(-self.current_state.combined_entropy)
        
        # Decision readiness suggests collapse
        should_collapse = self.current_state.decision_readiness > 0.7
        
        # Low cognitive load and high readiness = confidence boost
        confidence_boost = (1 - self.current_state.cognitive_load) * \
                          self.current_state.decision_readiness
        
        return {
            "entropy_factor": entropy_factor,
            "should_collapse": should_collapse,
            "confidence_boost": confidence_boost,
            "cognitive_load": self.current_state.cognitive_load
        }
    
    def create_measurement_event(self) -> Optional[MeasurementEvent]:
        """
        Create a measurement event based on current signal mesh state.
        
        Returns:
            MeasurementEvent if conditions met, None otherwise
        """
        if not self.current_state:
            return None
        
        # Create measurement event with confidence from decision readiness
        return MeasurementEvent(
            event_type="signal_mesh",
            confidence=self.current_state.decision_readiness,
            metadata={
                "combined_entropy": self.current_state.combined_entropy,
                "cognitive_load": self.current_state.cognitive_load,
                "has_hrv": self.current_state.hrv_metrics is not None,
                "has_haptic": self.current_state.haptic_metrics is not None
            }
        )
    
    def get_mesh_summary(self) -> Dict:
        """
        Get summary of signal mesh state.
        
        Returns:
            Dictionary with mesh state summary
        """
        if not self.current_state:
            return {"active": False}
        
        return {
            "active": True,
            "combined_entropy": self.current_state.combined_entropy,
            "cognitive_load": self.current_state.cognitive_load,
            "decision_readiness": self.current_state.decision_readiness,
            "history_length": len(self.state_history),
            "has_hrv": self.current_state.hrv_metrics is not None,
            "has_haptic": self.current_state.haptic_metrics is not None
        }
