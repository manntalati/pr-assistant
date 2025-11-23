import pytest
import time
from pr_assistant.rate_limiter import RateLimiter

def test_rate_limiter_initialization(mock_rate_limiter):
    assert mock_rate_limiter.max_requests == 50
    assert mock_rate_limiter.get_remaining() == 50

def test_rate_limiter_enforcement(mock_rate_limiter):
    # Set a low limit for testing
    mock_rate_limiter.max_requests = 2
    
    assert mock_rate_limiter.check_limit() is True
    assert mock_rate_limiter.check_limit() is True
    assert mock_rate_limiter.check_limit() is False # Limit reached

def test_rate_limiter_cleanup(mock_rate_limiter):
    mock_rate_limiter.max_requests = 5
    
    # Simulate old requests
    old_usage = {
        "req1": time.time() - 4000, # Older than 1 hour
        "req2": time.time() - 3700
    }
    mock_rate_limiter._save_usage(old_usage)
    
    assert mock_rate_limiter.get_remaining() == 5 # Should be cleared
    
    # Add a fresh request
    mock_rate_limiter.check_limit()
    assert mock_rate_limiter.get_remaining() == 4
