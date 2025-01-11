def headers_authorization(token):

    auth_token = 'Bearer '+token

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': auth_token
    }

    return headers