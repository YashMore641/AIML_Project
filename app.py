import csv
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "CEAS_08_first20.csv"


def load_dataset(path=DATASET_PATH):
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    required_columns = {"subject", "body", "label"}
    if not rows or not required_columns.issubset(rows[0]):
        raise ValueError(
            "Dataset must contain at least one email and the columns "
            "'subject', 'body', and 'label'."
        )

    dataset = []
    for row in rows:
        try:
            label = int(row["label"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid label in dataset row: {row.get('label')!r}") from error
        if label not in (0, 1):
            raise ValueError(f"Expected a binary label (0 or 1), got {label}.")

        subject = (row.get("subject") or "").strip()
        body = (row.get("body") or "").strip()
        dataset.append(
            {
                "sender": (row.get("sender") or "").strip(),
                "subject": subject,
                "body": body,
                "label": label,
                "text": f"{subject} {body}".strip(),
            }
        )

    if len({email["label"] for email in dataset}) < 2:
        raise ValueError("The dataset must include examples from both label classes.")
    return dataset


def train_classifier(dataset):
    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    max_features=5000,
                    sublinear_tf=True,
                    stop_words="english",
                ),
            ),
            (
                "classifier",
                LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42),
            ),
        ]
    )
    model.fit([email["text"] for email in dataset], [email["label"] for email in dataset])
    return model


emails = load_dataset()
classifier = train_classifier(emails)

app = Flask(__name__)


@app.get("/")
def home():
    phishing_count = sum(email["label"] == 1 for email in emails)
    return render_template(
        "index.html",
        emails=emails,
        total_count=len(emails),
        phishing_count=phishing_count,
        legitimate_count=len(emails) - phishing_count,
    )


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Please submit the subject and email body."), 400

    subject = payload.get("subject", "")
    body = payload.get("body", "")
    if not isinstance(subject, str) or not isinstance(body, str):
        return jsonify(error="Subject and body must be text."), 400

    subject = subject.strip()
    body = body.strip()
    if not subject and not body:
        return jsonify(error="Enter a subject or email body to analyze."), 400

    probabilities = classifier.predict_proba([f"{subject} {body}".strip()])[0]
    predicted_label = int(classifier.predict([f"{subject} {body}".strip()])[0])
    confidence = float(probabilities[list(classifier.classes_).index(predicted_label)])
    return jsonify(
        label=predicted_label,
        verdict="Phishing" if predicted_label == 1 else "Not phishing",
        confidence=round(confidence * 100, 1),
    )


if __name__ == "__main__":
    app.run(debug=False)
