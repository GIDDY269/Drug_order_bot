import requests
from typing import List,Tuple,Optional
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException,StaleElementReferenceException
import time
from io import BytesIO
from PIL import Image
import streamlit as st




def take_order_screenshot(driver):
        # take screenshot 
        time.sleep(10)
        screenshot_element = driver.find_element(By.XPATH,'//*[@id="default-wrapper"]/div/div/div/section[1]/div[2]/div[2]/div[4]/div')
        WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="default-wrapper"]/div/div/div/section[1]/div[2]/div[2]/div[4]/div/div/div/section/div/section[1]/li')))
        # Get the location and size of the element
        location = screenshot_element.location
        size = screenshot_element.size
        print(f'the size : {size}')
        print(f'location : {location}')

        
        # Take a screenshot of the entire page
       # driver.execute_script("window.scrollBy(0, 100);")
        screenshot = driver.get_screenshot_as_png()

        # Crop the screenshot to the desired element
        x = location['x'] 
        y = location['y'] 
        width = size['width']
        height = size['height'] 

        screenshot = Image.open(BytesIO(screenshot))
        element_screenshot = screenshot.crop((x, y, x + width,y + height))

        element_screenshot_bytes = BytesIO() #to store crenshot in memory
        element_screenshot.save(element_screenshot_bytes,format='PNG')
        element_screenshot.save('new_photo.png',format='PNG')

        element_screenshot_bytes.seek(0) # Reset the stream position to the beginning

        return element_screenshot_bytes


def order_automation(items:List):
    
    'To make order from web'
    url = 'https://glovoapp.com/ng/en/lagos/medplus-pharmacy-los/'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.chromedriver_executable = "chromedriver-win64/chromedriver.exe"
    try:
        driver = Chrome(options=chrome_options)
        print(f'driver yes : {driver}')
        user_agent = driver.execute_script("return navigator.userAgent;")
        is_mobile = 'Mobile' in user_agent

        # Set viewport size based on the device type
        if is_mobile:
            # Mobile viewport size
            driver.set_window_size(375, 812)  
        else:
            # Desktop viewport size
            driver.maximize_window()
            

        driver.get(url)
        wait = WebDriverWait(driver, 50)

        time.sleep(10)
        cookie = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,
             "//button[@class='onetrust-close-btn-handler onetrust-close-btn-ui banner-close-button ot-close-icon']")
             )).click()
        
        for drugs_dict in items:
            dict_keys = list(drugs_dict.keys())
            drug_name = drugs_dict['name']
            number_of_order = drugs_dict['NumOrder']
            print(f'Ordering {drug_name}')
            print(f'number of order {number_of_order}')

            search_elements = driver.find_elements(By.CLASS_NAME,'search-input__field')

            for search_input in search_elements:
                try:
                    # Wait for the element to be clickable
                  

                    if wait.until(EC.element_to_be_clickable((By.ID, search_input.get_attribute("id")))):
                        # If the element is interactable, send keys
                        search_input.send_keys(drug_name)
                    

                    # wait for search results
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME,'list__container')))

                    # the issues maybe here , foe not clicking on the item
                    search_result = driver.find_element(By.CLASS_NAME,'product-row')  

                    #check if name matches
                    if search_result.find_element(By.CLASS_NAME,'product-row__name').text == drug_name: 
                            
                        order_count = 1
                        while order_count <= number_of_order:
                            print(f'Number of orders made : {order_count}')

                            #wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'product-row'))).click()
                            search_result.click() 
                            print('CLICKED ON SEARCH RESULT')
                                
                            # excutes when there is a add location overlay
                            print('Finding location of overlay')
                            path_element = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[data-v-60bfb9dd]'))
                                    )
                    
                            if order_count == 1:
                                 
                                 print('TRYING TO CLICK ON OVERLAY') 
                                 path_element.click() 
                            else:
                                pass
                            print('CLICKED ON LOCATION OVERLAY')
                            #clicks on add to cart button 
                            print('CLICKING ON PRODUCT')
                            add_to_cart = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                                 "//button[@class='helio-button custom-submit primary custom-submit--centered']"))
                                                                                 ).click()
                            driver.implicitly_wait(20)
                            order_count += 1
                        
                    # restarts the search for another drug
                    driver.find_element(By.XPATH,
                                        "//*[@id='default-wrapper']/div/div/div/section[1]/div[2]/div/div[3]/div[1]/div[2]/div/form/img").click()
                    
                    break
    
                except Exception as e:
                    # Handle the exception if the element is not clickable
                    print(f"Element not clickable: {e}")


        # take screenshot of order
        screenshot = take_order_screenshot(driver)
        
   
    except (TimeoutException, NoSuchElementException, 
            ElementClickInterceptedException,StaleElementReferenceException) as e:
            print(f"Exception occurred: {type(e).__name__} - {str(e)}")
            return {'Cannot place order now, try again later':'message'}
    finally:
        driver.quit()
    return {' ORDER HAS BEEN COMPLETED, TAKE A LOOK AT IT, THANKS FOR SHOPPING WITH US' : screenshot }





if __name__ == '__main__':
    order_automation([{'name':'Panadol Actifast * 14 Tabs','NumOrder':3}])

            

            