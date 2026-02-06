from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

try:
    df = pd.read_csv('csv/Motor_Vehicle_Collisions_-_Crashes.csv', low_memory=False)
except FileNotFoundError:
    print("CSV file not found. Please check the file path.")
    df = pd.DataFrame()  

@app.route('/')
def home():
    return render_template('index.html')



#para ini sya sa data sa una nga chart
def read_death():
    if df.empty:
        return {"labels": [], "datasets": []}

    try:
        df_filtered = df.copy()

        df_filtered["NUMBER OF PERSONS KILLED"] = pd.to_numeric(df_filtered["NUMBER OF PERSONS KILLED"], errors="coerce")
        df_filtered["CRASH DATE"] = pd.to_datetime(df_filtered["CRASH DATE"], errors="coerce")
        df_filtered = df_filtered.dropna(subset=["NUMBER OF PERSONS KILLED", "CRASH DATE"])

        df_filtered["YEAR_MONTH"] = df_filtered["CRASH DATE"].dt.to_period('M').dt.to_timestamp()

        df_grouped = df_filtered.groupby("YEAR_MONTH", as_index=False)["NUMBER OF PERSONS KILLED"].sum()

        df_grouped = df_grouped.sort_values("YEAR_MONTH")

        df_grouped = df_grouped.nlargest(19, "NUMBER OF PERSONS KILLED")
        df_grouped["NUMBER OF PERSONS KILLED"] = df_grouped["NUMBER OF PERSONS KILLED"]

        df_grouped = df_grouped.sort_values("YEAR_MONTH")

        return {
            "labels": df_grouped["YEAR_MONTH"].dt.strftime('%Y-%m').tolist(),
            "datasets": [{
                "label": 'Accident Death Rate',
                "data": df_grouped["NUMBER OF PERSONS KILLED"].tolist(),
            }]
        }
    except Exception as e:
        print(f"Error in read_death: {e}")
        return {"labels": [], "datasets": []}

#same ra pud diri

#sa diri pud same ra sa explanation sa igbaw
def read_crash():
    try:
        df = pd.read_csv('csv/Motor_Vehicle_Collisions_-_Vehicles.csv')

        df.columns = df.columns.str.strip()
        df = df.nlargest(10, 'PRE_CRASH_NUM')

        required_columns = {"CRASH_DATE", "PRE_CRASH_NUM"}
        if not required_columns.issubset(df.columns):
            missing_cols = required_columns - set(df.columns)
            print(f"Missing columns: {missing_cols}")
            return {"error": f"Missing columns: {missing_cols}"}

        df["PRE_CRASH_NUM"] = pd.to_numeric(df["PRE_CRASH_NUM"], errors="coerce").fillna(0)
        df["CRASH_DATE"] = pd.to_datetime(df["CRASH_DATE"], errors="coerce")

        df_filtered = df.dropna(subset=["CRASH_DATE"])

        df_filtered = df_filtered.sort_values(by="CRASH_DATE")

        return {
            "labels": df_filtered["CRASH_DATE"].dt.strftime('%Y-%m-%d').tolist(),
            "datasets": [{
                "label": 'Pre-Crash Events',
                "data": df_filtered["PRE_CRASH_NUM"].tolist(),
            }]
        }

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {"error": "Failed to process crash data"}

#ug diri
def read_insights():
    df = pd.read_csv('csv/Motor_Vehicle_Collisions_-_Crashes.csv')
    df = df.nlargest(4,'data')
    
    return {
        "labels": df['insights'].tolist(), #ini sya kay para sa label name or name sang country
        "datasets": [{
            "label": 'Safety Insights',
            "data": df['data'].tolist(), #ini sya kay para sa data sa 2022 na growth population

        }]
    }

@app.route('/api/chart-data/insights', methods=['GET'])
def insights_chart():
    return jsonify(read_insights())

@app.route('/api/chart-data/crash', methods=['GET'])
def crash_chart():
    return jsonify(read_crash())


@app.route('/api/chart-data/death', methods=['GET'])
def death_chart():
    return jsonify(read_death())



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
