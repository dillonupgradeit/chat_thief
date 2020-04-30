from pathlib import Path

import pytest

from chat_thief.models.command import Command
from chat_thief.models.sfx_vote import SFXVote

from tests.support.database_setup import DatabaseConfig


class TestCommand(DatabaseConfig):
    def test_count(self):
        assert Command.count() == 0

    def test_allowed_to_play(self):
        subject = Command("help")
        assert subject.allowed_to_play("beginbot")

    def test_not_allowed_to_play_others_themes(self):
        subject = Command("artmattdank")
        assert subject.allowed_to_play("artmattdank")
        assert not subject.allowed_to_play("beginbot")

    def test_allow_user(self):
        subject = Command("clap")
        other_subject = Command("damn")
        assert not subject.allowed_to_play("spfar")
        assert not subject.allowed_to_play("rando")
        assert not other_subject.allowed_to_play("spfar")
        assert not other_subject.allowed_to_play("rando")
        subject.allow_user("spfar")
        other_subject.allow_user("rando")
        assert subject.allowed_to_play("spfar")
        assert not subject.allowed_to_play("rando")
        assert not other_subject.allowed_to_play("spfar")
        assert other_subject.allowed_to_play("rando")
        subject.allow_user("rando")
        assert subject.allowed_to_play("rando")

    def test_unallow(self):
        subject = Command("clap")
        other_subject = Command("damn")
        subject.allow_user("spfar")
        other_subject.allow_user("rando")

        assert subject.allowed_to_play("spfar")
        subject.unallow_user("spfar")
        assert not subject.allowed_to_play("spfar")

    @pytest.mark.focus
    def test_cost(self):
        subject = Command("clap")
        subject.save()
        assert subject.cost() == 1
        subject.increase_cost()
        assert subject.cost() == 2