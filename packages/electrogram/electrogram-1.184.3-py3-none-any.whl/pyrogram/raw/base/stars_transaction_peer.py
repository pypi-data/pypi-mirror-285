# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyrogram import raw
from pyrogram.raw.core import TLObject

StarsTransactionPeer = Union[raw.types.StarsTransactionPeer, raw.types.StarsTransactionPeerAds, raw.types.StarsTransactionPeerAppStore, raw.types.StarsTransactionPeerFragment, raw.types.StarsTransactionPeerPlayMarket, raw.types.StarsTransactionPeerPremiumBot, raw.types.StarsTransactionPeerUnsupported]


# noinspection PyRedeclaration
class StarsTransactionPeer:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 7 constructors available.

        .. currentmodule:: pyrogram.raw.types

        .. autosummary::
            :nosignatures:

            StarsTransactionPeer
            StarsTransactionPeerAds
            StarsTransactionPeerAppStore
            StarsTransactionPeerFragment
            StarsTransactionPeerPlayMarket
            StarsTransactionPeerPremiumBot
            StarsTransactionPeerUnsupported
    """

    QUALNAME = "pyrogram.raw.base.StarsTransactionPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
