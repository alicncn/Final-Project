import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_caching import Cache
import pandas as pd
import plotly
import plotly.express as px
from db_connections import get_mongodb_connection, get_snowflake_connection
from query_functions import get_schema_info

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'}) 

@app.route('/', methods=['GET','POST'])
@cache.cached(timeout=300)
def home():
    graphs_json = {}

    # Connect to Snowflake
    ctx = get_snowflake_connection()
    cur = ctx.cursor()

    try:
        # Query for the countries bar chart
        cur.execute("SELECT DATE, NO_OF_COUNTRIES FROM DAY_WISE ORDER BY DATE")
        countries_data = cur.fetchall()
        df_countries = pd.DataFrame(countries_data, columns=['DATE', 'NO_OF_COUNTRIES'])
        fig_countries = px.bar(
            df_countries,
            x='DATE',
            y='NO_OF_COUNTRIES',
            title='Number of Countries Reporting Each Day',
            width=700
        )
        graphs_json['countries_bar_chart'] = json.dumps(fig_countries, cls=plotly.utils.PlotlyJSONEncoder)

        # Query for scatter plot
        cur.execute("SELECT COUNTRY_OR_REGION, HEALTHY_LIFE_EXPECTANCY FROM WORLD_HAPPINESS_2019")
        happiness_data = cur.fetchall()
        df_happiness = pd.DataFrame(happiness_data, columns=['COUNTRY_OR_REGION', 'HEALTHY_LIFE_EXPECTANCY'])
        cur.execute("SELECT COUNTRY_REGION, DEATHS_100_CASES, WHO_REGION FROM COUNTRY_WISE_LATEST")
        latest_data = cur.fetchall()
        df_latest = pd.DataFrame(latest_data, columns=['COUNTRY_REGION', 'DEATHS_100_CASES', 'WHO_REGION'])
        merged_df = pd.merge(
            df_happiness,
            df_latest,
            left_on='COUNTRY_OR_REGION',
            right_on='COUNTRY_REGION'
        )
        fig_scatter = px.scatter(
            merged_df,
            x='HEALTHY_LIFE_EXPECTANCY',
            y='DEATHS_100_CASES',
            title='Healthy Life Expectency vs. Death / 100 Cases',
            color='WHO_REGION',
            hover_data=['COUNTRY_REGION'],
            width=900
        )
        graphs_json['scatter_plot'] = json.dumps(fig_scatter, cls=plotly.utils.PlotlyJSONEncoder)

        # Query for WHO region charts
        query = """
        SELECT WHO_REGION, SUM(CONFIRMED) AS TOTAL_CONFIRMED, SUM(DEATHS) AS TOTAL_DEATHS, 
               SUM(RECOVERED) AS TOTAL_RECOVERED
        FROM FULL_GROUPED
        GROUP BY WHO_REGION
        ORDER BY WHO_REGION
        """
        cur.execute(query)
        who_region_data = cur.fetchall()
        df_who_region = pd.DataFrame(who_region_data, columns=['WHO_REGION', 'TOTAL_CONFIRMED', 'TOTAL_DEATHS', 'TOTAL_RECOVERED'])
        df_who_region['FATALITY_RATE'] = df_who_region['TOTAL_DEATHS'] / df_who_region['TOTAL_CONFIRMED'] * 100
        df_who_region['RECOVERY_RATE'] = df_who_region['TOTAL_RECOVERED'] / df_who_region['TOTAL_CONFIRMED'] * 100
        fig_who_confirmed = px.bar(df_who_region, y='WHO_REGION', x='TOTAL_CONFIRMED', title='Total Confirmed Cases by WHO Region', orientation='h', color='WHO_REGION',width=700)
        fig_who_deaths = px.bar(df_who_region, y='WHO_REGION', x='TOTAL_DEATHS', title='Total Deaths by WHO Region', orientation='h', color='WHO_REGION', width=700)
        fig_who_fatality = px.bar(df_who_region, y='WHO_REGION', x='FATALITY_RATE', title='Fatality Rate (%) by WHO Region', orientation='h', color='WHO_REGION', width=700)
        fig_who_recovery = px.bar(df_who_region, y='WHO_REGION', x='RECOVERY_RATE', title='Recovery Rate (%) by WHO Region', orientation='h', color='WHO_REGION', width=700)

        graphs_json['who_confirmed'] = json.dumps(fig_who_confirmed, cls=plotly.utils.PlotlyJSONEncoder)
        graphs_json['who_deaths'] = json.dumps(fig_who_deaths, cls=plotly.utils.PlotlyJSONEncoder)
        graphs_json['who_fatality'] = json.dumps(fig_who_fatality, cls=plotly.utils.PlotlyJSONEncoder)
        graphs_json['who_recovery'] = json.dumps(fig_who_recovery, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        ctx.close()

    # Comment submission
    mongo_client = get_mongodb_connection()
    db = mongo_client.covid19_api
    comments_collection = db.comments
    if request.method == 'POST' and 'comment' in request.form:
        user_name = request.form.get('user_name', 'Anonymous')
        comment = request.form.get('comment')
        comment_data = {
            'user_name': user_name,
            'comment': comment,
            'timestamp': datetime.utcnow()
        }
        comments_collection.insert_one(comment_data)
        return redirect(url_for('home'))

    # Retrieve the last 10 comments
    comments = list(comments_collection.find().sort('timestamp', -1).limit(10))

    return render_template('home.html', graphs_json=graphs_json, comments=comments)

@cache.memoize(timeout=300)
@app.route('/results', methods=['POST'])
def show_results():
    query = request.form.get('query')
    rows, columns, error = [], [], None

    if query:
        ctx = get_snowflake_connection()
        cur = ctx.cursor()
        try:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [col[0] for col in cur.description]
        except Exception as e:
            error = str(e)
        finally:
            cur.close()
            ctx.close()

    return render_template('results.html', rows=rows, columns=columns, error=error)

@app.route('/schema', methods=['POST'])
def schema():
    ctx = get_snowflake_connection()
    cur = ctx.cursor()
    try:
        tables_info = get_schema_info(cur)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        ctx.close()
    
    return render_template('schema.html', tables_info=tables_info)


if __name__ == '__main__':
    app.run(debug=True)