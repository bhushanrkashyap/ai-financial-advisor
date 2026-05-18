"""
Market Features Extraction from NIFTY50 and Individual Stock Data.
Computes risk indicators, volatility, momentum, and market trends.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.parent.parent
DATASET_DIR = PROJECT_DIR / "datasets"
PROCESSED_DIR = DATASET_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_market_data():
    """Load NIFTY50 and individual stock data."""
    nifty_df = pd.read_csv(DATASET_DIR / "NIFTY50_all.csv")
    logger.info(f"Loaded NIFTY50 data: {nifty_df.shape}")
    
    # Load individual stocks
    stock_files = list(DATASET_DIR.glob("*.csv"))
    stock_files = [f for f in stock_files if f.name not in 
                   ['Bengaluru_House_Data.csv', 'NIFTY50_all.csv', 'train.csv', 
                    'test.csv', 'sample_submission.csv']]
    
    logger.info(f"Found {len(stock_files)} stock files")
    
    return nifty_df, stock_files


def compute_market_features(nifty_df):
    """Compute market-level risk indicators."""
    # Convert Date to datetime
    nifty_df['Date'] = pd.to_datetime(nifty_df['Date'])
    nifty_df = nifty_df.sort_values('Date')
    
    # Compute daily returns
    nifty_df['Returns'] = nifty_df['Close'].pct_change()
    
    # 30-day rolling volatility
    nifty_df['Volatility_30d'] = nifty_df['Returns'].rolling(window=30).std()
    
    # 30-day rolling average returns (momentum)
    nifty_df['Momentum_30d'] = nifty_df['Returns'].rolling(window=30).mean()
    
    # Volume trend (30-day average)
    nifty_df['AvgVolume_30d'] = nifty_df['Volume'].rolling(window=30).mean()
    
    # Volatility regime: classify as High/Medium/Low
    vol_high = nifty_df['Volatility_30d'].quantile(0.75)
    vol_low = nifty_df['Volatility_30d'].quantile(0.25)
    nifty_df['Volatility_Regime'] = pd.cut(
        nifty_df['Volatility_30d'], 
        bins=[0, vol_low, vol_high, np.inf],
        labels=['Low', 'Medium', 'High']
    )
    
    # Market stress indicator (negative returns + high volatility)
    nifty_df['Market_Stress'] = (
        (nifty_df['Returns'] < -0.02).astype(int) & 
        (nifty_df['Volatility_30d'] > vol_high).astype(int)
    ).astype(int)
    
    logger.info(f"Computed market features shape: {nifty_df.shape}")
    logger.info(f"Volatility range: {nifty_df['Volatility_30d'].min():.4f} - {nifty_df['Volatility_30d'].max():.4f}")
    
    return nifty_df


def aggregate_market_metrics(nifty_df):
    """Create time-aggregated market metrics for different time windows."""
    metrics = []
    
    # Latest metrics (most recent trading day with no NaNs)
    latest_valid = nifty_df.dropna(subset=['Volatility_30d']).iloc[-1]
    
    metrics_dict = {
        'date': latest_valid['Date'],
        'latest_close': latest_valid['Close'],
        'volatility_30d': latest_valid['Volatility_30d'],
        'momentum_30d': latest_valid['Momentum_30d'],
        'market_stress': latest_valid['Market_Stress'],
        'volatility_regime': latest_valid['Volatility_Regime'],
        # 60-day metrics
        'volatility_60d': nifty_df['Returns'].tail(60).std(),
        'momentum_60d': nifty_df['Returns'].tail(60).mean(),
        # Year-to-date metrics
        'ytd_return': (nifty_df['Close'].iloc[-1] / nifty_df['Close'].iloc[0] - 1) * 100,
        # VIX-like measure (30-day rolling std)
        'market_vix_equiv': latest_valid['Volatility_30d'] * np.sqrt(252) * 100
    }
    
    metrics.append(metrics_dict)
    metrics_df = pd.DataFrame(metrics)
    
    logger.info(f"Market metrics:\n{metrics_df.to_string()}")
    
    return metrics_df


def compute_sector_risk(stock_files):
    """Compute aggregated sector/portfolio risk from individual stocks."""
    sector_returns = []
    
    for stock_file in stock_files[:5]:  # Process first 5 stocks for efficiency
        try:
            stock_df = pd.read_csv(stock_file)
            stock_name = stock_file.stem
            
            stock_df['Date'] = pd.to_datetime(stock_df['Date'], errors='coerce')
            stock_df = stock_df.sort_values('Date')
            stock_df['Returns'] = stock_df['Close'].pct_change()
            
            if len(stock_df) > 30:
                sector_returns.append({
                    'symbol': stock_name,
                    'volatility_30d': stock_df['Returns'].tail(30).std(),
                    'momentum_30d': stock_df['Returns'].tail(30).mean(),
                    'latest_return': stock_df['Returns'].iloc[-1]
                })
                logger.info(f"Processed {stock_name}: vol={sector_returns[-1]['volatility_30d']:.4f}")
        except Exception as e:
            logger.warning(f"Error processing {stock_file.name}: {e}")
    
    sector_df = pd.DataFrame(sector_returns)
    logger.info(f"Processed {len(sector_df)} stocks")
    
    return sector_df


def create_market_risk_profile():
    """Create comprehensive market risk profile."""
    nifty_df, stock_files = load_market_data()
    nifty_df = compute_market_features(nifty_df)
    market_metrics = aggregate_market_metrics(nifty_df)
    sector_df = compute_sector_risk(stock_files)
    
    # Save processed market data
    nifty_df.to_csv(PROCESSED_DIR / "nifty50_features.csv", index=False)
    market_metrics.to_csv(PROCESSED_DIR / "market_metrics.csv", index=False)
    sector_df.to_csv(PROCESSED_DIR / "sector_risk.csv", index=False)
    
    logger.info(f"Saved market features to {PROCESSED_DIR}")
    
    return market_metrics, sector_df


def main():
    """Main market features pipeline."""
    market_metrics, sector_df = create_market_risk_profile()
    return market_metrics, sector_df


if __name__ == "__main__":
    main()
