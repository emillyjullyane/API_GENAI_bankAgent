import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API KEY não encontrada no .env")

llm = ChatGoogleGenerativeAI(
    model="gemini-1",  # ⚠️ obrigatório
    api_key=api_key
)

# Lista os modelos disponíveis
try:
    modelos = llm.list_models()
    print("Modelos disponíveis:")
    for m in modelos:
        print("-", m)
except Exception as e:
    print("Erro ao listar modelos:", e)