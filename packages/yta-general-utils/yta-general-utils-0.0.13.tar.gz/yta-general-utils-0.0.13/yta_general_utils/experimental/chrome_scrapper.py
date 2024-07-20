from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
import os
import pyautogui
import glob
import shutil

PROJECT_ABSOLUTE_PATH = os.getenv('PROJECT_ABSOLUTE_PATH')
TOUSE_ABSOLUTE_PATH = os.getenv('TOUSE_ABSOLUTE_PATH') 

def go_to_and_wait_loaded(driver, url):
    """
    Navigates to the provided 'url', using the provided 'driver', and waits until
    the page is loaded (by readyState method). If it is loaded, it returns True.
    If not, it returns False.

    This method will wait for 10 seconds maximum.
    """
    try:
        driver.get(url)

        page_state = 'loading'
        cont = 0
        while page_state != 'complete' and cont < 20:
            time.sleep(0.5)
            page_state = driver.execute_script('return document.readyState;')
            cont += 1

        if page_state == 'loading':
            return False
        
        return True
    except:
        driver.close()

def start_chrome(gui = False, ad_blocker = True, disable_popups_and_cookies = True, additional_options = []):
    """
    Starts the chrome driver with the local configuration and returns it. If 'gui' is True,
    it will show the Chrome working.

    Additional options must be simple strings. Cookies must be objects with .name and .value.
    """
    try:
        CHROME_EXTENSIONS_ABSOLUTEPATH = 'C:/Users/dania/AppData/Local/Google/Chrome/User Data/Profile 2/Extensions/'
        # TODO: Extensions versions are updated, so check below line
        AD_BLOCK_ABSOLUTEPATH = CHROME_EXTENSIONS_ABSOLUTEPATH + 'cjpalhdlnbpafiamejdnhcphjbkeiagm/1.58.0_0'

        # TODO: What if 'import undetected_chromedriver.v2 as uc'? Try it

        options = Options()
        
        option_arguments = ['--start-maximized']

        if len(additional_options) > 0:
            for additional_option in additional_options:
                option_arguments.append(additional_option)

        if not gui:
            option_arguments.append('--headless=new')

        if ad_blocker:
            # This loads the ad block 'uBlock' extension that is installed in my pc
            option_arguments.append('load-extension=' + AD_BLOCK_ABSOLUTEPATH)
        
        # Load user profile
        option_arguments.append('user-data-dir=C:/Users/dania/AppData/Local/Google/Chrome/User Data/Profile 2')

        for argument in option_arguments:
            options.add_argument(argument)

        if disable_popups_and_cookies:
            # TODO: Separate this into specific options, not all together. One is for cookies,
            # another one is for popups... Separate them, please
            # This disables popups, cookies and that stuff
            options.add_experimental_option('prefs', {
                'excludeSwitches': ['enable-automation', 'load-extension', 'disable-popup-blocking'],
                'profile.default_content_setting_values.automatic_downloads': 1,
                'profile.default_content_setting_values.media_stream_mic': 1
                })

        driver = webdriver.Chrome(options = options)

        return driver
    except:
        driver.close()

def download_fake_call_image(name, output_filename):
    # TODO: Move this to the faker
    URL = 'https://prankshit.com/fake-iphone-call.php'

    try:
        driver = start_chrome()
        go_to_and_wait_loaded(driver, URL)

        inputs = driver.find_elements(By.TAG_NAME, 'input')
        name_textarea = driver.find_element(By.TAG_NAME, 'textarea')

        #operator_input = inputs[4]
        #hour_input = inputs[5]

        name_textarea.clear()
        name_textarea.send_keys(name)

        image = driver.find_element(By.XPATH, '//div[contains(@class, "modal-content tiktok-body")]')
        image.screenshot(output_filename)
    finally:
        driver.close()

# Other fake generators (https://fakeinfo.net/fake-twitter-chat-generator) ad (https://prankshit.com/fake-whatsapp-chat-generator.php)
def download_discord_message_image(text, output_filename):
    URL = 'https://message.style/app/editor'

    try:
        driver = start_chrome()
        go_to_and_wait_loaded(driver, URL)
        
        time.sleep(3)

        clear_embed_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Clear Embeds')]")
        clear_embed_button.click()

        time.sleep(3)

        input_elements = driver.find_elements(By.TAG_NAME, 'input')
        username_input = input_elements[3]
        avatar_url_input = input_elements[4]

        username_input.clear()
        username_input.send_keys('botsito')

        avatar_url_input.clear()
        avatar_url_input.send_keys('https://cdn.pixabay.com/photo/2016/11/18/23/38/child-1837375_640.png')

        textarea_input = driver.find_element(By.TAG_NAME, 'textarea')
        textarea_input.clear()
        textarea_input.send_keys(text)

        time.sleep(3)

        # get element div class='discord-message'
        discord_message = driver.find_element(By.XPATH, "//div[contains(@class, 'discord-message')]")
        discord_message.screenshot(output_filename)
    finally:
        driver.close()


def navigate_to_and_screenshot(url, duration):
    """
    Browses the website 'url' and takes screenshots  while scrolling down. This method
    takes 30 screenshots per second.

    Returns the array of screenshot filenames stored locally.
    """
    try:
        FPS = 30

        driver = start_chrome()
        go_to_and_wait_loaded(driver, url)
        
        page_height = 0
        page_height = driver.execute_script("return document.body.scrollHeight")
        print(page_height)
        # We force it to 1000 if bigger
        if page_height > 1000:
            page_height = 1000

        screenshot_filenames = []
        number_of_screenshots = int(duration * FPS)

        # How much should we scroll?
        new_height = 0
        for i in range(number_of_screenshots):
            screenshot_filename = 'wip/screenshot_' + str(i) + '.png'
            driver.save_screenshot(screenshot_filename)
            screenshot_filenames.append(screenshot_filename)
            height = driver.execute_script("return window.pageYOffset")
            new_height += page_height / number_of_screenshots
            driver.execute_script('window.scrollTo(' + str(height) + ', ' + str(new_height) + ')')

        driver.execute_script("window.close();")
    finally:
        driver.close()

    # TODO: These screenshots are not 1920x1080, so crop them from center to sides
    return screenshot_filenames
    

def test_download_piano_music():
    # TODO: End this, to make it download music generated by this AI
    try:
        options = Options()
        #option_arguments = ['--start-maximized', '--headless=new']
        option_arguments = ['--start-maximized']
        for argument in option_arguments:
            options.add_argument(argument)

        driver = webdriver.Chrome(options = options)
        driver.get('https://huggingface.co/spaces/mrfakename/rwkv-music')
        wait = WebDriverWait(driver, 30)
        download_button_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-testid=\"checkbox\"]')))

        time.sleep(5)
        actions = ActionChains(driver)
        for i in range(11):
            actions.send_keys(Keys.TAB)
        actions.perform()
        actions.send_keys(Keys.SPACE)
        actions.perform()

        input_number_element = driver.find_elements_by_xpath('//*[@data-testid="number-input"]')[0]
        input_number_element.send_keys(14286)

        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB)
        actions.perform()

        time.sleep(1)

        driver.execute_script('window.scrollTo(0, 1000)')

        time.sleep(4)

        download_button_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@title=\"Download\"]')))
        #download_button_element = driver.find_elements_by_xpath('//*[@title="Download"]')[0]
        download_button_element.click()

    finally:
        driver.close()


def goto_and_scroll(url):
    # Intersting options: https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1726
    # Also this: https://stackoverflow.com/questions/19211006/how-to-enable-cookies-in-chromedriver-with-webdriver
    # What about this: options.AddUserProfilePreference("profile.cookie_controls_mode", 0);
    try:
        options = Options()
        option_arguments = ['--start-maximized', '--disabled-infobars', '--disable-blink-features=AutomationControlled', '--disable-animations', '--no-sandbox', '--disable-setuid-sandbox']
        # options.AddUserProfilePreference("profile.cookie_controls_mode", 0);
        for argument in option_arguments:
            options.add_argument(argument)

        """
        experimental_option_arguments = [{
            'option': 'excludeSwitches',
            'value': 'enable-automation'
        }]
        if len(experimental_option_arguments) > 0:
            options.add_experimental_option(experimental_option_arguments)
        """
        # Remove this line below for debug
        #options.add_argument("--headless=new") # for Chrome >= 109
        print('@@@@@@@@@@@@@')
        driver = webdriver.Chrome(options = options)
        print('@@@@@@@@@@@@@')
        driver.get(url)
        print('here i am')

        # Accept cookies

        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        driver.execute_script('window.scrollTo(0, 200)')
        time.sleep(4)
    except Exception as e:
        print(e)
    finally:
        driver.close()

def get_redicted_url(url, expected_url = None, wait_time = 5):
    """
    Navigates to the provided url and waits for a redirection. This method will wait
    until the 'expected_url' is contained in the new url (if 'expected_url' parameter
    is provided), or waits 'wait_time' seonds to return the current_url after that.
    """
    redirected_url = ''

    try:
        options = Options()
        options.add_argument("--start-maximized")
        # Remove this line below for debug
        options.add_argument("--headless=new") # for Chrome >= 109
        driver = webdriver.Chrome(options = options)
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        if not expected_url:
            time.sleep(wait_time)
        else:
            wait.until(EC.url_contains(expected_url))

        redirected_url = driver.current_url
    finally:
        driver.close()

    return redirected_url


def get_youtube_summary(video_id):
    """
    Searchs into 'summarize.tech' web to obtain the summary of the video with the 
    provided 'video_id'. This method returns the summary in English, as it is 
    provided by that website.
    """
    url = 'https://www.summarize.tech/www.youtube.com/watch?v=' + video_id

    try:
        options = Options()
        options.add_argument("--start-maximized")
        # Remove this line below for debug
        options.add_argument("--headless=new") # for Chrome >= 109
        driver = webdriver.Chrome(options = options)
        driver.get(url)

        summary = driver.find_element_by_tag_name('section').find_element_by_tag_name('p').get_attribute('innerText')
    finally:
        driver.close()

    return summary

def google_translate(text, input_language = 'en', output_language = 'es'):
    url = 'https://translate.google.com/?hl=es'
    """
    https://translate.google.com/?hl=es&sl=en&tl=es&text=Aporta%20una%20unidad%20de%20traducci%C3%B3n%20(segmento%20y%20traducci%C3%B3n)%20en%20alg%C3%BAn%20par%20de%20idiomas%20a%20MyMemory.%0ASin%20especificar%20ning%C3%BAn%20par%C3%A1metro%20clave%2C%20la%20contribuci%C3%B3n%20est%C3%A1%20disponible%20para%20todos%20(%C2%A1Gracias!).&op=translate

    https://translate.google.com/?hl=es&tab=TT&sl=en&tl=es&op=translate

    https://translate.google.com/?hl=es&tab=TT&sl=en&tl=es&text=La%20%C3%BAnica%20forma%20de%20saberlo%20es%20lo%20que%20t%C3%BA%20digas&op=translate
    """

    url = 'https://translate.google.com/?hl=' + output_language + '&tab=TT&sl=' + input_language + '&tl=' + output_language + '&text=' + text + '&op=translate'

    translation = ''

    try:
        options = Options()
        options.add_argument("--start-maximized")
        # Comment this line below for debug (enables GUI)
        options.add_argument("--headless=new") # for Chrome >= 109
        driver = webdriver.Chrome(options = options)
        driver.get(url)

        tries = 0
        while True:
            if tries < 20:
                try:
                    # We try until it doesn't fail (so we have the text)
                    # TODO: This 'jscontroller' changes from time to time, pay atention
                    translation = driver.find_elements('xpath', '//*[@jscontroller="JLEx7e"]')[0].get_attribute('innerText')
                    tries = 20
                except Exception as e:
                    # TODO: Uncomment this to see if code error or scrapper error
                    #print(e)
                    tries += 1
                    time.sleep(0.250)
            else:
                break
    finally:
        driver.close()

    return translation