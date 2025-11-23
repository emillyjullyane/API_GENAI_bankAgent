import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

# CPF de teste
cpf_teste = "12345678900"
conta_id_teste = "001"

print("--- Testes de Endpoint da API do Agente Bancário ---")
print(f"URL Base: {BASE_URL}\n")
time.sleep(1)

def run_test(name, method, url, data=None):
    """Função auxiliar para executar e imprimir os resultados dos testes."""
    print(f"🔹 {name}: {method} {url}")
    try:
        if method == "GET":
            res = requests.get(url)
        elif method == "POST":
            res = requests.post(url, json=data)
        else:
            print("Método não suportado.")
            return

        if res.status_code == 200:
            print(f"   [SUCESSO] Status: {res.status_code}")
            print(f"   Resposta: {json.dumps(res.json(), indent=2, ensure_ascii=False)}\n")
        else:
            print(f"   [FALHA] Status: {res.status_code}")
            print(f"   Resposta: {json.text}\n")

    except requests.exceptions.ConnectionError:
        print("   [ERRO] Não foi possível conectar. Certifique-se de que a API está rodando (uvicorn main:app --reload)\n")
    except Exception as e:
        print(f"   [ERRO] Exceção: {e}\n")


# 1. Testar GET - cliente
run_test("GET Cliente", "GET", f"{BASE_URL}/clientes/{cpf_teste}")

# 2. Testar GET - saldo
run_test("GET Saldo", "GET", f"{BASE_URL}/clientes/{cpf_teste}/saldo")

# 3. Testar GET - detalhes da conta
run_test("GET Detalhes da Conta", "GET", f"{BASE_URL}/clientes/{cpf_teste}/contas/{conta_id_teste}")

# 4. Testar POST - intenção
run_test(
    "POST Identificar Intenção",
    "POST",
    f"{BASE_URL}/intencao",
    data={"pergunta": "Quero saber meu limite de crédito na conta corrente"}
)

# 5. Testar POST - agente (usa o LLM)
print("--- Teste do Agente LLM (POST /agente) ---")
run_test(
    "POST Agente (LLM)",
    "POST",
    f"{BASE_URL}/agente",
    data={"pergunta": "Qual é o saldo atual da minha conta?"}
)

# 6. Testar Endpoint Raiz
run_test("GET Raiz", "GET", f"{BASE_URL}/")