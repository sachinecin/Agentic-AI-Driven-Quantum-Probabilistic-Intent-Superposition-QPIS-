"""
Haptic Feedback Processor

Processes haptic/tactile feedback signals to extract entropy and
interaction patterns for intent inference.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HapticEventType(Enum):
    """Types of haptic events."""
    TAP = "tap"
    PRESS = "press"
    SWIPE = "swipe"
    PINCH = "pinch"
    VIBRATION = "vibration"
    FORCE = "force"


@dataclass
class HapticEvent:
    """Represents a haptic event."""
    
    event_type: HapticEventType
    timestamp: float
    intensity: float  # 0-1
    duration: float  # seconds
    location: Optional[tuple] = None  # (x, y) coordinates
    velocity: Optional[float] = None  # For swipes
    metadata: Dict[str, Any] = None


@dataclass
class HapticMetrics:
    """Metrics extracted from haptic signals."""
    
    event_rate: float  # Events per second
    mean_intensity: float
    intensity_variance: float
    mean_duration: float
    entropy: float
    pattern_complexity: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "event_rate": self.event_rate,
            "mean_intensity": self.mean_intensity,
            "intensity_variance": self.intensity_variance,
            "mean_duration": self.mean_duration,
            "entropy": self.entropy,
            "pattern_complexity": self.pattern_complexity
        }


class HapticProcessor:
    """
    Haptic Feedback Signal Processor
    
    Processes haptic/tactile interaction signals to extract entropy
    and behavioral patterns that reveal user intent.
    
    Haptic patterns can indicate:
    - Interaction certainty/confidence
    - Cognitive load
    - Frustration or engagement
    - Decision-making processes
    - Motor control and attention
    """
    
    def __init__(
        self,
        window_size: float = 5.0  # seconds
    ):
        """
        Initialize haptic processor.
        
        Args:
            window_size: Time window for metric computation
        """
        self.window_size = window_size
        
        self.event_buffer: List[HapticEvent] = []
        self.metrics_history: List[HapticMetrics] = []
        
        logger.info(f"Initialized HapticProcessor (window={window_size}s)")
    
    def ingest_event(
        self,
        event_type: HapticEventType,
        intensity: float,
        duration: float = 0.1,
        location: Optional[tuple] = None,
        velocity: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Ingest a haptic event.
        
        Args:
            event_type: Type of haptic event
            intensity: Event intensity (0-1)
            duration: Event duration in seconds
            location: Optional (x, y) location
            velocity: Optional velocity (for swipes)
            metadata: Additional event data
        """
        event = HapticEvent(
            event_type=event_type,
            timestamp=float(np.datetime64("now").astype(float)),
            intensity=np.clip(intensity, 0, 1),
            duration=duration,
            location=location,
            velocity=velocity,
            metadata=metadata or {}
        )
        
        self.event_buffer.append(event)
        
        # Keep buffer within time window
        self._cleanup_buffer()
        
        logger.debug(f"Ingested haptic event: {event_type.value}")
    
    def compute_metrics(
        self,
        time_window: Optional[float] = None
    ) -> Optional[HapticMetrics]:
        """
        Compute haptic metrics from event buffer.
        
        Args:
            time_window: Time window in seconds (uses default if None)
            
        Returns:
            HapticMetrics object or None if insufficient data
        """
        if len(self.event_buffer) < 2:
            return None
        
        window = time_window or self.window_size
        current_time = float(np.datetime64("now").astype(float))
        cutoff_time = current_time - window
        
        # Filter events in window
        events = [e for e in self.event_buffer if e.timestamp >= cutoff_time]
        
        if len(events) < 2:
            return None
        
        # Compute metrics
        event_rate = len(events) / window
        
        intensities = [e.intensity for e in events]
        mean_intensity = np.mean(intensities)
        intensity_variance = np.var(intensities)
        
        durations = [e.duration for e in events]
        mean_duration = np.mean(durations)
        
        # Compute entropy
        entropy = self._compute_entropy(events)
        
        # Compute pattern complexity
        pattern_complexity = self._compute_pattern_complexity(events)
        
        metrics = HapticMetrics(
            event_rate=event_rate,
            mean_intensity=mean_intensity,
            intensity_variance=intensity_variance,
            mean_duration=mean_duration,
            entropy=entropy,
            pattern_complexity=pattern_complexity
        )
        
        self.metrics_history.append(metrics)
        
        logger.debug(
            f"Computed haptic metrics: rate={event_rate:.2f} evt/s, "
            f"entropy={entropy:.4f}"
        )
        
        return metrics
    
    def extract_intent_features(
        self,
        metrics: Optional[HapticMetrics] = None
    ) -> np.ndarray:
        """
        Extract intent-relevant features from haptic metrics.
        
        Args:
            metrics: Haptic metrics (computes from buffer if None)
            
        Returns:
            Feature vector for intent synthesis
        """
        if metrics is None:
            metrics = self.compute_metrics()
        
        if metrics is None:
            return np.zeros(6)
        
        # Normalize features
        features = np.array([
            np.clip(metrics.event_rate / 10.0, 0, 1),  # Normalize rate
            metrics.mean_intensity,  # Already [0, 1]
            np.clip(metrics.intensity_variance, 0, 1),
            np.clip(metrics.mean_duration, 0, 1),
            metrics.entropy,  # Already [0, 1]
            metrics.pattern_complexity  # Already [0, 1]
        ])
        
        return features
    
    def get_interaction_confidence(
        self,
        metrics: Optional[HapticMetrics] = None
    ) -> float:
        """
        Estimate user confidence from haptic patterns.
        
        Confident interactions: quick, consistent intensity
        Uncertain interactions: variable, hesitant patterns
        
        Returns:
            Confidence level (0-1)
        """
        if metrics is None:
            metrics = self.compute_metrics()
        
        if metrics is None:
            return 0.5  # Neutral
        
        # High confidence: high intensity, low variance, low entropy
        intensity_component = metrics.mean_intensity
        consistency_component = 1.0 - metrics.intensity_variance
        decisiveness_component = 1.0 - metrics.entropy
        
        confidence = (
            intensity_component * 0.4 +
            consistency_component * 0.3 +
            decisiveness_component * 0.3
        )
        
        return float(np.clip(confidence, 0, 1))
    
    def detect_pattern(
        self,
        pattern_name: str
    ) -> bool:
        """
        Detect specific interaction patterns.
        
        Args:
            pattern_name: Name of pattern to detect
            
        Returns:
            True if pattern detected
        """
        if len(self.event_buffer) < 3:
            return False
        
        recent_events = self.event_buffer[-10:]
        
        if pattern_name == "rapid_taps":
            # Rapid succession of tap events
            taps = [e for e in recent_events if e.event_type == HapticEventType.TAP]
            if len(taps) >= 3:
                time_diff = taps[-1].timestamp - taps[0].timestamp
                if time_diff < 1.0:  # Within 1 second
                    return True
        
        elif pattern_name == "hesitation":
            # Long duration or repeated events on same location
            if len(recent_events) >= 2:
                last_event = recent_events[-1]
                if last_event.duration > 1.0:  # Long press
                    return True
        
        elif pattern_name == "exploration":
            # Diverse event types and locations
            event_types = set(e.event_type for e in recent_events)
            if len(event_types) >= 3:
                return True
        
        return False
    
    def _compute_entropy(self, events: List[HapticEvent]) -> float:
        """
        Compute entropy of haptic event distribution.
        
        Returns:
            Normalized entropy (0-1)
        """
        if len(events) < 2:
            return 0.0
        
        # Event type distribution
        type_counts = {}
        for event in events:
            event_type = event.event_type.value
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        # Probability distribution
        total = sum(type_counts.values())
        probs = np.array([count / total for count in type_counts.values()])
        
        # Shannon entropy
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        
        # Normalize
        max_entropy = np.log2(len(HapticEventType))
        normalized_entropy = entropy / max_entropy
        
        return float(normalized_entropy)
    
    def _compute_pattern_complexity(
        self,
        events: List[HapticEvent]
    ) -> float:
        """
        Compute complexity of interaction pattern.
        
        Returns:
            Complexity score (0-1)
        """
        if len(events) < 2:
            return 0.0
        
        # Factors contributing to complexity:
        # 1. Variety of event types
        # 2. Variation in intensity
        # 3. Variation in timing
        
        # Event type variety
        event_types = set(e.event_type for e in events)
        type_variety = len(event_types) / len(HapticEventType)
        
        # Intensity variation
        intensities = [e.intensity for e in events]
        intensity_variation = np.std(intensities)
        
        # Timing variation (inter-event intervals)
        timestamps = [e.timestamp for e in events]
        intervals = np.diff(timestamps)
        if len(intervals) > 0:
            timing_variation = np.std(intervals) / (np.mean(intervals) + 1e-6)
            timing_variation = np.clip(timing_variation, 0, 1)
        else:
            timing_variation = 0.0
        
        # Combined complexity
        complexity = (
            type_variety * 0.4 +
            intensity_variation * 0.3 +
            timing_variation * 0.3
        )
        
        return float(np.clip(complexity, 0, 1))
    
    def _cleanup_buffer(self):
        """Remove old events outside the time window."""
        current_time = float(np.datetime64("now").astype(float))
        cutoff_time = current_time - self.window_size * 2  # Keep 2x window
        
        self.event_buffer = [
            e for e in self.event_buffer
            if e.timestamp >= cutoff_time
        ]
    
    def reset(self):
        """Reset processor state."""
        self.event_buffer.clear()
        logger.debug("Reset haptic processor")
