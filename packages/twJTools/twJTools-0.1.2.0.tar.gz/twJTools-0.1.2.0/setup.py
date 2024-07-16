from setuptools import setup, find_packages

setup(
    name="twJTools",
    version="0.1.2.0",
    packages=find_packages(),
    install_requires=[
        "webdriver-manager>=4.0.1",
        "selenium>=4.22.0",
        "psycopg2-binary>=2.9.9",
        "beautifulsoup4>=4.12.3",
    ],
    author="Jasper",
    author_email="tatsuno46@gmail.com",
    description="A core utility library by Jasper",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tatsuno/twJTools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
