import os
from dotenv import load_dotenv,find_dotenv
load_dotenv()
import json
from datetime import datetime
from typing import Union,List

## tools 
from image_displayer import extract_image_from_database
from order_automation import order_automation 
from order_scheduler import schedule_orders
from Current_time import get_current_time

from langchain.pydantic_v1 import BaseModel,Field
from langchain.memory import ConversationBufferMemory
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.tools import StructuredTool
from langchain.agents import AgentExecutor,LLMSingleActionAgent,AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.chains.llm import LLMChain
from langchain.tools import Tool
from langchain.schema import AgentAction, AgentFinish
import re

from langchain_core.utils.function_calling import convert_pydantic_to_openai_tool






# /// TOOLS INPUT SCHEMAS

class OrderAutoInput(BaseModel):
    name:str = Field(description='name of the drug to be order')
    NumOrder:int = Field(description='Number of order to make') 

class order(BaseModel):
    'For making drugs orders'
    item: List[List[OrderAutoInput]] = Field(description='a list of list containing the name of drug and number of order')

class image_displayer_input(BaseModel):
    '''Input for the images displayer'''
    drug_name:str = Field(...,description='Name of the drug, whose image is to be displayed')

class OrderSchInput(BaseModel):
    '''Schedule order at any time'''
    drug_name:str = Field(description='Name of the drug')
    NumOrder:int = Field(description='Number of orders to make')
    Time:datetime = Field(description='When to make the order. It must be in datetime in this format YYYY-MM-DD HH:MM:SS and current.')

class CurTimeInput(BaseModel):
    'Gets the current time'


#/// CREATING TOOLS FOR LLM

OrderTool = StructuredTool.from_function(
    name='Order automation',
    description='to make order on wesite. you have two input, one a string(the name of the drug) and other an int(the number of order to make)',
    args_schema=OrderAutoInput,
    func= order_automation,
    return_direct=True
)

ImageTool = StructuredTool.from_function(
    name='see picture',
    description='to see images',
    args_schema=image_displayer_input,
    func=extract_image_from_database,
    return_direct=True
)


Tools = [ImageTool,OrderTool]

#/// SETUP PROMPT TEMPLATE

template = """Answer the following questions as best you can, but speaking as friendly professional sales personnel. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Remember to answer as a friendly compassionate medical sales personnel when giving your final answer.
ensure to always use the tools when appropriate and follow the tool schema

Question: {input}
{agent_scratchpad}"""


# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)

prompt = CustomPromptTemplate(
    template=template,
    tools=Tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps"]
)


## /// SETUP OUTPUT PARSER

class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
    
output_parser = CustomOutputParser() # INSTANTIATING PARSER

## // SETTING UP LLM AND AGENT

llm = ChatGoogleGenerativeAI(temperature=0,model='gemini-pro',google_api_key=os.getenv('GEMINI_KEY'))
llm_chain = LLMChain(llm=llm, prompt=prompt)
tool_names = [tool.name for tool in Tools]

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=tool_names
)

tool_names

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                    tools=Tools,
                                                    verbose=True)

agent_executor.run("order one Clearblue Pregnancy Test *1 Tests")



order_fun['name']



def order_automation(items:list[list[str,int]]):
    'To make order from web'
    url = 'https://glovoapp.com/ng/en/lagos/medplus-pharmacy-los/'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.chromedriver_executable = "venv/chromedriver-win64/chromedriver.exe"
    try:
        driver = Chrome()
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        time.sleep(10)
        cookie = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='onetrust-close-btn-handler onetrust-close-btn-ui banner-close-button ot-close-icon']"))
                ).click()
        
        for drugs in items:
            print(f'Ordering {drugs[0]}')
            drug_name = drugs[0]
            number_of_order = drugs[1]

            search_elements = driver.find_elements(By.CLASS_NAME,'search-input__field')

            for search_input in search_elements:
                try:
                    # Wait for the element to be clickable
                  #  search_input = wait.until(EC.element_to_be_clickable((By.ID, search_input.get_attribute("id"))))

                    if wait.until(EC.element_to_be_clickable((By.ID, search_input.get_attribute("id")))):
                        # If the element is interactable, send keys
                        search_input.send_keys(drug_name)
                    


                        # wait for search results
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME,'list__container')))

                    
                    search_result = driver.find_element(By.CLASS_NAME,'product-row')  # the issues maybe here , foe not clicking on the item


                    if search_result.find_element(By.CLASS_NAME,'product-row__name').text == drug_name: #check if name matches
                            
                        order_count = 1
                        while order_count <= number_of_order:
                            print(f'Number of orders made : {order_count}')
                                
                            search_result.click() 
                                
                            # excutes when there is a add location overlay
                            path_element = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[data-v-60bfb9dd]'))
                                    )
                    
                            if order_count == 1: 
                                 path_element.click() 
                            else:
                                pass
                            #clicks on add to cart button 
                            add_to_cart = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[@class='helio-button custom-submit primary custom-submit--centered']"))).click()
                            driver.implicitly_wait(20)
                            order_count += 1
                        
                    
                    
                    # restarts the search for another drug
                    driver.find_element(By.XPATH,"//*[@id='default-wrapper']/div/div/div/section[1]/div[2]/div/div[3]/div[1]/div[2]/div/form/img").click()


                    break

                except Exception as e:
                    # Handle the exception if the element is not clickable
                    print(f"Element not clickable: {e}")

            
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException,StaleElementReferenceException) as e:
        print(f"Exception occurred: {type(e).__name__} - {str(e)}")
    finally:
        driver.quit()
    return ('COMPLETED')





if __name__ == '__main__':
    order_automation([['Postinor *2 Tabs',3],['Ellaone 30Mg *1Tab',4]])

            

            