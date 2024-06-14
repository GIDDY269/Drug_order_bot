import pyodbc
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from Data_Ingestion.schema import CreateScrapeSchema
from dotenv import load_dotenv
import os
import pandas as pd
import streamlit as st
load_dotenv()

database = st.secrets['DATABASE']
server = st.secrets['SERVER']
UID = st.secrets['UID']
PWD = st.secrets['PWD']


#create a connection with database
def create_sql_connection():
    print('CREATING SQL CONNECTION')
    connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};' + f'SERVER={server},1433;;DATABASE={database};UID={UID};PWD={PWD};'
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    return connection,cursor



def sql_table():
    print('CREATING SQL DATABASE TALE')
    Create_table = '''
        CREATE TABLE DRUG_ORDER_CHATBOT1 (
            Id INT PRIMARY KEY IDENTITY(1,1),
            name VARCHAR(MAX),
            section VARCHAR(MAX),
            category VARCHAR(MAX),
            image VARCHAR(MAX),
            price VARCHAR(MAX),
            
        )
        '''

    try:
        cnxn,cursor = create_sql_connection()
        cursor.execute(Create_table)
        cnxn.commit()

    except pyodbc.Error as e:
        # Check if the error is due to the table already existing (error code 2714)
        if e.args[0] == '42S01' and 'already an object named' in str(e):
            print("Table DRUG_ORDER_CHATBOT1 already exists. Using existing table.")
        else:
            raise  # Re-raise the exception if it's not the expected one

    finally:
        cnxn.close()


def insert_data(data):
    print('INSERTING DATA INTO TABLE')
    cnxn,cursor = create_sql_connection()
    try:
        # Construct and execute the insert query
        insert_query = f"INSERT INTO [DRUG_ORDER_CHATBOT1] ({', '.join(data.keys())}) VALUES ({', '.join(['?']*len(data.values()))})"
        cursor.execute(insert_query,list(data.values()))
        cnxn.commit()
    finally:
        cnxn.close()

def read_data_from_database():
    print('reading data')
    cnxn,cursor = create_sql_connection()
    try:
        read_query = 'SELECT * FROM DRUG_ORDER_CHATBOT1'
        cursor.execute(read_query)
        data = cursor.fetchall()
        columns = ['ID', 'Product', 'Category', 'Subcategory', 'Image_URL', 'Price']
        df = pd.DataFrame(columns=columns)

        for int,row in enumerate(data):
            df.loc[int,:] = row
        df['Price'] = df['Price'].str.replace('?','#')
        df.set_index('ID',drop=True,inplace=True)
        path = 'data2.csv'
        df.to_csv(f'Data_Ingestion/{path}',encoding='utf-8')
        return f'Data_Ingestion/{path}'

    except pyodbc.Error as e:
        print(f'This error occured {e}')
    finally:
        cnxn.close()







