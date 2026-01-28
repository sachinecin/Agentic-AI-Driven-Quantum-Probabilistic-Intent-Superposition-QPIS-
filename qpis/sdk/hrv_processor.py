"""
Heart Rate Variability (HRV) Processor

Processes HRV signals to extract entropy and physiological state information
that influences intent superpositions.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
from scipy import signal
from scipy.stats import entropy


@dataclass
class HRVMetrics:
    """
    Heart Rate Variability metrics.
    
    Attributes:
        mean_rr: Mean RR interval (ms)
        sdnn: Standard deviation of NN intervals
        rmssd: Root mean square of successive differences
        pnn50: Percentage of successive RR intervals differing by >50ms
        lf_power: Low frequency power (sympathetic)
        hf_power: High frequency power (parasympathetic)
        lf_hf_ratio: LF/HF ratio (autonomic balance)
        sample_entropy: Sample entropy of RR intervals
    """
    mean_rr: float
    sdnn: float
    rmssd: float
    pnn50: float
    lf_power: float
    hf_power: float
    lf_hf_ratio: float
    sample_entropy: float


class HRVProcessor:
    """
    Processes Heart Rate Variability signals for entropy extraction.
    
    HRV provides insight into autonomic nervous system state and cognitive load,
    which can influence intent formation and decision-making.
    """
    
    def __init__(self, sampling_rate: float = 1000.0):
        """
        Initialize HRV processor.
        
        Args:
            sampling_rate: Sampling rate of input signal in Hz
        """
        self.sampling_rate = sampling_rate
        self.rr_intervals: List[float] = []
    
    def detect_r_peaks(self, ecg_signal: np.ndarray) -> np.ndarray:
        """
        Detect R-peaks in ECG signal.
        
        Args:
            ecg_signal: Raw ECG signal
            
        Returns:
            Array of R-peak indices
        """
        # Simple peak detection using scipy
        # In production, use more sophisticated algorithm like Pan-Tompkins
        peaks, _ = signal.find_peaks(
            ecg_signal,
            height=np.mean(ecg_signal) + 0.5 * np.std(ecg_signal),
            distance=int(0.6 * self.sampling_rate)  # Min 600ms between beats
        )
        return peaks
    
    def compute_rr_intervals(self, r_peaks: np.ndarray) -> np.ndarray:
        """
        Compute RR intervals from R-peak locations.
        
        Args:
            r_peaks: Array of R-peak indices
            
        Returns:
            Array of RR intervals in milliseconds
        """
        if len(r_peaks) < 2:
            return np.array([])
        
        # Convert to milliseconds
        rr_intervals = np.diff(r_peaks) / self.sampling_rate * 1000
        self.rr_intervals.extend(rr_intervals.tolist())
        
        return rr_intervals
    
    def compute_time_domain_metrics(self, rr_intervals: np.ndarray) -> Tuple[float, float, float, float]:
        """
        Compute time-domain HRV metrics.
        
        Args:
            rr_intervals: Array of RR intervals in ms
            
        Returns:
            Tuple of (mean_rr, sdnn, rmssd, pnn50)
        """
        if len(rr_intervals) < 2:
            return 0.0, 0.0, 0.0, 0.0
        
        mean_rr = np.mean(rr_intervals)
        sdnn = np.std(rr_intervals, ddof=1)
        
        # RMSSD: root mean square of successive differences
        successive_diffs = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(successive_diffs ** 2))
        
        # pNN50: percentage of successive diffs > 50ms
        pnn50 = np.sum(np.abs(successive_diffs) > 50) / len(successive_diffs) * 100
        
        return mean_rr, sdnn, rmssd, pnn50
    
    def compute_frequency_domain_metrics(
        self,
        rr_intervals: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Compute frequency-domain HRV metrics using FFT.
        
        Args:
            rr_intervals: Array of RR intervals in ms
            
        Returns:
            Tuple of (lf_power, hf_power, lf_hf_ratio)
        """
        if len(rr_intervals) < 10:
            return 0.0, 0.0, 0.0
        
        # Interpolate to uniform time series (4 Hz)
        time_original = np.cumsum(rr_intervals) / 1000  # Convert to seconds
        time_uniform = np.arange(0, time_original[-1], 0.25)
        rr_uniform = np.interp(time_uniform, time_original[:-1], rr_intervals[:-1])
        
        # Compute power spectral density
        freqs, psd = signal.welch(rr_uniform, fs=4.0, nperseg=min(256, len(rr_uniform)))
        
        # LF: 0.04-0.15 Hz (sympathetic + parasympathetic)
        lf_mask = (freqs >= 0.04) & (freqs < 0.15)
        lf_power = np.trapz(psd[lf_mask], freqs[lf_mask])
        
        # HF: 0.15-0.4 Hz (parasympathetic)
        hf_mask = (freqs >= 0.15) & (freqs < 0.4)
        hf_power = np.trapz(psd[hf_mask], freqs[hf_mask])
        
        # LF/HF ratio (autonomic balance)
        lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0.0
        
        return lf_power, hf_power, lf_hf_ratio
    
    def compute_sample_entropy(self, rr_intervals: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """
        Compute sample entropy of RR intervals.
        
        Sample entropy measures signal complexity/regularity.
        
        Args:
            rr_intervals: Array of RR intervals
            m: Embedding dimension
            r: Tolerance (fraction of std dev)
            
        Returns:
            Sample entropy value
        """
        if len(rr_intervals) < 10:
            return 0.0
        
        # Normalize
        rr_norm = (rr_intervals - np.mean(rr_intervals)) / np.std(rr_intervals)
        
        n = len(rr_norm)
        tolerance = r * np.std(rr_norm)
        
        # Count template matches
        def _maxdist(xi, xj):
            return max(abs(xi - xj))
        
        def _phi(m_val):
            patterns = np.array([rr_norm[i:i+m_val] for i in range(n - m_val)])
            count = 0
            for i in range(len(patterns)):
                for j in range(len(patterns)):
                    if i != j and _maxdist(patterns[i], patterns[j]) <= tolerance:
                        count += 1
            return count / (n - m_val)
        
        phi_m = _phi(m)
        phi_m1 = _phi(m + 1)
        
        if phi_m > 0 and phi_m1 > 0:
            return -np.log(phi_m1 / phi_m)
        return 0.0
    
    def process_hrv(self, ecg_signal: np.ndarray) -> HRVMetrics:
        """
        Process ECG signal and extract complete HRV metrics.
        
        Args:
            ecg_signal: Raw ECG signal
            
        Returns:
            HRVMetrics object with all metrics
        """
        # Detect R-peaks and compute RR intervals
        r_peaks = self.detect_r_peaks(ecg_signal)
        rr_intervals = self.compute_rr_intervals(r_peaks)
        
        if len(rr_intervals) < 2:
            # Return zero metrics if insufficient data
            return HRVMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        # Compute time-domain metrics
        mean_rr, sdnn, rmssd, pnn50 = self.compute_time_domain_metrics(rr_intervals)
        
        # Compute frequency-domain metrics
        lf_power, hf_power, lf_hf_ratio = self.compute_frequency_domain_metrics(rr_intervals)
        
        # Compute entropy
        sample_ent = self.compute_sample_entropy(rr_intervals)
        
        return HRVMetrics(
            mean_rr=mean_rr,
            sdnn=sdnn,
            rmssd=rmssd,
            pnn50=pnn50,
            lf_power=lf_power,
            hf_power=hf_power,
            lf_hf_ratio=lf_hf_ratio,
            sample_entropy=sample_ent
        )
    
    def extract_cognitive_state(self, metrics: HRVMetrics) -> dict:
        """
        Extract cognitive/emotional state indicators from HRV metrics.
        
        Args:
            metrics: Computed HRV metrics
            
        Returns:
            Dictionary with state indicators
        """
        # High LF/HF ratio suggests stress/cognitive load
        stress_level = np.clip(metrics.lf_hf_ratio / 5.0, 0, 1)
        
        # Low RMSSD suggests reduced parasympathetic activity
        relaxation = np.clip(metrics.rmssd / 50.0, 0, 1)
        
        # High sample entropy suggests complexity/arousal
        arousal = np.clip(metrics.sample_entropy / 2.0, 0, 1)
        
        # SDNN reflects overall HRV
        autonomic_balance = np.clip(metrics.sdnn / 50.0, 0, 1)
        
        return {
            "stress_level": stress_level,
            "relaxation": relaxation,
            "arousal": arousal,
            "autonomic_balance": autonomic_balance,
            "decision_readiness": (1 - stress_level) * autonomic_balance
        }
