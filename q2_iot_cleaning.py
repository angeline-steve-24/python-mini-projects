import numpy as np
import pandas as pd

def generate_messy_iot_data():
    """Generates a messy, synthetic IoT sensor dataset with missing values, noise, and spikes."""
    timestamps = pd.date_range(start="2026-07-01 00:00:00", periods=100, freq="2min")
    # Base temperature pattern with random fluctuations
    temp = 20.0 + 5.0 * np.sin(np.linspace(0, 3*np.pi, 100)) + np.random.normal(0, 0.5, 100)
    
    # Introduce Messiness:
    temp[15:20] = np.nan            # Data gap (missing observations)
    temp[45] = 99.9                 # Severe positive spike (sensor electrical failure)
    temp[75] = -50.0                # Severe negative spike (sensor baseline drop)
    
    df = pd.DataFrame({'timestamp': timestamps, 'raw_temp': temp})
    # Induce irregular timestamps (network transmission delays)
    df['timestamp'] = df['timestamp'] + pd.to_timedelta(np.random.randint(-45, 45, size=100), unit='s')
    return df

class IoTCleaningPipeline:
    def __init__(self, resample_freq="5min", mad_threshold=3.5):
        self.resample_freq = resample_freq
        self.mad_threshold = mad_threshold

    def clean_stream(self, df):
        """Executes alignment, outlier filtering, and interpolation on the input data."""
        # Ensure correct datetime index
        df = df.copy().set_index('timestamp').sort_index()
        
        # Step 1: Align irregular timestamps to a uniform grid
        resampled = df.resample(self.resample_freq).mean()
        
        # Step 2: Identify and mask outliers using Median Absolute Deviation (MAD)
        median = resampled['raw_temp'].median()
        mad = np.median(np.abs(resampled['raw_temp'] - median))
        
        # Guard against division by zero in zero-variance scenarios
        mad_scale = 1.4826 * mad if mad != 0 else 1e-6 
        z_scores = (resampled['raw_temp'] - median) / mad_scale
        
        # Flag outliers
        resampled['is_outlier'] = np.abs(z_scores) > self.mad_threshold
        resampled['clean_temp'] = resampled['raw_temp']
        resampled.loc[resampled['is_outlier'], 'clean_temp'] = np.nan
        
        # Step 3: Interpolate missing data points and remaining outlier gaps
        resampled['interpolated_temp'] = resampled['clean_temp'].interpolate(method='linear')
        
        # Step 4: Extract temporal features for downstream EDA
        resampled['hour'] = resampled.index.hour
        resampled['is_weekend'] = resampled.index.dayofweek >= 5
        
        return resampled

# --- Execution ---
if __name__ == "__main__":
    raw_data = generate_messy_iot_data()
    pipeline = IoTCleaningPipeline(resample_freq="5min", mad_threshold=3.0)
    cleaned_data = pipeline.clean_stream(raw_data)
    
    # Showcase segment containing missing entries and the extreme outlier (at index index 45 -> timestamp offset)
    print("--- Sample Raw Irregular IoT Data ---")
    print(raw_data.iloc[14:18])
    
    print("\n--- Cleaned, Uniformly Aligned and Imputed Grid ---")
    print(cleaned_data[['raw_temp', 'is_outlier', 'interpolated_temp']].iloc[5:10])
    
    print("\n--- Handled Severe Outliers ---")
    # Pull samples where raw data spiked but cleaned data was corrected
    outlier_timestamps = cleaned_data[cleaned_data['is_outlier']].index
    for ts in outlier_timestamps[:2]:
        surroundings = cleaned_data.loc[ts - pd.Timedelta('10m'): ts + pd.Timedelta('10m')]
        print(f"\nOutlier Event at {ts}:")
        print(surroundings[['raw_temp', 'is_outlier', 'interpolated_temp']])