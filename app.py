import os
import logging
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from flask import Flask, request, Response
from faker import Faker
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

# Initialize Faker
fake = Faker('en_US')

class AutomotiveDashboard:
    def __init__(self):
        self.df = self.generate_sales_data()
        logging.info("Sales data generated successfully")
        self.hr_data, self.inventory_data, self.crm_data, self.demo_data, self.time_log_data = self.generate_fake_data()
        self.filtered_df = self.df.copy()  # Initialize filtered_df

    def generate_sales_data(self):
        try:
            car_makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes', 'Hyundai', 'Volkswagen']
            car_models = {
                'Toyota': ['Camry', 'Corolla', 'RAV4'],
                'Honda': ['Civic', 'Accord', 'CR-V'],
                'Ford': ['F-150', 'Mustang', 'Explorer'],
                'Chevrolet': ['Silverado', 'Malibu', 'Equinox'],
                'BMW': ['3 Series', '5 Series', 'X5'],
                'Mercedes': ['C-Class', 'E-Class', 'GLC'],
                'Hyundai': ['Elantra', 'Sonata', 'Tucson'],
                'Volkswagen': ['Jetta', 'Passat', 'Tiguan']
            }
            salespeople = [fake.name() for _ in range(10)]
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
            df['Car Model'] = df['Car Make'].apply(lambda x: random.choice(car_models[x]))
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
                "Name": [fake.name() for _ in range(10)],
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
                "Clock In": [f"{np.random.randint(8, 10)}:{str(np.random.randint(0, 60)).zfill(2)} AM" for _ in range(30)],
                "Clock Out": [f"{np.random.randint(4, 6)+12}:{str(np.random.randint(0, 60)).zfill(2)} PM" for _ in range(30)],
                "Total Hours": [round(np.random.uniform(6.5, 9.5), 1) for _ in range(30)]
            }).sort_values(by="Date", ascending=False)
            inventory_data = pd.DataFrame({
                "Part ID": [f"P{i:04d}" for i in range(1, 21)],
                "Part Name": [fake.word().capitalize() + " " + random.choice(["Filter", "Brake", "Tire", "Battery", "Sensor", "Pump"]) for _ in range(20)],
                "Car Make": [random.choice(self.df['Car Make'].dropna().unique()) for _ in range(20)],
                "Stock Level": [random.randint(0, 150) for _ in range(20)],
                "Reorder Level": [random.randint(10, 60) for _ in range(20)],
                "Unit Cost": [round(random.uniform(20, 600), 2) for _ in range(20)]
            })
            end_date = datetime.strptime("2025-07-13", "%Y-%m-%d")
            crm_data = pd.DataFrame({
                "Customer ID": [f"C{100+i}" for i in range(20)],
                "Customer Name": [fake.name() for _ in range(20)],
                "Contact Date": [fake.date_between(start_date="-1y", end_date=end_date) for _ in range(20)],
                "Interaction Type": [random.choice(["Inquiry", "Complaint", "Follow-up", "Feedback", "Service Request"]) for _ in range(20)],
                "Salesperson": [random.choice(self.df['Salesperson'].dropna().unique()) for _ in range(20)],
                "Satisfaction Score": [round(random.uniform(1.0, 5.0), 1) for _ in range(20)]
            })
            demo_data = pd.DataFrame({
                "Customer ID": [f"C{100+i}" for i in range(20)],
                "Age Group": [random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]) for _ in range(20)],
                "Region": [fake.state() for _ in range(20)],
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

@app.route('/health')
def health():
    return {"status": "OK"}, 200

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            dashboard.filtered_df = dashboard.df.copy()
            salesperson = request.form.get('salesperson', 'All')
            car_make = request.form.get('car_make', 'All')
            car_model = request.form.get('car_model', 'All')
            car_year = request.form.get('car_year', 'All')
            if salesperson != 'All':
                dashboard.filtered_df = dashboard.filtered_df[dashboard.filtered_df['Salesperson'] == salesperson]
            if car_make != 'All':
                dashboard.filtered_df = dashboard.filtered_df[dashboard.filtered_df['Car Make'] == car_make]
            if car_model != 'All':
                dashboard.filtered_df = dashboard.filtered_df[dashboard.filtered_df['Car Model'] == car_model]
            if car_year != 'All':
                dashboard.filtered_df = dashboard.filtered_df[dashboard.filtered_df['Car Year'].astype(str) == car_year]
            logging.info("Filters applied successfully")

        salespeople = ['All'] + sorted(dashboard.df['Salesperson'].dropna().unique())
        car_makes = ['All'] + sorted(dashboard.df['Car Make'].dropna().unique())
        car_years = ['All'] + sorted(dashboard.df['Car Year'].dropna().astype(str).unique())
        metrics = ["Sale Price", "Commission Earned"]

        salesperson_options = ''.join(f'<option value="{s.replace('"', '&quot;')}">{s}</option>' for s in salespeople)
        car_make_options = ''.join(f'<option value="{c}">{c}</option>' for c in car_makes)
        car_year_options = ''.join(f'<option value="{y}">{y}</option>' for y in car_years)
        metric_options = ''.join(f'<option value="{m}">{m}</option>' for m in metrics)

        # Calculate KPIs for display
        total_sales = f"${dashboard.filtered_df['Sale Price'].sum():,.0f}"
        total_comm = f"${dashboard.filtered_df['Commission Earned'].sum():,.0f}"
        avg_price = f"${dashboard.filtered_df['Sale Price'].mean():,.0f}" if not dashboard.filtered_df.empty else "$0"
        trans_count = f"{dashboard.filtered_df.shape[0]:,}"

        # Generate KPI Trend chart
        if dashboard.filtered_df.empty:
            chart_html = "<p style='color:white'>No data available for KPI Trend</p>"
        else:
            kpi_trend = dashboard.filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Sale Price'], name='Sale Price', line=dict(color='#A9A9A9')))
            fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Commission Earned'], name='Commission', line=dict(color='#808080')))
            fig.update_layout(
                xaxis_title='Month', yaxis_title='Amount ($)', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Automotive Sales Dashboard</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .header { background-color: #2A2A2A; padding: 10px; text-align: left; border-bottom: 1px solid #4A4A4A; }
                .header h1 { margin: 0; font-size: 24px; }
                .filters { background-color: #2A2A2A; padding: 10px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; border-bottom: 1px solid #4A4A4A; }
                .filters label { font-size: 14px; margin-right: 5px; }
                .filters select { padding: 8px; background-color: #3A3A3A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 4px; min-width: 120px; }
                .filters button { padding: 8px 15px; background-color: #606060; color: #D3D3D3; border: none; border-radius: 4px; cursor: pointer; }
                .filters button:hover { background-color: #707070; }
                .kpi-container { display: flex; flex-wrap: wrap; gap: 10px; padding: 10px; background-color: #1C1C1C; }
                .kpi-box { background-color: #2A2A2A; padding: 15px; border-radius: 4px; text-align: center; flex: 1; min-width: 150px; border: 1px solid #4A4A4A; }
                .kpi-label { font-size: 14px; color: #A9A9A9; }
                .kpi-value { font-size: 20px; font-weight: bold; }
                .nav { background-color: #2A2A2A; padding: 10px; border-bottom: 1px solid #4A4A4A; overflow-x: auto; white-space: nowrap; }
                .nav a { color: #A9A9A9; margin-right: 15px; text-decoration: none; font-size: 14px; }
                .nav a:hover { color: #FFFFFF; }
                .chart-container { padding: 10px; }
                .footer { text-align: center; font-size: 12px; color: #A9A9A9; padding: 10px; border-top: 1px solid #4A4A4A; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Automotive Sales Dashboard</h1>
            </div>
            <div class="filters">
                <form method="POST" action="/" style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; width: 100%;">
                    <label for="salesperson">Salesperson:</label>
                    <select name="salesperson" id="salesperson">
                        {0}
                    </select>
                    <label for="car_make">Car Make:</label>
                    <select id="car_make" name="car_make" onchange="updateModels()">
                        {1}
                    </select>
                    <label for="car_model">Car Model:</label>
                    <select id="car_model" name="car_model">
                        <option value="All">All</option>
                    </select>
                    <label for="car_year">Car Year:</label>
                    <select name="car_year" id="car_year">
                        {2}
                    </select>
                    <label for="metric">Metric:</label>
                    <select name="metric" id="metric">
                        {3}
                    </select>
                    <button type="submit">Apply Filters</button>
                </form>
            </div>
            <div class="kpi-container">
                <div class="kpi-box">
                    <div class="kpi-label">Total Sales</div>
                    <div class="kpi-value">{4}</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Total Commission</div>
                    <div class="kpi-value">{5}</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Avg Sale Price</div>
                    <div class="kpi-value">{6}</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Transactions</div>
                    <div class="kpi-value">{7}</div>
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
                <h3>KPI Trend</h3>
                {8}
            </div>
            <form id="downloadForm" method="POST" action="/download_csv" onsubmit="updateHidden()" style="padding: 10px;">
                <input type="hidden" name="salesperson" value="All">
                <input type="hidden" name="car_make" value="All">
                <input type="hidden" name="car_model" value="All">
                <input type="hidden" name="car_year" value="All">
                <button type="submit" style="background-color: #606060; color: #D3D3D3; border: none; border-radius: 4px; padding: 8px 15px; cursor: pointer;">Download CSV</button>
            </form>
            <div class="footer">
                © 2025 Automotive Sales | Crafted for smarter decisions
            </div>
            <script>
                const carModels = {{
                    'Toyota': ['Camry', 'Corolla', 'RAV4'],
                    'Honda': ['Civic', 'Accord', 'CR-V'],
                    'Ford': ['F-150', 'Mustang', 'Explorer'],
                    'Chevrolet': ['Silverado', 'Malibu', 'Equinox'],
                    'BMW': ['3 Series', '5 Series', 'X5'],
                    'Mercedes': ['C-Class', 'E-Class', 'GLC'],
                    'Hyundai': ['Elantra', 'Sonata', 'Tucson'],
                    'Volkswagen': ['Jetta', 'Passat', 'Tiguan']
                }};

                function updateModels() {{
                    const make = document.getElementById('car_make').value;
                    const modelSelect = document.getElementById('car_model');
                    modelSelect.innerHTML = '<option value="All">All</option>';
                    if (make !== 'All' && carModels[make]) {{
                        carModels[make].forEach(model => {{
                            const option = document.createElement('option');
                            option.value = model;
                            option.text = model;
                            modelSelect.add(option);
                        }});
                    }}
                }}

                function updateHidden() {{
                    document.querySelector('#downloadForm input[name="salesperson"]').value = document.querySelector('select[name="salesperson"]').value;
                    document.querySelector('#downloadForm input[name="car_make"]').value = document.querySelector('select[name="car_make"]').value;
                    document.querySelector('#downloadForm input[name="car_model"]').value = document.querySelector('select[name="car_model"]').value;
                    document.querySelector('#downloadForm input[name="car_year"]').value = document.querySelector('select[name="car_year"]').value;
                }}
            </script>
        </body>
        </html>
        """.format(salesperson_options, car_make_options, car_year_options, metric_options, total_sales, total_comm, avg_price, trans_count, chart_html)
        return html
    except Exception as e:
        logging.error(f"Error rendering index page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/3d')
def three_d():
    try:
        if dashboard.filtered_df.empty:
            chart_html = "<p style='color:white'>No data available for 3D Sales</p>"
        else:
            scatter_data = dashboard.filtered_df.sample(n=min(100, len(dashboard.filtered_df)), random_state=1)
            fig = go.Figure(data=[
                go.Scatter3d(
                    x=scatter_data['Commission Earned'], y=scatter_data['Sale Price'], z=scatter_data['Car Year'],
                    mode='markers', marker=dict(size=5, color=scatter_data['Car Year'], colorscale='Greys', showscale=True)
                )
            ])
            fig.update_layout(
                scene=dict(xaxis_title='Commission Earned ($)', yaxis_title='Sale Price ($)', zaxis_title='Car Year'),
                template='plotly_dark', plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>3D Sales</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .header { background-color: #2A2A2A; padding: 10px; text-align: left; border-bottom: 1px solid #4A4A4A; }
                .header h1 { margin: 0; font-size: 24px; }
                .nav { background-color: #2A2A2A; padding: 10px; border-bottom: 1px solid #4A4A4A; overflow-x: auto; white-space: nowrap; }
                .nav a { color: #A9A9A9; margin-right: 15px; text-decoration: none; font-size: 14px; }
                .nav a:hover { color: #FFFFFF; }
                .chart-container { padding: 10px; }
                .footer { text-align: center; font-size: 12px; color: #A9A9A9; padding: 10px; border-top: 1px solid #4A4A4A; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>3D Sales</h1>
            </div>
            <div class="nav">
                <a href="/">KPI Trend</a>
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
                {0}
            </div>
            <div class="footer">
                © 2025 Automotive Sales | Crafted for smarter decisions
            </div>
        </body>
        </html>
        """.format(chart_html)
        return html
    except Exception as e:
        logging.error(f"Error rendering 3D Sales page: {str(e)}")
        return f"Error: {str(e)}", 500

# Similarly update other routes with consistent layout and styling

@app.route('/heatmap')
def heatmap():
    try:
        selected_metric = request.args.get('metric', 'Sale Price')
        if dashboard.filtered_df.empty:
            chart_html = "<p style='color:white'>No data available for Heatmap</p>"
        else:
            heatmap_data = dashboard.filtered_df.pivot_table(
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
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Heatmap</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .header { background-color: #2A2A2A; padding: 10px; text-align: left; border-bottom: 1px solid #4A4A4A; }
                .header h1 { margin: 0; font-size: 24px; }
                .nav { background-color: #2A2A2A; padding: 10px; border-bottom: 1px solid #4A4A4A; overflow-x: auto; white-space: nowrap; }
                .nav a { color: #A9A9A9; margin-right: 15px; text-decoration: none; font-size: 14px; }
                .nav a:hover { color: #FFFFFF; }
                .chart-container { padding: 10px; }
                .footer { text-align: center; font-size: 12px; color: #A9A9A9; padding: 10px; border-top: 1px solid #4A4A4A; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Heatmap</h1>
            </div>
            <div class="nav">
                <a href="/">KPI Trend</a>
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
                {0}
            </div>
            <div class="footer">
                © 2025 Automotive Sales | Crafted for smarter decisions
            </div>
        </body>
        </html>
        """.format(chart_html)
        return html
    except Exception as e:
        logging.error(f"Error rendering Heatmap page: {str(e)}")
        return f"Error: {str(e)}", 500

# Continue updating other routes similarly for consistent UI

# ... (rest of the code for other routes, applying similar styling and structure)

@app.route('/download_csv', methods=['POST'])
def download_csv():
    try:
        filtered_df = dashboard.filtered_df.copy()
        salesperson = request.form.get('salesperson', 'All')
        car_make = request.form.get('car_make', 'All')
        car_model = request.form.get('car_model', 'All')
        car_year = request.form.get('car_year', 'All')
        if salesperson != 'All':
            filtered_df = filtered_df[filtered_df['Salesperson'] == salesperson]
        if car_make != 'All':
            filtered_df = filtered_df[filtered_df['Car Make'] == car_make]
        if car_model != 'All':
            filtered_df = filtered_df[filtered_df['Car Model'] == car_model]
        if car_year != 'All':
            filtered_df = filtered_df[filtered_df['Car Year'].astype(str) == car_year]
        csv = filtered_df.to_csv(index=False)
        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=filtered_data.csv"}
        )
    except Exception as e:
        logging.error(f"Error generating CSV: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
