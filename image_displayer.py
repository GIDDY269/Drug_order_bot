
import requests
from io import BytesIO
import pandas as pd



def extract_image_from_database(drug_name:str):

    'To display images'
    
    data = pd.read_csv('Data_Ingestion/data2.csv')
    sub_data = data[data['Product']==drug_name]
    image_url = sub_data['Image_URL'].iloc[0]
        

    try:
        get_image = requests.get(image_url)
        image = BytesIO(get_image.content)
        return {f'This is what the image of the drug {drug_name} looks like':image}
            
    except requests.exceptions.RequestException as e:
        return {f"Error retrieving image, could not place order: {e}": 'message'}     
   
        

