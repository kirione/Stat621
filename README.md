# Stat621
Generate summary statistics on users favorites

Lets a user enter a username, fetches data from the e621 API for that username and displays analytics

Frontend: HTML, CSS, JavaScript
Backend: Python, Node.js, PHP, etc.
*Jinja2 templates in Flask to render the analytics on the HTML page. Alternatively use JavaScript + Chart.js for more interactivity

[User Input Page (HTML)]
        |
        v
[Python Backend (Flask/FastAPI)]
        |  --> Makes HTTP request to e621 API
        |  --> Processes data using pandas
        v
[Return Analytics Page (HTML/JS)]

1. User enters username → form submits to /analytics route.
2. Flask route /analytics fetches data from e621 API.
3. Flask processes data with pandas → computes analytics.
4. Flask renders analytics.html passing data for display.
5. Page shows analytics (tables, charts, stats).

**Hosting**
Flask app can run locally at http://127.0.0.1:5000/
No external server required at this stage.

-----------------------------------------------------------------
**Front-end Improvements**
Update visual themes to match E621 themes and add pandas plots
