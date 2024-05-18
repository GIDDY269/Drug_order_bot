from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
genai.configure(api_key=os.getenv('GEMINI_KEY'))


model = genai.GenerativeModel(model_name='gemini-pro-vision')

def get_image_respone(input_prompt,image):
    '''
    generates responses
    '''
    response = model.generate_content([image[0],input_prompt])
    return response.text 


def get_image_setup(uploaded_file):
    '''
    Gets the image setup for gemini pro vision
    '''

    if uploaded_file:

        bytes_data = uploaded_file.getvalue()
        


        image_part = [
            {
                'mime_type' : uploaded_file.type,
                'data' : bytes_data
            }
        ]

        return image_part
    else:
        raise FileNotFoundError('image not found')
    

def main():
    '''
    TAKES THE DRUG RECIEPTS AND RETURNS THE NAME OF THE DRUG
    ''' 
    uploaded_file = st.file_uploader('choose image',type=['png', 'jpg','jpeg'])
    
    image = ''
    if uploaded_file:
        
        image = Image.open(uploaded_file)
        st.image(image)

        submit = st.button('press')


        input_prompt = '''You are expert pharmacist./n
          you are given an image to get the names of drugs listed in the image,/n
            extract the exact names of the drugs. if no drug name present, say no drug
            note: only extract the names of the drugs alone nothing else
            '''

        if submit:
            image_data = get_image_setup(uploaded_file)
            response = get_image_respone(input_prompt,image_data)

            st.write(response)


if __name__ == '__main__' :

    main()