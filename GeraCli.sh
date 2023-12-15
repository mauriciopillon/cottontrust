#!/bin/bash
echo "["
for i in $(seq 1 50); do
    echo "{
        \"name\": \"CLIENTE$i\",
        \"Endereco - Rua\": \"Rua 123\",
        \"Endereco - Bairro\": \"Bairro A\",
        \"Endereco - Cidade\": \"Cidade X\",
        \"Endereco - Estado\": \"Estado Y\",
        \"Endereco - Pais\": \"Pais Z\",
        \"wallet_config\": \"config_CLIENTE$i\",
        \"wallet_credentials\": \"credentials_CLIENTE$i\",
        \"balance\": $((i * 1000000)),
        \"quero_fardinho\": $((i * 10)),
        \"quant_fardinho\": $((i * 0))
    },"
done
echo "]"
