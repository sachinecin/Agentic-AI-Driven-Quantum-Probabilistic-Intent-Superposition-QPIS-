//! QPIS Rust Back-Propagation Engine
//!
//! High-performance implementation of recursive teleological back-propagation
//! with Python FFI bindings via PyO3.

use ndarray::{Array1, Array2};
use pyo3::prelude::*;
use rayon::prelude::*;

/// Represents a teleological state in the back-propagation graph
#[pyclass]
#[derive(Clone)]
pub struct TeleologicalState {
    #[pyo3(get, set)]
    pub state_id: String,
    
    #[pyo3(get, set)]
    pub features: Vec<f64>,
    
    #[pyo3(get, set)]
    pub gradient: Vec<f64>,
    
    #[pyo3(get, set)]
    pub goal_distance: f64,
}

#[pymethods]
impl TeleologicalState {
    #[new]
    pub fn new(state_id: String, features: Vec<f64>) -> Self {
        let gradient = vec![0.0; features.len()];
        TeleologicalState {
            state_id,
            features,
            gradient,
            goal_distance: f64::INFINITY,
        }
    }
    
    pub fn __repr__(&self) -> String {
        format!(
            "TeleologicalState(id={}, dims={}, distance={:.4})",
            self.state_id,
            self.features.len(),
            self.goal_distance
        )
    }
}

/// High-performance back-propagation engine
#[pyclass]
pub struct RustBackPropEngine {
    learning_rate: f64,
    decay_factor: f64,
    max_depth: usize,
}

#[pymethods]
impl RustBackPropEngine {
    #[new]
    pub fn new(learning_rate: f64, decay_factor: f64, max_depth: usize) -> Self {
        RustBackPropEngine {
            learning_rate,
            decay_factor,
            max_depth,
        }
    }
    
    /// Compute gradients from goal to current state
    pub fn compute_gradients(
        &self,
        current_features: Vec<f64>,
        goal_features: Vec<f64>,
        time_horizon: f64,
    ) -> Vec<f64> {
        let current = Array1::from_vec(current_features);
        let goal = Array1::from_vec(goal_features);
        
        // Compute error vector
        let error = &goal - &current;
        
        // Apply temporal decay
        let temporal_weight = (-time_horizon / self.decay_factor).exp();
        
        // Gradient is weighted error
        let gradient = &error * temporal_weight;
        
        gradient.to_vec()
    }
    
    /// Parallel gradient computation for multiple states
    pub fn compute_batch_gradients(
        &self,
        states: Vec<Vec<f64>>,
        goal_features: Vec<f64>,
        time_horizons: Vec<f64>,
    ) -> Vec<Vec<f64>> {
        let goal = Array1::from_vec(goal_features);
        
        // Parallel computation using rayon
        states
            .par_iter()
            .zip(time_horizons.par_iter())
            .map(|(state_features, &time_horizon)| {
                let current = Array1::from_vec(state_features.clone());
                let error = &goal - &current;
                let temporal_weight = (-time_horizon / self.decay_factor).exp();
                let gradient = &error * temporal_weight;
                gradient.to_vec()
            })
            .collect()
    }
    
    /// Compute goal alignment score
    pub fn compute_alignment(
        &self,
        state_features: Vec<f64>,
        goal_features: Vec<f64>,
    ) -> f64 {
        let state = Array1::from_vec(state_features);
        let goal = Array1::from_vec(goal_features);
        
        // Cosine similarity
        let dot_product = state.dot(&goal);
        let state_norm = state.dot(&state).sqrt();
        let goal_norm = goal.dot(&goal).sqrt();
        
        if state_norm == 0.0 || goal_norm == 0.0 {
            return 0.0;
        }
        
        let similarity = dot_product / (state_norm * goal_norm);
        
        // Map to [0, 1]
        (similarity + 1.0) / 2.0
    }
    
    /// Recursive back-propagation through time
    pub fn recursive_backprop(
        &self,
        initial_state: Vec<f64>,
        goal_state: Vec<f64>,
        depth: usize,
    ) -> Vec<Vec<f64>> {
        let mut trajectory = Vec::new();
        let mut current = Array1::from_vec(initial_state);
        let goal = Array1::from_vec(goal_state);
        
        trajectory.push(current.to_vec());
        
        for d in 0..depth.min(self.max_depth) {
            // Compute gradient
            let error = &goal - &current;
            let temporal_weight = (-(d as f64) * 0.1 / self.decay_factor).exp();
            let gradient = &error * temporal_weight * self.learning_rate;
            
            // Update state
            current = &current + &gradient;
            trajectory.push(current.to_vec());
            
            // Early stopping if close to goal
            let distance = (&goal - &current).dot(&(&goal - &current)).sqrt();
            if distance < 0.01 {
                break;
            }
        }
        
        trajectory
    }
    
    /// Optimize state distribution toward goal
    pub fn optimize_distribution(
        &self,
        state_probabilities: Vec<f64>,
        state_features: Vec<Vec<f64>>,
        goal_features: Vec<f64>,
    ) -> Vec<f64> {
        let goal = Array1::from_vec(goal_features);
        
        // Compute alignment scores
        let alignments: Vec<f64> = state_features
            .iter()
            .map(|features| {
                let state = Array1::from_vec(features.clone());
                let dot_product = state.dot(&goal);
                let state_norm = state.dot(&state).sqrt();
                let goal_norm = goal.dot(&goal).sqrt();
                
                if state_norm == 0.0 || goal_norm == 0.0 {
                    0.0
                } else {
                    (dot_product / (state_norm * goal_norm) + 1.0) / 2.0
                }
            })
            .collect();
        
        // Adjust probabilities based on alignment
        let mut new_probs: Vec<f64> = state_probabilities
            .iter()
            .zip(alignments.iter())
            .map(|(&prob, &alignment)| {
                prob * (1.0 + self.learning_rate * alignment)
            })
            .collect();
        
        // Normalize
        let total: f64 = new_probs.iter().sum();
        if total > 0.0 {
            new_probs.iter_mut().for_each(|p| *p /= total);
        }
        
        new_probs
    }
    
    pub fn __repr__(&self) -> String {
        format!(
            "RustBackPropEngine(lr={}, decay={}, max_depth={})",
            self.learning_rate, self.decay_factor, self.max_depth
        )
    }
}

/// Python module initialization
#[pymodule]
fn qpis_rust_backprop(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<TeleologicalState>()?;
    m.add_class::<RustBackPropEngine>()?;
    Ok(())
}
