async def create_wallet(Entidade):
    print("\"{}\" -> Criando Carteira(wallet)".format(Entidade['name']))

    try:
        await wallet.create_wallet(Entidade['wallet_config'],
                                   Entidade['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
        else:
            raise ex

    Entidade['wallet'] = await wallet.open_wallet(Entidade['wallet_config'],
                                                  Entidade['wallet_credentials'])
    
def create_seed(contador, nome):
        seed =  str(nome) + str(contador) + 'A0000000000000000000000000000000000' 
        return seed[:32]