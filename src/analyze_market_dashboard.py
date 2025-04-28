import json
import plotly.graph_objs as go
import pandas as pd

#IMPORTANT Add your market_analytics JSON filename instead of "IN_insights_20250426_080010.json"
with open('market_analytics/IN_insights_20250426_080010.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

def create_market_analysis_dashboard():
    """Generates an HTML dashboard"""

    #CARDS
    market_metrics = {
        "Total Tracks": (data['summary']['total_tracks'], "&#127926;"), 
        "Unique Genres": (data['summary']['unique_genres'], "&#127908;"), 
        "Opportunity Score": (data['opportunity_analysis']['opportunity_score'], "&#128200;"), 
        "Market Penetration (%)": (data['opportunity_analysis']['market_metrics']['market_penetration'] * 100, "&#127760;"), 
    }

    #CARDS
    metric_cards = []
    for metric, (value, icon) in market_metrics.items():
        metric_cards.append(f"""
            <div class="card">
                <div class="icon">{icon}</div>
                <div class="metric-title">{metric}</div>
                <div class="metric-value"><b>{round(value)}</b></div>
            </div>
        """)

    background_color = '#121212'
    card_chart_background = '#212121'  
    spotify_colors = ['#1DB954', '#A29BFE', '#00CEC9', '#FFE599']

    # CHART1
    factors = data['opportunity_analysis']['contributing_factors']
    diversity_metrics = {
        "Avg Genre Popularity": factors['avg_popularity'],
        "Genre Diversity Score": factors['genre_diversity'] / 10,
        "Growth Potential (%)": factors['growth_potential'],
        "Local Artist Share (%)": factors['local_percentage'],
    }
    genre_diversity_fig = go.Figure(data=[
        go.Bar(
            x=list(diversity_metrics.keys()),
            y=list(diversity_metrics.values()),
            marker_color=spotify_colors
        )
    ])
    genre_diversity_fig.update_layout(title="Genre Diversity Breakdown", 
                                      template='plotly_dark', 
                                      plot_bgcolor=card_chart_background, 
                                      paper_bgcolor=card_chart_background,
                                      yaxis=dict(range=[0, 100]))

    #CHART2
    gap_df = pd.DataFrame(data['gap_analysis']['genre_gaps'])
    content_gaps_fig = go.Figure(data=[
        go.Bar(
            x=gap_df['category'],
            y=gap_df['gap_size'],
            marker_color=['#c6182c' if status == 'missing' else '#E17055' for status in gap_df['status']],
            text=gap_df['status'],
            textposition='outside'
        )
    ])
    content_gaps_fig.update_layout(title="Content Gaps in Music Market", 
                                   template='plotly_dark', 
                                   plot_bgcolor=card_chart_background, 
                                   paper_bgcolor=card_chart_background)

    #CHART3
    genre_performance = []
    for cluster in data['genre_clusters'].values():
        for genre_info in cluster:
            if genre_info.get('genre'):
                genre_performance.append({
                    'genre': genre_info['genre'],
                    'popularity': genre_info['popularity']
                })
    genre_df = pd.DataFrame(genre_performance)
    top_genres = genre_df.nlargest(10, 'popularity')
    
    top_genres_fig = go.Figure(data=[
        go.Bar(
            x=top_genres['genre'],
            y=top_genres['popularity'],
            marker_color='#1DB954'
        )
    ])
    top_genres_fig.update_layout(title="Top 10 Genres by Popularity", 
                                 template='plotly_dark', 
                                 plot_bgcolor=card_chart_background, 
                                 paper_bgcolor=card_chart_background)

    dashboard_html = f"""
    <html>
    <head>
        <title>India Music Market Overview (Spotify API Data)</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
            body {{
                font-family: 'Montserrat', sans-serif;
                padding: 20px;
                background-color: {background_color};
                color: white;
            }}
            .dashboard-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }}
            .card {{
                background: {card_chart_background};
                padding: 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
                text-align: center;
            }}
            .icon {{
                font-size: 30px;
                color: #1DB954;
            }}
            .metric-title {{
                font-size: 16px;
                font-weight: bold;
                color: white;
                margin-top: 5px;
            }}
            .metric-value {{
                font-size: 22px;
                font-weight: bold;
                margin-top: 8px;
                color: #83eca8;
            }}
            .chart-container {{
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <h2>India Music Market Overview (Spotify API Data)</h2>
        <div class="dashboard-container">
            {''.join(metric_cards)}
        </div>

        <div class="chart-container">
            <div id="genre-diversity"></div>
            <div id="content-gaps"></div>
            <div id="top-genres"></div>
        </div>

        <script>
            Plotly.newPlot('genre-diversity', {genre_diversity_fig.to_json()});
            Plotly.newPlot('content-gaps', {content_gaps_fig.to_json()});
            Plotly.newPlot('top-genres', {top_genres_fig.to_json()});
        </script>
    </body>
    </html>
    """

    with open('outputs/india_music_market_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

    print("Dashboard is saved as india_music_market_dashboard.html")

create_market_analysis_dashboard()
