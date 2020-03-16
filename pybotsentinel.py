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

import requests
from time import time
from time import sleep
from scrapy.selector import Selector
import re


class PyBotSentinel(object):
    """
    The PyBotSentinel object is used to query twitter usernames
    against BotSentinel.
    """
    def __init__(self):
        # Base url that contains the time-based api key
        self.url = 'https://botsentinel.com/analyze/embedded?handle={0}'

        # Base URL for the API
        self.api_url = 'https://botsentinel.com/api/v2'

        # Unique user agent to show who is querying
        self.user_agent = 'pyBotSentinel/1.0 '\
                          '(+https://github.com/PlantDaddy/pyBotSentinel)'
        self.headers = {'Referrer': 'https://botsentinel.com/',
                        'User-Agent': self.user_agent}
        self.curtime = None

        # Regex for finding the descriptors, <script>, and key
        self.js_path = '/html/body/script[2]'
        self.key_regex = re.compile(r"KEY = \".*\"")
        self.desc_regex = re.compile(r"RESULT_DESCRIPTORS =.*\]\];")

        # Where we will hold the descriptors so we dont repeatedly
        # search
        self.descriptors = []

        # Regex for cleaning up the returned data
        self.tag_clean = re.compile('<.*?>')
        self.extra_chars = ['\]', '\[', '\"', ';']
        print("If you find this module and service useful, please\n",
              "donate to BotSentinel for all the hard work and\n",
              "incredible service they provide for free at:\n",
              "https://donorbox.org/bot-sentinel")

    def get_bot_rating(self, username):
        """
        This is the bread and butter function that gets the BotSentinel
        rating from a given Twitter username. It also checks the rating
        against the values from BotSentinel which determine if the user
        behavior is "Normal", "Moderate", "Problematic", or "Alarming."
        :param username: The twitter username to check
        :type username: str
        :return: The rating as an int, short descriptor (str), long descriptor (str)
        :rtype: list
        """
        key_line = None
        rating = None
        descriptor = None
        key_desc = None

        # Here we do some simple rate limiting based on time if
        # multiple queries are occurring
        if not self.curtime:
            self.curtime = time()
        else:
            if 8 >= (time() - self.curtime) > 0:
                sleep((time() - self.curtime))
        if username:

            # Get the main account page
            account_page = self.query_site(self.url.format(username), 'get')

            # Here we are using the ScraPy XPath selector to find
            # the <script> tag that contains the JS for user queries
            js = Selector(text=account_page.text).xpath(self.js_path).extract()
            for i in js:
                key_matched = self.key_regex.search(i)
                if not key_matched:
                    continue
                if key_matched:
                    key_line = key_matched.group(0)
                    break
            key_line = key_line.split('"')[1]

            # Send a POST request to the API with the twitter username
            # and time based API key parsed previously
            api = self.query_site(self.api_url, 'post',
                                  data={'user_id': username,
                                        'key': key_line})
            rating = api.json().get('bot_score')

        # Here we do a comparison of the bot_score that was returned
        # previously with the ranges for each rating that is return
        # from get_ratings_descriptors and assigned to self.descriptors
        if len(self.descriptors) == 0:
            self.descriptors = self.get_rating_descriptors()
        if self.descriptors[0][0] <= rating <= self.descriptors[0][1]:
            descriptor = self.descriptors[0]
        elif self.descriptors[0][1] < rating <= self.descriptors[1][1]:
            descriptor = self.descriptors[1]
        elif self.descriptors[1][1] < rating <= self.descriptors[2][1]:
            descriptor = self.descriptors[2]
        elif self.descriptors[2][1] < rating <= self.descriptors[3][1]:
            descriptor = self.descriptors[3]
        elif not rating:
            # BotSentinel returns null if there isnt a user in their db
            # or if the user is a private account
            return [False, 'Account doesn\'t exist or is private']
        else:
            return [False, 'Invalid bot rating returned. Please '
                    'create an issue on github with the query'
                    'you ran, at github.com/PlantDaddy/PyBotSentinel']
        key_desc = descriptor[2]
        descriptor = descriptor[3].format(username)
        return [rating, key_desc, descriptor]

    def get_rating_descriptors(self, desc_line=None):
        """
        get_rating_descriptors is used to query BotSentinel to get the
        descriptions that correspond to a description key, and both are
        correlated to the integer rating each user is assigned
        :param desc_line: Default argument, not required.
        :type desc_line: str
        :return: A list of tuples of the ranges and rating descriptions
        :rtype: list
        """
        descriptors = []

        # Check if we have the descriptors cached, return the cache
        if len(self.descriptors) > 0:
            return [True, self.descriptors]

        # If the descriptors arent in cache and arent provied, get them
        if len(self.descriptors) == 0 and not desc_line:
            page = self.query_site(self.url, 'get')
            desc_line = Selector(text=page.text).xpath(self.js_path).extract()

        # Parse the <script> text and grab the descriptors
        for i in desc_line:
            desc_matched = self.desc_regex.search(i)
            if not desc_matched:
                continue
            if desc_matched:
                desc_line = desc_matched.group(0)
                break

        # Clean up the returned descriptors
        desc_line = re.sub(self.tag_clean, '', desc_line)
        desc_line = desc_line.split('[')
        desc_line = [desc_line[2], desc_line[3], desc_line[4], desc_line[5]]

        # More cleanup of returned descriptors. This could probably be
        # improved
        for i in desc_line:
            i = re.sub("|".join(self.extra_chars), '', i)
            prelist = []
            for x in i.split(','):
                if x != '':

                    # The parsed integers are considered strings,
                    # convert them if theyre integers, catch the
                    # exception if it's a string and pass
                    try:
                        x = int(x)
                    except ValueError:
                        pass
                    prelist.append(x)
            descriptors.append(tuple(prelist))

        # Return a list of tuples, each tuple containing info
        # and ranges for each descriptor
        return descriptors

    def query_site(self, url, method, data=None):
        """
        A function to handle querying Botsentinel using the requests
        module, while also handling the HTTP exceptions
        :param url: The URL to be queried
        :type url: str
        :param method: Query method, only supporting POST and GET
        :type method: str
        :param data:  Dictionary of data/payload to send via POST
        :type data: dict
        :return: Requests object of the page that was queried
        :rtype: object
        """
        try:
            if method.lower() == 'get':
                page = requests.get(url, headers=self.headers)
            elif method.lower() == 'post':
                if not data:
                    return [False, 'Only POST or GET is allowed']
                else:
                    page = requests.post(url, headers=self.headers, data=data)
        except requests.exceptions.ConnectTimeout as err:
            print("Connection Timed out: {0}".format(err))
            return [False, err]
        except requests.exceptions.ConnectionError as err:
            print("Connection error: {0}".format(err))
            return [False, err]
        except requests.exceptions.HTTPError as err:
            print("HTTP Error: {0}".format(err))
            return [False, err]
        except requests.exceptions.ReadTimeout as err:
            print("Page read timed out: {0}".format(err))
            return [False, err]
        except requests.exceptions.Timeout as err:
            print("Timeout: {0}".format(err))
            return [False, err]
        except requests.exceptions.TooManyRedirects as err:
            print("Too many redirects: {0}".format(err))
            return [False, err]

        return page
