from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import loguniform, randint, uniform
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit, cross_val_score
from xgboost import XGBClassifier


warnings.filterwarnings("ignore")


@dataclass(frozen=True)
class WorkflowConfig:
    data_path: Path = Path("Exam3/CSI300_2005_2026.csv")
    start_date: str = "2010-01-01"
    target_threshold: float = 0.0015
    test_size: float = 0.20
    random_state: int = 42
    cv_splits: int = 5
    cv_gap: int = 1


def build_features(config: WorkflowConfig) -> tuple[pd.DataFrame, list[str]]:
    df = (
        pd.read_csv(config.data_path, parse_dates=["Date"])
        .sort_values("Date")
        .set_index("Date")
    )
    out = df.copy()

    out["log_ret_1"] = np.log(out["Adj Close"]).diff()
    out["simple_ret_1"] = out["Adj Close"].pct_change()
    out["intraday_ret"] = out["Close"] / out["Open"] - 1
    out["range_pct"] = out["High"] / out["Low"] - 1
    out["gap_ret"] = out["Open"] / out["Close"].shift(1) - 1
    out["upper_shadow"] = (
        out["High"] - out[["Open", "Close"]].max(axis=1)
    ) / out["Close"]
    out["lower_shadow"] = (
        out[["Open", "Close"]].min(axis=1) - out["Low"]
    ) / out["Close"]
    out["body_pct"] = (out["Close"] - out["Open"]) / out["Open"]
    out["close_pos"] = (out["Close"] - out["Low"]) / (
        out["High"] - out["Low"]
    ).replace(0, np.nan)
    out["volume_ret"] = np.log(out["Volume"]).diff()
    out["dow"] = out.index.dayofweek

    for window in [2, 3, 5, 10, 20, 40, 60, 120]:
        out[f"ret_sum_{window}"] = out["log_ret_1"].rolling(window).sum()
        out[f"ret_mean_{window}"] = out["log_ret_1"].rolling(window).mean()
        out[f"volatility_{window}"] = out["log_ret_1"].rolling(window).std()
        out[f"ma_ratio_{window}"] = (
            out["Adj Close"] / out["Adj Close"].rolling(window).mean() - 1
        )
        out[f"volume_z_{window}"] = (
            out["Volume"] - out["Volume"].rolling(window).mean()
        ) / out["Volume"].rolling(window).std()
        out[f"rolling_min_ret_{window}"] = out["log_ret_1"].rolling(window).min()
        out[f"rolling_max_ret_{window}"] = out["log_ret_1"].rolling(window).max()

    for window in [6, 14, 21]:
        delta = out["Adj Close"].diff()
        gain = delta.clip(lower=0).rolling(window).mean()
        loss = (-delta.clip(upper=0)).rolling(window).mean()
        rs = gain / loss.replace(0, np.nan)
        out[f"rsi_{window}"] = 100 - (100 / (1 + rs))

    ema12 = out["Adj Close"].ewm(span=12, adjust=False).mean()
    ema26 = out["Adj Close"].ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    true_range = pd.concat(
        [
            out["High"] - out["Low"],
            (out["High"] - out["Close"].shift(1)).abs(),
            (out["Low"] - out["Close"].shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    for window in [14, 20]:
        out[f"atr_{window}"] = true_range.rolling(window).mean() / out["Adj Close"]

    out["next_log_ret"] = out["log_ret_1"].shift(-1)
    out["target"] = (out["next_log_ret"] > config.target_threshold).astype(float)
    out.loc[out["next_log_ret"].isna(), "target"] = np.nan

    excluded = {
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
        "next_log_ret",
        "target",
    }
    feature_cols = [col for col in out.columns if col not in excluded]
    data = (
        out.loc[config.start_date :, feature_cols + ["target", "next_log_ret"]]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )
    return data, feature_cols


def train_test_split_time(
    data: pd.DataFrame, feature_cols: list[str], config: WorkflowConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.DataFrame, pd.DataFrame]:
    n_test = int(np.ceil(len(data) * config.test_size))
    train = data.iloc[:-n_test]
    test = data.iloc[-n_test:]
    return (
        train[feature_cols],
        test[feature_cols],
        train["target"].astype(int),
        test["target"].astype(int),
        train,
        test,
    )


def correlation_prune(
    X_train: pd.DataFrame, max_corr: float = 0.98
) -> tuple[list[str], list[str]]:
    corr = X_train.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    dropped = [col for col in upper.columns if any(upper[col] > max_corr)]
    kept = [col for col in X_train.columns if col not in dropped]
    return kept, dropped


def base_xgb_params(y_train: pd.Series, config: WorkflowConfig) -> dict:
    negative, positive = np.bincount(y_train)
    scale_pos_weight = negative / positive if positive else 1.0
    return {
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "tree_method": "hist",
        "random_state": config.random_state,
        "n_jobs": -1,
        "scale_pos_weight": scale_pos_weight,
    }


def regularized_xgb(y_train: pd.Series, config: WorkflowConfig) -> XGBClassifier:
    return XGBClassifier(
        **base_xgb_params(y_train, config),
        n_estimators=120,
        max_depth=2,
        learning_rate=0.035,
        subsample=0.75,
        colsample_bytree=0.75,
        min_child_weight=5,
        gamma=1.0,
        reg_alpha=0.5,
        reg_lambda=3.0,
    )


def cv_object(config: WorkflowConfig) -> TimeSeriesSplit:
    return TimeSeriesSplit(n_splits=config.cv_splits, gap=config.cv_gap)


def feature_selection_funnel(
    X_train: pd.DataFrame, y_train: pd.Series, config: WorkflowConfig
) -> dict:
    corr_features, corr_dropped = correlation_prune(X_train)

    mi_scores = pd.Series(
        mutual_info_classif(
            X_train[corr_features],
            y_train,
            random_state=config.random_state,
            discrete_features=False,
        ),
        index=corr_features,
    ).sort_values(ascending=False)

    cv = cv_object(config)
    subset_rows = []
    subset_sizes = [10, 15, 20, 25, 30, 35, 40, 50, len(mi_scores)]
    for size in sorted(set(min(size, len(mi_scores)) for size in subset_sizes)):
        cols = list(mi_scores.head(size).index)
        scores = cross_val_score(
            regularized_xgb(y_train, config),
            X_train[cols],
            y_train,
            cv=cv,
            scoring="roc_auc",
            n_jobs=1,
        )
        subset_rows.append(
            {
                "n_features": size,
                "cv_mean_auc": scores.mean(),
                "cv_std_auc": scores.std(),
                "features": cols,
            }
        )
    wrapper_table = pd.DataFrame(subset_rows)
    wrapper_choice = wrapper_table.sort_values(
        ["cv_mean_auc", "n_features"], ascending=[False, True]
    ).iloc[0]
    wrapper_features = list(wrapper_choice["features"])

    embedded_params = regularized_xgb(y_train, config).get_params()
    embedded_params["importance_type"] = "gain"
    embedded_model = XGBClassifier(**embedded_params)
    embedded_model.fit(X_train[wrapper_features], y_train)
    gain_scores = pd.Series(
        embedded_model.feature_importances_, index=wrapper_features
    ).sort_values(ascending=False)

    embedded_rows = []
    embedded_sizes = [10, 15, 20, 25, 30, 35, 40, len(gain_scores)]
    for size in sorted(set(min(size, len(gain_scores)) for size in embedded_sizes)):
        cols = list(gain_scores.head(size).index)
        scores = cross_val_score(
            regularized_xgb(y_train, config),
            X_train[cols],
            y_train,
            cv=cv,
            scoring="roc_auc",
            n_jobs=1,
        )
        embedded_rows.append(
            {
                "n_features": size,
                "cv_mean_auc": scores.mean(),
                "cv_std_auc": scores.std(),
                "features": cols,
            }
        )
    embedded_table = pd.DataFrame(embedded_rows)
    embedded_choice = embedded_table.sort_values(
        ["cv_mean_auc", "n_features"], ascending=[False, True]
    ).iloc[0]
    final_features = list(embedded_choice["features"])

    return {
        "corr_features": corr_features,
        "corr_dropped": corr_dropped,
        "mi_scores": mi_scores,
        "wrapper_table": wrapper_table.drop(columns=["features"]),
        "wrapper_features": wrapper_features,
        "gain_scores": gain_scores,
        "embedded_table": embedded_table.drop(columns=["features"]),
        "final_features": final_features,
    }


def select_decision_threshold(y_true: pd.Series, probabilities: np.ndarray) -> float:
    fpr, tpr, thresholds = roc_curve(y_true, probabilities)
    finite = np.isfinite(thresholds)
    if not finite.any():
        return 0.5
    youden_j = tpr[finite] - fpr[finite]
    return float(thresholds[finite][np.argmax(youden_j)])


def evaluate_classifier(
    model: XGBClassifier,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    model.fit(X_train, y_train)
    train_proba = model.predict_proba(X_train)[:, 1]
    test_proba = model.predict_proba(X_test)[:, 1]
    threshold = select_decision_threshold(y_train, train_proba)
    y_pred = (test_proba >= threshold).astype(int)
    return {
        "model": model,
        "threshold": threshold,
        "train_auc": roc_auc_score(y_train, train_proba),
        "test_auc": roc_auc_score(y_test, test_proba),
        "accuracy": accuracy_score(y_test, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(
            y_test, y_pred, digits=3, output_dict=False
        ),
        "test_proba": test_proba,
        "y_pred": y_pred,
    }


def tune_xgb(
    X_train: pd.DataFrame, y_train: pd.Series, config: WorkflowConfig, n_iter: int = 50
) -> RandomizedSearchCV:
    param_dist = {
        "n_estimators": randint(60, 350),
        "max_depth": randint(1, 4),
        "learning_rate": loguniform(0.01, 0.12),
        "subsample": uniform(0.60, 0.40),
        "colsample_bytree": uniform(0.60, 0.40),
        "min_child_weight": randint(2, 18),
        "gamma": uniform(0, 6),
        "reg_alpha": loguniform(1e-4, 8),
        "reg_lambda": loguniform(0.5, 20),
    }
    search = RandomizedSearchCV(
        estimator=XGBClassifier(**base_xgb_params(y_train, config)),
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="roc_auc",
        cv=cv_object(config),
        random_state=config.random_state,
        n_jobs=1,
        refit=True,
    )
    search.fit(X_train, y_train)
    return search


def backtest_signal(
    test_frame: pd.DataFrame, y_pred: np.ndarray, trading_days: int = 252
) -> pd.DataFrame:
    signal = pd.Series(y_pred, index=test_frame.index, name="signal")
    index_returns = test_frame["next_log_ret"]
    strategy_returns = signal * index_returns

    def performance(log_returns: pd.Series, exposure: float) -> pd.Series:
        wealth = np.exp(log_returns.cumsum())
        total_return = wealth.iloc[-1] - 1
        annual_return = wealth.iloc[-1] ** (trading_days / len(log_returns)) - 1
        annual_volatility = log_returns.std() * np.sqrt(trading_days)
        sharpe = (
            annual_return / annual_volatility if annual_volatility > 0 else np.nan
        )
        drawdown = wealth / wealth.cummax() - 1
        return pd.Series(
            {
                "total_return": total_return,
                "annual_return": annual_return,
                "annual_volatility": annual_volatility,
                "sharpe": sharpe,
                "max_drawdown": drawdown.min(),
                "exposure": exposure,
            }
        )

    return pd.DataFrame(
        {
            "strategy": performance(strategy_returns, signal.mean()),
            "buy_hold": performance(index_returns, 1.0),
        }
    )


def run_workflow(config: WorkflowConfig = WorkflowConfig()) -> dict:
    data, feature_cols = build_features(config)
    X_train, X_test, y_train, y_test, train_frame, test_frame = train_test_split_time(
        data, feature_cols, config
    )
    selection = feature_selection_funnel(X_train, y_train, config)
    final_features = selection["final_features"]

    base_eval = evaluate_classifier(
        regularized_xgb(y_train, config),
        X_train[final_features],
        y_train,
        X_test[final_features],
        y_test,
    )
    search = tune_xgb(X_train[final_features], y_train, config)
    tuned_eval = evaluate_classifier(
        search.best_estimator_,
        X_train[final_features],
        y_train,
        X_test[final_features],
        y_test,
    )
    backtest = backtest_signal(test_frame, tuned_eval["y_pred"])

    return {
        "config": config,
        "data": data,
        "train_frame": train_frame,
        "test_frame": test_frame,
        "feature_cols": feature_cols,
        "selection": selection,
        "final_features": final_features,
        "base_eval": base_eval,
        "search": search,
        "tuned_eval": tuned_eval,
        "backtest": backtest,
    }


if __name__ == "__main__":
    result = run_workflow()
    config = result["config"]
    train_frame = result["train_frame"]
    test_frame = result["test_frame"]
    selection = result["selection"]
    tuned_eval = result["tuned_eval"]

    print("Config:", config)
    print(
        "Train:",
        train_frame.index.min().date(),
        "to",
        train_frame.index.max().date(),
        "rows",
        len(train_frame),
    )
    print(
        "Test :",
        test_frame.index.min().date(),
        "to",
        test_frame.index.max().date(),
        "rows",
        len(test_frame),
    )
    print("Initial features:", len(result["feature_cols"]))
    print("Correlation dropped:", len(selection["corr_dropped"]))
    print("\nWrapper CV:")
    print(selection["wrapper_table"].round(4).to_string(index=False))
    print("\nEmbedded CV:")
    print(selection["embedded_table"].round(4).to_string(index=False))
    print("\nFinal features:")
    print(result["final_features"])
    print("\nBest params:")
    print(result["search"].best_params_)
    print("\nTuned metrics:")
    print(
        {
            "threshold": round(tuned_eval["threshold"], 4),
            "train_auc": round(tuned_eval["train_auc"], 4),
            "test_auc": round(tuned_eval["test_auc"], 4),
            "accuracy": round(tuned_eval["accuracy"], 4),
            "balanced_accuracy": round(tuned_eval["balanced_accuracy"], 4),
        }
    )
    print("\nConfusion matrix:")
    print(tuned_eval["confusion_matrix"])
    print("\nClassification report:")
    print(tuned_eval["classification_report"])
    print("\nBacktest:")
    print(result["backtest"].round(4).to_string())
