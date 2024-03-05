async def setup_identity(identity, trustee):
    print('cheguei no setup identity')
    did_safe = 'V4SGRU86Z58d6TV7PBUe6f'
    verkey_safe = '~CoRER63DVYnWZtK8uAzNbx'
    (identity['did'], identity['key']) = await did.create_and_store_my_did(identity['wallet'], "{}")
    nym_req = await ledger.build_nym_request(did_safe, identity['did'],identity['key'],None, None)
    await ledger.sign_and_submit_request(identity['pool'], trustee['wallet'], did_safe, nym_req)