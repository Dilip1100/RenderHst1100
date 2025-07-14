import os
import logging
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from flask import Flask, request, Response, session
from datetime import datetime
import random
import json

# Configure Plotly for offline rendering
pio.templates.default = "plotly_dark"

# Set up logging to stdout for Render
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'a secret key'

class AutomotiveDashboard:
    def __init__(self):
        self.df = self.generate_sales_data()
        logging.info("Sales data generated successfully")
        self.hr_data, self.inventory_data, self.crm_data, self.demo_data, self.time_log_data = self.generate_fake_data()
        self.car_models = {
            'Toyota': ['Camry', 'Corolla', 'RAV4'],
            'Honda': ['Civic', 'Accord', 'CR-V'],
            'Ford': ['F-150', 'Mustang', 'Explorer'],
            'Chevrolet': ['Silverado', 'Malibu', 'Equinox'],
            'BMW': ['3 Series', '5 Series', 'X5'],
            'Mercedes': ['C-Class', 'E-Class', 'GLC'],
            'Hyundai': ['Elantra', 'Sonata', 'Tucson'],
            'Volkswagen': ['Jetta', 'Passat', 'Tiguan']
        }

    def generate_sales_data(self):
        try:
            car_makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes', 'Hyundai', 'Volkswagen']
            salespeople = [f"Salesperson {i}" for i in range(1, 11)]
            dates = pd.date_range(start="2023-01-01", end="2025-07-13", freq="D")
            data = {
                'Salesperson': [random.choice(salespeople) for _ in range(1000)],
                'Car Make': [random.choice(car_makes) for _ in range(1000)],
                'Car Year': [random.randint(2018, 2025) for _ in range(1000)],
                'Date': [random.choice(dates) for _ in range(1000)],
                'Sale Price': [round(random.uniform(15000, 100000), 2) for _ in range(1000)],
                'Commission Earned': [round(random.uniform(500, 5000), 2) for _ in range(1000)]
            }
            df = pd.DataFrame(data)
            df['Car Model'] = df['Car Make'].apply(lambda x: random.choice(self.car_models[x]))
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Year'] = df['Date'].dt.year
            df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
            df['Month'] = df['Date'].dt.to_period('M').astype(str)
            return df
        except Exception as e:
            logging.error(f"Error generating sales data: {str(e)}")
            return pd.DataFrame()

    def generate_fake_data(self):
        try:
            hr_data = pd.DataFrame({
                "Employee ID": [f"E{1000+i}" for i in range(10)],
                "Name": [f"Employee {i}" for i in range(1, 11)],
                "Role": ["Sales Exec", "Manager", "Technician", "Clerk", "Sales Exec", "Technician", "HR", "Manager", "Clerk", "Sales Exec"],
                "Department": ["Sales", "Sales", "Service", "Admin", "Sales", "Service", "HR", "Sales", "Admin", "Sales"],
                "Join Date": pd.date_range(start="2018-01-01", periods=10, freq="180D"),
                "Salary (USD)": [50000 + i*1500 for i in range(10)],
                "Performance Score": [round(x, 1) for x in np.random.uniform(2.5, 5.0, 10)]
            })
            end_date = pd.to_datetime("2025-07-13")
            time_log_data = pd.DataFrame({
                "Employee ID": np.random.choice(hr_data["Employee ID"], size=30, replace=True),
                "Date": pd.date_range(end=end_date, periods=30).tolist(),
                "Clock In": [f"{random.randint(8, 10)}:{str(random.randint(0, 59)).zfill(2)} AM" for _ in range(30)],
                "Clock Out": [f"{random.randint(4, 6)+12}:{str(random.randint(0, 59)).zfill(2)} PM" for _ in range(30)],
                "Total Hours": [round(random.uniform(6.5, 9.5), 1) for _ in range(30)]
            }).sort_values(by="Date", ascending=False)
            inventory_data = pd.DataFrame({
                "Part ID": [f"P{i:04d}" for i in range(1, 21)],
                "Part Name": [f"Part {i} " + random.choice(["Filter", "Brake", "Tire", "Battery", "Sensor", "Pump"]) for i in range(1, 21)],
                "Car Make": [random.choice(self.df['Car Make'].dropna().unique()) for _ in range(20)],
                "Stock Level": [random.randint(0, 150) for _ in range(20)],
                "Reorder Level": [random.randint(10, 60) for _ in range(20)],
                "Unit Cost": [round(random.uniform(20, 600), 2) for _ in range(20)]
            })
            end_date = datetime.strptime("2025-07-13", "%Y-%m-%d")
            start_date = end_date - pd.Timedelta(days=365)
            crm_data = pd.DataFrame({
                "Customer ID": [f"C{100+i}" for i in range(20)],
                "Customer Name": [f"Customer {i}" for i in range(1, 21)],
                "Contact Date": [start_date + pd.Timedelta(days=random.randint(0, 365)) for _ in range(20)],
                "Interaction Type": [random.choice(["Inquiry", "Complaint", "Follow-up", "Feedback", "Service Request"]) for _ in range(20)],
                "Salesperson": [random.choice(self.df['Salesperson'].dropna().unique()) for _ in range(20)],
                "Satisfaction Score": [round(random.uniform(1.0, 5.0), 1) for _ in range(20)]
            })
            states = ['California', 'Texas', 'New York', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Michigan', 'Georgia', 'North Carolina']
            demo_data = pd.DataFrame({
                "Customer ID": [f"C{100+i}" for i in range(20)],
                "Age Group": [random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]) for _ in range(20)],
                "Region": [random.choice(states) for _ in range(20)],
                "Purchase Amount": [round(random.uniform(15000, 100000), 2) for _ in range(20)],
                "Preferred Make": [random.choice(self.df['Car Make'].dropna().unique()) for _ in range(20)]
            })
            logging.info("Fake data generated successfully")
            return hr_data, inventory_data, crm_data, demo_data, time_log_data
        except Exception as e:
            logging.error(f"Error generating fake data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Initialize dashboard
dashboard = AutomotiveDashboard()

# Helper function to generate table HTML
def generate_table_html(df, columns, formatters=None):
    if df.empty:
        return "<p style='color:white'>No data available</p>"
    formatters = formatters or {}
    html = "<table style='width:100%;border-collapse:collapse;border:1px solid #4A4A4A;color:#D3D3D3;background-color:#2A2A2A;font-family:Arial,sans-serif;font-size:12px;'>"
    html += "<tr style='background-color:#3A3A3A;'>" + "".join(f"<th style='padding:5px;border:1px solid #4A4A4A;'>{col}</th>" for col in columns) + "</tr>"
    for _, row in df.iterrows():
        html += "<tr>"
        for col in columns:
            value = row[col]
            formatter = formatters.get(col, lambda x: str(x))
            html += f"<td style='padding:5px;border:1px solid #4A4A4A;'>{formatter(value)}</td>"
        html += "</tr>"
    html += "</table>"
    return html

# Helper function to get filtered df
def get_filtered_df():
    df = dashboard.df.copy()
    salesperson = session.get('salesperson', 'All')
    car_make = session.get('car_make', 'All')
    car_model = session.get('car_model', 'All')
    car_year = session.get('car_year', 'All')
    if salesperson != 'All':
        df = df[df['Salesperson'] == salesperson]
    if car_make != 'All':
        df = df[df['Car Make'] == car_make]
    if car_model != 'All':
        df = df[df['Car Model'] == car_model]
    if car_year != 'All':
        df = df[df['Car Year'].astype(str) == car_year]
    return df

# Helper function to calculate KPIs
def calculate_kpis(filtered_df):
    total_sales = f"₹{filtered_df['Sale Price'].sum():,.0f}"
    total_comm = f"₹{filtered_df['Commission Earned'].sum():,.0f}"
    avg_price = f"₹{filtered_df['Sale Price'].mean():,.0f}" if not filtered_df.empty else "₹0"
    trans_count = f"{filtered_df.shape[0]:,}"
    return total_sales, total_comm, avg_price, trans_count

def get_common_html_parts():
    salespeople = ['All'] + sorted(dashboard.df['Salesperson'].dropna().unique().tolist())
    car_makes = ['All'] + sorted(dashboard.df['Car Make'].dropna().unique().tolist())
    car_years = ['All'] + sorted(dashboard.df['Car Year'].dropna().astype(str).unique().tolist())
    metrics = ["Sale Price", "Commission Earned"]

    salesperson_options = ''.join(f'<option value="{s}" {"selected" if s == session.get("salesperson", "All") else ""}>{s}</option>' for s in salespeople)
    car_make_options = ''.join(f'<option value="{c}" {"selected" if c == session.get("car_make", "All") else ""}>{c}</option>' for c in car_makes)
    car_year_options = ''.join(f'<option value="{y}" {"selected" if y == session.get("car_year", "All") else ""}>{y}</option>' for y in car_years)
    metric_options = ''.join(f'<option value="{m}" {"selected" if m == session.get("metric", "Sale Price") else ""}>{m}</option>' for m in metrics)

    car_models_json = json.dumps(dashboard.car_models)

    return salesperson_options, car_make_options, car_year_options, metric_options, car_models_json

@app.route('/health')
def health():
    return {"status": "OK"}, 200

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for KPI Trend</p>"
    else:
        kpi_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Sale Price'], name='Sale Price', line=dict(color='#A9A9A9')))
        fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Commission Earned'], name='Commission', line=dict(color='#808080')))
        fig.update_layout(
            xaxis_title='Month', yaxis_title='Amount (₹)', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/kpi', methods=['GET', 'POST'])
def kpi():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for KPI Trend</p>"
    else:
        kpi_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Sale Price'], name='Sale Price', line=dict(color='#A9A9A9')))
        fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Commission Earned'], name='Commission', line=dict(color='#808080')))
        fig.update_layout(
            xaxis_title='Month', yaxis_title='Amount (₹)', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>KPI Trend - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    <h2>KPI Trend</h2>
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/3d', methods=['GET', 'POST'])
def three_d():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for 3D Sales</p>"
    else:
        scatter_data = filtered_df.sample(n=min(100, len(filtered_df)), random_state=1)
        fig = go.Figure(data=[
            go.Scatter3d(
                x=scatter_data['Commission Earned'], y=scatter_data['Sale Price'], z=scatter_data['Car Year'],
                mode='markers', marker=dict(size=5, color=scatter_data['Car Year'], colorscale='Greys', showscale=True)
            )
        ])
        fig.update_layout(
            scene=dict(xaxis_title='Commission Earned (₹)', yaxis_title='Sale Price (₹)', zaxis_title='Car Year'),
            template='plotly_dark', plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>3D Sales - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    <h2>3D Sales</h2>
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/heatmap', methods=['GET', 'POST'])
def heatmap():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)
    selected_metric = session.get('metric', 'Sale Price')

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for Heatmap</p>"
    else:
        heatmap_data = filtered_df.pivot_table(
            values=selected_metric, index='Salesperson', columns='Car Make', aggfunc='sum', fill_value=0
        )
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index, colorscale='Greys'
        ))
        fig.update_layout(
            xaxis_title='Car Make', yaxis_title='Salesperson', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Heatmap - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    <h2>Heatmap</h2>
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/top', methods=['GET', 'POST'])
def top():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)
    selected_metric = session.get('metric', 'Sale Price')

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for Top Performers</p>"
    else:
        top_salespeople = filtered_df.groupby('Salesperson')[selected_metric].sum().nlargest(10).reset_index()
        fig = go.Figure(data=[go.Bar(x=top_salespeople['Salesperson'], y=top_salespeople[selected_metric], marker_color='#A9A9A9')])
        fig.update_layout(
            xaxis_title='Salesperson', yaxis_title=f"{selected_metric} (₹)", template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Top Performers - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    <h2>Top Performers</h2>
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/vehicle', methods=['GET', 'POST'])
def vehicle():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for Vehicle Sales</p>"
    else:
        car_make_metric = filtered_df.groupby('Car Make')['Sale Price'].sum().nlargest(10).reset_index()
        fig_make = go.Figure(data=go.Pie(
            labels=car_make_metric['Car Make'], values=car_make_metric['Sale Price'],
            marker_colors=['#D3D3D3', '#A9A9A9', '#808080', '#606060', '#4A4A4A', '#3A3A3A', '#2A2A2A', '#1C1C1C']
        ))
        fig_make.update_layout(template='plotly_dark', plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400)
        make_html = pio.to_html(fig_make, full_html=False, include_plotlyjs=True)

        car_model_metric = filtered_df.groupby('Car Model')['Sale Price'].sum().nlargest(10).reset_index()
        fig_model = go.Figure(data=go.Pie(
            labels=car_model_metric['Car Model'], values=car_model_metric['Sale Price'],
            marker_colors=['#D3D3D3', '#A9A9A9', '#808080', '#606060', '#4A4A4A', '#3A3A3A', '#2A2A2A', '#1C1C1C']
        ))
        fig_model.update_layout(template='plotly_dark', plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400)
        model_html = pio.to_html(fig_model, full_html=False, include_plotlyjs=True)

        chart_html = f"""
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 50%; padding: 10px;">
                    <h3>Car Make</h3>
                    {make_html}
                </div>
                <div style="flex: 50%; padding: 10px;">
                    <h3>Car Model</h3>
                    {model_html}
                </div>
            </div>
        """

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vehicle Sales - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    <h2>Vehicle Sales</h2>
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/model', methods=['GET', 'POST'])
def model():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for Model Comparison</p>"
    else:
        model_comparison = filtered_df.groupby(['Car Make', 'Car Model']).agg({
            'Sale Price': ['mean', 'sum', 'count'],
            'Commission Earned': 'mean'
        }).round(2)
        model_comparison.columns = ['Avg Sale Price', 'Total Sales', 'Transaction Count', 'Avg Commission']
        model_comparison = model_comparison.reset_index()
        table_html = generate_table_html(
            model_comparison,
            ['Car Make', 'Car Model', 'Avg Sale Price', 'Total Sales', 'Transaction Count'],
            {
                'Avg Sale Price': lambda x: f"₹{x:,.2f}",
                'Total Sales': lambda x: f"₹{x:,.2f}",
                'Transaction Count': lambda x: str(int(x))
            }
        )
        chart_html = f"<h2>Model Comparison</h2>{table_html}"

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Model Comparison - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/trends', methods=['GET', 'POST'])
def trends():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    if filtered_df.empty:
        chart_html = "<p style='color:white'>No data available for Trends</p>"
    else:
        trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=trend_df['Quarter'], y=trend_df['Sale Price'], name='Sale Price', line=dict(color='#A9A9A9')))
        fig_trend.add_trace(go.Scatter(x=trend_df['Quarter'], y=trend_df['Commission Earned'], name='Commission', line=dict(color='#808080')))
        fig_trend.update_layout(
            xaxis_title='Quarter', yaxis_title='Amount (₹)', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        trend_html = pio.to_html(fig_trend, full_html=False, include_plotlyjs=True)

        trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change().fillna(0) * 100
        trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change().fillna(0) * 100
        qoq_html = generate_table_html(
            trend_df,
            ['Quarter', 'Sale Price QoQ %', 'Commission QoQ %'],
            {
                'Sale Price QoQ %': lambda x: f"{x:.2f}%",
                'Commission QoQ %': lambda x: f"{x:.2f}%"
            }
        )

        monthly_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
        fig_monthly = make_subplots(rows=1, cols=1)
        fig_monthly.add_trace(go.Bar(x=monthly_trend['Month'], y=monthly_trend['Sale Price'], name='Sale Price', marker_color='#A9A9A9'))
        fig_monthly.add_trace(go.Bar(x=monthly_trend['Month'], y=monthly_trend['Commission Earned'], name='Commission', marker_color='#808080'))
        fig_monthly.update_layout(
            xaxis_title='Month', yaxis_title='Amount (₹)', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'),
            barmode='group', height=400
        )
        monthly_html = pio.to_html(fig_monthly, full_html=False, include_plotlyjs=True)

        chart_html = f"""
            <h2>Quarter-over-Quarter Trend</h2>
            {trend_html}
            <h2>Quarter-over-Quarter % Change</h2>
            {qoq_html}
            <h2>Monthly Trend</h2>
            {monthly_html}
        """

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Trends - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    <h2>Trends</h2>
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/hr', methods=['GET', 'POST'])
def hr():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    hr_html = generate_table_html(
        dashboard.hr_data,
        dashboard.hr_data.columns,
        {
            'Salary (USD)': lambda x: f"₹{x:,.2f}",
            'Join Date': lambda x: x.strftime('%Y-%m-%d')
        }
    )
    if dashboard.hr_data.empty:
        perf_html = "<p style='color:white'>No data available for Performance</p>"
        hours_html = "<p style='color:white'>No data available for Hours</p>"
    else:
        fig_perf = go.Figure(data=[go.Histogram(x=dashboard.hr_data['Performance Score'], nbinsx=5, marker_color='#A9A9A9')])
        fig_perf.update_layout(
            xaxis_title='Performance Score', yaxis_title='Count', template='plotly_dark',
            plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        perf_html = pio.to_html(fig_perf, full_html=False, include_plotlyjs=True)

        total_hours = dashboard.time_log_data.groupby('Employee ID')['Total Hours'].sum().reset_index()
        fig_hours = go.Figure(data=[go.Bar(x=total_hours['Employee ID'], y=total_hours['Total Hours'], marker_color='#A9A9A9')])
        fig_hours.update_layout(
            xaxis_title='Employee ID', yaxis_title='Total Hours', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        hours_html = pio.to_html(fig_hours, full_html=False, include_plotlyjs=True)
    time_log_html = generate_table_html(
        dashboard.time_log_data,
        dashboard.time_log_data.columns,
        {'Date': lambda x: x.strftime('%Y-%m-%d')}
    )

    chart_html = f"""
        <h2>HR Overview</h2>
        <h3>Employee Information & Salary</h3>
        {hr_html}
        <h3>Performance Distribution</h3>
        {perf_html}
        <h3>Employee Time Log</h3>
        {time_log_html}
        <h3>Total Logged Hours per Employee</h3>
        {hours_html}
    """

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>HR Overview - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    inventory_html = generate_table_html(
        dashboard.inventory_data,
        dashboard.inventory_data.columns,
        {'Unit Cost': lambda x: f"₹{x:,.2f}"}
    )
    if dashboard.inventory_data.empty:
        low_stock_html = "<p style='color:white'>No data available for Inventory</p>"
    else:
        low_stock = dashboard.inventory_data[dashboard.inventory_data['Stock Level'] < dashboard.inventory_data['Reorder Level']]
        if low_stock.empty:
            low_stock_html = "<p style='color:white'>No low stock items</p>"
        else:
            fig = go.Figure(data=[go.Bar(x=low_stock['Part Name'], y=low_stock['Stock Level'], marker_color='#A9A9A9')])
            fig.update_layout(
                xaxis_title='Part Name', yaxis_title='Stock Level', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            low_stock_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

    chart_html = f"""
        <h2>Inventory</h2>
        {inventory_html}
        <h3>Low Stock Alert</h3>
        {low_stock_html}
    """

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Inventory - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/crm', methods=['GET', 'POST'])
def crm():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    crm_html = generate_table_html(
        dashboard.crm_data,
        dashboard.crm_data.columns,
        {'Contact Date': lambda x: x.strftime('%Y-%m-%d')}
    )
    if dashboard.crm_data.empty:
        time_html = "<p style='color:white'>No data available for Satisfaction Over Time</p>"
        type_html = "<p style='color:white'>No data available for Satisfaction by Type</p>"
    else:
        line_chart_data = dashboard.crm_data.copy()
        line_chart_data['Contact Date'] = pd.to_datetime(line_chart_data['Contact Date'])
        line_chart_data = line_chart_data.groupby('Contact Date')['Satisfaction Score'].mean().reset_index()
        fig_time = go.Figure(data=[go.Scatter(x=line_chart_data['Contact Date'], y=line_chart_data['Satisfaction Score'], mode='lines+markers', line=dict(color='#A9A9A9'))])
        fig_time.update_layout(
            xaxis_title='Contact Date', yaxis_title='Satisfaction Score', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        time_html = pio.to_html(fig_time, full_html=False, include_plotlyjs=True)

        interaction_types = dashboard.crm_data['Interaction Type'].unique()
        fig_type = go.Figure()
        for itype in interaction_types:
            fig_type.add_trace(go.Box(y=dashboard.crm_data[dashboard.crm_data['Interaction Type'] == itype]['Satisfaction Score'], name=itype))
        fig_type.update_layout(
            xaxis_title='Interaction Type', yaxis_title='Satisfaction Score', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        type_html = pio.to_html(fig_type, full_html=False, include_plotlyjs=True)

    chart_html = f"""
        <h2>CRM</h2>
        {crm_html}
        <h3>Satisfaction Over Time</h3>
        {time_html}
        <h3>Satisfaction Score by Interaction Type</h3>
        {type_html}
    """

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRM - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        session['salesperson'] = request.form.get('salesperson', 'All')
        session['car_make'] = request.form.get('car_make', 'All')
        session['car_model'] = request.form.get('car_model', 'All')
        session['car_year'] = request.form.get('car_year', 'All')
        session['metric'] = request.form.get('metric', 'Sale Price')
        logging.info("Filters applied successfully")

    filtered_df = get_filtered_df()
    total_sales, total_comm, avg_price, trans_count = calculate_kpis(filtered_df)

    demo_html = generate_table_html(
        dashboard.demo_data,
        dashboard.demo_data.columns,
        {'Purchase Amount': lambda x: f"₹{x:,.2f}"}
    )
    if dashboard.demo_data.empty:
        age_html = "<p style='color:white'>No data available for Age Distribution</p>"
        region_html = "<p style='color:white'>No data available for Purchase Amount</p>"
    else:
        age_counts = dashboard.demo_data['Age Group'].value_counts().reset_index()
        age_counts.columns = ['Age Group', 'Count']
        fig_age = go.Figure(data=[go.Bar(x=age_counts['Age Group'], y=age_counts['Count'], marker_color='#A9A9A9')])
        fig_age.update_layout(
            xaxis_title='Age Group', yaxis_title='Count', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        age_html = pio.to_html(fig_age, full_html=False, include_plotlyjs=True)

        regions = dashboard.demo_data['Region'].unique()
        fig_region = go.Figure()
        for region in regions:
            fig_region.add_trace(go.Box(y=dashboard.demo_data[dashboard.demo_data['Region'] == region]['Purchase Amount'], name=region))
        fig_region.update_layout(
            xaxis_title='Region', yaxis_title='Purchase Amount (₹)', template='plotly_dark',
            xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
        )
        region_html = pio.to_html(fig_region, full_html=False, include_plotlyjs=True)

    chart_html = f"""
        <h2>Demographics</h2>
        {demo_html}
        <h3>Age Group Distribution</h3>
        {age_html}
        <h3>Purchase Amount by Region</h3>
        {region_html}
    """

    salesperson_options, car_make_options, car_year_options, metric_options, car_models_json = get_common_html_parts()

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Demographics - Automotive Analytics Dashboard</title>
            <style>
                body {{ background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ display: flex; align-items: center; }}
                h1::before {{ content: '🚗'; margin-right: 10px; }}
                .filter-form {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }}
                label {{ font-weight: bold; margin-bottom: 5px; display: block; }}
                select, button {{ width: 100%; padding: 10px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }}
                button:hover {{ background-color: #3A3A3A; cursor: pointer; }}
                .kpi-section {{ margin: 20px 0; }}
                .kpi-header {{ color: #FF0000; font-size: 18px; margin-bottom: 10px; }}
                .kpi-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
                .kpi-item {{ background-color: #2A2A2A; padding: 15px; border-radius: 5px; border: 1px solid #4A4A4A; text-align: center; }}
                .kpi-item span {{ display: block; font-size: 24px; font-weight: bold; }}
                .nav {{ margin: 20px 0; border-bottom: 1px solid #4A4A4A; }}
                .nav a {{ color: #A9A9A9; margin-right: 15px; text-decoration: none; padding: 10px; display: inline-block; }}
                .nav a:hover {{ color: #FFFFFF; background-color: #3A3A3A; border-radius: 5px 5px 0 0; }}
                .chart-container {{ margin: 20px 0; }}
                .download-form {{ margin-top: 20px; }}
                .footer {{ color: #A9A9A9; font-size: 12px; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Automotive Analytics Dashboard</h1>
                <form class="filter-form" method="POST">
                    <div>
                        <label>Salesperson</label>
                        <select name="salesperson">
                            {salesperson_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Make</label>
                        <select id="car_make" name="car_make" onchange="updateModels()">
                            {car_make_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Year</label>
                        <select name="car_year">
                            {car_year_options}
                        </select>
                    </div>
                    <div>
                        <label>Car Model</label>
                        <select id="car_model" name="car_model">
                            <option value="All">All</option>
                        </select>
                    </div>
                    <div>
                        <label>Metric</label>
                        <select name="metric">
                            {metric_options}
                        </select>
                    </div>
                    <div>
                        <label> </label>
                        <button type="submit">Apply Filters</button>
                    </div>
                </form>
                <div class="kpi-section">
                    <div class="kpi-header">* Key Performance Indicators</div>
                    <div class="kpi-box">
                        <div class="kpi-item">
                            Total Sales<br>
                            <span>{total_sales}</span>
                        </div>
                        <div class="kpi-item">
                            Total Commission<br>
                            <span>{total_comm}</span>
                        </div>
                        <div class="kpi-item">
                            Avg Sale Price<br>
                            <span>{avg_price}</span>
                        </div>
                        <div class="kpi-item">
                            Transactions<br>
                            <span>{trans_count}</span>
                        </div>
                    </div>
                </div>
                <div class="nav">
                    <a href="/kpi">KPI Trend</a>
                    <a href="/3d">3D Sales</a>
                    <a href="/heatmap">Heatmap</a>
                    <a href="/top">Top Performers</a>
                    <a href="/vehicle">Vehicle Sales</a>
                    <a href="/model">Model Comparison</a>
                    <a href="/trends">Trends</a>
                    <a href="/hr">HR Overview</a>
                    <a href="/inventory">Inventory</a>
                    <a href="/crm">CRM</a>
                    <a href="/demo">Demographics</a>
                </div>
                <div class="chart-container">
                    {chart_html}
                </div>
                <form class="download-form" method="POST" action="/download_csv">
                    <button type="submit">Download CSV</button>
                </form>
                <p class="footer">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
            <script>
                const carModels = {car_models_json};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            if (model === '{session.get("car_model", "All")}') {{
                                option.selected = true;
                            }}
                            modelSelect.add(option);
                        }});
                    }} else {{
                        modelSelect.value = '{session.get("car_model", "All")}';
                    }}
                }}
                updateModels();
            </script>
        </body>
        </html>
        """
    return html

@app.route('/download_csv', methods=['POST'])
def download_csv():
    filtered_df = get_filtered_df()
    csv = filtered_df.to_csv(index=False)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=filtered_data.csv"}
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
