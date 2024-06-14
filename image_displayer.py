#from Data_Ingestion.SQL_Database import create_sql_connection
#from Data_Ingestion.schema import CreateScrapeSchema
from PIL import Image
import requests
from io import BytesIO

import pandas as pd




def extract_image_from_database(drug_name:str):

    # create an sql connection
    'To display images'

    #cnxn,cursor = create_sql_connection()


    try:
        data = pd.read_csv('Data_Ingestion\data2.csv')
        sub_data = data[data['Product']==drug_name]
        image_url = sub_data['Image_URL'].iloc[0]
        
        #select_query = 'SELECT image FROM DRUG_ORDER_CHATBOT1 WHERE name = ?'
        #cursor.execute(select_query, (drug_name,))
        # Fetch the result
        #result = cursor.fetchone()
    
        if image_url:
            try:
                get_image = requests.get(image_url)
            
            
                image = BytesIO(get_image.content)
                
                
                return {f'This is what the image of the drug {drug_name} looks like':image}
            
            except requests.exceptions.RequestException as e:
                return {f"Error retrieving image: {e}": 'message'}     
        else:
            return {'No image for this drug for now':'message'}
    except Exception as e :
        return {'Can not retrieve image' : 'message'}
        



if __name__ == '__main__':
    extract_image_from_database('Listerine Mouthwash 250Ml(Cool Mint)')