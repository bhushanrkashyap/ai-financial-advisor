# AI Financial Advisor - API Reference

**Base URL**: `http://localhost:8000`

---

## 📋 Table of Contents

1. [House Price Endpoints](#house-price-endpoints)
2. [Market Risk Endpoints](#market-risk-endpoints)
3. [Portfolio Endpoints](#portfolio-endpoints)
4. [Health & Status](#health--status)
5. [Error Codes](#error-codes)
6. [Response Schemas](#response-schemas)
7. [Rate Limiting & Best Practices](#rate-limiting--best-practices)

---

## 🏠 House Price Endpoints

### 1. Estimate Single Property Price

**Endpoint**: `POST /credit/collateral/estimate-house-price`

**Purpose**: Predict residential property price for collateral valuation

**Request Body**:
```json
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
```

**Parameter Details**:
| Field | Type | Range | Description |
|-------|------|-------|-------------|
| total_sqft | integer | 100-10000 | Property size in sq ft |
| bhk | integer | 1-6 | Number of bedrooms |
| bath | integer | 1-6 | Number of bathrooms |
| balcony | integer | 0-5 | Number of balconies |
| price_per_sqft | float | 10000-200000 | Price per sq ft (INR) |
| area_type_encoded | integer | 0-2 | Area type (0=Super Built-up, 1=Built-up, 2=Plot) |
| availability_encoded | integer | 0-3 | Availability status |
| location_encoded | integer | 0-10 | Location code (0-9=top locations, 10=other) |
| has_society | integer | 0-1 | In gated society (0=No, 1=Yes) |

**Response (Success - 200)**:
```json
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
  "model_used": "xgboost",
  "input_features": {
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
}
```

**Response Details**:
- `predicted_price`: Price in Crores
- `confidence`: 0-1 scale (0.88 = 88% confidence)
- `uncertainty`: ±value around prediction
- `uncertainty_range`: 68% confidence interval

**cURL Example**:
```bash
curl -X POST http://localhost:8000/credit/collateral/estimate-house-price \
  -H "Content-Type: application/json" \
  -d '{
    "total_sqft": 1500,
    "bhk": 3,
    "bath": 2,
    "balcony": 1,
    "price_per_sqft": 45000,
    "area_type_encoded": 1,
    "availability_encoded": 2,
    "location_encoded": 5,
    "has_society": 1
  }'
```

**Python Example**:
```python
import requests

url = "http://localhost:8000/credit/collateral/estimate-house-price"
payload = {
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

response = requests.post(url, json=payload)
result = response.json()
print(f"Estimated Price: {result['predicted_price_formatted']}")
print(f"Confidence: {result['confidence']}")
```

---

### 2. Ensemble House Price Estimation

**Endpoint**: `POST /credit/collateral/ensemble-estimate`

**Purpose**: Get predictions from all 3 models with consensus score

**Request Body**: Same as above

**Response (Success - 200)**:
```json
{
  "status": "success",
  "ensemble_price": 67.2,
  "ensemble_price_formatted": "₹67.20 Cr",
  "individual_predictions": {
    "xgboost": 68.5,
    "random_forest": 66.8,
    "linear_regression": 66.3
  },
  "consensus": 0.92,
  "std_deviation": 1.2,
  "uncertainty_range": {
    "lower": 66.0,
    "upper": 68.4
  }
}
```

**Response Details**:
- `ensemble_price`: Average of 3 models
- `individual_predictions`: Each model's prediction
- `consensus`: Higher = more agreement between models
- `std_deviation`: Variation between model predictions

---

### 3. House Price Service Health

**Endpoint**: `GET /credit/collateral/health`

**Purpose**: Check if house price prediction service is ready

**Response (Success - 200)**:
```json
{
  "status": "healthy",
  "models_loaded": ["xgboost", "random_forest", "linear_regression"],
  "features_loaded": true,
  "num_features": 9,
  "model_dir": "C:/path/to/backend/models"
}
```

---

## 📈 Market Risk Endpoints

### 1. Get Current Market Conditions

**Endpoint**: `GET /credit/market/conditions`

**Purpose**: Retrieve current market volatility, trend, and stress indicators

**Parameters**: None

**Response (Success - 200)**:
```json
{
  "status": "success",
  "volatility_30d": 0.1542,
  "volatility_regime": "medium",
  "momentum_30d": 0.00052,
  "market_trend": "bullish",
  "vix_equivalent": 24.47,
  "market_stress": 0,
  "date": "2024-05-18"
}
```

**Response Details**:
- `volatility_30d`: 30-day rolling std (0-1, higher=more volatile)
- `volatility_regime`: "low" (<12%) / "medium" (12-18%) / "high" (>18%)
- `momentum_30d`: Average daily return (0.001 = 0.1%)
- `market_trend`: "bullish" / "neutral" / "bearish"
- `vix_equivalent`: Volatility index (0-100, like VIX)
- `market_stress`: Binary (0=normal, 1=stressed)

**cURL Example**:
```bash
curl http://localhost:8000/credit/market/conditions
```

---

### 2. Get Sector Analysis

**Endpoint**: `GET /credit/market/sector-analysis`

**Purpose**: Get individual stock/sector volatility and performance

**Parameters**: None

**Response (Success - 200)**:
```json
{
  "status": "success",
  "sectors": [
    {
      "symbol": "BHARTIARTL",
      "volatility_30d": 0.1823,
      "momentum_30d": 0.00043,
      "latest_return": 0.0234,
      "performance": "up"
    },
    {
      "symbol": "BRITANNIA",
      "volatility_30d": 0.1456,
      "momentum_30d": -0.00012,
      "latest_return": -0.0156,
      "performance": "down"
    }
  ],
  "avg_volatility": 0.1612,
  "market_health_score": 73.4,
  "num_sectors": 5
}
```

**Response Details**:
- `sectors`: List of analyzed stocks
- `volatility_30d`: Stock-specific 30-day volatility
- `latest_return`: Most recent daily return %
- `performance`: "up" or "down"
- `market_health_score`: 0-100 (higher=healthier market)

---

### 3. Market Risk Service Health

**Endpoint**: `GET /credit/market/health`

**Purpose**: Check market risk analysis service status

**Response (Success - 200)**:
```json
{
  "status": "healthy",
  "market_metrics_loaded": true,
  "sector_data_loaded": true,
  "portfolio_optimizer_loaded": true,
  "market_dir": "C:/path/to/datasets/processed"
}
```

---

## 💼 Portfolio Endpoints

### 1. Get Portfolio Recommendation

**Endpoint**: `POST /credit/portfolio/recommend`

**Purpose**: Get personalized asset allocation based on risk profile and income

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| risk_level | string | "moderate" | "conservative" / "moderate" / "aggressive" |
| income | float | 500000 | Annual income (INR) |

**Request**:
```bash
POST /credit/portfolio/recommend?risk_level=moderate&income=500000
```

**Response (Success - 200)**:
```json
{
  "status": "success",
  "risk_level": "moderate",
  "allocation": {
    "equity": "50%",
    "bonds": "30%",
    "cash": "10%",
    "gold": "10%"
  },
  "allocation_raw": {
    "equity": 0.50,
    "bonds": 0.30,
    "cash": 0.10,
    "gold": 0.10
  },
  "monthly_investment": 6250.0,
  "annual_investment": 75000.0,
  "expected_annual_return": 8.2,
  "volatility": 9.24,
  "sharpe_ratio": 0.53,
  "notes": "Balanced approach for long-term growth. Suitable for middle-aged investors with medium risk tolerance."
}
```

**Response Details**:
- `allocation`: Percentage strings for display
- `allocation_raw`: Raw decimal values for calculations
- `monthly_investment`: Recommended monthly investment (15% of annual income)
- `expected_annual_return`: Portfolio expected return %
- `volatility`: Portfolio standard deviation %
- `sharpe_ratio`: Risk-adjusted return metric (higher=better)

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/credit/portfolio/recommend?risk_level=aggressive&income=750000"
```

**Python Example**:
```python
import requests

url = "http://localhost:8000/credit/portfolio/recommend"
params = {
    "risk_level": "aggressive",
    "income": 750000
}

response = requests.post(url, params=params)
result = response.json()

print(f"Risk Level: {result['risk_level']}")
print(f"Allocation: {result['allocation']}")
print(f"Expected Return: {result['expected_annual_return']}%")
print(f"Monthly Investment: ₹{result['monthly_investment']}")
```

---

### 2. Analyze Market-Adjusted Loan Default Risk

**Endpoint**: `POST /credit/market/loan-default-risk`

**Purpose**: Calculate loan default risk considering current market conditions

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| borrower_income | float | 500000 | Annual income (INR) |

**Request**:
```bash
POST /credit/market/loan-default-risk?borrower_income=500000
```

**Response (Success - 200)**:
```json
{
  "status": "success",
  "macro_risk_score": 0.487,
  "market_adjusted_risk": 0.452,
  "risk_category": "moderate",
  "vix_equivalent": 24.47,
  "volatility_factor": 15.42,
  "income_stability_score": 1.0,
  "recommendation": "Standard loan terms recommended"
}
```

**Response Details**:
- `macro_risk_score`: Market-based risk (0-1)
- `market_adjusted_risk`: Combined risk with income (0-1)
- `risk_category`: "low" (<0.3) / "moderate" (0.3-0.6) / "high" (>0.6)
- `volatility_factor`: Current market volatility %
- `income_stability_score`: Borrower income stability (0-1)
- `recommendation`: Action item based on risk level

**Risk Categories**:
- **Low Risk** (<0.3): Favorable lending conditions
- **Moderate Risk** (0.3-0.6): Standard terms
- **High Risk** (>0.6): Higher collateral or stricter terms required

**Python Example**:
```python
import requests

url = "http://localhost:8000/credit/market/loan-default-risk"
params = {"borrower_income": 500000}

response = requests.post(url, params=params)
result = response.json()

print(f"Risk Category: {result['risk_category']}")
print(f"Market-Adjusted Risk: {result['market_adjusted_risk']:.1%}")
print(f"Recommendation: {result['recommendation']}")
```

---

## 🏥 Health & Status

### 1. Overall Health Check

**Note**: Both services provide health checks. Combine results for system status.

**House Price**: `GET /credit/collateral/health`  
**Market Risk**: `GET /credit/market/health`

**Expected healthy response**:
```json
{
  "status": "healthy",
  ...
}
```

---

## ⚠️ Error Codes

### Standard HTTP Codes

| Code | Meaning | Typical Scenario |
|------|---------|------------------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input parameters |
| 503 | Service Unavailable | Model not loaded |
| 500 | Internal Server Error | Unexpected error |

### Error Response Format

```json
{
  "status": "error",
  "message": "Description of what went wrong"
}
```

### Common Errors

**Model Not Loaded**:
```json
{
  "detail": "House price model not loaded. Please try again later."
}
```

**Invalid Risk Level**:
```json
{
  "detail": "Risk level must be 'conservative', 'moderate', or 'aggressive'"
}
```

**Negative Income**:
```json
{
  "detail": "Income must be positive"
}
```

**Missing Features**:
```json
{
  "message": "Invalid input features"
}
```

---

## 📦 Response Schemas

### House Price Response
```typescript
interface HousePriceResponse {
  status: "success" | "error";
  predicted_price?: number;          // Price in Crores
  predicted_price_formatted?: string;
  confidence?: number;               // 0-1
  uncertainty?: number;              // ±value
  uncertainty_range?: {
    lower: number;
    upper: number;
  };
  model_used?: string;              // "xgboost" | "random_forest" | "linear_regression"
  input_features?: object;
  message?: string;                 // Error message
}
```

### Market Conditions Response
```typescript
interface MarketConditionsResponse {
  status: "success" | "error";
  volatility_30d?: number;          // 0-1
  volatility_regime?: string;       // "low" | "medium" | "high"
  momentum_30d?: number;            // Daily avg return
  market_trend?: string;            // "bullish" | "neutral" | "bearish"
  vix_equivalent?: number;          // 0-100
  market_stress?: number;           // 0 or 1
  date?: string;                    // YYYY-MM-DD
  message?: string;                 // Error message
}
```

### Portfolio Response
```typescript
interface PortfolioResponse {
  status: "success" | "error";
  risk_level?: string;
  allocation?: {
    equity: string;                 // "50%"
    bonds: string;                  // "30%"
    cash: string;                   // "10%"
    gold: string;                   // "10%"
  };
  allocation_raw?: {
    equity: number;
    bonds: number;
    cash: number;
    gold: number;
  };
  monthly_investment?: number;
  annual_investment?: number;
  expected_annual_return?: number;  // %
  volatility?: number;              // %
  sharpe_ratio?: number;
  notes?: string;
  message?: string;                 // Error message
}
```

---

## 🚦 Rate Limiting & Best Practices

### Rate Limits
- **Current**: No hard limit (dev/test environment)
- **Production**: Recommended 100 requests/minute per client

### Best Practices

1. **Reuse Results**:
   ```python
   # Cache market conditions if fetched multiple times in same session
   conditions = requests.get('/credit/market/conditions').json()
   # Use same conditions for multiple portfolio calls
   ```

2. **Batch Operations**:
   ```python
   # For multiple properties, send sequentially (not parallel)
   properties = [...]
   for prop in properties:
       result = requests.post('/credit/collateral/estimate-house-price', 
                             json=prop)
   ```

3. **Error Handling**:
   ```python
   import requests
   
   try:
       response = requests.post(url, json=payload, timeout=5)
       response.raise_for_status()
       result = response.json()
   except requests.exceptions.Timeout:
       print("Request timed out")
   except requests.exceptions.HTTPError as e:
       print(f"HTTP Error: {e.response.status_code}")
   ```

4. **Monitor Health**:
   ```python
   # Check service health before making requests
   health = requests.get('/credit/collateral/health').json()
   if health['status'] != 'healthy':
       print("House Price service unavailable")
   ```

---

## 📞 Support

For API issues:
1. Check error response message
2. Verify input parameters match schema
3. Check service health endpoints
4. Review logs in `backend/` directory

---

**Last Updated**: May 18, 2026  
**API Version**: 1.0  
**Status**: Production Ready
