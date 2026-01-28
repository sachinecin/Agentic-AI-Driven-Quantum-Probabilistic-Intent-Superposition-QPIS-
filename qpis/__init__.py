"""
QPIS: Quantum-Probabilistic Intent Superposition Framework

An agentic AI framework that maintains intent as a superposition of all logically 
possible outcomes, collapsing into execution through measurement events based on 
probability density functions.

Core Components:
- Recursive Teleological Back-Propagation Engine
- Neuro-Signal Mesh SDK (HRV/Haptic entropy ingestion)
- Measurement Event Logic for intent collapse
- World Models for Latent Intent Synthesis
"""

__version__ = "0.1.0"
__author__ = "QPIS Framework Contributors"

from qpis.core.intent_superposition import IntentSuperposition
from qpis.core.agent_coordinator import AgenticCoordinator
from qpis.engines.teleological.backprop_engine import TeleologicalBackPropEngine
from qpis.measurement.collapse import MeasurementCollapse
from qpis.world_models.latent_synthesis import LatentIntentSynthesizer

__all__ = [
    "IntentSuperposition",
    "AgenticCoordinator",
    "TeleologicalBackPropEngine",
    "MeasurementCollapse",
    "LatentIntentSynthesizer",
]
