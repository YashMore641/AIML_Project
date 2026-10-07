import unittest

import app


class PhishingAppTests(unittest.TestCase):
    def setUp(self):
        app.app.config.update(TESTING=True)
        self.client = app.app.test_client()

    def test_home_shows_dataset_and_label_counts(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dataset emails", response.data)
        self.assertIn(b"15", response.data)
        self.assertIn(b"5", response.data)

    def test_prediction_returns_a_binary_verdict(self):
        response = self.client.post(
            "/api/predict",
            json={"subject": "Free prize claim now", "body": "Click this link to claim your reward"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json["label"], (0, 1))
        self.assertIn(response.json["verdict"], ("Phishing", "Not phishing"))
        self.assertGreaterEqual(response.json["confidence"], 0)
        self.assertLessEqual(response.json["confidence"], 100)

    def test_prediction_rejects_empty_input(self):
        response = self.client.post("/api/predict", json={"subject": " ", "body": ""})

        self.assertEqual(response.status_code, 400)
        self.assertIn("Enter a subject or email body", response.json["error"])


if __name__ == "__main__":
    unittest.main()
