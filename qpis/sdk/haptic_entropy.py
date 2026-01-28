"""
Haptic Entropy Processor

Processes haptic/touch interaction signals to extract entropy measures
that reflect user intent uncertainty and engagement.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from scipy.stats import entropy


@dataclass
class HapticEvent:
    """
    Represents a single haptic interaction event.
    
    Attributes:
        timestamp: Time of event in seconds
        event_type: Type of haptic event ('press', 'release', 'move', 'vibration')
        pressure: Pressure magnitude (0-1)
        velocity: Movement velocity
        position: 2D position (x, y)
        duration: Event duration in seconds
    """
    timestamp: float
    event_type: str
    pressure: float = 0.0
    velocity: float = 0.0
    position: Optional[Tuple[float, float]] = None
    duration: float = 0.0


@dataclass
class HapticEntropyMetrics:
    """
    Haptic entropy metrics.
    
    Attributes:
        temporal_entropy: Entropy of inter-event intervals
        pressure_entropy: Entropy of pressure distribution
        velocity_entropy: Entropy of velocity distribution
        spatial_entropy: Entropy of spatial distribution
        total_entropy: Combined entropy measure
        hesitation_score: Score indicating decision hesitation
        confidence_score: Estimated user confidence
    """
    temporal_entropy: float
    pressure_entropy: float
    velocity_entropy: float
    spatial_entropy: float
    total_entropy: float
    hesitation_score: float
    confidence_score: float


class HapticEntropyProcessor:
    """
    Processes haptic interaction signals to extract entropy measures.
    
    High haptic entropy suggests uncertainty or exploration, while low entropy
    suggests confident, decisive actions.
    """
    
    def __init__(self, window_size: int = 10):
        """
        Initialize haptic entropy processor.
        
        Args:
            window_size: Number of events in sliding window
        """
        self.window_size = window_size
        self.event_buffer: List[HapticEvent] = []
    
    def add_event(self, event: HapticEvent):
        """Add a haptic event to the buffer."""
        self.event_buffer.append(event)
        
        # Keep only recent events
        if len(self.event_buffer) > self.window_size * 2:
            self.event_buffer = self.event_buffer[-self.window_size * 2:]
    
    def compute_temporal_entropy(self, events: List[HapticEvent]) -> float:
        """
        Compute entropy of inter-event time intervals.
        
        High temporal entropy suggests irregular, uncertain interactions.
        
        Args:
            events: List of haptic events
            
        Returns:
            Temporal entropy value
        """
        if len(events) < 2:
            return 0.0
        
        # Compute inter-event intervals
        timestamps = [e.timestamp for e in events]
        intervals = np.diff(timestamps)
        
        if len(intervals) == 0:
            return 0.0
        
        # Create histogram for entropy calculation
        hist, _ = np.histogram(intervals, bins=min(10, len(intervals)))
        hist = hist / hist.sum()
        
        # Remove zero bins
        hist = hist[hist > 0]
        
        return entropy(hist)
    
    def compute_pressure_entropy(self, events: List[HapticEvent]) -> float:
        """
        Compute entropy of pressure distribution.
        
        Args:
            events: List of haptic events
            
        Returns:
            Pressure entropy value
        """
        if len(events) < 2:
            return 0.0
        
        pressures = np.array([e.pressure for e in events])
        
        # Create histogram
        hist, _ = np.histogram(pressures, bins=min(10, len(pressures)))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        
        return entropy(hist)
    
    def compute_velocity_entropy(self, events: List[HapticEvent]) -> float:
        """
        Compute entropy of velocity distribution.
        
        Args:
            events: List of haptic events
            
        Returns:
            Velocity entropy value
        """
        if len(events) < 2:
            return 0.0
        
        velocities = np.array([e.velocity for e in events])
        
        # Create histogram
        hist, _ = np.histogram(velocities, bins=min(10, len(velocities)))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        
        return entropy(hist)
    
    def compute_spatial_entropy(self, events: List[HapticEvent]) -> float:
        """
        Compute entropy of spatial position distribution.
        
        High spatial entropy suggests exploration or uncertainty about target.
        
        Args:
            events: List of haptic events
            
        Returns:
            Spatial entropy value
        """
        positions = [e.position for e in events if e.position is not None]
        
        if len(positions) < 2:
            return 0.0
        
        # Compute 2D histogram
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        hist, _, _ = np.histogram2d(
            x_coords, y_coords,
            bins=min(5, int(np.sqrt(len(positions))))
        )
        
        hist = hist.flatten()
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        
        return entropy(hist)
    
    def compute_hesitation_score(self, events: List[HapticEvent]) -> float:
        """
        Compute hesitation score based on event patterns.
        
        Hesitation indicators:
        - Multiple press/release cycles in short time
        - Low pressure (tentative touches)
        - Erratic movement patterns
        
        Args:
            events: List of haptic events
            
        Returns:
            Hesitation score (0=confident, 1=highly hesitant)
        """
        if len(events) < 2:
            return 0.0
        
        # Count press/release cycles
        press_release_pairs = 0
        for i in range(len(events) - 1):
            if events[i].event_type == 'press' and events[i + 1].event_type == 'release':
                if events[i + 1].timestamp - events[i].timestamp < 0.5:  # Quick tap
                    press_release_pairs += 1
        
        cycle_score = min(1.0, press_release_pairs / 5)
        
        # Average pressure (low pressure = tentative)
        avg_pressure = np.mean([e.pressure for e in events])
        pressure_score = 1.0 - avg_pressure
        
        # Velocity variation (erratic = uncertain)
        velocities = [e.velocity for e in events]
        velocity_std = np.std(velocities)
        velocity_score = min(1.0, velocity_std / 100)
        
        # Combine scores
        hesitation = (cycle_score + pressure_score + velocity_score) / 3
        
        return hesitation
    
    def process_haptic_entropy(
        self,
        events: Optional[List[HapticEvent]] = None
    ) -> HapticEntropyMetrics:
        """
        Process haptic events and compute comprehensive entropy metrics.
        
        Args:
            events: List of haptic events (uses buffer if None)
            
        Returns:
            HapticEntropyMetrics object
        """
        if events is None:
            events = self.event_buffer[-self.window_size:] if len(self.event_buffer) >= 2 else self.event_buffer
        
        if len(events) < 2:
            return HapticEntropyMetrics(0, 0, 0, 0, 0, 0, 1.0)
        
        # Compute individual entropy measures
        temporal_ent = self.compute_temporal_entropy(events)
        pressure_ent = self.compute_pressure_entropy(events)
        velocity_ent = self.compute_velocity_entropy(events)
        spatial_ent = self.compute_spatial_entropy(events)
        
        # Total entropy as weighted combination
        total_ent = (temporal_ent + pressure_ent + velocity_ent + spatial_ent) / 4
        
        # Compute hesitation score
        hesitation = self.compute_hesitation_score(events)
        
        # Confidence is inverse of entropy and hesitation
        confidence = 1.0 - min(1.0, total_ent / 3 + hesitation) / 2
        
        return HapticEntropyMetrics(
            temporal_entropy=temporal_ent,
            pressure_entropy=pressure_ent,
            velocity_entropy=velocity_ent,
            spatial_entropy=spatial_ent,
            total_entropy=total_ent,
            hesitation_score=hesitation,
            confidence_score=confidence
        )
    
    def extract_intent_influence(self, metrics: HapticEntropyMetrics) -> dict:
        """
        Extract how haptic entropy should influence intent superposition.
        
        High entropy suggests keeping superposition open (don't collapse).
        Low entropy with high confidence suggests readiness for collapse.
        
        Args:
            metrics: Computed haptic entropy metrics
            
        Returns:
            Dictionary with intent influence factors
        """
        return {
            "collapse_readiness": metrics.confidence_score,
            "exploration_factor": metrics.total_entropy / 3,  # Normalized
            "certainty": 1.0 - metrics.hesitation_score,
            "should_wait": metrics.hesitation_score > 0.6 or metrics.total_entropy > 2.0
        }
