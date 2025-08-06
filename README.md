A simple and fast web application to generate clinical notes using Llama 3 hosted on Groq API. Built with Streamlit for quick UI prototyping and ease of deployment.

🔧 Features
Generate structured clinical notes from short prompts
Utilizes Groq's Llama 3 models for blazing-fast responses
Built-in examples for quick testing
Streamlit-based UI for rapid interaction

Demo
Run the app locally:

git clone https://github.com/your-username/clinical-note-assistant.git
cd clinical-note-assistant
pip install -r requirements.txt
streamlit run app.py

⚙️ Configuration
Create a .env file with your Groq API Key:


GROQ_API_KEY=your_groq_api_key_here
Make sure to install python-dotenv to load environment variables.

Models
Uses the following Groq-hosted LLMs:
llama3-8b-8192
llama2-70b-4096 (optional fallback)
