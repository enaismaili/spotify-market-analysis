import pytest
from src.utils.spotify_client import SpotifyClient
from unittest.mock import Mock, patch

@pytest.fixture
def spotify_client():
    return SpotifyClient('test_client_id', 'test_client_secret')

def test_get_featured_playlists(spotify_client):
    with patch('src.utils.spotify_client.SpotifyClient.get_featured_playlists') as mock_get:
        mock_get.return_value = [{'name': 'Test Playlist', 'id': 'test_id'}]
        playlists = spotify_client.get_featured_playlists('IN', 1)
        assert len(playlists) == 1
        assert playlists[0]['name'] == 'Test Playlist'
