from indy_vdr.bindings import Pool, Wallet, Did, RequestBuilder

async def create_transaction(sender, receiver, custo_far, quant_far):
    global cont_Tran
    cont_Tran += 1

    amount = custo_far * quant_far
    print("--------------------------------------------")
    print(f"Iniciando trasacao {cont_Tran}:")
    print(f"Saldo atual de {sender['name']}: R${sender['balance']},00")
    print(f"Saldo atual de {receiver['name']}: R${receiver['balance']},00")
    print(f"Quantidade de Fardinhos disponiveis em {receiver['name']}: {receiver['quant_fardinho']}")
    print(f"Quantidade de Fardinhos que {sender['name']} quer comprar: {quant_far}")
    print(f"Preco de cada Fardinho: R${custo_far},00")
    print(f"Valor total da transacao: R${amount},00")

    start_time = time.time()

    # Verifique se o remetente tem saldo suficiente
    if sender['balance'] < amount:
        print(f"{sender['name']} nao tem saldo suficiente para a transacao de compra dos fardinhos")
        return

    # Atualize o saldo do remetente
    sender['balance'] -= amount

    # Atualize a quantidade de Fardinhos do remetente
    sender['quant_fardinho'] += quant_far

    # Construa a solicitação de atributo para o remetente
    sender_attr_req = RequestBuilder.build_attrib_request(sender['did'], sender['did'], None, json.dumps({'balance': sender['balance'], 'quant_fardinho': sender['quant_fardinho']}), None)

    # Assine e envie a solicitação de atributo para o remetente
    signed_request = await sender['wallet'].sign_request(sender['did'], sender_attr_req)
    await sender['pool'].submit_request(signed_request)

    # Atualize o saldo do destinatário
    receiver['balance'] += amount

    # Atualize a quantidade de Fardinhos do destinatário
    receiver['quant_fardinho'] -= quant_far

    # Construa a solicitação de atributo para o destinatário
    receiver_attr_req = RequestBuilder.build_attrib_request(receiver['did'], receiver['did'], None, json.dumps({'balance': receiver['balance'], 'quant_fardinho': receiver['quant_fardinho']}), None)

    # Assine e envie a solicitação de atributo para o destinatário
    signed_request = await receiver['wallet'].sign_request(receiver['did'], receiver_attr_req)
    await receiver['pool'].submit_request(signed_request)

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nA transacao levou {duration} segundos para ser concluida\n")
    tempos_transacao.append(duration)

    print(f"Transacao concluida: {sender['name']} enviou R${amount},00 para {receiver['name']} e recebeu {quant_far} Fardinhos")
    print(f"Saldo atual de {sender['name']}: R${sender['balance']},00 e {sender['quant_fardinho']} Fardinhos")
    print(f"Saldo atual de {receiver['name']}: R${receiver['balance']},00 e {receiver['quant_fardinho']} Fardinhos")
    print("--------------------------------------------")