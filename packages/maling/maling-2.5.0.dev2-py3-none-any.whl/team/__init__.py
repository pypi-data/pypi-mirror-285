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


__version__ = "2.5.0-dev2"
__license__ = "GNU Lesser General Public License v3.0 (LGPL-3.0)"
__copyright__ = "Copyright (C) 2017-present Dan <https://github.com/delivrance>"

from concurrent.futures.thread import ThreadPoolExecutor


class StopTransmission(Exception):
    pass


class StopPropagation(StopAsyncIteration):
    pass


class ContinuePropagation(StopAsyncIteration):
    pass


from . import raw, types, filters, handlers, emoji, enums
from .client import Client
from .sync import idle, compose
from .nandev.class_log import LOGGER
from .nandev.database import ndB, udB
from .nandev.autopilot import autobot
from .nandev.class_handler import ky, human, TAG_LOG, refresh_cache, isFinish
from .nandev.class_modules import CMD_HELP, paginate_modules
from .nandev.class_emoji import Emojik
from .nandev.class_pytgc import unpackInlineMessage, run_sync, YoutubeDownload, YouTubeSearch
from .nandev.new_database import Greetings, Users, LOCKS, Approve, Notes, NotesSettings, Filters, GBan, GMute


crypto_executor = ThreadPoolExecutor(1, thread_name_prefix="CryptoWorker")

