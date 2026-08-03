"""
============================================================================
PROJECT 1 : PREDICTING A STUDENT'S FINAL EXAM SCORE
Machine Learning Type : Supervised Learning -> Regression
============================================================================

WHAT THIS FILE DOES
-------------------
1. Loads the student performance dataset
2. Explores and explains the data
3. Cleans the data and prepares the features
4. Trains two regression models (Linear Regression + Random Forest)
5. Compares them using proper evaluation metrics
6. Shows which factors matter most for exam performance
7. Saves the best model so it can be reused later
8. Makes a prediction for one new student

HOW TO RUN
----------
Step 1 : Change DATA_PATH below to the location of your dataset file
Step 2 : Run this file

    python project_1_exam_score_regression.py

Nothing else needs to be changed.

REQUIREMENTS
------------
    pip install pandas numpy scikit-learn matplotlib joblib
============================================================================
"""

import os
import warnings

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

# Show every column when printing tables instead of hiding them behind "..."
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


# ===========================================================================
# SECTION 1 : CONFIGURATION
# The only line a student normally needs to change is DATA_PATH.
# ===========================================================================

CONFIG = {
    # ---- CHANGE THIS LINE ONLY ----
    "DATA_PATH": "C:\\Users\\5hari\\OneDrive\\Desktop\\ml_class_01\\student_performance_dataset.csv",

    # Column we want to predict (the answer / the target)
    "TARGET_COLUMN": "final_exam_score",

    # Columns that must never be used as inputs
    #   student_id  -> just a name tag, carries no real meaning
    #   final_grade -> it is calculated FROM final_exam_score (data leakage)
    "COLUMNS_TO_DROP": ["student_id", "final_grade"],

    # How much data is kept aside for testing (0.2 = 20 percent)
    "TEST_SIZE": 0.2,

    # Fixes randomness so results are the same every time we run
    "RANDOM_STATE": 42,

    # Where results are saved
    "OUTPUT_FOLDER": "outputs_project_1",

    # Set to False if you do not want charts
    "SAVE_CHARTS": True,
}


# ===========================================================================
# SECTION 2 : SMALL HELPER FUNCTIONS
# ===========================================================================

def print_heading(text):
    """Prints a clean section heading so the output is easy to read."""
    print("\n" + "=" * 76)
    print(text)
    print("=" * 76)


def load_dataset(path):
    """
    Reads the dataset from a file.

    sep=None with engine='python' lets pandas detect automatically whether the
    file is separated by commas, tabs or semicolons. This means the same code
    works for .csv and .tsv files without any change.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Dataset not found at: " + str(path) +
            "\nOpen this file, find CONFIG['DATA_PATH'] and set the correct path."
        )

    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)

    # IMPORTANT DETAIL
    # By default pandas treats the word "None" as an empty cell. In this
    # dataset "None" is a real answer for parental_education, so we tell
    # pandas exactly which words count as empty and leave "None" alone.
    return pd.read_csv(
        path,
        sep=None,
        engine="python",
        keep_default_na=False,
        na_values=["", " ", "NA", "N/A", "n/a", "NaN", "nan", "NULL", "null", "#N/A"],
    )


def build_preprocessor(numeric_columns, categorical_columns):
    """
    Builds the data preparation machine.

    Computers cannot learn from the word "Bachelors" or the word "Yes".
    Everything must become a number. This function does two jobs at once:

    NUMBERS  -> fill any missing value with the median, then scale the values
                so that a column measured in hours and a column measured in
                percent are treated fairly.

    WORDS    -> fill any missing value with the most common value, then apply
                One Hot Encoding, which turns one text column into several
                yes/no columns of 0 and 1.
    """
    numeric_pipeline = Pipeline(steps=[
        ("fill_missing", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])

    # Older and newer versions of scikit-learn use different argument names,
    # so we try the new one first and fall back to the old one.
    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)

    categorical_pipeline = Pipeline(steps=[
        ("fill_missing", SimpleImputer(strategy="most_frequent")),
        ("encode", encoder),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("numbers", numeric_pipeline, numeric_columns),
        ("words", categorical_pipeline, categorical_columns),
    ])

    return preprocessor


def evaluate_model(name, model, X_test, y_test):
    """Measures how good a trained model is on data it has never seen."""
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    print("\nModel: " + name)
    print("  MAE  (average error in marks)      : " + str(round(mae, 3)))
    print("  RMSE (punishes large mistakes)     : " + str(round(rmse, 3)))
    print("  R2   (0 = useless, 1 = perfect)    : " + str(round(r2, 4)))

    return {"name": name, "model": model, "mae": mae, "rmse": rmse, "r2": r2}


def get_feature_names(preprocessor, numeric_columns, categorical_columns):
    """Recovers readable column names after One Hot Encoding."""
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        return numeric_columns + categorical_columns


# ===========================================================================
# SECTION 3 : THE MAIN PROGRAM
# ===========================================================================

def main():

    os.makedirs(CONFIG["OUTPUT_FOLDER"], exist_ok=True)

    # -----------------------------------------------------------------------
    # STEP 1 : LOAD THE DATA
    # -----------------------------------------------------------------------
    print_heading("STEP 1 : LOADING THE DATASET")

    data = load_dataset(CONFIG["DATA_PATH"])

    print("Rows    : " + str(data.shape[0]))
    print("Columns : " + str(data.shape[1]))
    print("\nFirst 5 rows:")
    print(data.head())

    # -----------------------------------------------------------------------
    # STEP 2 : UNDERSTAND THE DATA
    # A good engineer always looks at the data before training anything.
    # -----------------------------------------------------------------------
    print_heading("STEP 2 : UNDERSTANDING THE DATASET")

    print("Column names and data types:")
    print(data.dtypes)

    print("\nMissing values per column:")
    missing = data.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "No missing values found.")

    print("\nDuplicate rows: " + str(data.duplicated().sum()))

    print("\nSummary of the numeric columns:")
    print(data.describe().round(2))

    target = CONFIG["TARGET_COLUMN"]
    if target not in data.columns:
        raise KeyError("Target column '" + target + "' is not in the dataset.")

    print("\nRelationship between each number column and " + target + ":")
    numeric_only = data.select_dtypes(include=[np.number])
    correlations = numeric_only.corr()[target].drop(target).sort_values(ascending=False)
    print(correlations.round(3))
    print("\nReading guide: a value close to +1 means the two rise together,")
    print("close to -1 means one rises while the other falls, and close to 0")
    print("means there is almost no straight line relationship.")

    # -----------------------------------------------------------------------
    # STEP 3 : CLEAN THE DATA
    # -----------------------------------------------------------------------
    print_heading("STEP 3 : CLEANING THE DATA")

    data = data.drop_duplicates()

    # Remove rows where the answer itself is missing. We cannot learn from a
    # question that has no answer.
    before = len(data)
    data = data.dropna(subset=[target])
    print("Rows removed because the target was empty: " + str(before - len(data)))

    columns_to_drop = [c for c in CONFIG["COLUMNS_TO_DROP"] if c in data.columns]
    print("Columns removed from the inputs: " + str(columns_to_drop))
    print("  student_id  -> an identity number, not a real cause of marks")
    print("  final_grade -> it is produced FROM the exam score, so using it")
    print("                 would be cheating. This mistake is called leakage.")

    y = data[target]
    X = data.drop(columns=columns_to_drop + [target])

    numeric_columns = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = X.select_dtypes(exclude=[np.number]).columns.tolist()

    print("\nNumber inputs : " + str(numeric_columns))
    print("Text inputs   : " + str(categorical_columns))

    # -----------------------------------------------------------------------
    # STEP 4 : SPLIT INTO TRAINING AND TESTING
    # -----------------------------------------------------------------------
    print_heading("STEP 4 : SPLITTING THE DATA")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=CONFIG["TEST_SIZE"],
        random_state=CONFIG["RANDOM_STATE"],
    )

    print("Training rows : " + str(len(X_train)) + "  (the model studies these)")
    print("Testing rows  : " + str(len(X_test)) + "  (the model is examined on these)")
    print("\nThe test rows are hidden from the model during training, exactly")
    print("like exam questions a student has never seen before.")

    # -----------------------------------------------------------------------
    # STEP 5 : TRAIN THE MODELS
    # -----------------------------------------------------------------------
    print_heading("STEP 5 : TRAINING THE MODELS")

    preprocessor = build_preprocessor(numeric_columns, categorical_columns)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            random_state=CONFIG["RANDOM_STATE"],
            n_jobs=-1,
        ),
    }

    results = []
    trained_pipelines = {}

    for name, algorithm in models.items():
        pipeline = Pipeline(steps=[
            ("prepare", preprocessor),
            ("model", algorithm),
        ])

        # Cross validation trains and tests 5 times on different slices of the
        # training data. It gives a much more honest picture than a single test.
        cv = KFold(n_splits=5, shuffle=True, random_state=CONFIG["RANDOM_STATE"])
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="r2")

        pipeline.fit(X_train, y_train)

        print("\nTrained: " + name)
        print("  Cross validation R2: " + str(round(cv_scores.mean(), 4)) +
              " (plus or minus " + str(round(cv_scores.std(), 4)) + ")")

        trained_pipelines[name] = pipeline
        results.append(evaluate_model(name, pipeline, X_test, y_test))

    # -----------------------------------------------------------------------
    # STEP 6 : COMPARE AND CHOOSE THE WINNER
    # -----------------------------------------------------------------------
    print_heading("STEP 6 : COMPARING THE MODELS")

    comparison = pd.DataFrame([
        {"Model": r["name"], "MAE": round(r["mae"], 3),
         "RMSE": round(r["rmse"], 3), "R2": round(r["r2"], 4)}
        for r in results
    ]).sort_values("R2", ascending=False)

    print(comparison.to_string(index=False))

    best = max(results, key=lambda r: r["r2"])
    print("\nBest model: " + best["name"])
    print("On average its prediction is about " + str(round(best["mae"], 2)) +
          " marks away from the real score.")

    # -----------------------------------------------------------------------
    # STEP 7 : WHICH FACTORS MATTER MOST
    # -----------------------------------------------------------------------
    print_heading("STEP 7 : WHAT INFLUENCES THE EXAM SCORE THE MOST")

    forest_pipeline = trained_pipelines.get("Random Forest Regressor")
    importance_table = None

    if forest_pipeline is not None:
        fitted_preprocessor = forest_pipeline.named_steps["prepare"]
        feature_names = get_feature_names(
            fitted_preprocessor, numeric_columns, categorical_columns
        )
        importances = forest_pipeline.named_steps["model"].feature_importances_

        importance_table = pd.DataFrame({
            "Feature": feature_names,
            "Importance": importances,
        }).sort_values("Importance", ascending=False).head(15)

        print(importance_table.to_string(index=False))
        print("\nHigher importance means the model relies on that column more")
        print("when deciding the final answer.")

    # -----------------------------------------------------------------------
    # STEP 8 : CHARTS
    # -----------------------------------------------------------------------
    if CONFIG["SAVE_CHARTS"]:
        print_heading("STEP 8 : SAVING CHARTS")
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            predictions = best["model"].predict(X_test)

            plt.figure(figsize=(7, 6))
            plt.scatter(y_test, predictions, alpha=0.6, edgecolor="none")
            low = float(min(y_test.min(), predictions.min()))
            high = float(max(y_test.max(), predictions.max()))
            plt.plot([low, high], [low, high], linestyle="--", linewidth=2)
            plt.xlabel("Real exam score")
            plt.ylabel("Predicted exam score")
            plt.title("Real vs Predicted  -  " + best["name"])
            plt.tight_layout()
            path_1 = os.path.join(CONFIG["OUTPUT_FOLDER"], "real_vs_predicted.png")
            plt.savefig(path_1, dpi=120)
            plt.close()
            print("Saved: " + path_1)
            print("  The closer the dots sit to the dashed line, the better.")

            if importance_table is not None:
                plt.figure(figsize=(9, 6))
                chart_data = importance_table.iloc[::-1]
                plt.barh(chart_data["Feature"], chart_data["Importance"])
                plt.xlabel("Importance")
                plt.title("Which factors drive the exam score")
                plt.tight_layout()
                path_2 = os.path.join(CONFIG["OUTPUT_FOLDER"], "feature_importance.png")
                plt.savefig(path_2, dpi=120)
                plt.close()
                print("Saved: " + path_2)

        except Exception as error:
            print("Charts were skipped. Reason: " + str(error))

    # -----------------------------------------------------------------------
    # STEP 9 : SAVE THE TRAINED MODEL
    # -----------------------------------------------------------------------
    print_heading("STEP 9 : SAVING THE TRAINED MODEL")

    try:
        import joblib
        model_path = os.path.join(CONFIG["OUTPUT_FOLDER"], "exam_score_model.joblib")
        joblib.dump(best["model"], model_path)
        print("Saved: " + model_path)
        print("Training is now finished forever. Any future program can load")
        print("this file and make predictions instantly without training again.")
    except Exception as error:
        print("Model could not be saved. Reason: " + str(error))

    comparison_path = os.path.join(CONFIG["OUTPUT_FOLDER"], "model_comparison.csv")
    comparison.to_csv(comparison_path, index=False)
    print("Saved: " + comparison_path)

    # -----------------------------------------------------------------------
    # STEP 10 : USE THE MODEL ON A NEW STUDENT
    # -----------------------------------------------------------------------
    print_heading("STEP 10 : PREDICTING FOR A NEW STUDENT")

    # We copy one real row and change the values. This guarantees that every
    # column the model expects is present and in the correct order.
    new_student = X_test.iloc[[0]].copy()

    example_values = {
        "gender": "Female",
        "study_time_hours": 5.0,
        "attendance_percent": 92.0,
        "sleep_hours": 7.5,
        "parental_education": "Bachelors",
        "internet_access": "Yes",
        "extracurricular_activities": "Yes",
        "part_time_job": "No",
        "previous_grade": 78.0,
    }

    for column, value in example_values.items():
        if column in new_student.columns:
            new_student.at[new_student.index[0], column] = value

    print("Student profile:")
    for column in new_student.columns:
        print("  " + column + " : " + str(new_student.iloc[0][column]))

    predicted_score = float(best["model"].predict(new_student)[0])
    predicted_score = max(0.0, min(100.0, predicted_score))

    print("\nPredicted final exam score: " + str(round(predicted_score, 2)))

    print_heading("PROJECT 1 COMPLETE")
    print("All results are inside the folder: " + CONFIG["OUTPUT_FOLDER"])


if __name__ == "__main__":
    main()