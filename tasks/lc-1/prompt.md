You are given a large Python codebase (30 files, ~260KB) for an automated ML experiment pipeline. The full codebase is provided below. Answer these 5 questions precisely, citing specific file names and line references.

**Questions:**

1. **Data flow**: Trace the complete data pipeline from raw data loading to final submission CSV. Which files handle each stage (load → preprocess → feature engineering → train → predict → submit)? List the exact function names and their files.

2. **Model architectures**: List ALL distinct model architectures used across the codebase (e.g., XGBoost, LightGBM, neural nets, etc.). For each, cite the file and the configuration parameters used (learning rate, number of estimators, etc.).

3. **Cross-validation strategy**: What cross-validation strategies are used? Are there any data leakage risks in how the folds are constructed? Cite specific code.

4. **Ensemble methods**: How are individual model predictions combined into the final submission? Describe each ensemble/blending technique used, citing the specific files and functions.

5. **Bug hunt**: Identify any bugs, anti-patterns, or potential issues in the codebase. For each, cite the file, describe the issue, and suggest a fix. Find at least 3.

---

**CODEBASE:**

# ===== FILE: evaluate.py =====
"""
Fixed evaluation script — do not modify.
Syncs experiment.py to GPU server, runs remotely, fetches results back.
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# GPU server config
GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET_SECONDS = 480  # 8 minutes


def main():
    start = time.time()

    try:
        # 1. Sync experiment.py to GPU server
        subprocess.run(
            ["scp", str(BASE_DIR / "experiment.py"), f"{GPU_HOST}:{GPU_WORKDIR}/experiment.py"],
            check=True, capture_output=True, timeout=15,
        )

        # 2. Run on GPU server with timeout
        cmd = (
            f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
            f"timeout {TIME_BUDGET_SECONDS} python3 -c '"
            f"from experiment import run_experiment; import json; "
            f"auc = run_experiment(); print(json.dumps({{\"auc\": auc}}))"
            f"'"
        )
        proc = subprocess.run(
            ["ssh", GPU_HOST, cmd],
            capture_output=True, text=True, timeout=TIME_BUDGET_SECONDS + 30,
        )

        elapsed = time.time() - start

        if proc.returncode == 0:
            # Parse AUC from last line of stdout
            output_lines = proc.stdout.strip().split("\n")
            result_line = output_lines[-1]
            remote_result = json.loads(result_line)
            auc = remote_result["auc"]
            result = {
                "auc": auc,
                "elapsed_seconds": round(elapsed, 1),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success",
            }
            print(f"✅ AUC: {auc:.6f} ({elapsed:.1f}s)")
        elif proc.returncode == 124:
            result = {
                "auc": None,
                "elapsed_seconds": round(elapsed, 1),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "timeout",
            }
            print(f"⏰ Timeout after {elapsed:.1f}s")
        else:
            result = {
                "auc": None,
                "elapsed_seconds": round(elapsed, 1),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": proc.stderr[-500:] if proc.stderr else "unknown error",
            }
            print(f"❌ Error (exit {proc.returncode}): {proc.stderr[-200:]}")

    except Exception as e:
        elapsed = time.time() - start
        result = {
            "auc": None,
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "error": str(e),
        }
        print(f"❌ Error: {e}")

    # Save result
    (RESULTS_DIR / "latest.json").write_text(json.dumps(result, indent=2))

    # Append to history
    history_path = RESULTS_DIR / "history.jsonl"
    with history_path.open("a") as f:
        f.write(json.dumps(result) + "\n")

    return result.get("auc")


if __name__ == "__main__":
    main()

# ===== FILE: exp_combo_7920.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        bagging_temperature=0.3,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: exp_g0_21449.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "contract_payment", "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    df["contract_payment"] = df["Contract"].astype(str) + "_" + df["PaymentMethod"].astype(str)
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: exp_g0_50933.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        min_data_in_leaf=5,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: exp_g1_26062.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)
            for g in GROUP_COLS:
                for n in NUM_COLS:
                    std_map = Xtr.groupby(g)[n].std().to_dict()
                    Xtr[f"gs_std_{n}_by_{g}"] = Xtr[g].map(std_map).astype(np.float32)
                    Xva[f"gs_std_{n}_by_{g}"] = Xva[g].map(std_map).astype(np.float32)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: exp_g1_87278.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        border_count=128,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: exp_g1_88926.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "contract_internet", "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: exp_gpu0.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "contract_payment", "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    df["contract_payment"] = df["Contract"].astype(str) + "_" + df["PaymentMethod"].astype(str)
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: exp_gpu1.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "contract_internet", "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: experiment.py =====
"""
Kaggle S6E3 — AutoResearch Experiment File
Current best: 0.9163 AUC (3-fold fast CV)
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — modify this to add/remove features."""
    df = df.copy()
    # Average monthly spend (TotalCharges / tenure), handling tenure=0
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    # Ratio of monthly charges to total charges (recency of spending)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    # Count of services subscribed to
    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    # Tenure * MonthlyCharges interaction
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=20.0):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def get_model():
    """Return the model — modify hyperparameters here."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=5,
        l2_leaf_reg=5.0,
        random_strength=2.0,
        bagging_temperature=0.3,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=SEED,
        early_stopping_rounds=300,
        task_type="GPU",
        devices="0:1",
    )


def run_experiment():
    """Main experiment — returns AUC score."""
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof = np.zeros(len(X))

    for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
        Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
        ytr, yva = y[tidx], y[vidx]

        # Target encoding
        Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)

        # Prepare features
        fc = [c for c in Xtr.columns if c != ID_COL]
        ci = [fc.index(c) for c in CAT_COLS if c in fc]

        model = get_model()
        model.fit(Xtr[fc], ytr, cat_features=ci,
                  eval_set=(Xva[fc], yva), use_best_model=True)

        vp = model.predict_proba(Xva[fc])[:, 1]
        oof[vidx] = vp
        elapsed = time.time() - job_start
        fold_auc = roc_auc_score(yva, vp)
        print(f"[HEARTBEAT {elapsed/60:.1f}m] Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

    auc = float(roc_auc_score(y, oof))
    return auc


if __name__ == "__main__":
    auc = run_experiment()
    print(f"AUC: {auc:.6f}")

# ===== FILE: experiment_backup.py =====
"""
Kaggle S6E3 — AutoResearch Experiment File
Current best: 0.9163 AUC (3-fold fast CV)
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 3
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — modify this to add/remove features."""
    df = df.copy()
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=20.0):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def get_model():
    """Return the model — modify hyperparameters here."""
    return CatBoostClassifier(
        iterations=3000,
        learning_rate=0.03,
        depth=5,
        l2_leaf_reg=8.0,
        random_strength=3.0,
        bagging_temperature=0.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=SEED,
        early_stopping_rounds=200,
        thread_count=-1,
    )


def run_experiment():
    """Main experiment — returns AUC score."""
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof = np.zeros(len(X))

    for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
        Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
        ytr, yva = y[tidx], y[vidx]

        # Target encoding
        Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)

        # Prepare features
        fc = [c for c in Xtr.columns if c != ID_COL]
        ci = [fc.index(c) for c in CAT_COLS if c in fc]

        model = get_model()
        model.fit(Xtr[fc], ytr, cat_features=ci,
                  eval_set=(Xva[fc], yva), use_best_model=True)

        vp = model.predict_proba(Xva[fc])[:, 1]
        oof[vidx] = vp
        elapsed = time.time() - job_start
        fold_auc = roc_auc_score(yva, vp)
        print(f"[HEARTBEAT {elapsed/60:.1f}m] Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

    auc = float(roc_auc_score(y, oof))
    return auc


if __name__ == "__main__":
    auc = run_experiment()
    print(f"AUC: {auc:.6f}")

# ===== FILE: experiment_best.py =====
"""
Kaggle S6E3 — AutoResearch Experiment File
Current best: 0.9163 AUC (3-fold fast CV)
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — modify this to add/remove features."""
    df = df.copy()
    # Average monthly spend (TotalCharges / tenure), handling tenure=0
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    # Ratio of monthly charges to total charges (recency of spending)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    # Count of services subscribed to
    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    # Tenure * MonthlyCharges interaction
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=20.0):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def get_model():
    """Return the model — modify hyperparameters here."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=5,
        l2_leaf_reg=5.0,
        random_strength=2.0,
        bagging_temperature=0.3,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=SEED,
        early_stopping_rounds=300,
        task_type="GPU",
        devices="0:1",
    )


def run_experiment():
    """Main experiment — returns AUC score."""
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof = np.zeros(len(X))

    for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
        Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
        ytr, yva = y[tidx], y[vidx]

        # Target encoding
        Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)

        # Prepare features
        fc = [c for c in Xtr.columns if c != ID_COL]
        ci = [fc.index(c) for c in CAT_COLS if c in fc]

        model = get_model()
        model.fit(Xtr[fc], ytr, cat_features=ci,
                  eval_set=(Xva[fc], yva), use_best_model=True)

        vp = model.predict_proba(Xva[fc])[:, 1]
        oof[vidx] = vp
        elapsed = time.time() - job_start
        fold_auc = roc_auc_score(yva, vp)
        print(f"[HEARTBEAT {elapsed/60:.1f}m] Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

    auc = float(roc_auc_score(y, oof))
    return auc


if __name__ == "__main__":
    auc = run_experiment()
    print(f"AUC: {auc:.6f}")

# ===== FILE: experiment_gpu0.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: experiment_gpu1.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: experiment_last_good.py =====
"""
Kaggle S6E3 — AutoResearch Experiment File
Current best: 0.9163 AUC (3-fold fast CV)
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — modify this to add/remove features."""
    df = df.copy()
    # Average monthly spend (TotalCharges / tenure), handling tenure=0
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    # Ratio of monthly charges to total charges (recency of spending)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    # Count of services subscribed to
    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    # Tenure * MonthlyCharges interaction
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=20.0):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def get_model():
    """Return the model — modify hyperparameters here."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=5,
        l2_leaf_reg=5.0,
        random_strength=3.0,
        bagging_temperature=0.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=SEED,
        early_stopping_rounds=200,
        task_type="GPU",
        devices="0",
    )


def run_experiment():
    """Main experiment — returns AUC score."""
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof = np.zeros(len(X))

    for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
        Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
        ytr, yva = y[tidx], y[vidx]

        # Target encoding
        Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)

        # Prepare features
        fc = [c for c in Xtr.columns if c != ID_COL]
        ci = [fc.index(c) for c in CAT_COLS if c in fc]

        model = get_model()
        model.fit(Xtr[fc], ytr, cat_features=ci,
                  eval_set=(Xva[fc], yva), use_best_model=True)

        vp = model.predict_proba(Xva[fc])[:, 1]
        oof[vidx] = vp
        elapsed = time.time() - job_start
        fold_auc = roc_auc_score(yva, vp)
        print(f"[HEARTBEAT {elapsed/60:.1f}m] Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

    auc = float(roc_auc_score(y, oof))
    return auc


if __name__ == "__main__":
    auc = run_experiment()
    print(f"AUC: {auc:.6f}")

# ===== FILE: prepare.py =====
"""
One-time data preparation for autoresearch experiments.
Downloads data shards and trains a BPE tokenizer.

Usage:
    python prepare.py                  # full prep (download + tokenizer)
    python prepare.py --num-shards 8   # download only 8 shards (for testing)

Data and tokenizer are stored in ~/.cache/autoresearch/.
"""

import os
import sys
import time
import math
import argparse
import pickle
from multiprocessing import Pool

import requests
import pyarrow.parquet as pq
import rustbpe
import tiktoken
import torch

# ---------------------------------------------------------------------------
# Constants (fixed, do not modify)
# ---------------------------------------------------------------------------

MAX_SEQ_LEN = 2048       # context length
TIME_BUDGET = 300        # training time budget in seconds (5 minutes)
EVAL_TOKENS = 40 * 524288  # number of tokens for val eval

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "autoresearch")
DATA_DIR = os.path.join(CACHE_DIR, "data")
TOKENIZER_DIR = os.path.join(CACHE_DIR, "tokenizer")
BASE_URL = "https://huggingface.co/datasets/karpathy/climbmix-400b-shuffle/resolve/main"
MAX_SHARD = 6542 # the last datashard is shard_06542.parquet
VAL_SHARD = MAX_SHARD  # pinned validation shard (shard_06542)
VAL_FILENAME = f"shard_{VAL_SHARD:05d}.parquet"
VOCAB_SIZE = 8192

# BPE split pattern (GPT-4 style, with \p{N}{1,2} instead of {1,3})
SPLIT_PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,2}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""

SPECIAL_TOKENS = [f"<|reserved_{i}|>" for i in range(4)]
BOS_TOKEN = "<|reserved_0|>"

# ---------------------------------------------------------------------------
# Data download
# ---------------------------------------------------------------------------

def download_single_shard(index):
    """Download one parquet shard with retries. Returns True on success."""
    filename = f"shard_{index:05d}.parquet"
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        return True

    url = f"{BASE_URL}/{filename}"
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            temp_path = filepath + ".tmp"
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            os.rename(temp_path, filepath)
            print(f"  Downloaded {filename}")
            return True
        except (requests.RequestException, IOError) as e:
            print(f"  Attempt {attempt}/{max_attempts} failed for {filename}: {e}")
            for path in [filepath + ".tmp", filepath]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
            if attempt < max_attempts:
                time.sleep(2 ** attempt)
    return False


def download_data(num_shards, download_workers=8):
    """Download training shards + pinned validation shard."""
    os.makedirs(DATA_DIR, exist_ok=True)
    num_train = min(num_shards, MAX_SHARD)
    ids = list(range(num_train))
    if VAL_SHARD not in ids:
        ids.append(VAL_SHARD)

    # Count what's already downloaded
    existing = sum(1 for i in ids if os.path.exists(os.path.join(DATA_DIR, f"shard_{i:05d}.parquet")))
    if existing == len(ids):
        print(f"Data: all {len(ids)} shards already downloaded at {DATA_DIR}")
        return

    needed = len(ids) - existing
    print(f"Data: downloading {needed} shards ({existing} already exist)...")

    workers = max(1, min(download_workers, needed))
    with Pool(processes=workers) as pool:
        results = pool.map(download_single_shard, ids)

    ok = sum(1 for r in results if r)
    print(f"Data: {ok}/{len(ids)} shards ready at {DATA_DIR}")

# ---------------------------------------------------------------------------
# Tokenizer training
# ---------------------------------------------------------------------------

def list_parquet_files():
    """Return sorted list of parquet file paths in the data directory."""
    files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".parquet") and not f.endswith(".tmp"))
    return [os.path.join(DATA_DIR, f) for f in files]


def text_iterator(max_chars=1_000_000_000, doc_cap=10_000):
    """Yield documents from training split (all shards except pinned val shard)."""
    parquet_paths = [p for p in list_parquet_files() if not p.endswith(VAL_FILENAME)]
    nchars = 0
    for filepath in parquet_paths:
        pf = pq.ParquetFile(filepath)
        for rg_idx in range(pf.num_row_groups):
            rg = pf.read_row_group(rg_idx)
            for text in rg.column("text").to_pylist():
                doc = text[:doc_cap] if len(text) > doc_cap else text
                nchars += len(doc)
                yield doc
                if nchars >= max_chars:
                    return


def train_tokenizer():
    """Train BPE tokenizer using rustbpe, save as tiktoken pickle."""
    tokenizer_pkl = os.path.join(TOKENIZER_DIR, "tokenizer.pkl")
    token_bytes_path = os.path.join(TOKENIZER_DIR, "token_bytes.pt")

    if os.path.exists(tokenizer_pkl) and os.path.exists(token_bytes_path):
        print(f"Tokenizer: already trained at {TOKENIZER_DIR}")
        return

    os.makedirs(TOKENIZER_DIR, exist_ok=True)

    parquet_files = list_parquet_files()
    if len(parquet_files) < 2:
        print("Tokenizer: need at least 2 data shards (1 train + 1 val). Download more data first.")
        sys.exit(1)

    # --- Train with rustbpe ---
    print("Tokenizer: training BPE tokenizer...")
    t0 = time.time()

    tokenizer = rustbpe.Tokenizer()
    vocab_size_no_special = VOCAB_SIZE - len(SPECIAL_TOKENS)
    tokenizer.train_from_iterator(text_iterator(), vocab_size_no_special, pattern=SPLIT_PATTERN)

    # Build tiktoken encoding from trained merges
    pattern = tokenizer.get_pattern()
    mergeable_ranks = {bytes(k): v for k, v in tokenizer.get_mergeable_ranks()}
    tokens_offset = len(mergeable_ranks)
    special_tokens = {name: tokens_offset + i for i, name in enumerate(SPECIAL_TOKENS)}
    enc = tiktoken.Encoding(
        name="rustbpe",
        pat_str=pattern,
        mergeable_ranks=mergeable_ranks,
        special_tokens=special_tokens,
    )

    # Save tokenizer
    with open(tokenizer_pkl, "wb") as f:
        pickle.dump(enc, f)

    t1 = time.time()
    print(f"Tokenizer: trained in {t1 - t0:.1f}s, saved to {tokenizer_pkl}")

    # --- Build token_bytes lookup for BPB evaluation ---
    print("Tokenizer: building token_bytes lookup...")
    special_set = set(SPECIAL_TOKENS)
    token_bytes_list = []
    for token_id in range(enc.n_vocab):
        token_str = enc.decode([token_id])
        if token_str in special_set:
            token_bytes_list.append(0)
        else:
            token_bytes_list.append(len(token_str.encode("utf-8")))
    token_bytes_tensor = torch.tensor(token_bytes_list, dtype=torch.int32)
    torch.save(token_bytes_tensor, token_bytes_path)
    print(f"Tokenizer: saved token_bytes to {token_bytes_path}")

    # Sanity check
    test = "Hello world! Numbers: 123. Unicode: 你好"
    encoded = enc.encode_ordinary(test)
    decoded = enc.decode(encoded)
    assert decoded == test, f"Tokenizer roundtrip failed: {test!r} -> {decoded!r}"
    print(f"Tokenizer: sanity check passed (vocab_size={enc.n_vocab})")

# ---------------------------------------------------------------------------
# Runtime utilities (imported by train.py)
# ---------------------------------------------------------------------------

class Tokenizer:
    """Minimal tokenizer wrapper. Training is handled above."""

    def __init__(self, enc):
        self.enc = enc
        self.bos_token_id = enc.encode_single_token(BOS_TOKEN)

    @classmethod
    def from_directory(cls, tokenizer_dir=TOKENIZER_DIR):
        with open(os.path.join(tokenizer_dir, "tokenizer.pkl"), "rb") as f:
            enc = pickle.load(f)
        return cls(enc)

    def get_vocab_size(self):
        return self.enc.n_vocab

    def get_bos_token_id(self):
        return self.bos_token_id

    def encode(self, text, prepend=None, num_threads=8):
        if prepend is not None:
            prepend_id = prepend if isinstance(prepend, int) else self.enc.encode_single_token(prepend)
        if isinstance(text, str):
            ids = self.enc.encode_ordinary(text)
            if prepend is not None:
                ids.insert(0, prepend_id)
        elif isinstance(text, list):
            ids = self.enc.encode_ordinary_batch(text, num_threads=num_threads)
            if prepend is not None:
                for row in ids:
                    row.insert(0, prepend_id)
        else:
            raise ValueError(f"Invalid input type: {type(text)}")
        return ids

    def decode(self, ids):
        return self.enc.decode(ids)


def get_token_bytes(device="cpu"):
    path = os.path.join(TOKENIZER_DIR, "token_bytes.pt")
    with open(path, "rb") as f:
        return torch.load(f, map_location=device)


def _document_batches(split, tokenizer_batch_size=128):
    """Infinite iterator over document batches from parquet files."""
    parquet_paths = list_parquet_files()
    assert len(parquet_paths) > 0, "No parquet files found. Run prepare.py first."
    val_path = os.path.join(DATA_DIR, VAL_FILENAME)
    if split == "train":
        parquet_paths = [p for p in parquet_paths if p != val_path]
        assert len(parquet_paths) > 0, "No training shards found."
    else:
        parquet_paths = [val_path]
    epoch = 1
    while True:
        for filepath in parquet_paths:
            pf = pq.ParquetFile(filepath)
            for rg_idx in range(pf.num_row_groups):
                rg = pf.read_row_group(rg_idx)
                batch = rg.column('text').to_pylist()
                for i in range(0, len(batch), tokenizer_batch_size):
                    yield batch[i:i+tokenizer_batch_size], epoch
        epoch += 1


def make_dataloader(tokenizer, B, T, split, buffer_size=1000):
    """
    BOS-aligned dataloader with best-fit packing.
    Every row starts with BOS. Documents packed using best-fit to minimize cropping.
    When no document fits remaining space, crops shortest doc to fill exactly.
    100% utilization (no padding).
    """
    assert split in ["train", "val"]
    row_capacity = T + 1
    batches = _document_batches(split)
    bos_token = tokenizer.get_bos_token_id()
    doc_buffer = []
    epoch = 1

    def refill_buffer():
        nonlocal epoch
        doc_batch, epoch = next(batches)
        token_lists = tokenizer.encode(doc_batch, prepend=bos_token)
        doc_buffer.extend(token_lists)

    # Pre-allocate buffers: [inputs (B*T) | targets (B*T)]
    row_buffer = torch.empty((B, row_capacity), dtype=torch.long)
    cpu_buffer = torch.empty(2 * B * T, dtype=torch.long, pin_memory=True)
    gpu_buffer = torch.empty(2 * B * T, dtype=torch.long, device="cuda")
    cpu_inputs = cpu_buffer[:B * T].view(B, T)
    cpu_targets = cpu_buffer[B * T:].view(B, T)
    inputs = gpu_buffer[:B * T].view(B, T)
    targets = gpu_buffer[B * T:].view(B, T)

    while True:
        for row_idx in range(B):
            pos = 0
            while pos < row_capacity:
                while len(doc_buffer) < buffer_size:
                    refill_buffer()

                remaining = row_capacity - pos

                # Find largest doc that fits entirely
                best_idx = -1
                best_len = 0
                for i, doc in enumerate(doc_buffer):
                    doc_len = len(doc)
                    if doc_len <= remaining and doc_len > best_len:
                        best_idx = i
                        best_len = doc_len

                if best_idx >= 0:
                    doc = doc_buffer.pop(best_idx)
                    row_buffer[row_idx, pos:pos + len(doc)] = torch.tensor(doc, dtype=torch.long)
                    pos += len(doc)
                else:
                    # No doc fits — crop shortest to fill remaining
                    shortest_idx = min(range(len(doc_buffer)), key=lambda i: len(doc_buffer[i]))
                    doc = doc_buffer.pop(shortest_idx)
                    row_buffer[row_idx, pos:pos + remaining] = torch.tensor(doc[:remaining], dtype=torch.long)
                    pos += remaining

        cpu_inputs.copy_(row_buffer[:, :-1])
        cpu_targets.copy_(row_buffer[:, 1:])
        gpu_buffer.copy_(cpu_buffer, non_blocking=True)
        yield inputs, targets, epoch

# ---------------------------------------------------------------------------
# Evaluation (DO NOT CHANGE — this is the fixed metric)
# ---------------------------------------------------------------------------

@torch.no_grad()
def evaluate_bpb(model, tokenizer, batch_size):
    """
    Bits per byte (BPB): vocab size-independent evaluation metric.
    Sums per-token cross-entropy (in nats), sums target byte lengths,
    then converts nats/byte to bits/byte. Special tokens (byte length 0)
    are excluded from both sums.
    Uses fixed MAX_SEQ_LEN so results are comparable across configs.
    """
    token_bytes = get_token_bytes(device="cuda")
    val_loader = make_dataloader(tokenizer, batch_size, MAX_SEQ_LEN, "val")
    steps = EVAL_TOKENS // (batch_size * MAX_SEQ_LEN)
    total_nats = 0.0
    total_bytes = 0
    for _ in range(steps):
        x, y, _ = next(val_loader)
        loss_flat = model(x, y, reduction='none').view(-1)
        y_flat = y.view(-1)
        nbytes = token_bytes[y_flat]
        mask = nbytes > 0
        total_nats += (loss_flat * mask).sum().item()
        total_bytes += nbytes.sum().item()
    return total_nats / (math.log(2) * total_bytes)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare data and tokenizer for autoresearch")
    parser.add_argument("--num-shards", type=int, default=10, help="Number of training shards to download (-1 = all). Val shard is always pinned.")
    parser.add_argument("--download-workers", type=int, default=8, help="Number of parallel download workers")
    args = parser.parse_args()

    num_shards = MAX_SHARD if args.num_shards == -1 else args.num_shards

    print(f"Cache directory: {CACHE_DIR}")
    print()

    # Step 1: Download data
    download_data(num_shards, download_workers=args.download_workers)
    print()

    # Step 2: Train tokenizer
    train_tokenizer()
    print()
    print("Done! Ready to train.")

# ===== FILE: run_batch.py =====
#!/usr/bin/env python3
"""
AutoResearch Batch Runner — runs all experiments from the plan sequentially.
Writes to results/batch_log.txt so progress can be monitored.
"""
import json, time, subprocess, copy, os, sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
LOG_FILE = RESULTS_DIR / "batch_log.txt"
GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET = 480

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def run_experiment(exp_code, desc):
    """Write experiment code, sync to GPU, run, return AUC."""
    try:
        (BASE_DIR / "experiment.py").write_text(exp_code)
        
        # Sync
        subprocess.run(["scp", str(BASE_DIR / "experiment.py"), 
                         f"{GPU_HOST}:{GPU_WORKDIR}/experiment.py"],
                        capture_output=True, timeout=30)
        
        # Run
        cmd = (f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
               f"timeout {TIME_BUDGET} python3 -c '"
               f"from experiment import run_experiment; import json; "
               f"auc = run_experiment(); print(json.dumps({{\"auc\": auc}}))"
               f"'")
        
        start = time.time()
        proc = subprocess.run(["ssh", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=30", GPU_HOST, cmd],
                              capture_output=True, text=True, timeout=TIME_BUDGET + 60)
        elapsed = time.time() - start
    
        if proc.returncode == 0:
            try:
                result = json.loads(proc.stdout.strip().split("\n")[-1])
                auc = result["auc"]
                log(f"  ✅ {desc}: AUC={auc:.6f} ({elapsed:.0f}s)")
                return auc
            except:
                log(f"  ❌ {desc}: parse error ({elapsed:.0f}s) stdout={proc.stdout[-200:]}")
                return None
        elif proc.returncode == 124:
            log(f"  ⏰ {desc}: TIMEOUT ({elapsed:.0f}s)")
            return None
        else:
            log(f"  ❌ {desc}: error code={proc.returncode} ({elapsed:.0f}s) stderr={proc.stderr[-200:]}")
            return None
    except Exception as e:
        log(f"  ❌ {desc}: EXCEPTION: {e}")
        return None

# Read the current best experiment.py as base
BASE_CODE = (BASE_DIR / "experiment_best.py").read_text()

def make_variant(base, changes):
    """Apply text replacements to create a variant."""
    code = base
    for old, new in changes:
        code = code.replace(old, new)
    return code

# ============================================================
# EXPERIMENT DEFINITIONS
# ============================================================

experiments = []

# --- PHASE 1: Feature Engineering ---

# 1. Contract x InternetService interaction
experiments.append(("feat_contract_x_internet", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "contract_internet", "gender",')
]))

# 2. Contract x PaymentMethod interaction
experiments.append(("feat_contract_x_payment", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["contract_payment"] = df["Contract"].astype(str) + "_" + df["PaymentMethod"].astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "contract_payment", "gender",')
]))

# 3. Tenure bucketing
experiments.append(("feat_tenure_bucket", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["tenure_bucket"] = pd.cut(df["tenure"], bins=[-1,6,12,24,48,72], labels=["0-6","7-12","13-24","25-48","49+"]).astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "tenure_bucket", "gender",')
]))

# 4. Count of "No internet service" 
experiments.append(("feat_no_internet_count", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    no_internet_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
     '    df["no_internet_count"] = sum((df[c] == "No internet service").astype(int) for c in no_internet_cols)')
]))

# 5. Multi-smooth TE (smooth=5 stacked alongside smooth=20)
experiments.append(("feat_multi_smooth_te", [
    ('Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)',
     'Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)\n'
     '        Xtr_s5, Xva_s5 = add_target_encoding(Xtr, Xva, CAT_COLS, ytr, smooth=5.0)\n'
     '        for c in CAT_COLS:\n'
     '            Xtr[f"{c}__te5"] = Xtr_s5[f"{c}__te"]\n'
     '            Xva[f"{c}__te5"] = Xva_s5[f"{c}__te"]')
]))

# 6. Frequency encoding
experiments.append(("feat_freq_encoding", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    # Will be overwritten per-fold but placeholder for columns\n'
     '    for c in ["Contract", "InternetService", "PaymentMethod"]:\n'
     '        df[f"{c}_freq"] = df[c].map(df[c].value_counts(normalize=True)).astype(np.float32)')
]))

# --- PHASE 2: Hyperparameter Tuning ---

# 7. Depth sweep
for d in [4, 6, 7, 8]:
    experiments.append((f"hp_depth_{d}", [
        ('depth=5,', f'depth={d},')
    ]))

# 8. L2 regularization sweep
for l2 in [1.0, 3.0, 8.0, 12.0, 20.0]:
    experiments.append((f"hp_l2_{l2}", [
        ('l2_leaf_reg=5.0,', f'l2_leaf_reg={l2},')
    ]))

# 9. Learning rate + iterations combos
for lr, iters in [(0.05, 3000), (0.01, 8000), (0.02, 5000)]:
    experiments.append((f"hp_lr{lr}_iter{iters}", [
        ('learning_rate=0.03,', f'learning_rate={lr},'),
        ('iterations=5000,', f'iterations={iters},')
    ]))

# 10. Bagging temperature
for bt in [0.3, 0.5, 0.8]:
    experiments.append((f"hp_bt_{bt}", [
        ('bagging_temperature=0.0,', f'bagging_temperature={bt},')
    ]))

# 11. Random strength
for rs in [1.0, 2.0, 5.0]:
    experiments.append((f"hp_rs_{rs}", [
        ('random_strength=3.0,', f'random_strength={rs},')
    ]))

# 12. Border count
for bc in [128, 254]:
    experiments.append((f"hp_bc_{bc}", [
        ('devices="0",', f'devices="0",\n        border_count={bc},')
    ]))

# 13. Min data in leaf
for md in [5, 10, 20, 50]:
    experiments.append((f"hp_min_leaf_{md}", [
        ('devices="0",', f'devices="0",\n        min_data_in_leaf={md},')
    ]))

# --- PHASE 3: Advanced ---

# 14. Group stats: mean MonthlyCharges by Contract
experiments.append(("feat_group_stats_contract", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    for grp in ["Contract", "InternetService"]:\n'
     '        gstats = df.groupby(grp)["MonthlyCharges"].transform("mean")\n'
     '        df[f"{grp}_mc_mean"] = gstats.astype(np.float32)\n'
     '        df[f"{grp}_mc_diff"] = (df["MonthlyCharges"] - gstats).astype(np.float32)')
]))

# 15. CatBoost native TE (drop manual TE entirely)
experiments.append(("native_catboost_te", [
    ('# Target encoding\n        Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)',
     '# No manual target encoding — let CatBoost handle categoricals natively\n        pass')
]))

# 16. Charge difference features
experiments.append(("feat_charge_diffs", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["charge_resid"] = df["TotalCharges"] - df["MonthlyCharges"] * df["tenure"]\n'
     '    df["monthly_per_service"] = df["MonthlyCharges"] / (sum((df[c] == "Yes").astype(int) for c in ["PhoneService", "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]) + 1)')
]))

# 17. Log transforms of numerical features
experiments.append(("feat_log_transforms", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["log_tenure"] = np.log1p(df["tenure"])\n'
     '    df["log_total_charges"] = np.log1p(df["TotalCharges"])\n'
     '    df["log_monthly_charges"] = np.log1p(df["MonthlyCharges"])')
]))

# 18. Internet x Senior interaction
experiments.append(("feat_internet_x_senior", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["internet_senior"] = df["InternetService"].astype(str) + "_" + df["SeniorCitizen"].astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "internet_senior", "gender",')
]))

# ============================================================
# RUN ALL
# ============================================================

def main():
    best_auc = 0.916435  # current baseline
    best_code = BASE_CODE
    results = []
    
    log(f"\n{'='*60}")
    log(f"AUTORESEARCH BATCH RUN — {len(experiments)} experiments")
    log(f"Baseline AUC: {best_auc:.6f}")
    log(f"{'='*60}\n")
    
    SKIP_FIRST = int(os.environ.get("SKIP_FIRST", "0"))
    for i, (name, changes) in enumerate(experiments, 1):
        if i <= SKIP_FIRST:
            log(f"  ⏭️ Skipping {name} (already done)")
            continue
        log(f"\n--- Experiment {i}/{len(experiments)}: {name} ---")
        
        try:
            variant = make_variant(best_code, changes)
        except Exception as e:
            log(f"  ❌ Code generation failed: {e}")
            results.append({"name": name, "auc": None, "status": "code_error"})
            continue
        
        auc = run_experiment(variant, name)
        
        if auc is not None and auc > best_auc:
            improvement = auc - best_auc
            log(f"  🎉 NEW BEST! {auc:.6f} (+{improvement:.6f})")
            best_auc = auc
            best_code = variant
            # Save best
            (BASE_DIR / "experiment_best.py").write_text(best_code)
            results.append({"name": name, "auc": auc, "status": "improved", "delta": improvement})
        elif auc is not None:
            delta = auc - best_auc
            log(f"  ↩️ Reverted ({delta:+.6f})")
            results.append({"name": name, "auc": auc, "status": "reverted", "delta": delta})
        else:
            results.append({"name": name, "auc": None, "status": "failed"})
        
        # Heartbeat every 5 experiments
        if i % 5 == 0:
            elapsed_exps = i
            log(f"\n[PROGRESS] {elapsed_exps}/{len(experiments)} done, best={best_auc:.6f}")
    
    # Final summary
    log(f"\n{'='*60}")
    log(f"FINAL RESULTS")
    log(f"{'='*60}")
    log(f"Best AUC: {best_auc:.6f}")
    log(f"Experiments run: {len(results)}")
    improved = [r for r in results if r["status"] == "improved"]
    log(f"Improvements found: {len(improved)}")
    for r in improved:
        log(f"  {r['name']}: {r['auc']:.6f} (+{r['delta']:.6f})")
    
    # Save results
    (RESULTS_DIR / "batch_results.json").write_text(json.dumps(results, indent=2))
    (BASE_DIR / "experiment.py").write_text(best_code)
    log(f"\nSaved best experiment to experiment.py and experiment_best.py")
    log("DONE!")

if __name__ == "__main__":
    main()

# ===== FILE: run_batch_v2.py =====
#!/usr/bin/env python3
"""
AutoResearch Batch Runner V2 — MORE feature engineering experiments.
Picks up from wherever batch 1 left off (reads experiment_best.py).
"""
import json, time, subprocess, os, sys
import numpy as np
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
LOG_FILE = RESULTS_DIR / "batch_log_v2.txt"
GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET = 480

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def run_experiment(exp_code, desc):
    (BASE_DIR / "experiment.py").write_text(exp_code)
    subprocess.run(["scp", str(BASE_DIR / "experiment.py"),
                     f"{GPU_HOST}:{GPU_WORKDIR}/experiment.py"],
                    capture_output=True, timeout=15)
    cmd = (f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
           f"timeout {TIME_BUDGET} python3 -c '"
           f"from experiment import run_experiment; import json; "
           f"auc = run_experiment(); print(json.dumps({{\"auc\": auc}}))"
           f"'")
    start = time.time()
    proc = subprocess.run(["ssh", GPU_HOST, cmd],
                          capture_output=True, text=True, timeout=TIME_BUDGET + 30)
    elapsed = time.time() - start
    if proc.returncode == 0:
        try:
            result = json.loads(proc.stdout.strip().split("\n")[-1])
            auc = result["auc"]
            log(f"  ✅ {desc}: AUC={auc:.6f} ({elapsed:.0f}s)")
            return auc
        except:
            log(f"  ❌ {desc}: parse error ({elapsed:.0f}s)")
            return None
    elif proc.returncode == 124:
        log(f"  ⏰ {desc}: TIMEOUT ({elapsed:.0f}s)")
        return None
    else:
        log(f"  ❌ {desc}: error code={proc.returncode} ({elapsed:.0f}s) stderr={proc.stderr[-200:]}")
        return None

def make_variant(base, changes):
    code = base
    for old, new in changes:
        code = code.replace(old, new)
    return code

# Read current best
BASE_CODE = (BASE_DIR / "experiment_best.py").read_text()

experiments = []

# --- MORE FEATURE ENGINEERING ---

# 1. Streaming bundle: both TV+Movies
experiments.append(("feat_streaming_bundle", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["streaming_both"] = ((df["StreamingTV"] == "Yes") & (df["StreamingMovies"] == "Yes")).astype(int)\n'
     '    df["streaming_none"] = ((df["StreamingTV"] == "No") & (df["StreamingMovies"] == "No")).astype(int)')
]))

# 2. Security bundle: security + backup + protection
experiments.append(("feat_security_bundle", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    sec_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection"]\n'
     '    df["security_count"] = sum((df[c] == "Yes").astype(int) for c in sec_cols)\n'
     '    df["has_any_security"] = (df["security_count"] > 0).astype(int)\n'
     '    df["has_all_security"] = (df["security_count"] == 3).astype(int)')
]))

# 3. Tenure polynomial features
experiments.append(("feat_tenure_poly", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["tenure_sq"] = df["tenure"] ** 2\n'
     '    df["tenure_sqrt"] = np.sqrt(df["tenure"])\n'
     '    df["tenure_inv"] = 1.0 / (df["tenure"] + 1)')
]))

# 4. Monthly charges quantile rank
experiments.append(("feat_charge_quantile", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["mc_rank"] = df["MonthlyCharges"].rank(pct=True).astype(np.float32)\n'
     '    df["tc_rank"] = df["TotalCharges"].rank(pct=True).astype(np.float32)\n'
     '    df["tenure_rank"] = df["tenure"].rank(pct=True).astype(np.float32)')
]))

# 5. Contract risk score (domain knowledge)
experiments.append(("feat_risk_score", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    # Risk factors: short tenure + month-to-month + fiber + high charges\n'
     '    risk = np.zeros(len(df))\n'
     '    risk += (df["tenure"] < 12).astype(float) * 0.3\n'
     '    risk += (df["Contract"] == "Month-to-month").astype(float) * 0.3\n'
     '    risk += (df["InternetService"] == "Fiber optic").astype(float) * 0.2\n'
     '    risk += (df["MonthlyCharges"] > 70).astype(float) * 0.1\n'
     '    risk += (df["PaperlessBilling"] == "Yes").astype(float) * 0.1\n'
     '    df["risk_score"] = risk.astype(np.float32)')
]))

# 6. Payment auto vs manual
experiments.append(("feat_auto_payment", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["auto_payment"] = df["PaymentMethod"].isin(["Bank transfer (automatic)", "Credit card (automatic)"]).astype(int)')
]))

# 7. Tenure * Contract interaction (numeric)
experiments.append(("feat_tenure_contract_num", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    contract_map = {"Month-to-month": 1, "One year": 12, "Two year": 24}\n'
     '    df["contract_months"] = df["Contract"].map(contract_map).fillna(1).astype(int)\n'
     '    df["tenure_per_contract"] = df["tenure"] / (df["contract_months"] + 1)\n'
     '    df["tenure_minus_contract"] = df["tenure"] - df["contract_months"]')
]))

# 8. Charges deviation from group mean (Contract + Internet)
experiments.append(("feat_charges_deviation", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    for col_pair in [("Contract", "InternetService"), ("Contract", "PaymentMethod")]:\n'
     '        grp = df.groupby(list(col_pair))["MonthlyCharges"].transform("mean")\n'
     '        name = "_".join(col_pair)\n'
     '        df[f"{name}_mc_dev"] = (df["MonthlyCharges"] - grp).astype(np.float32)')
]))

# 9. Has partner AND dependents (family indicator)
experiments.append(("feat_family", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["has_family"] = ((df["Partner"] == "Yes") & (df["Dependents"] == "Yes")).astype(int)\n'
     '    df["single_no_dep"] = ((df["Partner"] == "No") & (df["Dependents"] == "No")).astype(int)')
]))

# 10. Total services value per dollar
experiments.append(("feat_value_per_dollar", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
     '    n_svc = sum((df[c] == "Yes").astype(int) for c in service_cols)\n'
     '    df["cost_per_service"] = df["MonthlyCharges"] / (n_svc + 1)\n'
     '    df["services_per_dollar"] = n_svc / (df["MonthlyCharges"] + 1)')
]))

# 11. Internet x MultipleLines
experiments.append(("feat_internet_x_lines", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["internet_lines"] = df["InternetService"].astype(str) + "_" + df["MultipleLines"].astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "internet_lines", "gender",')
]))

# 12. Tenure percentile within contract type
experiments.append(("feat_tenure_pct_in_contract", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["tenure_pct_in_contract"] = df.groupby("Contract")["tenure"].rank(pct=True).astype(np.float32)')
]))

# 13. MonthlyCharges bins (categorical)
experiments.append(("feat_charge_bins", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["mc_bin"] = pd.cut(df["MonthlyCharges"], bins=[0,30,50,70,90,120], labels=["vlow","low","mid","high","vhigh"]).astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "mc_bin", "gender",')
]))

# 14. Contract x PaperlessBilling
experiments.append(("feat_contract_x_paperless", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["contract_paperless"] = df["Contract"].astype(str) + "_" + df["PaperlessBilling"].astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "contract_paperless", "gender",')
]))

# 15. Loyalty score: tenure / (total possible for contract)
experiments.append(("feat_loyalty", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["loyalty"] = df["tenure"] / 72.0  # normalized 0-1\n'
     '    df["new_customer"] = (df["tenure"] <= 3).astype(int)\n'
     '    df["long_customer"] = (df["tenure"] >= 60).astype(int)')
]))

# 16. All pairwise categorical interactions (top 3 predictors)
experiments.append(("feat_top3_interactions", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    for c1, c2 in [("Contract","InternetService"), ("Contract","PaymentMethod"), ("InternetService","PaymentMethod")]:\n'
     '        df[f"{c1}_x_{c2}"] = df[c1].astype(str) + "_" + df[c2].astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "Contract_x_InternetService", "Contract_x_PaymentMethod", "InternetService_x_PaymentMethod", "gender",')
]))

# 17. Tenure segments with monthly charges
experiments.append(("feat_tenure_charge_segment", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["tenure_short_high_charge"] = ((df["tenure"] < 12) & (df["MonthlyCharges"] > 70)).astype(int)\n'
     '    df["tenure_long_low_charge"] = ((df["tenure"] > 48) & (df["MonthlyCharges"] < 50)).astype(int)')
]))

# 18. Numerical interactions: MonthlyCharges * SeniorCitizen
experiments.append(("feat_senior_charges", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["senior_x_monthly"] = df["SeniorCitizen"] * df["MonthlyCharges"]\n'
     '    df["senior_x_tenure"] = df["SeniorCitizen"] * df["tenure"]')
]))

# 19. Expected vs actual total charges ratio
experiments.append(("feat_expected_vs_actual", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    expected = df["MonthlyCharges"] * df["tenure"]\n'
     '    df["charge_surplus"] = (df["TotalCharges"] - expected).astype(np.float32)\n'
     '    df["charge_surplus_pct"] = (df["charge_surplus"] / (expected + 1)).astype(np.float32)')
]))

# 20. Contract + Internet + Payment triple interaction
experiments.append(("feat_triple_interaction", [
    ('df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
     'df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    df["cip_triple"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str) + "_" + df["PaymentMethod"].astype(str)'),
    ('CAT_COLS = [\n    "gender",',
     'CAT_COLS = [\n    "cip_triple", "gender",')
]))


def main():
    # Wait for batch 1 to finish
    batch1_log = RESULTS_DIR / "batch_log.txt"
    while True:
        if batch1_log.exists():
            content = batch1_log.read_text()
            if "DONE!" in content:
                log("Batch 1 finished, starting batch 2")
                break
        log("Waiting for batch 1 to finish...")
        time.sleep(60)
    
    # Read the best from batch 1
    best_code = (BASE_DIR / "experiment_best.py").read_text()
    
    # Get baseline AUC from batch 1 results
    try:
        batch1_results = json.loads((RESULTS_DIR / "batch_results.json").read_text())
        best_auc = max(r["auc"] for r in batch1_results if r.get("auc"))
    except:
        best_auc = 0.916435  # fallback
    
    log(f"\n{'='*60}")
    log(f"AUTORESEARCH BATCH V2 — {len(experiments)} MORE feature engineering experiments")
    log(f"Starting AUC: {best_auc:.6f}")
    log(f"{'='*60}\n")
    
    results = []
    for i, (name, changes) in enumerate(experiments, 1):
        log(f"\n--- Experiment {i}/{len(experiments)}: {name} ---")
        try:
            variant = make_variant(best_code, changes)
        except Exception as e:
            log(f"  ❌ Code generation failed: {e}")
            results.append({"name": name, "auc": None, "status": "code_error"})
            continue
        
        auc = run_experiment(variant, name)
        
        if auc is not None and auc > best_auc:
            improvement = auc - best_auc
            log(f"  🎉 NEW BEST! {auc:.6f} (+{improvement:.6f})")
            best_auc = auc
            best_code = variant
            (BASE_DIR / "experiment_best.py").write_text(best_code)
            results.append({"name": name, "auc": auc, "status": "improved", "delta": improvement})
        elif auc is not None:
            delta = auc - best_auc
            log(f"  ↩️ Reverted ({delta:+.6f})")
            results.append({"name": name, "auc": auc, "status": "reverted", "delta": delta})
        else:
            results.append({"name": name, "auc": None, "status": "failed"})
        
        if i % 5 == 0:
            log(f"\n[PROGRESS] {i}/{len(experiments)} done, best={best_auc:.6f}")
    
    log(f"\n{'='*60}")
    log(f"BATCH V2 FINAL RESULTS")
    log(f"{'='*60}")
    log(f"Best AUC: {best_auc:.6f}")
    improved = [r for r in results if r["status"] == "improved"]
    log(f"Improvements: {len(improved)}")
    for r in improved:
        log(f"  {r['name']}: {r['auc']:.6f} (+{r['delta']:.6f})")
    
    (RESULTS_DIR / "batch_results_v2.json").write_text(json.dumps(results, indent=2))
    (BASE_DIR / "experiment.py").write_text(best_code)
    log("DONE!")

if __name__ == "__main__":
    main()

# ===== FILE: run_final_submission.py =====
"""
Full submission pipeline: best CatBoost config from autoresearch.
- Train on all data with target encoding from full train
- 10 checkpoints at 500-iteration intervals
- Multi-seed ensemble (7 seeds)
- Submit all checkpoints to Kaggle
"""
import numpy as np, pandas as pd, json, time, requests, os, warnings
warnings.filterwarnings('ignore')
from catboost import CatBoostClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
SUB_DIR = BASE_DIR / "submissions"
RESULTS_DIR.mkdir(exist_ok=True)
SUB_DIR.mkdir(exist_ok=True)

SEED = 42
N_SEEDS = 7
N_FOLDS = 5
CHECKPOINTS = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]

CAT_COLS = ['gender','Partner','Dependents','PhoneService','MultipleLines',
            'InternetService','OnlineSecurity','OnlineBackup','DeviceProtection',
            'TechSupport','StreamingTV','StreamingMovies','Contract',
            'PaperlessBilling','PaymentMethod']

# Best config from autoresearch (55 experiments)
CB_PARAMS = dict(
    learning_rate=0.03,
    depth=5,
    l2_leaf_reg=5.0,
    random_strength=2.0,
    bagging_temperature=0.8,
    min_data_in_leaf=50,
    loss_function='Logloss',
    eval_metric='AUC',
    verbose=False,
    task_type='GPU',
    devices='0:1',
)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)

def add_features(df):
    df = df.copy()
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup",
                    "DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df

def add_te_full(tr, te, cols, ytr, smooth=20.0):
    gm = float(np.mean(ytr)); ys = pd.Series(ytr, index=tr.index)
    tr2, te2 = tr.copy(), te.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), 't': ys})
        st = g.groupby(c)['t'].agg(['mean','count'])
        sm = ((st['count']*st['mean'])+(smooth*gm))/(st['count']+smooth)
        m = sm.to_dict(); nc = f'{c}__te'
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        te2[nc] = te[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, te2

def add_te_fold(tr, va, cols, ytr, smooth=20.0):
    gm = float(np.mean(ytr)); ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), 't': ys})
        st = g.groupby(c)['t'].agg(['mean','count'])
        sm = ((st['count']*st['mean'])+(smooth*gm))/(st['count']+smooth)
        m = sm.to_dict(); nc = f'{c}__te'
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2

def submit_to_kaggle(filepath, description):
    from kaggle_auth import get_kaggle_headers
    H = get_kaggle_headers()
    BASE = 'https://www.kaggle.com/api/v1'
    COMP = 'playground-series-s6e3'
    fsize = os.path.getsize(filepath)
    epoch = int(time.time())
    try:
        r1 = requests.post(f'{BASE}/competitions/{COMP}/submissions/url/{fsize}/{epoch}',
                           headers=H, data={'fileName': 'submission.csv'})
        data = r1.json()
        with open(filepath, 'rb') as f:
            requests.put(data['createUrl'], data=f)
        r3 = requests.post(f'{BASE}/competitions/submissions/submit/{COMP}',
                           headers=H, data={'blobFileTokens': data['token'],
                                            'submissionDescription': description})
        log(f"  Submitted: {r3.json().get('message','')}")
        return True
    except Exception as e:
        log(f"  Submit failed: {e}")
        return False

def main():
    log("Loading data...")
    train_df = pd.read_csv(BASE_DIR / 'train.csv')
    test_df = pd.read_csv(BASE_DIR / 'test.csv')
    y = (train_df['Churn'] == 'Yes').astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=['Churn']))
    X_test = add_features(test_df)
    
    # Step 1: CV to find best iteration per seed
    log(f"\n{'='*60}")
    log(f"STEP 1: {N_FOLDS}-fold CV with {N_SEEDS} seeds")
    log(f"{'='*60}")
    
    cv_results = []
    for seed_offset in range(N_SEEDS):
        seed = SEED + seed_offset
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))
        best_iters = []
        
        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]
            Xtr_te, Xva_te = add_te_fold(Xtr, Xva, CAT_COLS, ytr)
            fc = [c for c in Xtr_te.columns if c != 'id']
            ci = [fc.index(c) for c in CAT_COLS if c in fc]
            
            params = dict(CB_PARAMS)
            params['random_seed'] = seed
            params['iterations'] = 5000
            params['early_stopping_rounds'] = 300
            mdl = CatBoostClassifier(**params)
            mdl.fit(Xtr_te[fc], ytr, cat_features=ci, eval_set=(Xva_te[fc], yva), use_best_model=True)
            oof[vidx] = mdl.predict_proba(Xva_te[fc])[:,1]
            best_iters.append(mdl.get_best_iteration())
        
        auc = roc_auc_score(y, oof)
        avg_iter = int(np.mean(best_iters))
        cv_results.append({'seed': seed, 'auc': auc, 'avg_iter': avg_iter})
        log(f"  Seed {seed}: AUC={auc:.6f}, avg_best_iter={avg_iter}")
    
    mean_cv = np.mean([r['auc'] for r in cv_results])
    log(f"\n  Mean CV AUC: {mean_cv:.6f}")
    
    # Step 2: Train on full data with checkpoints, multi-seed
    log(f"\n{'='*60}")
    log(f"STEP 2: Full-train with {len(CHECKPOINTS)} checkpoints × {N_SEEDS} seeds")
    log(f"{'='*60}")
    
    # Prepare full-train TE
    Xfull_te, Xtest_te = add_te_full(X, X_test, CAT_COLS, y)
    fc = [c for c in Xfull_te.columns if c != 'id']
    ci = [fc.index(c) for c in CAT_COLS if c in fc]
    
    # For each checkpoint, accumulate predictions across seeds
    checkpoint_preds = {cp: np.zeros(len(test_df)) for cp in CHECKPOINTS}
    
    for seed_offset in range(N_SEEDS):
        seed = SEED + seed_offset
        log(f"\n  Training seed {seed}...")
        
        # Train with max iterations (no early stopping for full train)
        params = dict(CB_PARAMS)
        params['random_seed'] = seed
        params['iterations'] = max(CHECKPOINTS)
        # No early stopping on full train
        
        mdl = CatBoostClassifier(**params)
        mdl.fit(Xfull_te[fc], y, cat_features=ci)
        
        # Get predictions at each checkpoint by using shrink
        for cp in CHECKPOINTS:
            mdl_cp = mdl.copy()
            mdl_cp.shrink(cp)
            preds = mdl_cp.predict_proba(Xtest_te[fc])[:,1]
            checkpoint_preds[cp] += preds
        
        log(f"    [HEARTBEAT] Seed {seed} done, all checkpoints extracted")
    
    # Average across seeds
    for cp in CHECKPOINTS:
        checkpoint_preds[cp] /= N_SEEDS
    
    # Step 3: Save and submit all checkpoints
    log(f"\n{'='*60}")
    log(f"STEP 3: Save & submit {len(CHECKPOINTS)} checkpoints")
    log(f"{'='*60}")
    
    for cp in CHECKPOINTS:
        preds = checkpoint_preds[cp]
        fname = f"sub_best_iter{cp}_7seed.csv"
        fpath = SUB_DIR / fname
        sub = pd.DataFrame({'id': test_df['id'], 'Churn': preds})
        sub.to_csv(fpath, index=False)
        desc = f"Best config iter={cp} 7seed d5 lr0.03 bt0.8 rs2 ml50 CV={mean_cv:.6f}"
        log(f"\n  Checkpoint {cp}: mean={preds.mean():.4f}, std={preds.std():.4f}")
        submit_to_kaggle(str(fpath), desc)
        time.sleep(5)  # rate limit
    
    # Save results
    results = {
        'cv_results': cv_results,
        'mean_cv': mean_cv,
        'checkpoints': CHECKPOINTS,
        'params': {k:v for k,v in CB_PARAMS.items() if k not in ('task_type','devices')},
        'n_seeds': N_SEEDS,
    }
    (RESULTS_DIR / 'final_submission_results.json').write_text(json.dumps(results, indent=2))
    
    log(f"\n{'='*60}")
    log(f"ALL DONE! {len(CHECKPOINTS)} submissions made.")
    log(f"Mean CV: {mean_cv:.6f}")
    log(f"{'='*60}")

if __name__ == "__main__":
    main()

# ===== FILE: sub_51580.py =====

import numpy as np, pandas as pd, json, warnings, random
warnings.filterwarnings('ignore')
from catboost import CatBoostClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from pathlib import Path

BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
SEED = 42
N_SEEDS = 7
N_FOLDS = 5

CAT_COLS = ["contract_internet","tenure_bin","gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0

def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)

def add_features(df):
    df = df.copy()
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    df["streaming_bundle"] = ((df["StreamingTV"] == "Yes").astype(int) + (df["StreamingMovies"] == "Yes").astype(int))
    df["security_bundle"] = ((df["OnlineSecurity"] == "Yes").astype(int) + (df["OnlineBackup"] == "Yes").astype(int) + (df["DeviceProtection"] == "Yes").astype(int))
    for c in ["Contract", "InternetService", "PaymentMethod"]:
        df[f"{c}_freq"] = df[c].map(df[c].value_counts(normalize=True)).astype(np.float32)
    df["log_tenure"] = np.log1p(df["tenure"])
    df["log_total_charges"] = np.log1p(df["TotalCharges"])
    df["log_monthly_charges"] = np.log1p(df["MonthlyCharges"])
    no_int_cols = ["OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]
    df["no_internet_count"] = sum((df[c] == "No internet service").astype(int) for c in no_int_cols)
    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)
    df["tenure_bin"] = pd.cut(df["tenure"], bins=[-1,6,12,24,48,72], labels=["0-6","7-12","13-24","25-48","49+"]).astype(str)
    return df

def add_te(tr, other, cols, ytr, smooth=SMOOTH):
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, ot2 = tr.copy(), other.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        ot2[nc] = other[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, ot2

def add_group_stats(tr, other, group_cols, num_cols):
    tr2, ot2 = tr.copy(), other.copy()
    for g in group_cols:
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            tr2[f"gs_mean_{n}_by_{g}"] = tr[g].map(mean_map).astype(np.float32)
            ot2[f"gs_mean_{n}_by_{g}"] = other[g].map(mean_map).astype(np.float32)
            tr2[f"gs_resid_{n}_by_{g}"] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            ot2[f"gs_resid_{n}_by_{g}"] = (other[n].astype(float) - other[g].map(mean_map).astype(float)).astype(np.float32)
            tr2[f"gs_ratio_{n}_by_{g}"] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            ot2[f"gs_ratio_{n}_by_{g}"] = (other[n].astype(float) / (other[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, ot2



def get_model(seed=SEED):
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        bagging_temperature=0.3,
        border_count=254,
        early_stopping_rounds=300,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        task_type="GPU",
        devices="0",
    )

def main():
    set_seed()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    test_df = pd.read_csv(BASE_DIR / "test.csv")
    y = (train_df["Churn"] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=["Churn"]))
    X_test = add_features(test_df)

    # CV for validation
    all_oof = np.zeros((N_SEEDS, len(X)))
    all_test = np.zeros((N_SEEDS, len(X_test)))

    for si in range(N_SEEDS):
        seed = SEED + si
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))
        test_preds = np.zeros(len(X_test))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            Xtr, Xva = add_te(Xtr, Xva, CAT_COLS, ytr)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)
            # Also prepare test with train fold stats
            _, Xte_fold = add_group_stats(Xtr, X_test.copy(), GROUP_COLS, NUM_COLS)
            _, Xte_fold = add_te(Xtr, Xte_fold, CAT_COLS, ytr)
            # Group median+std+multi-TE applied in extra_fold_apply
            for g in GROUP_COLS:
                for n in NUM_COLS:
                    med_map = Xtr.groupby(g)[n].median().to_dict()
                    Xtr[f'gs_med_{n}_by_{g}'] = Xtr[g].map(med_map).astype(np.float32)
                    Xva[f'gs_med_{n}_by_{g}'] = Xva[g].map(med_map).astype(np.float32)
                    Xte_fold[f'gs_med_{n}_by_{g}'] = X_test[g].map(med_map).astype(np.float32) if g in X_test.columns else np.float32(0)
                    std_map = Xtr.groupby(g)[n].std().to_dict()
                    Xtr[f'gs_std_{n}_by_{g}'] = Xtr[g].map(std_map).astype(np.float32)
                    Xva[f'gs_std_{n}_by_{g}'] = Xva[g].map(std_map).astype(np.float32)
                    Xte_fold[f'gs_std_{n}_by_{g}'] = X_test[g].map(std_map).astype(np.float32) if g in X_test.columns else np.float32(0)

            fc = [c for c in Xtr.columns if c != "id"]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci, eval_set=(Xva[fc], yva), use_best_model=True)

            oof[vidx] = model.predict_proba(Xva[fc])[:, 1]
            test_preds += model.predict_proba(Xte_fold[fc])[:, 1] / N_FOLDS

        all_oof[si] = oof
        all_test[si] = test_preds
        seed_auc = roc_auc_score(y, oof)
        print(f"Seed {seed}: AUC={seed_auc:.6f}", flush=True)

    ensemble_oof = all_oof.mean(axis=0)
    ensemble_test = all_test.mean(axis=0)
    cv_auc = roc_auc_score(y, ensemble_oof)
    print(f"Ensemble CV AUC: {cv_auc:.6f}", flush=True)

    # Save submission
    sub = pd.DataFrame({"id": test_df["id"], "Churn": ensemble_test})
    sub.to_csv(BASE_DIR / "submission.csv", index=False)
    print(json.dumps({"cv_auc": cv_auc}))

if __name__ == "__main__":
    main()

# ===== FILE: train.py =====
"""
Autoresearch pretraining script. Single-GPU, single-file.
Cherry-picked and simplified from nanochat.
Usage: uv run train.py
"""

import os
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

import gc
import math
import time
from dataclasses import dataclass, asdict

import torch
import torch.nn as nn
import torch.nn.functional as F

from kernels import get_kernel
cap = torch.cuda.get_device_capability()
# varunneal's FA3 is Hopper only, use kernels-community on non-Hopper GPUs
repo = "varunneal/flash-attention-3" if cap == (9, 0) else "kernels-community/flash-attn3"
fa3 = get_kernel(repo).flash_attn_interface

from prepare import MAX_SEQ_LEN, TIME_BUDGET, Tokenizer, make_dataloader, evaluate_bpb

# ---------------------------------------------------------------------------
# GPT Model
# ---------------------------------------------------------------------------

@dataclass
class GPTConfig:
    sequence_len: int = 2048
    vocab_size: int = 32768
    n_layer: int = 12
    n_head: int = 6
    n_kv_head: int = 6
    n_embd: int = 768
    window_pattern: str = "SSSL"


def norm(x):
    return F.rms_norm(x, (x.size(-1),))


def has_ve(layer_idx, n_layer):
    """Returns True if layer should have Value Embedding (alternating, last always included)."""
    return layer_idx % 2 == (n_layer - 1) % 2


def apply_rotary_emb(x, cos, sin):
    assert x.ndim == 4
    d = x.shape[3] // 2
    x1, x2 = x[..., :d], x[..., d:]
    y1 = x1 * cos + x2 * sin
    y2 = x1 * (-sin) + x2 * cos
    return torch.cat([y1, y2], 3)


class CausalSelfAttention(nn.Module):
    def __init__(self, config, layer_idx):
        super().__init__()
        self.n_head = config.n_head
        self.n_kv_head = config.n_kv_head
        self.n_embd = config.n_embd
        self.head_dim = self.n_embd // self.n_head
        assert self.n_embd % self.n_head == 0
        assert self.n_kv_head <= self.n_head and self.n_head % self.n_kv_head == 0
        self.c_q = nn.Linear(self.n_embd, self.n_head * self.head_dim, bias=False)
        self.c_k = nn.Linear(self.n_embd, self.n_kv_head * self.head_dim, bias=False)
        self.c_v = nn.Linear(self.n_embd, self.n_kv_head * self.head_dim, bias=False)
        self.c_proj = nn.Linear(self.n_embd, self.n_embd, bias=False)
        self.ve_gate_channels = 32
        self.ve_gate = nn.Linear(self.ve_gate_channels, self.n_kv_head, bias=False) if has_ve(layer_idx, config.n_layer) else None

    def forward(self, x, ve, cos_sin, window_size):
        B, T, C = x.size()
        q = self.c_q(x).view(B, T, self.n_head, self.head_dim)
        k = self.c_k(x).view(B, T, self.n_kv_head, self.head_dim)
        v = self.c_v(x).view(B, T, self.n_kv_head, self.head_dim)

        # Value residual (ResFormer): mix in value embedding with input-dependent gate per head
        if ve is not None:
            ve = ve.view(B, T, self.n_kv_head, self.head_dim)
            gate = 2 * torch.sigmoid(self.ve_gate(x[..., :self.ve_gate_channels]))
            v = v + gate.unsqueeze(-1) * ve

        cos, sin = cos_sin
        q, k = apply_rotary_emb(q, cos, sin), apply_rotary_emb(k, cos, sin)
        q, k = norm(q), norm(k)

        y = fa3.flash_attn_func(q, k, v, causal=True, window_size=window_size)
        y = y.contiguous().view(B, T, -1)
        y = self.c_proj(y)
        return y


class MLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.c_fc = nn.Linear(config.n_embd, 4 * config.n_embd, bias=False)
        self.c_proj = nn.Linear(4 * config.n_embd, config.n_embd, bias=False)

    def forward(self, x):
        x = self.c_fc(x)
        x = F.relu(x).square()
        x = self.c_proj(x)
        return x


class Block(nn.Module):
    def __init__(self, config, layer_idx):
        super().__init__()
        self.attn = CausalSelfAttention(config, layer_idx)
        self.mlp = MLP(config)

    def forward(self, x, ve, cos_sin, window_size):
        x = x + self.attn(norm(x), ve, cos_sin, window_size)
        x = x + self.mlp(norm(x))
        return x


class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.window_sizes = self._compute_window_sizes(config)
        self.transformer = nn.ModuleDict({
            "wte": nn.Embedding(config.vocab_size, config.n_embd),
            "h": nn.ModuleList([Block(config, i) for i in range(config.n_layer)]),
        })
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        self.resid_lambdas = nn.Parameter(torch.ones(config.n_layer))
        self.x0_lambdas = nn.Parameter(torch.zeros(config.n_layer))
        # Value embeddings
        head_dim = config.n_embd // config.n_head
        kv_dim = config.n_kv_head * head_dim
        self.value_embeds = nn.ModuleDict({
            str(i): nn.Embedding(config.vocab_size, kv_dim)
            for i in range(config.n_layer) if has_ve(i, config.n_layer)
        })
        # Rotary embeddings
        self.rotary_seq_len = config.sequence_len * 10
        cos, sin = self._precompute_rotary_embeddings(self.rotary_seq_len, head_dim)
        self.register_buffer("cos", cos, persistent=False)
        self.register_buffer("sin", sin, persistent=False)

    @torch.no_grad()
    def init_weights(self):
        # Embedding and unembedding
        torch.nn.init.normal_(self.transformer.wte.weight, mean=0.0, std=1.0)
        torch.nn.init.normal_(self.lm_head.weight, mean=0.0, std=0.001)
        # Transformer blocks
        n_embd = self.config.n_embd
        s = 3**0.5 * n_embd**-0.5
        for block in self.transformer.h:
            torch.nn.init.uniform_(block.attn.c_q.weight, -s, s)
            torch.nn.init.uniform_(block.attn.c_k.weight, -s, s)
            torch.nn.init.uniform_(block.attn.c_v.weight, -s, s)
            torch.nn.init.zeros_(block.attn.c_proj.weight)
            torch.nn.init.uniform_(block.mlp.c_fc.weight, -s, s)
            torch.nn.init.zeros_(block.mlp.c_proj.weight)
        # Per-layer scalars
        self.resid_lambdas.fill_(1.0)
        self.x0_lambdas.fill_(0.1)
        # Value embeddings
        for ve in self.value_embeds.values():
            torch.nn.init.uniform_(ve.weight, -s, s)
        # Gate weights init to zero (sigmoid(0)=0.5, scaled by 2 -> 1.0 = neutral)
        for block in self.transformer.h:
            if block.attn.ve_gate is not None:
                torch.nn.init.zeros_(block.attn.ve_gate.weight)
        # Rotary embeddings
        head_dim = self.config.n_embd // self.config.n_head
        cos, sin = self._precompute_rotary_embeddings(self.rotary_seq_len, head_dim)
        self.cos, self.sin = cos, sin
        # Cast embeddings to bf16
        self.transformer.wte.to(dtype=torch.bfloat16)
        for ve in self.value_embeds.values():
            ve.to(dtype=torch.bfloat16)

    def _precompute_rotary_embeddings(self, seq_len, head_dim, base=10000, device=None):
        if device is None:
            device = self.transformer.wte.weight.device
        channel_range = torch.arange(0, head_dim, 2, dtype=torch.float32, device=device)
        inv_freq = 1.0 / (base ** (channel_range / head_dim))
        t = torch.arange(seq_len, dtype=torch.float32, device=device)
        freqs = torch.outer(t, inv_freq)
        cos, sin = freqs.cos(), freqs.sin()
        cos, sin = cos.bfloat16(), sin.bfloat16()
        cos, sin = cos[None, :, None, :], sin[None, :, None, :]
        return cos, sin

    def _compute_window_sizes(self, config):
        pattern = config.window_pattern.upper()
        assert all(c in "SL" for c in pattern)
        long_window = config.sequence_len
        short_window = long_window // 2
        char_to_window = {"L": (long_window, 0), "S": (short_window, 0)}
        window_sizes = []
        for layer_idx in range(config.n_layer):
            char = pattern[layer_idx % len(pattern)]
            window_sizes.append(char_to_window[char])
        window_sizes[-1] = (long_window, 0)
        return window_sizes

    def estimate_flops(self):
        """Estimated FLOPs per token (forward + backward)."""
        nparams = sum(p.numel() for p in self.parameters())
        value_embeds_numel = sum(ve.weight.numel() for ve in self.value_embeds.values())
        nparams_exclude = (self.transformer.wte.weight.numel() + value_embeds_numel +
                          self.resid_lambdas.numel() + self.x0_lambdas.numel())
        h = self.config.n_head
        q = self.config.n_embd // self.config.n_head
        t = self.config.sequence_len
        attn_flops = 0
        for window_size in self.window_sizes:
            window = window_size[0]
            effective_seq = t if window < 0 else min(window, t)
            attn_flops += 12 * h * q * effective_seq
        return 6 * (nparams - nparams_exclude) + attn_flops

    def num_scaling_params(self):
        wte = sum(p.numel() for p in self.transformer.wte.parameters())
        value_embeds = sum(p.numel() for p in self.value_embeds.parameters())
        lm_head = sum(p.numel() for p in self.lm_head.parameters())
        transformer_matrices = sum(p.numel() for p in self.transformer.h.parameters())
        scalars = self.resid_lambdas.numel() + self.x0_lambdas.numel()
        total = wte + value_embeds + lm_head + transformer_matrices + scalars
        return {
            'wte': wte, 'value_embeds': value_embeds, 'lm_head': lm_head,
            'transformer_matrices': transformer_matrices, 'scalars': scalars, 'total': total,
        }

    def setup_optimizer(self, unembedding_lr=0.004, embedding_lr=0.2, matrix_lr=0.02,
                        weight_decay=0.0, adam_betas=(0.8, 0.95), scalar_lr=0.5):
        model_dim = self.config.n_embd
        matrix_params = list(self.transformer.h.parameters())
        value_embeds_params = list(self.value_embeds.parameters())
        embedding_params = list(self.transformer.wte.parameters())
        lm_head_params = list(self.lm_head.parameters())
        resid_params = [self.resid_lambdas]
        x0_params = [self.x0_lambdas]
        assert len(list(self.parameters())) == (len(matrix_params) + len(embedding_params) +
            len(lm_head_params) + len(value_embeds_params) + len(resid_params) + len(x0_params))
        # Scale LR ∝ 1/√dmodel (tuned at 768 dim)
        dmodel_lr_scale = (model_dim / 768) ** -0.5
        print(f"Scaling AdamW LRs by 1/sqrt({model_dim}/768) = {dmodel_lr_scale:.6f}")
        param_groups = [
            dict(kind='adamw', params=lm_head_params, lr=unembedding_lr * dmodel_lr_scale, betas=adam_betas, eps=1e-10, weight_decay=0.0),
            dict(kind='adamw', params=embedding_params, lr=embedding_lr * dmodel_lr_scale, betas=adam_betas, eps=1e-10, weight_decay=0.0),
            dict(kind='adamw', params=value_embeds_params, lr=embedding_lr * dmodel_lr_scale, betas=adam_betas, eps=1e-10, weight_decay=0.0),
            dict(kind='adamw', params=resid_params, lr=scalar_lr * 0.01, betas=adam_betas, eps=1e-10, weight_decay=0.0),
            dict(kind='adamw', params=x0_params, lr=scalar_lr, betas=(0.96, 0.95), eps=1e-10, weight_decay=0.0),
        ]
        for shape in sorted({p.shape for p in matrix_params}):
            group_params = [p for p in matrix_params if p.shape == shape]
            param_groups.append(dict(
                kind='muon', params=group_params, lr=matrix_lr,
                momentum=0.95, ns_steps=5, beta2=0.95, weight_decay=weight_decay,
            ))
        optimizer = MuonAdamW(param_groups)
        for group in optimizer.param_groups:
            group["initial_lr"] = group["lr"]
        return optimizer

    def forward(self, idx, targets=None, reduction='mean'):
        B, T = idx.size()
        assert T <= self.cos.size(1)
        cos_sin = self.cos[:, :T], self.sin[:, :T]

        x = self.transformer.wte(idx)
        x = norm(x)
        x0 = x
        for i, block in enumerate(self.transformer.h):
            x = self.resid_lambdas[i] * x + self.x0_lambdas[i] * x0
            ve = self.value_embeds[str(i)](idx) if str(i) in self.value_embeds else None
            x = block(x, ve, cos_sin, self.window_sizes[i])
        x = norm(x)

        softcap = 15
        logits = self.lm_head(x)
        logits = logits.float()
        logits = softcap * torch.tanh(logits / softcap)

        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1),
                                   ignore_index=-1, reduction=reduction)
            return loss
        return logits

# ---------------------------------------------------------------------------
# Optimizer (MuonAdamW, single GPU only)
# ---------------------------------------------------------------------------

polar_express_coeffs = [
    (8.156554524902461, -22.48329292557795, 15.878769915207462),
    (4.042929935166739, -2.808917465908714, 0.5000178451051316),
    (3.8916678022926607, -2.772484153217685, 0.5060648178503393),
    (3.285753657755655, -2.3681294933425376, 0.46449024233003106),
    (2.3465413258596377, -1.7097828382687081, 0.42323551169305323),
]

@torch.compile(dynamic=False, fullgraph=True)
def adamw_step_fused(p, grad, exp_avg, exp_avg_sq, step_t, lr_t, beta1_t, beta2_t, eps_t, wd_t):
    p.mul_(1 - lr_t * wd_t)
    exp_avg.lerp_(grad, 1 - beta1_t)
    exp_avg_sq.lerp_(grad.square(), 1 - beta2_t)
    bias1 = 1 - beta1_t ** step_t
    bias2 = 1 - beta2_t ** step_t
    denom = (exp_avg_sq / bias2).sqrt() + eps_t
    step_size = lr_t / bias1
    p.add_(exp_avg / denom, alpha=-step_size)

@torch.compile(dynamic=False, fullgraph=True)
def muon_step_fused(stacked_grads, stacked_params, momentum_buffer, second_momentum_buffer,
                    momentum_t, lr_t, wd_t, beta2_t, ns_steps, red_dim):
    # Nesterov momentum
    momentum = momentum_t.to(stacked_grads.dtype)
    momentum_buffer.lerp_(stacked_grads, 1 - momentum)
    g = stacked_grads.lerp_(momentum_buffer, momentum)
    # Polar express orthogonalization
    X = g.bfloat16()
    X = X / (X.norm(dim=(-2, -1), keepdim=True) * 1.02 + 1e-6)
    if g.size(-2) > g.size(-1):
        for a, b, c in polar_express_coeffs[:ns_steps]:
            A = X.mT @ X
            B = b * A + c * (A @ A)
            X = a * X + X @ B
    else:
        for a, b, c in polar_express_coeffs[:ns_steps]:
            A = X @ X.mT
            B = b * A + c * (A @ A)
            X = a * X + B @ X
    g = X
    # NorMuon variance reduction
    beta2 = beta2_t.to(g.dtype)
    v_mean = g.float().square().mean(dim=red_dim, keepdim=True)
    red_dim_size = g.size(red_dim)
    v_norm_sq = v_mean.sum(dim=(-2, -1), keepdim=True) * red_dim_size
    v_norm = v_norm_sq.sqrt()
    second_momentum_buffer.lerp_(v_mean.to(dtype=second_momentum_buffer.dtype), 1 - beta2)
    step_size = second_momentum_buffer.clamp_min(1e-10).rsqrt()
    scaled_sq_sum = (v_mean * red_dim_size) * step_size.float().square()
    v_norm_new = scaled_sq_sum.sum(dim=(-2, -1), keepdim=True).sqrt()
    final_scale = step_size * (v_norm / v_norm_new.clamp_min(1e-10))
    g = g * final_scale.to(g.dtype)
    # Cautious weight decay + parameter update
    lr = lr_t.to(g.dtype)
    wd = wd_t.to(g.dtype)
    mask = (g * stacked_params) >= 0
    stacked_params.sub_(lr * g + lr * wd * stacked_params * mask)


class MuonAdamW(torch.optim.Optimizer):
    """Combined optimizer: Muon for 2D matrix params, AdamW for others."""

    def __init__(self, param_groups):
        super().__init__(param_groups, defaults={})
        # 0-D CPU tensors to avoid torch.compile recompilation when values change
        self._adamw_step_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._adamw_lr_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._adamw_beta1_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._adamw_beta2_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._adamw_eps_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._adamw_wd_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._muon_momentum_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._muon_lr_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._muon_wd_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")
        self._muon_beta2_t = torch.tensor(0.0, dtype=torch.float32, device="cpu")

    def _step_adamw(self, group):
        for p in group['params']:
            if p.grad is None:
                continue
            grad = p.grad
            state = self.state[p]
            if not state:
                state['step'] = 0
                state['exp_avg'] = torch.zeros_like(p)
                state['exp_avg_sq'] = torch.zeros_like(p)
            state['step'] += 1
            self._adamw_step_t.fill_(state['step'])
            self._adamw_lr_t.fill_(group['lr'])
            self._adamw_beta1_t.fill_(group['betas'][0])
            self._adamw_beta2_t.fill_(group['betas'][1])
            self._adamw_eps_t.fill_(group['eps'])
            self._adamw_wd_t.fill_(group['weight_decay'])
            adamw_step_fused(p, grad, state['exp_avg'], state['exp_avg_sq'],
                            self._adamw_step_t, self._adamw_lr_t, self._adamw_beta1_t,
                            self._adamw_beta2_t, self._adamw_eps_t, self._adamw_wd_t)

    def _step_muon(self, group):
        params = group['params']
        if not params:
            return
        p = params[0]
        state = self.state[p]
        num_params = len(params)
        shape, device, dtype = p.shape, p.device, p.dtype
        if "momentum_buffer" not in state:
            state["momentum_buffer"] = torch.zeros(num_params, *shape, dtype=dtype, device=device)
        if "second_momentum_buffer" not in state:
            state_shape = (num_params, shape[-2], 1) if shape[-2] >= shape[-1] else (num_params, 1, shape[-1])
            state["second_momentum_buffer"] = torch.zeros(state_shape, dtype=dtype, device=device)
        red_dim = -1 if shape[-2] >= shape[-1] else -2
        stacked_grads = torch.stack([p.grad for p in params])
        stacked_params = torch.stack(params)
        self._muon_momentum_t.fill_(group["momentum"])
        self._muon_beta2_t.fill_(group["beta2"] if group["beta2"] is not None else 0.0)
        self._muon_lr_t.fill_(group["lr"] * max(1.0, shape[-2] / shape[-1])**0.5)
        self._muon_wd_t.fill_(group["weight_decay"])
        muon_step_fused(stacked_grads, stacked_params,
                        state["momentum_buffer"], state["second_momentum_buffer"],
                        self._muon_momentum_t, self._muon_lr_t, self._muon_wd_t,
                        self._muon_beta2_t, group["ns_steps"], red_dim)
        torch._foreach_copy_(params, list(stacked_params.unbind(0)))

    @torch.no_grad()
    def step(self):
        for group in self.param_groups:
            if group['kind'] == 'adamw':
                self._step_adamw(group)
            elif group['kind'] == 'muon':
                self._step_muon(group)

# ---------------------------------------------------------------------------
# Hyperparameters (edit these directly, no CLI flags needed)
# ---------------------------------------------------------------------------

# Model architecture
ASPECT_RATIO = 64       # model_dim = depth * ASPECT_RATIO
HEAD_DIM = 128          # target head dimension for attention
WINDOW_PATTERN = "SSSL" # sliding window pattern: L=full, S=half context

# Optimization
TOTAL_BATCH_SIZE = 2**19 # ~524K tokens per optimizer step
EMBEDDING_LR = 0.6      # learning rate for token embeddings (Adam)
UNEMBEDDING_LR = 0.004  # learning rate for lm_head (Adam)
MATRIX_LR = 0.04        # learning rate for matrix parameters (Muon)
SCALAR_LR = 0.5         # learning rate for per-layer scalars (Adam)
WEIGHT_DECAY = 0.2      # cautious weight decay for Muon
ADAM_BETAS = (0.8, 0.95) # Adam beta1, beta2
WARMUP_RATIO = 0.0      # fraction of time budget for LR warmup
WARMDOWN_RATIO = 0.5    # fraction of time budget for LR warmdown
FINAL_LR_FRAC = 0.0     # final LR as fraction of initial

# Model size
DEPTH = 8               # number of transformer layers
DEVICE_BATCH_SIZE = 128  # per-device batch size (reduce if OOM)

# ---------------------------------------------------------------------------
# Setup: tokenizer, model, optimizer, dataloader
# ---------------------------------------------------------------------------

t_start = time.time()
torch.manual_seed(42)
torch.cuda.manual_seed(42)
torch.set_float32_matmul_precision("high")
device = torch.device("cuda")
autocast_ctx = torch.amp.autocast(device_type="cuda", dtype=torch.bfloat16)
H100_BF16_PEAK_FLOPS = 989.5e12

tokenizer = Tokenizer.from_directory()
vocab_size = tokenizer.get_vocab_size()
print(f"Vocab size: {vocab_size:,}")

def build_model_config(depth):
    base_dim = depth * ASPECT_RATIO
    model_dim = ((base_dim + HEAD_DIM - 1) // HEAD_DIM) * HEAD_DIM
    num_heads = model_dim // HEAD_DIM
    return GPTConfig(
        sequence_len=MAX_SEQ_LEN, vocab_size=vocab_size,
        n_layer=depth, n_head=num_heads, n_kv_head=num_heads, n_embd=model_dim,
        window_pattern=WINDOW_PATTERN,
    )

config = build_model_config(DEPTH)
print(f"Model config: {asdict(config)}")

with torch.device("meta"):
    model = GPT(config)
model.to_empty(device=device)
model.init_weights()

param_counts = model.num_scaling_params()
print("Parameter counts:")
for key, value in param_counts.items():
    print(f"  {key:24s}: {value:,}")
num_params = param_counts['total']
num_flops_per_token = model.estimate_flops()
print(f"Estimated FLOPs per token: {num_flops_per_token:e}")

tokens_per_fwdbwd = DEVICE_BATCH_SIZE * MAX_SEQ_LEN
assert TOTAL_BATCH_SIZE % tokens_per_fwdbwd == 0
grad_accum_steps = TOTAL_BATCH_SIZE // tokens_per_fwdbwd

optimizer = model.setup_optimizer(
    unembedding_lr=UNEMBEDDING_LR,
    embedding_lr=EMBEDDING_LR,
    scalar_lr=SCALAR_LR,
    adam_betas=ADAM_BETAS,
    matrix_lr=MATRIX_LR,
    weight_decay=WEIGHT_DECAY,
)

model = torch.compile(model, dynamic=False)

train_loader = make_dataloader(tokenizer, DEVICE_BATCH_SIZE, MAX_SEQ_LEN, "train")
x, y, epoch = next(train_loader)  # prefetch first batch

print(f"Time budget: {TIME_BUDGET}s")
print(f"Gradient accumulation steps: {grad_accum_steps}")

# Schedules (all based on progress = training_time / TIME_BUDGET)

def get_lr_multiplier(progress):
    if progress < WARMUP_RATIO:
        return progress / WARMUP_RATIO if WARMUP_RATIO > 0 else 1.0
    elif progress < 1.0 - WARMDOWN_RATIO:
        return 1.0
    else:
        cooldown = (1.0 - progress) / WARMDOWN_RATIO
        return cooldown * 1.0 + (1 - cooldown) * FINAL_LR_FRAC

def get_muon_momentum(step):
    frac = min(step / 300, 1)
    return (1 - frac) * 0.85 + frac * 0.95

def get_weight_decay(progress):
    return WEIGHT_DECAY * (1 - progress)

# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

t_start_training = time.time()
smooth_train_loss = 0
total_training_time = 0
step = 0

while True:
    torch.cuda.synchronize()
    t0 = time.time()
    for micro_step in range(grad_accum_steps):
        with autocast_ctx:
            loss = model(x, y)
        train_loss = loss.detach()
        loss = loss / grad_accum_steps
        loss.backward()
        x, y, epoch = next(train_loader)

    # Progress and schedules
    progress = min(total_training_time / TIME_BUDGET, 1.0)
    lrm = get_lr_multiplier(progress)
    muon_momentum = get_muon_momentum(step)
    muon_weight_decay = get_weight_decay(progress)
    for group in optimizer.param_groups:
        group["lr"] = group["initial_lr"] * lrm
        if group['kind'] == 'muon':
            group["momentum"] = muon_momentum
            group["weight_decay"] = muon_weight_decay
    optimizer.step()
    model.zero_grad(set_to_none=True)

    train_loss_f = train_loss.item()

    # Fast fail: abort if loss is exploding or NaN
    if math.isnan(train_loss_f) or train_loss_f > 100:
        print("FAIL")
        exit(1)

    torch.cuda.synchronize()
    t1 = time.time()
    dt = t1 - t0

    if step > 10:
        total_training_time += dt

    # Logging
    ema_beta = 0.9
    smooth_train_loss = ema_beta * smooth_train_loss + (1 - ema_beta) * train_loss_f
    debiased_smooth_loss = smooth_train_loss / (1 - ema_beta**(step + 1))
    pct_done = 100 * progress
    tok_per_sec = int(TOTAL_BATCH_SIZE / dt)
    mfu = 100 * num_flops_per_token * TOTAL_BATCH_SIZE / dt / H100_BF16_PEAK_FLOPS
    remaining = max(0, TIME_BUDGET - total_training_time)

    print(f"\rstep {step:05d} ({pct_done:.1f}%) | loss: {debiased_smooth_loss:.6f} | lrm: {lrm:.2f} | dt: {dt*1000:.0f}ms | tok/sec: {tok_per_sec:,} | mfu: {mfu:.1f}% | epoch: {epoch} | remaining: {remaining:.0f}s    ", end="", flush=True)

    # GC management (Python's GC causes ~500ms stalls)
    if step == 0:
        gc.collect()
        gc.freeze()
        gc.disable()
    elif (step + 1) % 5000 == 0:
        gc.collect()

    step += 1

    # Time's up — but only stop after warmup steps so we don't count compilation
    if step > 10 and total_training_time >= TIME_BUDGET:
        break

print()  # newline after \r training log

total_tokens = step * TOTAL_BATCH_SIZE

# Final eval
model.eval()
with autocast_ctx:
    val_bpb = evaluate_bpb(model, tokenizer, DEVICE_BATCH_SIZE)

# Final summary
t_end = time.time()
startup_time = t_start_training - t_start
steady_state_mfu = 100 * num_flops_per_token * TOTAL_BATCH_SIZE * (step - 10) / total_training_time / H100_BF16_PEAK_FLOPS if total_training_time > 0 else 0
peak_vram_mb = torch.cuda.max_memory_allocated() / 1024 / 1024

print("---")
print(f"val_bpb:          {val_bpb:.6f}")
print(f"training_seconds: {total_training_time:.1f}")
print(f"total_seconds:    {t_end - t_start:.1f}")
print(f"peak_vram_mb:     {peak_vram_mb:.1f}")
print(f"mfu_percent:      {steady_state_mfu:.2f}")
print(f"total_tokens_M:   {total_tokens / 1e6:.1f}")
print(f"num_steps:        {step}")
print(f"num_params_M:     {num_params / 1e6:.1f}")
print(f"depth:            {DEPTH}")

# ===== FILE: v2_experiment_base.py =====
"""
AutoResearch V2 — Based on Best LB Model (0.91447)
Base experiment template. Each experiment modifies this via code patches.
Uses 5-fold CV for more stable signal (vs holdout).
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
GPU_ID = 0  # Will be overridden per-experiment

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Feature engineering — baseline has group stats only."""
    df = df.copy()
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    """Smoothed target encoding — computed per fold."""
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    """Group statistics — mean, residual, ratio of num_cols by group_cols.
    Computed from train fold only, applied to both."""
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        grouped = tr[g]
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            mean_col = f"gs_mean_{n}_by_{g}"
            tr2[mean_col] = tr[g].map(mean_map).astype(np.float32)
            va2[mean_col] = va[g].map(mean_map).astype(np.float32)

            res_col = f"gs_resid_{n}_by_{g}"
            tr2[res_col] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[res_col] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)

            ratio_col = f"gs_ratio_{n}_by_{g}"
            tr2[ratio_col] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[ratio_col] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def get_model(seed=SEED):
    """Return the model — LB best config."""
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=8.0,
        random_strength=2.0,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        early_stopping_rounds=100,
        task_type="GPU",
        devices=str(GPU_ID),
    )


def run_experiment(gpu_id=0):
    """Main experiment — returns AUC score (5-fold CV, 3-seed ensemble)."""
    global GPU_ID
    GPU_ID = gpu_id
    set_seed()
    job_start = time.time()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]  # 3 seeds for speed during search
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # Target encoding (per fold)
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            # Group stats (per fold)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci,
                      eval_set=(Xva[fc], yva), use_best_model=True)

            vp = model.predict_proba(Xva[fc])[:, 1]
            oof[vidx] = vp
            elapsed = time.time() - job_start
            fold_auc = roc_auc_score(yva, vp)
            print(f"[HEARTBEAT {elapsed/60:.1f}m] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        seed_auc = float(roc_auc_score(y, oof))
        print(f"[SEED {seed}] AUC={seed_auc:.6f}", flush=True)
        all_oof[si] = oof

    # Ensemble: average OOF across seeds
    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    print(f"[ENSEMBLE] AUC={auc:.6f}", flush=True)
    return auc


if __name__ == "__main__":
    import sys
    gpu = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    auc = run_experiment(gpu_id=gpu)
    print(f"AUC: {auc:.6f}")

# ===== FILE: v2_pair_lr.py =====
"""
Chris Deotte's Pair TE + Logit³ + LR approach.
Adapted from: kaggle.com/code/cdeotte/chatgpt-vibe-coding-3xgpu-models-cv-0-9178

Pipeline:
1. Label encode all features
2. For each pair (i,j): target-encode the pair using inner CV
3. Logit transform: z = log(p/(1-p))
4. Create z, z², z³ features (171 pairs → 513 dims)
5. StandardScaler + L2 Logistic Regression
"""
import json
import numpy as np
import pandas as pd
import warnings
import time
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
SEED = 42
N_OUTER = 5
N_INNER_TE = 5  # inner folds for target encoding
TARGET = "Churn"

def main():
    t0 = time.time()
    
    train = pd.read_csv(BASE_DIR / "train.csv")
    test = pd.read_csv(BASE_DIR / "test.csv")
    
    y = (train[TARGET].astype(str).str.strip().str.lower() == "yes").astype(np.int32).values
    
    DROP_COLS = ["customerID", "id"]
    FEATURES = [c for c in train.columns if c not in DROP_COLS + [TARGET]]
    n_feat = len(FEATURES)
    N = len(train)
    
    print(f"Features: {n_feat}")
    print(f"Train: {N}, Test: {len(test)}")
    
    # ============================================================
    # 1. Label encode all features (train + test together)
    # ============================================================
    train_enc = train[FEATURES].copy()
    test_enc = test[FEATURES].copy()
    
    for c in FEATURES:
        tr_s = train_enc[c].astype(str).fillna("__MISSING__")
        te_s = test_enc[c].astype(str).fillna("__MISSING__")
        all_vals = pd.concat([tr_s, te_s], axis=0)
        uniq = sorted(all_vals.unique())
        mapping = {v: i for i, v in enumerate(uniq)}
        train_enc[c] = tr_s.map(mapping).astype(np.int32)
        test_enc[c] = te_s.map(mapping).astype(np.int32)
    
    X_all = train_enc.values.astype(np.int32)
    X_test = test_enc.values.astype(np.int32)
    
    # ============================================================
    # 2. Generate all pairs
    # ============================================================
    pair_cols = []
    for i in range(n_feat):
        for j in range(i + 1, n_feat):
            pair_cols.append((i, j, FEATURES[i], FEATURES[j]))
    
    n_pair = len(pair_cols)
    print(f"Num pairs: {n_pair}")
    
    # ============================================================
    # 3. Helper: target encode a pair column
    # ============================================================
    def target_encode_pair(X_tr_pair, X_va_pair, X_te_pair, y_tr, smooth=0):
        """
        Target encode a pair of columns.
        X_tr_pair: (n_tr, 2) int32
        Returns: tr_te, va_te, te_te as float32 arrays
        """
        # Create combined key from pair
        # Use string concatenation for simplicity
        def make_key(arr):
            return arr[:, 0].astype(str) + "_" + arr[:, 1].astype(str)
        
        tr_key = make_key(X_tr_pair)
        va_key = make_key(X_va_pair)
        te_key = make_key(X_te_pair)
        
        # Inner CV target encoding on training data (leak-free OOF)
        global_mean = y_tr.mean()
        tr_te = np.full(len(X_tr_pair), global_mean, dtype=np.float32)
        
        inner_kf = StratifiedKFold(n_splits=N_INNER_TE, shuffle=True, random_state=SEED + 999)
        for inner_tr, inner_va in inner_kf.split(X_tr_pair, y_tr):
            # Compute TE from inner train
            df_inner = pd.DataFrame({"key": tr_key[inner_tr], "y": y_tr[inner_tr]})
            stats = df_inner.groupby("key")["y"].agg(["sum", "count"])
            te_map = ((stats["sum"] + smooth * global_mean) / (stats["count"] + smooth)).to_dict()
            # Apply to inner val
            tr_te[inner_va] = pd.Series(tr_key[inner_va]).map(te_map).fillna(global_mean).values.astype(np.float32)
        
        # Full train TE for validation and test
        df_full = pd.DataFrame({"key": tr_key, "y": y_tr})
        stats_full = df_full.groupby("key")["y"].agg(["sum", "count"])
        te_map_full = ((stats_full["sum"] + smooth * global_mean) / (stats_full["count"] + smooth)).to_dict()
        
        va_te = pd.Series(va_key).map(te_map_full).fillna(global_mean).values.astype(np.float32)
        te_te = pd.Series(te_key).map(te_map_full).fillna(global_mean).values.astype(np.float32)
        
        return tr_te, va_te, te_te
    
    # ============================================================
    # 4. Logit transform + polynomial
    # ============================================================
    def clip01(x, eps=1e-5):
        return np.clip(x, eps, 1.0 - eps)
    
    def logit(x, eps=1e-5):
        x = clip01(x, eps)
        return np.log(x / (1.0 - x)).astype(np.float32)
    
    def make_logit3(tr, va, te):
        z_tr = logit(tr)
        z_va = logit(va)
        z_te = logit(te)
        X_tr = np.hstack([z_tr, z_tr**2, z_tr**3]).astype(np.float32)
        X_va = np.hstack([z_va, z_va**2, z_va**3]).astype(np.float32)
        X_te = np.hstack([z_te, z_te**2, z_te**3]).astype(np.float32)
        return X_tr, X_va, X_te
    
    # ============================================================
    # 5. Outer CV loop
    # ============================================================
    oof_meta = np.zeros(N, dtype=np.float32)
    pred_meta = np.zeros(len(test), dtype=np.float32)
    fold_aucs = []
    
    outer_kf = StratifiedKFold(n_splits=N_OUTER, shuffle=True, random_state=SEED)
    
    for fold, (tr_idx, va_idx) in enumerate(outer_kf.split(np.zeros(N), y), 1):
        fold_t0 = time.time()
        print(f"\n{'='*60}")
        print(f"[OUTER FOLD {fold}/{N_OUTER}] tr={len(tr_idx)} va={len(va_idx)}")
        print(f"{'='*60}")
        
        X_tr = X_all[tr_idx]
        X_va = X_all[va_idx]
        y_tr = y[tr_idx]
        y_va = y[va_idx]
        
        # Target encode all pairs
        tr_pair_te = np.zeros((len(tr_idx), n_pair), dtype=np.float32)
        va_pair_te = np.zeros((len(va_idx), n_pair), dtype=np.float32)
        te_pair_te = np.zeros((len(test), n_pair), dtype=np.float32)
        
        for t, (i, j, f1, f2) in enumerate(pair_cols):
            if (t == 0) or ((t + 1) % 50 == 0) or (t + 1 == n_pair):
                print(f"  Pair {t+1}/{n_pair}: {f1} x {f2} ({time.time()-fold_t0:.0f}s)", flush=True)
            
            tr_pair = np.column_stack([X_tr[:, i], X_tr[:, j]])
            va_pair = np.column_stack([X_va[:, i], X_va[:, j]])
            te_pair = np.column_stack([X_test[:, i], X_test[:, j]])
            
            tr_te, va_te, te_te = target_encode_pair(tr_pair, va_pair, te_pair, y_tr)
            tr_pair_te[:, t] = tr_te
            va_pair_te[:, t] = va_te
            te_pair_te[:, t] = te_te
        
        # Logit³ features
        X_tr_l3, X_va_l3, X_te_l3 = make_logit3(tr_pair_te, va_pair_te, te_pair_te)
        print(f"  Pair dims: {n_pair} → Logit³ dims: {X_tr_l3.shape[1]}")
        
        # Scale
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr_l3).astype(np.float32)
        X_va_s = scaler.transform(X_va_l3).astype(np.float32)
        X_te_s = scaler.transform(X_te_l3).astype(np.float32)
        
        # Logistic Regression
        lr = LogisticRegression(
            penalty="l2",
            C=0.5,
            max_iter=4000,
            tol=1e-4,
            solver="lbfgs",
            n_jobs=-1,
            random_state=SEED,
        )
        lr.fit(X_tr_s, y_tr)
        
        oof_va = lr.predict_proba(X_va_s)[:, 1].astype(np.float32)
        oof_meta[va_idx] = oof_va
        
        fold_auc = roc_auc_score(y_va, oof_va)
        fold_aucs.append(fold_auc)
        print(f"  [logit3] Fold {fold} AUC: {fold_auc:.6f} ({time.time()-fold_t0:.0f}s)")
        
        pred_meta += lr.predict_proba(X_te_s)[:, 1].astype(np.float32) / N_OUTER
    
    # ============================================================
    # 6. Final results
    # ============================================================
    meta_auc = roc_auc_score(y, oof_meta)
    elapsed = time.time() - t0
    
    print(f"\n{'='*60}")
    print(f"FINAL OOF AUC: {meta_auc:.6f}")
    print(f"Fold AUCs: {[f'{a:.6f}' for a in fold_aucs]}")
    print(f"Total time: {elapsed:.0f}s")
    print(f"{'='*60}")
    
    # Save OOF and test predictions
    np.save(BASE_DIR / "oof_pair_lr.npy", oof_meta)
    np.save(BASE_DIR / "pred_pair_lr.npy", pred_meta)
    
    # Save submission
    sub = pd.DataFrame({"id": test["id"], "Churn": pred_meta})
    sub.to_csv(BASE_DIR / "submission_pair_lr.csv", index=False)
    
    print(json.dumps({"auc": float(meta_auc), "elapsed": elapsed}))


if __name__ == "__main__":
    main()

# ===== FILE: v2_pair_lr_ablation.py =====
"""
Ablation study for Pair TE + Logit³ + LR approach.

Variants:
1. Single features TE only (19 features, no pairs) + LR
2. Single features TE + logit³ + LR  
3. Pair TE only (171 pairs) + LR (no logit transform)
4. Pair TE + logit (z only, no z²/z³) + LR
5. Pair TE + logit² (z + z²) + LR
6. Pair TE + logit³ (z + z² + z³) + LR  ← full model (baseline)
7. Single + Pair TE + logit³ + LR (19 + 171 = 190 features)
"""
import json
import numpy as np
import pandas as pd
import warnings
import time
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
SEED = 42
N_OUTER = 5
N_INNER_TE = 5
TARGET = "Churn"


def label_encode(train_df, test_df, features):
    train_enc = train_df[features].copy()
    test_enc = test_df[features].copy()
    for c in features:
        tr_s = train_enc[c].astype(str).fillna("__MISSING__")
        te_s = test_enc[c].astype(str).fillna("__MISSING__")
        all_vals = pd.concat([tr_s, te_s], axis=0)
        uniq = sorted(all_vals.unique())
        mapping = {v: i for i, v in enumerate(uniq)}
        train_enc[c] = tr_s.map(mapping).astype(np.int32)
        test_enc[c] = te_s.map(mapping).astype(np.int32)
    return train_enc.values.astype(np.int32), test_enc.values.astype(np.int32)


def target_encode_columns(X_tr_cols, X_va_cols, y_tr, smooth=0):
    """Target encode one or more columns combined as a single key."""
    def make_key(arr):
        if arr.ndim == 1:
            return arr.astype(str)
        return np.array(["_".join(str(x) for x in row) for row in arr])
    
    tr_key = make_key(X_tr_cols)
    va_key = make_key(X_va_cols)
    
    global_mean = y_tr.mean()
    tr_te = np.full(len(X_tr_cols), global_mean, dtype=np.float32)
    
    # Inner CV TE (leak-free)
    inner_kf = StratifiedKFold(n_splits=N_INNER_TE, shuffle=True, random_state=SEED + 999)
    for inner_tr, inner_va in inner_kf.split(X_tr_cols if X_tr_cols.ndim == 2 else X_tr_cols.reshape(-1, 1), y_tr):
        df_inner = pd.DataFrame({"key": tr_key[inner_tr], "y": y_tr[inner_tr]})
        stats = df_inner.groupby("key")["y"].agg(["sum", "count"])
        te_map = ((stats["sum"] + smooth * global_mean) / (stats["count"] + smooth)).to_dict()
        tr_te[inner_va] = pd.Series(tr_key[inner_va]).map(te_map).fillna(global_mean).values.astype(np.float32)
    
    # Full train TE for validation
    df_full = pd.DataFrame({"key": tr_key, "y": y_tr})
    stats_full = df_full.groupby("key")["y"].agg(["sum", "count"])
    te_map_full = ((stats_full["sum"] + smooth * global_mean) / (stats_full["count"] + smooth)).to_dict()
    va_te = pd.Series(va_key).map(te_map_full).fillna(global_mean).values.astype(np.float32)
    
    return tr_te, va_te


def clip01(x, eps=1e-5):
    return np.clip(x, eps, 1.0 - eps)

def logit(x, eps=1e-5):
    x = clip01(x, eps)
    return np.log(x / (1.0 - x)).astype(np.float32)


def run_variant(X_all, y, n_feat, pair_indices, variant_name, use_singles=False, use_pairs=True, poly_degree=3):
    """Run one ablation variant."""
    N = len(X_all)
    outer_kf = StratifiedKFold(n_splits=N_OUTER, shuffle=True, random_state=SEED)
    oof = np.zeros(N, dtype=np.float32)
    fold_aucs = []
    
    for fold, (tr_idx, va_idx) in enumerate(outer_kf.split(np.zeros(N), y), 1):
        fold_t0 = time.time()
        X_tr = X_all[tr_idx]
        X_va = X_all[va_idx]
        y_tr = y[tr_idx]
        y_va = y[va_idx]
        
        te_arrays_tr = []
        te_arrays_va = []
        
        # Single feature TE
        if use_singles:
            for i in range(n_feat):
                tr_te, va_te = target_encode_columns(X_tr[:, i], X_va[:, i], y_tr)
                te_arrays_tr.append(tr_te)
                te_arrays_va.append(va_te)
        
        # Pair TE
        if use_pairs:
            for i, j in pair_indices:
                tr_pair = np.column_stack([X_tr[:, i], X_tr[:, j]])
                va_pair = np.column_stack([X_va[:, i], X_va[:, j]])
                tr_te, va_te = target_encode_columns(tr_pair, va_pair, y_tr)
                te_arrays_tr.append(tr_te)
                te_arrays_va.append(va_te)
        
        tr_mat = np.column_stack(te_arrays_tr).astype(np.float32)
        va_mat = np.column_stack(te_arrays_va).astype(np.float32)
        
        # Apply polynomial features based on variant
        if poly_degree == 0:
            # Raw TE values, no transform
            X_tr_feat = tr_mat
            X_va_feat = va_mat
        elif poly_degree == 1:
            # logit(z) only
            z_tr = logit(tr_mat)
            z_va = logit(va_mat)
            X_tr_feat = z_tr
            X_va_feat = z_va
        elif poly_degree == 2:
            z_tr = logit(tr_mat)
            z_va = logit(va_mat)
            X_tr_feat = np.hstack([z_tr, z_tr**2])
            X_va_feat = np.hstack([z_va, z_va**2])
        elif poly_degree == 3:
            z_tr = logit(tr_mat)
            z_va = logit(va_mat)
            X_tr_feat = np.hstack([z_tr, z_tr**2, z_tr**3])
            X_va_feat = np.hstack([z_va, z_va**2, z_va**3])
        
        # Scale + LR
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr_feat).astype(np.float32)
        X_va_s = scaler.transform(X_va_feat).astype(np.float32)
        
        lr = LogisticRegression(penalty="l2", C=0.5, max_iter=4000, tol=1e-4,
                               solver="lbfgs", n_jobs=-1, random_state=SEED)
        lr.fit(X_tr_s, y_tr)
        
        oof_va = lr.predict_proba(X_va_s)[:, 1].astype(np.float32)
        oof[va_idx] = oof_va
        fold_auc = roc_auc_score(y_va, oof_va)
        fold_aucs.append(fold_auc)
    
    final_auc = roc_auc_score(y, oof)
    return final_auc, fold_aucs


def main():
    t0 = time.time()
    
    train = pd.read_csv(BASE_DIR / "train.csv")
    test = pd.read_csv(BASE_DIR / "test.csv")
    y = (train[TARGET].astype(str).str.strip().str.lower() == "yes").astype(np.int32).values
    
    DROP_COLS = ["customerID", "id"]
    FEATURES = [c for c in train.columns if c not in DROP_COLS + [TARGET]]
    n_feat = len(FEATURES)
    
    X_all, X_test = label_encode(train, test, FEATURES)
    
    # Generate pair indices
    pair_indices = []
    for i in range(n_feat):
        for j in range(i + 1, n_feat):
            pair_indices.append((i, j))
    
    print(f"Features: {n_feat}, Pairs: {len(pair_indices)}")
    print(f"{'='*70}")
    
    # Define ablation variants
    variants = [
        ("1_single_te_raw",          True,  False, 0, "Single features TE → raw → LR"),
        ("2_single_te_logit3",       True,  False, 3, "Single features TE → logit³ → LR"),
        ("3_pair_te_raw",            False, True,  0, "Pair TE → raw → LR"),
        ("4_pair_te_logit1",         False, True,  1, "Pair TE → logit(z) → LR"),
        ("5_pair_te_logit2",         False, True,  2, "Pair TE → logit(z,z²) → LR"),
        ("6_pair_te_logit3",         False, True,  3, "Pair TE → logit(z,z²,z³) → LR  [FULL]"),
        ("7_single_pair_te_logit3",  True,  True,  3, "Single+Pair TE → logit³ → LR"),
    ]
    
    results = {}
    
    for name, use_singles, use_pairs, poly_deg, desc in variants:
        vt0 = time.time()
        n_base = (n_feat if use_singles else 0) + (len(pair_indices) if use_pairs else 0)
        if poly_deg == 0:
            n_dims = n_base
        else:
            n_dims = n_base * poly_deg
        
        print(f"\n--- {name} ---")
        print(f"  {desc}")
        print(f"  Base features: {n_base} → Dims: {n_dims}")
        
        auc, fold_aucs = run_variant(X_all, y, n_feat, pair_indices,
                                      name, use_singles, use_pairs, poly_deg)
        elapsed = time.time() - vt0
        
        results[name] = {
            "auc": float(auc),
            "fold_aucs": [float(a) for a in fold_aucs],
            "dims": n_dims,
            "desc": desc,
            "elapsed": elapsed,
        }
        
        print(f"  AUC: {auc:.6f} ({elapsed:.0f}s)")
        print(f"  Fold AUCs: {[f'{a:.6f}' for a in fold_aucs]}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"ABLATION SUMMARY")
    print(f"{'='*70}")
    print(f"{'Variant':<35} {'Dims':>6} {'AUC':>10} {'Δ from full':>12}")
    print(f"{'-'*65}")
    
    full_auc = results["6_pair_te_logit3"]["auc"]
    for name, r in sorted(results.items(), key=lambda x: x[1]["auc"], reverse=True):
        delta = r["auc"] - full_auc
        print(f"  {r['desc']:<33} {r['dims']:>6} {r['auc']:>10.6f} {delta:>+12.6f}")
    
    print(f"\nTotal time: {time.time()-t0:.0f}s")
    print(json.dumps(results))


if __name__ == "__main__":
    main()

# ===== FILE: v2_run_batch.py =====
#!/usr/bin/env python3
"""
AutoResearch V2 — Dual-GPU Batch Runner (v3 — proper GPU isolation)
Each GPU process gets its own SSH session with CUDA_VISIBLE_DEVICES set so CatBoost
only sees ONE GPU. Both GPU queues run in parallel threads.
"""
import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results" / "v2_from_best"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = RESULTS_DIR / "batch_log.txt"
RESULTS_FILE = RESULTS_DIR / "all_results.json"

GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET = 1500  # 25 min — dual GPU CPU contention can slow things down

BASE_CODE = (BASE_DIR / "v2_experiment_base.py").read_text()

log_lock = threading.Lock()
results_lock = threading.Lock()

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with log_lock:
        print(line, flush=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")

def make_variant(changes):
    code = BASE_CODE
    for old, new in changes:
        if old not in code:
            raise ValueError(f"Patch not found: {old[:80]}...")
        code = code.replace(old, new)
    return code

def kill_gpu_processes(gpu_id):
    """Kill any orphaned python processes using this GPU."""
    try:
        # Kill any exp_g{gpu_id} processes
        subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
             f"pkill -9 -f 'exp_g{gpu_id}_' 2>/dev/null; "
             f"sleep 1; true"],
            capture_output=True, timeout=15
        )
    except:
        pass

def run_on_gpu(exp_code, gpu_id, desc):
    """Upload and run experiment with CUDA_VISIBLE_DEVICES isolation."""
    tmp_name = f"exp_g{gpu_id}_{hash(desc) % 100000}.py"
    tmp_local = BASE_DIR / tmp_name
    tmp_local.write_text(exp_code)

    try:
        # CRITICAL: Kill any orphaned processes from previous runs on this GPU
        kill_gpu_processes(gpu_id)

        r = subprocess.run(
            ["scp", "-o", "ConnectTimeout=10", str(tmp_local),
             f"{GPU_HOST}:{GPU_WORKDIR}/{tmp_name}"],
            capture_output=True, timeout=30
        )
        if r.returncode != 0:
            log(f"  [GPU{gpu_id}] ❌ {desc}: SCP failed — {r.stderr.decode()[:100]}")
            return None, 0

        # Use setsid to create a new process group, so timeout can kill the entire group.
        # Use --signal=KILL --kill-after=10 to force-kill if TERM doesn't work.
        cmd = (
            f"export CUDA_VISIBLE_DEVICES={gpu_id} && "
            f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
            f"timeout --signal=KILL {TIME_BUDGET} python3 -c '"
            f"import sys; sys.path.insert(0, \".\"); "
            f"from {tmp_name[:-3]} import run_experiment; "
            f"import json; auc = run_experiment(gpu_id=0); "
            f"print(json.dumps({{\"auc\": auc}}))"
            f"'"
        )

        start = time.time()
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=60",
             "-o", "ServerAliveCountMax=20", GPU_HOST, cmd],
            capture_output=True, text=True, timeout=TIME_BUDGET + 120
        )
        elapsed = time.time() - start

        if proc.returncode == 0:
            try:
                lines = proc.stdout.strip().split("\n")
                result = json.loads(lines[-1])
                auc = result["auc"]
                log(f"  [GPU{gpu_id}] ✅ {desc}: AUC={auc:.6f} ({elapsed:.0f}s)")
                return auc, elapsed
            except Exception as e:
                log(f"  [GPU{gpu_id}] ❌ {desc}: parse error — {e}")
                return None, elapsed
        elif proc.returncode in (124, 137):
            log(f"  [GPU{gpu_id}] ⏰ {desc}: TIMEOUT ({elapsed:.0f}s)")
            # Kill orphans after timeout
            kill_gpu_processes(gpu_id)
            return None, elapsed
        else:
            log(f"  [GPU{gpu_id}] ❌ {desc}: exit={proc.returncode} ({elapsed:.0f}s)")
            if proc.stderr:
                log(f"    {proc.stderr[-200:]}")
            return None, elapsed

    except subprocess.TimeoutExpired:
        log(f"  [GPU{gpu_id}] ⏰ {desc}: SSH timeout")
        # Kill orphans after SSH timeout — THIS WAS THE MISSING PIECE
        kill_gpu_processes(gpu_id)
        return None, TIME_BUDGET
    except Exception as e:
        log(f"  [GPU{gpu_id}] ❌ {desc}: {e}")
        return None, 0
    finally:
        tmp_local.unlink(missing_ok=True)
        # Clean up remote file
        subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", GPU_HOST, f"rm -f {GPU_WORKDIR}/{tmp_name}"],
            capture_output=True, timeout=10
        )


# ============================================================
# EXPERIMENT DEFINITIONS (same as before)
# ============================================================
experiments = OrderedDict()

# --- FEATURE ENGINEERING ---
experiments["feat_avg_spend_charge_ratio"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n'
     '    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n'
     '    return df')
]
experiments["feat_num_services"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",\n'
     '                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
     '    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n'
     '    return df')
]
experiments["feat_tenure_x_monthly"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    return df')
]
experiments["feat_all_old_combined"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n'
     '    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n'
     '    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",\n'
     '                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
     '    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n'
     '    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
     '    return df')
]
experiments["feat_log_transforms"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["log_tenure"] = np.log1p(df["tenure"])\n'
     '    df["log_total_charges"] = np.log1p(df["TotalCharges"])\n'
     '    df["log_monthly_charges"] = np.log1p(df["MonthlyCharges"])\n'
     '    return df')
]
experiments["feat_contract_x_internet"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)\n'
     '    return df'),
    ('CAT_COLS = [\n    "gender",', 'CAT_COLS = [\n    "contract_internet", "gender",')
]
experiments["feat_contract_x_payment"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["contract_payment"] = df["Contract"].astype(str) + "_" + df["PaymentMethod"].astype(str)\n'
     '    return df'),
    ('CAT_COLS = [\n    "gender",', 'CAT_COLS = [\n    "contract_payment", "gender",')
]
experiments["feat_multi_smooth_te"] = [
    ('            # Group stats (per fold)\n            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)',
     '            # Group stats (per fold)\n'
     '            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)\n'
     '            Xtr_s5, Xva_s5 = add_target_encoding(Xtr, Xva, CAT_COLS, ytr, smooth=5.0)\n'
     '            for c in CAT_COLS:\n'
     '                Xtr[f"{c}__te5"] = Xtr_s5[f"{c}__te"]\n'
     '                Xva[f"{c}__te5"] = Xva_s5[f"{c}__te"]')
]
experiments["feat_freq_encoding"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    for c in ["Contract", "InternetService", "PaymentMethod"]:\n'
     '        df[f"{c}_freq"] = df[c].map(df[c].value_counts(normalize=True)).astype(np.float32)\n'
     '    return df')
]
experiments["feat_service_bundles"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["streaming_bundle"] = ((df["StreamingTV"] == "Yes").astype(int) + (df["StreamingMovies"] == "Yes").astype(int))\n'
     '    df["security_bundle"] = ((df["OnlineSecurity"] == "Yes").astype(int) + (df["OnlineBackup"] == "Yes").astype(int) + (df["DeviceProtection"] == "Yes").astype(int))\n'
     '    return df')
]
experiments["feat_tenure_bins"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["tenure_bin"] = pd.cut(df["tenure"], bins=[-1,6,12,24,48,72], labels=["0-6","7-12","13-24","25-48","49+"]).astype(str)\n'
     '    return df'),
    ('CAT_COLS = [\n    "gender",', 'CAT_COLS = [\n    "tenure_bin", "gender",')
]
experiments["feat_no_internet_count"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    no_int_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
     '    df["no_internet_count"] = sum((df[c] == "No internet service").astype(int) for c in no_int_cols)\n'
     '    return df')
]
experiments["feat_family"] = [
    ('    df = df.copy()\n    return df',
     '    df = df.copy()\n'
     '    df["has_family"] = ((df["Partner"] == "Yes").astype(int) + (df["Dependents"] == "Yes").astype(int))\n'
     '    return df')
]
experiments["feat_group_median"] = [
    ('            # Group stats (per fold)\n            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)',
     '            # Group stats (per fold)\n'
     '            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)\n'
     '            for g in GROUP_COLS:\n'
     '                for n in NUM_COLS:\n'
     '                    med_map = Xtr.groupby(g)[n].median().to_dict()\n'
     '                    Xtr[f"gs_med_{n}_by_{g}"] = Xtr[g].map(med_map).astype(np.float32)\n'
     '                    Xva[f"gs_med_{n}_by_{g}"] = Xva[g].map(med_map).astype(np.float32)')
]
experiments["feat_group_std"] = [
    ('            # Group stats (per fold)\n            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)',
     '            # Group stats (per fold)\n'
     '            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)\n'
     '            for g in GROUP_COLS:\n'
     '                for n in NUM_COLS:\n'
     '                    std_map = Xtr.groupby(g)[n].std().to_dict()\n'
     '                    Xtr[f"gs_std_{n}_by_{g}"] = Xtr[g].map(std_map).astype(np.float32)\n'
     '                    Xva[f"gs_std_{n}_by_{g}"] = Xva[g].map(std_map).astype(np.float32)')
]
experiments["feat_more_group_cols"] = [
    ('GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]',
     'GROUP_COLS = ["Contract", "PaymentMethod", "InternetService", "gender", "PaperlessBilling"]')
]
experiments["feat_group_2way"] = [
    ('            # Group stats (per fold)\n            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)',
     '            # Group stats (per fold)\n'
     '            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)\n'
     '            for g in ["Contract", "InternetService"]:\n'
     '                combo = Xtr[g].astype(str) + "_" + Xtr["PaymentMethod"].astype(str)\n'
     '                combo_va = Xva[g].astype(str) + "_" + Xva["PaymentMethod"].astype(str)\n'
     '                for n in ["MonthlyCharges", "tenure"]:\n'
     '                    mean_map = pd.DataFrame({"g": combo, "v": Xtr[n]}).groupby("g")["v"].mean().to_dict()\n'
     '                    Xtr[f"gs2_{n}_{g}_pay"] = combo.map(mean_map).astype(np.float32)\n'
     '                    Xva[f"gs2_{n}_{g}_pay"] = combo_va.map(mean_map).astype(np.float32)')
]

# --- HYPERPARAMETERS ---
for d in [5, 7, 8, 4]:
    experiments[f"hp_depth_{d}"] = [('depth=6,', f'depth={d},')]
for l2 in [3.0, 5.0, 12.0, 15.0]:
    experiments[f"hp_l2_{l2}"] = [('l2_leaf_reg=8.0,', f'l2_leaf_reg={l2},')]
for bt in [0.3, 0.5, 0.8, 1.0]:
    experiments[f"hp_bt_{bt}"] = [
        ('        early_stopping_rounds=100,',
         f'        bagging_temperature={bt},\n        early_stopping_rounds=100,')]
for rs in [1.0, 3.0, 5.0]:
    experiments[f"hp_rs_{rs}"] = [('random_strength=2.0,', f'random_strength={rs},')]
for md in [5, 20, 50, 100]:
    experiments[f"hp_min_leaf_{md}"] = [
        ('        early_stopping_rounds=100,',
         f'        min_data_in_leaf={md},\n        early_stopping_rounds=100,')]
for es in [200, 300]:
    experiments[f"hp_es_{es}"] = [('early_stopping_rounds=100,', f'early_stopping_rounds={es},')]
experiments["hp_lr0.02_iter7000"] = [
    ('learning_rate=0.03,', 'learning_rate=0.02,'),
    ('iterations=5000,', 'iterations=7000,')]
experiments["hp_lr0.05_iter3000"] = [
    ('learning_rate=0.03,', 'learning_rate=0.05,'),
    ('iterations=5000,', 'iterations=3000,')]
experiments["hp_bc_128"] = [
    ('        early_stopping_rounds=100,',
     '        border_count=128,\n        early_stopping_rounds=100,')]
experiments["hp_bc_254"] = [
    ('        early_stopping_rounds=100,',
     '        border_count=254,\n        early_stopping_rounds=100,')]

# --- ABLATIONS ---
experiments["ablation_no_group_stats"] = [
    ('            # Group stats (per fold)\n            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)',
     '            # Group stats REMOVED')]
experiments["ablation_no_manual_te"] = [
    ('            # Target encoding (per fold)\n            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)',
     '            # Manual TE removed')]
experiments["ablation_group_stats_only"] = [
    ('            # Target encoding (per fold)\n            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)',
     '            # TE removed')]
experiments["hp_te_smooth_10"] = [('SMOOTH = 20.0', 'SMOOTH = 10.0')]
experiments["hp_te_smooth_50"] = [('SMOOTH = 20.0', 'SMOOTH = 50.0')]
experiments["hp_5seeds"] = [
    ('seeds = [42, 52, 62]  # 3 seeds for speed during search',
     'seeds = [42, 52, 62, 72, 82]  # 5 seeds')]
experiments["ablation_group_mc_only"] = [
    ('NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]',
     'NUM_COLS = ["MonthlyCharges"]')]
experiments["feat_group_senior"] = [
    ('NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]',
     'NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]')]


# ============================================================
# DUAL-GPU RUNNER with proper isolation
# ============================================================

def run_gpu_queue(gpu_id, task_list, all_results, baseline_auc):
    """Run a queue of experiments sequentially on one GPU."""
    for name, changes in task_list:
        try:
            variant = make_variant(changes)
        except ValueError as e:
            log(f"❌ {name}: patch failed — {e}")
            with results_lock:
                all_results[name] = {"auc": None, "delta": None, "status": "patch_error"}
            continue

        auc, elapsed = run_on_gpu(variant, gpu_id, name)

        with results_lock:
            if auc is not None:
                delta = auc - baseline_auc
                status = "improved" if delta > 0 else "worse"
                all_results[name] = {"auc": auc, "delta": delta, "status": status, "elapsed": elapsed}
            else:
                all_results[name] = {"auc": None, "delta": None, "status": "failed", "elapsed": elapsed}

            done = sum(1 for k, v in all_results.items()
                      if k != "BASELINE" and v.get("status") not in (None, "baseline"))
            if done % 5 == 0:
                log(f"[PROGRESS] {done}/{len(experiments)} done")
            RESULTS_FILE.write_text(json.dumps(all_results, indent=2))


def main():
    LOG_FILE.write_text("")
    total = len(experiments)

    log(f"\n{'='*60}")
    log(f"AUTORESEARCH V2 — FROM BEST LB MODEL")
    log(f"Total experiments: {total}")
    log(f"Mode: Dual-GPU parallel (CUDA_VISIBLE_DEVICES isolation)")
    log(f"{'='*60}\n")

    # Load prior results
    prior = OrderedDict()
    if RESULTS_FILE.exists():
        try:
            prior = OrderedDict(json.loads(RESULTS_FILE.read_text()))
        except:
            pass

    # Baseline
    if "BASELINE" in prior and prior["BASELINE"].get("auc"):
        baseline_auc = prior["BASELINE"]["auc"]
        log(f"📊 BASELINE AUC (cached): {baseline_auc:.6f}")
    else:
        log("--- Running BASELINE on GPU 0 ---")
        baseline_auc, be = run_on_gpu(BASE_CODE, gpu_id=0, desc="BASELINE")
        if baseline_auc is None:
            log("❌ BASELINE FAILED")
            return
        log(f"📊 BASELINE AUC: {baseline_auc:.6f}")

    all_results = OrderedDict()
    all_results["BASELINE"] = {"auc": baseline_auc, "delta": 0.0, "status": "baseline"}
    for k, v in prior.items():
        if k != "BASELINE":
            all_results[k] = v

    # Filter to remaining experiments (skip successful ones, retry failed)
    remaining = [(n, c) for n, c in experiments.items()
                 if n not in prior or prior[n].get("status") in ("failed",)]
    skip_count = len(experiments) - len(remaining)
    log(f"Skipping {skip_count} completed, running {len(remaining)} remaining\n")

    if not remaining:
        log("All experiments done!")
    else:
        gpu0_tasks = remaining[0::2]
        gpu1_tasks = remaining[1::2]
        log(f"GPU 0: {len(gpu0_tasks)} | GPU 1: {len(gpu1_tasks)}")

        t0 = threading.Thread(target=run_gpu_queue, args=(0, gpu0_tasks, all_results, baseline_auc))
        t1 = threading.Thread(target=run_gpu_queue, args=(1, gpu1_tasks, all_results, baseline_auc))
        t0.start()
        t1.start()
        t0.join()
        t1.join()

    # Final summary
    log(f"\n{'='*60}")
    log(f"FINAL RESULTS — BASELINE AUC: {baseline_auc:.6f}")
    log(f"{'='*60}")

    sorted_res = sorted(
        [(k, v) for k, v in all_results.items() if k != "BASELINE" and v.get("auc")],
        key=lambda x: x[1]["auc"], reverse=True
    )
    for name, r in sorted_res:
        m = "🟢" if r["delta"] > 0 else "🔴"
        log(f"  {m} {name}: AUC={r['auc']:.6f} (Δ={r['delta']:+.6f})")

    failed = [k for k, v in all_results.items() if v.get("status") in ("failed", "error", "patch_error")]
    if failed:
        log(f"\n  Failed ({len(failed)}): {', '.join(failed)}")

    RESULTS_FILE.write_text(json.dumps(all_results, indent=2))
    log(f"\nSaved to {RESULTS_FILE}")
    log("DONE!")


if __name__ == "__main__":
    main()

# ===== FILE: v2_run_combos.py =====
#!/usr/bin/env python3
"""Combination experiments — stacking top improvements from V2."""
import json, time, subprocess
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results" / "v2_from_best"
RESULTS_FILE = RESULTS_DIR / "combo_results.json"
LOG_FILE = RESULTS_DIR / "combo_log.txt"
GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET = 900
BASE_CODE = (BASE_DIR / "v2_experiment_base.py").read_text()
BASELINE_AUC = 0.916517  # from previous run

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def make_variant(changes):
    code = BASE_CODE
    for old, new in changes:
        if old not in code:
            raise ValueError(f"Patch not found: {old[:80]}...")
        code = code.replace(old, new)
    return code

def run_on_gpu0(exp_code, desc):
    tmp_name = f"exp_combo_{hash(desc) % 100000}.py"
    tmp_local = BASE_DIR / tmp_name
    tmp_local.write_text(exp_code)
    try:
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       f"pkill -9 -f 'exp_combo_' 2>/dev/null; true"],
                      capture_output=True, timeout=15)
        subprocess.run(
            ["scp", "-o", "ConnectTimeout=10", str(tmp_local),
             f"{GPU_HOST}:{GPU_WORKDIR}/{tmp_name}"],
            capture_output=True, timeout=30, check=True)
        cmd = (
            f"export CUDA_VISIBLE_DEVICES=0 && "
            f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
            f"timeout --signal=KILL {TIME_BUDGET} python3 -c '"
            f"import sys; sys.path.insert(0, \".\"); "
            f"from {tmp_name[:-3]} import run_experiment; "
            f"import json; auc = run_experiment(gpu_id=0); "
            f"print(json.dumps({{\"auc\": auc}}))"
            f"'"
        )
        start = time.time()
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=60",
             "-o", "ServerAliveCountMax=20", GPU_HOST, cmd],
            capture_output=True, text=True, timeout=TIME_BUDGET + 120)
        elapsed = time.time() - start
        if proc.returncode == 0:
            lines = proc.stdout.strip().split("\n")
            result = json.loads(lines[-1])
            auc = result["auc"]
            log(f"  ✅ {desc}: AUC={auc:.6f} ({elapsed:.0f}s)")
            return auc, elapsed
        else:
            log(f"  ❌ {desc}: exit={proc.returncode} ({elapsed:.0f}s)")
            subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                           "pkill -9 -f 'exp_combo_' 2>/dev/null; true"],
                          capture_output=True, timeout=15)
            return None, elapsed
    except Exception as e:
        log(f"  ❌ {desc}: {e}")
        return None, 0
    finally:
        tmp_local.unlink(missing_ok=True)
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       f"rm -f {GPU_WORKDIR}/{tmp_name}"],
                      capture_output=True, timeout=10)

# ============================================================
# PATCHES — reusable building blocks
# ============================================================

PATCH_BT_03 = ('        early_stopping_rounds=100,',
               '        bagging_temperature=0.3,\n        early_stopping_rounds=100,')

PATCH_BT_05 = ('        early_stopping_rounds=100,',
               '        bagging_temperature=0.5,\n        early_stopping_rounds=100,')

PATCH_BC_254 = ('        early_stopping_rounds=100,',
                '        border_count=254,\n        early_stopping_rounds=100,')

# For combos with bt AND bc, we need to chain them
PATCH_BT_03_BC_254 = ('        early_stopping_rounds=100,',
                      '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=100,')

PATCH_BT_05_BC_254 = ('        early_stopping_rounds=100,',
                      '        bagging_temperature=0.5,\n        border_count=254,\n        early_stopping_rounds=100,')

PATCH_BT_03_BC_254_RS5_L215 = ('        early_stopping_rounds=100,',
                                '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=100,')

PATCH_DEPTH_5 = ('depth=6,', 'depth=5,')
PATCH_ES_300 = ('early_stopping_rounds=100,', 'early_stopping_rounds=300,')
PATCH_RS_5 = ('random_strength=2.0,', 'random_strength=5.0,')
PATCH_L2_15 = ('l2_leaf_reg=8.0,', 'l2_leaf_reg=15.0,')

PATCH_ALL_OLD_FEATS = (
    '    df = df.copy()\n    return df',
    '    df = df.copy()\n'
    '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n'
    '    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n'
    '    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",\n'
    '                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
    '    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n'
    '    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
    '    return df'
)

PATCH_NO_MANUAL_TE = (
    '            # Target encoding (per fold)\n            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)',
    '            # Manual TE removed'
)

# ============================================================
# COMBINATION EXPERIMENTS
# ============================================================

experiments = OrderedDict()

# 1. bt=0.3 + all_old_features
experiments["combo_bt03_feats"] = [
    PATCH_BT_03,
    PATCH_ALL_OLD_FEATS,
]

# 2. bt=0.3 + bc=254
experiments["combo_bt03_bc254"] = [
    PATCH_BT_03_BC_254,
]

# 3. bt=0.3 + depth=5
experiments["combo_bt03_depth5"] = [
    PATCH_BT_03,
    PATCH_DEPTH_5,
]

# 4. bt=0.3 + es=300
experiments["combo_bt03_es300"] = [
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        early_stopping_rounds=300,'),
]

# 5. bt=0.3 + bc=254 + es=300
experiments["combo_bt03_bc254_es300"] = [
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

# 6. bt=0.3 + depth=5 + bc=254
experiments["combo_bt03_depth5_bc254"] = [
    PATCH_DEPTH_5,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=100,'),
]

# 7. bt=0.3 + feats + bc=254
experiments["combo_bt03_feats_bc254"] = [
    PATCH_ALL_OLD_FEATS,
    PATCH_BT_03_BC_254,
]

# 8. bt=0.3 + feats + bc=254 + es=300
experiments["combo_bt03_feats_bc254_es300"] = [
    PATCH_ALL_OLD_FEATS,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

# 9. bt=0.3 + depth=5 + feats + bc=254 + es=300
experiments["combo_bt03_depth5_feats_bc254_es300"] = [
    PATCH_ALL_OLD_FEATS,
    PATCH_DEPTH_5,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

# 10. bt=0.5 + feats + bc=254
experiments["combo_bt05_feats_bc254"] = [
    PATCH_ALL_OLD_FEATS,
    PATCH_BT_05_BC_254,
]

# 11. top HPs only: bt=0.3 + bc=254 + es=300 + rs=5.0 + l2=15.0
experiments["combo_top_hps"] = [
    PATCH_RS_5,
    PATCH_L2_15,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

# 12. kitchen sink: bt=0.3 + depth=5 + bc=254 + es=300 + rs=5.0 + l2=15.0 + feats + no_manual_te
experiments["combo_kitchen_sink"] = [
    PATCH_ALL_OLD_FEATS,
    PATCH_NO_MANUAL_TE,
    PATCH_DEPTH_5,
    PATCH_RS_5,
    PATCH_L2_15,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

# All-positive-features mega patch
PATCH_ALL_POSITIVE_FEATS = (
    '    df = df.copy()\n    return df',
    '    df = df.copy()\n'
    '    # avg_monthly_spend + charge_ratio\n'
    '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n'
    '    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n'
    '    # num_services\n'
    '    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",\n'
    '                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
    '    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n'
    '    # tenure_x_monthly\n'
    '    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
    '    # service bundles\n'
    '    df["streaming_bundle"] = ((df["StreamingTV"] == "Yes").astype(int) + (df["StreamingMovies"] == "Yes").astype(int))\n'
    '    df["security_bundle"] = ((df["OnlineSecurity"] == "Yes").astype(int) + (df["OnlineBackup"] == "Yes").astype(int) + (df["DeviceProtection"] == "Yes").astype(int))\n'
    '    # freq encoding\n'
    '    for c in ["Contract", "InternetService", "PaymentMethod"]:\n'
    '        df[f"{c}_freq"] = df[c].map(df[c].value_counts(normalize=True)).astype(np.float32)\n'
    '    # log transforms\n'
    '    df["log_tenure"] = np.log1p(df["tenure"])\n'
    '    df["log_total_charges"] = np.log1p(df["TotalCharges"])\n'
    '    df["log_monthly_charges"] = np.log1p(df["MonthlyCharges"])\n'
    '    # no internet count\n'
    '    no_int_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
    '    df["no_internet_count"] = sum((df[c] == "No internet service").astype(int) for c in no_int_cols)\n'
    '    # contract x internet interaction\n'
    '    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)\n'
    '    # tenure bins\n'
    '    df["tenure_bin"] = pd.cut(df["tenure"], bins=[-1,6,12,24,48,72], labels=["0-6","7-12","13-24","25-48","49+"]).astype(str)\n'
    '    return df'
)

PATCH_ALL_POSITIVE_CATS = (
    'CAT_COLS = [\n    "gender",',
    'CAT_COLS = [\n    "contract_internet", "tenure_bin", "gender",'
)

PATCH_ALL_POSITIVE_GROUP_EXTRAS = (
    '            # Group stats (per fold)\n            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)',
    '            # Group stats (per fold)\n'
    '            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)\n'
    '            # Group medians\n'
    '            for g in GROUP_COLS:\n'
    '                for n in NUM_COLS:\n'
    '                    med_map = Xtr.groupby(g)[n].median().to_dict()\n'
    '                    Xtr[f"gs_med_{n}_by_{g}"] = Xtr[g].map(med_map).astype(np.float32)\n'
    '                    Xva[f"gs_med_{n}_by_{g}"] = Xva[g].map(med_map).astype(np.float32)\n'
    '            # Group stds\n'
    '            for g in GROUP_COLS:\n'
    '                for n in NUM_COLS:\n'
    '                    std_map = Xtr.groupby(g)[n].std().to_dict()\n'
    '                    Xtr[f"gs_std_{n}_by_{g}"] = Xtr[g].map(std_map).astype(np.float32)\n'
    '                    Xva[f"gs_std_{n}_by_{g}"] = Xva[g].map(std_map).astype(np.float32)\n'
    '            # Multi-smooth TE\n'
    '            Xtr_s5, Xva_s5 = add_target_encoding(Xtr, Xva, CAT_COLS, ytr, smooth=5.0)\n'
    '            for c in CAT_COLS:\n'
    '                Xtr[f"{c}__te5"] = Xtr_s5[f"{c}__te"]\n'
    '                Xva[f"{c}__te5"] = Xva_s5[f"{c}__te"]'
)

# 13. ALL positive features combined (no HP changes)
experiments["combo_all_positive_feats"] = [
    PATCH_ALL_POSITIVE_FEATS,
    PATCH_ALL_POSITIVE_CATS,
    PATCH_ALL_POSITIVE_GROUP_EXTRAS,
]

# 14. ALL positive features + top HPs (bt=0.3 + bc=254 + es=300)
experiments["combo_all_positive_feats_top_hps"] = [
    PATCH_ALL_POSITIVE_FEATS,
    PATCH_ALL_POSITIVE_CATS,
    PATCH_ALL_POSITIVE_GROUP_EXTRAS,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

# 15. ALL positive features + ALL positive HPs
experiments["combo_all_positive_everything"] = [
    PATCH_ALL_POSITIVE_FEATS,
    PATCH_ALL_POSITIVE_CATS,
    PATCH_ALL_POSITIVE_GROUP_EXTRAS,
    PATCH_RS_5,
    PATCH_L2_15,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]


def main():
    LOG_FILE.write_text("")
    log(f"\n{'='*60}")
    log(f"COMBINATION EXPERIMENTS — {len(experiments)} combos")
    log(f"Baseline: {BASELINE_AUC:.6f}")
    log(f"{'='*60}\n")

    results = OrderedDict()

    for i, (name, changes) in enumerate(experiments.items(), 1):
        log(f"--- [{i}/{len(experiments)}] {name} ---")
        try:
            variant = make_variant(changes)
        except ValueError as e:
            log(f"  ❌ patch error: {e}")
            results[name] = {"auc": None, "status": "patch_error", "error": str(e)}
            continue

        auc, elapsed = run_on_gpu0(variant, name)
        if auc is not None:
            delta = auc - BASELINE_AUC
            results[name] = {"auc": auc, "delta": delta,
                           "status": "improved" if delta > 0 else "worse",
                           "elapsed": elapsed}
        else:
            results[name] = {"auc": None, "status": "failed", "elapsed": elapsed}

        RESULTS_FILE.write_text(json.dumps(results, indent=2))

    # Summary
    log(f"\n{'='*60}")
    log(f"COMBO RESULTS — Baseline: {BASELINE_AUC:.6f}")
    log(f"{'='*60}")
    sorted_res = sorted(
        [(k, v) for k, v in results.items() if v.get("auc")],
        key=lambda x: x[1]["auc"], reverse=True)
    for name, r in sorted_res:
        m = "🟢" if r["delta"] > 0 else "🔴"
        log(f"  {m} {name}: {r['auc']:.6f} (Δ={r['delta']:+.6f})")
    log("DONE!")

if __name__ == "__main__":
    main()

# ===== FILE: v2_run_combos_extra.py =====
#!/usr/bin/env python3
"""Run just the 3 all-positive-features combo experiments."""
import json, time, subprocess
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results" / "v2_from_best"
RESULTS_FILE = RESULTS_DIR / "combo_results.json"
LOG_FILE = RESULTS_DIR / "combo_log.txt"
GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET = 900
BASE_CODE = (BASE_DIR / "v2_experiment_base.py").read_text()
BASELINE_AUC = 0.916517
import numpy as np

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def make_variant(changes):
    code = BASE_CODE
    for old, new in changes:
        if old not in code:
            raise ValueError(f"Patch not found: {old[:80]}...")
        code = code.replace(old, new)
    return code

def run_on_gpu0(exp_code, desc):
    tmp_name = f"exp_combo_{hash(desc) % 100000}.py"
    tmp_local = BASE_DIR / tmp_name
    tmp_local.write_text(exp_code)
    try:
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       "pkill -9 -f 'exp_combo_' 2>/dev/null; true"],
                      capture_output=True, timeout=15)
        subprocess.run(
            ["scp", "-o", "ConnectTimeout=10", str(tmp_local),
             f"{GPU_HOST}:{GPU_WORKDIR}/{tmp_name}"],
            capture_output=True, timeout=30, check=True)
        cmd = (
            f"export CUDA_VISIBLE_DEVICES=0 && "
            f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
            f"timeout --signal=KILL {TIME_BUDGET} python3 -c '"
            f"import sys; sys.path.insert(0, \".\"); "
            f"from {tmp_name[:-3]} import run_experiment; "
            f"import json; auc = run_experiment(gpu_id=0); "
            f"print(json.dumps({{\"auc\": auc}}))"
            f"'"
        )
        start = time.time()
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=60",
             "-o", "ServerAliveCountMax=20", GPU_HOST, cmd],
            capture_output=True, text=True, timeout=TIME_BUDGET + 120)
        elapsed = time.time() - start
        if proc.returncode == 0:
            lines = proc.stdout.strip().split("\n")
            result = json.loads(lines[-1])
            auc = result["auc"]
            log(f"  ✅ {desc}: AUC={auc:.6f} ({elapsed:.0f}s)")
            return auc, elapsed
        else:
            log(f"  ❌ {desc}: exit={proc.returncode} ({elapsed:.0f}s)")
            return None, elapsed
    except Exception as e:
        log(f"  ❌ {desc}: {e}")
        return None, 0
    finally:
        tmp_local.unlink(missing_ok=True)
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       f"rm -f {GPU_WORKDIR}/{tmp_name}"],
                      capture_output=True, timeout=10)

# All-positive-features patches
PATCH_ALL_POSITIVE_FEATS = (
    '    df = df.copy()\n    return df',
    '    df = df.copy()\n'
    '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n'
    '    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n'
    '    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",\n'
    '                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
    '    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n'
    '    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n'
    '    df["streaming_bundle"] = ((df["StreamingTV"] == "Yes").astype(int) + (df["StreamingMovies"] == "Yes").astype(int))\n'
    '    df["security_bundle"] = ((df["OnlineSecurity"] == "Yes").astype(int) + (df["OnlineBackup"] == "Yes").astype(int) + (df["DeviceProtection"] == "Yes").astype(int))\n'
    '    for c in ["Contract", "InternetService", "PaymentMethod"]:\n'
    '        df[f"{c}_freq"] = df[c].map(df[c].value_counts(normalize=True)).astype(np.float32)\n'
    '    df["log_tenure"] = np.log1p(df["tenure"])\n'
    '    df["log_total_charges"] = np.log1p(df["TotalCharges"])\n'
    '    df["log_monthly_charges"] = np.log1p(df["MonthlyCharges"])\n'
    '    no_int_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]\n'
    '    df["no_internet_count"] = sum((df[c] == "No internet service").astype(int) for c in no_int_cols)\n'
    '    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)\n'
    '    df["tenure_bin"] = pd.cut(df["tenure"], bins=[-1,6,12,24,48,72], labels=["0-6","7-12","13-24","25-48","49+"]).astype(str)\n'
    '    return df'
)
PATCH_ALL_POSITIVE_CATS = (
    'CAT_COLS = [\n    "gender",',
    'CAT_COLS = [\n    "contract_internet", "tenure_bin", "gender",'
)
PATCH_ALL_POSITIVE_GROUP_EXTRAS = (
    '            # Group stats (per fold)\n            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)',
    '            # Group stats (per fold)\n'
    '            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)\n'
    '            for g in GROUP_COLS:\n'
    '                for n in NUM_COLS:\n'
    '                    med_map = Xtr.groupby(g)[n].median().to_dict()\n'
    '                    Xtr[f"gs_med_{n}_by_{g}"] = Xtr[g].map(med_map).astype(np.float32)\n'
    '                    Xva[f"gs_med_{n}_by_{g}"] = Xva[g].map(med_map).astype(np.float32)\n'
    '            for g in GROUP_COLS:\n'
    '                for n in NUM_COLS:\n'
    '                    std_map = Xtr.groupby(g)[n].std().to_dict()\n'
    '                    Xtr[f"gs_std_{n}_by_{g}"] = Xtr[g].map(std_map).astype(np.float32)\n'
    '                    Xva[f"gs_std_{n}_by_{g}"] = Xva[g].map(std_map).astype(np.float32)\n'
    '            Xtr_s5, Xva_s5 = add_target_encoding(Xtr, Xva, CAT_COLS, ytr, smooth=5.0)\n'
    '            for c in CAT_COLS:\n'
    '                Xtr[f"{c}__te5"] = Xtr_s5[f"{c}__te"]\n'
    '                Xva[f"{c}__te5"] = Xva_s5[f"{c}__te"]'
)

experiments = OrderedDict()

experiments["combo_all_positive_feats"] = [
    PATCH_ALL_POSITIVE_FEATS,
    PATCH_ALL_POSITIVE_CATS,
    PATCH_ALL_POSITIVE_GROUP_EXTRAS,
]

experiments["combo_all_positive_feats_top_hps"] = [
    PATCH_ALL_POSITIVE_FEATS,
    PATCH_ALL_POSITIVE_CATS,
    PATCH_ALL_POSITIVE_GROUP_EXTRAS,
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

experiments["combo_all_positive_everything"] = [
    PATCH_ALL_POSITIVE_FEATS,
    PATCH_ALL_POSITIVE_CATS,
    PATCH_ALL_POSITIVE_GROUP_EXTRAS,
    ('random_strength=2.0,', 'random_strength=5.0,'),
    ('l2_leaf_reg=8.0,', 'l2_leaf_reg=15.0,'),
    ('        early_stopping_rounds=100,',
     '        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,'),
]

def main():
    # Load existing results
    results = OrderedDict(json.loads(RESULTS_FILE.read_text()))
    log(f"\n{'='*60}")
    log(f"ALL-POSITIVE-FEATURES COMBOS — 3 experiments")
    log(f"Baseline: {BASELINE_AUC:.6f}")
    log(f"{'='*60}\n")

    for i, (name, changes) in enumerate(experiments.items(), 1):
        if name in results:
            log(f"  ⏭️ {name} already done, skipping")
            continue
        log(f"--- [{i}/3] {name} ---")
        try:
            variant = make_variant(changes)
        except ValueError as e:
            log(f"  ❌ patch error: {e}")
            results[name] = {"auc": None, "status": "patch_error", "error": str(e)}
            continue

        auc, elapsed = run_on_gpu0(variant, name)
        if auc is not None:
            delta = auc - BASELINE_AUC
            results[name] = {"auc": auc, "delta": delta,
                           "status": "improved" if delta > 0 else "worse",
                           "elapsed": elapsed}
        else:
            results[name] = {"auc": None, "status": "failed", "elapsed": elapsed}
        RESULTS_FILE.write_text(json.dumps(results, indent=2))

    # Summary
    log(f"\n{'='*60}")
    log(f"ALL COMBO RESULTS — Baseline: {BASELINE_AUC:.6f}")
    log(f"{'='*60}")
    sorted_res = sorted(
        [(k, v) for k, v in results.items() if v.get("auc")],
        key=lambda x: x[1]["auc"], reverse=True)
    for name, r in sorted_res:
        m = "🟢" if r["delta"] > 0 else "🔴"
        log(f"  {m} {name}: {r['auc']:.6f} (Δ={r['delta']:+.6f})")
    log("DONE!")

if __name__ == "__main__":
    main()

# ===== FILE: v2_run_gpu0_only.py =====
#!/usr/bin/env python3
"""GPU 0-only runner for remaining experiments."""
import json, time, subprocess
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results" / "v2_from_best"
RESULTS_FILE = RESULTS_DIR / "all_results.json"
LOG_FILE = RESULTS_DIR / "batch_log.txt"
GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET = 900
BASE_CODE = (BASE_DIR / "v2_experiment_base.py").read_text()

# Import experiment definitions
import importlib.util
spec = importlib.util.spec_from_file_location("batch", BASE_DIR / "v2_run_batch.py")
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
experiments = batch.experiments

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def make_variant(changes):
    code = BASE_CODE
    for old, new in changes:
        if old not in code:
            raise ValueError(f"Patch not found: {old[:80]}...")
        code = code.replace(old, new)
    return code

def run_on_gpu0(exp_code, desc):
    tmp_name = f"exp_run_{hash(desc) % 100000}.py"
    tmp_local = BASE_DIR / tmp_name
    tmp_local.write_text(exp_code)
    try:
        # Kill any orphans first
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       f"pkill -9 -f 'exp_run_' 2>/dev/null; true"],
                      capture_output=True, timeout=15)

        subprocess.run(
            ["scp", "-o", "ConnectTimeout=10", str(tmp_local),
             f"{GPU_HOST}:{GPU_WORKDIR}/{tmp_name}"],
            capture_output=True, timeout=30, check=True)

        cmd = (
            f"export CUDA_VISIBLE_DEVICES=0 && "
            f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
            f"timeout --signal=KILL {TIME_BUDGET} python3 -c '"
            f"import sys; sys.path.insert(0, \".\"); "
            f"from {tmp_name[:-3]} import run_experiment; "
            f"import json; auc = run_experiment(gpu_id=0); "
            f"print(json.dumps({{\"auc\": auc}}))"
            f"'"
        )

        start = time.time()
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=60",
             "-o", "ServerAliveCountMax=20", GPU_HOST, cmd],
            capture_output=True, text=True, timeout=TIME_BUDGET + 120)
        elapsed = time.time() - start

        if proc.returncode == 0:
            lines = proc.stdout.strip().split("\n")
            result = json.loads(lines[-1])
            auc = result["auc"]
            log(f"  ✅ {desc}: AUC={auc:.6f} ({elapsed:.0f}s)")
            return auc, elapsed
        else:
            log(f"  ❌ {desc}: exit={proc.returncode} ({elapsed:.0f}s)")
            subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                           f"pkill -9 -f 'exp_run_' 2>/dev/null; true"],
                          capture_output=True, timeout=15)
            return None, elapsed
    except Exception as e:
        log(f"  ❌ {desc}: {e}")
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       f"pkill -9 -f 'exp_run_' 2>/dev/null; true"],
                      capture_output=True, timeout=15)
        return None, 0
    finally:
        tmp_local.unlink(missing_ok=True)
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       f"rm -f {GPU_WORKDIR}/{tmp_name}"],
                      capture_output=True, timeout=10)

def main():
    results = OrderedDict(json.loads(RESULTS_FILE.read_text()))
    baseline_auc = results["BASELINE"]["auc"]

    remaining = [(n, c) for n, c in experiments.items()
                 if n not in results or results[n].get("status") == "failed"]

    log(f"\n{'='*60}")
    log(f"GPU 0-ONLY RUNNER — {len(remaining)} remaining experiments")
    log(f"Baseline: {baseline_auc:.6f}")
    log(f"{'='*60}\n")

    for i, (name, changes) in enumerate(remaining, 1):
        log(f"--- [{i}/{len(remaining)}] {name} ---")
        try:
            variant = make_variant(changes)
        except ValueError as e:
            log(f"  ❌ patch error: {e}")
            results[name] = {"auc": None, "delta": None, "status": "patch_error"}
            continue

        auc, elapsed = run_on_gpu0(variant, name)
        if auc is not None:
            delta = auc - baseline_auc
            results[name] = {"auc": auc, "delta": delta,
                           "status": "improved" if delta > 0 else "worse",
                           "elapsed": elapsed}
        else:
            results[name] = {"auc": None, "delta": None, "status": "failed", "elapsed": elapsed}

        RESULTS_FILE.write_text(json.dumps(results, indent=2))

    # Final summary
    log(f"\n{'='*60}")
    log(f"ALL DONE — BASELINE: {baseline_auc:.6f}")
    log(f"{'='*60}")
    sorted_res = sorted(
        [(k, v) for k, v in results.items() if k != "BASELINE" and v.get("auc")],
        key=lambda x: x[1]["auc"], reverse=True)
    for name, r in sorted_res:
        m = "🟢" if r["delta"] > 0 else "🔴"
        log(f"  {m} {name}: {r['auc']:.6f} (Δ={r['delta']:+.6f})")
    failed = [k for k, v in results.items() if v.get("status") in ("failed", "patch_error")]
    if failed:
        log(f"\n  Still failed: {', '.join(failed)}")
    log("DONE!")

if __name__ == "__main__":
    main()

# ===== FILE: v2_submit_top10.py =====
#!/usr/bin/env python3
"""
Submit top 10 combo configs to Kaggle.
For each config: 5-fold CV (7 seeds) + full-train predictions + submit.
Runs on GPU 0 only.
"""
import json, time, requests, os, subprocess, sys
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

BASE_DIR = Path(__file__).resolve().parent
SUB_DIR = BASE_DIR / "submissions" / "combos"
LOG_FILE = BASE_DIR / "results" / "v2_from_best" / "submission_log.txt"
SUB_DIR.mkdir(parents=True, exist_ok=True)

GPU_HOST = "yourslewis@192.168.0.23"
GPU_WORKDIR = "/home/yourslewis/autoresearch_kaggle"
GPU_VENV = "/home/yourslewis/kaggle_envs/s6e3/bin/activate"
TIME_BUDGET = 1800  # 30 min for full submission pipeline

from kaggle_auth import get_kaggle_headers
KAGGLE_COMP = 'playground-series-s6e3'

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def submit_to_kaggle(filepath, description):
    H = get_kaggle_headers()
    BASE = 'https://www.kaggle.com/api/v1'
    fsize = os.path.getsize(filepath)
    epoch = int(time.time())
    try:
        r1 = requests.post(f'{BASE}/competitions/{KAGGLE_COMP}/submissions/url/{fsize}/{epoch}',
                           headers=H, data={'fileName': 'submission.csv'})
        data = r1.json()
        with open(filepath, 'rb') as f:
            requests.put(data['createUrl'], data=f)
        r3 = requests.post(f'{BASE}/competitions/submissions/submit/{KAGGLE_COMP}',
                           headers=H, data={'blobFileTokens': data['token'],
                                            'submissionDescription': description})
        result = r3.json()
        log(f"    Kaggle: {result.get('message','')}")
        return True
    except Exception as e:
        log(f"    Submit failed: {e}")
        return False

# ============================================================
# SUBMISSION TEMPLATE — runs on GPU server
# ============================================================

SUBMISSION_TEMPLATE = '''
import numpy as np, pandas as pd, json, warnings, random
warnings.filterwarnings('ignore')
from catboost import CatBoostClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from pathlib import Path

BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")
SEED = 42
N_SEEDS = 7
N_FOLDS = 5

CAT_COLS = {cat_cols}

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0

def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)

def add_features(df):
    df = df.copy()
{feature_code}
    return df

def add_te(tr, other, cols, ytr, smooth=SMOOTH):
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, ot2 = tr.copy(), other.copy()
    for c in cols:
        g = pd.DataFrame({{c: tr[c].astype(str), "t": ys}})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{{c}}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        ot2[nc] = other[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, ot2

def add_group_stats(tr, other, group_cols, num_cols):
    tr2, ot2 = tr.copy(), other.copy()
    for g in group_cols:
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            tr2[f"gs_mean_{{n}}_by_{{g}}"] = tr[g].map(mean_map).astype(np.float32)
            ot2[f"gs_mean_{{n}}_by_{{g}}"] = other[g].map(mean_map).astype(np.float32)
            tr2[f"gs_resid_{{n}}_by_{{g}}"] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            ot2[f"gs_resid_{{n}}_by_{{g}}"] = (other[n].astype(float) - other[g].map(mean_map).astype(float)).astype(np.float32)
            tr2[f"gs_ratio_{{n}}_by_{{g}}"] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            ot2[f"gs_ratio_{{n}}_by_{{g}}"] = (other[n].astype(float) / (other[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, ot2

{extra_fold_code}

def get_model(seed=SEED):
    return CatBoostClassifier(
        iterations=5000,
        learning_rate=0.03,
{model_params}
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=seed,
        task_type="GPU",
        devices="0",
    )

def main():
    set_seed()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    test_df = pd.read_csv(BASE_DIR / "test.csv")
    y = (train_df["Churn"] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=["Churn"]))
    X_test = add_features(test_df)

    # CV for validation
    all_oof = np.zeros((N_SEEDS, len(X)))
    all_test = np.zeros((N_SEEDS, len(X_test)))

    for si in range(N_SEEDS):
        seed = SEED + si
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))
        test_preds = np.zeros(len(X_test))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

{te_code}
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)
            # Also prepare test with train fold stats
            _, Xte_fold = add_group_stats(Xtr, X_test.copy(), GROUP_COLS, NUM_COLS)
{te_test_code}
{extra_fold_apply}

            fc = [c for c in Xtr.columns if c != "id"]
            ci = [fc.index(c) for c in CAT_COLS if c in fc]

            model = get_model(seed=seed)
            model.fit(Xtr[fc], ytr, cat_features=ci, eval_set=(Xva[fc], yva), use_best_model=True)

            oof[vidx] = model.predict_proba(Xva[fc])[:, 1]
            test_preds += model.predict_proba(Xte_fold[fc])[:, 1] / N_FOLDS

        all_oof[si] = oof
        all_test[si] = test_preds
        seed_auc = roc_auc_score(y, oof)
        print(f"Seed {{seed}}: AUC={{seed_auc:.6f}}", flush=True)

    ensemble_oof = all_oof.mean(axis=0)
    ensemble_test = all_test.mean(axis=0)
    cv_auc = roc_auc_score(y, ensemble_oof)
    print(f"Ensemble CV AUC: {{cv_auc:.6f}}", flush=True)

    # Save submission
    sub = pd.DataFrame({{"id": test_df["id"], "Churn": ensemble_test}})
    sub.to_csv(BASE_DIR / "submission.csv", index=False)
    print(json.dumps({{"cv_auc": cv_auc}}))

if __name__ == "__main__":
    main()
'''

# ============================================================
# TOP 10 CONFIGS
# ============================================================

configs = OrderedDict()

# 1. combo_kitchen_sink: bt=0.3 + depth=5 + bc=254 + es=300 + rs=5 + l2=15 + old_features + no_manual_te
configs["combo_kitchen_sink"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]\n    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
    "model_params": '        depth=5,\n        l2_leaf_reg=15.0,\n        random_strength=5.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,',
    "use_te": False,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.917134,
}

# 2. combo_bt03_depth5_feats_bc254_es300: bt=0.3 + depth=5 + feats + bc=254 + es=300
configs["combo_bt03_depth5_feats_bc254_es300"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]\n    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
    "model_params": '        depth=5,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.917116,
}

# 3. combo_bt03_feats_bc254_es300
configs["combo_bt03_feats_bc254_es300"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]\n    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
    "model_params": '        depth=6,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.917087,
}

# 4. combo_all_positive_feats_top_hps
configs["combo_all_positive_feats_top_hps"] = {
    "cat_cols": '["contract_internet","tenure_bin","gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]\n    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]\n    df["streaming_bundle"] = ((df["StreamingTV"] == "Yes").astype(int) + (df["StreamingMovies"] == "Yes").astype(int))\n    df["security_bundle"] = ((df["OnlineSecurity"] == "Yes").astype(int) + (df["OnlineBackup"] == "Yes").astype(int) + (df["DeviceProtection"] == "Yes").astype(int))\n    for c in ["Contract", "InternetService", "PaymentMethod"]:\n        df[f"{c}_freq"] = df[c].map(df[c].value_counts(normalize=True)).astype(np.float32)\n    df["log_tenure"] = np.log1p(df["tenure"])\n    df["log_total_charges"] = np.log1p(df["TotalCharges"])\n    df["log_monthly_charges"] = np.log1p(df["MonthlyCharges"])\n    no_int_cols = ["OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]\n    df["no_internet_count"] = sum((df[c] == "No internet service").astype(int) for c in no_int_cols)\n    df["contract_internet"] = df["Contract"].astype(str) + "_" + df["InternetService"].astype(str)\n    df["tenure_bin"] = pd.cut(df["tenure"], bins=[-1,6,12,24,48,72], labels=["0-6","7-12","13-24","25-48","49+"]).astype(str)',
    "model_params": '        depth=6,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "            # Group median+std+multi-TE applied in extra_fold_apply\n            for g in GROUP_COLS:\n                for n in NUM_COLS:\n                    med_map = Xtr.groupby(g)[n].median().to_dict()\n                    Xtr[f'gs_med_{n}_by_{g}'] = Xtr[g].map(med_map).astype(np.float32)\n                    Xva[f'gs_med_{n}_by_{g}'] = Xva[g].map(med_map).astype(np.float32)\n                    Xte_fold[f'gs_med_{n}_by_{g}'] = X_test[g].map(med_map).astype(np.float32) if g in X_test.columns else np.float32(0)\n                    std_map = Xtr.groupby(g)[n].std().to_dict()\n                    Xtr[f'gs_std_{n}_by_{g}'] = Xtr[g].map(std_map).astype(np.float32)\n                    Xva[f'gs_std_{n}_by_{g}'] = Xva[g].map(std_map).astype(np.float32)\n                    Xte_fold[f'gs_std_{n}_by_{g}'] = X_test[g].map(std_map).astype(np.float32) if g in X_test.columns else np.float32(0)",
    "cv_auc": 0.917078,
}

# 5. combo_bt03_feats_bc254
configs["combo_bt03_feats_bc254"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]\n    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
    "model_params": '        depth=6,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=100,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.917048,
}

# 6. combo_bt03_bc254_es300
configs["combo_bt03_bc254_es300"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    pass',
    "model_params": '        depth=6,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.917010,
}

# 7. combo_top_hps: bt=0.3 + bc=254 + es=300 + rs=5 + l2=15
configs["combo_top_hps"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    pass',
    "model_params": '        depth=6,\n        l2_leaf_reg=15.0,\n        random_strength=5.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=300,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.917010,
}

# 8. combo_bt05_feats_bc254
configs["combo_bt05_feats_bc254"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)\n    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)\n    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]\n    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)\n    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]',
    "model_params": '        depth=6,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.5,\n        border_count=254,\n        early_stopping_rounds=100,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.916993,
}

# 9. combo_bt03_depth5_bc254
configs["combo_bt03_depth5_bc254"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    pass',
    "model_params": '        depth=5,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=100,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.916985,
}

# 10. combo_bt03_bc254
configs["combo_bt03_bc254"] = {
    "cat_cols": '["gender","Partner","Dependents","PhoneService","MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling","PaymentMethod"]',
    "feature_code": '    pass',
    "model_params": '        depth=6,\n        l2_leaf_reg=8.0,\n        random_strength=2.0,\n        bagging_temperature=0.3,\n        border_count=254,\n        early_stopping_rounds=100,',
    "use_te": True,
    "extra_fold_code": "",
    "extra_fold_apply": "",
    "cv_auc": 0.916958,
}


def build_script(cfg):
    """Build the submission script from config."""
    te_code = '            Xtr, Xva = add_te(Xtr, Xva, CAT_COLS, ytr)' if cfg["use_te"] else '            pass  # no manual TE'
    te_test_code = '            _, Xte_fold = add_te(Xtr, Xte_fold, CAT_COLS, ytr)' if cfg["use_te"] else '            pass'

    script = SUBMISSION_TEMPLATE.format(
        cat_cols=cfg["cat_cols"],
        feature_code=cfg["feature_code"],
        model_params=cfg["model_params"],
        te_code=te_code,
        te_test_code=te_test_code,
        extra_fold_code=cfg.get("extra_fold_code", ""),
        extra_fold_apply=cfg.get("extra_fold_apply", ""),
    )
    return script


def run_submission(script_code, name):
    """Upload script to GPU, run, download submission.csv, submit to Kaggle."""
    tmp_name = f"sub_{hash(name) % 100000}.py"
    tmp_local = BASE_DIR / tmp_name

    tmp_local.write_text(script_code)
    try:
        # Kill orphans
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       "pkill -9 -f 'sub_' 2>/dev/null; true"],
                      capture_output=True, timeout=15)

        # Upload
        subprocess.run(["scp", "-o", "ConnectTimeout=10", str(tmp_local),
                       f"{GPU_HOST}:{GPU_WORKDIR}/{tmp_name}"],
                      capture_output=True, timeout=30, check=True)

        # Run
        cmd = (
            f"export CUDA_VISIBLE_DEVICES=0 && "
            f"source {GPU_VENV} && cd {GPU_WORKDIR} && "
            f"timeout --signal=KILL {TIME_BUDGET} python3 {tmp_name}"
        )

        start = time.time()
        proc = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=60",
             "-o", "ServerAliveCountMax=30", GPU_HOST, cmd],
            capture_output=True, text=True, timeout=TIME_BUDGET + 120)
        elapsed = time.time() - start

        if proc.returncode != 0:
            log(f"  ❌ {name}: exit={proc.returncode} ({elapsed:.0f}s)")
            log(f"    stderr: {proc.stderr[-300:]}")
            return None, elapsed

        # Parse CV AUC from output
        lines = proc.stdout.strip().split("\n")
        cv_auc = None
        for line in lines:
            try:
                d = json.loads(line)
                cv_auc = d.get("cv_auc")
            except:
                pass
        log(f"  ✅ {name}: CV={cv_auc:.6f} ({elapsed:.0f}s)")

        # Download submission
        local_sub = SUB_DIR / f"submission_{name}.csv"
        subprocess.run(
            ["scp", f"{GPU_HOST}:{GPU_WORKDIR}/submission.csv", str(local_sub)],
            capture_output=True, timeout=30, check=True)

        return cv_auc, elapsed

    except Exception as e:
        log(f"  ❌ {name}: {e}")
        return None, 0
    finally:
        tmp_local.unlink(missing_ok=True)
        subprocess.run(["ssh", "-o", "ConnectTimeout=5", GPU_HOST,
                       f"rm -f {GPU_WORKDIR}/{tmp_name} {GPU_WORKDIR}/submission.csv"],
                      capture_output=True, timeout=10)


def main():
    LOG_FILE.write_text("")
    log(f"\n{'='*60}")
    log(f"KAGGLE SUBMISSIONS — Top 10 Combos")
    log(f"{'='*60}\n")

    results = OrderedDict()

    for i, (name, cfg) in enumerate(configs.items(), 1):
        log(f"\n--- [{i}/{len(configs)}] {name} (search CV={cfg['cv_auc']:.6f}) ---")

        script = build_script(cfg)
        cv_auc, elapsed = run_submission(script, name)

        if cv_auc is not None:
            results[name] = {"cv_auc": cv_auc, "search_cv": cfg["cv_auc"], "elapsed": elapsed}

            # Submit to Kaggle
            local_sub = SUB_DIR / f"submission_{name}.csv"
            if local_sub.exists():
                desc = f"{name} CV={cv_auc:.6f}"
                log(f"  Submitting to Kaggle...")
                submit_to_kaggle(str(local_sub), desc)
                time.sleep(10)  # rate limit
        else:
            results[name] = {"cv_auc": None, "status": "failed", "elapsed": elapsed}

        # Save intermediate
        (BASE_DIR / "results" / "v2_from_best" / "submission_results.json").write_text(
            json.dumps(results, indent=2))

    # Summary
    log(f"\n{'='*60}")
    log(f"SUBMISSION SUMMARY")
    log(f"{'='*60}")
    for name, r in results.items():
        if r.get("cv_auc"):
            log(f"  {name}: CV={r['cv_auc']:.6f} (search={r['search_cv']:.6f})")
        else:
            log(f"  {name}: FAILED")
    log("DONE!")

if __name__ == "__main__":
    main()

# ===== FILE: v2_xgb_lr.py =====
"""
Train XGBoost and Logistic Regression on kitchen sink features.
Same pipeline: 5-fold CV, 3-seed ensemble, GPU 0.
"""
import json
import random
import warnings
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

SEED = 42
N_FOLDS = 5
TARGET_COL = "Churn"
ID_COL = "id"
BASE_DIR = Path("/home/yourslewis/autoresearch_kaggle")

CAT_COLS = [
    "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
    "PaperlessBilling", "PaymentMethod",
]

GROUP_COLS = ["Contract", "PaymentMethod", "InternetService"]
NUM_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]
SMOOTH = 20.0


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)


def add_features(df):
    """Kitchen sink features."""
    df = df.copy()
    df["avg_monthly_spend"] = df["TotalCharges"] / (df["tenure"] + 1)
    df["charge_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
    service_cols = ["PhoneService", "OnlineSecurity", "OnlineBackup",
                    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    df["num_services"] = sum((df[c] == "Yes").astype(int) for c in service_cols)
    df["tenure_x_monthly"] = df["tenure"] * df["MonthlyCharges"]
    return df


def add_target_encoding(tr, va, cols, ytr, smooth=SMOOTH):
    gm = float(np.mean(ytr))
    ys = pd.Series(ytr, index=tr.index)
    tr2, va2 = tr.copy(), va.copy()
    for c in cols:
        g = pd.DataFrame({c: tr[c].astype(str), "t": ys})
        st = g.groupby(c)["t"].agg(["mean", "count"])
        sm = ((st["count"] * st["mean"]) + (smooth * gm)) / (st["count"] + smooth)
        m = sm.to_dict()
        nc = f"{c}__te"
        tr2[nc] = tr[c].astype(str).map(m).fillna(gm).astype(np.float32)
        va2[nc] = va[c].astype(str).map(m).fillna(gm).astype(np.float32)
    return tr2, va2


def add_group_stats(tr, va, group_cols, num_cols):
    tr2, va2 = tr.copy(), va.copy()
    for g in group_cols:
        for n in num_cols:
            mean_map = tr.groupby(g)[n].mean().to_dict()
            tr2[f"gs_mean_{n}_by_{g}"] = tr[g].map(mean_map).astype(np.float32)
            va2[f"gs_mean_{n}_by_{g}"] = va[g].map(mean_map).astype(np.float32)
            tr2[f"gs_resid_{n}_by_{g}"] = (tr[n].astype(float) - tr[g].map(mean_map).astype(float)).astype(np.float32)
            va2[f"gs_resid_{n}_by_{g}"] = (va[n].astype(float) - va[g].map(mean_map).astype(float)).astype(np.float32)
            tr2[f"gs_ratio_{n}_by_{g}"] = (tr[n].astype(float) / (tr[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
            va2[f"gs_ratio_{n}_by_{g}"] = (va[n].astype(float) / (va[g].map(mean_map).astype(float) + 1e-6)).astype(np.float32)
    return tr2, va2


def encode_cats_numeric(tr, va, cat_cols):
    """Label encode categoricals for XGBoost/LR."""
    tr2, va2 = tr.copy(), va.copy()
    for c in cat_cols:
        cats = tr[c].astype(str).unique()
        mapping = {v: i for i, v in enumerate(sorted(cats))}
        tr2[c] = tr[c].astype(str).map(mapping).fillna(-1).astype(int)
        va2[c] = va[c].astype(str).map(mapping).fillna(-1).astype(int)
    return tr2, va2


def run_xgboost():
    """XGBoost with kitchen sink features."""
    import xgboost as xgb

    set_seed()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # TE + group stats (no manual TE for kitchen sink variant)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)
            Xtr, Xva = encode_cats_numeric(Xtr, Xva, CAT_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]

            model = xgb.XGBClassifier(
                n_estimators=5000,
                learning_rate=0.03,
                max_depth=6,
                reg_lambda=8.0,
                subsample=0.8,
                colsample_bytree=0.8,
                min_child_weight=5,
                objective="binary:logistic",
                eval_metric="auc",
                tree_method="hist",
                device="cuda",
                random_state=seed,
                verbosity=0,
                early_stopping_rounds=100,
            )
            model.fit(Xtr[fc], ytr, eval_set=[(Xva[fc], yva)], verbose=False)
            oof[vidx] = model.predict_proba(Xva[fc])[:, 1]
            fold_auc = roc_auc_score(yva, oof[vidx])
            print(f"[XGB] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        all_oof[si] = oof
        print(f"[XGB] Seed {seed} AUC={roc_auc_score(y, oof):.6f}", flush=True)

    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    return auc


def run_logistic_regression():
    """Logistic Regression with kitchen sink features."""
    set_seed()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    seeds = [42, 52, 62]
    all_oof = np.zeros((len(seeds), len(X)))

    for si, seed in enumerate(seeds):
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(len(X))

        for fi, (tidx, vidx) in enumerate(skf.split(X, y), 1):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]

            # TE + group stats
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)
            Xtr, Xva = encode_cats_numeric(Xtr, Xva, CAT_COLS)

            fc = [c for c in Xtr.columns if c != ID_COL]

            # Scale features for LR
            scaler = StandardScaler()
            Xtr_scaled = scaler.fit_transform(Xtr[fc].fillna(0))
            Xva_scaled = scaler.transform(Xva[fc].fillna(0))

            model = LogisticRegression(
                C=1.0,
                max_iter=1000,
                solver="lbfgs",
                random_state=seed,
                n_jobs=-1,
            )
            model.fit(Xtr_scaled, ytr)
            oof[vidx] = model.predict_proba(Xva_scaled)[:, 1]
            fold_auc = roc_auc_score(yva, oof[vidx])
            print(f"[LR] Seed {seed} Fold {fi}/{N_FOLDS} AUC={fold_auc:.6f}", flush=True)

        all_oof[si] = oof
        print(f"[LR] Seed {seed} AUC={roc_auc_score(y, oof):.6f}", flush=True)

    ensemble_oof = all_oof.mean(axis=0)
    auc = float(roc_auc_score(y, ensemble_oof))
    return auc


def run_lr_tuned():
    """LR with different C values."""
    set_seed()
    train_df = pd.read_csv(BASE_DIR / "train.csv")
    y = (train_df[TARGET_COL] == "Yes").astype(np.int64).to_numpy()
    X = add_features(train_df.drop(columns=[TARGET_COL]))

    best_auc = 0
    best_c = 1.0
    for C in [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]:
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
        oof = np.zeros(len(X))
        for fi, (tidx, vidx) in enumerate(skf.split(X, y)):
            Xtr, Xva = X.iloc[tidx], X.iloc[vidx]
            ytr, yva = y[tidx], y[vidx]
            Xtr, Xva = add_target_encoding(Xtr, Xva, CAT_COLS, ytr)
            Xtr, Xva = add_group_stats(Xtr, Xva, GROUP_COLS, NUM_COLS)
            Xtr, Xva = encode_cats_numeric(Xtr, Xva, CAT_COLS)
            fc = [c for c in Xtr.columns if c != ID_COL]
            scaler = StandardScaler()
            Xtr_s = scaler.fit_transform(Xtr[fc].fillna(0))
            Xva_s = scaler.transform(Xva[fc].fillna(0))
            model = LogisticRegression(C=C, max_iter=1000, solver="lbfgs", random_state=42)
            model.fit(Xtr_s, ytr)
            oof[vidx] = model.predict_proba(Xva_s)[:, 1]
        auc = roc_auc_score(y, oof)
        print(f"[LR_TUNE] C={C}: AUC={auc:.6f}", flush=True)
        if auc > best_auc:
            best_auc = auc
            best_c = C

    print(f"[LR_TUNE] Best C={best_c}, AUC={best_auc:.6f}", flush=True)
    return best_auc, best_c


if __name__ == "__main__":
    import sys
    model_type = sys.argv[1] if len(sys.argv) > 1 else "all"

    results = {}

    if model_type in ("xgb", "all"):
        print("\n=== XGBoost ===", flush=True)
        t0 = time.time()
        xgb_auc = run_xgboost()
        results["xgboost"] = {"auc": xgb_auc, "elapsed": time.time() - t0}
        print(f"\n[XGB FINAL] AUC={xgb_auc:.6f}", flush=True)

    if model_type in ("lr", "all"):
        print("\n=== Logistic Regression ===", flush=True)
        t0 = time.time()
        lr_auc = run_logistic_regression()
        results["logistic_regression"] = {"auc": lr_auc, "elapsed": time.time() - t0}
        print(f"\n[LR FINAL] AUC={lr_auc:.6f}", flush=True)

    if model_type in ("lr_tune", "all"):
        print("\n=== LR Tuning ===", flush=True)
        t0 = time.time()
        lr_best_auc, lr_best_c = run_lr_tuned()
        results["lr_tuned"] = {"auc": lr_best_auc, "best_C": lr_best_c, "elapsed": time.time() - t0}

    print(json.dumps(results))

