import pandas as pd
import datetime
import boto3
from io import StringIO
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr


# please replace the df data source from csv file to your streaming source

def queryDynamo(chosen_option):
    ddb = boto3.resource('dynamodb', region_name='us-east-2')
        table = ddb.Table('disneyridepreds')

    response = table.scan(
    FilterExpression=Attr('ds').begins_with(chosen_option)
    )

    data = response['Items']
    df = pd.DataFrame.from_dict(data)

    df['Hour']=df['ds'].str[-8:]
    df['Hour']=df['Hour'].str[:2]
    df['Date']=df['ds'].str[:10]
    df['yhat']=df['yhat'].str.replace("'","")
    df['yhat']=df['yhat'].astype(float)
    # df["Date"] = pd.to_datetime(df["Date"]).dt.strftime('%Y-%m-%d')
    # df["Hourstr"]=df["Hour"].astype(str)

    df["Hourstr"]=df["Hour"]+':00-'+df["Hour"]+':59'
    # st.header('Disneyland Ride Planner')
    return df


with st.sidebar:
    image = Image.open('dateicon.png')

    st.image(image, width=30)
    d = st.date_input(
        'Select your visit date',
        # value=None
        # label_visibility="collapsed"
        datetime.date(2021, 12, 15)
    )

    # st.write('You've selected f:', d.strftime('%Y-%m-%d'))


# @st.cache
# def agg(dfx, date):
# df2 = df[df['Date'] == d.strftime('%Y-%m-%d')]

df2 = queryDynamo(d)

df2["Hourstr"]=df2["Hour"].astype(str)
df2["Hourstr"]=df2["Hourstr"]+':00-'+df2["Hourstr"]+':59'
df2["Hour"]=df2["Hour"].astype(int)
df2_2=df2.copy()
df2_2 = df2_2.groupby(["Hour",'ride_name']).agg({'yhat': ['mean']})
df2_2 = df2_2.reset_index()
df2_2.columns=['Hour','Ride','Wait Time']
df2_2['Ride'] = df2_2['Ride'].str.replace('.csv', '')
df2_2['Ride'] = df2_2['Ride'].str.replace('_', ' ')
#
# df2_2=df2.groupby(['Hour','ride']).size()
# df2_2=df2_2.reset_index()

#########################################
header='Park Hourly Traffic Projection on '+d.strftime('%Y-%m-%d')
st.subheader(header)
hist_values = np.histogram(
    df2['Hour'], bins=24, range=(0, 24))[0]

st.bar_chart(hist_values, width=350, height=300)

######################

header='Time Planner'
st.subheader(header)

option = st.selectbox(
    'Select a Ride',
     df2_2['Ride'].unique())
df2_3= df2_2[df2_2['Ride'] == option]

st.bar_chart(df2_3,x='Hour',y='Wait Time', width=350, height=300)
########################################################

header='Ride Planner'
st.subheader(header)

option2 = st.selectbox(
    'Select a Time',
     df2["Hourstr"].unique())
df2_4= df2[df2['Hourstr'] == option2]
df2_4 = df2_4.groupby(['ride_name']).agg({'yhat': ['mean']})

# print('df2_4',df2_4.head())

df3 = df2_4.reset_index()
df3.columns = ['Ride', 'Wait Time']
df3['Ride'] = df3['Ride'].str.replace('.csv', '')
df3['Ride'] = df3['Ride'].str.replace('_', ' ')

# print('df3',df3.head())
df3['Rank'] = df3['Wait Time'].rank(ascending=True)
df3['Rank']=df3['Rank'].astype(int)
df3=df3.sort_values(by='Rank')

########################################################
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# Display a static table
st.table(df3)
#########################################################
