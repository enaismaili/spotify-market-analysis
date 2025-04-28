import pandas as pd
import numpy as np
from typing import Dict, List
import logging
import json
from datetime import datetime
import os
from collections import defaultdict

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, raw_data_dir: str, processed_data_dir: str):
        """Initialize data processor with directory paths"""
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        os.makedirs(raw_data_dir, exist_ok=True)
        os.makedirs(processed_data_dir, exist_ok=True)

    def save_raw_data(self, data: Dict, market_code: str) -> str:
        """Save raw data to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{market_code}_raw_{timestamp}.json"
        filepath = os.path.join(self.raw_data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Raw data saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving raw data: {str(e)}")
            raise

    def process_playlist_data(self, playlist_data: List[Dict]) -> pd.DataFrame:
        """Convert playlist data to DF with genre information"""
        try:
            processed_data = []
            
            for playlist in playlist_data:
                if not isinstance(playlist, dict):
                    continue
                    
                playlist_name = playlist.get('name', 'Unknown')
                playlist_id = playlist.get('id', 'Unknown')
                tracks = playlist.get('tracks', [])
                
                for track in tracks:
                    if not isinstance(track, dict):
                        continue
                        
                    #Extract basic track info
                    track_info = {
                        'playlist_name': playlist_name,
                        'playlist_id': playlist_id,
                        'track_name': track.get('name', 'Unknown'),
                        'track_id': track.get('id', 'Unknown'),
                        'artists': ', '.join([
                            artist.get('name', 'Unknown') 
                            for artist in track.get('artists', [])
                            if isinstance(artist, dict)
                        ]),
                        'popularity': track.get('popularity', 0),
                        'explicit': track.get('explicit', False),
                        'duration_ms': track.get('duration_ms', 0),
                    }
                    
                    #Add genres as a comma separated string
                    track_genres = track.get('genres', [])
                    if isinstance(track_genres, list):
                        track_info['genres'] = ', '.join(track_genres)
                    else:
                        track_info['genres'] = ''
                    
                    processed_data.append(track_info)
            
            if not processed_data:
                logger.warning("No data to process")
                return pd.DataFrame()
            
            df = pd.DataFrame(processed_data)
            
            #Add derived metrics
            if 'artists' in df.columns:
                df['artist_count'] = df['artists'].str.count(',') + 1
            
            if 'genres' in df.columns:
                df['genre_count'] = df['genres'].str.count(',') + 1
            
            #Calculate genre statistics
            if 'genres' in df.columns and len(df) > 0:
                all_genres = df['genres'].str.split(', ').explode()
                genre_counts = all_genres.value_counts()
                
                logger.info(f"Found {len(genre_counts)} unique genres")
                logger.info("Top genres: \n" + str(genre_counts.head()))
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing playlist data: {str(e)}")
            raise

    def save_processed_data(self, df: pd.DataFrame, market_code: str) -> str:
        """Save processed DataFrame to CSV."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{market_code}_processed_{timestamp}.csv"
        filepath = os.path.join(self.processed_data_dir, filename)
        
        try:
            if df.empty:
                logger.warning("Empty DataFrame, creating file with headers only")
                df = pd.DataFrame(columns=[
                    'playlist_name', 'playlist_id', 'track_name', 'track_id',
                    'artists', 'popularity', 'explicit', 'duration_ms', 
                    'genres', 'artist_count', 'genre_count'
                ])
            
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Processed data saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving processed data: {str(e)}")
            raise

    def analyze_genres(self, df: pd.DataFrame) -> Dict:
        """Analyze genre distribution and patterns."""
        try:
            if 'genres' not in df.columns or df.empty:
                return {}
            
            genre_series = df['genres'].str.split(', ').explode()
            genre_counts = genre_series.value_counts()
            
            total_tracks = len(df)
            genre_percentages = (genre_counts / total_tracks * 100).round(2)
            
            top_genres = genre_percentages.head(10).to_dict()
            
            unique_genres = len(genre_counts)
            avg_genres_per_track = df['genre_count'].mean()
            
            return {
                'top_genres': top_genres,
                'unique_genres': unique_genres,
                'avg_genres_per_track': round(avg_genres_per_track, 2),
                'total_tracks': total_tracks
            }
            
        except Exception as e:
            logger.error(f"Error analyzing genres: {str(e)}")
            return {}