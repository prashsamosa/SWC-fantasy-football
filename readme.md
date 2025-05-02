# 🏆 SWC Fantasy Football Analytics Platform

> *Transform your fantasy football experience with data-driven insights, ML-powered predictions, and championship-winning strategies*

![Fantasy Football Banner](https://img.shields.io/badge/Fantasy-Football-brightgreen?style=for-the-badge) 
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python) 
![Streamlit](https://img.shields.io/badge/Streamlit-1.15+-red?style=flat-square&logo=streamlit) 
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green?style=flat-square&logo=fastapi)
![ML](https://img.shields.io/badge/ML-ONNX-yellow?style=flat-square&logo=onnx)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/swc-fantasy-football.git
cd swc-fantasy-football

# Set up environment with UV (faster than pip!)
uv venv env
source env/bin/activate      # On Windows: .\env\Scripts\activate
uv pip install -r requirements.txt

# Launch the Streamlit dashboard
streamlit run streamlit_football_app.py
```

## 🌟 Features

- **Interactive Analytics Dashboard**: Explore team performance, player statistics, and league trends
- **AI-Powered Predictions**: ML models for player acquisition values and weekly performance forecasts
- **Championship Visualization**: Visualize your path to victory with intuitive map displays
- **REST API Integration**: Professional-grade API for seamless data access
- **Player Acquisition Predictor**: Make smarter FAAB bids and roster decisions

## 📱 Interactive Dashboard

Our Streamlit application provides powerful visualizations to dominate your fantasy league:

<table>
  <tr>
    <td width="50%"><img src="/assets/first-page.png" alt="Team Rosters" style="width: 100%;"/></td>
    <td width="50%"><img src="/assets/second-page.png" alt="TD Stats" style="width: 100%;"/></td>
  </tr>
  <tr>
    <td><img src="/assets/third-page.png" alt="Scoring Distribution" style="width: 100%;"/></td>
    <td><img src="/assets/fourth-page.png" alt="Points Race" style="width: 100%;"/></td>
  </tr>
  <tr>
    <td><img src="/assets/fifth-page.png" alt="Championship Map" style="width: 100%;"/></td>
    <td><img src="/assets/sixth-page.png" alt="Analysis View" style="width: 100%;"/></td>
  </tr>
</table>

## 🔧 Architecture

The platform consists of four key components that work together to deliver comprehensive fantasy football insights:

### 🛠️ Python SDK (`/sdk`)

A professional-grade API client library that handles all communication with our data services.

**Key Features:**
- ✅ **Type-Safe Data Models**: Built with Pydantic for reliable data validation
- 🔁 **Resilient Connections**: Implements exponential backoff and retry mechanisms
- 🪵 **Comprehensive Logging**: Debug with ease using integrated logging

📂 [`/sdk`](./sdk)

### 📊 Dual API System

**Two specialized APIs working in harmony:**

<table>
  <tr>
    <td width="50%">
      <h4>🌐 Server API</h4>
      <a href="https://swc-s-fantasy-football-api-service.onrender.com/docs">
        <img src="/assets/api.png" alt="Server API" style="width: 100%;"/>
      </a>
      <ul>
        <li>Core fantasy football data endpoints</li>
        <li>Historical statistics and trends</li>
        <li>Team and player performance metrics</li>
      </ul>
    </td>
    <td width="50%">
      <h4>🧠 ML Model API</h4>
      <a href="https://swc-fantasy-football.onrender.com/docs">
        <img src="/assets/deployed-ml-api.png" alt="ML Model API" style="width: 100%;"/>
      </a>
      <ul>
        <li>Predictive analytics endpoints</li>
        <li>Player acquisition value forecasts</li>
        <li>Weekly performance projections</li>
      </ul>
    </td>
  </tr>
</table>

**Local Development:**
```bash
# Server API
cd server && uvicorn main:app --reload

# ML Model API
cd ml_model && uvicorn main:app --reload
```

### 📦 Machine Learning Pipeline (`/ml_model`)

Our production-ready ML deployment provides accurate predictions for fantasy football decisions.

**Technical Highlights:**
- ⚙️ **Optimized Inference**: ONNX Runtime for high-performance predictions
- 🌐 **RESTful Interface**: FastAPI endpoints for seamless model integration
- 🧪 **End-to-End Pipeline**: Complete preprocessing and postprocessing workflow

📂 [`/ml_model`](./ml_model)

### 🤖 AI Assistant (`/ai_agent`)

An advanced AI-powered fantasy football assistant to guide your strategy.

**Powered By:**
- 🧠 **LangGraph**: Sophisticated reasoning workflows for complex fantasy decisions
- ✨ **Gemini API**: Natural language understanding for intuitive interactions
- 📓 **Interactive Examples**: Jupyter notebooks demonstrating capabilities

📂 [`/ai_agent`](./ai_agent)

## 💰 Player Acquisition Predictor

Make smarter bids with our ML-powered FAAB predictor:

<img src="/assets/bid-predictor.png" alt="Player Acquisition Predictor" style="max-width: 100%; height: auto;">

## 📊 Example: Points Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt
import swc_simple_client as swc

# Configure API connection
client = swc.FFClient("https://swc-s-fantasy-football-api-service.onrender.com")

# Fetch weekly data
weeks_df = client.get_weeks()
weeks_df['year'] = weeks_df['week_number'].str.slice(0, 4).astype(int)
weeks_df['week'] = weeks_df['week_number'].str.slice(4, 6).astype(int)

# Filter to regular season
reg_season = weeks_df.query('week <= 14')

# Aggregate yearly point totals
yearly_totals = reg_season.groupby('year').agg({
    'ppr_12_max_points': 'sum',
    'half_ppr_8_max_points': 'sum'
})

# Visualize trend
plt.figure(figsize=(10, 6))
yearly_totals.plot(kind='bar', color=['#1f77b4', '#ff7f0e'])
plt.title('Fantasy Points by Season', fontsize=16)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Total Points', fontsize=12)
plt.legend(['PPR (12-team)', 'Half PPR (8-team)'])
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
```

## 📈 Data Sources

The platform integrates multiple data sources for comprehensive analysis:

- **Live API Data**: Real-time team and player statistics
- **Historical CSV Data**: Long-term trends and championship analytics
- **Custom Metrics**: Proprietary scoring and performance indicators

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<p align="center">
  <i>Dominate your fantasy league with data-driven decisions</i><br>
  <a href="https://github.com/yourusername/swc-fantasy-football">GitHub</a> •
  <a href="https://swc-s-fantasy-football-api-service.onrender.com/docs">API Docs</a> •
  <a href="https://swc-fantasy-football.onrender.com/docs">ML API</a>
</p>