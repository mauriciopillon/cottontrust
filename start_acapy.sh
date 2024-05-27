export ACAPY_AUTO_ACCEPT_INVITES="true"
export ACAPY_AUTO_ACCEPT_REQUESTS="true"
export ACAPY_AUTO_PING_CONNECTION="true"
export ACAPY_AUTO_RESPOND_MESSAGES="true"
export ACAPY_AUTO_RESPOND_CREDENTIAL_OFFER="true"
export ACAPY_AUTO_RESPOND_CREDENTIAL_REQUEST="true"
export ACAPY_AUTO_RESPOND_PRESENTATION_REQUEST="true"
export ACAPY_AUTO_STORE_CREDENTIAL="true"
export ACAPY_INBOUND_TRANSPORT_TYPE="http"
export ACAPY_INBOUND_TRANSPORT_HOST="0.0.0.0"
ps -edf | grep aca-py | awk '{print "kill -9 "$2'} | $SHELL

# Defina o número da porta inicial
initial_port=8150
initial_admin_port=8150

# Ler os IDs do arquivo JSON usando jq
ids=$(jq -r '.[].id' fardinhos_menor.json)

# Inicializar o contador
counter=0

# Iterar sobre cada ID
for id in $ids; do
    # Adicione o contador ao número da porta inicial
    export ACAPY_INBOUND_TRANSPORT_PORT=$(($initial_port+$counter))
    export ACAPY_ADMIN_PORT=$(($initial_admin_port+$counter))

    # Verifique se a porta está em uso e, em caso afirmativo, mate o processo
    if lsof -Pi :$ACAPY_INBOUND_TRANSPORT_PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $ACAPY_INBOUND_TRANSPORT_PORT is in use. Attempting to kill process..."
        kill -9 $(lsof -t -i:$ACAPY_INBOUND_TRANSPORT_PORT)
    fi

    if lsof -Pi :$ACAPY_ADMIN_PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "Admin port $ACAPY_ADMIN_PORT is in use. Attempting to kill process..."
        kill -9 $(lsof -t -i:$ACAPY_ADMIN_PORT)
    fi

    # O restante do código permanece o mesmo
    export ACAPY_WALLET_NAME="carteira_"$id
    export ACAPY_WALLET_KEY="chave_da_carteira_"$id

    aca-py start -it $ACAPY_INBOUND_TRANSPORT_TYPE $ACAPY_INBOUND_TRANSPORT_HOST $ACAPY_INBOUND_TRANSPORT_PORT -ot http -e http://localhost:8150 --genesis-file /home/gabriel/cottontrust_ACA_Blockchain/genesis.txn --admin 0.0.0.0 $ACAPY_ADMIN_PORT --admin-api-key secretkey --wallet-name $ACAPY_WALLET_NAME --wallet-key $ACAPY_WALLET_KEY &

    # Incrementar o contador
    counter=$(($counter+1))
done