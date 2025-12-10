import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from faker import Faker

WAIT_TIMEOUT = 10
STEAM_URL = "https://store.steampowered.com"
EXPECTED_ERROR_TEXT = "Пожалуйста, проверьте свой пароль и имя аккаунта и попробуйте снова."

LOGIN_BUTTON = (By.XPATH, "//a[contains(@class, 'global_action_link')]")
LOGIN_FORM = (
    By.XPATH, "//form[.//input[@type='text'] and .//input[@type='password']]")
USERNAME_FIELD = (By.XPATH, ".//input[@type='text']")
PASSWORD_FIELD = (By.XPATH, ".//input[@type='password']")
SUBMIT_BUTTON = (By.XPATH, ".//*[@type='submit']")
LOADING_INDICATOR = (By.XPATH, "//form//button[@type='submit' and @disabled]")
ERROR_MESSAGE = (
    By.XPATH, "//button[@type='submit']/parent::div/following-sibling::div")
UNIQUE_MAIN_PAGE_ELEMENT = (By.ID, "global_header")
UNIQUE_LOGIN_PAGE_ELEMENT = (By.XPATH, '//div[@data-featuretarget="login"]')

fake = Faker()


@pytest.fixture
def driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, WAIT_TIMEOUT)


class TestSteamLogin:
    def test_failed_login_shows_error(self, driver, wait):
        driver.get(STEAM_URL)
        wait.until(EC.visibility_of_element_located(UNIQUE_MAIN_PAGE_ELEMENT))

        login_btn = wait.until(EC.element_to_be_clickable(LOGIN_BUTTON))
        login_btn.click()

        wait.until(EC.presence_of_element_located(UNIQUE_LOGIN_PAGE_ELEMENT))

        login_form = wait.until(EC.presence_of_element_located(LOGIN_FORM))

        username = login_form.find_element(*USERNAME_FIELD)
        password = login_form.find_element(*PASSWORD_FIELD)

        username.send_keys(fake.user_name())
        password.send_keys(fake.password())

        submit_btn = login_form.find_element(*SUBMIT_BUTTON)
        submit_btn.click()

        wait.until(EC.presence_of_element_located(LOADING_INDICATOR))
        wait.until(EC.invisibility_of_element_located(LOADING_INDICATOR))

        error_element = wait.until(
            EC.visibility_of_element_located(ERROR_MESSAGE))

        actual_error_text = error_element.text

        assert EXPECTED_ERROR_TEXT in actual_error_text, \
            f"Фактическое: '{actual_error_text}' | Ожидаемое: должен содержать '{EXPECTED_ERROR_TEXT}'"
