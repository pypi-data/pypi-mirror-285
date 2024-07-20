Play Store Scraper API
============

Play Store Scraper is a simple tool for scraping app store data. It returns the app name, description, price, and more.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Play Store Scraper API](https://apiverve.com/marketplace/api/playstorescraper)

---

## Installation
	pip install apiverve-playstorescraper

---

## Configuration

Before using the playstorescraper API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Play Store Scraper API documentation is found here: [https://docs.apiverve.com/api/playstorescraper](https://docs.apiverve.com/api/playstorescraper).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_playstorescraper.apiClient import PlaystorescraperAPIClient

# Initialize the client with your APIVerve API key
api = PlaystorescraperAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = { "appid": "com.google.android.apps.maps",  "country": "us" }
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
    "title": "Google Maps",
    "description": "Navigate your world faster and easier with Google Maps.  Over 220 countries and territories mapped and hundreds of millions of businesses and places on the map.  Get real-time GPS navigation, traffic, and transit info, and explore local neighborhoods by knowing where to eat, drink and go - no matter what part of the world you’re in.  Get there faster with real-time updates • Beat traffic with real-time ETAs and traffic conditions • Catch your bus, train, or ride-share with real-time transit info • Save time with automatic rerouting based on live traffic, incidents, and road closures  Discover places and explore like a local • Discover local restaurant, events, and activities that matter to you • Know what’s trending and new places that are opening in the areas you care about • Decide more confidently with “Your match,” a number on how likely you are to like a place • Group planning made easy.  Share a shortlist of options and vote in real-time • Create lists of your favorite places and share with friends • Follow must-try places recommended by local experts, Google, and publishers • Review places you’ve visited. Add photos, missing roads and places.  More experiences on Google Maps • Offline maps to search and navigate without an internet connection • Street View and indoor imagery for restaurants, shops, museums and more • Indoor maps to quickly find your way inside big places like airports, malls and stadiums  * Some features not available in all countries  * Also available for Wear OS. Add a Tile on your Wear OS watch to quickly access home and work.  * Navigation isn't intended to be used by oversized or emergency vehicles",
    "descriptionHTML": "Navigate your world faster and easier with Google Maps.  Over 220 countries and territories mapped and hundreds of millions of businesses and places on the map.  Get real-time GPS navigation, traffic, and transit info, and explore local neighborhoods by knowing where to eat, drink and go - no matter what part of the world you’re in.<br><br>Get there faster with real-time updates<br>• Beat traffic with real-time ETAs and traffic conditions<br>• Catch your bus, train, or ride-share with real-time transit info<br>• Save time with automatic rerouting based on live traffic, incidents, and road closures<br><br>Discover places and explore like a local<br>• Discover local restaurant, events, and activities that matter to you<br>• Know what’s trending and new places that are opening in the areas you care about<br>• Decide more confidently with “Your match,” a number on how likely you are to like a place<br>• Group planning made easy.  Share a shortlist of options and vote in real-time<br>• Create lists of your favorite places and share with friends<br>• Follow must-try places recommended by local experts, Google, and publishers<br>• Review places you’ve visited. Add photos, missing roads and places.<br><br>More experiences on Google Maps<br>• Offline maps to search and navigate without an internet connection<br>• Street View and indoor imagery for restaurants, shops, museums and more<br>• Indoor maps to quickly find your way inside big places like airports, malls and stadiums<br><br>* Some features not available in all countries<br><br>* Also available for Wear OS. Add a Tile on your Wear OS watch to quickly access home and work.<br><br>* Navigation isn&#39;t intended to be used by oversized or emergency vehicles",
    "summary": "Real-time GPS navigation &amp; local suggestions for food, events, &amp; activities",
    "installs": "10,000,000,000+",
    "minInstalls": 10000000000,
    "maxInstalls": 15881938489,
    "score": 3.9253075,
    "scoreText": "3.9",
    "ratings": 18037987,
    "reviews": 647852,
    "histogram": {
      "1": 3130645,
      "2": 972009,
      "3": 1127659,
      "4": 1691316,
      "5": 11116333
    },
    "price": 0,
    "free": true,
    "currency": "USD",
    "priceText": "Free",
    "available": true,
    "offersIAP": false,
    "androidVersion": "VARY",
    "androidVersionText": "Varies with device",
    "androidMaxVersion": "VARY",
    "developer": "Google LLC",
    "developerId": "5700313618786177705",
    "developerEmail": "apps-help@google.com",
    "developerWebsite": "http://maps.google.com/about/",
    "developerAddress": "1600 Amphitheatre Parkway, Mountain View 94043",
    "privacyPolicy": "http://www.google.com/policies/privacy",
    "developerInternalID": "5700313618786177705",
    "genre": "Travel & Local",
    "genreId": "TRAVEL_AND_LOCAL",
    "categories": [
      {
        "name": "Travel & Local",
        "id": "TRAVEL_AND_LOCAL"
      }
    ],
    "icon": "https://play-lh.googleusercontent.com/Kf8WTct65hFJxBUDm5E-EpYsiDoLQiGGbnuyP6HBNax43YShXti9THPon1YKB6zPYpA",
    "headerImage": "https://play-lh.googleusercontent.com/FQx43QTaAqeOtoTLylK3WIs7ySKuGS8AurXNA1Kj34m6w6CjavF4Oj3s5DB6xZZ7DS63",
    "screenshots": [
      "https://play-lh.googleusercontent.com/FK7X8M1BCF0Ji6-TkHaww2qP8FEdIrvofW6qDRMCNjszqq5XiVmGNCV00KXSSuETMS8",
      "https://play-lh.googleusercontent.com/PJkiXQiABQxpVdHMpvOux53wP2TVuYg0fq9K5JYYDO336nvbX-0ShhHWzZGnagmWlw",
      "https://play-lh.googleusercontent.com/6K2sbPKNLgAKWrEUFDLkoumlAoeCH491rS7b_yEWdxwEXgLslsXg64Uq7UC-_n9u0eo",
      "https://play-lh.googleusercontent.com/GxNGfSXkAxOEvgOXPKNLp373_MqNS9rPVYlCi-1JekFD3N3JdT3g3d4z_5dxWaFvtKg",
      "https://play-lh.googleusercontent.com/iXEapPYDZQvo6qFLwlcEpau5qSrNECycERn5mPtr2t4DAIfNJSj3h0FM_t74By7bI9rb",
      "https://play-lh.googleusercontent.com/rbE2lxgiuVV_CjldaGNdBKEZRizx97rEO_yl4ihk7pXh5y8cRf7FROsmw5OLtQrcFA",
      "https://play-lh.googleusercontent.com/CZqlsBWxW65_RNZVPzMlWqQ6dg9meysacASXxgH1IJr81mnXCbsr4qQg5wwkD7xQ8Vk",
      "https://play-lh.googleusercontent.com/TUsqChyQ0N92woJa_wI3CBcE3s2_AVOYqKhzBJhF0_kbJIrbexoX8WLMhzxu9DiQ4EM",
      "https://play-lh.googleusercontent.com/eAjXucba0K068B4vftcTCP_my9c1Jc2cVoBHJ4iOKC0sCmJbfH4DA2apFXW_afEedJK5",
      "https://play-lh.googleusercontent.com/CtsHG3eIDWZLPvfx9EHyvy1C-a79N93mAH1SE7KpBwgfWUUfgMFhideRpcynzXWNzQ",
      "https://play-lh.googleusercontent.com/pY3-lUJH2B4EiUIW0Os8rSGtIXi2D1SBBpUUsODoTK55Rqq_nk8mFqeX-LmQdRDTCQ",
      "https://play-lh.googleusercontent.com/XB6MPAFJh0nh3NzSygUU5vdp53HO4gcYaaw3ifeao-i5b0nmL2sm1i0ewWkJN1PKXQ",
      "https://play-lh.googleusercontent.com/bV3JqTSIxqcbqPEcEEKLIfBO3Z04Q0vtMRYXFTKH3pspCe0da0s-HtbcVy9IwX23qOA",
      "https://play-lh.googleusercontent.com/DLpbKo2JM6C7mCM5CRjhYyNRFvE5LB6EpW2ke7JaGklg-rO2ZCHvOepMgZpvQEjiHw",
      "https://play-lh.googleusercontent.com/ZJ219UkXj0fWgaj6MowzMVQSu3Yi5yatHj1gkO8O5u2A6BTTkBAIXulNwvcQBO021lQ",
      "https://play-lh.googleusercontent.com/uUzei9bj47jnqynYszL-4bv1og_icGxkg0EGHj3-H7bAcc1WrSZDCbRvYECxyFjn2XFd",
      "https://play-lh.googleusercontent.com/nMYDAh_uAVJwdUMrldBhJoJbAo6c2nOrzJHlj1L_5Pr-KxS6NZP0BN4I1IGvPQpTPvM",
      "https://play-lh.googleusercontent.com/j3ie0r4OgyoxJ6uYC5SIUL1Jrh2zstVn3Lq_N9QbMjhC6qzbz_U9_Rnlp9AjXWYHUg",
      "https://play-lh.googleusercontent.com/VIWtxGqi0t7r6xBk5I3GxrX0r7SaB2pxLICKf_frFlENdorlWIr0AdL6aam4ZpIz1L-E",
      "https://play-lh.googleusercontent.com/H01Rq4yLLWzXeVNv1_dZpN1hUXVS2um1td-4MV4QpaeEp8NJVjS7GWtL2suk-ZWUn_M",
      "https://play-lh.googleusercontent.com/BjMBjq8a85USfXrf_Bta7gdPGAhHd5HkausCns05qKE9AOPa19af7S5bwwLfsFAVYv3Y",
      "https://play-lh.googleusercontent.com/IOxpItUvwASYpWNBjYKIgHKtb0VekTSjke7RQfivNrAHJyKgRPB8cq9SYivk4kP3TTIf",
      "https://play-lh.googleusercontent.com/yIvO-5ymaTwH-Q3I_auPp1d9OJpZKjiHHNGQCAyJvRPBtc4JXdQ14lKJIgc5UFMLY4E",
      "https://play-lh.googleusercontent.com/jJiCBmpnboxxwA9_fqq-ZwQdkevSKtOfagG2TlJGkLCcFKXSGFHLNIf652QwNHoSjw",
      "https://play-lh.googleusercontent.com/7eKbrr6jlF-RugEG_pe3ESDOIp15zUomlE_y4wQiouBIUk6tRupMF0t2jl5iZcoEFw",
      "https://play-lh.googleusercontent.com/-slZK5SE4SZcmhDCcZIz1_W7ISMxTmk_KlcEXe0rpml1gwK4p0PwEy9giA8DNxHX5A",
      "https://play-lh.googleusercontent.com/JY0zyKWASM0BzAd40awxPWR6keI9ysBMAEKpsyFvsplly1KWUzXy9Z8S3ccKN3Agy0g",
      "https://play-lh.googleusercontent.com/vBcuOdCAku4tm6Y8QzW2Z1w7lGpbqpkvrr3A1VA-_wA06Euzvykac94JlaaudMFnGAfN",
      "https://play-lh.googleusercontent.com/SdzQa_r5rGEXLPl5ftkb7hsxqdoxL80itXNpO7KU0Nc8gLCglb9m6ofI0mO_8wAfxFU",
      "https://play-lh.googleusercontent.com/PvFLtmgzzRLL0qN1-EyAZK9T63tT77IsWbEP0Sr9CZjRI0098KregLRBYlyiT71aVx62",
      "https://play-lh.googleusercontent.com/WrBEnDt5mfDlHElx72gzKGKq2CJ1E0QQbpUQoXgtU5WdzvjH4wGFr7QOzfuLWVw0mVY",
      "https://play-lh.googleusercontent.com/gSvwkZ1MivH5JZ0zPEV4tpyNm6RQzxDoGlUihIoHNAEcZGX9Wpc2HZ06-ax4mLIu4nM",
      "https://play-lh.googleusercontent.com/hQCxox4G84d7k01DyY6Mi9OXU5OSEPoJtvXaL6_77dXLgH6EWHBjenZdJpGrGHlPqXI",
      "https://play-lh.googleusercontent.com/2UoocsMKRJJXCKOwCNGV2-Sjw7wecVpAItkWcyFosAjbA1kVGaP0eeKCysL7z88ikoQ",
      "https://play-lh.googleusercontent.com/Dh38UZpomyLI5y_DQNyitxb92XcqWSKTPJPZGOMmtGx0LlbKB9QGn4p67fCiB5GM3w",
      "https://play-lh.googleusercontent.com/RkBAvpeZF7JdRveRaZ-zuyqCUDOxOdnoPiGxub5WHn-kYY_DDk5l5PTgEQwvQoxMrA",
      "https://play-lh.googleusercontent.com/7vJw3QBAbshQQ2NsDOvLgBgQyp17sc9MVIovWKp849tFtC2K9P9VXrcmtUnEv7_1ic4",
      "https://play-lh.googleusercontent.com/WUAoUXKemZfxcUTPRSkbP5-3In4kHf89UMB9bE3XJQQyuoIEObrLho9XMf0HoDp0kDo"
    ],
    "contentRating": "Everyone",
    "adSupported": true,
    "updated": 1721129610000,
    "version": "VARY",
    "recentChanges": "Thanks for using Google Maps! This release brings bug fixes that improve our product to help you discover new places and navigate to them.<br><br>Become a beta tester: http://goo.gl/vLUcaJ",
    "comments": [
      null
    ],
    "preregister": false,
    "earlyAccessEnabled": false,
    "isAvailableInPlayPass": false,
    "appId": "com.google.android.apps.maps",
    "url": "https://play.google.com/store/apps/details?id=com.google.android.apps.maps&hl=en&gl=us"
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