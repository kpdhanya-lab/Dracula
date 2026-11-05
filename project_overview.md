# 🌊 BasinShift: FloodCast Intelligence 
**AI-Powered Hydrological Flood Forecasting Command Center**

## 📖 1. Project Abstract
BasinShift (FloodCast) is an end-to-end hydrological machine learning pipeline and interactive command center designed to predict river discharge and provide early warnings for extreme flood events. 

*Explain it like I'm 5:* We built a smart AI brain that reads weather diaries (rainfall, soil moisture) to guess how high a river will rise. Because massive floods are tricky, we taught it a special math trick so it respects huge waves just as much as calm streams. Finally, we put this brain into an interactive chat-dashboard so emergency workers can ask it questions and see the predictions on a chart!

## 💾 2. Data Engineering & Governance (Google Colab)
To handle the massive scale of the data without exhausting Google Colab's RAM, we implemented a highly optimized, memory-efficient data pipeline.

### Datasets Used
*   **Primary:** Caravan Dataset (Jan 25 CSV Release - CAMELS & LamaH subsets) encompassing meteorological forcing and static attributes for over 3,428+ basins.
*   **Secondary/Context:** Copernicus GloFAS, CEMS, and NASA POWER.

### Data Processing Rules
*   **Memory Optimization:** Transitioned from Pandas to **Polars** for multi-threaded lazy loading. Downcasted float columns to `float32` and converted raw CSVs into highly compressed **Parquet** files.
*   **Missing Value Governance:** Strict rules enforced to *never* zero-fill missing discharge labels (which would distort low-flow baselines).
*   **Leakage Prevention:** Catchment-wise geographic splits applied *before* windowing (Train: 2056, Val: 685, Test: 687). Scalers and statistical features were fitted *strictly* on the training splits.

## 🧠 3. Feature Engineering & Target Transformation
Hydrological memory is critical. Rain does not instantly equal floods; soil saturation and river routing take time.
*   **Target Transformation:** Applied `log1p` (natural log) to the target streamflow. This compressed extreme flood outliers (500+ m³/s) and baseflows onto a manageable scale, stabilizing our error metrics.
*   **Temporal Lags:** Extracted `streamflow_lag_1`, `streamflow_lag_2`, and `streamflow_lag_7` to teach the model river routing dynamics.
*   **Antecedent Moisture Windows:** Engineered 7-day, 14-day, and 30-day rolling precipitation sums to capture long-term soil saturation, alongside 7-day rolling standard deviations to identify volatile storm bursts.

## 🤖 4. Model Architectures
We developed two competitive models in Colab, progressing from a fast baseline to a deep learning sequence model.

### Model A: Advanced LightGBM (Gradient Boosting)
*   **Objective:** Tuned L2 Regression with heavy regularization (`reg_alpha=0.1`, `reg_lambda=1.0`, `min_child_samples=40`) to prevent leaf nodes from overfitting to noise.
*   **Performance:** Achieved an outstanding validation RMSE of **0.8237** and MAE of **0.1547** on log-transformed data.

### Model B: PyTorch LSTM (Production Sequence Model)
*   **Streaming Data Loader:** Built `StreamingCaravanDataset` to generate 365-day sliding window sequence tensors on the fly, outputting over 500,000+ windows without crashing Colab RAM.
*   **Hardware Acceleration:** Utilized `torch.cuda.amp` (Automatic Mixed Precision) on Colab's T4 GPU for lightning-fast training.
*   **Loss Function:** Transitioned to **Huber Loss** to smoothly balance standard baseflow errors while robustly penalizing extreme flood outlier misses.

## 📊 5. Final Evaluation Metrics
Evaluated on the held-out geographic **Test Split** (unseen basins) using inverse-transformed (`expm1`) real-world $m^3/s$ values:
*   **Test RMSE:** 2.49 m³/s 
*   **Test MAE:** 0.76 m³/s
*   *Conclusion:* The strategic use of `log1p` and Huber Loss successfully closed the initial 3x gap between RMSE and MAE, proving the model detects extreme flash floods accurately without throwing off daily baseflow predictions.

## 🖥️ 6. Decoupled UI & AI Chatbot Integration
To protect the ML backend, the user interface was decoupled from Colab and designed for local execution (e.g., via VS Code and Streamlit).

*   **Artifact Bridge:** Colab exports two lightweight files: the model weights (`flood_lstm_weights.pth`) and telemetry schemas (`sample_predictions.json`).
*   **Interactive Hydrographs:** Plotly-powered charts tracking multi-horizon predictions (1-day, 3-day, 7-day) alongside 90% confidence uncertainty intervals.
*   **Groq AI Copilot:** Embedded a conversational assistant powered by `llama-3.3-70b-versatile`. Grounded in our Colab metrics, it answers natural language queries about basin safety, model RMSE/MAE, and flood routing mechanics in real-time.