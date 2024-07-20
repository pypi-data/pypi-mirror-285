################################################################
"""
 Mix-Userbot Open Source . Maintained ? Yes Oh No Oh Yes Ngentot
 
 @ CREDIT : NAN-DEV || Gojo_Satoru
"""
################################################################


from hashlib import md5
from threading import RLock
from time import time
from datetime import datetime
import pytz
from .class_mongo import MongoDB3
from .class_log import LOGGER

from Mix.core.msgty import Types

INSERTION_LOCK = RLock()


ANTISPAM_BANNED = set()

ANTISPAM_MUTE = set()

TZ = pytz.timezone("Asia/Jakarta")

class GMute(MongoDB3):
    """Class for managing GMute in bot."""

    db_name = "gmutes"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def check_gmute(self, user_id: int):
        with INSERTION_LOCK:
            return bool(self.find_one({"_id": user_id}))

    def add_gmute(self, user_id: int, reason: str, by_user: int):
        global ANTISPAM_MUTE
        with INSERTION_LOCK:
            # Check if  user is already gmutened or not
            if self.find_one({"_id": user_id}):
                return self.update_gmute_reason(user_id, reason)

            # If not already gmutened, then add to gmute
            time_rn = datetime.now(TZ)
            return self.insert_one(
                {
                    "_id": user_id,
                    "reason": reason,
                    "by": by_user,
                    "time": time_rn,
                },
            )

    def remove_gmute(self, user_id: int):
        global ANTISPAM_MUTE
        with INSERTION_LOCK:
            # Check if  user is already gmutened or not
            if self.find_one({"_id": user_id}):
                return self.delete_one({"_id": user_id})

            return "User not gmutened!"

    def get_gmute(self, user_id: int):
        if self.check_gmute(user_id):
            curr = self.find_one({"_id": user_id})
            if curr:
                return True, curr["reason"]
        return False, ""

    def update_gmute_reason(self, user_id: int, reason: str):
        with INSERTION_LOCK:
            return self.update(
                {"_id": user_id},
                {"reason": reason},
            )

    def count_gmutes(self):
        with INSERTION_LOCK:
            return self.count()

    def load_from_db(self):
        with INSERTION_LOCK:
            return self.find_all()

    def list_gmutes(self):
        with INSERTION_LOCK:
            return self.find_all()

class GBan(MongoDB3):
    """Class for managing Gbans in bot."""

    db_name = "gbans"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def check_gban(self, user_id: int):
        with INSERTION_LOCK:
            return bool(self.find_one({"_id": user_id}))

    def add_gban(self, user_id: int, reason: str, by_user: int):
        global ANTISPAM_BANNED
        with INSERTION_LOCK:
            # Check if  user is already gbanned or not
            if self.find_one({"_id": user_id}):
                return self.update_gban_reason(user_id, reason)

            # If not already gbanned, then add to gban
            time_rn = datetime.now(TZ)
            return self.insert_one(
                {
                    "_id": user_id,
                    "reason": reason,
                    "by": by_user,
                    "time": time_rn,
                },
            )

    def remove_gban(self, user_id: int):
        global ANTISPAM_BANNED
        with INSERTION_LOCK:
            # Check if  user is already gbanned or not
            if self.find_one({"_id": user_id}):
                return self.delete_one({"_id": user_id})

            return "User not gbanned!"

    def get_gban(self, user_id: int):
        if self.check_gban(user_id):
            curr = self.find_one({"_id": user_id})
            if curr:
                return True, curr["reason"]
        return False, ""

    def update_gban_reason(self, user_id: int, reason: str):
        with INSERTION_LOCK:
            return self.update(
                {"_id": user_id},
                {"reason": reason},
            )

    def count_gbans(self):
        with INSERTION_LOCK:
            return self.count()

    def load_from_db(self):
        with INSERTION_LOCK:
            return self.find_all()

    def list_gbans(self):
        with INSERTION_LOCK:
            return self.find_all()


class Greetings(MongoDB3):
    """Class for managing antichannelpins in chats."""

    # Database name to connect to to preform operations
    db_name = "welcome_chats"

    def __init__(self, chat_id: int) -> None:
        super().__init__(self.db_name)
        self.chat_id = chat_id
        self.chat_info = self.__ensure_in_db()

    # Get settings from database
    def get_welcome_status(self):
        with INSERTION_LOCK:
            return self.chat_info["welcome"]

    def get_goodbye_status(self):
        with INSERTION_LOCK:
            return self.chat_info["goodbye"]

    def get_current_cleanservice_settings(self):
        with INSERTION_LOCK:
            return self.chat_info["cleanservice"]

    def get_current_cleanwelcome_settings(self):
        with INSERTION_LOCK:
            return self.chat_info["cleanwelcome"]

    def get_current_cleangoodbye_settings(self):
        with INSERTION_LOCK:
            return self.chat_info["cleangoodbye"]

    def get_welcome_text(self):
        with INSERTION_LOCK:
            return self.chat_info["welcome_text"]

    def get_welcome_media(self):
        with INSERTION_LOCK:
            return self.chat_info["welcome_media"]

    def get_welcome_msgtype(self):
        with INSERTION_LOCK:
            return self.chat_info["welcome_mtype"]

    def get_goodbye_msgtype(self):
        with INSERTION_LOCK:
            return self.chat_info["goodbye_mtype"]

    def get_goodbye_media(self):
        with INSERTION_LOCK:
            return self.chat_info["goodbye_media"]

    def get_goodbye_text(self):
        with INSERTION_LOCK:
            return self.chat_info["goodbye_text"]

    def get_current_cleanwelcome_id(self):
        with INSERTION_LOCK:
            return self.chat_info["cleanwelcome_id"]

    def get_current_cleangoodbye_id(self):
        with INSERTION_LOCK:
            return self.chat_info["cleangoodbye_id"]

    # Set settings in database
    def set_current_welcome_settings(self, status: bool):
        with INSERTION_LOCK:
            return self.update({"_id": self.chat_id}, {"welcome": status})

    def set_current_goodbye_settings(self, status: bool):
        with INSERTION_LOCK:
            return self.update({"_id": self.chat_id}, {"goodbye": status})

    def set_welcome_text(self, welcome_text: str, mtype, media=None):
        with INSERTION_LOCK:
            self.update(
                {"_id": self.chat_id},
                {"welcome_text": welcome_text, "welcome_mtype": mtype},
            )
            if media:
                self.update(
                    {"_id": self.chat_id},
                    {"welcome_media": media, "welcome_mtype": mtype},
                )

            return

    def set_goodbye_text(self, goodbye_text: str, mtype, media=None):
        with INSERTION_LOCK:
            self.update(
                {"_id": self.chat_id},
                {"goodbye_text": goodbye_text, "goodbye_mtype": mtype},
            )
            if media:
                self.update(
                    {"_id": self.chat_id},
                    {"goodbye_media": media, "goodbye_mtype": mtype},
                )
                return

    def set_current_cleanservice_settings(self, status: bool):
        with INSERTION_LOCK:
            return self.update(
                {"_id": self.chat_id},
                {"cleanservice": status},
            )

    def set_current_cleanwelcome_settings(self, status: bool):
        with INSERTION_LOCK:
            return self.update(
                {"_id": self.chat_id},
                {"cleanwelcome": status},
            )

    def set_current_cleangoodbye_settings(self, status: bool):
        with INSERTION_LOCK:
            return self.update(
                {"_id": self.chat_id},
                {"cleangoodbye": status},
            )

    def set_cleanwlcm_id(self, status: int):
        with INSERTION_LOCK:
            return self.update(
                {"_id": self.chat_id},
                {"cleanwelcome_id": status},
            )

    def set_cleangoodbye_id(self, status: int):
        with INSERTION_LOCK:
            return self.update(
                {"_id": self.chat_id},
                {"cleangoodbye_id": status},
            )

    def __ensure_in_db(self):
        chat_data = self.find_one({"_id": self.chat_id})
        if not chat_data:
            new_data = {
                "_id": self.chat_id,
                "cleanwelcome": False,
                "cleanwelcome_id": None,
                "cleangoodbye_id": None,
                "cleangoodbye": False,
                "cleanservice": False,
                "goodbye_text": "Sad to see you leaving {fullname}.\nTake Care!",
                "welcome_text": "Hey {fullname}, welcome to {chatname}!",
                "welcome": False,
                "goodbye": False,
                "welcome_media": False,
                "welcome_mtype": False,
                "goodbye_media": False,
                "goodbye_mtype": False,
            }
            self.insert_one(new_data)
            LOGGER(__name__).info(
                f"Initialized Greetings Document for chat {self.chat_id}"
            )
            return new_data
        return chat_data

    # Migrate if chat id changes!
    def migrate_chat(self, new_chat_id: int):
        old_chat_db = self.find_one({"_id": self.chat_id})
        new_data = old_chat_db.update({"_id": new_chat_id})
        self.insert_one(new_data)
        self.delete_one({"_id": self.chat_id})

    def clean_greetings(self):
        with INSERTION_LOCK:
            return self.delete_one({"_id": self.chat_id})

    @staticmethod
    def count_chats(query: str):
        with INSERTION_LOCK:
            collection = MongoDB3(Greetings.db_name)
            return collection.count({query: True})


class Users(MongoDB3):
    """Class to manage users for bot."""

    db_name = "users"

    def __init__(self, user_id: int) -> None:
        super().__init__(self.db_name)
        self.user_id = user_id
        self.user_info = self.__ensure_in_db()

    def update_user(self, name: str, username: str = None):
        with INSERTION_LOCK:
            if name != self.user_info["name"] or username != self.user_info["username"]:
                return self.update(
                    {"_id": self.user_id},
                    {"username": username, "name": name},
                )
            return True

    def delete_user(self):
        with INSERTION_LOCK:
            return self.delete_one({"_id": self.user_id})

    @staticmethod
    def count_users():
        with INSERTION_LOCK:
            collection = MongoDB3(Users.db_name)
            return collection.count()

    def get_my_info(self):
        with INSERTION_LOCK:
            return self.user_info

    @staticmethod
    def list_users():
        with INSERTION_LOCK:
            collection = MongoDB3(Users.db_name)
            return collection.find_all()

    @staticmethod
    def get_user_info(user_id: int or str):
        with INSERTION_LOCK:
            collection = MongoDB3(Users.db_name)
            if isinstance(user_id, int):
                curr = collection.find_one({"_id": user_id})
            elif isinstance(user_id, str):
                # user_id[1:] because we don't want the '@' in the username
                # search!
                curr = collection.find_one({"username": user_id[1:]})
            else:
                curr = None

            if curr:
                return curr

            return {}

    def __ensure_in_db(self):
        chat_data = self.find_one({"_id": self.user_id})
        if not chat_data:
            new_data = {"_id": self.user_id, "username": "", "name": "unknown_till_now"}
            self.insert_one(new_data)
            LOGGER(__name__).info(f"Initialized User Document for {self.user_id}")
            return new_data
        return chat_data

    @staticmethod
    def load_from_db():
        with INSERTION_LOCK:
            collection = MongoDB3(Users.db_name)
            return collection.find_all()

    @staticmethod
    def repair_db(collection):
        all_data = collection.find_all()
        keys = {"username": "", "name": "unknown_till_now"}
        for data in all_data:
            for key, val in keys.items():
                try:
                    _ = data[key]
                except KeyError:
                    LOGGER(__name__).warning(
                        f"Repairing Users Database - setting '{key}:{val}' for {data['_id']}",
                    )
                    collection.update({"_id": data["_id"]}, {key: val})


def __pre_req_users():
    start = time()
    LOGGER(__name__).info("Starting Users Database Repair...")
    collection = MongoDB3(Users.db_name)
    Users.repair_db(collection)
    LOGGER(__name__).info(f"Done in {round((time() - start), 3)}s!")


class LOCKS(MongoDB3):
    """Class to store locks"""

    db_name = "locks"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def insert_lock_channel(self, chat: int, locktype: str):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        curr = self.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            return False
        else:
            with INSERTION_LOCK:
                hmm = self.merge_u_and_c(chat, locktype)
                if not hmm:
                    self.insert_one({"chat_id": chat, "locktype": locktype})
            return True

    def remove_lock_channel(self, chat: int, locktype: str):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        curr = self.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            with INSERTION_LOCK:
                self.delete_one({"chat_id": chat, "locktype": locktype})
            return True
        else:
            return False

    def get_lock_channel(self, locktype: str = "all"):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        if locktype not in [
            "anti_c_send",
            "anti_fwd",
            "anti_fwd_u",
            "anti_fwd_c",
            "anti_links",
            "all",
        ]:
            return False
        else:
            if locktype == "all":
                find = {}
            else:
                find = {"locktype": locktype}
            curr = self.find_all(find)
            if not curr:
                list_ = []
            else:
                list_ = [i["chat_id"] for i in curr]
            return list_

    def merge_u_and_c(self, chat: int, locktype: str):
        if locktype == "anti_fwd_u":
            curr = self.find_one({"chat_id": chat, "locktype": "anti_fwd_c"})
        elif locktype == "anti_fwd_c":
            curr = self.find_one({"chat_id": chat, "locktype": "anti_fwd_u"})
        else:
            return False

        if curr:
            self.delete_one({"chat_id": chat, "locktype": locktype})
            self.insert_one({"chat_id": chat, "locktype": "anti_fwd"})
            return True
        else:
            return False

    def is_particular_lock(self, chat: int, locktype: str):
        """
        locktypes: anti_c_send, anti_fwd, anti_fwd_u, anti_fwd_c, anti_links
        """
        curr = self.find_one({"chat_id": chat, "locktype": locktype})
        if curr:
            return True
        else:
            return False


class Approve(MongoDB3):
    """Class for managing Approves in Chats in Bot."""

    # Database name to connect to to preform operations
    db_name = "approve"

    def __init__(self, chat_id: int) -> None:
        super().__init__(self.db_name)
        self.chat_id = chat_id
        self.chat_info = self.__ensure_in_db()

    def check_approve(self, user_id: int):
        with INSERTION_LOCK:
            if not self.chat_info["users"]:
                return False
            for i in self.chat_info["users"]:
                if user_id in i:
                    j = True
                    break
                else:
                    j = False
            return j

    def add_approve(self, user_id: int, user_name: str):
        with INSERTION_LOCK:
            if not self.check_approve(user_id):
                self.chat_info["users"].append((user_id, user_name))
                return self.update(
                    {"_id": self.chat_id},
                    {"users": self.chat_info["users"]},
                )
            return True

    def remove_approve(self, user_id: int):
        with INSERTION_LOCK:
            if self.check_approve(user_id):
                inde = 0
                for index, user in enumerate(self.chat_info["users"]):
                    if user[0] == user_id:
                        inde = index
                        break
                self.chat_info["users"].pop(inde)
                return self.update(
                    {"_id": self.chat_id},
                    {"users": self.chat_info["users"]},
                )
            return True

    def unapprove_all(self):
        with INSERTION_LOCK:
            return self.delete_one(
                {"_id": self.chat_id},
            )

    def clean_approve(self):
        with INSERTION_LOCK:
            return self.delete_one({"_id": self.chat_id})

    def list_approved(self):
        with INSERTION_LOCK:
            return self.chat_info["users"]

    def count_approved(self):
        with INSERTION_LOCK:
            return len(self.chat_info["users"])

    def load_from_db(self):
        return self.find_all()

    def __ensure_in_db(self):
        chat_data = self.find_one({"_id": self.chat_id})
        if not chat_data:
            new_data = {"_id": self.chat_id, "users": []}
            self.insert_one(new_data)
            LOGGER(__name__).info(
                f"Initialized Approve Document for chat {self.chat_id}"
            )
            return new_data
        return chat_data

    # Migrate if chat id changes!
    def migrate_chat(self, new_chat_id: int):
        old_chat_db = self.find_one({"_id": self.chat_id})
        new_data = old_chat_db.update({"_id": new_chat_id})
        self.insert_one(new_data)
        self.delete_one({"_id": self.chat_id})

    @staticmethod
    def count_all_approved():
        with INSERTION_LOCK:
            collection = MongoDB3(Approve.db_name)
            all_data = collection.find_all()
            return sum(len(i["users"]) for i in all_data if len(i["users"]) >= 1)

    @staticmethod
    def count_approved_chats():
        with INSERTION_LOCK:
            collection = MongoDB3(Approve.db_name)
            all_data = collection.find_all()
            return sum(len(i["users"]) >= 1 for i in all_data)

    @staticmethod
    def repair_db(collection):
        all_data = collection.find_all()
        keys = {"users": []}
        for data in all_data:
            for key, val in keys.items():
                try:
                    _ = data[key]
                except KeyError:
                    LOGGER(__name__).warning(
                        f"Repairing Approve Database - setting '{key}:{val}' for {data['_id']}",
                    )
                    collection.update({"_id": data["_id"]}, {key: val})


class Notes(MongoDB3):
    db_name = "notes"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def save_note(
        self,
        chat_id: int,
        note_name: str,
        note_value: str,
        msgtype: int = Types.TEXT,
        fileid="",
    ):
        with INSERTION_LOCK:
            curr = self.find_one(
                {"chat_id": chat_id, "note_name": note_name},
            )
            if curr:
                return False
            hash_gen = md5(
                (note_name + note_value + str(chat_id) + str(int(time()))).encode(),
            ).hexdigest()
            return self.insert_one(
                {
                    "chat_id": chat_id,
                    "note_name": note_name,
                    "note_value": note_value,
                    "hash": hash_gen,
                    "msgtype": msgtype,
                    "fileid": fileid,
                },
            )

    def get_note(self, chat_id: int, note_name: str):
        with INSERTION_LOCK:
            curr = self.find_one(
                {"chat_id": chat_id, "note_name": note_name},
            )
            if curr:
                return curr
            return "Note does not exist!"

    def get_note_by_hash(self, note_hash: str):
        return self.find_one({"hash": note_hash})

    def get_all_notes(self, chat_id: int):
        with INSERTION_LOCK:
            curr = self.find_all({"chat_id": chat_id})
            note_list = sorted([(note["note_name"], note["hash"]) for note in curr])
            return note_list

    def rm_note(self, chat_id: int, note_name: str):
        with INSERTION_LOCK:
            curr = self.find_one(
                {"chat_id": chat_id, "note_name": note_name},
            )
            if curr:
                self.delete_one(curr)
                return True
            return False

    def rm_all_notes(self, chat_id: int):
        with INSERTION_LOCK:
            return self.delete_one({"chat_id": chat_id})

    def count_notes(self, chat_id: int):
        with INSERTION_LOCK:
            curr = self.find_all({"chat_id": chat_id})
            if curr:
                return len(curr)
            return 0

    def count_notes_chats(self):
        with INSERTION_LOCK:
            notes = self.find_all()
            chats_ids = [chat["chat_id"] for chat in notes]
            return len(set(chats_ids))

    def count_all_notes(self):
        with INSERTION_LOCK:
            return self.count()

    def count_notes_type(self, ntype):
        with INSERTION_LOCK:
            return self.count({"msgtype": ntype})

    # Migrate if chat id changes!
    def migrate_chat(self, old_chat_id: int, new_chat_id: int):
        with INSERTION_LOCK:
            old_chat_db = self.find_one({"_id": old_chat_id})
            if old_chat_db:
                new_data = old_chat_db.update({"_id": new_chat_id})
                self.delete_one({"_id": old_chat_id})
                self.insert_one(new_data)


class NotesSettings(MongoDB3):
    db_name = "notes_settings"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def set_privatenotes(self, chat_id: int, status: bool = False):
        curr = self.find_one({"_id": chat_id})
        if curr:
            return self.update({"_id": chat_id}, {"privatenotes": status})
        return self.insert_one({"_id": chat_id, "privatenotes": status})

    def get_privatenotes(self, chat_id: int):
        curr = self.find_one({"_id": chat_id})
        if curr:
            return curr["privatenotes"]
        self.update({"_id": chat_id}, {"privatenotes": False})
        return False

    def clean_notes(self, chat_id):
        with INSERTION_LOCK:
            return self.delete_one({"_id": chat_id})

    def list_chats(self):
        return self.find_all({"privatenotes": True})

    def count_chats(self):
        return len(self.find_all({"privatenotes": True}))

    # Migrate if chat id changes!
    def migrate_chat(self, old_chat_id: int, new_chat_id: int):
        with INSERTION_LOCK:
            old_chat_db = self.find_one({"_id": old_chat_id})
            if old_chat_db:
                new_data = old_chat_db.update({"_id": new_chat_id})
                self.delete_one({"_id": old_chat_id})
                self.insert_one(new_data)


class Filters(MongoDB3):
    db_name = "chat_filters"

    def __init__(self) -> None:
        super().__init__(self.db_name)

    def save_filter(
        self,
        chat_id: int,
        keyword: str,
        filter_reply: str,
        msgtype: int = Types.TEXT,
        fileid="",
    ):
        with INSERTION_LOCK:
            # Database update
            curr = self.find_one({"chat_id": chat_id, "keyword": keyword})
            if curr:
                return False
            return self.insert_one(
                {
                    "chat_id": chat_id,
                    "keyword": keyword,
                    "filter_reply": filter_reply,
                    "msgtype": msgtype,
                    "fileid": fileid,
                },
            )

    def get_filter(self, chat_id: int, keyword: str):
        with INSERTION_LOCK:
            curr = self.find_one({"chat_id": chat_id, "keyword": keyword})
            if curr:
                return curr
            return "Filter does not exist!"

    def get_all_filters(self, chat_id: int):
        with INSERTION_LOCK:
            curr = self.find_all({"chat_id": chat_id})
            if curr:
                filter_list = {i["keyword"] for i in curr}
                return list(filter_list)
            return []

    def rm_filter(self, chat_id: int, keyword: str):
        with INSERTION_LOCK:
            curr = self.find_one({"chat_id": chat_id, "keyword": keyword})
            if curr:
                self.delete_one(curr)
                return True
            return False

    def rm_all_filters(self, chat_id: int):
        with INSERTION_LOCK:
            return self.delete_one({"chat_id": chat_id})

    def count_filters_all(self):
        with INSERTION_LOCK:
            return self.count()

    def count_filter_aliases(self):
        with INSERTION_LOCK:
            curr = self.find_all()
            if curr:
                return len(
                    [z for z in (i["keyword"].split("|") for i in curr) if len(z) >= 2],
                )
            return 0

    def count_filters_chats(self):
        with INSERTION_LOCK:
            filters = self.find_all()
            chats_ids = {i["chat_id"] for i in filters}
            return len(chats_ids)

    def count_all_filters(self):
        with INSERTION_LOCK:
            return self.count()

    def count_filter_type(self, ntype):
        with INSERTION_LOCK:
            return self.count({"msgtype": ntype})

    def load_from_db(self):
        with INSERTION_LOCK:
            return self.find_all()

    # Migrate if chat id changes!
    def migrate_chat(self, old_chat_id: int, new_chat_id: int):
        with INSERTION_LOCK:
            old_chat_db = self.find_one({"_id": old_chat_id})
            if old_chat_db:
                new_data = old_chat_db.update({"_id": new_chat_id})
                self.delete_one({"_id": old_chat_id})
                self.insert_one(new_data)
