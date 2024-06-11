import os
from dotenv import load_dotenv,find_dotenv
load_dotenv()
import json
from datetime import datetime
from typing import List,Optional
import time
from PIL import Image
from io import BytesIO

## tools 
from image_displayer import extract_image_from_database
from order_automation import order_automation
from RAG import RetrievalAugmentGen

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.pydantic_v1 import BaseModel,Field
from langchain_core.prompts import (HumanMessagePromptTemplate,
                                    MessagesPlaceholder)
from langchain_core.messages import HumanMessage,ToolMessage
from langchain_groq.chat_models import ChatGroq
from langchain_core.exceptions import LangChainException

import streamlit as st




rag = RetrievalAugmentGen()


# Function to display the image
def display_image(image_bytes):
    image = Image.open(image_bytes)
    return image


# PROCESS CHAT MESSAGES
def process_chat(model,user_input,chat_history):

    response = model.invoke(
        {
            'chat_history' : chat_history,
            'input' : user_input
        }
    )
    return response

# /// TOOLS INPUT SCHEMAS

class InnerOrderAutoInput(BaseModel):
    name:str = Field(description='name of the drug to be order')
    NumOrder:int = Field(description='Number of order to make') 

class OrderAutoTool(BaseModel):
    'To make orders on the website'
    item : List[InnerOrderAutoInput] = Field(description='A list that contains the drug name and number of order')

class ImageDisplayerTool(BaseModel):
    '''To display the images or pictures of the product, always return the response when done'''
    drug_name:str = Field(...,description='Name of the drug, whose image is to be displayed')

class InventoryTool(BaseModel):
    'To check inventory, get list of drugs and snacks  available and search for information about product,their prices or description in the store. Note use this to answer questions and return the exact name in the reach, do not change anything. if you don\'t know , say you don\'t know.'
    user_query:str = Field(description='user query or input')


#/// CONVERTING TO FUNCTION DECLARATION OBJECT

order_fun = convert_to_openai_function(OrderAutoTool)
display_fun = convert_to_openai_function(ImageDisplayerTool)
simi_fun = convert_to_openai_function(InventoryTool)

#  CREATE CHAT TEMPLATE

system = (
    '''
        you are a very chatty,compassionate and friendly drug store assistant for glovo.Your job is to provide excellent service to customers  and answer questions concerning drugs,snacks in the store,display images amd place drug orders . \n\n
        You should be very detailed when answering question concerning drugs or any other product in the store, like the price or any other description.

        Note: Very important,use the exact name of the drugs return by the inventory tool, do not modify anything, leave the asterisks and brackets as they are. \n
        for example :  Snickers Chocolate 80G * 24 for Snickers Chocolate 80G or Crepe Bandage for Crepe Bandage 10Cm X 4.5M(M/S) . Take this very seriously, on no condition should you do otherwise.

        you have been provide with 3 tools to achieve this task. Use the response of the tool give message back to the user:
        use only one and ensure to return a text response back to the user.
       
    '''
)


prompt = ChatPromptTemplate.from_messages(
    [ 
        ('system' , system),


        MessagesPlaceholder(
            variable_name="chat_history"
        ), # to store chat memory

        HumanMessagePromptTemplate.from_template(
           '{input}'
        )
    ]
)

# INITIATE LLM AND BIND TOOLS
chat_model = ChatGroq(
             model= 'llama3-70b-8192',
             api_key=os.getenv('GROQ_KEY'),
             temperature=0,
             max_retries=5
        )

chat_with_tools = chat_model.bind_tools(tools=[order_fun,display_fun,simi_fun]) 


chain =  prompt | chat_with_tools



# /// SETUP STREAMLIT APP

st.set_page_config(
    page_title="DRUG ORDER BOT",
    page_icon="images (4).jpeg",
    layout="wide",
)

col1, col2 = st.columns([8, 1])
with col1:
    st.title("DRUG ORDER BOT")
with col2:
    st.image("images (4).jpeg")

st.subheader("Powered by Function Calling in LLAMA 3")


# INITIALIZE SESSION_STATE HISTORY TO STORE CHAT HISTORY FOR THE MODEL AND HISTORY TO USED TO PERSIST CHAT HISTORY ON THE APP\n  
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [] 

if "messages" not in st.session_state:
    st.session_state.messages = []



for message in st.session_state.messages: #display content on the streamlit ui
    with st.chat_message(message["role"]):
        if message['role'] == 'image':
            st.image(message['content'],width=200,clamp=True)
        else:
            st.markdown(message["content"])    
            

if user_input := st.chat_input('How can i help you today........?',key='User_input'):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message('assistant'):
    
        response = process_chat(chain,user_input,st.session_state.chat_history)
        
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        st.session_state.chat_history.append(response)

        print(response)
        print(response.additional_kwargs)

        if response.content != '' : 
  
            st.markdown(response.content)

            st.session_state.messages.append({"role": "assistant", "content": response.content})

        if response.content == '':
            api_requests_and_responses = []
            backend_details = ''
           
            try:
                params = {}
                # Extracting information
                tool_calls = response.additional_kwargs.get('tool_calls', [])
                for call in tool_calls:
                    function_id = call.get('id')
                    function = call.get('function', {})
                    function_name = function.get('name')
                    function_arg = json.loads(function.get('arguments'))
              
                print(function_name)
                print(function_arg)
                #  EXTRACT THE PARAMETERS TO BE PASSED TO THE FUNCTIONS
                for key,value in function_arg.items():
                    params[key] = value
                    print(function_name)
                    print(params)
                    print(params[key])
                # PERFORMS THE FUNCTION CALL OUTSIDE THE LLM MODEL
                if function_name == 'InventoryTool':
                    with st.status('CHECKING STORE DATABASE',expanded=True) as status:
                        api_response = rag.retriever(params[key])
                        status.update(label='INFORMATION RETRIEVED',state='complete',expanded=False)
                    
                if function_name == 'OrderAutoTool':
                    with st.status('PLACING ORDER FOR YOU',expanded=True) as status:
                        api_response = order_automation(params[key])
                        status.update(label='PROCESS COMPLETED',state='complete',expanded=False)

                    
                if function_name == 'ImageDisplayerTool':
                    with st.status('RETRIEVING IMAGE FROM DATABASE',expanded=True) as status:
                        api_response = extract_image_from_database(params[key])
                        status.update(label='IMAGE RETRIEVED',state='complete',expanded=False)
                    
    
                # PARSE THE RESPONSE OF THE API CALLS BACK INTO THE MODEL
                for k,v in api_response.items(): # check is reponse contains bytes object
                    if isinstance(v,BytesIO): 
                        image = display_image(v)
                        st.image(image=image,width=200)
                        response = process_chat(chain,ToolMessage(content=k,name=function_name,tool_call_id=function_id),st.session_state.chat_history)
                        print('======================================')
                        print(response)
                        st.markdown(response.content)
                        
                        
                    else :
                        response = process_chat(chain,ToolMessage(content=k,name=function_name,tool_call_id=function_id),st.session_state.chat_history)
                        print('======================================')
                        print(response)
                        st.markdown(response.content)
                
                # APPEND THE FUNCTION RESPONSE AND AI RESPONSE TO BOTH THE CHAT_HISTORY AND MESSAGE HISTORY FOR STREAMLIT  
                st.session_state.chat_history.append(ToolMessage(content=k,name=function_name,tool_call_id=function_id)) # append tool response
                st.session_state.chat_history.append(response)
                st.session_state.messages.append({"role": "assistant", "content": response.content})
                st.session_state.messages.append({'role':'image','content':image})
            
            except (Exception,LangChainException) as e:
                print(f"Error: {e}")
                   
    




        



print(st.session_state.chat_history)
print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
print(st.session_state.messages)
print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')
#print(st.session_state.images_loaded)





