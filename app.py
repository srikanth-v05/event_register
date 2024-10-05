from flask import Flask, render_template, request, redirect, url_for, flash
import snowflake.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Snowflake connection details
SNOWFLAKE_USER = 'srikanth'
SNOWFLAKE_PASSWORD = 'Srik@2005'
SNOWFLAKE_ACCOUNT = 'mvzaemy-ha30008'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'
SNOWFLAKE_DATABASE = 'WASTE_MANGE'
SNOWFLAKE_SCHEMA = 'DATA'
SNOWFLAKE_ROLE = 'ACCOUNTADMIN'

# Function to connect to Snowflake
def connect_snowflake():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE
    )
    return conn

# Route for the form
@app.route('/')
def index():
    return render_template('su5.html')

# Route to handle form submission and store data in Snowflake
@app.route('/submit', methods=['POST'])
def submit_event():
    if request.method == 'POST':
        try:
            # Get form data
            event_name = request.form['eventName']
            event_date = request.form['eventDate']
            attendees = request.form['attendees']
            event_type = request.form['eventType']
            address = request.form['address']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            waste_estimate = request.form['wasteEstimate']
            vehicles_needed = request.form['vehiclesNeeded']
            personnel_needed = request.form['personnelNeeded']

            # Validate that numeric fields are not empty and are valid numbers
            if not attendees.isdigit() or not vehicles_needed.isdigit() or not personnel_needed.isdigit():
                flash("Please enter valid numeric values for attendees, vehicles, and personnel.", "danger")
                return redirect(url_for('index'))

            try:
                latitude = float(latitude)
                longitude = float(longitude)
                waste_estimate = float(waste_estimate)
            except ValueError:
                flash("Please enter valid decimal values for latitude, longitude, and waste estimate.", "danger")
                return redirect(url_for('index'))

            # Connect to Snowflake
            conn = connect_snowflake()
            cur = conn.cursor()

            # Insert data into the Snowflake table
            insert_query = f"""
            INSERT INTO WASTE_MANGE.DATA.EVENT_WASTE_ESTIMATION (
                EVENT_NAME, EVENT_DATE, ATTENDEES, EVENT_TYPE, ADDRESS, LATITUDE, LONGITUDE, ESTIMATED_WASTE, VEHICLES_NEEDED, PERSONNEL_NEEDED
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_query, (
                event_name, event_date, int(attendees), event_type, address, 
                latitude, longitude, waste_estimate, int(vehicles_needed), int(personnel_needed)
            ))

            # Commit and close connection
            conn.commit()
            cur.close()
            conn.close()

            flash("Event data has been successfully submitted!", "success")
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
