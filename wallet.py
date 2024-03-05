from indy_vdr.bindings import Wallet

async def create_wallet(Entidade):
    print("\"{}\" -> Criando Carteira(wallet)".format(Entidade['name']))

    try:
        Entidade['wallet'] = await Wallet.create(Entidade['wallet_config'], Entidade['wallet_credentials'])
    except Exception as ex:
        print("A carteira já existe. Abrindo a carteira existente.")
        Entidade['wallet'] = await Wallet.open(Entidade['wallet_config'], Entidade['wallet_credentials'])

def create_seed(contador, nome):
    seed =  str(nome) + str(contador) + 'A0000000000000000000000000000000000' 
    return seed[:32]