//! Recursive Teleological Back-Propagation Engine (Rust Implementation)
//!
//! High-performance implementation of recursive back-propagation for
//! teleological goal-directed intent evolution.

use nalgebra::{DVector, DMatrix};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Represents an intent with probability amplitude
#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RustIntent {
    #[pyo3(get, set)]
    pub label: String,
    
    #[pyo3(get, set)]
    pub probability: f64,
    
    #[pyo3(get, set)]
    pub teleological_weight: f64,
}

#[pymethods]
impl RustIntent {
    #[new]
    fn new(label: String, probability: f64, teleological_weight: f64) -> Self {
        RustIntent {
            label,
            probability,
            teleological_weight,
        }
    }
}

/// Teleological state at a point in time
#[pyclass]
#[derive(Clone, Debug)]
pub struct TeleologicalStateRust {
    #[pyo3(get)]
    pub timestamp: f64,
    
    #[pyo3(get)]
    pub intents: Vec<RustIntent>,
    
    #[pyo3(get)]
    pub entropy: f64,
    
    #[pyo3(get)]
    pub goal_alignment: f64,
}

#[pymethods]
impl TeleologicalStateRust {
    #[new]
    fn new(timestamp: f64, intents: Vec<RustIntent>) -> Self {
        let entropy = Self::compute_entropy(&intents);
        TeleologicalStateRust {
            timestamp,
            intents,
            entropy,
            goal_alignment: 0.0,
        }
    }
    
    fn compute_entropy(intents: &[RustIntent]) -> f64 {
        intents.iter()
            .filter(|i| i.probability > 1e-10)
            .map(|i| -i.probability * i.probability.ln())
            .sum()
    }
}

/// High-performance Teleological Back-Propagation Engine
#[pyclass]
pub struct TeleologicalEngineRust {
    learning_rate: f64,
    decay_rate: f64,
    trajectory: Vec<TeleologicalStateRust>,
    goals: HashMap<String, f64>, // goal_label -> target_probability
}

#[pymethods]
impl TeleologicalEngineRust {
    #[new]
    fn new(learning_rate: f64, decay_rate: f64) -> Self {
        TeleologicalEngineRust {
            learning_rate,
            decay_rate,
            trajectory: Vec::new(),
            goals: HashMap::new(),
        }
    }
    
    /// Add a teleological goal
    fn add_goal(&mut self, label: String, target_probability: f64) {
        self.goals.insert(label, target_probability);
    }
    
    /// Record a state in the trajectory
    fn record_state(&mut self, timestamp: f64, intents: Vec<RustIntent>) {
        let state = TeleologicalStateRust::new(timestamp, intents);
        self.trajectory.push(state);
    }
    
    /// Compute goal alignment for a set of intents
    fn compute_goal_alignment(&self, intents: &[RustIntent]) -> f64 {
        if self.goals.is_empty() {
            return 0.0;
        }
        
        let mut kl_divergence = 0.0;
        
        for (label, target_prob) in &self.goals {
            let current_prob = intents.iter()
                .find(|i| &i.label == label)
                .map(|i| i.probability)
                .unwrap_or(1e-10);
            
            if *target_prob > 0.0 {
                kl_divergence += target_prob * (target_prob / current_prob).ln();
            }
        }
        
        // Convert to alignment score
        (-kl_divergence).exp()
    }
    
    /// Recursive back-propagation (main algorithm)
    fn recursive_backprop(&self, depth: usize, max_depth: usize) -> HashMap<String, Vec<f64>> {
        if depth >= max_depth || self.trajectory.is_empty() {
            return HashMap::new();
        }
        
        let mut gradients: HashMap<String, Vec<f64>> = HashMap::new();
        
        // Base case: compute gradients for most recent state
        if depth == 0 {
            let latest_state = self.trajectory.last().unwrap();
            
            for intent in &latest_state.intents {
                if let Some(target_prob) = self.goals.get(&intent.label) {
                    let gradient = (target_prob - intent.probability) * 1.0; // importance = 1.0
                    gradients.insert(intent.label.clone(), vec![gradient]);
                }
            }
        }
        
        // Recursive case: back-propagate to earlier states
        if self.trajectory.len() > 1 {
            let future_gradients = self.recursive_backprop(depth + 1, max_depth);
            
            for (label, future_grad) in future_gradients {
                let decayed_grad: Vec<f64> = future_grad.iter()
                    .map(|g| g * self.decay_rate)
                    .collect();
                
                gradients.entry(label)
                    .and_modify(|g| g.extend(&decayed_grad))
                    .or_insert(decayed_grad);
            }
        }
        
        gradients
    }
    
    /// Apply teleological updates to intents
    fn apply_teleological_update(&self, intents: Vec<RustIntent>) -> Vec<RustIntent> {
        let max_depth = std::cmp::min(10, self.trajectory.len());
        let gradients = self.recursive_backprop(0, max_depth);
        
        let mut updated_intents = Vec::new();
        let mut total_prob = 0.0;
        
        for mut intent in intents {
            if let Some(grads) = gradients.get(&intent.label) {
                let avg_gradient: f64 = grads.iter().sum::<f64>() / grads.len() as f64;
                let adjustment = avg_gradient * self.learning_rate * intent.teleological_weight;
                intent.probability = (intent.probability + adjustment).max(0.0).min(1.0);
            }
            total_prob += intent.probability;
            updated_intents.push(intent);
        }
        
        // Normalize probabilities
        if total_prob > 0.0 {
            for intent in &mut updated_intents {
                intent.probability /= total_prob;
            }
        }
        
        updated_intents
    }
    
    /// Execute one full teleological cycle
    fn execute_cycle(&mut self, timestamp: f64, intents: Vec<RustIntent>) -> Vec<RustIntent> {
        self.record_state(timestamp, intents.clone());
        self.apply_teleological_update(intents)
    }
    
    /// Reset trajectory
    fn reset_trajectory(&mut self) {
        self.trajectory.clear();
    }
    
    /// Get trajectory length
    fn trajectory_length(&self) -> usize {
        self.trajectory.len()
    }
    
    /// Get average entropy over trajectory
    fn average_entropy(&self) -> f64 {
        if self.trajectory.is_empty() {
            return 0.0;
        }
        
        let sum: f64 = self.trajectory.iter().map(|s| s.entropy).sum();
        sum / self.trajectory.len() as f64
    }
}

/// Python module initialization
#[pymodule]
fn teleological_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustIntent>()?;
    m.add_class::<TeleologicalStateRust>()?;
    m.add_class::<TeleologicalEngineRust>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_intent_creation() {
        let intent = RustIntent::new("test".to_string(), 0.5, 1.0);
        assert_eq!(intent.label, "test");
        assert_eq!(intent.probability, 0.5);
    }
    
    #[test]
    fn test_engine_creation() {
        let engine = TeleologicalEngineRust::new(0.1, 0.95);
        assert_eq!(engine.trajectory_length(), 0);
    }
    
    #[test]
    fn test_goal_addition() {
        let mut engine = TeleologicalEngineRust::new(0.1, 0.95);
        engine.add_goal("intent1".to_string(), 0.8);
        assert!(engine.goals.contains_key("intent1"));
    }
    
    #[test]
    fn test_state_recording() {
        let mut engine = TeleologicalEngineRust::new(0.1, 0.95);
        let intents = vec![
            RustIntent::new("intent1".to_string(), 0.6, 1.0),
            RustIntent::new("intent2".to_string(), 0.4, 1.0),
        ];
        engine.record_state(0.0, intents);
        assert_eq!(engine.trajectory_length(), 1);
    }
    
    #[test]
    fn test_teleological_cycle() {
        let mut engine = TeleologicalEngineRust::new(0.1, 0.95);
        engine.add_goal("intent1".to_string(), 0.9);
        
        let intents = vec![
            RustIntent::new("intent1".to_string(), 0.5, 1.0),
            RustIntent::new("intent2".to_string(), 0.5, 1.0),
        ];
        
        let updated = engine.execute_cycle(0.0, intents);
        assert_eq!(updated.len(), 2);
        
        // After one cycle, intent1 should have higher probability (moving toward goal)
        let intent1_prob = updated.iter()
            .find(|i| i.label == "intent1")
            .unwrap()
            .probability;
        assert!(intent1_prob > 0.5);
    }
}
