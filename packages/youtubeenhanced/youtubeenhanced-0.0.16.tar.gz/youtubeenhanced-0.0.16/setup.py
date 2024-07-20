from setuptools import setup, find_packages

VERSION = '0.0.16'
DESCRIPTION = 'Youtube Enhanced simplifies the interaction with Youtube videos.'
LONG_DESCRIPTION = 'Youtube Enhanced package is built to simplify the way you interact with Youtube videos. It is an abstraction to let you call simple methods to be able to search for video information, download video or audio, subtitles, etc.'

setup(
        name = "youtubeenhanced", 
        version = VERSION,
        author = "Daniel Alcalá",
        author_email = "<danielalcalavalera@gmail.com>",
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        packages = find_packages(),
        install_requires = [
            'yt_dlp',
            'google-auth',
            'yta_general_utils',
        ],
        
        keywords = [
            'youtube enhanced',
            'youtube downloader'
        ],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)