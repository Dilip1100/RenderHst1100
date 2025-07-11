import os
import tempfile
import logging
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from flask import Flask, render_template, request, Response
from faker import Faker
from datetime import datetime
import random
import json

# Configure Plotly for offline rendering
pio.templates.default = "plotly_dark"

# Set up logging
log_dir = os.path.join(tempfile.gettempdir(), "AutomotiveDashboard")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "dashboard.log")
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Flask app
app = Flask(__name__, template_folder="templates")

# Initialize Faker
fake = Faker()

class AutomotiveDashboard:
    def __init__(self):
        self.df = self.generate_sales_data()
        logging.info("Sales data generated successfully")
        self.hr_data, self.inventory_data, self.crm_data, self.demo_data, self.time_log_data = self.generate_fake_data()

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
            dates = pd.date_range(start="2023-01-01", end="2025-07-07", freq="D")
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
            time_log_data = pd.DataFrame({
                "Employee ID": np.random.choice(hr_data["Employee ID"], size=30, replace=True),
                "Date": pd.date_range(endieversend_date=end_date).tolist(),
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
            end_date = datetime.strptime("2025-07-07", "%Y-%m-%d")
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

@app.route('/')
def index():
    salespeople = ['All'] + sorted(dashboard.df['Salesperson'].dropna().unique())
    car_makes = ['All'] + sorted(dashboard.df['Car Make'].dropna().unique())
    car_years = ['All'] + sorted(dashboard.df['Car Year'].dropna().astype(str).unique())
    metrics = ["Sale Price", "Commission Earned"]
    return render_template('index.html', salespeople=salespeople, car_makes=car_makes, car_years=car_years, metrics=metrics)

@app.route('/kpi', methods=['GET', 'POST'])
def kpi():
    try:
        filtered_df = dashboard.df.copy()
        if request.method == 'POST':
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

        if filtered_df.empty:
            chart_html = "<p style='color:white'>No data available for KPI Trend</p>"
        else:
            kpi_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Sale Price'], name='Sale Price', line=dict(color='#A9A9A9')))
            fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Commission Earned'], name='Commission', line=dict(color='#808080')))
            fig.update_layout(
                xaxis_title='Month', yaxis_title='Amount ($)', template='plotly_dark',
                xaxis=dict(tickangle=45), plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'), height=400
            )
            chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)

        total_sales = f"${filtered_df['Sale Price'].sum():,.0f}"
        total_comm = f"${filtered_df['Commission Earned'].sum():,.0f}"
        avg_price = f"${filtered_df['Sale Price'].mean():,.0f}" if not filtered_df.empty else "$0"
        trans_count = f"{filtered_df.shape[0]:,}"

        return render_template('kpi.html', chart_html=chart_html, total_sales=total_sales, total_comm=total_comm, avg_price=avg_price, trans_count=trans_count)

    except Exception as e:
        logging.error(f"Error rendering KPI chart: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/download_csv', methods=['POST'])
def download_csv():
    try:
        filtered_df = dashboard.df.copy()
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
    app.run(debug=True)