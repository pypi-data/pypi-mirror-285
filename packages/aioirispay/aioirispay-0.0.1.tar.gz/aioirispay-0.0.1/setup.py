from setuptools import setup

version = "0.0.1"

long_description = """
Python library for automating payments using the iris bot in telegram
"""

setup(
    version=version,
    author="immortalbuddha",
    author_email="immortalcoder69@gmail.com",
    description=("automatic acceptance of payments in the form of toffees from the telegram bot Iris"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/immortalbuddha/aioirispay",
    download_url="https://github.com/immortalbuddha/aioirispay/archive/v{}.zip".format(version),
    license="GNU AFFERO GENERAL PUBLIC LICENSE Version 3, 19 November 2007",
    package=["aioirispay"],
    install_requires=["aiohttp", "aiofiles", "telethon"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers"
    ]

)