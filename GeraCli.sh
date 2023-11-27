#!/bin/bash

for i in $(seq 1 10); do
    echo "{
        \"name\": \"CLIENTE$i\",
        \"Endereco - Rua\": \"Rua 123\",
        \"Endereco - Bairro\": \"Bairro A\",
        \"Endereco - Cidade\": \"Cidade X\",
        \"Endereco - Estado\": \"Estado Y\",
        \"Endereco - Pais\": \"Pais Z\",
        \"wallet_config\": \"config_CLIENTE$i\",
        \"wallet_credentials\": \"credentials_CLIENTE$i\"
    },"
done
