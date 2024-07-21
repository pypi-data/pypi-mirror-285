from setuptools import setup, find_packages

VERSION = '0.0.3'  
DESCRIPTION = 'Open Redirect Vulnerability Scanner for Bug Bounty Hunters'
LONG_DESCRIPTION = 'This tool uses a comprehensive list of open redirect payloads to identify web applications vulnerable to open redirect attacks.'

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="OpenRedirectVulnerablityScanner",
    version=VERSION,
    author="Nawin",
    author_email="vnawin8@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'openredirectvulnerablityscanner = OPEN_REDIRECT.main:main', 
        ],
    },
    install_requires=[
        'urllib3',
        'requests',
        'twilio',  
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    packages=find_packages(),  
    python_requires='>=3.6', 
)
