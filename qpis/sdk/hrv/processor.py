"""
HRV (Heart Rate Variability) Processor

Processes heart rate variability signals to extract entropy and
intent-relevant features for the QPIS framework.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from scipy import signal
import logging

logger = logging.getLogger(__name__)


@dataclass
class HRVMetrics:
    """Heart Rate Variability metrics."""
    
    mean_hr: float  # Mean heart rate (BPM)
    sdnn: float  # Standard deviation of NN intervals
    rmssd: float  # Root mean square of successive differences
    pnn50: float  # Percentage of successive NN intervals > 50ms
    lf_power: float  # Low frequency power
    hf_power: float  # High frequency power
    lf_hf_ratio: float  # LF/HF ratio
    entropy: float  # Signal entropy
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "mean_hr": self.mean_hr,
            "sdnn": self.sdnn,
            "rmssd": self.rmssd,
            "pnn50": self.pnn50,
            "lf_power": self.lf_power,
            "hf_power": self.hf_power,
            "lf_hf_ratio": self.lf_hf_ratio,
            "entropy": self.entropy
        }


class HRVProcessor:
    """
    Heart Rate Variability Signal Processor
    
    Ingests and processes HRV signals to extract entropy and
    physiological features that indicate cognitive/emotional state
    and intent.
    
    HRV entropy can serve as a biomarker for:
    - Cognitive load
    - Emotional arousal
    - Decision-making state
    - Attention and focus
    """
    
    def __init__(
        self,
        sampling_rate: float = 1000.0,  # Hz
        window_size: int = 300  # samples
    ):
        """
        Initialize HRV processor.
        
        Args:
            sampling_rate: Sampling rate in Hz
            window_size: Window size for analysis
        """
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        
        self.signal_buffer: List[float] = []
        self.rr_intervals: List[float] = []
        self.metrics_history: List[HRVMetrics] = []
        
        logger.info(
            f"Initialized HRVProcessor "
            f"(rate={sampling_rate}Hz, window={window_size})"
        )
    
    def ingest_signal(self, signal_data: np.ndarray):
        """
        Ingest raw physiological signal data.
        
        Args:
            signal_data: Raw signal samples
        """
        self.signal_buffer.extend(signal_data.tolist())
        
        # Keep buffer at reasonable size
        if len(self.signal_buffer) > self.window_size * 10:
            self.signal_buffer = self.signal_buffer[-self.window_size * 5:]
        
        logger.debug(f"Ingested {len(signal_data)} signal samples")
    
    def detect_heartbeats(
        self,
        signal_data: Optional[np.ndarray] = None
    ) -> List[int]:
        """
        Detect heartbeat peaks in signal.
        
        Args:
            signal_data: Signal to process (uses buffer if None)
            
        Returns:
            List of peak indices
        """
        if signal_data is None:
            if len(self.signal_buffer) < 10:
                return []
            signal_data = np.array(self.signal_buffer[-self.window_size:])
        
        # Simple peak detection
        # In production, use more sophisticated algorithms (Pan-Tompkins, etc.)
        peaks, _ = signal.find_peaks(
            signal_data,
            distance=int(0.5 * self.sampling_rate),  # Min 0.5s between peaks
            prominence=0.5 * np.std(signal_data)
        )
        
        logger.debug(f"Detected {len(peaks)} heartbeats")
        
        return peaks.tolist()
    
    def compute_rr_intervals(
        self,
        peak_indices: List[int]
    ) -> np.ndarray:
        """
        Compute RR intervals from peak indices.
        
        Args:
            peak_indices: Indices of heartbeat peaks
            
        Returns:
            Array of RR intervals in milliseconds
        """
        if len(peak_indices) < 2:
            return np.array([])
        
        # Compute differences
        rr_intervals = np.diff(peak_indices) / self.sampling_rate * 1000  # Convert to ms
        
        # Filter physiologically plausible intervals (300-2000 ms)
        valid_mask = (rr_intervals >= 300) & (rr_intervals <= 2000)
        rr_intervals = rr_intervals[valid_mask]
        
        self.rr_intervals.extend(rr_intervals.tolist())
        
        return rr_intervals
    
    def compute_metrics(
        self,
        rr_intervals: Optional[np.ndarray] = None
    ) -> Optional[HRVMetrics]:
        """
        Compute HRV metrics from RR intervals.
        
        Args:
            rr_intervals: RR intervals in ms (uses buffer if None)
            
        Returns:
            HRVMetrics object or None if insufficient data
        """
        if rr_intervals is None:
            if len(self.rr_intervals) < 10:
                return None
            rr_intervals = np.array(self.rr_intervals[-100:])
        
        if len(rr_intervals) < 5:
            return None
        
        # Time domain metrics
        mean_hr = 60000.0 / np.mean(rr_intervals)  # BPM
        sdnn = np.std(rr_intervals)
        
        # RMSSD: root mean square of successive differences
        diff_rr = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(diff_rr ** 2))
        
        # pNN50: percentage of successive differences > 50ms
        pnn50 = np.sum(np.abs(diff_rr) > 50) / len(diff_rr) * 100
        
        # Frequency domain metrics (simplified)
        lf_power, hf_power = self._compute_frequency_metrics(rr_intervals)
        lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0.0
        
        # Entropy
        entropy = self._compute_entropy(rr_intervals)
        
        metrics = HRVMetrics(
            mean_hr=mean_hr,
            sdnn=sdnn,
            rmssd=rmssd,
            pnn50=pnn50,
            lf_power=lf_power,
            hf_power=hf_power,
            lf_hf_ratio=lf_hf_ratio,
            entropy=entropy
        )
        
        self.metrics_history.append(metrics)
        
        logger.debug(f"Computed HRV metrics: HR={mean_hr:.1f} BPM, entropy={entropy:.4f}")
        
        return metrics
    
    def extract_intent_features(
        self,
        metrics: Optional[HRVMetrics] = None
    ) -> np.ndarray:
        """
        Extract intent-relevant features from HRV metrics.
        
        Args:
            metrics: HRV metrics (computes from buffer if None)
            
        Returns:
            Feature vector for intent synthesis
        """
        if metrics is None:
            metrics = self.compute_metrics()
        
        if metrics is None:
            return np.zeros(8)
        
        # Normalize features to [0, 1] range
        features = np.array([
            metrics.mean_hr / 200.0,  # Normalize HR
            metrics.sdnn / 200.0,  # Normalize SDNN
            metrics.rmssd / 200.0,  # Normalize RMSSD
            metrics.pnn50 / 100.0,  # Already percentage
            metrics.lf_power / 10000.0,  # Normalize power
            metrics.hf_power / 10000.0,
            metrics.lf_hf_ratio / 10.0,  # Normalize ratio
            metrics.entropy  # Already [0, 1]
        ])
        
        return features
    
    def get_arousal_level(self, metrics: Optional[HRVMetrics] = None) -> float:
        """
        Estimate arousal level from HRV.
        
        Higher arousal -> higher HR, lower HRV
        
        Returns:
            Arousal level (0-1)
        """
        if metrics is None:
            metrics = self.compute_metrics()
        
        if metrics is None:
            return 0.5  # Neutral
        
        # High HR and low RMSSD indicate high arousal
        hr_component = (metrics.mean_hr - 60) / 80  # Normalize around resting HR
        hrv_component = 1.0 - (metrics.rmssd / 100.0)  # Lower HRV = higher arousal
        
        arousal = (hr_component + hrv_component) / 2
        arousal = np.clip(arousal, 0, 1)
        
        return float(arousal)
    
    def _compute_frequency_metrics(
        self,
        rr_intervals: np.ndarray
    ) -> Tuple[float, float]:
        """
        Compute frequency domain metrics (LF and HF power).
        
        Returns:
            (lf_power, hf_power) tuple
        """
        if len(rr_intervals) < 10:
            return 0.0, 0.0
        
        # Interpolate to uniform sampling
        time_points = np.cumsum(rr_intervals) / 1000.0  # Convert to seconds
        uniform_time = np.arange(0, time_points[-1], 1.0)  # 1 Hz sampling
        
        if len(uniform_time) < 10:
            return 0.0, 0.0
        
        uniform_rr = np.interp(uniform_time, time_points, rr_intervals)
        
        # Compute power spectral density
        freqs, psd = signal.periodogram(uniform_rr, fs=1.0)
        
        # LF band: 0.04-0.15 Hz, HF band: 0.15-0.4 Hz
        lf_mask = (freqs >= 0.04) & (freqs < 0.15)
        hf_mask = (freqs >= 0.15) & (freqs < 0.4)
        
        lf_power = np.sum(psd[lf_mask])
        hf_power = np.sum(psd[hf_mask])
        
        return float(lf_power), float(hf_power)
    
    def _compute_entropy(self, rr_intervals: np.ndarray) -> float:
        """
        Compute entropy of RR interval distribution.
        
        Returns:
            Normalized entropy (0-1)
        """
        if len(rr_intervals) < 5:
            return 0.0
        
        # Histogram-based entropy
        hist, _ = np.histogram(rr_intervals, bins=20, density=True)
        hist = hist[hist > 0]  # Remove zeros
        
        if len(hist) == 0:
            return 0.0
        
        # Shannon entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        
        # Normalize to [0, 1]
        max_entropy = np.log2(20)  # Maximum entropy for 20 bins
        normalized_entropy = entropy / max_entropy
        
        return float(normalized_entropy)
    
    def reset(self):
        """Reset processor state."""
        self.signal_buffer.clear()
        self.rr_intervals.clear()
        logger.debug("Reset HRV processor")
