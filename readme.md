# 🏈 SWC Fantasy Football Analytics Platform

A comprehensive platform for fantasy football data analysis, visualization, and ML-powered predictions.

## 📱 Streamlit Application

Our interactive Streamlit application provides dynamic visualizations of fantasy football data:

![Team Rosters](/assets/first-page.png)
![TD Stats](/assets/second-page.png)
![Scoring Distribution](/assets/third-page.png)
![Points Race](/assets/fourth-page.png)
![Championship Map](/assets/fifth-page.png)
![Analysis View](/assets/sixth-page.png)

## 🔧 Key Components

### 🛠 Python SDK (`/sdk`)

**Professional-grade API client library** featuring:

- ✅ **Pydantic models** for strong data validation
- 🔁 **Exponential backoff** with retry handling 
- 🪵 **Integrated logging** for simplified debugging

📂 Folder: [`/sdk`](./sdk)

### 📊 Data APIs

**RESTful services for data access and analysis:**

- 🌐 **[Server API](https://swc-s-fantasy-football-api-service.onrender.com/docs)** - Core fantasy football data
- 🧠 **[ML Model API](https://swc-fantasy-football.onrender.com/docs)** - Predictive analytics endpoints

![Server API](/assets/api.png)
![ML Model API](/assets/deployed-ml-api.png)

### 📦 Machine Learning Model (`/ml_model`)

**Production-ready ML deployment** with:

- ⚙️ **ONNX Runtime** for optimized inference
- 🌐 **FastAPI** endpoints for model serving
- 🧪 Complete pre/post-processing pipeline

📂 Folder: [`/ml_model`](./ml_model)

### 🤖 AI Agent (`/ai_agent`)

**Advanced AI-powered assistant** built with:

- 🧠 **LangGraph** for sophisticated reasoning workflows
- ✨ **Gemini API** for natural language understanding
- 📓 **Jupyter Notebooks** demonstrating capabilities

📂 Folder: [`/ai_agent`](./ai_agent)

## 📊 Sample Analysis

```python
import pandas as pd
import logging
import swc_simple_client as swc

# Configure logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='shark_notebook.log', level=logging.INFO)

# API connection (local or remote)
base_url = "http://127.0.0.1:8000"  # Local development
# base_url = "https://swc-s-fantasy-football-api-service.onrender.com"  # Production

# Fetch and analyze weekly data
week_api_response = swc.call_api_endpoint(base_url, swc.LIST_WEEKS_ENDPOINT)
weeks_df = pd.DataFrame(week_api_response.json())
weeks_df['year'] = weeks_df['week_number'].str.slice(0, 4).astype(int)
weeks_df['week'] = weeks_df['week_number'].str.slice(4, 6).astype(int)

# Filter to regular season
weeks_df = weeks_df.query('week <= 14')

# Aggregate yearly point totals
max_totals_grouped_df = weeks_df.groupby('year').agg(
    ppr_12_max_points=('ppr_12_max_points', 'sum'), 
    half_ppr_8_max_points=('half_ppr_8_max_points', 'sum'))

display(max_totals_grouped_df)

```

📁 Data Sources

1. API-based data for real-time team and player statistics
2. CSV historical data for long-term trends and championship visualizations

🚀 Getting Started
1. Clone the repository
2. Install dependencies: uv venv env && source env/bin/activate
3. Install dependencies: uv pip install -r requirements.txt
4. Run the Streamlit app: streamlit run streamlit_football_app.py
5. Explore fantasy football insights through interactive visualizations!