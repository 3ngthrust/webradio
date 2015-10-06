import sys
import os.path
from unittest import mock

sys.modules['musicpd'] = mock.Mock()

import webradio.player as player


class TestPlayer(object):
    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_init(self, mpdclient):
        socketpath = os.path.expanduser("~/.config/mpd/socket")
        client_mock = mpdclient()
        music_client = player.Player(socketpath)

        assert isinstance(music_client, player.Player)
        client_mock.connect.called_once_with(host=socketpath, port=0)

    @mock.patch("webradio.player.musicpd.MPDClient")
    def test_destroy(self, mpdclient):
        socketpath = ""
        client_mock = mpdclient()
        player.Player(socketpath)

        assert client_mock.disconnect.call_count == 1
