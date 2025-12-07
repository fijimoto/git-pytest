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

LOGIN_BUTTON = (
    By.XPATH,
    "//a[contains(@class, 'global_action_link') and contains(@href, 'login')]"
)

LOGIN_PAGE_UNIQUE_ELEMENT = (
    By.XPATH,
    "//div[@data-featuretarget='login']"
)

USERNAME_FIELD = (
    By.XPATH,
    "//div[@data-featuretarget='login']//input[@type='text']"
)

PASSWORD_FIELD = (
    By.XPATH,
    "//div[@data-featuretarget='login']//input[@type='password']"
)

SUBMIT_BUTTON = (
    By.XPATH,
    "//div[@data-featuretarget='login']//button[@type='submit']"
)

ERROR_CONTAINER = (
    By.XPATH,
    "//div[@data-featuretarget='login']//form//button[@type='submit']/parent::div/following-sibling::div[1]"
)

fake = Faker()


@pytest.fixture
def driver():
    """Фикстура для инициализации и закрытия драйвера"""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def wait(driver):
    """Фикстура для явных ожиданий"""
    return WebDriverWait(driver, WAIT_TIMEOUT)


class ElementHasText:
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            text = element.text.strip()
            if text and len(text) > 0 and text != "\xa0":
                return element
            return False
        except:
            return False


class TestSteamLogin:
    def test_failed_login_shows_error(self, driver, wait):
        driver.get(STEAM_URL)
        print("Страница Steam открыта")

        login_btn = wait.until(EC.element_to_be_clickable(LOGIN_BUTTON))
        print("Кнопка Login найдена")
        login_btn.click()
        print("Кликнули на Login")

        wait.until(EC.presence_of_element_located(LOGIN_PAGE_UNIQUE_ELEMENT))
        print(f"Страница входа загружена")

        username_input = wait.until(
            EC.visibility_of_element_located(USERNAME_FIELD)
        )
        password_input = wait.until(
            EC.visibility_of_element_located(PASSWORD_FIELD)
        )
        print("Поля ввода найдены")

        random_login = fake.user_name()
        random_password = fake.password()

        username_input.send_keys(random_login)
        password_input.send_keys(random_password)
        print(f"Данные введены: {random_login} / {random_password}")

        submit_btn = wait.until(EC.element_to_be_clickable(SUBMIT_BUTTON))
        submit_btn.click()
        print("Форма отправлена")

        try:
            error_element = wait.until(ElementHasText(ERROR_CONTAINER))
            error_text = error_element.text.strip()
            print(f"Ошибка отображена: '{error_text}'")
        except Exception as e:
            # Если ошибка не найдена делается скриншот для отладки + fail с подробным сообщением с указанием на expected и actual для условного отчета
            screenshot_path = "error_not_found.png"
            driver.save_screenshot(screenshot_path)

            pytest.fail(
                f"Expected: Сообщение об ошибке должно появиться в элементе. "
                f"Actual: Текст ошибки не появился в течение {WAIT_TIMEOUT} секунд. "
                f"Локатор: {ERROR_CONTAINER[1]}. "
                f"Скриншот: {screenshot_path}. "
                f"Ошибка: {str(e)}"
            )

        # Шаг 9: Проверяем что текст ошибки не пустой
        assert len(error_text) > 0, (
            f"Expected: Текст ошибки не пустой (длина > 0). "
            f"Actual: Длина текста = {len(error_text)}: '{error_text}'"
        )

# Доп. проверка
        error_keywords = [
            'пароль', 'password',
            'аккаунт', 'account',
            'проверьте', 'check',
            'неверн', 'incorrect',
            'invalid', 'попробуйте'
        ]

        has_keyword = any(
            keyword.lower() in error_text.lower()
            for keyword in error_keywords
        )

        assert has_keyword, (
            f"Expected: Текст ошибки содержит одно из ключевых слов: {error_keywords}. "
            f"Actual: Получен текст '{error_text}'"
        )

        print(f"\n Тест успешно пройден!")
        print(f"Сообщение об ошибке: '{error_text}'")
