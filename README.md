# PyBotSentinel

PyBotSentinel is an API wrapper for [BotSentinel](https://botsentinel.com). It's simple in functionality as at this point,
it only provides you a rating, and the description of what that rating means to
BotSentinel.

### Requirements

This requires Python 3.6 and above, and was built on Python 3.8. It requires
the requests, ScraPy

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