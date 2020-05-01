import pytest

from chat_thief.sample_saver import SampleSaver
from chat_thief.models.command import Command

from tests.support.database_setup import DatabaseConfig

class TestSampleSaver(DatabaseConfig):

    def test_saving_a_sample(self):
        # TODO: We need some process around not actually saving during tests
        assert Command.count() == 0
        subject = SampleSaver(
                user="thugga",
                youtube_id="UZvwFztC1Gc",
                command="my_girlfriend",
                start_time="0:08",
                end_time="0:13"
        )
        subject.save()
        assert Command.count() == 1
        SampleSaver(
                user="thugga",
                youtube_id="UZvwFztC1Gc",
                command="my_girlfriend",
                start_time="0:08",
                end_time="0:13"
        )
        subject.save()
        assert Command.count() == 1
