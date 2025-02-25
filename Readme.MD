# AI-Powered Chatbot Revolutionizes Online Drug Inventory Management
## Case overview
* __Client:__ Self-initiated project for GLOVO (Healthcare & E-commerce)
* __Industry:__ Pharmacy, Online Retail, AI Chatbots
* __Product:__ LLM-powered chatbot system for inventory management and customer engagement
* __Technologies Used:__ Large Language Models (LLM), Retrieval-Augmented Generation (RAG),
Web Scraping, FastAPI, LangChain, Database Integration
* __Results:__
* Automated 80% of customer inquiries about drug availability
* Enabled customers to browse and add drugs to their cart seamlessly
* Reduced manual workload for store staff by over 60%
## The Problem/Goal
E-commerce websites often struggle with high volumes of customer inquiries about product
availability, pricing, and details. Many customers either browse the website trying to find what
they need or come with specific products in mind, but slow response times and poor search
experiences can lead to frustration and abandoned carts. Handling these queries manually
increases operational costs and delays purchases. Additionally, most e-commerce platforms
lack an intuitive chat-based interface where customers can quickly search, view product images,
and add items to their cart seamlessly without navigating multiple pages.
This project aimed to build an AI-powered chatbot that could:
1. Provide real-time inventory information about drugs.
2. Allow customers to view product images and descriptions.
3. Enable users to add items to their cart and proceed to checkout seamlessly.
A major challenge was ensuring the chatbot could accurately retrieve drug information from a
dynamic inventory system while providing a human-like conversational experience.
## The Solution
I developed an LLM-powered chatbot with a retrieval-augmented generation (RAG) system to
fetch real-time drug inventory data.
## Key Features & Implementation
1. Web Scraping & Database Integration – Extracted and stored up-to-date product
information from the pharmacy’s inventory system.
2. Automated Inventory Queries – Used LangChain & LLAMA3 model to understand
customer queries and provide relevant drug details. Customers could ask, “Do you have
500mg of Amoxicillin in stock?” and get an instant response.
3. Product Image & Description Retrieval – Users could see drug packaging, read usage
instructions, and check alternative brands, before purchase.
4. Cart & Checkout Integration – Customers could add items to their cart within the chat
and proceed to purchase.
5. Scalable & Fast Backend – Implemented using FastAPI, ensuring low-latency
responses.
6. Conversational AI with Context Awareness – Leveraged LangChain + Llama3 to
handle complex queries (e.g., “What’s the difference between Ibuprofen and
Paracetamol?”).
## Why This Solution Stands Out
1. The chatbot was designed to handle complex customer queries about drug interactions,
alternatives, and availability.
2. Unlike standard chatbots, it used retrieval-augmented generation (RAG) for accurate and
context-aware responses.
3. It significantly reduced the workload on pharmacy staff, allowing them to focus on critical
tasks.
## The Results
The AI chatbot significantly improved pharmacy operations and customer engagement:
1. 80% of inquiries automated – reducing response time from 5 minutes to instant answers.
2. 60% reduction in manual workload
3. Enhanced customer shopping experience – users could see drug images and add items to
their cart directly from chat.
Unexpected Benefits
1. The pharmacy gained valuable insights into popular products and customer buying
patterns.
2. The system could be expanded to support voice-based interactions for even greater
accessibility.
## Conclusion & Next Steps
This AI chatbot project showcases how LLMs can transform online pharmacy operations by
improving efficiency and customer experience. Future improvements could include:
1. Integration with telemedicine services for doctor consultations.
2. Voice and multilingual support to serve a wider audience.
3. More advanced personalization, recommending medications based on purchase history

Video link on how the chatbot performs : https://x.com/oboro_gideon/status/1803518453334110381?t=XEoxb39Q8owronYrfPSLgw&s=19
