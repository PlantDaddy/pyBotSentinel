'''
    This file is part of pyBotSentinel.

    pyBotSentinel is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyBotSentinel is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyBotSentinel.  If not, see <https://www.gnu.org/licenses/>.
'''

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py3botsentinel",
    version="0.0.1",
    author="Plant Daddy",
    author_email="CqP5TZ77NYBf5uQt@protonmail.com",
    description="A package to programmatically query a twitter user on BotSentinel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PlantDaddy/pyBotSentinel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['requests', 'scrapy', 'time', 're'],
)