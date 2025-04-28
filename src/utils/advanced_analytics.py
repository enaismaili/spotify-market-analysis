from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

class AdvancedAnalytics:
    def __init__(self):
        self.genre_categories = {
            'classical': ['classical', 'orchestra', 'symphonic'],
            'electronic': ['edm', 'electronic', 'dance', 'house', 'techno'],
            'hip_hop': ['rap', 'hip hop', 'trap', 'grime'],
            'pop': ['pop', 'indie pop', 'synth-pop'],
            'rock': ['rock', 'metal', 'punk', 'indie rock'],
            'folk': ['folk', 'acoustic', 'singer-songwriter'],
            'regional': {
                'IN': ['bollywood', 'indian', 'bhangra', 'punjabi', 'hindi'],
                'JP': ['j-pop', 'j-rock', 'anime', 'japanese'],
            }
        }

    def cluster_genres(self, df: pd.DataFrame, n_clusters: int = 5) -> Dict:
        """Cluster genres based on popularity and engagement patterns"""
        genre_stats = defaultdict(lambda: {
            'count': 0,
            'avg_popularity': 0,
            'tracks': []
        })

        #Aggregate genre statistics
        for _, row in df.iterrows():
            genres = str(row['genres']).split(', ')
            popularity = row['popularity']
            
            for genre in genres:
                genre_stats[genre]['count'] += 1
                genre_stats[genre]['avg_popularity'] += popularity
                genre_stats[genre]['tracks'].append(row['track_id'])

        #Clustering prep
        genres_data = []
        genre_names = []
        
        for genre, stats in genre_stats.items():
            if stats['count'] > 0:
                genres_data.append([
                    stats['count'],
                    stats['avg_popularity'] / stats['count']
                ])
                genre_names.append(genre)

        if not genres_data:
            return {}

        scaler = StandardScaler()
        genres_normalized = scaler.fit_transform(genres_data)

        kmeans = KMeans(n_clusters=min(n_clusters, len(genres_normalized)))
        clusters = kmeans.fit_predict(genres_normalized)

        clustered_genres = defaultdict(list)
        for genre, cluster, (count, avg_pop) in zip(
            genre_names, clusters, genres_data
        ):
            clustered_genres[f"cluster_{cluster}"].append({
                'genre': genre,
                'count': int(count),
                'popularity': float(avg_pop),
                'tracks': genre_stats[genre]['tracks']
            })

        return dict(clustered_genres)

    def calculate_opportunity_score(
        self, 
        df: pd.DataFrame, 
        market_code: str,
        market_size: int,
        competition_level: float
    ) -> Dict:
        """Calculate market opportunity score based on multiple factors"""
        if df.empty:
            return {}

        total_tracks = len(df)
        unique_genres = len(set(','.join(df['genres'].fillna('')).split(',')))
        avg_popularity = df['popularity'].mean()
        
        local_genres = self.genre_categories['regional'].get(market_code, [])
        local_content = df[
            df['genres'].str.contains('|'.join(local_genres), case=False, na=False)
        ]
        local_percentage = (len(local_content) / total_tracks * 100) if total_tracks > 0 else 0

        market_penetration = min(1.0, total_tracks / market_size)
        
        max_possible_genres = len(self.genre_categories) + len(self.genre_categories['regional'].get(market_code, []))
        genre_diversity = unique_genres / max_possible_genres

        growth_potential = (1 - market_penetration) * (1 - competition_level)

        opportunity_score = (
            0.3 * (avg_popularity / 100) + 
            0.2 * genre_diversity +       
            0.3 * growth_potential +        
            0.2 * (local_percentage / 100) 
        ) * 100

        return {
            'opportunity_score': round(opportunity_score, 2),
            'contributing_factors': {
                'avg_popularity': round(avg_popularity, 2),
                'genre_diversity': round(genre_diversity * 100, 2),
                'growth_potential': round(growth_potential * 100, 2),
                'local_percentage': round(local_percentage, 2)
            },
            'market_metrics': {
                'total_tracks': total_tracks,
                'unique_genres': unique_genres,
                'market_penetration': round(market_penetration * 100, 2)
            }
        }

    def analyze_content_gaps(
        self, 
        df: pd.DataFrame, 
        market_code: str
    ) -> Dict:
        """Identify content gaps and opportunities."""
        if df.empty:
            return {}

        all_genres = ','.join(df['genres'].fillna('')).split(',')
        genre_counts = pd.Series(all_genres).value_counts()
        total_tracks = len(df)
        
        genre_representation = {
            genre: (count / total_tracks * 100)
            for genre, count in genre_counts.items()
        }

        #Gaps by category
        gaps = []
        for category, genres in self.genre_categories.items():
            if category == 'regional':
                continue
                
            category_genres = set(genres)
            present_genres = set(genre_counts.index) & category_genres
            
            if not present_genres:
                gap_size = 100
                status = 'missing'
            else:
                representation = sum(
                    genre_representation.get(genre, 0)
                    for genre in present_genres
                )
                gap_size = max(0, 100 - representation)
                status = 'underrepresented' if gap_size > 50 else 'present'

            gaps.append({
                'category': category,
                'gap_size': round(gap_size, 2),
                'status': status,
                'present_genres': list(present_genres),
                'missing_genres': list(category_genres - present_genres)
            })

        #Local content gaps 
        local_genres = set(self.genre_categories['regional'].get(market_code, []))
        present_local = set(genre_counts.index) & local_genres
        local_representation = sum(
            genre_representation.get(genre, 0)
            for genre in present_local
        )

        return {
            'genre_gaps': sorted(gaps, key=lambda x: x['gap_size'], reverse=True),
            'local_content': {
                'representation': round(local_representation, 2),
                'present_genres': list(present_local),
                'missing_genres': list(local_genres - present_local)
            },
            'recommendations': [
                gap for gap in gaps 
                if gap['gap_size'] > 50 or gap['status'] == 'missing'
            ]
        }

    def generate_market_insights(
        self,
        df: pd.DataFrame,
        market_code: str,
        market_size: int,
        competition_level: float
    ) -> Dict:
        """Generate comprehensive market insights"""
        clusters = self.cluster_genres(df)
        opportunity = self.calculate_opportunity_score(
            df, market_code, market_size, competition_level
        )
        gaps = self.analyze_content_gaps(df, market_code)

        return {
            'market_code': market_code,
            'genre_clusters': clusters,
            'opportunity_analysis': opportunity,
            'gap_analysis': gaps,
            'summary': {
                'opportunity_score': opportunity.get('opportunity_score', 0),
                'total_tracks': len(df),
                'unique_genres': len(set(','.join(df['genres'].fillna('')).split(','))),
                'key_gaps': [gap['category'] for gap in gaps.get('recommendations', [])]
            }
        }