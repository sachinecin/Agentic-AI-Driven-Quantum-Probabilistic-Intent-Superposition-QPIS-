"""
Multi-Agent Coordination Example

Demonstrates coordinating multiple agents with intent superpositions
in a teleological loop.
"""

import numpy as np
from qpis import AgenticCoordinator
from qpis.measurement import MeasurementCollapse, MeasurementType


def main():
    print("=" * 60)
    print("QPIS Framework - Multi-Agent Coordination")
    print("=" * 60)
    
    # Create coordinator
    coordinator = AgenticCoordinator(system_id="collaborative_system")
    
    # Register multiple agents
    print("\n1. Registering Agents...")
    agent1 = coordinator.register_agent(
        agent_id="agent_001",
        agent_type="decision_maker",
        metadata={"role": "primary", "expertise": "strategy"}
    )
    
    agent2 = coordinator.register_agent(
        agent_id="agent_002",
        agent_type="decision_maker",
        metadata={"role": "support", "expertise": "analysis"}
    )
    
    agent3 = coordinator.register_agent(
        agent_id="agent_003",
        agent_type="observer",
        metadata={"role": "monitor", "expertise": "patterns"}
    )
    
    print(f"   Registered {len(coordinator.agents)} agents")
    
    # Add intent states to agents
    print("\n2. Initializing Intent States...")
    for agent in [agent1, agent2, agent3]:
        agent.superposition.add_state(
            state_id="collaborate",
            description="Agent collaborates with others",
            amplitude=0.5+0.1j,
            parameters={"engagement": 0.8}
        )
        
        agent.superposition.add_state(
            state_id="independent",
            description="Agent acts independently",
            amplitude=0.4+0.15j,
            parameters={"engagement": 0.6}
        )
        
        agent.superposition.add_state(
            state_id="observe",
            description="Agent observes without action",
            amplitude=0.3+0.05j,
            parameters={"engagement": 0.3}
        )
    
    # Set teleological goal
    print("\n3. Setting Teleological Goal...")
    coordinator.set_teleological_goal(
        goal_id="team_success",
        description="Achieve collaborative success",
        target_state={"collaboration_index": 0.9, "efficiency": 0.85},
        priority=1.0
    )
    
    print(f"   Goal: {coordinator.teleological_goals[0]['description']}")
    
    # Coordinate agents through multiple time steps
    print("\n4. Running Coordination Loop...")
    for step in range(5):
        print(f"\n   Time Step {step + 1}:")
        
        # Coordinate
        coordinator.coordinate_agents(time_step=1.0)
        
        # Get system entropy
        entropy = coordinator.get_system_entropy()
        print(f"      System entropy: {entropy:.4f}")
        
        # Show dominant states
        for agent_id in ["agent_001", "agent_002"]:
            agent = coordinator.get_agent(agent_id)
            dominant = agent.superposition.get_dominant_state()
            if dominant:
                print(f"      {agent_id} dominant: {dominant.description} (P={dominant.probability:.3f})")
    
    # Perform collective measurement
    print("\n5. Performing Collective Measurement...")
    collapse_handler = MeasurementCollapse()
    
    results = {}
    for agent_id, agent in coordinator.agents.items():
        collapsed = collapse_handler.measure(
            agent.superposition,
            measurement_type=MeasurementType.OBSERVATION,
            context={"collective": True}
        )
        results[agent_id] = collapsed
    
    print(f"   Measurement Results:")
    for agent_id, state in results.items():
        print(f"      {agent_id}: {state.description} (P={state.probability:.3f})")
    
    # Analyze collective probability
    print("\n6. Collective State Analysis...")
    pattern = {
        "agent_001": "collaborate",
        "agent_002": "collaborate",
        "agent_003": "observe"
    }
    
    collective_prob = coordinator.get_collective_probability(pattern)
    print(f"   Probability of collaborative pattern: {collective_prob:.4f}")
    
    # System status
    print("\n7. System Status:")
    status = coordinator.get_status()
    print(f"   Total agents: {status['total_agents']}")
    print(f"   Active agents: {status['active_agents']}")
    print(f"   Teleological goals: {status['teleological_goals']}")
    print(f"   Collective state: {status['collective_state']}")
    
    print("\n" + "=" * 60)
    print("Multi-agent example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
