import pytest
import pandas as pd
from src.utils.data_processing import DataProcessor
import os
import tempfile

@pytest.fixture
def data_processor():
    with tempfile.TemporaryDirectory() as raw_dir:
        with tempfile.TemporaryDirectory() as processed_dir:
            yield DataProcessor(raw_dir, processed_dir)

def test_process_playlist_data(data_processor):
    test_data = [{
        'name': 'Test Playlist',
        'id': 'test_id',
        'tracks': [{
            'name': 'Test Track',
            'artists': ['Test Artist'],
            'popularity': 80,
            'explicit': False
        }]
    }]
    
    df = data_processor.process_playlist_data(test_data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['track_name'] == 'Test Track'