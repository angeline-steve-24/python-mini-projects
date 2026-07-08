# Academic Assignment: Data Science and Analytics

This repository contains implementation code, conceptual architectures, and descriptive analyses for three distinct engineering and statistical problems.

---

## Question 1: Global Banking System Data Infrastructure & Real-Time Fraud Detection Framework

### Theoretical Appraisal
Global banking networks process millions of events per second across multiple endpoints. Relational data warehouse structures, which rely on nocturnal batch ETL loads, are vulnerable to latency gaps, allowing card cloning or systemic fraud to persist unnoticed. 

#### Suggested Architecture: Hybrid Lakehouse & Streaming
* **Real-time processing (Kappa Pattern):** Log messages are ingested via **Apache Kafka** and streamed directly to a processing layer (**Apache Flink**).
* **Distributed Feature Store:** Flink updates and queries rolling customer metrics (e.g., number of locations visited in 15 minutes) inside a stateful cache like **Redis** (managed by **Feast**).
* **Low-latency ML Inference:** A pre-trained model (e.g., **Isolation Forest**) evaluates transaction vectors in $<50\text{ ms}$.
* **Compliance Archival:** The raw transactional logs are written to an open table format (e.g., **Apache Iceberg**) for batch analytics and model retraining.

### Python Code
The implementation is in `q1_fraud_detection.py`. It constructs an Isolation Forest baseline, processes user events with rolling temporal features, and flags anomalies.

---

## Question 2: Strategy for Data Preparation & EDA of a Smart-City IoT Dataset

### Processing Strategy
Physical IoT deployments introduce high volatility (missing reports, hardware failures, variable network delays). A structured cleaning framework consists of:

1. **Grid Resampling:** Aligning irregular, asynchronous timestamps to fixed bins (e.g., 5-minute bins).
2. **Outlier Filtering (Median Absolute Deviation):** Standard Z-score methods rely on the mean, which can be distorted by extreme outliers. We compute:
   $$\text{MAD} = \text{median}(|X_i - \text{median}(X)|)$$
   and mask values where $|X_i - \text{median}(X)| / (1.4826 \times \text{MAD}) > \text{Threshold}$.
3. **Data Imputation:** Linear interpolation is applied to small, contiguous missing blocks. For prolonged gaps, temporal/seasonal interpolation is used.

### Python Code
The implementation is in `q2_iot_cleaning.py`. It generates a noisy, irregular time series, aligns it to a uniform grid, filters out anomalies using rolling MAD, and imputes missing indices.

---

## Question 3: Critique of Statistical Descriptions for Skewed Income Data

### Critique of Classical Statistics
Applying standard parametric statistics to highly right-skewed data distributions (such as income, which typically follows a Pareto distribution) introduces significant distortions:

1. **Mean Distortion:** The arithmetic mean is heavily influenced by high-income outliers, misrepresenting the average citizen's financial reality.
2. **Standard Deviation Failure:** SD assumes symmetric bounds. In highly skewed distributions, calculation of intervals like $\mu \pm 2\sigma$ can result in impossible negative values at the lower bound.

### Recommended Alternative Framework
1. **Median ($Q_2$):** Measures central tendency robustly.
2. **IQR ($Q_3 - Q_1$):** Measures dispersion without being affected by extreme outliers.
3. **Gini Index:** Standard mathematical model for overall wealth inequality.
4. **Palma Ratio:** Focuses on the structural ratio of the top 10% income share divided by the bottom 40% income share.

### Python Code
The implementation is in `q3_income_critique.py`. It compares classical statistics against the robust framework on a simulated Pareto-distributed income population.
