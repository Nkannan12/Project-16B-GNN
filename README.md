# Recipe Generator: Eat Your Veggies!

## General Overview
### Goal: Create a web app that people can use to find new recipes to make using the produce in their fridge.
- A user uploads images of the produce they have in their fridge.
- Then they can pick their preferred cuisine.
- The model identifies the ingredients from the images and compares them to the ingredients from the dataset of recipes.
- Then the website displays recipes with matching ingredients of the preferred cuisine, from most matching to least matching.
### Tasks Required:
1. Web scraping: web-scrape different recipes from different cuisines from all recipes and web-scrape images of different ingredients to train our model.
2. Research and implementation of a machine learning model: Create an advanced image classification model to recognize the different ingredients in the images uploaded by the user.
3. Web-app implementation: Create a web app where users can upload their images and receive recipe recommendations.

## 1. Web Scraping
### Web Scraping Recipes:
Website Scraped: AllRecipes
- 49 different cuisines
- List of ingredients for each dish
Web-Scraper Used: BeautifulSoup
File Location: Recipes_scrape_and_clean.ipynb

### Web Scraping Images:
Website Scraped: Google Images
Necessities: selenium, ChromeDriver (should be put in the same folder as the py file)
Steps to run:
- Download wed driver and py file into the same folder where you want to download the images.
- In the terminal, move into the folder location where files located and then use “python image_scraper.py”.
- Then, when it prompts you, input a list of key words for each ingredient (about 5 or 6) and ask for 375 images for each word.
- Then it will ask for what name you want for the file you want to download the image in which you would put just the ingredients name. It will create the file for you if it does not already exist in the directory.

## 2. Research and implementation of a machine learning model:

## 3. Web-app implementation:

# Deploying webapp to Google Cloud from GitHub repository

1. Redeem the free student google cloud credit by following instructions from announcement email last Friday.

2. Make a fork of this repository.

### Testing locally
2. Copy this repo into your local computer. Both `git clone` and downloading the zip file works.

3. Inside the code folder `pic16b-mnist-demo`, run 
 ```
conda activate PIC16B-24W
export FLASK_ENV=development
flask run
```
to make sure you're in the correct directory and the code and flask is working. 
Once you've checked that the website is working locally, you can close the flask app.

  **FAQ**: If you get an error message like "port 5000 is in use", make sure no other flask app is running in your laptop, and run `flask run -p 5001` (or any other number than 5000) instead.

### Deploying the app

4. Now, go to Google Cloud console (https://console.cloud.google.com/) and create a new project. 
Project ID can be anything, and the organization can be "no organization". 
The most important thing is that the __billing account is connected to your "education" billing account__ (which is where your free credit should be at).

5. Enable IAM API.
  - Go to "APIs & Servies" menu (you can type it into the search bar at the top).
  - Press "+ Enable APIs and Services" button.
  - Search "Identity and Access Management (IAM) API", and enable it (not to be confused with IAM Service Account Credentials API).
6. Create the cloud service.
  - Go to "Cloud Run" menu.
  - Press "+ Create Service" button.
  - Select "Continuously deploy new revisions from a source repository".
  - Click on "Set up with cloud build"
    - Select your GitHub repository.
      - You may have to authenticate to GitHub first.
    - Select docker build option.
  - For region, let's use "us-west-1".
  - For revision autoscaling, let's use 0 to 5 for this class, as this is supposed to be a small app.
  - For Authentication, select "Allow unauthenticated invocations".
  - If everything goes smoothly, your service should run at some url that looks like https://mnist-[...]-wn.a.run.app/. You will have to wait several minutes for your app to be built first.

7. You can update your app by pushing to the `main` branch on GitHub.
   
**FAQ**: If you see trigger failed error, you might have missed enabling IAM API. You can go enable it, then trigger the build again by pushing something to the repository. 

**FAQ**: Can I change the weird url? Looks like you can but it's a lot more involved than I initially thought: https://cloud.google.com/run/docs/mapping-custom-domains

**FAQ**: You can deploy multiple times in the same project. You can delete the deployed app from the "Services" tab of the "Cloud Run" menu. Keep your eyes on Billing tab every several days, and try to avoid overcharges -- it often won't be a major issue for lightweight apps, but things can happen. Nothing specifically occurs other than you will no longer be able to use Google Cloud Platform if you use all the credits.




## What you should look for in the website

1. Go to `submit (advanced)` page and upload some of the .txt files from https://github.com/pic16b-ucla/pic16b-mnist-demo/tree/main/mnist-model/sample-data.

2. Look at the `submit` function in `app.py` and try to understand the general logic.

3. Look at the css files are in the static folder. If you have javascript files, that should also go in there.

4. As before, the jinja template files (and html files) are in the templates folder. This time, some of the templates `extend` the `base.html`, which you can read more about [here](https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/#register) and [here](https://jinja.palletsprojects.com/en/3.1.x/templates/#template-inheritance).

5. When you're working on the web app homework or project, I fully expect you to copy the files from this git repo and modify it.
   You may need to change `requirements.txt` based on packages and their versions you use, but I recommend keeping the `Dockerfile` and `Procfile` as is (unless you have a good understanding of what you're doing!).

