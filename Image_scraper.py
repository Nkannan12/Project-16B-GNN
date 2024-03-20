from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
import os
from PIL import Image
import time

'''
This py file is used to scrape images of keywords from google images using selenium and BeautifulSoup
'''

# Don't need to include PATH because in the same folder as this py file
wd = webdriver.Chrome()

Google_Image = \
    'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

def main():
    """
    This script performs a Google image search for a list of keywords provided by the user, and downloads a specified number of images for each keyword.
    Requirements:
    - selenium library
    - geckodriver (Firefox) installed and added to PATH
    
    Parameters: None
    Returns: None
    """
    
    # Don't need to include PATH because in the same folder as this py file
    wd = webdriver.Firefox()

    # Ask for list of key words and turn it into a list object
    data = input('Enter your list of search keywords: ')
    data_list = data.split(", ")
    print(data_list)

    # ask for number of images to fetch and file name for where they should be downloaded
    num_images = int(input('Enter the number of images you want for each word: '))
    file_name = input('Enter file location: ')

    # Create file with file_name if does not already exist
    if not os.path.exists(file_name):
        os.mkdir(file_name)

    # Loop through each key word and download the desired number of images
    count = 0
    for i in data_list:
        search_url = Google_Image + 'q=' + i #'q=' because its a query
        print(search_url)
        urls = scrape_images(search_url, wd, 1, num_images)
        print(f"Found {len(urls)} images")

        # loop through the list of image urls and download them
        for j, url in enumerate(urls):
            download_image(file_name + "/", url, str(count) + ".jpg")
            count += 1
        
        print("Success!")
            
    print("Complete!")
    wd.quit()

def scrape_images(initial_url, wd, delay, max_images):
    """
    Scrapes images from a Google Image Search results page.
    This function scrolls through the Google Image Search results page and collects the URLs of the images. 
    It simulates scrolling down the webpage until the bottom is reached, and then extracts image URLs from the thumbnails displayed on the page.
    Args:
        initial_url (str): The URL of the Google Image Search results page.
        wd: WebDriver instance.
        delay (int): Delay time between scrolling and page updates.
        max_images (int): Maximum number of images to scrape.
    
    Returns: set: A set containing the URLs of the scraped images.
    Note: This function assumes that the WebDriver instance (wd) has already navigated to the initial URL.
    """
    
    url = initial_url
    wd.get(url)
    
    # scroll height of webpage
    last_height = wd.execute_script("return document.body.scrollHeight") 
    while True:
        # The driver scrolls down the webpage
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")   
        time.sleep(8)
        new_height = wd.execute_script("return document.body.scrollHeight")
        if new_height == last_height:   # Breaks if driver reached bottom of the webpage (cannot scroll down anymore).
            break
        # If the driver failed to scroll to the bottom of the webpage, the current scroll height is recorded. 
        # Following, it is compared to the scroll height in the next iteration of the loop to decide if the driver reached the bottom of the webpage or not.
        last_height = new_height        
    wd.execute_script("window.scrollTo(0, 0);")

    # The HTML of the webpage is obtained by the driver.
    page_html = wd.page_source
    pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')  # parse the HTML using BeautifulSoup
    thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")  # class of the thumbnail of each image in Google Image Search.
    time.sleep(3)
    
    len_thumbnails = len(thumbnails)    # The number of images found is recorded and printed.
    print("Found %s image thumbnails"%(len_thumbnails))
    image_urls = set()

    # Loops through the images of the webpage to obtain and store the number of image URLs requested.
    for img in thumbnails[len(image_urls): max_images]:
        try: 
            img.click()
            time.sleep(0.5)
        except:
            continue

        images = wd.find_elements(By.CLASS_NAME, "iPVvYb") #class name is obtained from the actual image
        for image in images:
            # Prevents an image URL from being stored if it is already there.
            if image.get_attribute('src') in image_urls:
                max_images += 1 # Accounts for a duplicate image URL by ensuring that the function still returns the number of image URLs requested.
                break
            # Checks if an image URL is usable.
            if image.get_attribute('src') and 'http' in image.get_attribute('src'): 
                    image_urls.add(image.get_attribute('src')) # Stores an image URL if it is usable.
                    
            else:
                print(image)
    # Returns all of the usable image URLs.
    return image_urls 
                    
def download_image(download_path, url, file_name):
    """
    Downloads an image from a given URL and saves it to a specified file path.
    This function attempts to download an image from the provided URL and save it to the specified file path. 
    It handles potential errors that may occur during the download and save process, such as failed requests, 
    invalid image formats, and file writing errors.
    
    This function requires the `requests`, `io`, and `PIL` (Python Imaging Library) modules to be imported.
    Parameters:
        download_path (str): The directory path where the image will be saved.
        url (str): The URL of the image to download.
        file_name (str): The name of the file to save the image as.
    Returns: None
    """
    try:
        image_content = requests.get(url).content
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image from {url} - {e}")
        return  # Return without attempting to process the image further

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
    except (IOError, OSError) as e:
        print(f"Failed to open image file - {e}")
        return  # Return without attempting to process the image further
    
    try:
        # Convert image to RGB mode
        image = image.convert('RGB')
    
        file_path = os.path.join(download_path, file_name)
        try:
            with open(file_path, "wb") as f:
                image.save(f, "JPEG")
            print(f"Downloaded: {file_name}")
        except Exception as e:
            print(f"Failed to save image - {e}")
            return
    except Exception as e:
        print("Failed -", e)
        return
        

if __name__ == '__main__':
    '''
    - calls main when the file is called in the terminal
    - no arguments and returns None
    '''
    main()
