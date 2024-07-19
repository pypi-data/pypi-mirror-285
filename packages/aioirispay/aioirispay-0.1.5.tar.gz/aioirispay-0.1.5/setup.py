from setuptools import setup, find_packages

long_description = "Python library for automating payments using the iris bot in telegram"

setup(
    name="aioirispay",
    version="0.1.5",
    author="immortalbuddha",
    author_email="immortalbuddha69@gmail.com",
    description=("Python library for automating payments using the iris bot in telegram"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["telethon", "aiohttp", "aiofiles", "asyncio"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)