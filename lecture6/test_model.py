#!/usr/bin/env python3
"""
Lecture 6 - Mid-Semester Assignment: Model Testing Script

Tests the trained gold price prediction model.
Usage:
  python test_model.py --model models/gold_model.pkl --data data/
  python test_model.py --model /data/gold_war_pipeline/models/gold_model.pkl
"""

import argparse
import pickle
from pathlib import Path

import pandas as pd


def load_model(model_path: Path):
    """Load the saved model and feature names."""
    with open(model_path, "rb") as f:
        data = pickle.load(f)
    return data["model"], data["features"]


def test_model(model_path: Path, data_dir: Path) -> dict:
    """
    Run model tests: load model, load training data, compute accuracy.
    Returns dict with accuracy and sample predictions.
    """
    model, features = load_model(model_path)

    training_csv = data_dir / "training_data.csv"
    if not training_csv.exists():
        raise FileNotFoundError(
            f"Training data not found: {training_csv}. Run ETL first."
        )

    df = pd.read_csv(training_csv)
    X = df[features].fillna(0)
    y = df["target"]

    accuracy = model.score(X, y)
    preds = model.predict(X)
    sample = df[["date", "close", "target"]].head(10).copy()
    sample["predicted"] = preds[:10]

    return {
        "accuracy": accuracy,
        "n_samples": len(df),
        "sample_predictions": sample,
    }


def main():
    parser = argparse.ArgumentParser(description="Test gold price prediction model")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("models/gold_model.pkl"),
        help="Path to saved model .pkl",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("/data/gold_war_pipeline"),
        help="Data directory containing training_data.csv",
    )
    args = parser.parse_args()

    if not args.model.exists():
        print(f"ERROR: Model not found: {args.model}")
        print("Run the ETL pipeline first to train and save the model.")
        return 1

    result = test_model(args.model, args.data)
    print(f"\n=== Model Test Results ===")
    print(f"Accuracy: {result['accuracy']:.3f}")
    print(f"Samples:  {result['n_samples']}")
    print(f"\nSample predictions (first 10):")
    print(result["sample_predictions"].to_string(index=False))
    return 0


if __name__ == "__main__":
    exit(main())
