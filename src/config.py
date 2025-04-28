import os
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

#Spotify API config
SPOTIFY_CONFIG = {
    'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
    'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
}

#Config for analyzing the market. India and Japan
MARKETS = {
    'IN': {
        'name': 'India',
        'playlists_limit': 50,
        'analysis_depth': 'deep'
    },
    'JP': {
        'name': 'Japan',
        'playlists_limit': 50,
        'analysis_depth': 'deep'
    }
}

#Config for data collection
COLLECTION_CONFIG = {
    'update_frequency': 'daily',
    'save_raw_data': True,
    'data_directory': 'collected_data',
    'raw_data_dir': 'collected_data/raw_data',
    'processed_data_dir': 'collected_data/processed_data'
}