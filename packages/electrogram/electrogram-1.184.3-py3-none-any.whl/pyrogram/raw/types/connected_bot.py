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


class ConnectedBot(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.ConnectedBot`.

    Details:
        - Layer: ``184``
        - ID: ``BD068601``

    Parameters:
        bot_id (``int`` ``64-bit``):
            N/A

        recipients (:obj:`BusinessBotRecipients <pyrogram.raw.base.BusinessBotRecipients>`):
            N/A

        can_reply (``bool``, *optional*):
            N/A

    """

    __slots__: List[str] = ["bot_id", "recipients", "can_reply"]

    ID = 0xbd068601
    QUALNAME = "types.ConnectedBot"

    def __init__(self, *, bot_id: int, recipients: "raw.base.BusinessBotRecipients", can_reply: Optional[bool] = None) -> None:
        self.bot_id = bot_id  # long
        self.recipients = recipients  # BusinessBotRecipients
        self.can_reply = can_reply  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ConnectedBot":
        
        flags = Int.read(b)
        
        can_reply = True if flags & (1 << 0) else False
        bot_id = Long.read(b)
        
        recipients = TLObject.read(b)
        
        return ConnectedBot(bot_id=bot_id, recipients=recipients, can_reply=can_reply)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.can_reply else 0
        b.write(Int(flags))
        
        b.write(Long(self.bot_id))
        
        b.write(self.recipients.write())
        
        return b.getvalue()
