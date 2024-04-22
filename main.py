import requests
import random

# Inicie uma instância do ACA-Py ----------------------------------------------------------------------------------
#ACA_PY_URL = "http://localhost:8150"

# Defina as credenciais de autenticação da API --------------------------------------------------------------------
headers = {"X-API-Key": "secretkey"}

import requests

# Defina o número da porta inicial
initial_port = 8150

# Defina as credenciais de autenticação da API
headers = {"X-API-Key": "secretkey"}

# Crie uma lista de instâncias do ACA-Py
aca_py_instances = []
for i in range(1, 5):
    # Adicione o número da iteração ao número da porta inicial
    port = initial_port + i

    # Crie a URL base para a instância do ACA-Py
    url = f"http://localhost:{port}"

    # Adicione a instância à lista
    instance = {
        "url": url,
        "headers": headers
    }
    aca_py_instances.append(instance)

# Agora você tem uma lista de instâncias do ACA-Py que você pode manipular
# Por exemplo, aqui está como você pode obter o status de cada instância
for instance in aca_py_instances:
    response = requests.get(f"{instance['url']}/status", headers=instance['headers'])
    print(response.text)  # altere esta linha