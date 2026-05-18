"""
Portfolio Optimization and Financial Planning.
Implements Modern Portfolio Theory (Markowitz) for asset allocation.
Computes efficient frontier and generates personalized portfolios.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import logging
from scipy.optimize import minimize
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.parent.parent
PROCESSED_DIR = PROJECT_DIR / "datasets" / "processed"
MODEL_DIR = PROJECT_DIR / "backend" / "models"


class PortfolioOptimizer:
    """Modern Portfolio Theory implementation for asset allocation."""
    
    def __init__(self, market_df=None):
        """Initialize portfolio optimizer."""
        self.market_df = market_df
        self.efficient_frontier = None
        self.asset_classes = {
            'stocks': {'return': 0.12, 'volatility': 0.18, 'color': 'red'},
            'bonds': {'return': 0.05, 'volatility': 0.06, 'color': 'blue'},
            'cash': {'return': 0.03, 'volatility': 0.01, 'color': 'green'},
            'gold': {'return': 0.04, 'volatility': 0.15, 'color': 'yellow'},
        }
        
    def compute_expected_returns(self, returns_df):
        """Compute annualized expected returns for assets."""
        # Annualize daily returns (252 trading days)
        returns = returns_df.mean() * 252
        return returns
    
    def compute_covariance(self, returns_df):
        """Compute annualized covariance matrix."""
        # Annualize daily covariance
        cov = returns_df.cov() * 252
        return cov
    
    def portfolio_stats(self, weights, expected_returns, cov_matrix):
        """Calculate portfolio return and volatility."""
        portfolio_return = np.sum(weights * expected_returns)
        portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        return portfolio_return, portfolio_volatility, sharpe_ratio
    
    def negative_sharpe(self, weights, expected_returns, cov_matrix, risk_free_rate=0.03):
        """Negative Sharpe ratio for minimization."""
        p_return, p_volatility, _ = self.portfolio_stats(weights, expected_returns, cov_matrix)
        return -(p_return - risk_free_rate) / p_volatility if p_volatility > 0 else 0
    
    def optimize_portfolio(self, expected_returns, cov_matrix, constraints=None):
        """Optimize portfolio weights for maximum Sharpe ratio."""
        n_assets = len(expected_returns)
        weights = np.array([1/n_assets] * n_assets)
        
        bounds = tuple((0, 1) for _ in range(n_assets))
        constraints_list = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        
        if constraints:
            constraints_list.extend(constraints)
        
        result = minimize(
            self.negative_sharpe,
            weights,
            args=(expected_returns, cov_matrix),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list
        )
        
        return result.x
    
    def generate_efficient_frontier(self, expected_returns, cov_matrix, n_points=50):
        """Generate efficient frontier."""
        frontier_returns = []
        frontier_volatility = []
        frontier_weights = []
        
        # Target returns from min to max
        min_return = expected_returns.min()
        max_return = expected_returns.max()
        target_returns = np.linspace(min_return, max_return, n_points)
        
        for target_return in target_returns:
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w: np.sum(w * expected_returns) - target_return}
            ]
            
            weights = self.optimize_portfolio(expected_returns, cov_matrix, constraints)
            p_return, p_volatility, _ = self.portfolio_stats(weights, expected_returns, cov_matrix)
            
            frontier_returns.append(p_return)
            frontier_volatility.append(p_volatility)
            frontier_weights.append(weights)
        
        self.efficient_frontier = {
            'returns': np.array(frontier_returns),
            'volatility': np.array(frontier_volatility),
            'weights': np.array(frontier_weights)
        }
        
        logger.info(f"Generated efficient frontier with {n_points} points")
        return self.efficient_frontier
    
    def allocate_by_risk_profile(self, risk_level='moderate'):
        """Generate portfolio allocation based on user risk profile."""
        risk_profiles = {
            'conservative': {'stocks': 0.30, 'bonds': 0.50, 'cash': 0.15, 'gold': 0.05},
            'moderate': {'stocks': 0.50, 'bonds': 0.30, 'cash': 0.10, 'gold': 0.10},
            'aggressive': {'stocks': 0.70, 'bonds': 0.15, 'cash': 0.05, 'gold': 0.10},
        }
        
        allocation = risk_profiles.get(risk_level, risk_profiles['moderate'])
        
        # Compute expected portfolio metrics
        expected_return = sum(
            allocation[asset] * self.asset_classes[asset]['return']
            for asset in allocation
        )
        
        portfolio_variance = sum(
            allocation[asset] ** 2 * self.asset_classes[asset]['volatility'] ** 2
            for asset in allocation
        )
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        sharpe = (expected_return - 0.03) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        logger.info(f"Risk Profile: {risk_level}")
        logger.info(f"Allocation: {allocation}")
        logger.info(f"Expected Return: {expected_return:.2%}, Volatility: {portfolio_volatility:.2%}, Sharpe: {sharpe:.2f}")
        
        return allocation, {
            'expected_return': expected_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe
        }
    
    def recommend_rebalancing(self, current_allocation, target_allocation, threshold=0.05):
        """Recommend portfolio rebalancing if drift exceeds threshold."""
        rebalancing_needed = []
        
        for asset, target_weight in target_allocation.items():
            current_weight = current_allocation.get(asset, 0)
            drift = abs(current_weight - target_weight)
            
            if drift > threshold:
                rebalancing_needed.append({
                    'asset': asset,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'drift': drift,
                    'action': 'increase' if current_weight < target_weight else 'decrease'
                })
        
        if rebalancing_needed:
            logger.info(f"Rebalancing needed for {len(rebalancing_needed)} assets")
            return rebalancing_needed
        else:
            logger.info("Portfolio is well-balanced")
            return []


def create_sample_portfolios():
    """Create sample portfolios for different scenarios."""
    optimizer = PortfolioOptimizer()
    
    portfolios = {}
    
    for risk_level in ['conservative', 'moderate', 'aggressive']:
        allocation, metrics = optimizer.allocate_by_risk_profile(risk_level)
        portfolios[risk_level] = {
            'allocation': allocation,
            'metrics': metrics
        }
    
    # Save portfolios
    portfolio_df = pd.DataFrame([
        {
            'risk_level': level,
            **portfolios[level]['allocation'],
            **{f"metric_{k}": v for k, v in portfolios[level]['metrics'].items()}
        }
        for level in portfolios
    ])
    
    portfolio_df.to_csv(MODEL_DIR / "sample_portfolios.csv", index=False)
    logger.info(f"Saved sample portfolios to {MODEL_DIR / 'sample_portfolios.csv'}")
    
    return portfolios


def save_portfolio_optimizer():
    """Save portfolio optimizer for backend use."""
    optimizer = PortfolioOptimizer()
    # Save to both locations for accessibility
    model_dir = Path(__file__).parent.parent.parent / "backend" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(optimizer, model_dir / "portfolio_optimizer.joblib")
    logger.info(f"Saved portfolio optimizer to {model_dir / 'portfolio_optimizer.joblib'}")


def main():
    """Main portfolio optimization pipeline."""
    logger.info("=== Portfolio Optimization ===")
    portfolios = create_sample_portfolios()
    save_portfolio_optimizer()
    return portfolios


if __name__ == "__main__":
    main()
