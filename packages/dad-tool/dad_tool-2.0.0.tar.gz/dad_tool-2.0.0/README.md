<div align="center">

# Dummy Address Data (DAD) Python Library

Dummy Address Data (DAD) - Retrieve real addresses from all around the world. (Python Client Library)

[![Build Status](https://github.com/Justintime50/dad-python/workflows/build/badge.svg)](https://github.com/Justintime50/dad-python/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/dad-python/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/dad-python?branch=main)
[![PyPi](https://img.shields.io/pypi/v/dad_tool)](https://pypi.org/project/dad_tool)
[![Licence](https://img.shields.io/github/license/Justintime50/dad-python)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/dad/showcase.png" alt="Showcase">

</div>

The DAD Python library is the perfect companion to quickly bootstrap address data in your application. DAD provides real addresses from all over the world with a consistent data structure so you can spend less time looking up addresses and address rules and more time coding.

## Install

```bash
# Install tool
pip3 install dad_tool

# Install locally
just install
```

## Address Data

Address objects will look like the [sample below](#sample-address-object). The data type of each field on an address object is a `string`. A list of addresses is an `array` of `json` objects.

Attempts have been made to verify addresses and ensure that street1, city, state, and zip are present on all records. Some lists may be shorter than others to avoid complexity or because of a lack of accurate data.

The following files can be found in the `data` directory.

## Australia

| Locations       | Tag   |
| --------------- | ----- |
| Victoria Area   | AU_VT |

## Canada

| Locations       | Tag   |
| --------------- | ----- |
| BC Area         | CA_BC |

## China

| Locations                 | Tag   |
| ------------------------- | ----- |
| Beijing Area              | CN_BJ |
| Hong Kong - Wan Chai Area | CN_HK |

## Europe

| Locations                     | Tag   |
| ----------------------------- | ----- |
| Germany - Wesel Area          | EU_DE |
| Spain - Countrywide           | EU_ES |
| France - Paris Area           | EU_FR |
| United Kingdom - England Area | EU_UK |

## Mexico

| Locations                     | Tag   |
| ----------------------------- | ----- |
| Mexico - Mexico City Area     | MX_MX |

## United States

| Locations                 | Tag   |
| ------------------------- | ----- |
| Arizona - Gilbert Area    | US_AZ |
| California - Anaheim Area | US_CA |
| Idaho - Boise Area        | US_ID |
| Kansas - Barton County    | US_KS |
| Nevada - Lincoln Area     | US_NV |
| New York - Rochester Area | US_NY |
| Oregon - Portland Area    | US_OR |
| Texas - Austin Area       | US_TX |
| Utah - Provo Area         | US_UT |
| Washington - Spokane Area | US_WA |

## Usage

```python
import dad_tool

# Grab a random UT address
address = dad_tool.random_address('US_UT')
print(address)

# Alternatively, grab the entire UT list
addresses = dad_tool.list_addresses('US_UT')
print(addresses)

# Get the list of all ISO country codes
iso_data = dad_tool.list_iso_country_codes()
print(iso_data)
```

### Sample Address Object

A sample address object will look like the following:

```json
{
    "street1": "231 N 1200 W",
    "street2": "UNIT 104",
    "city": "OREM",
    "state": "UT",
    "zip": "84057",
    "country": "US"
}
```

### Sample ISO Country Object

```json
{
    "country": "United States of America",
    "alpha_2_code": "US",
    "alpha_3_code": "USA"
}
```

## Development

```bash
# To setup the `DAD` git submodule
just setup-dad

# Get a comprehensive list of development tools
just --list
```

## Attribution

- Addresses provided by [DAD](https://github.com/justintime50/dad).
