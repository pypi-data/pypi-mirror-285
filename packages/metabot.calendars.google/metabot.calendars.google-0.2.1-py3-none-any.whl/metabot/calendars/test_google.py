"""Tests for metabot.calendars.google."""

import datetime

import pytest

from metabot.calendars import google


class _MockEventsList:  # pylint: disable=too-few-public-methods

    def __init__(self):
        self.events = []

    def execute(self):  # pylint: disable=missing-function-docstring
        ret = {'nextSyncToken': 'next sync token', 'timeZone': 'America/Los_Angeles'}
        if self.events:
            ret['nextPageToken'] = 'next page token'
            ret['items'] = [self.events.pop()]

        return ret

    def push(self, event):
        """Queue the given event for the next call to service().events().list(...)."""

        self.events.append(event)


class _MockEvents:  # pylint: disable=too-few-public-methods
    _list = _MockEventsList()

    @classmethod
    def list(cls, **unused_kwargs):  # pylint: disable=missing-function-docstring
        return cls._list


class _MockService:  # pylint: disable=too-few-public-methods
    _events = _MockEvents()

    @classmethod
    def events(cls):  # pylint: disable=missing-function-docstring
        return cls._events


class _MockCalendar(google.Calendar):
    _service = _MockService()


@pytest.fixture
def cal():  # pylint: disable=missing-function-docstring
    return _MockCalendar('google:metabot@example.com')


def test_basic(cal):  # pylint: disable=redefined-outer-name
    """Make sure the basic machinery is working."""

    assert cal.sync_token is None
    assert cal.poll() is True
    assert cal.sync_token == 'next sync token'
    assert cal.poll() is False
    assert cal.events == {}
    cal.service().events().list().push({
        'end': {
            'date': '2024-07-21',
        },
        'id': 'alpha-id',
        'start': {
            'date': '2024-07-20',
        },
        'status': 'confirmed',
        'updated': '2024-07-18T15:44:56.837Z',
    })
    cal.service().events().list().push({
        'end': {
            'dateTime': '2024-07-20T19:30:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'id': 'bravo-id',
        'start': {
            'dateTime': '2024-07-20T14:30:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'status': 'confirmed',
        'updated': '2024-07-18T15:44:56.837Z',
    })
    assert cal.poll() is True
    assert cal.events == {
        '8d983638:14deb9be': {
            'description': '',
            'end': 1721529000.0,
            'id': 'bravo-id',
            'local_id': '8d983638:14deb9be',
            'location': '',
            'start': 1721511000.0,
            'summary': '',
            'updated': 1721317496.837,
        },
        '8d983638:e64203a8': {
            'description': '',
            'end': 1721545200.0,
            'id': 'alpha-id',
            'local_id': '8d983638:e64203a8',
            'location': '',
            'start': 1721458800.0,
            'summary': '',
            'updated': 1721317496.837,
        },
    }
    alpha = cal.events['8d983638:e64203a8']
    assert datetime.datetime.utcfromtimestamp(
        alpha['start']) == datetime.datetime(2024, 7, 20) + datetime.timedelta(hours=7)
    assert datetime.datetime.utcfromtimestamp(
        alpha['end']) == datetime.datetime(2024, 7, 21) + datetime.timedelta(hours=7)
    assert datetime.datetime.utcfromtimestamp(alpha['updated']) == datetime.datetime(
        2024, 7, 18, 15, 44, 56, 837000)
    bravo = cal.events['8d983638:14deb9be']
    assert datetime.datetime.utcfromtimestamp(
        bravo['start']) == datetime.datetime(2024, 7, 20, 14, 30) + datetime.timedelta(hours=7)
    assert datetime.datetime.utcfromtimestamp(
        bravo['end']) == datetime.datetime(2024, 7, 20, 19, 30) + datetime.timedelta(hours=7)
    assert datetime.datetime.utcfromtimestamp(bravo['updated']) == datetime.datetime(
        2024, 7, 18, 15, 44, 56, 837000)
    assert cal.poll() is False
