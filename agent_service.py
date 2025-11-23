from typing import Dict
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

clientes_db: Dict[str, Dict] = {
    "12345678900": {
        "nome": "Maria Clara",
        "saldo": 2500.75,
        "contas": [
            {"id": "001", "tipo": "corrente", "limite": 1000},
            {"id": "002", "tipo": "poupança", "rendimento": "6% a.a"}
        ]
    }
}

def identificar_intencao(frase: str) -> str:
    frase = frase.lower()
    if "saldo" in frase:
        return "consultar_saldo"
    if "conta" in frase:
        return "informacao_conta"
    if "empréstimo" in frase or "emprestimo" in frase:
        return "solicitar_emprestimo"
    return "conversa_geral"

class AgentBankService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API KEY não encontrada. Configure GOOGLE_API_KEY no .env")

        modelos = ["gemini-1.5-flash", "gemini-1.5", "gemini-1"]

        self.llm = None
        for modelo in modelos:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=modelo,
                    api_key=api_key
                )
                self.llm.invoke("Olá")
                print(f"[INFO] Usando modelo: {modelo}")
                break
            except Exception as e:
                print(f"[AVISO] Modelo {modelo} não disponível: {str(e)}")

        if not self.llm:
            raise RuntimeError("Nenhum modelo disponível para uso. Verifique sua conta no Google Cloud.")

    def responder(self, pergunta: str) -> str:
        try:
            resposta = self.llm.invoke(pergunta)
            return resposta.content
        except Exception as e:
            return f"Erro ao gerar resposta: {str(e)}"