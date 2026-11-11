# AI-Powered Inventory Intelligence & Demand Forecasting System

An AI-powered inventory management and demand forecasting application built using Python, Streamlit, MySQL, and Machine Learning.

## Project Overview

This project helps businesses analyse historical sales data, predict future product demand, monitor inventory levels, and make data-driven restocking decisions.

The system uses Machine Learning and statistical forecasting techniques to estimate future demand and provides inventory recommendations through an interactive dashboard.

## Key Features

- Interactive inventory analytics dashboard
- CSV and Excel dataset upload
- Automatic detection of common dataset column names
- Product-wise demand forecasting
- Forecasting model comparison
- Forecast accuracy evaluation
- Safety stock and reorder point calculations
- Inventory risk classification
- Recommended reorder quantities
- Sales and revenue analytics
- MySQL database integration
- Rule-based inventory chatbot
- PDF report generation
- CSV report export
- Forecast history tracking

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Database | MySQL |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Reporting | ReportLab |
| Version Control | Git and GitHub |

## Forecasting Techniques

**1. Linear Regression**

A Machine Learning algorithm used to identify trends in historical sales data and predict future demand.

**2. Moving Average**

A statistical forecasting technique that calculates demand using the average of the previous three months.

**3. Naive Forecasting**

A baseline method that uses the previous month's sales as the next month's prediction.

The application compares forecasting errors to help select an appropriate forecasting model.

## Inventory Management

The system calculates:

- Predicted monthly demand
- Average daily demand
- Safety stock
- Reorder point
- Recommended order quantity
- Inventory coverage days
- Inventory risk level

These calculations support inventory planning and help identify products that may require restocking.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Inventory-Demand-Forecasting.git
```

### 2. Navigate to the project directory

```bash
cd AI-Inventory-Demand-Forecasting
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the database

Install MySQL and create the required database and tables.

Create a `.env` file locally with the database connection settings expected by `config/database.py`.

Do not commit passwords or API keys to GitHub.

### 7. Run the application

```bash
streamlit run app.py
```

## Application Workflow

1. Upload historical sales data.
2. Validate and process the dataset.
3. Identify relevant product, sales, and inventory columns.
4. Generate product-wise demand forecasts.
5. Compare forecasting methods.
6. Calculate inventory requirements and risk levels.
7. Explore the dashboard and business insights.
8. Save analysis results in MySQL.
9. Export reports.

## Chatbot

The application includes a rule-based chatbot that answers predefined inventory-related questions using database queries.

The chatbot is not a Generative AI or LLM-based assistant.

## Limitations

- Forecast quality depends on historical sales data.
- Linear Regression may not capture complex seasonal patterns.
- Safety stock uses a simplified calculation.
- The chatbot supports predefined query patterns rather than unrestricted natural-language conversations.

## Future Enhancements

- Random Forest and XGBoost forecasting
- Seasonal demand prediction
- Advanced anomaly detection
- Supplier management
- Purchase order generation
- More advanced AI chatbot integration
- Cloud deployment

## Project Category

Machine Learning | Inventory Management | Demand Forecasting | Business Analytics

## License

No license has been specified for this repository.