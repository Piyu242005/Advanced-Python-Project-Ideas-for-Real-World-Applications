"""
Stock Market Prediction
Generates synthetic OHLCV data, engineers time-series features
(SMA, EMA, RSI, volatility, momentum), then trains and evaluates
Linear Regression and Random Forest models side-by-side.

Dependencies:
    pip install pandas numpy scikit-learn
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# ── Generate synthetic stock data ────────────────────────────────────────────

def generate_stock_data(n_days: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", periods=n_days, freq="B")

    # Geometric Brownian Motion
    returns = rng.normal(loc=0.0003, scale=0.015, size=n_days)
    price = 150.0 * np.exp(np.cumsum(returns))

    high  = price * (1 + rng.uniform(0.001, 0.02, n_days))
    low   = price * (1 - rng.uniform(0.001, 0.02, n_days))
    open_ = price * (1 + rng.normal(0, 0.005, n_days))
    volume = rng.integers(1_000_000, 10_000_000, n_days).astype(float)

    return pd.DataFrame({
        "Date": dates, "Open": open_, "High": high,
        "Low": low, "Close": price, "Volume": volume,
    }).set_index("Date")


# ── Feature engineering ───────────────────────────────────────────────────────

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["Close"]

    # Moving averages
    df["SMA_5"]  = c.rolling(5).mean()
    df["SMA_20"] = c.rolling(20).mean()
    df["EMA_12"] = c.ewm(span=12, adjust=False).mean()
    df["EMA_26"] = c.ewm(span=26, adjust=False).mean()
    df["MACD"]   = df["EMA_12"] - df["EMA_26"]

    # RSI (14-period)
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI_14"] = 100 - (100 / (1 + rs))

    # Volatility & momentum
    df["Volatility_10"] = c.rolling(10).std()
    df["Momentum_5"]    = c.pct_change(5)
    df["Momentum_20"]   = c.pct_change(20)

    # Price ratios
    df["High_Low_Ratio"]   = df["High"] / df["Low"]
    df["Close_Open_Ratio"] = df["Close"] / df["Open"]
    df["Volume_SMA_10"]    = df["Volume"].rolling(10).mean()

    # Target: next-day close
    df["Target"] = c.shift(-1)

    return df.dropna()


# ── Train & evaluate ──────────────────────────────────────────────────────────

FEATURE_COLS = [
    "Open", "High", "Low", "Close", "Volume",
    "SMA_5", "SMA_20", "EMA_12", "EMA_26", "MACD",
    "RSI_14", "Volatility_10", "Momentum_5", "Momentum_20",
    "High_Low_Ratio", "Close_Open_Ratio", "Volume_SMA_10",
]


def evaluate(name: str, y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    return {"Model": name, "MAE": mae, "RMSE": rmse, "R²": r2}


def run_prediction(df: pd.DataFrame):
    X = df[FEATURE_COLS]
    y = df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    results = []

    # Linear Regression
    lr = LinearRegression()
    lr.fit(X_train_s, y_train)
    results.append(evaluate("Linear Regression", y_test, lr.predict(X_test_s)))

    # Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    results.append(evaluate("Random Forest    ", y_test, rf.predict(X_test)))

    return pd.DataFrame(results), rf, X_test


def feature_importance(rf: RandomForestRegressor) -> pd.Series:
    fi = pd.Series(rf.feature_importances_, index=FEATURE_COLS)
    return fi.sort_values(ascending=False).head(8)


# ── Display ───────────────────────────────────────────────────────────────────

def display(results_df: pd.DataFrame, fi: pd.Series, df: pd.DataFrame):
    print("\n" + "═" * 56)
    print("  📈  STOCK MARKET PREDICTION RESULTS")
    print("═" * 56)
    print(f"\n  Dataset : {len(df)} trading days  |  Features: {len(FEATURE_COLS)}")
    print(f"  Split   : 80% train / 20% test\n")

    print(f"  {'Model':<22} {'MAE':>8} {'RMSE':>8} {'R²':>8}")
    print("  " + "─" * 50)
    for _, row in results_df.iterrows():
        bar = "█" * int(row["R²"] * 20)
        print(f"  {row['Model']:<22} {row['MAE']:>8.4f} {row['RMSE']:>8.4f} {row['R²']:>8.4f}  {bar}")

    print("\n  🌲  Top Features (Random Forest):")
    print("  " + "─" * 36)
    for feat, imp in fi.items():
        bar = "▓" * int(imp * 60)
        print(f"  {feat:<18} {imp:.4f}  {bar}")

    print("\n" + "═" * 56)
    best = results_df.loc[results_df["R²"].idxmax(), "Model"].strip()
    print(f"  ✅  Best model: {best}")
    print("═" * 56)


def main():
    print("Running Stock Market Prediction …")
    raw   = generate_stock_data(n_days=500)
    df    = add_features(raw)
    results_df, rf, X_test = run_prediction(df)
    fi    = feature_importance(rf)
    display(results_df, fi, df)


if __name__ == "__main__":
    main()
