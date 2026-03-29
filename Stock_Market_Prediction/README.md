# 📈 Stock Market Prediction

## Purpose
Predict the next day's closing stock price using machine learning models trained on engineered time-series features.

## Use Case
Algorithmic trading research, financial data science experiments, or learning ML on real-world style datasets.

## Tech Used
| Library | Role |
|:---|:---|
| `pandas` | Data generation, feature engineering (SMA, EMA, RSI, MACD) |
| `NumPy` | Numerical computation and Geometric Brownian Motion simulation |
| `scikit-learn` | Linear Regression + Random Forest models, train/test split, scaling |

## Run
```bash
pip install -r requirements.txt
python main.py
```

> Outputs model accuracy (MAE, RMSE, R²) and top feature importances side by side.
