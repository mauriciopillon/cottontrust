import requests
import random

# Inicie uma instância do ACA-Py
ACA_PY_URL = "http://localhost:8151"

# Defina as credenciais de autenticação da API
headers = {"X-API-Key": "secretkey"}

# Defina o número de DIDs que você deseja criar
num_dids = 2

# Crie as DIDs
for _ in range(num_dids):
    response = requests.post(f"{ACA_PY_URL}/wallet/did/create", headers=headers)
    if response.status_code == 200:
        did_info = response.json()
        print(f"Novo DID: {did_info['result']['did']}, Verkey: {did_info['result']['verkey']}")
    else:
        print(f"Erro ao criar DID: {response.content}")

# Imprima todos os DIDs
response = requests.get(f"{ACA_PY_URL}/wallet/did", headers=headers)
if response.status_code == 200:
    dids = response.json()
    print("Todos os DIDs:")
    for did_info in dids['results']:
        print(f"DID: {did_info['did']}, Verkey: {did_info['verkey']}")
else:
    print(f"Erro ao recuperar DIDs: {response.content}")

# Obtenha todas as DIDs
did_url = f"{ACA_PY_URL}/wallet/did"
response = requests.get(did_url, headers=headers)
if response.status_code == 200:
    dids = response.json()['results']
else:
    print(f"Erro ao obter DIDs: {response.content}")
    exit(1)

# Escolha duas DIDs aleatoriamente
did1, did2 = random.sample(dids, 2)

# Crie convites para cada DID
connection_ids = []
for did in [did1, did2]:
    invite_url = f"{ACA_PY_URL}/connections/create-invitation"
    response = requests.post(invite_url, headers=headers, json={"alias": did['did']})
    if response.status_code == 200:
        invitation = response.json()
        connection_ids.append(invitation['connection_id'])
        print(f"Convite criado para {did['did']}: {invitation}")
    else:
        print(f"Erro ao criar convite para {did['did']}: {response.content}")

# Aqui, você precisaria ter cada DID aceitar o convite do outro para estabelecer a conexão
# Isso geralmente é feito fora do ACA-Py, por exemplo, através de um aplicativo de mensagens

# Uma vez que as conexões estejam estabelecidas, você pode realizar a transação
# Por exemplo, você pode enviar uma mensagem de did1 para did2
message_url = f"{ACA_PY_URL}/connections/{connection_ids[0]}/send-message"
message_body = {"content": "Olá, esta é uma mensagem de teste."}
response = requests.post(message_url, json=message_body, headers=headers)
if response.status_code == 200:
    print("Mensagem enviada com sucesso")
else:
    print(f"Erro ao enviar mensagem: {response.content}")

# Aceite o convite de conexão para cada DID
for connection_id in connection_ids:
    # Obtenha o estado da conexão
    get_connection_url = f"{ACA_PY_URL}/connections/{connection_id}"
    response = requests.get(get_connection_url, headers=headers)
    connection_state = response.json()["state"]

    # Se a conexão estiver no estado "invitation", tente aceitar o convite
    if connection_state == "invitation":
        accept_invitation_url = f"{ACA_PY_URL}/connections/{connection_id}/accept-invitation"
        response = requests.post(accept_invitation_url, headers=headers)

        if response.status_code == 200:
            print(f"Convite de conexão aceito com sucesso para a conexão {connection_id}.")
        else:
            print(f"Erro ao aceitar o convite de conexão para a conexão {connection_id}: {response.content}")
    else:
        print(f"A conexão {connection_id} já está no estado {connection_state}.")

# Obtenha informações sobre a conexão
connection_id = connection_ids[0]
connection_url = f"{ACA_PY_URL}/connections/{connection_id}"
response = requests.get(connection_url, headers=headers)

if response.status_code == 200:
    connection_info = response.json()
    if connection_info['state'] == 'active':
        print("A conexão foi estabelecida.")
    else:
        print(f"A conexão está no estado: {connection_info['state']}")
else:
    print(f"Erro ao obter informações da conexão: {response.content}")