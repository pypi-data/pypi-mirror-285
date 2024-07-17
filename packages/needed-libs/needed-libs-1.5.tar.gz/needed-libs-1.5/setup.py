from setuptools import setup
setup(
    name = 'needed-libs',
    packages = ['needed_libs'],
    version = '1.5',
    install_requires = [
        # cc
        'websocket',
        'httpx',
        'requests',
        'python_ghost_cursor',
        'price_parser',
        
        # Mine
        'python-timeout',
        'python-printr',
        'error_alerts',
        'python-objectifier',
        'python-window-recorder',
        
        # Socials     
        'tweepy',
        'python-twitter',     
        'praw',
        'instagrapi',
        'moviepy',
        'telethon',
        'yt-dlp',
        
        # Scraping
        'requestium',
        'feedparser',
        'bs4',
        'selenium-shortcuts',
        'python-slugify',
        'anticaptchaofficial',
        'openai',

        # Google
        'gspread',
        'googleapiclient',
        'google_auth_oauthlib',
        'google',

        # Server
        'flask',
        'waitress',
        'requests-futures',
        
        # Misc
        'schedule',
        'demoji',
        'ffprobe-python',
        'python-dateutil',
        'dateparser',
        ]
    )