Text Readability Score API
============

Readability Score is a simple tool for calculating the readability score of text. It returns the readability score based on various readability formulas.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Text Readability Score API](https://apiverve.com/marketplace/api/readabilityscore)

---

## Installation
	pip install apiverve-textreadabilityscore

---

## Configuration

Before using the readabilityscore API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Text Readability Score API documentation is found here: [https://docs.apiverve.com/api/readabilityscore](https://docs.apiverve.com/api/readabilityscore).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_textreadabilityscore.apiClient import ReadabilityscoreAPIClient

# Initialize the client with your APIVerve API key
api = ReadabilityscoreAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = {  "text": "Western astrology is founded on the movements and relative positions of celestial bodies such as the Sun, Moon and planets, which are analysed by their movement through signs of the zodiac (twelve spatial divisions of the ecliptic) and by their aspects (based on geometric angles) relative to one another." }
```

###### Simple Request

```
# Make a request to the API
result = api.execute(query)

# Print the result
print(result)
```

###### Example Response

```
{
  "status": "ok",
  "error": null,
  "data": {
    "textCounts": {
      "syllableCount": 82,
      "lexiconCount": 49,
      "sentenceCount": 1
    },
    "readability": {
      "fleschReadingEase": 13.28,
      "fleschKincaidGrade": 23.6,
      "gunningFog": 26.95,
      "colemanLiauIndex": 13.19,
      "smogIndex": 0,
      "automatedReadabilityIndex": 27.8,
      "daleChallReadabilityScore": 10.9
    },
    "readabilityText": {
      "fleschReadingEase": "very confusing",
      "daleChallReadabilityScore": "average 13th to 15th-grade (college) student"
    }
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