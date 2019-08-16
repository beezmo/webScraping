from bs4 import BeautifulSoup
from splinter import Browser
from flask import Flask, jsonify
import pandas as pd
import requests
import pymongo
import numpy as np

def init_browser():
    executable_path = {"executable_path": "../chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    mars_data = {}

    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find('div', class_="content_title")
    news_title = title.find('a').text

    p_results = soup.find('div', class_='article_teaser_body')
    news_p = p_results.text

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    img = soup.find('img', class_='fancybox-image')
    featured_image_url = 'https://www.jpl.nasa.gov' + img["src"]

    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    tweets = soup.find_all('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')

    for tweet in tweets:
        if 'InSight' in tweet.text:
            clean1 = tweet.text.split('InSight ')[1]
            mars_weather = clean1.split(' hPapic.twitter.com/OnwaHAaYRH')[0]
            break
    

    url = 'https://space-facts.com/mars/'
    browser.visit(url)

    tables = pd.read_html(url)
    df = tables[1]
    df.columns = ['Mars Attribute', 'Value']

    html_table = df.to_html()

    html_table.replace('\n', '')

    url_list = ['https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced',
                'https://astrogeology.usgs.gov/search/map/Mars/Viking/schiaparelli_enhanced',
                'https://astrogeology.usgs.gov/search/map/Mars/Viking/syrtis_major_enhanced',
                'https://astrogeology.usgs.gov/search/map/Mars/Viking/valles_marineris_enhanced']

    hemisphere_image_urls = []

    for url in url_list:
        browser.visit(url)

        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.find('h2', class_='title').text.split(' Enhanced')[0]

        img = soup.find_all('a')[5]
        img_url = img["href"]

        store_in_dict = {"title": title,
                         "img_url": img_url}

        hemisphere_image_urls.append(store_in_dict)

    mars_data = {'news_title': news_title,
                 'news_p': news_p,
                 'image': featured_image_url,
                 'weather': mars_weather,
                 'facts': html_table,
                 'hemis': hemisphere_image_urls}

    browser.quit()

    return mars_data