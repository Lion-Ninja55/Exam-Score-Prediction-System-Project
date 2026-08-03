import sys
import json
import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "outputs_project_1", "exam_score_model.joblib")

def predict(features):
    model = joblib.load(MODEL_PATH)
    df = pd.DataFrame([features])
    prediction = model.predict(df)[0]
    prediction = max(0.0, min(100.0, float(prediction)))
    return round(prediction, 2)

def main():
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"error": "No input provided"}))
        sys.exit(1)

    try:
        input_data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": "Invalid JSON: " + str(e)}))
        sys.exit(1)

    required = ["gender", "study_time_hours", "attendance_percent", "sleep_hours",
                "parental_education", "internet_access", "extracurricular_activities",
                "part_time_job", "previous_grade"]

    missing = [k for k in required if k not in input_data]
    if missing:
        print(json.dumps({"error": "Missing fields: " + ", ".join(missing)}))
        sys.exit(1)

    try:
        result = predict(input_data)
        print(json.dumps({"prediction": result}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()