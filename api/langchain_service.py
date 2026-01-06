from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory # 1. Naya import
import os

import os
from dotenv import load_dotenv

# .env file se variables load karne ke liye
load_dotenv()

# Sahi tarika API key assign karne ka
api_key = os.getenv("GEMINI_API_KEY")

# DHAYAN DEIN: Yahan quotes nahi lagane hain
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key 
else:
    print("Error: GEMINI_API_KEY .env file mein nahi mili!")

llm = ChatGoogleGenerativeAI(
    # model="gemini-3-flash-preview",
    model="gemini-3-flash-preview",
    temperature=0
)

# 3. History object (isko function ke bahar rakhein taaki memory bani rahe)
demo_history = ChatMessageHistory()

def get_db():
    return SQLDatabase.from_uri("sqlite:///db.sqlite3")

def ask_sql(query):
    db = get_db()

    # 4. Pichli history ko context mein badlein
    history_context = ""
    for msg in demo_history.messages[-6:]: # Aakhri 6 messages ka context
        history_context += f"{msg.type}: {msg.content}\n"

    # 5. Prompt mein history ko merge karein
    full_query = f"Context:\n{history_context}\nQuestion: {query}"

    chain = SQLDatabaseChain.from_llm(
        llm,
        db,
        verbose=True,
        top_k=5,
    )

    result = chain.run(full_query)

    # 6. Naya sawal aur AI ka jawab history mein save karein
    demo_history.add_user_message(query)
    demo_history.add_ai_message(result)

    return result




