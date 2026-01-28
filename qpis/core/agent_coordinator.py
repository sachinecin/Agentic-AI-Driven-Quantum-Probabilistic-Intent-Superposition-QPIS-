"""
Agentic Coordinator

Manages multiple agents and their intent superpositions in a teleological loop,
coordinating collective behavior and world model updates.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
import numpy as np

from qpis.core.intent_superposition import IntentSuperposition, IntentState

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Represents an agent in the system."""
    
    agent_id: str
    agent_type: str
    superposition: IntentSuperposition
    metadata: Dict[str, Any]
    active: bool = True


class AgenticCoordinator:
    """
    Coordinates multiple agents and their intent superpositions.
    
    Implements high-agency system architecture where agents maintain
    superposed intents and influence each other through teleological loops.
    """
    
    def __init__(self, system_id: str = "qpis_system"):
        """
        Initialize the agentic coordinator.
        
        Args:
            system_id: Unique identifier for this coordination system
        """
        self.system_id = system_id
        self.agents: Dict[str, Agent] = {}
        self.collective_state: Dict[str, Any] = {}
        self.teleological_goals: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized AgenticCoordinator: {system_id}")
    
    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Register a new agent in the coordination system.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type/class of agent
            metadata: Additional agent metadata
            
        Returns:
            The registered Agent object
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered")
            return self.agents[agent_id]
        
        superposition = IntentSuperposition(agent_id)
        agent = Agent(
            agent_id=agent_id,
            agent_type=agent_type,
            superposition=superposition,
            metadata=metadata or {}
        )
        
        self.agents[agent_id] = agent
        logger.info(f"Registered agent {agent_id} of type {agent_type}")
        
        return agent
    
    def deregister_agent(self, agent_id: str):
        """Remove an agent from the system."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Deregistered agent {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        return self.agents.get(agent_id)
    
    def set_teleological_goal(
        self,
        goal_id: str,
        description: str,
        target_state: Dict[str, Any],
        priority: float = 1.0
    ):
        """
        Set a teleological goal for the system.
        
        Teleological goals drive back-propagation of intent through time,
        shaping current behavior based on desired future states.
        
        Args:
            goal_id: Unique goal identifier
            description: Human-readable goal description
            target_state: Desired future state
            priority: Goal priority (0-1)
        """
        goal = {
            "goal_id": goal_id,
            "description": description,
            "target_state": target_state,
            "priority": priority,
            "timestamp": np.datetime64("now")
        }
        
        self.teleological_goals.append(goal)
        logger.info(f"Set teleological goal: {goal_id}")
    
    def coordinate_agents(self, time_step: float = 1.0):
        """
        Coordinate all active agents for one time step.
        
        This performs:
        1. Evolution of each agent's intent superposition
        2. Cross-agent entanglement based on shared goals
        3. Collective state updates
        
        Args:
            time_step: Time delta for evolution
        """
        active_agents = [a for a in self.agents.values() if a.active]
        
        if not active_agents:
            logger.warning("No active agents to coordinate")
            return
        
        logger.debug(f"Coordinating {len(active_agents)} agents")
        
        # Evolve each agent's superposition
        for agent in active_agents:
            agent.superposition.evolve(time_step)
        
        # Check for cross-agent entanglement opportunities
        self._entangle_related_agents(active_agents)
        
        # Update collective state
        self._update_collective_state(active_agents)
    
    def measure_all_agents(
        self,
        measurement_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, IntentState]:
        """
        Perform measurement on all active agents, collapsing superpositions.
        
        Returns:
            Dictionary mapping agent_id to collapsed IntentState
        """
        results = {}
        
        for agent_id, agent in self.agents.items():
            if agent.active and not agent.superposition.collapsed_state:
                collapsed = agent.superposition.measure(context=measurement_context)
                results[agent_id] = collapsed
                logger.info(f"Agent {agent_id} collapsed to: {collapsed.description}")
        
        return results
    
    def reset_all_agents(self):
        """Reset all agent superpositions for a new measurement cycle."""
        for agent in self.agents.values():
            agent.superposition.reset()
        
        logger.info("Reset all agent superpositions")
    
    def get_system_entropy(self) -> float:
        """
        Calculate total system entropy across all agent superpositions.
        
        Higher entropy indicates more uncertainty/possibilities.
        """
        total_entropy = 0.0
        
        for agent in self.agents.values():
            if not agent.active:
                continue
            
            # Shannon entropy of probability distribution
            probs = list(agent.superposition.get_state_probabilities().values())
            if probs:
                probs = np.array(probs)
                probs = probs[probs > 0]  # Filter zeros
                entropy = -np.sum(probs * np.log2(probs))
                total_entropy += entropy
        
        return total_entropy
    
    def get_collective_probability(self, state_pattern: Dict[str, str]) -> float:
        """
        Calculate probability of a collective state across multiple agents.
        
        Args:
            state_pattern: Mapping of agent_id to desired state_id
            
        Returns:
            Joint probability (product of individual probabilities)
        """
        joint_prob = 1.0
        
        for agent_id, state_id in state_pattern.items():
            agent = self.agents.get(agent_id)
            if agent and state_id in agent.superposition.states:
                joint_prob *= agent.superposition.states[state_id].probability
            else:
                return 0.0  # Impossible state
        
        return joint_prob
    
    def _entangle_related_agents(self, agents: List[Agent]):
        """
        Create entanglement between agents with shared goals or related states.
        """
        # Simple entanglement based on agent types
        type_groups = {}
        for agent in agents:
            agent_type = agent.agent_type
            if agent_type not in type_groups:
                type_groups[agent_type] = []
            type_groups[agent_type].append(agent)
        
        # Entangle agents of the same type
        for agent_type, agent_list in type_groups.items():
            if len(agent_list) > 1:
                for i in range(len(agent_list) - 1):
                    agent1 = agent_list[i]
                    agent2 = agent_list[i + 1]
                    
                    # Find matching states and entangle them
                    states1 = set(agent1.superposition.states.keys())
                    states2 = set(agent2.superposition.states.keys())
                    common_states = states1.intersection(states2)
                    
                    for state_id in list(common_states)[:1]:  # Entangle one pair
                        agent1.superposition.entangle_states(state_id, state_id)
    
    def _update_collective_state(self, agents: List[Agent]):
        """Update the collective system state based on agent superpositions."""
        self.collective_state = {
            "total_entropy": self.get_system_entropy(),
            "active_agents": len(agents),
            "total_states": sum(
                len(a.superposition.states) for a in agents
            ),
            "collapsed_agents": sum(
                1 for a in agents if a.superposition.collapsed_state
            )
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the coordination system."""
        return {
            "system_id": self.system_id,
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.active),
            "teleological_goals": len(self.teleological_goals),
            "collective_state": self.collective_state
        }
    
    def __repr__(self) -> str:
        return f"AgenticCoordinator(system={self.system_id}, agents={len(self.agents)})"
