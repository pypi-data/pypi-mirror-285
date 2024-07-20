DNS Lookup API
============

DNS Lookup is a simple tool for looking up the DNS records of a domain. It returns the A, MX, and other records of the domain.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [DNS Lookup API](https://apiverve.com/marketplace/api/dnslookup)

---

## Installation
	pip install apiverve-dnslookup

---

## Configuration

Before using the dnslookup API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The DNS Lookup API documentation is found here: [https://docs.apiverve.com/api/dnslookup](https://docs.apiverve.com/api/dnslookup).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_dnslookup.apiClient import DnslookupAPIClient

# Initialize the client with your APIVerve API key
api = DnslookupAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = { "domain": "myspace.com" }
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
    "domain": "myspace.com",
    "records": {
      "A": [
        "34.111.176.156"
      ],
      "NS": [
        "ns-cloud-a2.googledomains.com",
        "ns-cloud-a1.googledomains.com",
        "ns-cloud-a3.googledomains.com",
        "ns-cloud-a4.googledomains.com"
      ],
      "SOA": {
        "nsname": "ns-cloud-a1.googledomains.com",
        "hostmaster": "cloud-dns-hostmaster.google.com",
        "serial": 2,
        "refresh": 21600,
        "retry": 3600,
        "expire": 259200,
        "minttl": 300
      },
      "MX": [
        {
          "exchange": "us-smtp-inbound-1.mimecast.com",
          "priority": 10
        },
        {
          "exchange": "us-smtp-inbound-2.mimecast.com",
          "priority": 10
        }
      ],
      "TXT": [
        [
          "cj65vjpq0s1v9u7vfo020c6rel"
        ],
        [
          "google-site-verification=q0iWqpcfOBclAJaCeWh83v62QQ4uCgbWObQ08p37qgU"
        ],
        [
          "qpdYoeakhlmAxsnmxgAVFmJgUSibqb/y+Eu6GGn8pdmLf+mFGIB3jhRAxIC5KObsPMES9MW2c+oOrpOo/lCQVw=="
        ],
        [
          "oZ19a+EOIwWVDPJ7POj14UAGBfzk9xcJMmsTUAMUy7H82sDuVCxvw9rZqdg3znFrdTH04+49zd1djhEAt0ooiA=="
        ],
        [
          "v=spf1 mx ip4:63.208.226.34 ip4:204.16.32.0/22 ip4:67.134.143.0/24 ip4:216.205.243.0/24 ip4:34.85.156.5/32 ip4:35.245.108.108/32 ip4:34.86.129.193/32 ip4:34.86.134.94/32 ip4:34.85.222.234/32 ip4:34.86.176.234/32 ip4:34.86.125.212/32 ip4:34.85.224.60/32 ip4:34.86.160.49/32 ip4:35.245.64.166/32 ip4:35.188.226.11/32 ip4:34.86.208.228/32 ip4:34.85.216.144/32 ip4:35.221.22.153/32 ip4:34.86.137.108/32 ip4:34.86.51.35/32 ip4:34.150.221.40/32 ip4:34.85.216.70/32 ip4:34.86.37.191/32 ip4:34.85.214.215/32 ip4:35.236.234.82/32 ip4:34.86.161.241/32 ip4:216.32.181.16 ip4:216.178.32.0/20 ip4:168.235.224.0/24 include:_netblocks.mimecast.com -all"
        ],
        [
          "google-site-verification=eu-3gW1JePvsGRRCaEvH17YUOTFJNofm4lnz2Pk0LTc"
        ],
        [
          "cr40m536tje9on1slld9bi81bg"
        ],
        [
          "al4upe6q5cl13sg4srvfivflvg"
        ],
        [
          "MS=ms89904786"
        ]
      ]
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