App Store Scraper API
============

App Store Scraper is a simple tool for scraping app store data. It returns the app name, description, price, and more.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [App Store Scraper API](https://apiverve.com/marketplace/api/appstorescraper)

---

## Installation
	pip install apiverve-appstorescraper

---

## Configuration

Before using the appstorescraper API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The App Store Scraper API documentation is found here: [https://docs.apiverve.com/api/appstorescraper](https://docs.apiverve.com/api/appstorescraper).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_appstorescraper.apiClient import AppstorescraperAPIClient

# Initialize the client with your APIVerve API key
api = AppstorescraperAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = { "appid": "553834731",  "country": "us" }
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
    "appId": "com.midasplayer.apps.candycrushsaga",
    "contentRating": "4+",
    "currency": "USD",
    "currentVersionReviews": 3293019,
    "currentVersionScore": 4.70599,
    "description": "Start playing Candy Crush Saga today – a legendary puzzle game loved by millions of players around the world.  With over a trillion levels played, this sweet match 3 puzzle game is one of the most popular mobile games of all time!  Switch and match Candies in this tasty puzzle adventure to progress to the next level for that sweet winning feeling! Solve puzzles with quick thinking and smart moves, and be rewarded with delicious rainbow-colored cascades and tasty candy combos!  Plan your moves by matching 3 or more candies in a row, using boosters wisely in order to overcome those extra sticky puzzles! Blast the chocolate and collect sweet candy across thousands of levels, guaranteed to have you craving more!  Candy Crush Saga features:  THE GAME THAT KEEPS YOU CRAVING MORE Thousands of the best levels and puzzles in the Candy Kingdom and with more added every 2 weeks your sugar fix is never far away!   MANY WAYS TO WIN REWARDS Check back daily and spin the Daily Booster Wheel to receive free tasty rewards, and take part in time limited challenges to earn boosters to help you level up!    VARIETY OF SUGAR-COATED CHALLENGES Sweet ways to play: Game modes including Target Score, Clear the Jelly, Collect the Ingredients and Order Mode  PLAY ALONE OR WITH FRIENDS Get to the top of the leaderboard events and compare scores with friends and competitors!  Levels range from easy to hard for all adults to enjoy – accessible on-the-go, offline and online. It's easy to sync the game between devices and unlock full game features when connected to the Internet or Wifi. Follow us to get news and updates; facebook.com/CandyCrushSaga, Twitter @CandyCrushSaga, Youtube https://www.youtube.com/user/CandyCrushOfficial Visit https://community.king.com/en/candy-crush-saga to access the Community and competitions! Candy Crush Saga is completely free to play but some optional in-game items will require payment. You can turn off the payment feature by disabling in-app purchases in your device’s settings. By downloading this game you are agreeing to our terms of service; http://about.king.com/consumer-terms/terms  Do not sell my data: King shares your personal information with advertising partners to personalize ads. Learn more at https://king.com/privacyPolicy.  If you wish to exercise your Do Not Sell My Data rights, you can do so by contacting us via the in game help centre or by going to https://soporto.king.com/  Have fun playing Candy Crush Saga the sweetest match 3 puzzle game around!   If you enjoy playing Candy Crush Saga, you may also enjoy its sister puzzle games; Candy Crush Soda Saga, Candy Crush Jelly Saga and Candy Crush Friends Saga!  All Stars Tournament Selected level 25+. 18+. In-game tournament 09:00 EDT 28th March - 09:00 EDT 28th April 2024. Participating countries only. Win the in-game tournament and receive an invite to the live contest in California, June 2024. Requires US travel. T&Cs: candycrush-saga.web.app/pages/all_stars_terms. © 2024 King.com Ltd.",
    "developer": "King",
    "developerId": 526656015,
    "developerUrl": "https://apps.apple.com/us/developer/king/id526656015?uo=4",
    "developerWebsite": "http://candycrushsaga.com/",
    "free": true,
    "genreIds": [
      "6014",
      "6016",
      "7012",
      "7003"
    ],
    "genres": [
      "Games",
      "Entertainment",
      "Puzzle",
      "Casual"
    ],
    "icon": "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/3b/bf/e6/3bbfe6ef-e343-f718-3dec-26e21fbdf942/AppIcon-0-0-1x_U007emarketing-0-7-0-85-220.png/512x512bb.jpg",
    "id": 553834731,
    "ipadScreenshots": [
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/e5/83/6e/e5836e5e-07f5-c5a3-4108-1ede12d3442a/89b1faee-9df2-4d83-bc7c-ee5a734344ef_v4-candies_478284_423160_CCS_Creative_Results_First_Screenshots_Nov_23_sta_ios-iPad_2048x2732_4.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/84/b5/3c/84b53cb6-cf20-70a1-f96b-d63f4b62d529/77bc4e75-e791-4479-91cb-ca98312abc59_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-iPad_2048x2732_1.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource211/v4/d8/36/94/d83694c3-9e5f-374d-d41d-154e6d9a7bc0/448fc95c-7091-443f-b359-40884cff34c9_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-iPad_2048x2732_2.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/9e/ca/70/9eca7058-5fc1-47c5-bd62-25444a005f42/65eec630-c5f0-46f4-98fb-1ce029fb36d2_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-iPad_2048x2732_4.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource211/v4/6b/23/56/6b23568f-7064-0a84-07e2-5746661a3a2e/10511ee6-b050-4f6f-9f5e-1644ff5d158a_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-iPad_2048x2732_3.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/5d/41/6c/5d416ce8-9b63-e735-d8bf-f1bc79f76924/43dbc8a0-5f8c-4f42-ad4b-9de28521386a_285580_ccs_lt_aso-true-to-gameplay-ss_sta_ios-iPad_2048x2732_1.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/12/3b/1c/123b1cb0-85b8-eedb-354f-b416e62ddc2e/96b029b6-7822-4ed5-8367-552646806b1b_285580_ccs_lt_aso-true-to-gameplay-ss_sta_ios-iPad_2048x2732_2.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/9d/50/c0/9d50c0af-7502-af75-823e-668523a6d15e/835e9d44-e4b3-4f74-b6f0-a01a8f1f0ec3_285580_ccs_lt_aso-true-to-gameplay-ss_sta_ios-iPad_2048x2732_3.jpg/576x768bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/cd/91/8c/cd918ccf-16f4-ed93-7601-2a16092db1ec/d1c5f541-5d59-4cb6-abf7-b9d68d943277_364295_CCS_Saga-Map-Update_ss_2048x2732_en.jpg/576x768bb.jpg"
    ],
    "languages": [
      "AR",
      "CA",
      "HR",
      "CS",
      "DA",
      "NL",
      "EN",
      "FI",
      "FR",
      "DE",
      "HU",
      "ID",
      "IT",
      "JA",
      "KO",
      "MS",
      "NB",
      "PL",
      "PT",
      "RO",
      "RU",
      "ZH",
      "SK",
      "ES",
      "SV",
      "TH",
      "ZH",
      "TR",
      "VI"
    ],
    "price": 0,
    "primaryGenre": "Games",
    "primaryGenreId": 6014,
    "releaseNotes": "We hope you’re having fun playing Candy Crush Saga! We update the game every week so don't forget to download the latest version to get all the sweet new features and levels!\n\nNew to the game? Don’t be shy, join the fun!",
    "released": "2012-11-14T14:41:32Z",
    "requiredOsVersion": "12.0.0",
    "reviews": 3293019,
    "score": 4.70599,
    "screenshots": [
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource211/v4/e3/3d/2f/e33d2f6b-4dbd-17e3-0c0a-7139a382dc4a/e7363b16-199a-4326-a0b2-6b7e1283f711_v4-candies_478284_423160_CCS_Creative_Results_First_Screenshots_Nov_23_sta_ios-6s_1242x2208_4.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/60/4e/c5/604ec5b5-e6e5-b28e-417f-76c8a7ec397b/cbad1cb5-2271-4d88-9124-ee1005d38939_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-6s_1242x2208_1.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/69/6d/18/696d18a9-c5e6-adc6-3c82-c17441753e4c/2024dae5-c018-49c4-ab73-e5577b0b56d7_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-6s_1242x2208_2.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource211/v4/cc/2d/ee/cc2deee1-4830-ae11-cca7-8ced14852504/7698e8e5-d0e3-4906-8ff6-147c9b190ad6_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-6s_1242x2208_4.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/21/36/90/213690ff-ae6d-0481-f767-e7825efc3ee3/b628ce56-834c-4cc8-9dfc-b990e1c0107a_479855_CCS_Rewording_Taglines_Screenshots_Nov_23_route4_sta_ios-6s_1242x2208_3.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/97/27/81/9727816b-c0f4-adab-9e78-4bdc4cba35f0/e8161bd0-89f5-4dd0-b725-f04922f194e8_285580_ccs_lt_aso-true-to-gameplay-ss_sta_ios-6s_1242x2208_1.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/d6/f3/71/d6f3716c-110f-9f11-01a0-005e2f7c4ed1/feece3b7-0e98-44f6-a410-c0839c5f023c_285580_ccs_lt_aso-true-to-gameplay-ss_sta_ios-6s_1242x2208_2.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/8a/08/19/8a0819a2-637c-d52c-e86a-07762b51d5c3/4566515f-0e05-46e9-a782-2075a59941a5_285580_ccs_lt_aso-true-to-gameplay-ss_sta_ios-6s_1242x2208_3.jpg/392x696bb.jpg",
      "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/e6/4a/7e/e64a7ea8-36f5-3186-b2fc-a5d6b9a70534/22e89292-8124-4f09-9788-3995305da759_364295_CCS_Saga-Map-Update_ss_1242x2208_en.jpg/392x696bb.jpg"
    ],
    "size": "363412480",
    "supportedDevices": [
      "iPhone5s-iPhone5s",
      "iPadAir-iPadAir",
      "iPadAirCellular-iPadAirCellular",
      "iPadMiniRetina-iPadMiniRetina",
      "iPadMiniRetinaCellular-iPadMiniRetinaCellular",
      "iPhone6-iPhone6",
      "iPhone6Plus-iPhone6Plus",
      "iPadAir2-iPadAir2",
      "iPadAir2Cellular-iPadAir2Cellular",
      "iPadMini3-iPadMini3",
      "iPadMini3Cellular-iPadMini3Cellular",
      "iPodTouchSixthGen-iPodTouchSixthGen",
      "iPhone6s-iPhone6s",
      "iPhone6sPlus-iPhone6sPlus",
      "iPadMini4-iPadMini4",
      "iPadMini4Cellular-iPadMini4Cellular",
      "iPadPro-iPadPro",
      "iPadProCellular-iPadProCellular",
      "iPadPro97-iPadPro97",
      "iPadPro97Cellular-iPadPro97Cellular",
      "iPhoneSE-iPhoneSE",
      "iPhone7-iPhone7",
      "iPhone7Plus-iPhone7Plus",
      "iPad611-iPad611",
      "iPad612-iPad612",
      "iPad71-iPad71",
      "iPad72-iPad72",
      "iPad73-iPad73",
      "iPad74-iPad74",
      "iPhone8-iPhone8",
      "iPhone8Plus-iPhone8Plus",
      "iPhoneX-iPhoneX",
      "iPad75-iPad75",
      "iPad76-iPad76",
      "iPhoneXS-iPhoneXS",
      "iPhoneXSMax-iPhoneXSMax",
      "iPhoneXR-iPhoneXR",
      "iPad812-iPad812",
      "iPad834-iPad834",
      "iPad856-iPad856",
      "iPad878-iPad878",
      "iPadMini5-iPadMini5",
      "iPadMini5Cellular-iPadMini5Cellular",
      "iPadAir3-iPadAir3",
      "iPadAir3Cellular-iPadAir3Cellular",
      "iPodTouchSeventhGen-iPodTouchSeventhGen",
      "iPhone11-iPhone11",
      "iPhone11Pro-iPhone11Pro",
      "iPadSeventhGen-iPadSeventhGen",
      "iPadSeventhGenCellular-iPadSeventhGenCellular",
      "iPhone11ProMax-iPhone11ProMax",
      "iPhoneSESecondGen-iPhoneSESecondGen",
      "iPadProSecondGen-iPadProSecondGen",
      "iPadProSecondGenCellular-iPadProSecondGenCellular",
      "iPadProFourthGen-iPadProFourthGen",
      "iPadProFourthGenCellular-iPadProFourthGenCellular",
      "iPhone12Mini-iPhone12Mini",
      "iPhone12-iPhone12",
      "iPhone12Pro-iPhone12Pro",
      "iPhone12ProMax-iPhone12ProMax",
      "iPadAir4-iPadAir4",
      "iPadAir4Cellular-iPadAir4Cellular",
      "iPadEighthGen-iPadEighthGen",
      "iPadEighthGenCellular-iPadEighthGenCellular",
      "iPadProThirdGen-iPadProThirdGen",
      "iPadProThirdGenCellular-iPadProThirdGenCellular",
      "iPadProFifthGen-iPadProFifthGen",
      "iPadProFifthGenCellular-iPadProFifthGenCellular",
      "iPhone13Pro-iPhone13Pro",
      "iPhone13ProMax-iPhone13ProMax",
      "iPhone13Mini-iPhone13Mini",
      "iPhone13-iPhone13",
      "iPadMiniSixthGen-iPadMiniSixthGen",
      "iPadMiniSixthGenCellular-iPadMiniSixthGenCellular",
      "iPadNinthGen-iPadNinthGen",
      "iPadNinthGenCellular-iPadNinthGenCellular",
      "iPhoneSEThirdGen-iPhoneSEThirdGen",
      "iPadAirFifthGen-iPadAirFifthGen",
      "iPadAirFifthGenCellular-iPadAirFifthGenCellular",
      "iPhone14-iPhone14",
      "iPhone14Plus-iPhone14Plus",
      "iPhone14Pro-iPhone14Pro",
      "iPhone14ProMax-iPhone14ProMax",
      "iPadTenthGen-iPadTenthGen",
      "iPadTenthGenCellular-iPadTenthGenCellular",
      "iPadPro11FourthGen-iPadPro11FourthGen",
      "iPadPro11FourthGenCellular-iPadPro11FourthGenCellular",
      "iPadProSixthGen-iPadProSixthGen",
      "iPadProSixthGenCellular-iPadProSixthGenCellular",
      "iPhone15-iPhone15",
      "iPhone15Plus-iPhone15Plus",
      "iPhone15Pro-iPhone15Pro",
      "iPhone15ProMax-iPhone15ProMax",
      "iPadAir11M2-iPadAir11M2",
      "iPadAir11M2Cellular-iPadAir11M2Cellular",
      "iPadAir13M2-iPadAir13M2",
      "iPadAir13M2Cellular-iPadAir13M2Cellular",
      "iPadPro11M4-iPadPro11M4",
      "iPadPro11M4Cellular-iPadPro11M4Cellular",
      "iPadPro13M4-iPadPro13M4",
      "iPadPro13M4Cellular-iPadPro13M4Cellular"
    ],
    "title": "Candy Crush Saga",
    "updated": "2024-07-03T05:42:24Z",
    "url": "https://apps.apple.com/us/app/candy-crush-saga/id553834731?uo=4",
    "version": "1.281.0.2"
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