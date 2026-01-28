"""
Neuro-Signal Mesh SDK

SDK for ingesting and processing biological entropy signals including
Heart Rate Variability (HRV) and haptic feedback for intent inference.
"""

from qpis.sdk.hrv.processor import HRVProcessor
from qpis.sdk.haptic.processor import HapticProcessor
from qpis.sdk.mesh.coordinator import SignalMeshCoordinator

__all__ = ["HRVProcessor", "HapticProcessor", "SignalMeshCoordinator"]
