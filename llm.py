from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import re

class LLM:

    pass

# class LLM:
#     def __init__(self, api_key: str, model_name: str = 'gemini-1.5-flash'):
#         self.model_name = model_name
#         self.api_key = api_key
#         self.history = []

#     def generate_answer(self, prompt: str) -> str:
#         chat = ChatGoogleGenerativeAI(model=self.model_name, api_key=self.api_key)

#         self.history.append(HumanMessage(content=prompt))
#         response = chat.invoke(self.history)
#         self.history.append(AIMessage(content=response.content))

#         return response.content

#     def pos_answer(self, answer: str) -> tuple:
#         code_pattern = re.compile(r'```(.*?)```', re.DOTALL)
#         match = code_pattern.search(answer)

#         if match:
#             code = match.group(1).strip()  # Extrai o código
#             output = answer.replace(match.group(0), '').strip()  # Remove o código do restante da resposta
#             return code, output
#         else:
#             return '', answer  # Se não encontrar código, retorna resposta completa
