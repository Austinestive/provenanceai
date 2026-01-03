"""
Scoring Engine Module

This module provides the core scoring functionality for the trust framework.
"""

from typing import Any, Dict, Optional

from provenanceai.trust.metrics import TrustMetrics
from provenanceai.trust.weights import MetricWeights


class ScoringEngine:
    """
    Engine for calculating trust scores based on various metrics.
    
    This class combines different trust metrics using weighted calculations
    to produce overall trust scores for AI systems and components.
    """
    
    def __init__(self, weights: Optional[MetricWeights] = None):
        """
        Initialize the scoring engine.
        
        Args:
            weights: Custom metric weights. If None, uses default weights.
        """
        self.weights = weights or MetricWeights()
    
    def calculate_score(self, metrics: TrustMetrics) -> float:
        """
        Calculate the overall trust score based on provided metrics.
        
        Args:
            metrics: The trust metrics to score
            
        Returns:
            A normalized trust score between 0 and 1
        """
        # Weighted average of all metrics
        score = (
            metrics.transparency * self.weights.transparency +
            metrics.accountability * self.weights.accountability +
            metrics.fairness * self.weights.fairness +
            metrics.robustness * self.weights.robustness +
            metrics.privacy * self.weights.privacy
        )
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))
    
    def get_detailed_breakdown(self, metrics: TrustMetrics) -> Dict[str, Any]:
        """
        Get a detailed breakdown of the trust score calculation.
        
        Args:
            metrics: The trust metrics to analyze
            
        Returns:
            Dictionary containing score breakdown and analysis
        """
        overall_score = self.calculate_score(metrics)
        
        return {
            'overall_score': overall_score,
            'component_scores': {
                'transparency': metrics.transparency * self.weights.transparency,
                'accountability': metrics.accountability * self.weights.accountability,
                'fairness': metrics.fairness * self.weights.fairness,
                'robustness': metrics.robustness * self.weights.robustness,
                'privacy': metrics.privacy * self.weights.privacy
            },
            'weights_used': {
                'transparency': self.weights.transparency,
                'accountability': self.weights.accountability,
                'fairness': self.weights.fairness,
                'robustness': self.weights.robustness,
                'privacy': self.weights.privacy
            },
            'raw_metrics': {
                'transparency': metrics.transparency,
                'accountability': metrics.accountability,
                'fairness': metrics.fairness,
                'robustness': metrics.robustness,
                'privacy': metrics.privacy
            }
        }
