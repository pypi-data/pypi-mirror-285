from __future__ import annotations

from typing import TypeAlias

from .base import CryptProvider, IdentityProvider    


ProviderMap: TypeAlias = dict[str, type[CryptProvider] | None]


def _get_dome_providers() -> ProviderMap:
    from ._cryptodome import DomeAES128Provider, DomeARC4Provider

    return {"ARC4": DomeARC4Provider, "AESV2": DomeAES128Provider, 
            "Identity": IdentityProvider}
    

def load_providers() -> ProviderMap:
    provider_functions = [_get_dome_providers]

    for function in provider_functions:
        try:
            return function()
        except ImportError:
            pass

    return {"ARC4": None, "AESV2": None, "Identity": IdentityProvider}


CRYPT_PROVIDERS = load_providers()
