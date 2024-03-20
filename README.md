# Recipe Generator: Eat Your Veggies!

## General Overview
### Goal: Create a web app that people can use to find new recipes to make using the produce in their fridge.
- A user uploads images of the produce they have in their fridge.
- Then they can pick their preferred cuisine.
- The model identifies the ingredients from the images and compares them to the ingredients from the dataset of recipes.
- Then the website displays recipes with matching ingredients of the preferred cuisine, from most matching to least matching.
### Tasks Required:
- Web scraping: web-scrape different recipes from different cuisines from all recipes and web-scrape images of different ingredients to train our model.
- Research and implementation of a machine learning model: Create an advanced image classification model to recognize the different ingredients in the images uploaded by the user.
- Web-app implementation: Create a web app where users can upload their images and receive recipe recommendations.

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
- Created from scratch a resnet CNN, carefully considering past works to determine kernel sizes that would fit model size
- We didn’t want to use a pytorch pretrained model since they are built for 
- Model was trained on data scraped from google, needs a large variety of classes and large number of images to achieve adequate performance.
Basic workflow: create a dataset from a directory of scraped images --> preprocess the data, changing pixel values and adding a transform --> train
- The training process was extremely labor intensive -- in fact, we ended up draining all resources available on both colab and jupyter lab
- Thus, we were unortunately unable to provide a completed site with a trained model, since the resources weren’t available -- however, on smaller demos, the model can provide classification with around 70% accuracy
- It would be simple for a team with adequate resources to implement our strucutre for deployment

## 3. Web-app implementation:
### Deploying webapp to Google Cloud from GitHub repository
Testing locally
2. Copy this repo into your local computer. Both `git clone` and downloading the zip file works.
3. Inside the code folder `pic16b-mnist-demo`, run 
 ```
conda activate PIC16B-24W
export FLASK_ENV=development
flask run
```
to make sure you're in the correct directory and the code and flask is working. 
Once you've checked that the website is working locally, you can close the flask app.

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
