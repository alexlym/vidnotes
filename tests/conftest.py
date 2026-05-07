def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: hit real network + yt-dlp (requires internet)"
    )
    config.addinivalue_line(
        "markers", "requires_auth: needs a valid dl-summarizer session (run auth login first)"
    )
