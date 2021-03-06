from typing import List

from tinydb import Query

from chat_thief.models.database import db_table
from chat_thief.models.base_db_model import BaseDbModel


class SFXVote(BaseDbModel):
    table_name = "sfx_votes"
    database_path = "db/sfx_votes.json"

    def is_enabled(self):
        if self.supporter_count() == 0 and self.detractor_count() == 0:
            return True

        return self.supporter_count() >= self.detractor_count()

    def __init__(self, command, supporters=[], detractors=[]):
        self.command = command
        self.supporters = supporters
        self.detractors = detractors

    def support(self, supporter):
        vote = self._find_or_create_vote()

        def show_support(supporter):
            def transform(doc):
                if supporter not in doc["supporters"]:
                    doc["supporters"].append(supporter)
                if supporter in doc["detractors"]:
                    doc["detractors"].remove(supporter)

            return transform

        self.db().update(show_support(supporter), Query().command == self.command)
        # We are returning Dict
        return self._find_or_create_vote()

    def detract(self, detractor):
        vote = self._find_or_create_vote()

        def detract_support(detractor):
            def transform(doc):
                if detractor not in doc["detractors"]:
                    doc["detractors"].append(detractor)
                if detractor in doc["supporters"]:
                    doc["supporters"].remove(detractor)

            return transform

        self.db().update(detract_support(detractor), Query().command == self.command)
        return self._find_or_create_vote()

    def like_to_hate_ratio(self):
        if self.detractor_count() < 1:
            return 100
        total = self.supporter_count() + self.detractor_count()
        return (self.supporter_count() / total) * 100

    def supporter_count(self):
        vote = self._find_or_create_vote()
        return len(vote["supporters"])

    def detractor_count(self):
        vote = self._find_or_create_vote()
        return len(vote["detractors"])

    def _find_or_create_vote(self):
        vote = self.db().get(Query().command == self.command)

        if vote:
            return vote
        else:
            print(f"Creating New SFXVote: {self.doc()}")
            from tinyrecord import transaction

            with transaction(self.db()) as tr:
                tr.insert(self.doc())
            return self.doc()

    def doc(self):
        return {
            "command": self.command,
            "supporters": self.supporters,
            "detractors": self.detractors,
        }
