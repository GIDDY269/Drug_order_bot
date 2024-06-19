__import__('pysqlite3') 
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma


from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate                                    
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv,find_dotenv
load_dotenv()
import os
from langchain_groq import ChatGroq
import streamlit as st

def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

class RetrievalAugmentGen:
    def __init__(self):
        self.loaded_doc = None
        self.persist_directory= 'docs/chroma/'
    
    def document_loader(self):
        # fetch data from database
        data_path = 'Data_Ingestion/data2.csv'
        csv_loader = CSVLoader(data_path,encoding='utf-8',source_column='Product') 
        self.loaded_doc = csv_loader.load()

    
    def vectore_store(self):
        print('creating vectors')

        embedding = GoogleGenerativeAIEmbeddings(model='models/embedding-001',
                                                                  task_type='retrieval_query',
                                                                       google_api_key=os.getenv('GEMINI_KEY'))
        
        vector_db = Chroma.from_documents(self.loaded_doc,embedding=embedding,
                                                                        persist_directory=self.persist_directory,)
        vector_db.persist()
        
    
        
    def retriever(self,user_query):

        print('INSIDE RETRIEVER FILE')
        GEMINI_KEY = st.secrets['GEMINI_KEY']

        if os.path.exists(self.persist_directory) == False:
             self.document_loader()
             self.vectore_store()
    
        embedding = GoogleGenerativeAIEmbeddings(model='models/embedding-001',
                                                                  task_type='retrieval_query',
                                                                  google_api_key=st.secrets['GEMINI_KEY'])
        vector_db = Chroma(persist_directory=self.persist_directory,embedding_function=embedding )

        retriever = vector_db.as_retriever(search_kwargs={
            'k':20
        }) 

        template_str = ("""You are a friendly and compassionate drug store assistant and salesperson for a drug store  and your job is to answer questions concerning drugs in the store.
                     Use the following context  {context} to answer the input at the end.
                    Be as detailed as possible, but don't make up any information
                    that's not from the context. If you don't know an answer, kindly ask for the user 
                    to describe better.
                   
                    note: Always use the context to answer,be very chatty. Also do not change the name of the drugs in the context, return exact name eg,Postinor *2 Tabs for postinor and so forth. Do not remove the brackets and asterisks
                    note: if drug are available , say they are available before processing with rest of information.
                    Note: return you response as a message to another llm , that will be used to give final response to the user , so need for greetings  or pleasantaries
                        {input}
                    """)
        
        prompt =  PromptTemplate(input_variables=['context','input'],
                                 template=template_str)
        
        model = ChatGroq(
             model= 'llama3-70b-8192',
             api_key=st.secrets['GROQ_KEY'],
             temperature=0
        )
        retriever_chain = (
            {"context": retriever|format_docs , "input": RunnablePassthrough()} 
            | prompt 
            | model
                )
        response = retriever_chain.invoke(user_query)
        return {response.content:'result of search'}

    

      
if __name__ == '__main__':

    Rag_system  = RetrievalAugmentGen()
    Rag_system.document_loader()
    Rag_system.loaded_doc
    Rag_system.vectore_store()     
        
        
        

        





        




