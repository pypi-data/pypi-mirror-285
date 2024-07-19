__version__="0.1.3.5"
__prefix__="python-ultra-auth"
__repo__="https://github.com/sbarbett/ultra_auth"

def get_client_user_agent() :
    return f"{__prefix__}/v{__version__} (+{__repo__})"