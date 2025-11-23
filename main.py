import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

clientes_db: Dict[str, Dict[str, Any]] = {
    "12345678900": {
        "nome": "Maria Clara",
        "saldo": 2500.75,
        "contas": [
            {"id": "001", "tipo": "corrente", "limite": 1000.00},
            {"id": "002", "tipo": "poupança", "rendimento": "6% a.a"}
        ]
    }
}

def identificar_intencao(frase: str) -> str:
    """Função heurística simples para identificar a intenção do usuário."""
    frase = frase.lower()
    if "saldo" in frase:
        return "consultar_saldo"
    if "conta" in frase:
        return "informacao_conta"
    if "empréstimo" in frase or "emprestimo" in frase:
        return "solicitar_emprestimo"
    return "conversa_geral"

class AgentBankService:
    """Serviço que encapsula o LLM, tentando conectar-se a modelos em ordem de
    preferência até encontrar um funcional."""
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API KEY não encontrada. Configure GOOGLE_API_KEY no .env")

        modelos = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]

        self.llm = None
        print("[INFO] Tentando inicializar o agente bancário...")
        for modelo in modelos:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=modelo,
                    api_key=api_key,
                    temperature=0.0
                )
                
                start_time = time.time()
                self.llm.invoke("Olá")
                latency = time.time() - start_time

                print(f"[SUCESSO] Usando modelo: {modelo} (Latência de teste: {latency:.2f}s)")
                break
            except Exception as e:
                print(f"[AVISO] Modelo {modelo} indisponível ou erro na inicialização: {str(e)}")

        if not self.llm:
            raise RuntimeError("Nenhum modelo disponível para uso. Verifique sua chave API e permissões.")

    def responder(self, pergunta: str) -> str:
        """Invoca o LLM com a pergunta do usuário."""
        system_prompt = (
            "Você é um assistente virtual de banco amigável, prestativo e seguro. "
            "Responda às perguntas do cliente. Seja conciso e profissional. "
            "Não divulgue informações confidenciais ou sensíveis."
        )
        
        try:
            prompt_completo = f"Instrução: {system_prompt}\n\nPergunta do Cliente: {pergunta}"
            resposta = self.llm.invoke(prompt_completo)
            return resposta.content
        except Exception as e:
            print(f"[ERRO LLM] Falha ao gerar resposta: {str(e)}")
            return "Desculpe, houve um erro interno ao processar sua solicitação."

# Inicialização do FastAPI e Agente
# Aqui acontece a inicialização do agente é feita aqui e é bloqueante
# Garante que o agente está pronto antes de o servidor aceitar requisições.
try:
    agent = AgentBankService()
except (ValueError, RuntimeError) as e:
    print(f"\n[ERRO CRÍTICO DE INICIALIZAÇÃO] {e}")
    agent = None

app = FastAPI(
    title="Agente Bancário - LangChain/FastAPI",
    description="API para interagir com um assistente virtual bancário e dados simulados de clientes."
)

class Pergunta(BaseModel):
    """Esquema de dados para a entrada do endpoint /agente e /intencao."""
    pergunta: str


# Endpoints da API

@app.get("/")
def read_root():
    """Endpoint raiz simples para verificar se a API está rodando."""
    return {"status": "online", "message": "API do Agente Bancário pronta."}

# Conversa com o agente (usa o LLM)
@app.post("/agente")
async def agente_endpoint(input_data: Pergunta):
    """Recebe uma pergunta e retorna a resposta gerada pelo LLM."""
    if not agent:
        raise HTTPException(
            status_code=503, 
            detail="Serviço do Agente indisponível. Falha na inicialização do LLM."
        )
        
    resposta = agent.responder(input_data.pergunta)
    return {"pergunta": input_data.pergunta, "resposta": resposta}

# Dados do cliente
@app.get("/clientes/{cpf}")
async def get_cliente(cpf: str):
    """Busca dados completos do cliente pelo CPF."""
    cliente = clientes_db.get(cpf)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente

# Saldo do cliente
@app.get("/clientes/{cpf}/saldo")
async def get_saldo(cpf: str):
    """Busca o saldo do cliente pelo CPF."""
    cliente = clientes_db.get(cpf)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return {"saldo": cliente.get("saldo", "Não informado")}

# Detalhes de conta
@app.get("/clientes/{cpf}/contas/{conta_id}")
async def get_detalhes_conta(cpf: str, conta_id: str):
    """Busca detalhes específicos de uma conta do cliente."""
    cliente = clientes_db.get(cpf)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    contas = cliente.get("contas", [])
    conta = next((c for c in contas if c["id"] == conta_id), None)

    if not conta:
        raise HTTPException(status_code=404, detail=f"Conta ID '{conta_id}' não encontrada para o CPF.")

    return conta

#Identificar intenção
@app.post("/intencao")
async def endpoint_intencao(data: Pergunta):
    """Identifica a intenção da pergunta usando uma função local (não LLM)."""
    intent = identificar_intencao(data.pergunta)
    return {"pergunta": data.pergunta, "intencao": intent}