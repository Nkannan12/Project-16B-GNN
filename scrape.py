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
    data = input('Enter your search keyword: ')
    num_images = int(input('Enter the number of images you want: '))
    if not os.path.exists(data):
        os.mkdir(data)
    
    search_url = Google_Image + 'q=' + data #'q=' because its a query
    print(search_url)
    urls = scrape_images(search_url, wd, 0.001, num_images)
    print(f"Found {len(urls)}")

    for i, url in enumerate(urls):
    	download_image(data + "/", url, str(i) + ".jpg")
        
    print("Complete!")
    wd.quit()

def scrape_images(initial_url, wd, delay, max_images):
    def scroll(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)
        
    url = initial_url
    wd.get(url)
    image_urls = set()
    skips = 0
        
    while len(image_urls) + skips < max_images:
        scroll(wd)
        thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")
        # prevent adding the same thumbnail over and over again
        for img in thumbnails[len(image_urls) + skips: max_images]:
            try:
                img.click()
                time.sleep(delay)
            except:
                continue
                
            images = wd.find_elements(By.CSS_SELECTOR, ".sFlh5c.pT0Scc.iPVvYb")
            print(images)
            for image in images:
                if image.get_attribute('src') in image_urls:
                    max_images += 1
                    skips += 1
                    break
                    
                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.add(image.get_attribute('src'))
                    print(image_urls)
                        
    return image_urls
                    
def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content) # like storing a file in memory
        image = Image.open(image_file)  # Convert binary to an image
        file_path = download_path + file_name
        
        with open(file_path, "wb") as f:
            image.save(f, "JPEG")
            
        print("Success!")
    except Exception as e:
        print("Failed -", e)
        

if __name__ == '__main__':
    main()