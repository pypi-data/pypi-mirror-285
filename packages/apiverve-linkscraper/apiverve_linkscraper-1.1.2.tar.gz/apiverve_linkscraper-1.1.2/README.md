Link Scraper API
============

Link Scraper is a simple tool for scraping web page links. It returns all the links on a web page.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Link Scraper API](https://apiverve.com/marketplace/api/linkscraper)

---

## Installation
	pip install apiverve-linkscraper

---

## Configuration

Before using the linkscraper API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Link Scraper API documentation is found here: [https://docs.apiverve.com/api/linkscraper](https://docs.apiverve.com/api/linkscraper).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_linkscraper.apiClient import LinkscraperAPIClient

# Initialize the client with your APIVerve API key
api = LinkscraperAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = {  "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html",  "maxlinks": 20,  "includequery": false }
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
    "linkCount": 16,
    "links": [
      {
        "external": false,
        "href": "http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html/pdfs/AWSEC2/latest/UserGuide/ec2-ug.pdf#concepts",
        "text": ""
      },
      {
        "external": true,
        "href": "https://aws.amazon.com",
        "text": "AWS"
      },
      {
        "external": false,
        "href": "http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html/index.html",
        "text": "Documentation"
      },
      {
        "external": false,
        "href": "http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html/ec2/index.html",
        "text": "Amazon EC2"
      },
      {
        "external": true,
        "href": "concepts.html",
        "text": "User Guide"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/ec2/latest/instancetypes/",
        "text": "Amazon EC2 Instance Types Guide"
      },
      {
        "external": true,
        "href": "https://aws.amazon.com/compliance/pci-dss-level-1-faqs/",
        "text": "PCI DSS Level 1"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/autoscaling",
        "text": "Amazon EC2 Auto Scaling"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/aws-backup",
        "text": "AWS Backup"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/cloudwatch",
        "text": "Amazon CloudWatch"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/elasticloadbalancing",
        "text": "Elastic Load Balancing"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/guardduty",
        "text": "Amazon GuardDuty"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/imagebuilder",
        "text": "EC2 Image Builder"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/launchwizard",
        "text": "AWS Launch Wizard"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/systems-manager",
        "text": "AWS Systems Manager"
      },
      {
        "external": true,
        "href": "https://docs.aws.amazon.com/lightsail",
        "text": "Amazon Lightsail"
      }
    ],
    "maxLinksReached": false,
    "url": "http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html"
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