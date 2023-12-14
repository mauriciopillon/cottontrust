INSTRUÇÕES PARA RODAR TESTES:
Cada pasta tem o seu próprio arquivo ".env", que deve ser inserido na pasta "~/von-network", sendo parâmetro para a rede.
mv .env /home/ubuntu/cottontrust/von-network

Depois, o arquivo de script "von_generate_transactions" de cada pasta é modificado para seu respectivo número de nodos. Ele precisa ser 
substituído na pasta "~/von-network/bin"
mv von_generate_transactions /home/ubuntu/cottontrust/von-network/bin

O mesmo tem de ser feito para os arquivos e suas respectivas pastas:

Arquivo: "start_nodes.sh"       ---->    Pasta: "~/von-network/scripts"
mv start_nodes.sh /home/ubuntu/cottontrust/von-network/scripts

Arquivo: "docker-compose.yml"   ---->    Pasta: "~/von-network"
mv docker-compose.yml /home/ubuntu/cottontrust/von-network

Arquivo: "manage"               ---->    Pasta: "~/von-network"
mv manage /home/ubuntu/cottontrust/von-network

Após tudo isso, vá até a pasta "~/von-network" e execute o comando "./manage rebuild" e quando ele terminar de executar, "./manage start".
Isso *deve* funcionar. :D