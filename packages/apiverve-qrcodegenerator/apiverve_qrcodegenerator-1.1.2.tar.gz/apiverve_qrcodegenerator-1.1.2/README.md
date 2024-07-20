QR Code Generator API
============

QR Code Generator is a simple tool for generating QR codes. It returns a PNG image of the QR code.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [QR Code Generator API](https://apiverve.com/marketplace/api/qrcodegenerator)

---

## Installation
	pip install apiverve-qrcodegenerator

---

## Configuration

Before using the qrcodegenerator API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The QR Code Generator API documentation is found here: [https://docs.apiverve.com/api/qrcodegenerator](https://docs.apiverve.com/api/qrcodegenerator).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_qrcodegenerator.apiClient import QrcodegeneratorAPIClient

# Initialize the client with your APIVerve API key
api = QrcodegeneratorAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = {  "value": "https://myspace.com",  "type": "url",  "format": "png",  "margin": "0" }
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
    "id": "d8d12c06-c7c6-486f-81e9-508957e62e59",
    "format": "png",
    "type": "url",
    "correction": "M",
    "size": 5,
    "margin": 0,
    "expires": 1721402311899,
    "downloadURL": "https://storage.googleapis.com/apiverve.appspot.com/qrcodegenerator/deadb24a-e658-40af-a0c3-b124c8ed35ce.png?GoogleAccessId=635500398038-compute%40developer.gserviceaccount.com&Expires=1721402311&Signature=XC1VU2yoGDRkFdjMU4OBeKZfbxaXbSRdW75s3ZfqVP3FKRX1dhSIua%2BRqCdDYZsj4ZlJsl8jAQcwS%2B6WXJW%2BDWf0k0z1UK42ZniLKLk5jDFvFjl2BYoXy%2BVolb%2BZyorRNmg%2BseXtsEuHswnlTQurs%2F%2FF%2BE51TvkbpjodvLg8J%2Fxn5oBmo%2BKtaBM9kEv11yHB88mTZLBmp5re8xMTRA9qFmHCOxgqOTPe0Y7FFMqMxmFhzT%2BuLkpfrab7KivhzSaKIjIThCMb%2BQyrZoSU%2F2Ag3zHuY%2B2ib7Am0ETFr%2FV1s8%2Fdxc6IUcKn3IyxEqhG7VnCc1vlMSmqmOn%2FFy%2F6kxnrNw%3D%3D"
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