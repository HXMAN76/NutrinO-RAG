# NutrinO-RAG - A Personal Food Assistant
<center><h2>Project Title : A Personal Chatbot for Food Guidance </h2></center>

## 🚀 Demo






## Overview
NutrinO-RAG offers a personal food guidance chatbot that uses the power of Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG). Our model is designed to provide users with reliable and personalized nutritional information. By integrating a comprehensive dataset of food items from domain knowledge document extracted using Gemini AI, NutrinO-RAG delivers clear and concise responses powered by GPT-4o mini, ensuring that users receive accurate and relevant information.

The chatbot's capabilities include providing nutritional values for various food items, generating personalized diet plans based on specific health conditions, regional preferences, and accessibility concerns, and offering region-based food suggestions. By combining the strengths of LLMs and RAG, NutrinO-RAG provides an intuitive and user-friendly experience that helps users make informed dietary choices, ultimately contributing to better health and well-being.

## 🧐 Features
- **Nutritional Information**: Obtain the right nutritional values to specific foods. 
- **Personalized Diet Plans**: Enter your health status or about the area where you live or any issues with access to food, and you will get your diet plan for the tenure you mentioned. 
- **Region-Based Suggestions**: Targeted food recommendations according to the availability of certain foods in specific region in addition to the user ability to access certain foods. 
- **Conversational Clarity**: Uses GPT-4 to present information in an easy-to-understand manner. 

## User Benefits
- **Health Improvement**: Access to accurate nutritional information helps users make better dietary choices.
- **Customized Diet Plans**: Personalized guidance for managing specific health conditions.
- **Convenience**: Easy access to region-specific food recommendations based on user preferences and availability.

## Workflow Diagram
![NUTRINORAG](https://github.com/user-attachments/assets/27b775ca-882a-46bb-a44c-ba1d2b6316fa)

## Userflow Diagram

## Tech Stack Used
 - **Flask**
 - **Lang-Chain**
     - OpenAI
     - Gemini AI
 - **ChromaDB**
 - **Docker** 

## How We Built It 🛠️👷‍♂️
- To create NutrinO-RAG the following technologies and knowledge areas were used: Large Language Models (LLMs) such as GPT-4o mini, Retrieval-Augmented Generation (RAG), and Gemini AI. we first employed Gemini AI in a scenario where the AI is designed to read from tables containing images of foods in order to extract nutrition values. 
- The following data was interpreted and placed in a vector database through use of RAG thereby enabling easy chequer point information acquisition. The backend, created in Python employing Flask, on the user’s request searches the database for the requested food. When it is found, this information is relayed to GPT-4o mini whereby it develops a simple answer in relation to the question that was posed. Should the response not be found, the program has GPT-4o mini create the response on its own. 
- Regarding the determination of specific diet requirements, the system considers the user defined inputs including health conditions, geographical location and availability of food in the location, The system utilizes RAG and LLMs to generate the recommended diet and only gives the advices that can be implemented by the users.
  
## How to Set Up?


## Possiblesd Upgrades

## Contributing 🤝
  Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests to help improve this project.
  
## Authors

- [@Sai Nivedh V](https://github.com/SaiNivedh26)
- [@Baranidharan S](https://github.com/thespectacular314)
- [@Roshan T](https://github.com/Twinn-github09)
- [@Hari Heman](https://github.com/MAD-MAN-HEMAN)



## 🛡️License

This project is licensed under the [MIT License](LICENSE).

