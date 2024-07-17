# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyrogram import raw
from pyrogram.raw.core import TLObject

InputFileLocation = Union[raw.types.InputDocumentFileLocation, raw.types.InputEncryptedFileLocation, raw.types.InputFileLocation, raw.types.InputGroupCallStream, raw.types.InputPeerPhotoFileLocation, raw.types.InputPeerPhotoFileLocationLegacy, raw.types.InputPhotoFileLocation, raw.types.InputPhotoLegacyFileLocation, raw.types.InputSecureFileLocation, raw.types.InputStickerSetThumb, raw.types.InputStickerSetThumbLegacy, raw.types.InputTakeoutFileLocation]


# noinspection PyRedeclaration
class InputFileLocation:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 12 constructors available.

        .. currentmodule:: pyrogram.raw.types

        .. autosummary::
            :nosignatures:

            InputDocumentFileLocation
            InputEncryptedFileLocation
            InputFileLocation
            InputGroupCallStream
            InputPeerPhotoFileLocation
            InputPeerPhotoFileLocationLegacy
            InputPhotoFileLocation
            InputPhotoLegacyFileLocation
            InputSecureFileLocation
            InputStickerSetThumb
            InputStickerSetThumbLegacy
            InputTakeoutFileLocation
    """

    QUALNAME = "pyrogram.raw.base.InputFileLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
