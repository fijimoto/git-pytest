import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import random
import string


def random_string(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


class TestSteamLogin:
    def setup_method(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 10)

    def teardown_method(self):
        self.driver.quit()

    def test_failed_login_shows_error(self):
        self.driver.get("https://store.steampowered.com")
        print("Главная страница Steam открыта. Успешно")

        login_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "(//*[contains(@class, 'global_action_link')])[1]"))
        )
        login_btn.click()
        print("Кнопка входа нажата. Успешно")

        username = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "(//*[contains(@class, '_2GBWeup')])[1]"))
        )
        password = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "(//*[contains(@class, '_2GBWeup')])[2]"))
        )

        random_login = random_string()
        random_password = random_string()
        username.send_keys(random_login)
        password.send_keys(random_password)
        print(f"Введены случайные данные: {random_login}/{random_password}")

        submit_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(@class, 'DjSvCZoK') and contains(text(),'Войти')]"))
        )
        submit_btn.click()
        print("Кнопка 'Войти' нажата")

        error_message = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'_1W_6HX') and contains(text(),'проверьте свой пароль')]"))
        )

        assert error_message.is_displayed(), "Сообщение об ошибке не отображается"
        print("Тест пройден! Ошибка входа отображается корректно")
        print(f"Текст ошибки: {error_message.text}")


if __name__ == "__main__":
    test = TestSteamLogin()
    test.setup_method()
    try:
        test.test_failed_login_shows_error()
        print("Тест завершен успешно!")
    except Exception as e:
        print(f"Тест упал с ошибкой: {e}")
    finally:
        test.teardown_method()
