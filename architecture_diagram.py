#!/usr/bin/env python3
"""
QPIS Architecture Diagram Generator
Generates a comprehensive architecture diagram for the Quantum-Probabilistic Intent Superposition system
"""

from graphviz import Digraph
import os

def generate_qpis_architecture():
    """Generate the QPIS architecture diagram"""
    
    # Create a new directed graph
    dot = Digraph(comment='QPIS Architecture', format='png')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='1.2')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue', 
             fontname='Arial', fontsize='10')
    
    # Title
    dot.attr(label='Quantum-Probabilistic Intent Superposition (QPIS) Architecture', 
             fontsize='16', fontname='Arial Bold', labelloc='t')
    
    # Input Layer
    with dot.subgraph(name='cluster_input') as c:
        c.attr(label='Input Layer', style='filled', color='lightgrey', fontsize='12')
        c.node('user_actions', 'User Actions\n(Digital Micro-Gestures)', fillcolor='#E8F4F8')
        c.node('physiological', 'Physiological Signals\n(HRV, Haptics)', fillcolor='#E8F4F8')
        c.node('environmental', 'Environmental Context\n(Digital State)', fillcolor='#E8F4F8')
    
    # Intention Entanglement Layer
    with dot.subgraph(name='cluster_entanglement') as c:
        c.attr(label='Intention Entanglement Layer', style='filled', color='lightgrey', fontsize='12')
        c.node('entropy_analyzer', 'Physiological Entropy\nAnalyzer', fillcolor='#D4E6F1')
        c.node('cognitive_load', 'Cognitive Load\nEstimator', fillcolor='#D4E6F1')
        c.node('entanglement_core', 'Entanglement Core\n(User ⊗ Environment)', fillcolor='#A9CCE3')
    
    # Superposition State Management
    with dot.subgraph(name='cluster_superposition') as c:
        c.attr(label='Intent Superposition Management', style='filled', color='lightgrey', fontsize='12')
        c.node('intent_states', 'Intent State\nSuperposition\n|Ψ⟩ = Σ αᵢ|iᵢ⟩', fillcolor='#F9E79F')
        c.node('probability_calc', 'Probability\nDensity Calculator', fillcolor='#F9E79F')
        c.node('goal_simulator', 'Multi-Goal State\nSimulator', fillcolor='#F9E79F')
    
    # Recursive Teleological Back-Propagation
    with dot.subgraph(name='cluster_backprop') as c:
        c.attr(label='Recursive Teleological Back-Propagation', style='filled', color='lightgrey', fontsize='12')
        c.node('goal_states', 'Future Goal States\nGenerator', fillcolor='#ABEBC6')
        c.node('backflow', 'Probability\nBack-Flow Engine', fillcolor='#ABEBC6')
        c.node('gradient_calc', 'Teleological\nGradient Calculator', fillcolor='#ABEBC6')
    
    # Neuro-Signal Mesh
    with dot.subgraph(name='cluster_neurosignal') as c:
        c.attr(label='Neuro-Signal Mesh', style='filled', color='lightgrey', fontsize='12')
        c.node('signal_mesh', 'Signal Mesh\nProcessor', fillcolor='#F5B7B1')
        c.node('stress_detector', 'Cognitive Stress\nDetector', fillcolor='#F5B7B1')
        c.node('priority_engine', 'Intent Priority\nEngine', fillcolor='#F5B7B1')
    
    # Measurement & Collapse Layer
    with dot.subgraph(name='cluster_measurement') as c:
        c.attr(label='Measurement & Collapse Layer', style='filled', color='lightgrey', fontsize='12')
        c.node('teleological_trigger', 'Teleological\nTrigger Detector', fillcolor='#D7BDE2')
        c.node('collapse_engine', 'Superposition\nCollapse Engine', fillcolor='#D7BDE2')
        c.node('measurement_event', 'Measurement Event\n(P(Gᵢ) > θ)', fillcolor='#D7BDE2')
    
    # Execution Layer
    with dot.subgraph(name='cluster_execution') as c:
        c.attr(label='Autonomous Execution Layer', style='filled', color='lightgrey', fontsize='12')
        c.node('action_selector', 'Optimal Action\nSelector', fillcolor='#C5E1A5')
        c.node('executor', 'Autonomous\nExecutor', fillcolor='#C5E1A5')
        c.node('feedback_loop', 'Feedback Loop\n& Adaptation', fillcolor='#C5E1A5')
    
    # Connections - Input to Entanglement
    dot.edge('user_actions', 'entanglement_core', label='digital signals')
    dot.edge('physiological', 'entropy_analyzer', label='bio signals')
    dot.edge('environmental', 'entanglement_core', label='context')
    dot.edge('entropy_analyzer', 'cognitive_load')
    dot.edge('cognitive_load', 'entanglement_core', label='energy of intent')
    
    # Entanglement to Superposition
    dot.edge('entanglement_core', 'intent_states', label='entangled state')
    dot.edge('intent_states', 'probability_calc')
    dot.edge('probability_calc', 'goal_simulator')
    
    # Superposition to Back-Propagation
    dot.edge('goal_simulator', 'goal_states', label='possible futures')
    dot.edge('goal_states', 'backflow')
    dot.edge('backflow', 'gradient_calc')
    dot.edge('gradient_calc', 'intent_states', label='update probabilities', style='dashed', color='blue')
    
    # Neuro-Signal Mesh connections
    dot.edge('physiological', 'signal_mesh')
    dot.edge('user_actions', 'signal_mesh')
    dot.edge('signal_mesh', 'stress_detector')
    dot.edge('stress_detector', 'priority_engine')
    dot.edge('priority_engine', 'intent_states', label='priority weights')
    
    # Measurement connections
    dot.edge('intent_states', 'measurement_event', label='probability density')
    dot.edge('probability_calc', 'measurement_event')
    dot.edge('entropy_analyzer', 'teleological_trigger', label='entropy drop')
    dot.edge('measurement_event', 'teleological_trigger')
    dot.edge('teleological_trigger', 'collapse_engine', label='trigger fired')
    dot.edge('collapse_engine', 'action_selector', label='collapsed intent')
    
    # Execution
    dot.edge('action_selector', 'executor')
    dot.edge('executor', 'feedback_loop')
    dot.edge('feedback_loop', 'entanglement_core', label='state update', style='dashed', color='red')
    
    return dot

def main():
    """Generate and save the architecture diagram"""
    print("Generating QPIS Architecture Diagram...")
    
    # Generate the diagram
    dot = generate_qpis_architecture()
    
    # Save the diagram
    output_path = 'qpis_architecture'
    dot.render(output_path, cleanup=True)
    
    print(f"✓ Architecture diagram generated: {output_path}.png")
    print("✓ Diagram saved successfully!")
    
    # Also save the DOT source
    with open(f'{output_path}.dot', 'w') as f:
        f.write(dot.source)
    print(f"✓ DOT source saved: {output_path}.dot")

if __name__ == '__main__':
    main()
