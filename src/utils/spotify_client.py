import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List, Optional, Set
import logging
import time
from collections import defaultdict
import concurrent.futures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str):
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.client = spotipy.Spotify(auth_manager=auth_manager)
            self.artist_genre_cache = {}
            logger.info("Successfully initialized Spotify client")
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {str(e)}")
            raise

    def get_artist_genres_batch(self, artist_ids: List[str]) -> Dict[str, List[str]]:
        """Get genres for multiple artists in one batch."""
        uncached_ids = [aid for aid in artist_ids if aid not in self.artist_genre_cache]
        
        if not uncached_ids:
            return {aid: self.artist_genre_cache[aid] for aid in artist_ids}
            
        try:
            #Split into batches of 50
            batch_results = {}
            for i in range(0, len(uncached_ids), 50):
                batch = uncached_ids[i:i+50]
                artists = self.client.artists(batch)['artists']
                
                for artist in artists:
                    if artist:
                        aid = artist['id']
                        genres = artist.get('genres', [])
                        self.artist_genre_cache[aid] = genres
                        batch_results[aid] = genres
                
                if i + 50 < len(uncached_ids):
                    time.sleep(0.1)  #Limit the rate between batches
            
            #Combine with results that are cached
            return {
                aid: self.artist_genre_cache.get(aid, [])
                for aid in artist_ids
            }
            
        except Exception as e:
            logger.warning(f"Error in batch genre fetch: {str(e)}")
            return {aid: [] for aid in artist_ids}

    def get_market_playlists(self, country_code: str, limit: int = 20) -> List[Dict]:
        try:
            search_terms = [
                'top hits', 'popular', f'top {country_code}',
                'trending', 'viral', 'best'
            ]
            
            all_playlists = []
            for term in search_terms[:3]: 
                try:
                    results = self.client.search(
                        q=term,
                        type='playlist',
                        market=country_code,
                        limit=10
                    )
                    
                    if results and 'playlists' in results:
                        items = results['playlists'].get('items', [])
                        all_playlists.extend(items)
                    
                    time.sleep(0.1)
                except Exception as e:
                    continue
            
            #Remove duplicate playlists and then sort
            unique_playlists = list({
                playlist['id']: playlist 
                for playlist in all_playlists 
                if isinstance(playlist, dict) and 'id' in playlist
            }.values())
            
            unique_playlists.sort(
                key=lambda x: (
                    x.get('followers', {}).get('total', 0) 
                    if isinstance(x.get('followers'), dict) else 0
                ),
                reverse=True
            )
            
            return unique_playlists[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching playlists: {str(e)}")
            return []

    def get_playlist_tracks(self, playlist_id: str, limit: int = 30) -> List[Dict]:
        try:
            tracks = []
            results = self.client.playlist_tracks(
                playlist_id, 
                limit=limit,
                fields='items(track(id,name,artists(id,name,uri),album(name),popularity,explicit,duration_ms,external_urls))'
            )
            
            if not results or 'items' not in results:
                return []
            
            #Collect all unique artist IDs
            artist_ids = set()
            track_data = []
            
            for item in results['items'][:limit]:
                if not item or 'track' not in item:
                    continue
                    
                track = item['track']
                if not track:
                    continue
                
                artists = [
                    {
                        'id': artist.get('id'),
                        'name': artist.get('name', 'Unknown'),
                        'uri': artist.get('uri')
                    }
                    for artist in track.get('artists', [])[:3]  #Should limit to top 3 artists
                    if artist and artist.get('id')
                ]
                
                artist_ids.update(artist['id'] for artist in artists)
                
                track_data.append({
                    'track': track,
                    'artists': artists
                })
            
            #Fetch genres for all artists in batches
            artist_genres = self.get_artist_genres_batch(list(artist_ids))
            
            #Construct final track data with genres
            for data in track_data:
                track = data['track']
                track_genres = []
                
                for artist in data['artists']:
                    track_genres.extend(artist_genres.get(artist['id'], []))
                
                tracks.append({
                    'id': track.get('id', 'Unknown'),
                    'name': track.get('name', 'Unknown'),
                    'artists': data['artists'],
                    'album': track.get('album', {}).get('name', 'Unknown'),
                    'popularity': track.get('popularity', 0),
                    'explicit': track.get('explicit', False),
                    'duration_ms': track.get('duration_ms', 0),
                    'external_urls': track.get('external_urls', {}).get('spotify', ''),
                    'genres': list(set(track_genres))
                })
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error fetching tracks: {str(e)}")
            return []

    def analyze_genre_distribution(self, tracks: List[Dict]) -> Dict:
        genre_counts = defaultdict(int)
        total_tracks = len(tracks)
        
        for track in tracks:
            for genre in track.get('genres', []):
                genre_counts[genre] += 1
        
        genre_distribution = {
            genre: {
                'count': count,
                'percentage': (count / total_tracks) * 100 if total_tracks > 0 else 0
            }
            for genre, count in genre_counts.items()
        }
        
        return {
            'total_tracks': total_tracks,
            'unique_genres': len(genre_counts),
            'genre_distribution': dict(sorted(
                genre_distribution.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            ))
        }