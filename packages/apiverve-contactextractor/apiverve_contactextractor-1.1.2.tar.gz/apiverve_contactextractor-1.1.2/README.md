Contact Extractor API
============

is a simple tool for extracting contact data from a website URL. It returns the contact emails, phone numbers, and places.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Contact Extractor API](https://apiverve.com/marketplace/api/contactextractor)

---

## Installation
	pip install apiverve-contactextractor

---

## Configuration

Before using the contactextractor API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Contact Extractor API documentation is found here: [https://docs.apiverve.com/api/contactextractor](https://docs.apiverve.com/api/contactextractor).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_contactextractor.apiClient import ContactextractorAPIClient

# Initialize the client with your APIVerve API key
api = ContactextractorAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = {  "url": "https://en.wikipedia.org/wiki/Email_address" }
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
    "url": "https://en.wikipedia.org/wiki/Email_address",
    "contactsFound": null,
    "emails": [
      "john.smith@example.com",
      "jsmith@example.com",
      "john.smith@example.org",
      "John..Doe@example.com",
      "johns@example.com",
      "JohnS@example.com",
      "tag@example.com",
      "joeuser@example.com",
      "simple@example.com",
      "very.common@example.com",
      "FirstName.LastName@EasierReading.org",
      "x@example.com",
      "long.email-address-with-hyphens@and.subdomains.example.com",
      "sorting@example.com",
      "user.name@example.com",
      "surname@example.com",
      "example@s.example",
      "username@example.org",
      "example.com@example.org",
      "user@example.com",
      "user-@example.org",
      "CHOCOLATE@example.com",
      "c@example.com",
      "l@example.com",
      "right@example.com",
      "allowed@example.com",
      "tag@domain.com",
      "extension@pobox.com"
    ],
    "phones": [],
    "places": {}
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