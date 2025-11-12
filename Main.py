from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import io
import base64
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from bs4 import BeautifulSoup
import webbrowser
import re
import json

#Dataframes
favorites_df = pd.DataFrame()
posts_df = pd.DataFrame()

#Load allowed e621 tags from JSON
with open('tags.json', 'r', encoding='utf-8') as f:
    allowed_tags = set(json.load(f))  # set for fast lookup
    
#Flask App Initialization
app = Flask(__name__)


HEADERS = {
    "User-Agent": "Stat621 (by kirione)"
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        return fetch_analytics(user_name)
    return render_template("index.html")

def fetch_analytics(user_name):    
    print(f"Fetching data for user: {user_name}")
    # Fetch profile from e621 by username
    params = {"name": user_name} 
    response = requests.get("https://e621.net/users.json", headers=HEADERS, params=params)
    print("Status:", response.status_code)

    if response.status_code != 200:
        return f"Error fetching data: {response.status_code}"

    # Parse user page HTML to extract avatar URL and user_id
    soup = BeautifulSoup(response.text, "html.parser")
    #print ("Response Text:", response.text)

    # Find the <script> tag containing "window.___deferred_posts"
    script_tag = soup.find("script", string=re.compile(r"window.___deferred_posts"))
    #print (f"script found, script_tag:",{script_tag})
    if script_tag:
    # Extract avatar url from script_tag
        avatar_url = re.findall(r'"sample_url"\s*:\s*"([^"]+)"', script_tag.string)
        if avatar_url:
            avatar_url = avatar_url[0]
            print (f"avatar url:",{avatar_url})

    #Extract user_id
    for a in soup.find_all("a", href=True):
        href = a.get('href', '')  # safely get the href attribute
        if href.startswith("/users/") and href[7:].isdigit():
            user_id = int(href[7:])
            print("Found user ID:", user_id)
    
    params = {"tags": f"user:{user_name}"} 
    #Fetch posts uploaded by user
    response = requests.get("https://e621.net/posts.json", headers=HEADERS, params=params)
    print("Fetching posts:")
    posts_data = response.json()
    print(f"Found {len(posts_data['posts'])} posts")

    params = {"user_id": user_id} 
    # Fetch favorite posts using user_id with favorites API
    response = requests.get("https://e621.net/favorites.json", headers=HEADERS, params=params)
    print("Fetching favorites:")
    favorites_data = response.json().get("posts", [])

    # Convert user favorites data to pandas DataFrame
    favorites_df = pd.DataFrame(favorites_data)
    print(favorites_df.columns)
    
    # analytics visualization:

    #Favorites Analysis
    # Count by rating
    rating_counts = favorites_df['rating'].value_counts().to_dict()
    #top 10 general tags list
    general_tags_series = favorites_df['tags'].apply(lambda x: x['general'])
    # Flatten the list of lists and count occurrences
    general_all_tags = [tag for sublist in general_tags_series for tag in sublist]
    tag_counts = pd.Series(general_all_tags).value_counts().to_dict()
    #Filter the tag_counts to include only allowed tags
    filtered_tag_counts = {tag: count for tag, count in tag_counts.items() if tag in allowed_tags}
    #Replace all _ with space in tag names
    filtered_tag_counts = {tag.replace('_', ' '): count for tag, count in filtered_tag_counts.items()}
    #Select top 5 tags by count
    top_tags = dict(sorted(filtered_tag_counts.items(), key=lambda item: item[1], reverse=True)[:5])

    #Bar Chart Creation for Top Tags
    #df_toptags = pd.Series(tag_counts)
    #Plot
    plt.figure(figsize=(8,4))
    plt.bar(top_tags.keys(), top_tags.values())
    plt.title("Top Tags")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Encode to base64
    general_tags_img = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template("analytics.html", user_name=user_name,
                           rating_counts=rating_counts, top_tags=top_tags,avatar_url=avatar_url, general_toptags_chart=general_tags_img, posts_data=posts_data)

if __name__ == "__main__":
    app.run(debug=True)
