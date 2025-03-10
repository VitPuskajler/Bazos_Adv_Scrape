# Tool to Analyze Car Ads on Bazos Without Opening Each Listing

This Python–Flask application automates the extraction of key details from [auto.bazos.sk](https://auto.bazos.sk) ads, saving you the hassle of manually opening each listing. It retrieves:

- **Year of Manufacture:** 1995–2023
- **Engine Power:** in kW
- **Mileage:** in km

> **Note:** Since Bazos uses free-form text, the search logic might not be flawless—but it reliably handles common ad formats.

Due to an average page load time of about 12 seconds, implementing local caching is recommended to enhance performance. Need to analyze other vehicle types (e.g., bikes)? Simply extend the existing Flask functions.
