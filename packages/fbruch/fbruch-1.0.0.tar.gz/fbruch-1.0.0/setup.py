import setuptools

DESC = '''
Simple python library using graph api and scraping.
Made with♥️ Errucha.
'''

setuptools.setup(
    author= 'Errucha (jepluk)',
    description= DESC,
    entry_points= {'console_scripts': ['fbruch=fbruch:Api']},
    install_requires= [
        'requests', 
        'bs4', 
        'fake-useragent'
    ],
    long_description= open("readme.md").read(),
    long_description_content_type= "text/markdown",
    url= "https://github.com/jepluk/fbruch",
    classifiers= [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords= [
        'fb', 'facebook', 'fb-api', 'facebook-api', 'facebook-graph',
        'bruteforce', 'facebook-scraping', 'fb-scraping', 'scraping'
    ],
    name= 'fbruch',
    packages=setuptools.find_packages(),
    version='1.0.0'
)


