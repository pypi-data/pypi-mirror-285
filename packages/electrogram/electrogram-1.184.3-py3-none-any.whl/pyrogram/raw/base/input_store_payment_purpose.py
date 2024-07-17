# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyrogram import raw
from pyrogram.raw.core import TLObject

InputStorePaymentPurpose = Union[raw.types.InputStorePaymentGiftPremium, raw.types.InputStorePaymentPremiumGiftCode, raw.types.InputStorePaymentPremiumGiveaway, raw.types.InputStorePaymentPremiumSubscription, raw.types.InputStorePaymentStars]


# noinspection PyRedeclaration
class InputStorePaymentPurpose:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 5 constructors available.

        .. currentmodule:: pyrogram.raw.types

        .. autosummary::
            :nosignatures:

            InputStorePaymentGiftPremium
            InputStorePaymentPremiumGiftCode
            InputStorePaymentPremiumGiveaway
            InputStorePaymentPremiumSubscription
            InputStorePaymentStars
    """

    QUALNAME = "pyrogram.raw.base.InputStorePaymentPurpose"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
