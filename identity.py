from indy_vdr.bindings import RequestBuilder

async def setup_identity(identity, trustee):
    print('cheguei no setup identity')
    did_safe = 'V4SGRU86Z58d6TV7PBUe6f'
    verkey_safe = '~CoRER63DVYnWZtK8uAzNbx'
    (identity['did'], identity['key']) = await Did.create_and_store_my_did(identity['wallet'], "{}")

    # Create the nym request
    nym_request = RequestBuilder.build_nym_request(
        submitter_did=did_safe,
        target_did=identity['did'],
        ver_key=identity['key'],
        alias=None,
        role=None
    )

    # Sign the request
    signed_request = await identity['wallet'].sign_request(did_safe, nym_request)

    # Submit the request
    response = await identity['pool'].submit_request(signed_request)