from tinydb import Query
from datetime import datetime
import time

from chat_thief.models.base_db_model import BaseDbModel

DEFAULT_EXPIRE_TIME_IN_SECS = 120


class Proposal(BaseDbModel):
    table_name = "proposals"
    database_path = "db/proposals.json"
    EXPIRE_TIME_IN_SECS = DEFAULT_EXPIRE_TIME_IN_SECS

    def __init__(self, user, command, proposal):
        self.user = user
        self.command = command
        self.proposal = proposal
        self.supporters = []

    def is_expired(self):
        info = self.db().get(Query().user == self.user)
        current_time = datetime.fromtimestamp(time.time())
        proposed_at = datetime.fromisoformat(info['proposed_at'])
        elapsed_time = current_time - proposed_at

        return elapsed_time.seconds >= self.EXPIRE_TIME_IN_SECS

    @classmethod
    def support(cls, user, doc_id, supporter):
        def add_support(supporter):
            def transform(doc):
                if supporter not in doc["supporters"]:
                    doc["supporters"].append(supporter)

            return transform

        cls.db().update(add_support(supporter), doc_ids=[doc_id])
        return f"@{user} thanks you for the support @{supporter}"

    @classmethod
    def find_by_user(cls, user):
        return cls.db().get(Query().user == user)

    def doc(self):
        proposed_at = str(datetime.fromtimestamp(time.time()))

        return {
            "user": self.user,
            "command": self.command,
            "proposal": self.proposal,
            "supporters": self.supporters,
            "proposed_at": proposed_at,
        }
