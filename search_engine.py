import requests
from bs4 import BeautifulSoup
import re
import time

class SearchEngine():
    def __init__(self):
        # Save data from bazos
        ...
    

    # Loading links from 1 page
    def download_ads(self, url : str) -> list:
        links = []

        req_url = f"{url}"
        r = requests.get(req_url)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, features="lxml")
        content = soup.find_all("div", class_="inzeraty inzeratyflex")

        for car_page in content:
            href = car_page.find("a", href=True)
            if href:
                link_end = href.get("href")
                if link_end:
                    full_link = "https://auto.bazos.sk" + link_end
                    links.append(full_link)
        
        return links, content
    
    # Use scraped links to scrape inner content - ads info
    def scrape_data_from_ads(self, links) -> list:
        webpages = []
        for link in links:
            r = requests.get(link, "html.parser")
            r.raise_for_status()
            ad_soup = BeautifulSoup(r.content, features="lxml")
            ad_text = ad_soup.find_all("div", class_="popisdetail")
            ad_text_str = ''.join([str(ad_text) for ad_text in ad_text])
            webpages.append(ad_text_str) # Need to flatten text for BS4 to work
            
        return webpages
    
    # Extract data from scraped (and saved) data - km, yyyy, kW
    def extract_and_create_tags(self, ads):
        # Ads loaded from scrape_data_from_ads
        read_all_ads = ''.join(ads)  # Join all HTML strings into a single string
        
        # Parse the HTML content
        soup = BeautifulSoup(read_all_ads, 'html.parser')

        # Extract all divs with the class 'popisdetail'
        divs = soup.find_all('div', class_='popisdetail')

        # Store the content of each div in a list
        div_content_list = [div.get_text(separator="\n", strip=True) for div in divs]

        # List to store maximum numbers found in each div
        top_km = []

        for div in div_content_list:
            # Pattern to match integers like 10000
            pattern1 = r'(?<=\D)\d+(?=\D)|(?<=\D)\d+$|^\d+(?=\D)'
            nums_in_list = re.findall(pattern1, div)
            nums_in_list = [int(num) for num in nums_in_list if 20000 <= int(num) <= 500000]

            # Pattern to match numbers with thousands separators like 10.000
            pattern2 = r'\b\d{1,3}(?:[.,]\d{3})+\b'
            nums_with_separators = re.findall(pattern2, div)
            for num_str in nums_with_separators:
                # Replace commas or dots with empty strings to convert to integer
                num_str_cleaned = num_str.replace('.', '').replace(',', '')
                num = int(num_str_cleaned)
                if 5000 <= num <= 500000:
                    nums_in_list.append(num)

            # Pattern to match numbers with spaces as thousands separators like "10 000"
            pattern3 = r'\b\d{1,3}(?: \d{3})+\b'
            nums_with_spaces = re.findall(pattern3, div)
            for num_str in nums_with_spaces:
                # Replace spaces with empty strings to convert to integer
                num_str_cleaned = num_str.replace(' ', '')
                num = int(num_str_cleaned)
                if 5000 <= num <= 500000:
                    nums_in_list.append(num)

            # Pattern to match numbers followed by "tis" like "106 tis"
            pattern_tis = r'\b(\d{1,3})\s*tis\b'
            nums_with_tis = re.findall(pattern_tis, div)
            for num_str in nums_with_tis:
                num = int(num_str) * 1000
                if 5000 <= num <= 500000:
                    nums_in_list.append(num)

            # Pattern to match numbers followed by "km" like "179 000km"
            pattern_km = r'\b(\d{1,3}(?: \d{3})*)km\b'
            nums_with_km = re.findall(pattern_km, div)
            for num_str in nums_with_km:
                # Remove spaces and convert to integer
                num_str_cleaned = num_str.replace(' ', '')
                num = int(num_str_cleaned)
                if 5000 <= num <= 500000:
                    nums_in_list.append(num)

            if nums_in_list:
                max_km = max(nums_in_list)
                top_km.append(max_km)
            else:
                top_km.append(0)  # Append 0 if no valid numbers found


        # Extract YYYY
        years = []
        # Pattern to match years from 1995 to 2030
        pattern_year = r"\b(199[5-9]|20[0-2][0-9]|2023)\b"
        
        for div in div_content_list:
            # Find all matching years in the current div content
            years_in_list = re.findall(pattern_year, div)
            # Convert to integers and ensure they are in the range 1995-2030
            years_in_list = [int(num) for num in years_in_list if 1995 <= int(num) <= 2023]
            # Add to the list of years
            if years_in_list:
                max_years = max(years_in_list)
                years.append(max_years)
            else:
                years.append(0)

        # Extract kW
        kw = []
        # Combined pattern to match both "kW" and "kw" formats and also "KW"
        pattern_kw = r"\b(\d+)\s*[kK][wW]\b|\b(\d+)\s*kW\b|\b(\d+)kw\b"
        
        for div in div_content_list:
            # Find all matching kW in the current div content
            kw_in_list = re.findall(pattern_kw, div)
            
            # Flatten the list and filter out empty matches
            kw_in_list = [int(num) for match in kw_in_list for num in match if num]

            # Filter by range
            kw_in_list = [num for num in kw_in_list if 30 <= num <= 300]
            
            if kw_in_list:
                max_kw = max(kw_in_list)
                kw.append(max_kw)
            else:
                kw.append(0)  # Default to 0 if no valid kW found  
            
        
        return top_km, years, kw

    
    # Create new tags based on extracted data from: extract_and_create_tags
    def new_tags(self, km_list: list, year_list: list, kw_list: list, ads: list) -> list:
        # Extract the HTML content from each BeautifulSoup Tag object
        ad_descriptions = ''.join([str(ad) for ad in ads])

        full_km: list = km_list
        full_year: list = year_list
        full_kw: list = kw_list

        read_ads = BeautifulSoup(ad_descriptions, "html.parser")

        # Extract all divs with the class 'inzeraty inzeratyflex'
        divs = read_ads.find_all('div', class_='inzeraty inzeratyflex')
        
        ads_tags = []
        for i, div in enumerate(divs):
            # Fix URL in the <a> tags within each div
            for a_tag in div.find_all("a", href=True):
                href = a_tag["href"]
                if not href.startswith('http'):
                    a_tag["href"] = 'https://auto.bazos.sk' + href

            full_tag = f"<h5>Najazdene KM: {full_km[i]}&nbsp; Rok výroby: {full_year[i]}&nbsp; Výkon motora: {full_kw[i]} kW</h5>"
            adv =  full_tag + str(div)  # Convert div back to string
            ads_tags.append(adv)

        return ads_tags
