from bullpenfi.auth import authenticator

def example_function(api_key):
    authenticator.authenticate(api_key)
    return "Hello, PyPI!"

def restricted_function(api_key):
    authenticator.authenticate(api_key)
    return "This is a restricted function"
