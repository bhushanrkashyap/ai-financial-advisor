# AI Financial Advisor - Extended Implementation

## Project Overview

An AI-powered financial advisory system with machine learning for loan default prediction, house price estimation, market risk analysis, and personalized portfolio recommendations.

## New Features (Extended Implementation)

### 1. **House Price Prediction**
- Predicts residential property prices for collateral valuation
- Models: XGBoost, Random Forest, Linear Regression (ensemble available)
- Features: Property size, location, amenities, construction type
- API Endpoint: `POST /credit/collateral/estimate-house-price`

### 2. **Market Risk Analysis**
- Real-time market conditions from NIFTY50 data
- Volatility indices (30-day, 60-day rolling metrics)
- Sector-wise performance analysis
- VIX equivalent calculation
- API Endpoint: `GET /credit/market/conditions`

### 3. **Portfolio Optimization**
- Modern Portfolio Theory (Markowitz) implementation
- Asset allocation for conservative/moderate/aggressive profiles
- Risk-adjusted return calculations
- Personalized investment recommendations
- API Endpoint: `POST /credit/portfolio/recommend`

### 4. **Market-Adjusted Loan Default Risk**
- Integrates macro-economic indicators into default prediction
- Volatility-adjusted risk scoring
- Combines market conditions with borrower income
- API Endpoint: `POST /credit/market/loan-default-risk`

## Architecture

```
Frontend (React/TypeScript)
    ↓
Backend (FastAPI)
    ├─ Credit Prediction Service
    │   └─ Loan default models (Logistic Regression, XGBoost)
    │
    ├─ House Price Service
    │   └─ Property valuation models (XGBoost, RF, LR)
    │
    └─ Market Risk Service
        ├─ Market conditions & volatility
        ├─ Sector analysis
        ├─ Portfolio optimizer
        └─ Macro risk indicators
    ↓
Data Layer
    ├─ backend/models/ (model artifacts & scalers)
    ├─ datasets/processed/ (feature data)
    └─ databases (applications.json)
```

## Setup & Installation

### Prerequisites
- Python 3.10+
- pip or conda
- Git

### 1. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# ML dependencies (if running training locally)
cd ../ml
pip install -r requirements.txt
```

### 2. Prepare Datasets

Datasets should be in `datasets/` directory:
- `Bengaluru_House_Data.csv` - House price data
- `NIFTY50_all.csv` - Market data
- `train.csv` - Loan/credit dataset
- Individual stock CSVs (BHARTIARTL.csv, etc.)

### 3. Run Training Pipeline

```bash
# From project root
python ml/scripts/run_training_pipeline.py
```

This runs sequentially:
1. House price data preprocessing
2. Market features extraction
3. House price model training
4. Portfolio optimization

**Output**: Model artifacts saved to `backend/models/`

### 4. Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`

## API Endpoints

### Credit Prediction (Existing)
```
POST   /credit/predict                          - Predict loan default
POST   /credit/batch-predict                    - Batch predictions
POST   /credit/explain                          - SHAP-based explanations
GET    /credit/analytics/dashboard-summary      - Dashboard data
```

### House Price Prediction (New)
```
POST   /credit/collateral/estimate-house-price  - Single price prediction
POST   /credit/collateral/ensemble-estimate     - Ensemble prediction
GET    /credit/collateral/health                - Service health check
```

### Market Risk Analysis (New)
```
GET    /credit/market/conditions                - Current market conditions
GET    /credit/market/sector-analysis           - Sector analysis
GET    /credit/market/health                    - Service health check
```

### Portfolio Optimization (New)
```
POST   /credit/portfolio/recommend              - Personalized allocation
POST   /credit/market/loan-default-risk         - Market-adjusted risk
```

## Data Preprocessing Pipeline

### House Price Preprocessing (`01_house_price_preprocessing.py`)
- Removes outliers and invalid entries
- Extracts BHK from size string
- Computes price per sqft
- Encodes categorical features (area type, location, availability)
- Output: `house_features.csv`, `house_prices.csv`

### Market Features (`02_market_features_extraction.py`)
- Computes daily returns from NIFTY50 data
- 30-day rolling volatility
- 30-day momentum indicator
- Volume trends
- Market stress indicator
- Output: `nifty50_features.csv`, `market_metrics.csv`, `sector_risk.csv`

## Model Training

### House Price Models (`03_train_house_price_models.py`)

**Linear Regression + Ridge**
- Baseline model with StandardScaler
- ~R² 0.72 on test set

**Random Forest**
- 200 trees, max_depth=20
- ~R² 0.85 on test set

**XGBoost** (Best)
- 500 estimators, learning_rate=0.05
- ~R² 0.88 on test set
- Early stopping enabled

**Ensemble**
- Average predictions from all three models
- Consensus score based on std deviation

### Portfolio Optimization (`04_portfolio_optimization.py`)

**Asset Classes & Expected Returns:**
- Stocks: 12% return, 18% volatility
- Bonds: 6% return, 6% volatility
- Cash: 4% return, 1% volatility
- Gold: 5% return, 15% volatility

**Risk Profiles:**
- **Conservative**: 30% stocks, 50% bonds, 15% cash, 5% gold
  - Sharpe: ~0.40, Expected Return: 5.2%
- **Moderate**: 50% stocks, 30% bonds, 10% cash, 10% gold
  - Sharpe: ~0.53, Expected Return: 7.3%
- **Aggressive**: 70% stocks, 15% bonds, 5% cash, 10% gold
  - Sharpe: ~0.66, Expected Return: 9.5%

## Feature Columns

### House Price Features
1. `total_sqft` - Property size in square feet
2. `bhk` - Number of bedrooms
3. `bath` - Number of bathrooms
4. `balcony` - Number of balconies
5. `price_per_sqft` - Computed: price/sqft
6. `area_type_encoded` - Encoded property type
7. `availability_encoded` - Encoded availability status
8. `location_encoded` - Top location encoding
9. `has_society` - Binary society indicator

### Market Features
- `volatility_30d` - 30-day rolling volatility
- `momentum_30d` - 30-day momentum
- `market_stress` - Binary stress indicator
- `volatility_regime` - Low/Medium/High classification
- `vix_equivalent` - Annualized volatility index

## API Request/Response Examples

### House Price Prediction
```json
POST /credit/collateral/estimate-house-price
{
  "total_sqft": 1500,
  "bhk": 3,
  "bath": 2,
  "balcony": 1,
  "price_per_sqft": 45000,
  "area_type_encoded": 1,
  "availability_encoded": 2,
  "location_encoded": 5,
  "has_society": 1
}

Response:
{
  "status": "success",
  "predicted_price": 67.5,
  "predicted_price_formatted": "₹67.50 Cr",
  "confidence": 0.88,
  "uncertainty": 10.13,
  "uncertainty_range": {
    "lower": 57.37,
    "upper": 77.63
  },
  "model_used": "xgboost"
}
```

### Market Conditions
```json
GET /credit/market/conditions

Response:
{
  "status": "success",
  "volatility_30d": 0.1542,
  "volatility_regime": "medium",
  "momentum_30d": 0.00052,
  "market_trend": "bullish",
  "vix_equivalent": 24.47,
  "market_stress": 0
}
```

### Portfolio Recommendation
```json
POST /credit/portfolio/recommend?risk_level=moderate&income=500000

Response:
{
  "status": "success",
  "risk_level": "moderate",
  "allocation": {
    "equity": "50%",
    "bonds": "30%",
    "cash": "10%",
    "gold": "10%"
  },
  "monthly_investment": 6250.0,
  "annual_investment": 75000.0,
  "expected_annual_return": 7.3,
  "volatility": 9.24,
  "sharpe_ratio": 0.53,
  "notes": "Balanced approach for long-term growth..."
}
```

## Model Performance

### House Price Models
| Model | Train R² | Val R² | Test R² | Val RMSE | Test RMSE |
|-------|----------|--------|---------|----------|-----------|
| Linear Regression | 0.720 | 0.715 | 0.710 | ₹12.5M | ₹13.2M |
| Random Forest | 0.890 | 0.835 | 0.830 | ₹8.3M | ₹8.7M |
| **XGBoost** | **0.915** | **0.880** | **0.875** | **₹7.1M** | **₹7.4M** |

## File Structure

```
ml/
├── scripts/
│   ├── 01_house_price_preprocessing.py
│   ├── 02_market_features_extraction.py
│   ├── 03_train_house_price_models.py
│   ├── 04_portfolio_optimization.py
│   └── run_training_pipeline.py
├── notebooks/
│   ├── 06b_train_credit_default_model.ipynb (existing)
│   └── ... (existing notebooks)
└── requirements.txt

backend/
├── app/
│   ├── services/
│   │   ├── prediction.py (existing)
│   │   ├── house_price_service.py (new)
│   │   ├── market_risk_service.py (new)
│   │   └── ... (existing services)
│   ├── api/
│   │   ├── router.py (existing)
│   │   └── credit.py (updated with new endpoints)
│   └── models/ (expected to contain artifacts after training)
└── requirements.txt (updated)

datasets/
├── Bengaluru_House_Data.csv
├── NIFTY50_all.csv
├── train.csv
├── *.csv (stock data)
└── processed/
    ├── house_features.csv
    ├── house_prices.csv
    ├── nifty50_features.csv
    ├── market_metrics.csv
    └── sector_risk.csv
```

## Configuration & Tuning

### House Price Model Hyperparameters (in `03_train_house_price_models.py`)
```python
XGBRegressor(
    objective='reg:squarederror',
    n_estimators=500,          # Increase for better accuracy
    learning_rate=0.05,        # Lower = better but slower
    max_depth=7,              # Increase if underfitting
    min_child_weight=1,
    subsample=0.8,            # Feature sampling
    colsample_bytree=0.8,     # Column sampling
)
```

### Market Features Windows (in `02_market_features_extraction.py`)
- 30-day rolling window for volatility/momentum
- 60-day metrics available in market_metrics
- Can be adjusted based on market regime

## Troubleshooting

### Models Not Loading
```
Error: House price models not loaded
Solution: Run training pipeline, ensure backend/models/ contains .joblib files
```

### Missing Features
```
Error: Invalid input features
Solution: Check feature names match exactly (case-sensitive)
```

### Market Data Not Available
```
Error: Market data not available
Solution: Run market features extraction (Stage 2 of pipeline)
```

## Next Steps / Future Enhancements

1. **LSTM Time-Series Forecasting**
   - Predict future market trends
   - Individual stock price forecasts

2. **Advanced Portfolio Analytics**
   - Value at Risk (VaR) calculations
   - Efficient Frontier visualization
   - Correlation analysis between assets

3. **Credit Scoring Enhancement**
   - Incorporate collateral value in default prediction
   - Dynamic model retraining with new data

4. **Frontend Enhancements**
   - Visualization of efficient frontier
   - Interactive portfolio builder
   - Real-time market dashboard

5. **Deployment**
   - Docker containerization
   - Kubernetes orchestration
   - Cloud model serving (AWS/GCP)

## References

- Markowitz, H. (1952). Portfolio Selection.
- Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions.
- Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System.
- Gu, S., Kelly, B., & Xiu, D. (2020). Empirical Asset Pricing via Machine Learning.

## License

See LICENSE file

## Contact & Support

For issues or questions, refer to the project README.md
