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

@app.route('/')
def index():
    try:
        salespeople = ['All'] + sorted(dashboard.df['Salesperson'].dropna().unique())
        car_makes = ['All'] + sorted(dashboard.df['Car Make'].dropna().unique())
        car_years = ['All'] + sorted(dashboard.df['Car Year'].dropna().astype(str).unique())
        metrics = ["Sale Price", "Commission Earned"]
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Automotive Analytics Dashboard</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                select, button { padding: 10px; margin: 5px; background-color: #2A2A2A; color: #D3D3D3; border: 1px solid #4A4A4A; border-radius: 5px; }
                button:hover { background-color: #606060; }
                .nav { margin: 20px 0; }
                .nav a { color: #A9A9A9; margin-right: 15px; text-decoration: none; }
                .nav a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚗 Automotive Analytics Dashboard</h1>
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
                <form method="POST" action="/apply_filters">
                    <label>Salesperson:</label>
                    <select name="salesperson">
                        {}
                    </select><br>
                    <label>Car Make:</label>
                    <select name="car_make">
                        {}
                    </select><br>
                    <label>Car Model:</label>
                    <select name="car_model">
                        <option value="All">All</option>
                    </select><br>
                    <label>Car Year:</label>
                    <select name="car_year">
                        {}
                    </select><br>
                    <label>Metric:</label>
                    <select name="metric">
                        {}
                    </select><br>
                    <button type="submit">Apply Filters</button>
                </form>
                <form method="POST" action="/download_csv">
                    <input type="hidden" name="salesperson" value="All">
                    <input type="hidden" name="car_make" value="All">
                    <input type="hidden" name="car_model" value="All">
                    <input type="hidden" name="car_year" value="All">
                    <button type="submit">Download CSV</button>
                </form>
                <p style="color:#A9A9A9;font-size:12px;text-align:center;">© 2025 One Trust | Crafted for smarter auto-financial decisions</p>
            </div>
        </body>
        </html>
        """
        salesperson_options = ''.join(f'<option value="{s}">{s}</option>' for s in salespeople)
        car_make_options = ''.join(f'<option value="{c}">{c}</option>' for c in car_makes)
        car_year_options = ''.join(f'<option value="{y}">{y}</option>' for y in car_years)
        metric_options = ''.join(f'<option value="{m}">{m}</option>' for m in metrics)
        return html.format(salesperson_options, car_make_options, car_year_options, metric_options)
    except Exception as e:
        logging.error(f"Error rendering index page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/apply_filters', methods=['POST'])
def apply_filters():
    try:
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
        return index()  # Redirect to index to show updated data
    except Exception as e:
        logging.error(f"Error applying filters: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/kpi')
def kpi():
    try:
        if dashboard.filtered_df.empty:
            chart_html = "<p style='color:white'>No data available for KPI Trend</p>"
        else:
            kpi_trend = dashboard.filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
            chart_config = {
                "type": "line",
                "data": {
                    "labels": kpi_trend['Month'].tolist(),
                    "datasets": [
                        {
                            "label": "Sale Price",
                            "data": kpi_trend['Sale Price'].tolist(),
                            "borderColor": "#A9A9A9",
                            "backgroundColor": "#A9A9A9",
                            "fill": False
                        },
                        {
                            "label": "Commission",
                            "data": kpi_trend['Commission Earned'].tolist(),
                            "borderColor": "#808080",
                            "backgroundColor": "#808080",
                            "fill": False
                        }
                    ]
                },
                "options": {
                    "responsive": True,
                    "scales": {
                        "x": {"title": {"display": True, "text": "Month", "color": "#D3D3D3"}, "ticks": {"color": "#D3D3D3", "maxRotation": 45, "minRotation": 45}},
                        "y": {"title": {"display": True, "text": "Amount ($)", "color": "#D3D3D3"}, "ticks": {"color": "#D3D3D3"}}
                    },
                    "plugins": {
                        "legend": {"labels": {"color": "#D3D3D3"}},
                        "title": {"display": True, "text": "KPI Trend", "color": "#D3D3D3"}
                    },
                    "backgroundColor": "#2A2A2A"
                }
            }
            chart_html = f"""
                <canvas id='kpiChart'></canvas>
                <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
                <script>
                    var ctx = document.getElementById('kpiChart').getContext('2d');
                    new Chart(ctx, {json.dumps(chart_config)});
                </script>
            """
        total_sales = f"${dashboard.filtered_df['Sale Price'].sum():,.0f}"
        total_comm = f"${dashboard.filtered_df['Commission Earned'].sum():,.0f}"
        avg_price = f"${dashboard.filtered_df['Sale Price'].mean():,.0f}" if not dashboard.filtered_df.empty else "$0"
        trans_count = f"{dashboard.filtered_df.shape[0]:,}"
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>KPI Trend</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .kpi-box { margin: 20px 0; }
                .kpi-box div { display: inline-block; margin-right: 20px; font-size: 16px; font-weight: bold; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>KPI Trend</h1>
                <div class="kpi-box">
                    <div>Total Sales: {}</div>
                    <div>Total Commission: {}</div>
                    <div>Average Sale Price: {}</div>
                    <div>Transaction Count: {}</div>
                </div>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(total_sales, total_comm, avg_price, trans_count, chart_html)
    except Exception as e:
        logging.error(f"Error rendering KPI page: {str(e)}")
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
        <html>
        <head>
            <title>3D Sales</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>3D Sales</h1>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(chart_html)
    except Exception as e:
        logging.error(f"Error rendering 3D Sales page: {str(e)}")
        return f"Error: {str(e)}", 500

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
        <html>
        <head>
            <title>Heatmap</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Heatmap</h1>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(chart_html)
    except Exception as e:
        logging.error(f"Error rendering Heatmap page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/top')
def top():
    try:
        selected_metric = request.args.get('metric', 'Sale Price')
        if dashboard.filtered_df.empty:
            chart_html = "<p style='color:white'>No data available for Top Performers</p>"
        else:
            top_salespeople = dashboard.filtered_df.groupby('Salesperson')[selected_metric].sum().nlargest(10).reset_index()
            fig = go.Figure(data=[go.Bar(x=top_salespeople['Salesperson'], y=top_salespeople[selected_metric], marker_color='#A9A9A9')])
            fig.update_layout(
                xaxis_title='Salesperson', yaxis_title=f"{selected_metric} ($)", template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Top Performers</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Top Performers</h1>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(chart_html)
    except Exception as e:
        logging.error(f"Error rendering Top Performers page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/vehicle')
def vehicle():
    try:
        if dashboard.filtered_df.empty:
            make_html = "<p style='color:white'>No data available for Car Make</p>"
            model_html = "<p style='color:white'>No data available for Car Model</p>"
        else:
            car_make_metric = dashboard.filtered_df.groupby('Car Make')['Sale Price'].sum().nlargest(10).reset_index()
            fig = go.Figure(data=go.Pie(
                labels=car_make_metric['Car Make'], values=car_make_metric['Sale Price'],
                marker_colors=['#D3D3D3', '#A9A9A9', '#808080', '#606060', '#4A4A4A', '#3A3A3A', '#2A2A2A', '#1C1C1C']
            ))
            fig.update_layout(template='plotly_dark', plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400)
            make_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

            car_model_metric = dashboard.filtered_df.groupby('Car Model')['Sale Price'].sum().nlargest(10).reset_index()
            fig = go.Figure(data=go.Pie(
                labels=car_model_metric['Car Model'], values=car_model_metric['Sale Price'],
                marker_colors=['#D3D3D3', '#A9A9A9', '#808080', '#606060', '#4A4A4A', '#3A3A3A', '#2A2A2A', '#1C1C1C']
            ))
            fig.update_layout(template='plotly_dark', plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400)
            model_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vehicle Sales</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .row { display: flex; justify-content: space-between; }
                .column { flex: 50%; padding: 10px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Vehicle Sales</h1>
                <div class="row">
                    <div class="column"><h3>Car Make</h3>{}</div>
                    <div class="column"><h3>Car Model</h3>{}</div>
                </div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(make_html, model_html)
    except Exception as e:
        logging.error(f"Error rendering Vehicle Sales page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/model')
def model():
    try:
        if dashboard.filtered_df.empty:
            table_html = "<p style='color:white'>No data available for Model Comparison</p>"
        else:
            model_comparison = dashboard.filtered_df.groupby(['Car Make', 'Car Model']).agg({
                'Sale Price': ['mean', 'sum', 'count'],
                'Commission Earned': 'mean'
            }).round(2)
            model_comparison.columns = ['Avg Sale Price', 'Total Sales', 'Transaction Count', 'Avg Commission']
            model_comparison = model_comparison.reset_index()
            table_html = generate_table_html(
                model_comparison,
                ['Car Make', 'Car Model', 'Avg Sale Price', 'Total Sales', 'Transaction Count'],
                {
                    'Avg Sale Price': lambda x: f"${x:,.2f}",
                    'Total Sales': lambda x: f"${x:,.2f}",
                    'Transaction Count': lambda x: str(int(x))
                }
            )
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Model Comparison</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Model Comparison</h1>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(table_html)
    except Exception as e:
        logging.error(f"Error rendering Model Comparison page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/trends')
def trends():
    try:
        if dashboard.filtered_df.empty:
            trend_html = "<p style='color:white'>No data available for Trends</p>"
            qoq_html = "<p style='color:white'>No data available for QoQ</p>"
            animated_html = "<p style='color:white'>No data available for Monthly Trend</p>"
        else:
            trend_df = dashboard.filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trend_df['Quarter'], y=trend_df['Sale Price'], name='Sale Price', line=dict(color='#A9A9A9')))
            fig.add_trace(go.Scatter(x=trend_df['Quarter'], y=trend_df['Commission Earned'], name='Commission', line=dict(color='#808080')))
            fig.update_layout(
                xaxis_title='Quarter', yaxis_title='Amount ($)', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            trend_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

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

            monthly_trend = dashboard.filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(go.Bar(x=monthly_trend['Month'], y=monthly_trend['Sale Price'], name='Sale Price', marker_color='#A9A9A9'))
            fig.add_trace(go.Bar(x=monthly_trend['Month'], y=monthly_trend['Commission Earned'], name='Commission', marker_color='#808080'))
            fig.update_layout(
                xaxis_title='Month', yaxis_title='Amount ($)', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'),
                barmode='group', height=400
            )
            animated_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trends</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Trends</h1>
                <h3>Quarter-over-Quarter Trend</h3>
                <div>{}</div>
                <h3>Quarter-over-Quarter % Change</h3>
                <div>{}</div>
                <h3>Monthly Trend</h3>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(trend_html, qoq_html, animated_html)
    except Exception as e:
        logging.error(f"Error rendering Trends page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/hr')
def hr():
    try:
        hr_html = generate_table_html(
            dashboard.hr_data,
            dashboard.hr_data.columns,
            {
                'Salary (USD)': lambda x: f"${x:,.2f}",
                'Join Date': lambda x: x.strftime('%Y-%m-%d')
            }
        )
        if dashboard.hr_data.empty:
            perf_html = "<p style='color:white'>No data available for Performance</p>"
            hours_html = "<p style='color:white'>No data available for Hours</p>"
        else:
            fig = go.Figure(data=[go.Histogram(x=dashboard.hr_data['Performance Score'], nbinsx=5, marker_color='#A9A9A9')])
            fig.update_layout(
                xaxis_title='Performance Score', yaxis_title='Count', template='plotly_dark',
                plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            perf_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

            total_hours = dashboard.time_log_data.groupby('Employee ID')['Total Hours'].sum().reset_index()
            fig = go.Figure(data=[go.Bar(x=total_hours['Employee ID'], y=total_hours['Total Hours'], marker_color='#A9A9A9')])
            fig.update_layout(
                xaxis_title='Employee ID', yaxis_title='Total Hours', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            hours_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)
        time_log_html = generate_table_html(
            dashboard.time_log_data,
            dashboard.time_log_data.columns,
            {'Date': lambda x: x.strftime('%Y-%m-%d')}
        )
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>HR Overview</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>HR Overview</h1>
                <h3>Employee Information & Salary</h3>
                <div>{}</div>
                <h3>Performance Distribution</h3>
                <div>{}</div>
                <h3>Employee Time Log</h3>
                <div>{}</div>
                <h3>Total Logged Hours per Employee</h3>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(hr_html, perf_html, time_log_html, hours_html)
    except Exception as e:
        logging.error(f"Error rendering HR Overview page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/inventory')
def inventory():
    try:
        inventory_html = generate_table_html(
            dashboard.inventory_data,
            dashboard.inventory_data.columns,
            {'Unit Cost': lambda x: f"${x:,.2f}"}
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
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Inventory</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Inventory</h1>
                <div>{}</div>
                <h3>Low Stock Alert</h3>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(inventory_html, low_stock_html)
    except Exception as e:
        logging.error(f"Error rendering Inventory page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/crm')
def crm():
    try:
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
            fig = go.Figure(data=[go.Scatter(x=line_chart_data['Contact Date'], y=line_chart_data['Satisfaction Score'], mode='lines+markers', line=dict(color='#A9A9A9'))])
            fig.update_layout(
                xaxis_title='Contact Date', yaxis_title='Satisfaction Score', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            time_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

            interaction_types = dashboard.crm_data['Interaction Type'].unique()
            fig = go.Figure()
            for itype in interaction_types:
                fig.add_trace(go.Box(y=dashboard.crm_data[dashboard.crm_data['Interaction Type'] == itype]['Satisfaction Score'], name=itype))
            fig.update_layout(
                xaxis_title='Interaction Type', yaxis_title='Satisfaction Score', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            type_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CRM</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>CRM</h1>
                <div>{}</div>
                <h3>Satisfaction Over Time</h3>
                <div>{}</div>
                <h3>Satisfaction Score by Interaction Type</h3>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(crm_html, time_html, type_html)
    except Exception as e:
        logging.error(f"Error rendering CRM page: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/demo')
def demo():
    try:
        demo_html = generate_table_html(
            dashboard.demo_data,
            dashboard.demo_data.columns,
            {'Purchase Amount': lambda x: f"${x:,.2f}"}
        )
        if dashboard.demo_data.empty:
            age_html = "<p style='color:white'>No data available for Age Distribution</p>"
            region_html = "<p style='color:white'>No data available for Purchase Amount</p>"
        else:
            age_counts = dashboard.demo_data['Age Group'].value_counts().reset_index()
            age_counts.columns = ['Age Group', 'Count']
            fig = go.Figure(data=[go.Bar(x=age_counts['Age Group'], y=age_counts['Count'], marker_color='#A9A9A9')])
            fig.update_layout(
                xaxis_title='Age Group', yaxis_title='Count', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            age_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

            regions = dashboard.demo_data['Region'].unique()
            fig = go.Figure()
            for region in regions:
                fig.add_trace(go.Box(y=dashboard.demo_data[dashboard.demo_data['Region'] == region]['Purchase Amount'], name=region))
            fig.update_layout(
                xaxis_title='Region', yaxis_title='Purchase Amount ($)', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            region_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Demographics</title>
            <style>
                body { background-color: #1C1C1C; color: #D3D3D3; font-family: Arial, sans-serif; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                a { color: #A9A9A9; text-decoration: none; }
                a:hover { color: #FFFFFF; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Demographics</h1>
                <div>{}</div>
                <h3>Age Group Distribution</h3>
                <div>{}</div>
                <h3>Purchase Amount by Region</h3>
                <div>{}</div>
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
        return html.format(demo_html, age_html, region_html)
    except Exception as e:
        logging.error(f"Error rendering Demographics page: {str(e)}")
        return f"Error: {str(e)}", 500

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
