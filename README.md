# Olist E-commerce Analytics & Recommendation Engine 🚀

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)

A comprehensive Business Intelligence dashboard and Product Recommendation System built for the Olist E-commerce dataset. This project utilizes Data Science techniques (RFM Analysis, Segmentation) to provide actionable business insights and personalized product suggestions.

## 🎯 Key Features

### 1. 📊 Executive Dashboard
* **High-Level KPIs:** Real-time tracking of Total Revenue, Average Order Value (AOV), and Customer Retention Rate.
* **Business Impact Analysis:** Visualization of the Pareto principle (80/20 rule) comparing customer count vs. revenue share.
* **RFM Segmentation Matrix:** Interactive Scatter Plot visualizing customer clusters based on Recency and Monetary value.

### 2. 👥 Customer 360° View
* **Deep Dive Profiling:** Detailed individual customer statistics (Total Spend, Frequency, Days since last purchase).
* **Order History:** Full searchable history of previous transactions for every client.
* **Dynamic Filtering:** Filter customers by Segment (VIP, Repeat, One-time), Spend, and Order Count.

### 3. 🛍️ Recommendation Engine
* **Segment-Based Filtering:** Products are recommended based on what is most popular within the user's specific behavioral segment.
* **"Lottery" Mechanism:** To ensure variety, the system selects top candidates and randomizes the display from the best-performing items.
* **Purchase Probability:** A calculated "Match Score" showing how well a product fits the segment's buying patterns.

## 🛠️ Tech Stack
* **Application:** Python, Streamlit
* **Data Processing:** Pandas, NumPy, Jupyter Notebooks
* **Containerization:** Docker, Docker Compose
* **Data Source:** Olist Brazilian E-Commerce Dataset

## 📂 Project Structure

```text
├── data/                   # Dataset files (CSV) - excluded from git
├── app.py                  # Main Streamlit application
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Container orchestration
├── requirements.txt        # Python dependencies
├── segmentation.ipynb      # ETL & Analysis Notebook (generates segments)
└── README.md               # Project documentation
```

## 🚀 How to Run

### Prerequisites
* Docker & Docker Compose installed.
* **Data Files:** Due to GitHub size limits, the raw data files are not included in this repository.

### Step 1: Clone the repository
```bash
git clone https://github.com/BartlomiejJurowicz/segmentacja
cd <YOUR_FOLDER_NAME>
