from flask import Flask, render_template, request
import pandas as pd
import datetime
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])  # estimation
def predict():

    start = datetime.datetime.now().strftime("%Y-%m-%d")
    time_delt = datetime.datetime.now() + datetime.timedelta(days=5)
    end = time_delt.strftime("%Y-%m-%d") 
    d_list = pd.date_range(start, end)
    index_list = [d.strftime("%Y-%m-%d") for d in d_list]

    chosen_option = None

    if request.method == 'POST':
        default_value = 'None Selected'
        chosen_option = request.form.get(
            key='select_Ride',
            default=default_value,
        )
    # filtering data based on 'chosen option

    # try:
    ddb = boto3.resource('dynamodb', region_name='us-east-2')
    table = ddb.Table('disneyridepreds')

    response = table.scan(
    FilterExpression=Attr('ds').begins_with(chosen_option)
    )

    data = response['Items']
    df = pd.DataFrame.from_dict(data)

    df2 = df.groupby(['ds', 'ride_name']).agg({'yhat': ['mean']})
    df2 = df2.reset_index()
    df2.columns = ['hour', 'ride', 'wait']
    df2['rank'] = df2.groupby('ride')['hour'].rank(ascending=True)

    df3 = df2[df2['rank'] < 4]
    df3 = df3.sort_values(by=['ride', 'rank', 'hour'], ascending=True)
    df3['ride'] = df3['ride'].str.replace('.csv', '')
    
    # except:
    #     df3 = pd.DataFrame(
    #         {
    #             'ride': [],
    #             'rank': [],
    #             'hour': [],
    #             'wait_time': []
    #         }
    #     )

    return render_template(
        template_name_or_list='index.html',
        index_list=index_list,
        # prediction=prediction,
        chosen_option=chosen_option,
        tables=[df3.to_html(classes='data')],
        titles=['Time','Ride','Estimate Wait Time','Priority']#df4.columns.values
    )



if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=5000, debug=True)