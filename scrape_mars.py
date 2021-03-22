# Dependencies
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup as bs
import pandas as pd
from pprint import pprint
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager

def scrape():

    # This is to initialize Splinter for Mac users...look below for instructions for Windows users
    # https://splinter.readthedocs.io/en/latest/drivers/chrome.html
    # !which chromedriver

    # executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    # browser = Browser('chrome', **executable_path, headless=True)

    # Hi, Windows user initializing Splinter here...if you're a Mac user, comment this out and use the lines above
    executable_path = {'executable_path': ChromeDriverManager().install()}
    # executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)
   
    # Get headline news title and paragraph
    news_title, news_p = mars_news(browser)
    
    # Store data in a dictionary
    results = {
        "title": news_title,
        "paragraph": news_p,
        "image_URL": jpl_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemisphere(browser),
    }

    # Close the browser after scraping
    browser.quit()

    # Return Results
    return results

def mars_news(browser):
    # Define url and scrape page
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    sleep(1)
    html = browser.html
    soup_news = bs(html, 'html.parser')

    # Scrape the first headline title and paragraph 
    news_title = soup_news.find_all('div', class_='content_title')[1].text
    news_p = soup_news.find_all('div', class_='article_teaser_body')[0].text
    return news_title, news_p

def jpl_image(browser):
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    sleep(1)
    # Click and navigate to full image page and scrape page
    try:
        browser.click_link_by_partial_text('FULL IMAGE')
        sleep(1)
        html = browser.html
        soup_jpl = bs(html, 'html.parser')
    except ElementDoesNotExist:
        print("Something went wrong")

    # Get image tag and concatenate relative local image path to base url
    featured_image = soup_jpl.find(class_='fancybox-image')
    sleep(1)
    featured_image_src= featured_image['src']
    featured_image_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{featured_image_src}'
    return featured_image_url

def mars_facts():
    mars_facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(mars_facts_url)
    mars_planet_profile_df = tables[0]
    mars_planet_profile_df.columns = ['FACT', 'VALUE']
    mars_planet_profile_df.set_index('FACT', inplace=True)

    # Convert to HTML table string and return
    return mars_planet_profile_df.to_html()
    
def mars_hemisphere(browser):
    #Define array to store title and img urls
    hemisphere_image_urls = []
    hemisphere_title_tags = []
    hemisphere_title_strings = []

    #Define url to scrape
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    sleep(1)

    #Scrap first page
    try:
        html = browser.html
        soup_hemisphere = bs(html, 'html.parser')
        print('---soup_hemisphere---',soup_hemisphere)
        sleep(1)
    except ElementDoesNotExist:
        print("Something went wrong")
    
    #Get all link titles to hemisphere data and store in array
    hemisphere_title_tags = soup_hemisphere.find_all('h3')

    #Check output
    print('---Tags---', hemisphere_title_tags)

    # Strip string text from each of the link titles and store in list
    for title in hemisphere_title_tags:
        hemisphere_title_strings.append(title.string)

    # Get images from all hemisphere title links
    for link_title in hemisphere_title_strings:
        # Declare dictionary for the each entry
        link_img_dict = {}
        
        #Save hemisphere title updated
        link_img_dict["title"] = link_title

        # Navigate to link using key word 'hemisphere'
        browser.click_link_by_partial_text('Hemisphere')
        sleep(1)

        #Save img url into the dictionary
        link_img_dict["img_url"] = browser.find_by_text('Sample')['href']
        
        # Save dict to hemisphere_image_urls
        hemisphere_image_urls.append(link_img_dict)
               
        # Return to full list of titles page
        browser.visit(hemisphere_url)

        # Check output
        print("---hemisphere_image_urls---",hemisphere_image_urls)

    return hemisphere_image_urls

    