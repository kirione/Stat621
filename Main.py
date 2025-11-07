from flask import Flask, render_template, request
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from bs4 import BeautifulSoup


#Global Variables declaration
username = "your_username"
api_key = "your_api_key"

app = Flask(__name__)

E621_API = "https://e621.net/users.json"

HEADERS = {
    "User-Agent": "Stat621 (by kirione)"
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        #api_key = request.form.get("api_key")
        return fetch_analytics(user_name)
    return render_template("index.html")

def fetch_analytics(user_name):    
    print(f"Fetching data for user: {user_name}")
    # Fetch profile from e621 by username
    params = {"name": user_name} 
    response = requests.get(E621_API, headers=HEADERS, params=params)
    print("Status:", response.status_code)
    #print("Response text:", response.text[:5000])

    if response.status_code != 200:
        return f"Error fetching data: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a.get('href', '')  # safely get the href attribute
        if href.startswith("/users/") and href[7:].isdigit():
            user_id = int(href[7:])
            print("Found user ID:", user_id)
    

    # Fetch favorite posts by user_id
    params = {"user_id": user_id} 
    response = requests.get("https://e621.net/favorites.json", headers=HEADERS, params=params)
    print("Fetching favorites:")
    data = response.json().get("posts", [])


    # Convert to pandas DataFrame
    df = pd.DataFrame(data)
    
    # Example analytics:
    # Count by rating
    rating_counts = df['rating'].value_counts().to_dict()
    
    # Count top 10 tags
    tags_series = df['tags'].apply(lambda x: x['general'])
    all_tags = [tag for sublist in tags_series for tag in sublist]
    tag_counts = pd.Series(all_tags).value_counts().head(10).to_dict()

    return render_template("analytics.html", user_name=user_name,
                           rating_counts=rating_counts, tag_counts=tag_counts)

if __name__ == "__main__":
    app.run(debug=True)
