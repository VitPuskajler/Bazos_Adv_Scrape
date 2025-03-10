# Tool to Analyze Car Ads on Bazos Without Opening Each Listing

A Python–Flask application that automatically extracts:

Year of manufacture (1995–2023)
Engine power in kW
Mileage (km)
from auta.bazos.sk ads—no need to manually open each listing. Because Bazos uses free-form text, the search logic can be imperfect, but it reliably handles common ad formats. Pages can take ~12 seconds to load, so local caching is recommended to improve performance. If you need to adapt the tool for other vehicle types (e.g., bikes), simply extend the existing Flask functions.
