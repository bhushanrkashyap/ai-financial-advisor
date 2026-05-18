"""
Market Risk and Portfolio Analysis Service.
Computes market sentiment, volatility indices, and portfolio recommendations.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
import joblib
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MarketRiskService:
    """Service for market risk analysis and portfolio optimization."""
    
    def __init__(self, market_dir: Path | None = None):
        """Initialize market risk service.
        
        Parameters
        ----------
        market_dir : Path, optional
            Directory containing market data and models.
        """
        if market_dir is None:
            current_dir = Path(__file__).resolve().parent.parent.parent  # backend
            market_dir = current_dir.parent / "datasets" / "processed"
        
        self.market_dir = market_dir
        self.market_metrics = None
        self.sector_data = None
        self.portfolio_optimizer = None
        self.is_loaded = False
        
        self._load_artifacts()
    
    def _load_artifacts(self) -> None:
        """Load market data and portfolio optimizer."""
        try:
            # Load market metrics
            metrics_file = self.market_dir / "market_metrics.csv"
            if metrics_file.exists():
                self.market_metrics = pd.read_csv(metrics_file)
                logger.info(f"Loaded market metrics")
            
            # Load sector data
            sector_file = self.market_dir / "sector_risk.csv"
            if sector_file.exists():
                self.sector_data = pd.read_csv(sector_file)
                logger.info(f"Loaded sector data")
            
            # Portfolio optimizer is computed on-the-fly for simplicity
            # Pre-computed portfolios are available in sample_portfolios.csv
            self.portfolio_optimizer = None  # Not needed for runtime
            logger.info("Portfolio optimizer initialized (computed on-the-fly)")
            
            self.is_loaded = self.market_metrics is not None
        
        except Exception as e:
            logger.error(f"Error loading market artifacts: {e}")
            self.is_loaded = False
    
    def get_current_market_conditions(self) -> Dict:
        """Get current market conditions and risk indicators.
        
        Returns
        -------
        Dict
            Market conditions with:
            - volatility: Current 30-day volatility
            - volatility_regime: Low/Medium/High
            - market_trend: Bull/Neutral/Bear
            - market_stress: Stress indicator (0-1)
            - vix_equivalent: Market volatility index equivalent
        """
        if not self.is_loaded or self.market_metrics is None or len(self.market_metrics) == 0:
            return {
                'status': 'error',
                'message': 'Market data not available'
            }
        
        try:
            latest = self.market_metrics.iloc[-1] if len(self.market_metrics) > 0 else None
            if latest is None:
                return {'status': 'error', 'message': 'No market data available'}
            
            vol_30d = latest.get('volatility_30d', 0) or 0.15
            momentum_30d = latest.get('momentum_30d', 0) or 0.0005
            
            # Determine market trend
            if momentum_30d > 0.001:
                trend = 'bullish'
            elif momentum_30d < -0.001:
                trend = 'bearish'
            else:
                trend = 'neutral'
            
            # Volatility regime
            if vol_30d < 0.12:
                regime = 'low'
            elif vol_30d < 0.18:
                regime = 'medium'
            else:
                regime = 'high'
            
            return {
                'status': 'success',
                'volatility_30d': round(float(vol_30d), 4),
                'volatility_regime': regime,
                'momentum_30d': round(float(momentum_30d), 6),
                'market_trend': trend,
                'vix_equivalent': round(float(vol_30d * np.sqrt(252) * 100), 2),
                'market_stress': float(latest.get('market_stress', 0)),
                'date': str(latest.get('date', 'Unknown')) if 'date' in latest else 'Unknown'
            }
        
        except Exception as e:
            logger.error(f"Error getting market conditions: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_sector_analysis(self) -> Dict:
        """Get sector/stock analysis.
        
        Returns
        -------
        Dict
            Sector analysis with:
            - sectors: List of sectors with volatility and performance
            - avg_volatility: Market average volatility
            - market_health: Overall market health score
        """
        if not self.is_loaded or self.sector_data is None or len(self.sector_data) == 0:
            return {
                'status': 'error',
                'message': 'Sector data not available'
            }
        
        try:
            sectors = []
            
            for _, row in self.sector_data.iterrows():
                sectors.append({
                    'symbol': row.get('symbol', 'Unknown'),
                    'volatility_30d': round(float(row.get('volatility_30d', 0)), 4),
                    'momentum_30d': round(float(row.get('momentum_30d', 0)), 6),
                    'latest_return': round(float(row.get('latest_return', 0)), 4),
                    'performance': 'up' if float(row.get('latest_return', 0)) > 0 else 'down'
                })
            
            avg_vol = self.sector_data['volatility_30d'].mean() if len(self.sector_data) > 0 else 0.15
            
            # Market health: 0-100 score
            health_score = 100 * (1 - min(avg_vol / 0.30, 1.0))
            
            return {
                'status': 'success',
                'sectors': sectors,
                'avg_volatility': round(float(avg_vol), 4),
                'market_health_score': round(health_score, 1),
                'num_sectors': len(sectors)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing sectors: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def recommend_portfolio(self, risk_level: str = 'moderate', 
                          income: float = 500000) -> Dict:
        """Recommend portfolio allocation based on risk profile and income.
        
        Parameters
        ----------
        risk_level : str
            Risk level: 'conservative', 'moderate', or 'aggressive'
        income : float
            Annual income in INR
        
        Returns
        -------
        Dict
            Portfolio recommendation with:
            - allocation: Asset allocation percentages
            - monthly_investment: Recommended monthly investment
            - expected_returns: Expected annual return
            - risk_metrics: Volatility and Sharpe ratio
        """
        try:
            # Asset allocation by risk profile
            allocations = {
                'conservative': {
                    'equity': 0.30, 'bonds': 0.50, 'cash': 0.15, 'gold': 0.05
                },
                'moderate': {
                    'equity': 0.50, 'bonds': 0.30, 'cash': 0.10, 'gold': 0.10
                },
                'aggressive': {
                    'equity': 0.70, 'bonds': 0.15, 'cash': 0.05, 'gold': 0.10
                }
            }
            
            allocation = allocations.get(risk_level, allocations['moderate'])
            
            # Asset class expected returns and volatility
            asset_metrics = {
                'equity': {'return': 0.12, 'volatility': 0.18},
                'bonds': {'return': 0.06, 'volatility': 0.06},
                'cash': {'return': 0.04, 'volatility': 0.01},
                'gold': {'return': 0.05, 'volatility': 0.15}
            }
            
            # Portfolio metrics
            portfolio_return = sum(
                allocation[asset] * asset_metrics[asset]['return']
                for asset in allocation
            )
            
            portfolio_variance = sum(
                allocation[asset] ** 2 * asset_metrics[asset]['volatility'] ** 2
                for asset in allocation
            )
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            sharpe_ratio = (portfolio_return - 0.04) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Investment recommendations
            annual_savings_rate = 0.15  # Assume 15% savings rate
            monthly_investment = (income * annual_savings_rate) / 12
            
            return {
                'status': 'success',
                'risk_level': risk_level,
                'allocation': {
                    'equity': f"{allocation['equity']*100:.0f}%",
                    'bonds': f"{allocation['bonds']*100:.0f}%",
                    'cash': f"{allocation['cash']*100:.0f}%",
                    'gold': f"{allocation['gold']*100:.0f}%"
                },
                'allocation_raw': allocation,
                'monthly_investment': round(monthly_investment, 2),
                'annual_investment': round(monthly_investment * 12, 2),
                'expected_annual_return': round(portfolio_return * 100, 2),
                'volatility': round(portfolio_volatility * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'notes': self._get_allocation_notes(risk_level)
            }
        
        except Exception as e:
            logger.error(f"Error recommending portfolio: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_allocation_notes(self, risk_level: str) -> str:
        """Get notes for allocation strategy."""
        notes = {
            'conservative': 'Focus on capital preservation with steady income. Suitable for near-retirees and risk-averse investors.',
            'moderate': 'Balanced approach for long-term growth. Suitable for middle-aged investors with medium risk tolerance.',
            'aggressive': 'Growth-oriented strategy for long-term wealth creation. Suitable for young investors with high risk tolerance.'
        }
        return notes.get(risk_level, '')
    
    def analyze_loan_default_risk(self, market_conditions: Dict, 
                                 borrower_income: float) -> Dict:
        """Analyze loan default risk based on market conditions.
        
        Parameters
        ----------
        market_conditions : Dict
            Current market conditions
        borrower_income : float
            Borrower's annual income
        
        Returns
        -------
        Dict
            Risk assessment with:
            - macro_risk_score: Market-based risk (0-1)
            - market_adjusted_risk: Risk adjusted for market conditions
            - recommendation: Risk mitigation strategies
        """
        try:
            # Extract market indicators
            volatility = market_conditions.get('volatility_30d', 0.15)
            vix = market_conditions.get('vix_equivalent', 20)
            market_trend = market_conditions.get('market_trend', 'neutral')
            
            # Macro risk calculation
            base_risk = volatility / 0.20  # Normalize to 20% baseline
            
            # Trend adjustment
            trend_factor = {'bullish': 0.8, 'neutral': 1.0, 'bearish': 1.3}.get(market_trend, 1.0)
            
            macro_risk_score = min(base_risk * trend_factor, 1.0)
            
            # Income stability score (inverse)
            income_stability = min(borrower_income / 500000, 1.0)
            
            # Adjusted risk
            market_adjusted_risk = macro_risk_score * 0.7 + (1 - income_stability) * 0.3
            
            # Risk category
            if market_adjusted_risk < 0.3:
                risk_category = 'low'
                recommendation = 'Market conditions favorable for lending'
            elif market_adjusted_risk < 0.6:
                risk_category = 'moderate'
                recommendation = 'Standard loan terms recommended'
            else:
                risk_category = 'high'
                recommendation = 'Require higher collateral or stricter terms'
            
            return {
                'status': 'success',
                'macro_risk_score': round(macro_risk_score, 3),
                'market_adjusted_risk': round(market_adjusted_risk, 3),
                'risk_category': risk_category,
                'vix_equivalent': vix,
                'volatility_factor': round(volatility * 100, 2),
                'income_stability_score': round(income_stability, 3),
                'recommendation': recommendation
            }
        
        except Exception as e:
            logger.error(f"Error analyzing default risk: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def health_check(self) -> Dict:
        """Check service health."""
        return {
            'status': 'healthy' if self.is_loaded else 'unhealthy',
            'market_metrics_loaded': self.market_metrics is not None,
            'sector_data_loaded': self.sector_data is not None,
            'portfolio_optimizer_loaded': self.portfolio_optimizer is not None,
            'market_dir': str(self.market_dir)
        }
