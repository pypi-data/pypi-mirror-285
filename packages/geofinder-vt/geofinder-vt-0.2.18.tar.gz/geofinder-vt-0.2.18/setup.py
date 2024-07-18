from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geofinder-vt",  # Replace with your own package name
    version="0.2.18",
    author="Your Name",
    author_email="vaidhyanathan@vt.edu",
    description="A brief description of your package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathan846/geofindervt",  # Replace with the URL of your project
    packages=find_packages(include=["geofinder_vt", "geofinder_vt.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose your license
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=[
        'ffmpeg-python==0.2.0',
        'geocoder==1.38.1',
        'geopy==2.3.0',
        'gpmf==0.1',
        'gpxpy==1.5.0',
        'lxml==4.9.2',
        'moviepy==1.0.3',
        'numpy==1.24.3',
        'pandas==2.0.1',
        'python-dateutil>=2.8.2',
        'pytz>=2023.3',
        'pywin32>=306',
        'typing-extensions==4.6.0',
        'xmltodict==0.13.0',
    ],
)