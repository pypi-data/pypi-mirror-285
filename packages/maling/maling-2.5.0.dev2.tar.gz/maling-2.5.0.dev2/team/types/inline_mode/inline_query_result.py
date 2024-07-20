#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from uuid import uuid4

import team
from team import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~team.types.InlineQueryResultCachedAudio`
    - :obj:`~team.types.InlineQueryResultCachedDocument`
    - :obj:`~team.types.InlineQueryResultCachedAnimation`
    - :obj:`~team.types.InlineQueryResultCachedPhoto`
    - :obj:`~team.types.InlineQueryResultCachedSticker`
    - :obj:`~team.types.InlineQueryResultCachedVideo`
    - :obj:`~team.types.InlineQueryResultCachedVoice`
    - :obj:`~team.types.InlineQueryResultArticle`
    - :obj:`~team.types.InlineQueryResultAudio`
    - :obj:`~team.types.InlineQueryResultContact`
    - :obj:`~team.types.InlineQueryResultDocument`
    - :obj:`~team.types.InlineQueryResultAnimation`
    - :obj:`~team.types.InlineQueryResultLocation`
    - :obj:`~team.types.InlineQueryResultPhoto`
    - :obj:`~team.types.InlineQueryResultVenue`
    - :obj:`~team.types.InlineQueryResultVideo`
    - :obj:`~team.types.InlineQueryResultVoice`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "team.Client"):
        pass
