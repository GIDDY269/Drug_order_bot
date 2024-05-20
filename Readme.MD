## LANCHAIN CHATBOT FOR MAKING ORDER ON A WEBSITE POWERED BY FUNCTION CALLING IN LLAMA3

This is a chatbot designed to assist users in placing orderson a pharmaceutical e-commerce website using the function calling features in llama3.

The intuition about function calling, is that the model gives structured output which will be used to make an api call. The response of the api call will be passed back to the model to give back the final response.

### Table of Contents

* Features
* Project Structure
* Prerquisties
* Installation
* Usage
* Configuration
* contribution
* License

### Features
* __Large Language Model(llm):__ Used langchain to access the llama3 api using Groq to interpret user messages.
* __DEBUG:__ Used Langsmith to debug model reponses and function calls
* __Retrieval Augmentation Generation(RAG):__ In order to give the model knowledge about drugs or product available in the store, A RAG system was built. This will enable the model to answer questions about the product with contextual understanding.
* __Order Placement:__ Facilitates the process of making orders for the users. All the user needs is to prompt the model to do so.
* __View Images of Product:__ Also, the chatbot can also display images of the product to the user, if asked to. 
* __Error Handling:__ Error handling to ensure smooth user experience

### Prerequistes
Before you begin, ensure you have met the following requirements:

* Python 3.8 or higher
* API keys or other necessary authentication credentials

### Installation

1) __Clone the Repository:__
    ```git clone git@github.com:GIDDY269/Drug_order_bot.git```

2) __Install Dependencies:__
    ```pip install -r requirements.txt```

3) __Set Up Environment Variables:__
    Create a .env file in the root directory of the project and add your API keys and other configurations:
    ```GROQ_API_KEY = API_KEY \n  GEMINI API KEY = API_KEY SQL SERVER = SERVER DATABASE = DATABASE```


### Usage

1) Run Chatbot:
    `streamlit run drug_bot.py`

2) Interact with the chatbot:
    You can interact with the chatbot using the streamlit ui.