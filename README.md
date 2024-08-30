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

## Flow Diagram 🔄📊
![NUTRINORAG](https://github.com/user-attachments/assets/27b775ca-882a-46bb-a44c-ba1d2b6316fa)

## Tech Stack Used

## How We Built It 🛠️👷‍♂️
- NutrinO-RAG was built by leveraging a combination of cutting-edge technologies, including Large Language Models (LLMs) like GPT-4, Retrieval-Augmented Generation (RAG), and Gemini AI. We started by using Gemini AI to extract nutritional information from images of tables containing food items.
- This data was then embedded and stored in a vector database using RAG, allowing for efficient retrieval of relevant information. The backend, developed in Python using Flask, processes user queries by searching the database for the requested food item. If found, the information is passed to GPT-4o mini, which generates a clear and concise response. If not found, GPT-4o mini directly generates the response.
- For personalized diet plans, the system considers user inputs such as health conditions, region, and food accessibility, using RAG and LLMs to create tailored recommendations, ensuring that the advice is both relevant and actionable.
  
## How to Set Up?


## Model Architecture 🕝 ⚡


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

