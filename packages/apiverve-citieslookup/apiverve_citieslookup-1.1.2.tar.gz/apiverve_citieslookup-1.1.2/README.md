Cities Lookup API
============

Cities Lookup is a simple tool for looking up city data. It returns the city name, population, and more.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Cities Lookup API](https://apiverve.com/marketplace/api/citieslookup)

---

## Installation
	pip install apiverve-citieslookup

---

## Configuration

Before using the citieslookup API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Cities Lookup API documentation is found here: [https://docs.apiverve.com/api/citieslookup](https://docs.apiverve.com/api/citieslookup).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_citieslookup.apiClient import CitieslookupAPIClient

# Initialize the client with your APIVerve API key
api = CitieslookupAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = { "city": "San Francisco" }
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
    "search": "San Francisco",
    "foundCities": [
      {
        "name": "San Francisco",
        "altName": "",
        "country": "US",
        "featureCode": "PPLA2",
        "population": 864816,
        "loc": {
          "type": "Point",
          "coordinates": [
            -122.41942,
            37.77493
          ]
        }
      },
      {
        "name": "San Francisco de Macorís",
        "altName": "",
        "country": "DO",
        "featureCode": "PPLA",
        "population": 124763,
        "loc": {
          "type": "Point",
          "coordinates": [
            -70.25259,
            19.30099
          ]
        }
      },
      {
        "name": "San Francisco del Rincón",
        "altName": "",
        "country": "MX",
        "featureCode": "PPLA2",
        "population": 71139,
        "loc": {
          "type": "Point",
          "coordinates": [
            -101.85515,
            21.01843
          ]
        }
      },
      {
        "name": "South San Francisco",
        "altName": "",
        "country": "US",
        "featureCode": "PPL",
        "population": 67271,
        "loc": {
          "type": "Point",
          "coordinates": [
            -122.40775,
            37.65466
          ]
        }
      },
      {
        "name": "San Francisco",
        "altName": "",
        "country": "AR",
        "featureCode": "PPLA2",
        "population": 59062,
        "loc": {
          "type": "Point",
          "coordinates": [
            -62.08266,
            -31.42797
          ]
        }
      },
      {
        "name": "San Francisco",
        "altName": "",
        "country": "CR",
        "featureCode": "PPL",
        "population": 55923,
        "loc": {
          "type": "Point",
          "coordinates": [
            -84.12934,
            9.99299
          ]
        }
      },
      {
        "name": "San Francisco El Alto",
        "altName": "",
        "country": "GT",
        "featureCode": "PPLA2",
        "population": 54493,
        "loc": {
          "type": "Point",
          "coordinates": [
            -91.4431,
            14.9449
          ]
        }
      },
      {
        "name": "San Francisco Acuautla",
        "altName": "",
        "country": "MX",
        "featureCode": "PPL",
        "population": 27960,
        "loc": {
          "type": "Point",
          "coordinates": [
            -98.86034,
            19.34564
          ]
        }
      },
      {
        "name": "San Francisco Cuaxusco",
        "altName": "",
        "country": "MX",
        "featureCode": "PPLX",
        "population": 24900,
        "loc": {
          "type": "Point",
          "coordinates": [
            -99.61925,
            19.26755
          ]
        }
      },
      {
        "name": "San Francisco Tlalcilalcalpan",
        "altName": "",
        "country": "MX",
        "featureCode": "PPL",
        "population": 16509,
        "loc": {
          "type": "Point",
          "coordinates": [
            -99.76771,
            19.29474
          ]
        }
      },
      {
        "name": "San Francisco",
        "altName": "",
        "country": "SV",
        "featureCode": "PPLA",
        "population": 16152,
        "loc": {
          "type": "Point",
          "coordinates": [
            -88.1,
            13.7
          ]
        }
      },
      {
        "name": "San Francisco de los Romo",
        "altName": "",
        "country": "MX",
        "featureCode": "PPLA2",
        "population": 16124,
        "loc": {
          "type": "Point",
          "coordinates": [
            -102.2714,
            22.07748
          ]
        }
      },
      {
        "name": "San Francisco Zapotitlán",
        "altName": "",
        "country": "GT",
        "featureCode": "PPLA2",
        "population": 13855,
        "loc": {
          "type": "Point",
          "coordinates": [
            -91.52144,
            14.58939
          ]
        }
      },
      {
        "name": "San Francisco Ocotlán",
        "altName": "",
        "country": "MX",
        "featureCode": "PPL",
        "population": 11636,
        "loc": {
          "type": "Point",
          "coordinates": [
            -98.28345,
            19.13411
          ]
        }
      },
      {
        "name": "San Francisco Tecoxpa",
        "altName": "",
        "country": "MX",
        "featureCode": "PPL",
        "population": 11456,
        "loc": {
          "type": "Point",
          "coordinates": [
            -99.00639,
            19.19167
          ]
        }
      },
      {
        "name": "San Francisco Telixtlahuaca",
        "altName": "",
        "country": "MX",
        "featureCode": "PPLA2",
        "population": 10618,
        "loc": {
          "type": "Point",
          "coordinates": [
            -96.90529,
            17.29684
          ]
        }
      },
      {
        "name": "San Francisco Tetlanohcan",
        "altName": "",
        "country": "MX",
        "featureCode": "PPLA2",
        "population": 9858,
        "loc": {
          "type": "Point",
          "coordinates": [
            -98.1637,
            19.2602
          ]
        }
      },
      {
        "name": "San Francisco Chimalpa",
        "altName": "",
        "country": "MX",
        "featureCode": "PPL",
        "population": 8953,
        "loc": {
          "type": "Point",
          "coordinates": [
            -99.34398,
            19.44279
          ]
        }
      },
      {
        "name": "Altos de San Francisco",
        "altName": "",
        "country": "PA",
        "featureCode": "PPL",
        "population": 8189,
        "loc": {
          "type": "Point",
          "coordinates": [
            -79.79,
            8.86167
          ]
        }
      },
      {
        "name": "San Francisco Zacacalco",
        "altName": "",
        "country": "MX",
        "featureCode": "PPL",
        "population": 7420,
        "loc": {
          "type": "Point",
          "coordinates": [
            -98.98279,
            19.92875
          ]
        }
      }
    ]
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