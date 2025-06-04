import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import data_ingest  # <-- use this instead of from src import data_ingest

def test_dummy():
    assert 2 + 2 == 4
    def test_load_csv(tmp_path):
    csv_path = tmp_path / "AAPL.csv"
    csv_content = "date,open,high,low,close,volume\n2024-01-01,150,155,149,154,1000000"
    csv_path.write_text(csv_content)
    df = data_ingest.load_csv(str(csv_path))
    assert 'date' in df.columns
    assert df.iloc[0]['open'] == 150
    def test_load_csv(tmp_path):
    csv_path = tmp_path / "AAPL.csv"
    csv_content = "date,open,high,low,close,volume\n2024-01-01,150,155,149,154,1000000"
    csv_path.write_text(csv_content)
    df = data_ingest.load_csv(str(csv_path))
    assert 'date' in df.columns
    assert df.iloc[0]['open'] == 150
    