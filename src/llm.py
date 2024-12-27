import os
import json
import io
import base64
from PIL import Image

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory


class LLM:
    def __init__(self, memory: list = []):
        
        self.memory = memory
        self.load_memory()  # troque para ler outras memorias


    def load_memory(self, memory_file: str = 'data/personality/memory.json'):
        """Carrega a memória do arquivo JSON ou inicializa com valores padrão"""
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.loads(f.read())

                self.memory = [
                    self._create_message(msg["type"], msg["content"])
                    for msg in memory_data
                ]

            self._truncate_memory()

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar memory.json: {str(e)}")
            self.memory = []

    def _truncate_memory(self, max_messages=50):
        if len(self.memory) > max_messages:
            first_message = self.memory[0]
            last_messages = self.memory[-(max_messages-1):]
            self.memory = [first_message] + last_messages

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
        self._truncate_memory()
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
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

    def generate_answer_genai(self,
                              api_key,
                              prompt,
                              image_content=None,
                              max_tokens=None
                              ):

        if not prompt:
            raise ValueError("O prompt não pode estar vazio")

        self._truncate_memory()

        chat = ChatGoogleGenerativeAI(
            model='gemini-1.5-flash',
            api_key=api_key,
            max_tokens=max_tokens,
        )

        content = [prompt] if not image_content else [prompt, image_content]
        self.memory.append(HumanMessage(content=content))

        try:
            response = chat.invoke(self.memory)
            self.memory.append(AIMessage(content=response.content))
            return response.content

        except Exception as e:
            print(f"Erro ao gerar resposta: {str(e)}")
            raise

    def read_image(self, image_path):
        try:
            image = Image.open(image_path)
            buffer = io.BytesIO()
            image.save(buffer, format=image.format or 'PNG')
            buffer.seek(0)
            
            # Converte para base64
            image_bytes = buffer.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determina o tipo MIME da imagem
            mime_type = f"image/{image.format.lower() if image.format else 'png'}"
            
            # Retorna no formato esperado pelo LangChain
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_base64}",
                    "detail": "auto"
                }
            }
        except Exception as e:
            print(f"Erro ao processar imagem: {str(e)}")
            raise
