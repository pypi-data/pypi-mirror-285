from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class BotBusinessConnection(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.BotBusinessConnection`.

    Details:
        - Layer: ``184``
        - ID: ``896433B4``

    Parameters:
        connection_id (``str``):
            N/A

        user_id (``int`` ``64-bit``):
            N/A

        dc_id (``int`` ``32-bit``):
            N/A

        date (``int`` ``32-bit``):
            N/A

        can_reply (``bool``, *optional*):
            N/A

        disabled (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["connection_id", "user_id", "dc_id", "date", "can_reply", "disabled"]

    ID = 0x896433b4
    QUALNAME = "types.BotBusinessConnection"

    def __init__(self, *, connection_id: str, user_id: int, dc_id: int, date: int, can_reply: Optional[bool] = None, disabled: Optional[bool] = None) -> None:
        self.connection_id = connection_id  # string
        self.user_id = user_id  # long
        self.dc_id = dc_id  # int
        self.date = date  # int
        self.can_reply = can_reply  # flags.0?true
        self.disabled = disabled  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BotBusinessConnection":
        
        flags = Int.read(b)
        
        can_reply = True if flags & (1 << 0) else False
        disabled = True if flags & (1 << 1) else False
        connection_id = String.read(b)
        
        user_id = Long.read(b)
        
        dc_id = Int.read(b)
        
        date = Int.read(b)
        
        return BotBusinessConnection(connection_id=connection_id, user_id=user_id, dc_id=dc_id, date=date, can_reply=can_reply, disabled=disabled)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.can_reply else 0
        flags |= (1 << 1) if self.disabled else 0
        b.write(Int(flags))
        
        b.write(String(self.connection_id))
        
        b.write(Long(self.user_id))
        
        b.write(Int(self.dc_id))
        
        b.write(Int(self.date))
        
        return b.getvalue()
