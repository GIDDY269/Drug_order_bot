from Data_Ingestion.SQL_Database import create_sql_connection
from Data_Ingestion.schema import CreateScrapeSchema
from PIL import Image
import requests
from io import BytesIO
from langchain.agents import tool
import pyodbc




def extract_image_from_database(drug_name:str):

    # create an sql connection
    'To display images'

    cnxn,cursor = create_sql_connection()


    try:
        select_query = 'SELECT image FROM DRUG_ORDER_CHATBOT1 WHERE name = ?'
        cursor.execute(select_query, (drug_name,))
        # Fetch the result
        result = cursor.fetchone()
    
        if result:
            try:
                get_image = requests.get(result[0])
            
                image = BytesIO(get_image.content)
                return {f'This is what the image of the drug {drug_name} looks like':image}
            
            except requests.exceptions.RequestException as e:
                return {f"Error retrieving image: {e}": 'message'}     
        else:
            return {'No image for this drug for now':'message'}
        
    except (Exception, pyodbc.Error) as err:  # Catch general and database errors
        return {" can not retrieve image right now because of Database error: {err}":'message'}
            
    finally:
        cnxn.close()



if __name__ == '__main__':
    extract_image_from_database('Clearblue Pregnancy Test *1 Tests')