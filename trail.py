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
#from order_scheduler import schedule_orders
from Current_time import get_current_time


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_pydantic_to_openai_function,convert_to_openai_function
from langchain.pydantic_v1 import BaseModel,Field
from langchain_core.prompts import (HumanMessagePromptTemplate,SystemMessagePromptTemplate,
                                    ChatPromptTemplate,
                                    MessagesPlaceholder)
from langchain_core.messages import SystemMessage,HumanMessage,ToolMessage
from langchain.memory import ConversationBufferMemory
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.messages import FunctionMessage
#from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains.llm import LLMChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from langchain_google_genai._enums import HarmBlockThreshold, HarmCategory

import streamlit as st

from RAG import RetrievalAugmentGen
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import StructuredTool


rag = RetrievalAugmentGen()
#rag.document_loader()
#rag.vectore_store()

 

# Function to display the image
def display_image(image_bytes):
    image = Image.open(image_bytes)
    return image




def process_chat(model,user_input,chat_history):

    response = model.invoke(
        {
            'input' : user_input,
            'chat_history' : chat_history
        }
    )
    return response

# /// TOOLS INPUT SCHEMAS

class InnerOrderAutoInput(BaseModel):
    'For making drugs orders'
    name:str = Field(description='name of the drug to be order')
    NumOrder:int = Field(description='Number of order to make') 

class OrderAutoInput(BaseModel):
    'For making drugs orders'
    item : List[InnerOrderAutoInput] = Field(description='A list that contains the drug name and number of order')

class image_displayer_input(BaseModel):
    '''To display the images of the drugs, always return the response when done'''
    drug_name:str = Field(...,description='Name of the drug, whose image is to be displayed')

class similarity_search(BaseModel):
    'search for information about drugs,their prices or description in the store. Note use this to answer questions and return the exact name in the reach, do ot change anything. if you don\'t know , say you don\'t know. user can ask questions like , do you have a dru for 2500?'
    user_query:str = Field(description='user query or input')


#/// CONVERTING TO FUNCTION DECLARATION OBJECT
image_tool = StructuredTool.from_function(
 func= extract_image_from_database,
 name='order func',
 args_schema=OrderAutoInput   
)

tools = [image_tool]

order_fun = convert_to_openai_function(OrderAutoInput)
display_fun = convert_to_openai_function(image_displayer_input)
simi_fun = convert_to_openai_function(similarity_search)
#sche_fun = convert_to_openai_function(MainOrderSchInput)
#cur_fun = convert_to_openai_function(CurTimeInput)

#  CREATE CHAT TEMPLATE



system_prompt = '''You are a compassionate drug store assistant equipped with three specialized tools to provide excellent service to customers, use the context to answer questions\n
                 if you don't know say you don't know

                 {context}




                    '''



prompt = ChatPromptTemplate.from_messages(
    [ 
        SystemMessage(
            content= system_prompt
        ),


        MessagesPlaceholder(
            variable_name="chat_history"
        ), # to store chat memory


        HumanMessagePromptTemplate.from_template(
            '{input}'
        )

    ]
)

# ADDING memmory

#/// INSTANIATING LLM MODEL WITH TOOL and chain
safety_settings =    {
                 HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            }



chat = ChatGoogleGenerativeAI(model='gemini-pro',
                              google_api_key=os.getenv('GEMINI_KEY'),
                              temperature=0,
                              verbose=True,
                              safety_settings=safety_settings)


chat_with_tools = chat.bind_tools(tools=[order_fun,display_fun,simi_fun ]) 




query = 'can you order 2 paracetamol'
chat_with_tools.invoke(query)



chain =prompt | chat_with_tools

chain.invoke('hey')









import requests
from bs4 import BeautifulSoup
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException,StaleElementReferenceException
from SQL_Database import *
from schema import CreateScrapeSchema




def fetch(url):
    response = requests.get(url)
    return response.text

def get_desc(section_url,img_link):
    # FUNCTION TO GET THE DESCRIPTION OF THE DRUGS 
    chrome_options = Options()
    print('set up chrom driver')
    chrome_options.add_argument('--headless')
   # chrome_options.chromedriver_executable = "venv/chromedriver-win64/chromedriver.exe"


    max_attempts = 2
    try:
        driver = Chrome()
        driver.get('https://glovoapp.com' + section_url)
        print('gotten page')
        page_source = driver.page_source
    
        cookie = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='onetrust-close-btn-handler onetrust-close-btn-ui banner-close-button ot-close-icon']"))
        ).click()
       
        elements = WebDriverWait(driver, 50).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tile']//img[contains(@class, 'tile__image store-product-image')]"))
            )
        
        product_list = [] # Initialize an empty list to store dictionaries for each product
        
        for element in elements:
            
            WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='tile']//img[contains(@class, 'tile__image store-product-image')]"))
            )

            element.click()
            driver.implicitly_wait(10)
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
        
            path_element = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#vue-bottom-sheet-shell > div > div.modal--window__top-buttons.modal--window__top-buttons--only-one-on-the-right > svg'))
             ).click()
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            
            driver.implicitly_wait(100)
            name = driver.find_element(By.XPATH,"//h1[@class='product-details__name']").text.strip()
            price = driver.find_element(By.XPATH,"//span[@class='product-price__effective size-large']").text.strip()
            #desc = driver.find_element(By.XPATH, "//div[@class='product-details__description product-details__description--centered']").text.strip()
            image = driver.find_element(By.XPATH,"//*[@id='base-modal']/div/div[2]/div/section/div[1]/div/div/div[1]/div/div/div/div/picture/img").get_attribute('src')

            print(f'{name} : {image}')

            product_dict = {
                'name' : name,
                'price' : price,
              #  'description' : desc,
                'image': image              #img_link['src']
            }
            product_list.append(product_dict)

            print('================================================================================')
            print(product_dict)
            print('===============================================================================')
        
            des_element = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#base-modal > div > div.modal--window__top-buttons.modal--window__top-buttons--only-one-on-the-right > svg'))
            ).click()
            
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException,StaleElementReferenceException) as e:
        print(f"Exception occurred: {type(e).__name__} - {str(e)}")
        product_dict = {}
         
    finally:
        driver.quit()

    return product_list

def main():
    # MAIN SCRAPER FUNCTION
    url = 'https://glovoapp.com/ng/en/lagos/medplus-pharmacy-los/'
    html = fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    print('BEGINING TO SCRAPE DATA')
    for section in soup.find_all('div', class_='store__body__dynamic-content')[1:]:
        header_title_class = ['grid__title', 'carousel__title']
        for title in header_title_class:
            section_name = section.find('h2', class_=title) #gets the section text
            if section_name:
                section_name = section_name.text.strip()
                print(section_name)
                if title == 'grid__title':
                    link = section.find('div', class_='grid__content').find('a').get('href')
                    sub_html = fetch('https://glovoapp.com' + link)
                    sub_soup = BeautifulSoup(sub_html, 'html.parser')
                    for products in sub_soup.find_all('div', class_='tile'):
                        category = sub_soup.find('h2', class_='grid__title').text.strip()
                        img_link = products.find('img')
                    print('Entering get desc function')
                    product_list = get_desc(link, img_link) #get product information
                    for product_dict in product_list:
                        product_dict['section'] = section_name
                        product_dict['category'] = category
                        

                        product_data = CreateScrapeSchema(**product_dict).dict()
                        print(f'after pydantic{product_data}')
                        sql_table()
                        insert_data(product_data)
                else:
                    carousel_content = section.find_all('div', class_='carousel__content__element')
                    for content in carousel_content:
                        link = content.find('a').get('href')
                        sub_html = fetch('https://glovoapp.com' + link)
                        sub_soup = BeautifulSoup(sub_html, 'html.parser')
                        category = sub_soup.find('h2',class_='grid__title').text.strip()
                        print(f'Scraping category {category}')
                        grid_content = sub_soup.find('div',class_ = 'grid__content') 
                        for products in grid_content.find_all('div',class_='tile'):
                            img_link = products.find('img')
                        print('Entering get desc function')
                        product_list = get_desc(link, img_link) #get product information
                        for product_dict in product_list:
                            product_dict['section'] = section_name
                            product_dict['category'] = category
                            print(f'categorised dict {product_dict}')

                            product_data = CreateScrapeSchema(**product_dict).dict()
                            print(f'after pydantic{product_data}')
                            sql_table()
                            insert_data(product_data)
                print('===============================================')
                continue

if __name__ == "__main__":
    main()




def get_desc(section_url,img_link):
    # FUNCTION TO GET THE DESCRIPTION OF THE DRUGS 
    chrome_options = Options()
    print('set up chrom driver')
    chrome_options.add_argument('--headless')
   # chrome_options.chromedriver_executable = "venv/chromedriver-win64/chromedriver.exe"


    max_attempts = 2
    try:
        driver = Chrome()
        driver.get('https://glovoapp.com' + section_url)
        print('gotten page')
        page_source = driver.page_source
    
        cookie = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='onetrust-close-btn-handler onetrust-close-btn-ui banner-close-button ot-close-icon']"))
        ).click()
       
        elements = WebDriverWait(driver, 50).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tile']//img[contains(@class, 'tile__image store-product-image')]"))
            )
        
        product_list = [] # Initialize an empty list to store dictionaries for each product
        
        for element in elements:
            
            WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='tile']//img[contains(@class, 'tile__image store-product-image')]"))
            )

            element.click()
            driver.implicitly_wait(10)
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
        
            path_element = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#vue-bottom-sheet-shell > div > div.modal--window__top-buttons.modal--window__top-buttons--only-one-on-the-right > svg'))
             ).click()
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            
            driver.implicitly_wait(100)
            name = driver.find_element(By.XPATH,"//h1[@class='product-details__name']").text.strip()
            price = driver.find_element(By.XPATH,"//span[@class='product-price__effective size-large']").text.strip()
            #desc = driver.find_element(By.XPATH, "//div[@class='product-details__description product-details__description--centered']").text.strip()
            image = driver.find_element(By.XPATH,"//*[@id='base-modal']/div/div[2]/div/section/div[1]/div/div/div[1]/div/div/div/div/picture/img").get_attribute('src')

            print(f'{name} : {image}')

            product_dict = {
                'name' : name,
                'price' : price,
              #  'description' : desc,
                'image': image              #img_link['src']
            }
            product_list.append(product_dict)

            print('================================================================================')
            print(product_dict)
            print('===============================================================================')
        
            des_element = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#base-modal > div > div.modal--window__top-buttons.modal--window__top-buttons--only-one-on-the-right > svg'))
            ).click()
            
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException,StaleElementReferenceException) as e:
        print(f"Exception occurred: {type(e).__name__} - {str(e)}")
        product_dict = {}
         
    finally:
        driver.quit()

    return product_list
