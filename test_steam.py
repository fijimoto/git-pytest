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
ERROR_KEYWORDS = ['error', 'ошиб', 'невер', 'invalid', 'wrong', 'проверь']

LOGIN_BUTTON = (By.XPATH, "//a[contains(@class, 'global_action_link')]")
LOGIN_FORM = (
    By.XPATH, "//form[.//input[@type='text'] and .//input[@type='password']]")
USERNAME_FIELD = (By.XPATH, ".//input[@type='text']")
PASSWORD_FIELD = (By.XPATH, ".//input[@type='password']")
SUBMIT_BUTTON = (By.XPATH, ".//*[@type='submit']")
ERROR_MESSAGE = (
    By.XPATH, "//*[@role='alert' or contains(@class, 'error') or contains(@class, 'alert')]")
UNIQUE_MAIN_PAGE_ELEMENT = (By.ID, "global_header")

fake = Faker()


@pytest.fixture
def driver():
    """Фикстура для инициализации драйвера"""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def wait(driver):
    """Фикстура для ожиданий"""
    return WebDriverWait(driver, WAIT_TIMEOUT)


class TestSteamLogin:
    def test_failed_login_shows_error(self, driver, wait):
        """Тест неудачного входа на Steam"""

        driver.get(STEAM_URL)
        wait.until(EC.visibility_of_element_located(UNIQUE_MAIN_PAGE_ELEMENT))

        login_btn = wait.until(EC.element_to_be_clickable(LOGIN_BUTTON))
        login_btn.click()

        login_form = wait.until(EC.presence_of_element_located(LOGIN_FORM))

        username = login_form.find_element(*USERNAME_FIELD)
        password = login_form.find_element(*PASSWORD_FIELD)

        random_login = fake.email()
        random_password = fake.password()

        username.send_keys(random_login)
        password.send_keys(random_password)

        submit_btn = login_form.find_element(*SUBMIT_BUTTON)
        submit_btn.click()

        error_found = False
        error_text = ""

        try:
            error_elements = driver.find_elements(*ERROR_MESSAGE)
            for error in error_elements:
                if error.is_displayed() and error.text:
                    error_text = error.text
                    error_found = True
                    break
        except:
            pass

        if not error_found:
            all_elements = driver.find_elements(By.XPATH, "//*[text()]")
            for element in all_elements:
                if element.is_displayed():
                    text = element.text.lower()
                    if any(keyword in text for keyword in ERROR_KEYWORDS):
                        error_text = element.text
                        error_found = True
                        break

        assert error_found, "Не удалось найти сообщение об ошибке"
        assert len(error_text) > 0, "Текст ошибки пуст"

        print(f"Тест пройден! Ошибка входа: '{error_text}'")
