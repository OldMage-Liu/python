import time
import requests
from selenium import webdriver
from lxml import etree

# Initialize Edge WebDriver
browser = webdriver.Edge()

# Navigate to the Pixabay videos page
browser.get("https://pixabay.com/zh/")

# Wait a bit for the page to load (optional)
time.sleep(2)

# Get all cookies from the browser session
browser_cookies = browser.get_cookies()

# Create a requests session
sess = requests.Session()

# Set cookies in the requests session
for cookie in browser_cookies:
    # Extract cookie attributes
    cookie_dict = {
        'name': cookie['name'],
        'value': cookie['value'],
        'domain': cookie.get('domain', None),
        'path': cookie.get('path', None),
        'secure': cookie.get('secure', None),
        'expires': cookie.get('expiry', None)
    }

    # Add cookie to the session
    sess.cookies.set(**cookie_dict)

# Example usage: Fetch a page using the requests session
response = sess.get("https://pixabay.com/zh/")

# Parse the HTML response
html = etree.HTML(response.text)
print(html)
# Use correct XPath expression to extract href attribute
href = html.xpath('/html/body/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/a/@href')
print(href)

# Close the browser and the requests session
browser.quit()
sess.close()
