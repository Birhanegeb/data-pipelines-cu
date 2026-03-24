# =============================================================================
# test_model.py
# Load the trained gold prediction model and report its accuracy.
#
# Usage:
#   python test_model.py \
#       --model /data/gold_war_pipeline/models/gold_model.pkl \
#       --data  /data/gold_war_pipeline
# =============================================================================

import argparse
import os
import sys
import joblib
import pandas as pd # type: ignore
from sklearn.metrics import accuracy_score, classification_report
# Features the model was trained on – must match gold_war_etl_dag.py
FEATURE_COLUMNS = ["close", "sentiment_mean", "news_count"]
def load_model(model_path: str):
    """
    Load the trained model from a .pkl file.
    Exits with a clear error message if the file is missing or corrupted.
    """
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: '{model_path}'")
        print("   Have you run the Airflow pipeline at least once?")
        sys.exit(1)

    try:
        model = joblib.load(model_path)
        print(f"✅ Model loaded from: {model_path}")
        return model

    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        sys.exit(1)


def load_data(data_dir: str) -> pd.DataFrame:
    """
    Load training_data.csv from the data directory.
    Exits with a clear error message if the file is missing or unreadable.
    """
    csv_path = os.path.join(data_dir, "training_data.csv")

    if not os.path.exists(csv_path):
        print(f"❌ Data file not found: '{csv_path}'")
        print("   Have you run the full Airflow pipeline?")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Data loaded: {len(df)} rows from '{csv_path}'")
        return df

    except Exception as e:
        print(f"❌ Failed to read data file: {e}")
        sys.exit(1)


def validate_columns(df: pd.DataFrame):
    """
    Check that all required feature columns exist in the DataFrame.
    Exits if any columns are missing.
    """
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]

    if missing:
        print(f"❌ Missing columns in training_data.csv: {missing}")
        print(f"   Expected columns: {FEATURE_COLUMNS}")
        sys.exit(1)

    if "target" not in df.columns:
        print("❌ Column 'target' not found in training_data.csv")
        sys.exit(1)


def evaluate(model, df: pd.DataFrame):
    """
    Run predictions and print accuracy + classification report.
    """
    X = df[FEATURE_COLUMNS]
    y = df["target"]

    try:
        predictions = model.predict(X)
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        sys.exit(1)

    accuracy = accuracy_score(y, predictions)

    print()
    print("=" * 50)
    print("         MODEL EVALUATION RESULTS")
    print("=" * 50)
    print(f"  Rows evaluated : {len(df)}")
    print(f"  Features used  : {FEATURE_COLUMNS}")
    print(f"  Accuracy       : {accuracy:.4f}  ({accuracy * 100:.1f}%)")
    print("=" * 50)
    print()
    print(classification_report(
        y, predictions,
        target_names=["Down (0)", "Up (1)"]
    ))

    # Give the student a plain-language interpretation
    if accuracy >= 0.60:
        print("✅ Good accuracy for a financial prediction model.")
    elif accuracy >= 0.50:
        print("⚠️  Accuracy is above 50% but there is room to improve.")
        print("   Tip: try adding lagged prices or moving average features.")
    else:
        print("❌ Accuracy is below 50% – worse than random guessing.")
        print("   Tip: check that shuffle=False was used in train/test split.")


def main():
    parser = argparse.ArgumentParser(
        description="Test the trained gold price prediction model"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Path to the trained model file (e.g. gold_model.pkl)",
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Directory containing training_data.csv",
    )
    args = parser.parse_args()

    # Step 1: load model
    model = load_model(args.model)

    # Step 2: load data
    df = load_data(args.data)

    # Step 3: check columns
    validate_columns(df)

    # Step 4: evaluate and print results
    evaluate(model, df)


if __name__ == "__main__":
    main()
