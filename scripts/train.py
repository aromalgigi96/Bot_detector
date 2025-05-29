#!/usr/bin/env python
import argparse, glob, os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from lightgbm import LGBMClassifier

def load_data(parquet_dir: str) -> pd.DataFrame:
    paths = glob.glob(os.path.join(parquet_dir, "*.parquet"))
    dfs = [pd.read_parquet(p) for p in paths]
    return pd.concat(dfs, ignore_index=True)

def main():
    p = argparse.ArgumentParser(description="Train bot-vs-benign classifier")
    p.add_argument("--input-dir",  type=str, required=True, help="Folder with processed Parquets")
    p.add_argument("--model-out",  type=str, default="app/models/classifier.pkl", help="Where to save the model")
    args = p.parse_args()

    print("🔍 Loading data from", args.input_dir)
    df = load_data(args.input_dir)
    print(f"✔️ Loaded {len(df):,} rows")

    # Assume your Parquet has a 'Label' column with 'Bot' vs 'Benign'
    y = (df["Label"] == "Bot").astype(int)
    X = df.drop(columns=["Label"])

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("🏋️ Training LightGBM classifier…")
    model = LGBMClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    print("📊 Evaluating on test set…")
    preds = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    print(f"➡️ Test ROC-AUC: {auc:.4f}")

    # Serialize (None, model) so scorer can load it
    os.makedirs(os.path.dirname(args.model_out), exist_ok=True)
    joblib.dump((None, model), args.model_out)
    print("💾 Saved model to", args.model_out)

if __name__ == "__main__":
    main()
