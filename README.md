# COVID-19 Data Integration, Analysis, and Visualization Platform

## Description

This project is designed to provide an interactive web dashboard to visualize COVID-19 statistics and allow users to query the database while being able to show database schema. It allows users to explore the relationship between the health crisis and the well-being of different countries. The dashboard is built using Flask, Plotly for visualization, and connected to Snowflake for querying the database and MongoDB for storing user comments.

## Features

- Interactive fixed-charts and graphs to explore COVID-19 data.
- Analyzing the COVID-19 impacts.
- User comments section for community engagement.
- Caching for improved performance.

## Technologies

- Python 3.11
- Flask
- Snowflake
- MongoDB
- Pandas
- Plotly, Plotly Express

## Running the App / Dependencies

- Create a virtual environment in the folder with the command:  python3 -m venv venv
- Before running the app you should get these libraries. Run the command in your terminal:
      pip install -r requirements.txt

## Configuration

Update the config.py file with your own Snowflake and MongoDB credentials:

<p>USER = 'your_snowflake_username'</p>
<p>PASSWORD = 'your_snowflake_password'</p>
<p>ACCOUNT = 'your_snowflake_account'</p>
<p>WAREHOUSE = 'your_snowflake_warehouse'</p>
<p>DATABASE = 'your_snowflake_database'</p>
<p>SCHEMA = 'your_snowflake_schema'</p>
<p>ROLE = 'your_snowflake_role'</p>
<p>MONGODB_URI='your_mongodb_uri'</p>

## Usage

To run the Flask application, execute:

    python app.py

The application will start and be accessible at http://127.0.0.1:5000/.

## Contact

If you want to contact me you can reach me at alican@can.biz.tr
