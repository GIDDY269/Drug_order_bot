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


def main():
    # MAIN SCRAPER FUNCTION
    url = 'https://glovoapp.com/ng/en/lagos/medplus-pharmacy-los/'
    html = fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    print('BEGINING TO SCRAPE DATA')
    for section in soup.find_all('div', class_='store__body__dynamic-content'):
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
                    for categories in sub_soup.find_all('div', class_='store__body__dynamic-content'):
                        category = categories.find('h2', class_='grid__title').text.strip()
                        products = categories.find_all('div',class_='tile')
                        print(f'scraping {category}')
                        for product in products:
                            img = product.find('img')['src']
                            product_name = product.find('span',class_='tile__description').text.strip()
                            product_price = product.find('div',class_='tile__price').text.split()[0].strip()

                            product_info = {
                                    'name' : product_name,
                                    'section' : section_name,
                                    'category' : category,
                                    'image' : img,
                                    'price': product_price
                                }

                            print(f'Product info {product_info}')
                            

                            product_data = CreateScrapeSchema(**product_info).dict()
                            print(f'after pydantic{product_data}')
                            sql_table()
                            insert_data(product_data)

                else:
                    carousel_content = section.find_all('div', class_='carousel__content__element')
                    for content in carousel_content:
                        link = content.find('a').get('href')
                        sub_html = fetch('https://glovoapp.com' + link)
                        sub_soup = BeautifulSoup(sub_html, 'html.parser')
                        for categories in sub_soup.find_all('div', class_='store__body__dynamic-content'):
                            category = categories.find('h2', class_='grid__title').text.strip()
                            products = categories.find_all('div',class_='tile')
                            for product in products:
                                img = product.find('img')['src']
                                product_name = product.find('span',class_='tile__description').text.strip()
                                product_price = product.find('div',class_='tile__price').text.split()[0].strip()
                                print(f'Scraping category {category}')
                            
        
                                product_info = {
                                    'name' : product_name,
                                    'section' : section_name,
                                    'category' : category,
                                    'image' : img,
                                    'price': product_price
                                }

                                print(f'Product info {product_info}')
                            

                                product_data = CreateScrapeSchema(**product_info).dict()
                                print(f'after pydantic{product_data}')
                                sql_table()
                                insert_data(product_data)
                print('===============================================')
                continue

if __name__ == "__main__":
    main()







    