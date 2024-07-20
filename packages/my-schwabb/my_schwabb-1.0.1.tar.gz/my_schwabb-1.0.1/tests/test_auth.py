from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--remote-debugging-pipe')
chrome_options.binary_location = '/home/dev/Downloads/chromedriver'

# Specify the path to the ChromeDriver if necessary
service = Service('/home/dev/Downloads/chromedriver')

driver = webdriver.Chrome(service=service, options=chrome_options)


# Navigate to the webpage
# driver.get('https://api.schwabapi.com/v1/oauth/authorize?client_id=1wzwOrhivb2PkR1UCAUVTKYqC4MTNYlj&redirect_uri=https://127.0.0.1')
driver.get('https://www.google.com')

# Option 1: Locate button by ID and click it
# button = driver.find_element(By.ID, 'button-id')
# button.click()

# Option 2: Locate button by name and click it
# button = driver.find_element(By.NAME, 'button-name')
# button.click()

# Option 3: Locate button by class name and click it
# button = driver.find_element(By.CLASS_NAME, 'button-class')
# button.click()

# Option 4: Locate button by CSS selector and click it
# button = driver.find_element(By.CSS_SELECTOR, 'button.button-class')
# button.click()

# Option 5: Locate button by XPath and click it
# button = driver.find_element(By.XPATH, '//*[@id="button-id"]')
# button.click()

# Option 6: Using ActionChains to click (useful for complex scenarios)
# actions = ActionChains(driver)
# actions.move_to_element(button).click().perform()

# Add some delay to see the action (optional)
# time.sleep(5)

# Close the browser
# driver.quit()