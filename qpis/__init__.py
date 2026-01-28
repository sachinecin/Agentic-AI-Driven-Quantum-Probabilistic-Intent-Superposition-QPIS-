"""
QPIS - Quantum-Probabilistic Intent Superposition Framework

This framework implements a novel approach to intent recognition and execution
by maintaining intents as probability superpositions that collapse based on
measurement events and entropy signals.
"""

__version__ = "0.1.0"

from qpis.core.intent_superposition import IntentSuperposition, Intent
from qpis.core.measurement_event import MeasurementEvent, MeasurementCollapse
from qpis.engines.teleological_backprop import TeleologicalEngine
from qpis.world_models.latent_intent_synthesis import LatentIntentSynthesizer

__all__ = [
    "IntentSuperposition",
    "Intent", 
    "MeasurementEvent",
    "MeasurementCollapse",
    "TeleologicalEngine",
    "LatentIntentSynthesizer",
]
