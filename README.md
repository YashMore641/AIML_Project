# PhishGuard — Phishing Email Detection

A small Flask web app that trains a TF-IDF and Logistic Regression text classifier from `CEAS_08_first20.csv`. It shows the dataset's labeled emails and lets you submit an email subject and body for a prediction.

## Run locally

1. Open a terminal in this project folder.
2. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install the dependencies and start the app:
   ```powershell
   pip install -r requirements.txt
   python app.py
   ```
4. Open <http://127.0.0.1:5000>.

The model trains from the CSV when the app starts. For this demo, dataset label `1` is displayed as **Phishing** and label `0` as **Not phishing**; verify that this mapping matches the source dataset before relying on it. Because the supplied file contains only 20 examples, predictions are for demonstration only and should not be used to make security decisions.
