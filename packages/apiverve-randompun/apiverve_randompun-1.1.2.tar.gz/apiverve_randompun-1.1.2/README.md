Random Pun API
============

Random Pun is a simple tool for getting random puns. It returns a random pun from a collection of puns.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Random Pun API](https://apiverve.com/marketplace/api/randompun)

---

## Installation
	pip install apiverve-randompun

---

## Configuration

Before using the randompun API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Random Pun API documentation is found here: [https://docs.apiverve.com/api/randompun](https://docs.apiverve.com/api/randompun).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_randompun.apiClient import RandompunAPIClient

# Initialize the client with your APIVerve API key
api = RandompunAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
This API does not require a Query
```

###### Simple Request

```
# Make a request to the API
result = api.execute()

# Print the result
print(result)
```

###### Example Response

```
{
  "status": "ok",
  "error": null,
  "data": {
    "category": "Heaven and Hell",
    "rating": 4,
    "pun": "The Reverend Francis Norton woke up Sunday morning and realizing it was an exceptionally beautiful and sunny early spring day, decided he just had to play golf. So... he told the Associate Pastor that he was feeling sick and convinced him to say Mass for him that day.As soon as the Associate Pastor left the room, Father Norton headed out of town to a golf course about forty miles away. This way he knew he wouldn't accidentally meet anyone he knew from his parish. Setting up on the first tee, he was alone. After all, it was Sunday morning and everyone else was in church!At about this time, Saint Peter leaned over to the Lord while looking down from the heavens and exclaimed, 'You're not going to let him get away with this, are you?'The Lord sighed, and said, 'No, I guess not.'Just then Father Norton hit the ball and it shot straight towards the pin, dropping just short of it, rolled up and fell into the hole. It WAS A 420 YARD HOLE IN ONE!St. Peter was astonished. He looked at the Lord and asked, 'Why did you let him do that?'The Lord smiled and replied, 'Who's he going to tell?'"
  }
}
```

---

## Customer Support

Need any assistance? [Get in touch with Customer Support](https://apiverve.com/contact).

---

## Updates
Stay up to date by following [@apiverveHQ](https://twitter.com/apiverveHQ) on Twitter.

---

## Legal

All usage of the APIVerve website, API, and services is subject to the [APIVerve Terms of Service](https://apiverve.com/terms) and all legal documents and agreements.

---

## License
Licensed under the The MIT License (MIT)

Copyright (&copy;) 2024 APIVerve, and Evlar LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.