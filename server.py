from flask import Flask, render_template, request, session
from search_engine import SearchEngine
import requests

app = Flask(__name__)
app.secret_key = "secretKeyBuTstillintheCodesonotSoSecurebUtHeReWEare.*433btwIwaslazytocreateenvfileasucansee"
search = SearchEngine()

# Modified bazos/auta webpage
@app.route("/", methods=["GET"])
def home():
    base_url = "https://auto.bazos.sk"

    # Get the query parameters from the URL
    query_param = request.args.get("param")
    page = request.args.get("page", default=0, type=int)
    
    # Store category in session so it is possible to search by it
    # Get the category from query parameters
    category = request.args.get("category", default='', type=str)

    # Check if category is empty and use session to retain the last value
    if not category:
        category = session.get('previous_category', None)  # Default to None if not set

    # Update session with the current category
    session['previous_category'] = category

    # Continue with your logic
    print(f"Current Category: {category}")
    
    # Search
    search_input = request.args.get("search")
    
    print(category)
    try:
        if search_input:
            base_url = f"{base_url}/?hledat={search_input}&rubriky=auto&hlokalita=&humkreis=25&cenaod=&cenado=8000&Submit=Hľadať&order=&crp=&kitx=ano"
            if category is not None or category != "":
                ase_url = f"{base_url}/{category}/?hledat={search_input}&rubriky=auto&hlokalita=&humkreis=25&cenaod=&cenado=8000&Submit=Hľadať&order=&crp=&kitx=ano"
                print(ase_url)
    except TypeError:
        base_url = base_url
    param_pass = 0
    try:
        if query_param is not None:
            param_pass = int(query_param)
    except ValueError:
        param_pass = query_param

    if query_param is not None:
        base_url = f"{base_url}/{query_param}"

    # URL logic
    final_url_parts = [base_url]

    # Only append category and page if they are valid
    if category:
        final_url_parts.append(category)

    if page > 0:  # Check if page is greater than 0
        final_url_parts.append(str(page))

    # Join parts to create the final URL
    final_url = "/".join(final_url_parts)

    # Attempt to download ads
    try:
        search_ads, content = search.download_ads(final_url)
    except requests.exceptions.HTTPError as e:
        final_url = base_url
        search_ads, content = search.download_ads(final_url)
        print("Caught an exception: ", e)

    # Download content from first 10 pages
    web_content = search.scrape_data_from_ads(search_ads)

    # Extract km, kw, yyyy from each ad
    km, year, kw = search.extract_and_create_tags(web_content)

    # Generate new edited tags in list
    tags = search.new_tags(km, year, kw, content)
    tags_text = ''.join(tags)

    return render_template("main/index.html", tags_text=tags_text, last_query=param_pass, current_page=page, current_category=category)

@app.route("/moto")
def moto_home():
    # Here you can make basically the same with motocycles, but I am more into cars so have fun
    return render_template("moto/moto.html")

if __name__ == '__main__':
    app.run(debug=True)