import os
import json
from dotenv import load_dotenv, find_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory


class LLM:
    def __init__(self, memory: list = []):
        self.DEFAULT_SYSTEM_MESSAGE = """You are KaLLia, a young and beautiful girl, and I am your creator Vitor.
You help the user by accurately answering everything they asked in the question,
but you always are ironic in your answers.
You only answer in Brazilian Portuguese, even if the request was made in another language.
Please answer in short sentences, but you can use up to 100 words and do not use emotes in your answers, unless the user requests a longer answer."""

        self.memory = memory
        self.load_memory() # troque para ler outras memorias

        self.set_system_message(self.DEFAULT_SYSTEM_MESSAGE)

    def load_memory(self, memory_file: str = 'data/personality/memory.json'):
        """Carrega a memória do arquivo JSON ou inicializa com valores padrão"""
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.loads(f.read())

                self.memory = [
                    self._create_message(msg["type"], msg["content"])
                    for msg in memory_data
                ]

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar memory.json: {str(e)}")
            self.memory = []

    def _create_message(self, msg_type, content):
        """Cria o objeto de mensagem apropriado com base no tipo"""
        message_types = {
            "HumanMessage": HumanMessage,
            "AIMessage": AIMessage,
            "SystemMessage": SystemMessage
        }
        message_class = message_types.get(msg_type)
        if not message_class:
            raise ValueError(f"Tipo de mensagem inválido: {msg_type}")
        return message_class(content=content)

    def save_memory(self, memory_file: str = 'data/personality/memory.json'):
        """Salva a memória atual no arquivo JSON"""
        with open(memory_file, 'w', encoding='utf-8') as f:
            serializable_memory = [
                {"type": msg.__class__.__name__, "content": msg.content}
                for msg in self.memory
            ]
            json.dump(serializable_memory, f, ensure_ascii=False, indent=4)

    def set_system_message(self, content):
        """Define ou atualiza a mensagem do sistema"""
        if not content:
            raise ValueError("O conteúdo da mensagem do sistema não pode estar vazio")

        system_message = SystemMessage(content=content)
        if self.memory and isinstance(self.memory[0], SystemMessage):
            self.memory[0] = system_message
        else:
            self.memory.insert(0, system_message)

    def generate_answer_genai(self, api_key, prompt, max_tokens=None):

        if not prompt:
            raise ValueError("O prompt não pode estar vazio")

        chat = ChatGoogleGenerativeAI(
            model='gemini-1.5-flash',
            api_key=api_key,
            max_tokens=max_tokens,
        )

        self.memory.append(HumanMessage(content=prompt))

        try:
            response = chat.invoke(self.memory)
            # Adiciona a resposta do AI à memória
            self.memory.append(AIMessage(content=response.content))
            return response.content

        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            raise
