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


class GetBroadcastRevenueWithdrawalUrl(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``184``
        - ID: ``2A65EF73``

    Parameters:
        channel (:obj:`InputChannel <pyrogram.raw.base.InputChannel>`):
            N/A

        password (:obj:`InputCheckPasswordSRP <pyrogram.raw.base.InputCheckPasswordSRP>`):
            N/A

    Returns:
        :obj:`stats.BroadcastRevenueWithdrawalUrl <pyrogram.raw.base.stats.BroadcastRevenueWithdrawalUrl>`
    """

    __slots__: List[str] = ["channel", "password"]

    ID = 0x2a65ef73
    QUALNAME = "functions.stats.GetBroadcastRevenueWithdrawalUrl"

    def __init__(self, *, channel: "raw.base.InputChannel", password: "raw.base.InputCheckPasswordSRP") -> None:
        self.channel = channel  # InputChannel
        self.password = password  # InputCheckPasswordSRP

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetBroadcastRevenueWithdrawalUrl":
        # No flags
        
        channel = TLObject.read(b)
        
        password = TLObject.read(b)
        
        return GetBroadcastRevenueWithdrawalUrl(channel=channel, password=password)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.channel.write())
        
        b.write(self.password.write())
        
        return b.getvalue()
