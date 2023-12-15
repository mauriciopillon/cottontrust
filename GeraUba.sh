#!/bin/bash
echo "["
for i in $(seq 1 50); do
    echo "{
        \"name\": \"UBA$i\",
        \"Codigo de Registro da UBA\": \"123\",
        \"CNPJ\": \"123456789\",
        \"Endereco - Rua\": \"Rua 123\",
        \"Endereco - Bairro\": \"Bairro A\",
        \"Endereco - Cidade\": \"Cidade X\",
        \"Endereco - Estado\": \"Estado Y\",
        \"Endereco - Pais\": \"Pais Z\",
        \"wallet_config\": \"config_uba$i\",
        \"wallet_credentials\": \"credentials_uba$i\",
        \"balance\": $((i * 10)),
        \"preco_fardinho\": $((i * 100)),
        \"quant_fardinho\": $((i * 100000))
    },"
done
echo "]"
