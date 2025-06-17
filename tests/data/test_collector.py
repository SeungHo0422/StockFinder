import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.data import collector

@pytest.mark.skip(reason="크롤러 구현 전 임시 skip")
def test_get_us_stocks():
    pass

@pytest.mark.skip(reason="크롤러 구현 전 임시 skip")
def test_get_stock_recent_data():
    pass

if __name__ == "__main__":
    pytest.main()