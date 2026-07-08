import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import time
from collections import deque

class RealTimeFraudDetector:
    def __init__(self, contamination=0.05):
        # Isolation Forest is unsupervised and works well for high-dimensional anomaly detection
        self.model = IsolationForest(contamination=contamination, random_state=42)
        # In-memory sliding window queue to track transaction velocity for each user
        self.transaction_history = {}
        self.is_trained = False
        
    def fit_baseline_model(self, baseline_data):
        """
        Trains the model offline using historical data.
        baseline_data: DataFrame with features ['amount', 'velocity_5m', 'location_shift']
        """
        self.model.fit(baseline_data)
        self.is_trained = True
        print("[System] Offline model training completed successfully.")

    def update_user_history(self, user_id, amount, timestamp):
        """
        Updates sliding window state and calculates real-time features.
        """
        if user_id not in self.transaction_history:
            self.transaction_history[user_id] = deque(maxlen=10) # Keep last 10 txs
        
        user_queue = self.transaction_history[user_id]
        
        # Calculate velocity feature (transactions in last 5 minutes)
        five_min_ago = timestamp - 300
        user_queue.append((timestamp, amount))
        
        recent_txs = [tx for tx in user_queue if tx[0] > five_min_ago]
        velocity_5m = len(recent_txs)
        
        return velocity_5m

    def score_transaction(self, transaction):
        """
        Evaluates a single incoming transaction in real-time.
        transaction: dict with keys ['user_id', 'amount', 'timestamp', 'location_shift']
        """
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
            
        user_id = transaction['user_id']
        amount = transaction['amount']
        ts = transaction['timestamp']
        loc_shift = transaction['location_shift']
        
        # Compute dynamic feature
        velocity_5m = self.update_user_history(user_id, amount, ts)
        
        # Prepare feature vector: shape (1, 3)
        feature_vector = np.array([[amount, velocity_5m, loc_shift]])
        
        # Inference: 1 = Normal, -1 = Anomaly
        prediction = self.model.predict(feature_vector)[0]
        anomaly_score = self.model.decision_function(feature_vector)[0]
        
        is_fraud = prediction == -1
        return is_fraud, anomaly_score

# --- Execution Setup ---
if __name__ == "__main__":
    # 1. Generate synthetic baseline data to train the detector
    np.random.seed(42)
    normal_amounts = np.random.normal(loc=50, scale=20, size=500)
    normal_velocities = np.random.poisson(lam=1, size=500)
    normal_shifts = np.random.uniform(0, 5, size=500)
    
    historical_df = pd.DataFrame({
        'amount': normal_amounts,
        'velocity_5m': normal_velocities,
        'location_shift': normal_shifts
    })
    
    detector = RealTimeFraudDetector(contamination=0.02)
    detector.fit_baseline_model(historical_df)
    
    # 2. Simulate streaming transactions
    stream = [
        {'user_id': 'USR_101', 'amount': 45.0, 'timestamp': time.time(), 'location_shift': 0.1},
        {'user_id': 'USR_101', 'amount': 52.5, 'timestamp': time.time() + 10, 'location_shift': 0.2},
        # USR_101 exhibits high velocity (rapid transaction requests in seconds)
        {'user_id': 'USR_101', 'amount': 30.0, 'timestamp': time.time() + 20, 'location_shift': 0.1},
        {'user_id': 'USR_101', 'amount': 25.0, 'timestamp': time.time() + 25, 'location_shift': 0.1},
        # USR_102 shows high location shift (impossible physical travel distance) and large amount
        {'user_id': 'USR_102', 'amount': 2500.0, 'timestamp': time.time(), 'location_shift': 95.0}
    ]
    
    print("\n--- Processing Live Transaction Stream ---")
    for i, tx in enumerate(stream):
        is_fraud, score = detector.score_transaction(tx)
        status = "ALERT: FRAUD DETECTED" if is_fraud else "APPROVED"
        print(f"Tx {i+1} | User: {tx['user_id']} | Amount: ${tx['amount']:.2f} | Status: {status} (Score: {score:.4f})")