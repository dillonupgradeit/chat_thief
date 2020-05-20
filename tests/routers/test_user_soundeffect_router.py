import pytest
from chat_thief.routers.user_soundeffect_router import UserSoundeffectRouter
from chat_thief.welcome_committee import WelcomeCommittee
from chat_thief.models.command import Command
from chat_thief.models.user import User
from chat_thief.models.sfx_vote import SFXVote

from tests.support.database_setup import DatabaseConfig


class TestUserSoundeffectRouter(DatabaseConfig):
    @pytest.fixture
    def mock_find_random_user(self, monkeypatch):
        def _fake_find_random_user(self):
            return "thugga"

        monkeypatch.setattr(
            UserSoundeffectRouter, "_random_user", _fake_find_random_user
        )

    @pytest.fixture(autouse=True)
    def mock_present_users(self, monkeypatch):
        def _mock_present_users(self):
            return ["not_streamlord", "young.thug", "uzi"]

        monkeypatch.setattr(WelcomeCommittee, "present_users", _mock_present_users)

    def test_me(self):
        result = UserSoundeffectRouter("beginbotbot", "me", []).route()
        assert result == "@beginbotbot - Mana: 3 | Street Cred: 0 | Cool Points: 0"

    def test_perms(self):
        result = UserSoundeffectRouter("beginbotbot", "perms", ["clap"]).route()
        assert result == "!clap | Cost: 1 | Health: 0 | Like Ratio 100%"

    def test_donate(self):
        Command("clap").allow_user("thugga")
        assert "thugga" in Command("clap").users()
        result = UserSoundeffectRouter("thugga", "donate", []).route()
        assert "thugga" not in Command("clap").users()
        assert "was gifted" in result[0]

    def test_hate_and_like_command(self):
        assert SFXVote("clap").supporter_count() == 0
        assert SFXVote("clap").detractor_count() == 0
        result = UserSoundeffectRouter("thugga", "like", ["clap"]).route()
        assert SFXVote("clap").supporter_count() == 1
        result = UserSoundeffectRouter("future", "hate", ["clap"]).route()
        assert SFXVote("clap").detractor_count() == 1

    def test_you_cannot_love_yourself(self):
        user = "young.thug"
        result = UserSoundeffectRouter("young.thug", "love", ["@young.thug"]).route()
        assert (
            result
            == "You can love yourself in real life, but not in Beginworld @young.thug"
        )

    def test_props(self):
        young_thug = User("young.thug")
        uzi = User("uzi")

        uzi.update_street_cred(10)

        assert young_thug.cool_points() == 0
        assert young_thug.street_cred() == 0
        assert uzi.street_cred() == 10

        result = UserSoundeffectRouter(uzi.name, "props", [young_thug.name]).route()
        assert young_thug.cool_points() == 1
        assert young_thug.street_cred() == 0
        assert uzi.street_cred() == 9

    def test_steal_with_no_params(self, mock_find_random_user):
        thugga = User("thugga")
        thugga.update_cool_points(10)
        Command("damn").allow_user("thugga")
        user = User("beginbot")
        user.update_cool_points(10)
        result = UserSoundeffectRouter(user.name, "steal", []).route()
        result == "@beginbot stole from @thugga"
        assert user.cool_points() == 9

    def test_buying_random(self, mock_find_random_user):
        user = "young.thug"
        User(user).update_cool_points(10)
        result = UserSoundeffectRouter(user, "buy", ["clap"]).route()
        assert result == "@young.thug bought !clap"
        assert User(user).cool_points() < 10

    def test_transferring_to_another_user(self, mock_find_random_user):
        user = "young.thug"
        User(user).update_cool_points(10)
        command = Command("damn")
        command.allow_user(user)
        result = UserSoundeffectRouter(user, "give", ["damn", "uzi"]).route()
        assert result == [
            "@uzi now has access to !damn",
            "@young.thug lost access to !damn",
        ]

    def test_sharing_with_another_user(self, mock_find_random_user):
        user = "young.thug"
        User(user).update_cool_points(10)
        command = Command("damn")
        command.allow_user(user)
        result = UserSoundeffectRouter(user, "share", ["damn", "uzi"]).route()
        assert result == "young.thug shared @uzi now has access to !damn"