from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
import os
from PIL import Image
import time

# Don't need to include PATH because in the same folder as this py file
wd = webdriver.Chrome()

Google_Image = \
    'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

def main():
    # Don't need to include PATH because in the same folder as this py file
    wd = webdriver.Firefox()
    
    data = input('Enter your search keyword: ')
    data_list = data.split(", ")
    print(data_list)
    
    num_images = int(input('Enter the number of images you want: '))
    file_name = input('Enter file location: ')
    
    if not os.path.exists(file_name):
        os.mkdir(file_name)
    
    count = 0
    for i in data_list:
        search_url = Google_Image + 'q=' + i #'q=' because its a query
        print(search_url)
        urls = scrape_images(search_url, wd, 1, num_images)
        print(f"Found {len(urls)} images")
    
        for j, url in enumerate(urls):
            download_image(file_name + "/", url, str(count) + ".jpg")
            count += 1
        
        print("Success!")
            
    print("Complete!")
    wd.quit()

def scrape_images(initial_url, wd, delay, max_images):
    url = initial_url
    wd.get(url)
    
    # scroll height of webpage
    last_height = wd.execute_script("return document.body.scrollHeight") 
    while True:
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")    # The driver scrolls down the webpage here.
        time.sleep(8)
        new_height = wd.execute_script("return document.body.scrollHeight")
        if new_height == last_height:   # Breaks here if the driver reached the bottom of the webpage (when it cannot scroll down anymore).
            break
        last_height = new_height        # If the driver failed to scroll to the bottom of the webpage, the current scroll height is recorded. Following, it is compared to the scroll height in the next iteration of the loop to decide if the driver reached the bottom of the webpage or not.
    wd.execute_script("window.scrollTo(0, 0);")
    
    page_html = wd.page_source  # The HTML of the webpage is obtained by the driver.
    pageSoup = bs4.BeautifulSoup(page_html, 'html.parser')  # Using Beautiful Soup to parse the HTML of the webpage.
    thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")  # This class name is obtained from the thumbnail of each image in Google Image Search.
    time.sleep(3)
    
    len_thumbnails = len(thumbnails)    # The number of images found is recorded and printed.
    print("Found %s image thumbnails"%(len_thumbnails))
    image_urls = set()
        
    for img in thumbnails[len(image_urls): max_images]: # Loops through the images of the webpage to obtain and store the number of image URLs requested.
        try: 
            img.click()
            time.sleep(0.5)

        except:
            continue

        images = wd.find_elements(By.CLASS_NAME, "iPVvYb") # This class name is obtained from the actual image and not its thumbnail in Google Image Search.
        for image in images:
            if image.get_attribute('src') in image_urls: # Prevents an image URL from being stored if it is already there.
                max_images += 1 # Accounts for a duplicate image URL by ensuring that the function still returns the number of image URLs requested.
                break

            if image.get_attribute('src') and 'http' in image.get_attribute('src'): # Checks if an image URL is usable.
                    image_urls.add(image.get_attribute('src')) # Stores an image URL if it is usable.
                    
            else:
                print(image)
        
    return image_urls # Returns all of the usable image URLs.
                    
def download_image(download_path, url, file_name):
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
    main()
