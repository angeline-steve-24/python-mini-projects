import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import time
from collections import deque


class RealTimeFraudDetector:
    def __init__(self, contamination=0.05):
        # Isolation Forest for anomaly detection
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42
        )

        # Store recent transactions for each user
        self.transaction_history = {}

        self.is_trained = False

    def fit_baseline_model(self, baseline_data):
        """
        Train the Isolation Forest model using historical data.

        baseline_data:
        DataFrame containing:
        - amount
        - velocity_5m
        - location_shift
        """

        self.model.fit(baseline_data)
        self.is_trained = True

        print("[System] Offline model training completed successfully.")

    def update_user_history(self, user_id, amount, timestamp):
        """
        Update user's recent transaction history and
        calculate transaction velocity.
        """

        if user_id not in self.transaction_history:
            self.transaction_history[user_id] = deque(maxlen=10)

        user_queue = self.transaction_history[user_id]

        five_min_ago = timestamp - 300

        user_queue.append((timestamp, amount))

        recent_transactions = [
            tx for tx in user_queue
            if tx[0] > five_min_ago
        ]

        velocity_5m = len(recent_transactions)

        return velocity_5m

    def score_transaction(self, transaction):
        """
        Evaluate an incoming transaction.

        transaction dictionary:
        {
            user_id,
            amount,
            timestamp,
            location_shift
        }
        """

        if not self.is_trained:
            raise ValueError("Model is not trained yet.")

        user_id = transaction["user_id"]
        amount = transaction["amount"]
        timestamp = transaction["timestamp"]
        location_shift = transaction["location_shift"]

        # Calculate transaction velocity
        velocity_5m = self.update_user_history(
            user_id,
            amount,
            timestamp
        )

        # Create DataFrame with feature names
        feature_vector = pd.DataFrame({
            "amount": [amount],
            "velocity_5m": [velocity_5m],
            "location_shift": [location_shift]
        })

        # Predict anomaly
        prediction = self.model.predict(feature_vector)[0]
        anomaly_score = self.model.decision_function(feature_vector)[0]

        is_fraud = prediction == -1

        return is_fraud, anomaly_score


# ----------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------

if __name__ == "__main__":

    np.random.seed(42)

    # Generate synthetic historical data

    normal_amounts = np.random.normal(
        loc=50,
        scale=20,
        size=500
    )

    normal_velocities = np.random.poisson(
        lam=1,
        size=500
    )

    normal_location_shift = np.random.uniform(
        0,
        5,
        size=500
    )

    historical_df = pd.DataFrame({
        "amount": normal_amounts,
        "velocity_5m": normal_velocities,
        "location_shift": normal_location_shift
    })

    detector = RealTimeFraudDetector(contamination=0.02)

    detector.fit_baseline_model(historical_df)

    # Simulated live transactions

    current_time = time.time()

    stream = [

        {
            "user_id": "USR_101",
            "amount": 45.0,
            "timestamp": current_time,
            "location_shift": 0.1
        },

        {
            "user_id": "USR_101",
            "amount": 52.5,
            "timestamp": current_time + 10,
            "location_shift": 0.2
        },

        {
            "user_id": "USR_101",
            "amount": 30.0,
            "timestamp": current_time + 20,
            "location_shift": 0.1
        },

        {
            "user_id": "USR_101",
            "amount": 25.0,
            "timestamp": current_time + 25,
            "location_shift": 0.1
        },

        {
            "user_id": "USR_102",
            "amount": 2500.0,
            "timestamp": current_time,
            "location_shift": 95.0
        }

    ]

    print("\n--- Processing Live Transaction Stream ---")

    for i, transaction in enumerate(stream, start=1):

        fraud, score = detector.score_transaction(transaction)

        status = (
            "ALERT: FRAUD DETECTED"
            if fraud
            else "APPROVED"
        )

        print(
            f"Tx {i} | "
            f"User: {transaction['user_id']} | "
            f"Amount: ${transaction['amount']:.2f} | "
            f"Status: {status} "
            f"(Score: {score:.4f})"
        )