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

for i in `seq 1 1 10`; do
export ACAPY_INBOUND_TRANSPORT_PORT="815"$i

# Defina o nome e a chave da carteira
export ACAPY_WALLET_NAME="carteira_gabas"$i
export ACAPY_WALLET_KEY="chave_da_carteira_gabas"$i

# Inicie o ACA-Py
aca-py start -it $ACAPY_INBOUND_TRANSPORT_TYPE $ACAPY_INBOUND_TRANSPORT_HOST $ACAPY_INBOUND_TRANSPORT_PORT -ot http -e http://localhost:8150 --genesis-file /home/gabriel/cottontrust_ACA_lab/genesis.txn --admin 0.0.0.0 8150 --admin-api-key secretkey --wallet-name $ACAPY_WALLET_NAME --wallet-key $ACAPY_WALLET_KEY &
done