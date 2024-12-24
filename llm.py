import os
import json
from dotenv import load_dotenv, find_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory


class LLM:
    def __init__(self, memory: list = []):
        self.memory = memory

    def load_memory(self):
        with open('memory.json', 'r', encoding='utf-8') as f:
            memory_data = json.loads(f.read())
            # Reconstrói os objetos a partir dos dicionários
            self.memory = [
                HumanMessage(content=msg["content"]) if msg["type"] == "HumanMessage"
                else AIMessage(content=msg["content"])
                for msg in memory_data
            ]

    def save_memory(self):
        with open('memory.json', 'w', encoding='utf-8') as f:
            # Serializa os objetos como dicionários
            serializable_memory = [
                {"type": msg.__class__.__name__, "content": msg.content} for msg in self.memory
            ]
            json.dump(serializable_memory, f, ensure_ascii=False, indent=4)

    def generate_ansewer_genai(self, api_key, prompt, max_tokens):

        chat = ChatGoogleGenerativeAI(
            model='gemini-1.5-flash',
            api_key=api_key,
            max_tokens=max_tokens,
        )

        self.memory.append(HumanMessage(content=prompt))

        response = chat.invoke(self.memory)

        self.memory.append(AIMessage(content=response.content))

        return response.content
