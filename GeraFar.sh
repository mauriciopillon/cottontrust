#!/bin/bash

for i in $(seq 1 10); do
    echo "{
        \"name\": \"Fardinho$i\",
        \"Identificador do Fardinho\": \"ID$i\",
        \"Identificador da Fazenda\": \"Fazenda$i\",
        \"Identificador da UBA\": \"UBA$i\",
        \"Safra\": \"Safra$i\",
        \"Talhao\": \"Talhao$i\",
        \"Data da Colheita\": \"01/01/2023\",
        \"Produto da Semente\": \"Semente$i\",
        \"Lote da Semente\": \"Lote$i\",
        \"Peso\": \"10kg\",
        \"wallet_config\": \"config_fardinho$i\",
        \"wallet_credentials\": \"credentials_fardinho$i\"
    },"
done
