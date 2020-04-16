from pathlib import Path

from tinydb import TinyDB, Query

from chat_thief.soundeffects_library import SoundeffectsLibrary
from chat_thief.audio_player import AudioPlayer
from chat_thief.models import CommandPermission

from chat_thief.stream_lords import STREAM_LORDS

TABLE_NAME = "command_permissions"
DEFAULT_DB_LOCATION = "db/soundeffects.json"


def _command_permissions_table(db_location):
    soundeffects_db_path = Path(__file__).parent.parent.joinpath(db_location)
    return TinyDB(soundeffects_db_path).table(TABLE_NAME)


class AudioCommand:
    def __init__(self, name, db_location=DEFAULT_DB_LOCATION):
        self.name = name
        self.soundfile = SoundeffectsLibrary.find_sample(name)
        self.is_theme_song = self.name in SoundeffectsLibrary.fetch_theme_songs()
        self.table = _command_permissions_table(db_location)

    def play_sample(self):
        AudioPlayer.play_sample(self.soundfile.resolve())

    def allowed_to_play(self, user):
        if self.is_theme_song:
            return user == self.name

        if user in STREAM_LORDS:
            return True

        command_permission = self.table.search(Query().command == self.name)

        if command_permission:
            return user in command_permission[-1]["permitted_users"]

        return False

    def permitted_users(self):
        if command_permission := self.table.search(Query().command == self.name):
            return command_permission[-1]["permitted_users"]
        else:
            return []

    def allow_user(self, user):
        command_permission = self.table.search(Query().command == self.name)

        if command_permission:
            command_permission = command_permission[-1]
            if user not in command_permission["permitted_users"]:
                command_permission["permitted_users"].append(user)
                print(
                    f"Updating Previous Command Permissions {command_permission.__dict__}"
                )
                self.table.update(command_permission)
        else:
            command_permission = CommandPermission(
                user=user, command=self.name, permitted_users=[user],
            )
            print(f"Creating New Command Permissions: {command_permission.__dict__}")
            self.table.insert(command_permission.__dict__)

    # def _validate_user(self, user):
    #     if self.skip_validation:
    #         print("Skipping Validation for adding user permissions")
    #         return True
    #     user_eligible_for_permissions = (
    #         # user not in STREAM_LORDS
    #         user in WelcomeCommittee.fetch_present_users()
    #         and self.command not in SoundeffectsLibrary.fetch_theme_songs()
    #     )
    #     if not user_eligible_for_permissions:
    #         print("This user is not eligible for permissions")
    #     return user_eligible_for_permissions