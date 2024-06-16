from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import ctypes
import platform
import datetime
import os
import sys
import time

if getattr(sys, 'frozen', False):
    env_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    env_path = '.env'

load_dotenv(env_path)

# Environment variables
COURT = os.getenv("COURT")
PASSWORD = os.getenv("PASSWORD")
TESTING_OVERRIDE = os.getenv("TESTING_OVERRIDE")
TIME = os.getenv("TIME")
USERNAME = os.getenv("USER_NAME")


class Config:
    STARTING_URL = "https://www.boulevardclub.com/login.aspx"
    TARGET_TIME = datetime.time(hour=8, minute=0, second=0)  # 08:00:00 AM
    USERNAME_ID = 'p_lt_ContentWidgets_pageplaceholder_p_lt_zoneContent_CHO_Widget_LoginFormWithFullscreenBackground_XLarge_loginCtrl_BaseLogin_UserName'
    PASSWORD_ID = 'p_lt_ContentWidgets_pageplaceholder_p_lt_zoneContent_CHO_Widget_LoginFormWithFullscreenBackground_XLarge_loginCtrl_BaseLogin_Password'
    LOGIN_BUTTON_ID = 'p_lt_ContentWidgets_pageplaceholder_p_lt_zoneContent_CHO_Widget_LoginFormWithFullscreenBackground_XLarge_loginCtrl_BaseLogin_LoginButton'
    SPORT_BOOKINGS_XPATH = "//a[text()='Sport Bookings']"
    TENNIS_XPATH = "//a[text()='TENNIS']"
    DATE_SELECTOR_XPATH = "//div[@id='dateSelector-picker']/ul/li[last()]"
    COURT_HEADER_XPATH = f"//th[a/span/text()='{COURT}']"
    TIMESLOT_XPATH_TEMPLATE = f"//table[@class='courtViewer']/tbody/tr/td[{{}}]//div[contains(@class, 'timeslot') and .//div[@class='time' and contains(text(),  '{TIME}')]]"
    SUCCESS_SCREENSHOT_PATH = "screenshot_success.png"
    ERROR_SCREENSHOT_PATH = "screenshot_error.png"


def wait_for_visibility(driver, by, value, timeout=5):
    """Wait until an element is visible."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located((by, value)))


def wait_for_visibility_of_elements(driver, by, value, timeout=5):
    """Wait until all elements are visible."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_all_elements_located((by, value)))


def setup_driver():
    """Setup the Chrome driver."""
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def login(driver, username, password):
    """Login to the website."""
    driver.get(Config.STARTING_URL)
    username_field = wait_for_visibility(driver, By.ID, Config.USERNAME_ID)
    password_field = wait_for_visibility(driver, By.ID, Config.PASSWORD_ID)
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button = wait_for_visibility(driver, By.ID, Config.LOGIN_BUTTON_ID)
    login_button.click()


def navigate_to_tennis(driver):
    """Navigate to the tennis page."""
    sport_bookings_button = wait_for_visibility(driver, By.XPATH, Config.SPORT_BOOKINGS_XPATH)
    sport_bookings_button.click()
    tennis_button = wait_for_visibility(driver, By.XPATH, Config.TENNIS_XPATH)
    tennis_button.click()


def select_date(driver):
    """Select the date."""
    last_li = wait_for_visibility(driver, By.XPATH, Config.DATE_SELECTOR_XPATH)
    last_li.find_element(By.TAG_NAME, "a").click()


def wait_until_target_time():
    """Wait until the target time."""
    if TESTING_OVERRIDE == 'True':
        print("Waiting for 5 seconds")
        time.sleep(5)
    else:
        now = datetime.datetime.now()
        current_time = now.time()
        if current_time > Config.TARGET_TIME:
            target_datetime = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), Config.TARGET_TIME)
        else:
            target_datetime = datetime.datetime.combine(now.date(), Config.TARGET_TIME)
        time_difference = (target_datetime - now).total_seconds()
        print(f"Waiting for {time_difference} seconds")
        time.sleep(time_difference)


def book_timeslot(driver):
    """Book the timeslot."""
    court_6_elements = wait_for_visibility_of_elements(driver, By.XPATH,
                                                       f"{Config.COURT_HEADER_XPATH}/preceding-sibling::th")
    court_6_index = len(court_6_elements) + 1
    timeslot_xpath = Config.TIMESLOT_XPATH_TEMPLATE.format(court_6_index)
    timeslot_element = wait_for_visibility(driver, By.XPATH, timeslot_xpath)
    timeslot_element.click()


def main():
    """Main script."""
    driver = setup_driver()
    try:
        login(driver, USERNAME, PASSWORD)
        navigate_to_tennis(driver)
        select_date(driver)
        wait_until_target_time()
        book_timeslot(driver)
        driver.save_screenshot(Config.SUCCESS_SCREENSHOT_PATH)
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot(Config.ERROR_SCREENSHOT_PATH)
    finally:
        input("Press Enter to close...")

        # if getattr(sys, 'frozen', False):
        #     if platform.system() == 'Windows':
        #         ctypes.windll.user32.MessageBoxW(0, "Press OK to close...", "Done", 1)
        #     elif platform.system() == 'Darwin':  # macOS
        #         os.system(
        #             '''/usr/bin/osascript -e 'tell app "System Events" to display dialog "Press OK to close..." buttons {"OK"}' ''')
        # else:


if __name__ == "__main__":
    main()
