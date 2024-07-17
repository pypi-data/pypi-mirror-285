# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyrogram import raw
from pyrogram.raw.core import TLObject

MediaArea = Union[raw.types.InputMediaAreaChannelPost, raw.types.InputMediaAreaVenue, raw.types.MediaAreaChannelPost, raw.types.MediaAreaGeoPoint, raw.types.MediaAreaSuggestedReaction, raw.types.MediaAreaUrl, raw.types.MediaAreaVenue]


# noinspection PyRedeclaration
class MediaArea:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 7 constructors available.

        .. currentmodule:: pyrogram.raw.types

        .. autosummary::
            :nosignatures:

            InputMediaAreaChannelPost
            InputMediaAreaVenue
            MediaAreaChannelPost
            MediaAreaGeoPoint
            MediaAreaSuggestedReaction
            MediaAreaUrl
            MediaAreaVenue
    """

    QUALNAME = "pyrogram.raw.base.MediaArea"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
