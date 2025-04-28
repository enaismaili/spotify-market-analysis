from utils.spotify_client import SpotifyClient
from utils.data_processing import DataProcessor
from utils.advanced_analytics import AdvancedAnalytics
from config import SPOTIFY_CONFIG, MARKETS, COLLECTION_CONFIG
import logging
from typing import Dict
import os
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketAnalyzer:
    def __init__(self):
        """Initialize market analyzer with Spotify client and data processor"""
        self.spotify_client = SpotifyClient(
            SPOTIFY_CONFIG['client_id'],
            SPOTIFY_CONFIG['client_secret']
        )
        self.data_processor = DataProcessor(
            COLLECTION_CONFIG['raw_data_dir'],
            COLLECTION_CONFIG['processed_data_dir']
        )
        self.analytics = AdvancedAnalytics()
        self.analytics_dir = 'market_analytics'
        os.makedirs(self.analytics_dir, exist_ok=True)

    def analyze_market(self, market_code: str) -> Dict:
        """Run complete market analysis for a specific country"""
        try:
            logger.info(f"Starting analysis for market: {MARKETS[market_code]['name']}")
            
            #Market config
            market_size = {
                'IN': 1000000,
                'JP': 800000,
                'ID': 600000
            }.get(market_code, 500000)
            
            competition_level = {
                'IN': 0.6,
                'JP': 0.8,
                'ID': 0.5
            }.get(market_code, 0.5)
            
            #Get playlists
            playlists = self.spotify_client.get_market_playlists(
                market_code,
                MARKETS[market_code]['playlists_limit']
            )
            
            if not playlists:
                logger.warning(f"No playlists found for market {market_code}")
                return {
                    'market': MARKETS[market_code]['name'],
                    'playlists': [],
                    'genre_analysis': {},
                    'market_insights': {}
                }
            
            #Process playlists
            processed_playlists = []
            for playlist in playlists:
                if not isinstance(playlist, dict):
                    continue
                    
                tracks = self.spotify_client.get_playlist_tracks(playlist['id'])
                
                if tracks:
                    processed_playlist = {
                        'name': playlist.get('name', 'Unknown'),
                        'id': playlist.get('id', 'Unknown'),
                        'description': playlist.get('description', ''),
                        'followers': playlist.get('followers', {}).get('total', 0),
                        'tracks': tracks
                    }
                    processed_playlists.append(processed_playlist)
            
            #Save raw data
            market_data = {
                'market': MARKETS[market_code]['name'],
                'playlists': processed_playlists,
                'timestamp': datetime.now().isoformat()
            }
            
            raw_filepath = self.data_processor.save_raw_data(market_data, market_code)
            logger.info(f"Raw data saved to: {raw_filepath}")
            
            #Process and analyze data
            df = self.data_processor.process_playlist_data(processed_playlists)
            processed_filepath = self.data_processor.save_processed_data(df, market_code)
            logger.info(f"Processed data saved to: {processed_filepath}")
            
            #Generate advanced insights
            market_insights = self.analytics.generate_market_insights(
                df,
                market_code,
                market_size,
                competition_level
            )
            
            #Save the generated insights
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            insights_file = f"{self.analytics_dir}/{market_code}_insights_{timestamp}.json"
            with open(insights_file, 'w') as f:
                json.dump(market_insights, f, indent=2)
            
            #Basic genre analysis
            genre_analysis = self.data_processor.analyze_genres(df)
            market_data['genre_analysis'] = genre_analysis
            market_data['market_insights'] = market_insights
            
            #Summary log
            logger.info(f"\nAnalysis Summary for {market_code}:")
            logger.info(f"Basic Metrics:")
            logger.info(f"- Total Tracks: {genre_analysis.get('total_tracks', 0)}")
            logger.info(f"- Unique Genres: {genre_analysis.get('unique_genres', 0)}")
            logger.info(f"- Avg Genres per Track: {genre_analysis.get('avg_genres_per_track', 0)}")
            
            logger.info(f"\nAdvanced Metrics:")
            logger.info(f"- Opportunity Score: {market_insights['summary']['opportunity_score']}")
            logger.info(f"- Content Gaps: {', '.join(market_insights['summary']['key_gaps'])}")
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error analyzing market {market_code}: {str(e)}")
            raise

if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    
    for market_code in MARKETS.keys():
        try:
            result = analyzer.analyze_market(market_code)
            
            #Completion status log 
            playlist_count = len(result.get('playlists', []))
            genre_analysis = result.get('genre_analysis', {})
            market_insights = result.get('market_insights', {})
            
            print(f"\n{'='*50}")
            print(f"MARKET ANALYSIS: {market_code}")
            print(f"{'='*50}")
            
            print(f"\nBasic Metrics:")
            print(f"- Processed {playlist_count} playlists")
            print(f"- Found {genre_analysis.get('unique_genres', 0)} unique genres")
            print(f"- Analyzed {genre_analysis.get('total_tracks', 0)} tracks")
            
            print(f"\nMarket Insights:")
            print(f"- Opportunity Score: {market_insights['summary']['opportunity_score']}")
            print(f"- Key Gaps: {', '.join(market_insights['summary']['key_gaps'])}")
            print(f"- Results saved to: {analyzer.analytics_dir}/{market_code}_insights_*.json")
            
        except Exception as e:
            logger.error(f"Failed to analyze market {market_code}: {str(e)}")