"""Past-only, seven-day rolling-origin evaluation with frozen selection windows."""
from __future__ import annotations

import math
from datetime import date, timedelta
import numpy as np

MODELS = ("last_week", "trailing_28", "weekday_8w", "ridge_ar")
HORIZON = 7


def features(history, index):
    return [*np.log1p([history[-k] for k in (1, 2, 7, 14, 21, 28)]),
            np.log1p(np.mean(history[-7:])), np.log1p(np.mean(history[-28:])),
            math.sin(2 * math.pi * index / 7), math.cos(2 * math.pi * index / 7)]


def predict(history, model, horizon=HORIZON):
    """Only accepts history. Calendar index zero is the fixed dataset start."""
    y = np.asarray(history, dtype=float)
    if len(y) < 56 or not np.isfinite(y).all() or (y < 0).any():
        raise ValueError("need at least 56 finite nonnegative observations")
    if model == "last_week":
        return np.resize(y[-7:], horizon)
    if model == "trailing_28":
        return np.repeat(y[-28:].mean(), horizon)
    if model == "weekday_8w":
        return np.array([y[-56:][np.arange(len(y)-56, len(y)) % 7 == (len(y)+h) % 7].mean()
                         for h in range(horizon)])
    if model != "ridge_ar":
        raise ValueError(f"unknown model: {model}")
    start = max(28, len(y) - 112)
    x = np.array([features(y[:i], i) for i in range(start, len(y))])
    target = np.log1p(y[start:])
    mean, scale = x.mean(axis=0), x.std(axis=0)
    scale[scale == 0] = 1
    design = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    penalty = np.eye(design.shape[1]) * 10
    penalty[0, 0] = 0
    coef = np.linalg.solve(design.T @ design + penalty, design.T @ target)
    extended, output = list(y), []
    for _ in range(horizon):
        f = np.r_[1, (np.array(features(extended, len(extended))) - mean) / scale]
        value = float(np.expm1(np.clip(f @ coef, 0, np.log1p(max(y.max() * 3, 1)))))
        output.append(value)
        extended.append(value)
    return np.array(output)


def interval_radius(residuals, level=.8):
    """Finite-sample order statistic; time dependence prevents a coverage guarantee."""
    r = np.asarray(residuals)
    if r.ndim != 2 or r.shape[0] < 5 or not np.isfinite(r).all():
        raise ValueError("insufficient or invalid calibration residuals")
    rank = min(r.shape[0], math.ceil((r.shape[0] + 1) * level))
    return np.sort(r, axis=0)[rank - 1]


def metrics(actual, prediction):
    a, p = np.asarray(actual), np.asarray(prediction)
    error = a-p
    return {"mae": float(np.abs(error).mean()), "rmse": float(np.sqrt((error**2).mean())),
            "wape": float(np.abs(error).sum()/a.sum()) if a.sum() else None}


def paired_block_interval(deltas, seed=42):
    """Exploratory paired moving-block bootstrap of weekly MAE differences."""
    values = np.asarray(deltas)
    rng = np.random.default_rng(seed)
    n = len(values)
    boot = []
    for _ in range(2000):
        starts = rng.integers(0, n, math.ceil(n/2))
        indices = np.array([[i, (i+1) % n] for i in starts]).ravel()[:n]
        boot.append(values[indices].mean())
    return np.quantile(boot, [.025, .975]).tolist()


def benchmark(values, start="2025-01-01"):
    y = np.asarray(values, dtype=float)
    first = date.fromisoformat(start)
    select_end = (date(2025, 7, 1)-first).days
    holdout_start = (date(2025, 10, 1)-first).days
    folds = {m: {"selection": [], "calibration": [], "holdout": []} for m in MODELS}
    for origin in range(84, len(y)-HORIZON+1, HORIZON):
        end = origin + HORIZON
        if end <= select_end:
            split = "selection"
        elif origin >= select_end and end <= holdout_start:
            split = "calibration"
        elif origin >= holdout_start:
            split = "holdout"
        else:
            continue  # Never let a forecast block cross a selection boundary.
        for model in MODELS:
            p = predict(y[:origin], model)
            folds[model][split].append({"origin": origin, "actual": y[origin:end], "predicted": p})
    def score(items):
        return metrics(np.concatenate([f["actual"] for f in items]),
                       np.concatenate([f["predicted"] for f in items]))
    selected = min(MODELS, key=lambda m: score(folds[m]["selection"])["mae"])
    results, forecast = [], []
    for model in MODELS:
        calibration = folds[model]["calibration"]
        radius = interval_radius([np.abs(f["actual"]-f["predicted"]) for f in calibration])
        holdout = folds[model]["holdout"]
        coverage = np.concatenate([(f["actual"] >= np.maximum(0, f["predicted"]-radius)) &
                                   (f["actual"] <= f["predicted"]+radius) for f in holdout]).mean()
        width = np.concatenate([f["predicted"]+radius-np.maximum(0, f["predicted"]-radius)
                                for f in holdout]).mean()
        results.append({"model": model, "selection": score(folds[model]["selection"]),
                        "holdout": score(holdout), "coverage_80": float(coverage),
                        "mean_interval_width": float(width), "holdout_origins": len(holdout),
                        "calibration_origins": len(calibration)})
        if model == selected:
            p = predict(y, selected)
            forecast = [{"date": (first+timedelta(days=len(y)+h)).isoformat(),
                         "prediction": float(v), "lower": float(max(0, v-radius[h])),
                         "upper": float(v+radius[h])} for h, v in enumerate(p)]
    winner, baseline = folds[selected]["holdout"], folds["last_week"]["holdout"]
    deltas = [float(np.abs(a["actual"]-a["predicted"]).mean()-
                    np.abs(b["actual"]-b["predicted"]).mean()) for a,b in zip(winner, baseline)]
    ci = paired_block_interval(deltas)
    selected_mae = next(r["holdout"]["mae"] for r in results if r["model"] == selected)
    base_mae = results[0]["holdout"]["mae"]
    skill = 1-selected_mae/base_mae if base_mae else None
    promoted = selected != "last_week" and skill is not None and skill >= .05 and ci[1] < 0
    predictions = [{"model": m, "split": split,
                    "origin": (first+timedelta(days=f["origin"])).isoformat(),
                    "train_end": (first+timedelta(days=f["origin"]-1)).isoformat(),
                    "actual": f["actual"].tolist(), "predicted": f["predicted"].tolist()}
                   for m in MODELS for split, items in folds[m].items() for f in items]
    return {"target": "quality-filtered vegetation active H3 resolution-8 cell-days per UTC day",
            "selected_model": selected, "selection_rule": "lowest pre-July rolling-origin MAE",
            "selection_end": "2025-06-30", "calibration_window": ["2025-07-01", "2025-09-30"],
            "holdout_window": ["2025-10-01", "2025-12-31"], "horizon_days": HORIZON,
            "results": results, "skill_vs_last_week": skill, "paired_mae_delta_ci95": ci,
            "promotion_passed": promoted, "forecast": forecast,
            "forecast_status": "archival continuation from 2025-12-31; not a live forecast",
            "interval_caveat": "80% residual bands calibrated July–September; no guaranteed coverage under drift",
            "predictions": predictions}
