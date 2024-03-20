# -*- coding: utf-8 -*-
"""
This is the algorithm used to determine the recipe recommendations based off of the ingredient list output by the image classification model
"""

import numpy as np
import pandas as pd

def gen_recipe(cuisine, list_of_ingredients=None):
  '''
  - Generates recipe recommendations from the recipe dataset based off of the
    detected ingredients from user input images and prefered cuisine.
  - Input: cuisine, list of ingredients
  - Output: dataframe of recomended recipes
  '''
  link = 'https://raw.githubusercontent.com/Nkannan12/Project-16B-GNN/main/Recipes_cleaned.csv'
  df = pd.read_csv(link)

  if list_of_ingredients == None:
    cuisine_df = df[df["Cuisine"] == cuisine].copy()
    return cuisine_df
  else:
    cuisine_df = df[df["Cuisine"] == cuisine].copy()
    # Create a new column to count matching ingredients
    cuisine_df['Matched Ingredients'] = cuisine_df['key_ingredients'].apply(lambda x: sum(1 for ingredient in list_of_ingredients if ingredient in x))
    if len(list_of_ingredients) > 2:
      cuisine_df = cuisine_df[cuisine_df['Matched Ingredients'] >= 2]
    else:
      cuisine_df = cuisine_df[cuisine_df['Matched Ingredients'] >= 1]
    # Sort dataframe based on the number of matched ingredients in descending order
    cuisine_df = cuisine_df.sort_values(by='Matched Ingredients', ascending=False)

    # Reset index
    cuisine_df.reset_index(drop=True, inplace=True)

    return cuisine_df
