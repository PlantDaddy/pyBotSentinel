# PyBotSentinel

PyBotSentinel is an API wrapper for [BotSentinel](https://botsentinel.com). It's simple in functionality as at this point,
it only provides you a rating, and the description of what that rating means to
BotSentinel.

### Requirements

This requires Python 3.6 and above, and was built on Python 3.8. It requires
requests, ScraPy

### Installation
I recommend you install this via pip3 ([PyPi](https://pip.pypa.io/en/stable/installing/))

```bash
$ pip3 install pybotsentinel
```

### Getting Started and Finished

```python
import pybotsentinel
query = pybotsentinel.PyBotSentinel()


rating = query.get_bot_rating('realdonaldtrump')
>>> rating
[True, 30, 'Moderate', 'Our analysis has concluded realdonaldtrump exhibits moderate tweet activity and is not a trollbot account.']
```

### Troubleshooting

If you end up getting an occasional 403 while querying, it's most likely due to a race condition
as a result of making the GET request to the page to get the one-time-key
for BotSentinel's backend API, the next key generates before the POST call is made,
the POST call to the API is made, and the API returns a JSON object of {'success': False,
'bot_rating': 'INCORRECT_DATA'} with a HTTP status code code of 403. If a
 subsequent query is made for the same user, it will succeed and return the user's bot
 rating.