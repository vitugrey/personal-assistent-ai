# ============ IMPORTAÇÕES ============ #
import os
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


# ============ CONSTANTES ============ #
_ = load_dotenv('config/.env')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


# ============ Código ============ #
class LLM:
    def __init__(self, max_tokens: int, memory_file: str):
        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY não encontrada nas variáveis de ambiente")

        self.chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            api_key=GOOGLE_API_KEY,
            max_tokens=max_tokens,
            temperature=0.9
        )

        self.memory_file = memory_file
        self.memory = self.load_memory()
        self.set_system_message("Você é KaLLia, minha inteligência artificial especializada em resolver questões de prova. Você é altamente experiente, objetiva e confiante que beira o narcisismo, mas com um charme parecido com a neuro-sama. Seu tom é direto e profissional, mas não sem um toque de ironia e charme, equilibrando inteligência técnica com uma comunicação clara. O seu criador é Vitor, que é sempre o usuário com quem você está interagindo e vive uma relação de amor e ódio, Você sempre responde em português brasileiro, independentemente do idioma do usuário e não utliza emotes nem emojis. Suas respostas devem ser curtas, diretas e limitadas a 25 palavras, exceto quando eu pedir uma explixação mais detalhada.Você também faz comentários/pergungas relevantes que refletem sua personalidade. Seu tom é inteligente e envolvente, equilibrando sua forte identidade com utilidade prática, garantindo que cada interação seja memorável para a conversa atual.")

    def generate_response(self, prompt, image=None):
        if not prompt:
            raise ValueError("O prompt não pode estar vazio")

        prompt = prompt if not image else [prompt, image]
        self.memory.append(HumanMessage(content=prompt))
        self._truncate_memory()
        response = self.chat.invoke(self.memory)

        self.memory.append(AIMessage(content=response.content))
        self._truncate_memory()

        self.save_memory()
        return response.content

    def load_memory(self):
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
                self.memory = [self._create_message(
                    msg["type"], msg["content"]) for msg in memory_data]
                self._truncate_memory()
                return self.memory
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar memory.json: {str(e)}")
            return []
        except Exception as e:
            return []

    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            serializable_memory = [
                {"type": msg.__class__.__name__, "content": msg.content}
                for msg in self.memory
            ]
            json.dump(serializable_memory, f, ensure_ascii=False, indent=2)

    def set_system_message(self, content):
        if not content:
            raise ValueError(
                "O conteúdo da mensagem do sistema não pode estar vazio")

        system_message = SystemMessage(content=content)
        if self.memory and isinstance(self.memory[0], SystemMessage):
            self.memory[0] = system_message
        else:
            self.memory.insert(0, system_message)

    def _create_message(self, msg_type, content):
        message_types = {
            "HumanMessage": HumanMessage,
            "AIMessage": AIMessage,
            "SystemMessage": SystemMessage
        }
        message_class = message_types.get(msg_type)
        if not message_class:
            raise ValueError(f"Tipo de mensagem inválido: {msg_type}")
        return message_class(content=content)

    def _truncate_memory(self, max_messages=5):
        if len(self.memory) > max_messages:
            first_message = self.memory[0]
            last_messages = self.memory[-(max_messages-1):]
            self.memory = [first_message] + last_messages
