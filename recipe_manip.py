# -*- coding: utf-8 -*-
"""recipe_manip.ipynb
Used to scrape the recipes and manipulate the recipes dataframe
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def scrape_allRecipes_cuisines():
  """
  Scrapes recipe data from Allrecipes.com based on different cuisines.

  Returns:
  pandas.DataFrame: DataFrame containing the scraped recipe information including Name, URL, Cuisine, and Ingredients.
  """

  # URL of the page listing all cuisines on Allrecipes.com
  url = 'https://www.allrecipes.com/cuisine-a-z-6740455'
  result = requests.get(url)
  doc = BeautifulSoup(result.text, "html.parser")
  cuisines = doc.select('ul.loc.mntl-link-list a')

  # Send a GET request to the page listing all cuisines
  cuisine_dict = {}
  for link in cuisines:
      cuisine = link.get_text(strip=True)
      url = link['href']
      cuisine_dict[cuisine] = url

  # Parse the HTML content of the page
  df = pd.DataFrame(list(cuisine_dict.items()), columns=['Cuisine', 'URL'])

  # Create an empty list to store recipe information
  recipes_data = []

  # Iterate over rows in the cuisine DataFrame
  for index, row in df.iterrows():
      cuisine_url = row['URL']
      cuisine = df['Cuisine'][index]
      result = requests.get(cuisine_url)
      doc = BeautifulSoup(result.text, 'html.parser')

      # {'class': 'comp mntl-card-list-items mntl-document-card mntl-card card--image-top card card--no-image'}
      # Extract information for each recipe
      recipe_info1 = doc.find_all('a', {'class': 'comp mntl-card-list-items mntl-document-card mntl-card card card--no-image'})
      recipe_info2 = doc.find_all('a', {'class': 'comp mntl-card-list-items mntl-document-card mntl-card card--image-top card card--no-image'})
      recipe_info = recipe_info1 + recipe_info2

      # Iterate over each recipe and extract relevant information
      for recipe_card in recipe_info:
          name = recipe_card.find('span', {'class': 'card__title-text'}).text.strip()
          url = recipe_card['href']

          # Extract information from individual recipe URLs
          if not pd.isna(url):
              result2 = requests.get(url)
              doc2 = BeautifulSoup(result2.text, 'html.parser')

              # Create a list to store ingredients
              ingredients_list = []
              ingredients_container = doc2.find('div', {'class': 'mntl-lrs-ingredients'})

              # Check if the container is found
              if ingredients_container:
                  # Find the list of ingredients
                  ingredients_list_element = ingredients_container.find('ul', {'class': 'mntl-structured-ingredients__list'})

                  # Check if the list of ingredients is found
                  if ingredients_list_element:
                      # Extract and append each ingredient to the list
                      for ingredient_item in ingredients_list_element.find_all('li', {'class': 'mntl-structured-ingredients__list-item'}):
                          ingredient = ingredient_item.find('span', {'data-ingredient-name': 'true'})
                          quantity = ingredient_item.find('span', {'data-ingredient-quantity': 'true'})
                          unit = ingredient_item.find('span', {'data-ingredient-unit': 'true'})

                          if ingredient and quantity and unit:
                              ingredient_text = f"{quantity.text.strip()} {unit.text.strip()} {ingredient.text.strip()}"
                              ingredients_list.append(ingredient_text)

              # Append recipe information to the list
              recipes_data.append({
                  'Name': name,
                  'URL': url,
                  'Cuisine': cuisine,
                  'Ingredients': ingredients_list,
              })

  # Create a DataFrame from the list of recipes
  recipes_df = pd.DataFrame(recipes_data)
  return recipes_df

import string

def remove_punctuation(text):
  '''
  - Removes the punctuation from the string of recipe ingredients
  - Input: string of ingredients
  - Output: the cleaned string
  '''
  translator = str.maketrans('', '', string.punctuation)
  return text.translate(translator)

def find_key_ingredients(df, key_ingredients):
  '''
  - Compares the lists of ingredients and creates a new column in the dataframe
    with a list of key ingredients for each recipe
  - Input: dataframe of recipes, list of key ingredients
  - Output: dataframe with new column of key ingredients
  '''

  # Function to check if any key ingredient is found in a list of ingredients
  def find_word_in_string(text):
    '''
    - Finds key ingredients in ingredient string
    - Input: text from ingredient column of df
    - Output: List of key ingredients found in ingredient column
    '''
    R = []
    for i in key_ingredients:
      if i in text:
        # a lot of recipes use corn starch and corn flour
        if i == 'corn' and ('corn starch' in text or 'corn flour' in text):
          break;
        R.append(i)
        # Sometimes only need one egg
        if i == 'eggs' and 'egg' in text and 'eggs' not in R:
          R.append(i)
    return R

  # Remove punctuation
  df['Ingredients'] = df['Ingredients'].apply(remove_punctuation)

  # Find key ingredients in each row
  df['key_ingredients'] = df['Ingredients'].apply(find_word_in_string)
  return df
