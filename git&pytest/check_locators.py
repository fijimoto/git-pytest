"""
Скрипт для проверки и поиска локаторов на странице Steam
Используй этот файл для отладки и поиска правильных локаторов
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def check_locator(driver, by, value, description):
    """
    Универсальная функция для проверки локатора

    Args:
        driver: WebDriver instance
        by: By.XPATH, By.CSS_SELECTOR и т.д.
        value: значение локатора
        description: описание что ищем
    """
    try:
        element = driver.find_element(by, value)
        print(f"✅ {description}")
        print(f"   Локатор: {by} = '{value}'")
        # Первые 100 символов
        print(f"   Текст элемента: '{element.text[:100]}'")
        print(
            f"   Атрибуты: tag={element.tag_name}, visible={element.is_displayed()}")
        print()
        return True
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Локатор: {by} = '{value}'")
        print(f"   Ошибка: {str(e)[:100]}")
        print()
        return False


def check_multiple_elements(driver, by, value, description):
    """
    Проверяет сколько элементов найдено по локатору
    """
    try:
        elements = driver.find_elements(by, value)
        print(f"🔍 {description}")
        print(f"   Локатор: {by} = '{value}'")
        print(f"   Найдено элементов: {len(elements)}")

        for i, elem in enumerate(elements[:3], 1):  # Показываем первые 3
            print(
                f"   [{i}] Текст: '{elem.text[:50]}', visible={elem.is_displayed()}")
        print()
        return len(elements)
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Ошибка: {str(e)}")
        print()
        return 0


def main():
    """Основная функция для проверки локаторов"""

    # Инициализация драйвера
    print("🚀 Запуск браузера...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    try:
        # ============= ШАГ 1: Главная страница =============
        print("\n" + "="*60)
        print("ШАГ 1: Открываем главную страницу Steam")
        print("="*60 + "\n")

        driver.get("https://store.steampowered.com")
        time.sleep(2)

        # Проверяем что страница загрузилась
        print(f"📍 Текущий URL: {driver.current_url}")
        print(f"📍 Заголовок: {driver.title}\n")

        # ============= ШАГ 2: Поиск кнопки Login =============
        print("\n" + "="*60)
        print("ШАГ 2: Ищем кнопку LOGIN")
        print("="*60 + "\n")

        # Пробуем разные варианты локаторов для кнопки Login
        login_locators = [
            (By.LINK_TEXT, "login", "Кнопка Login по LINK_TEXT"),
            (By.PARTIAL_LINK_TEXT, "login", "Кнопка Login по PARTIAL_LINK_TEXT"),
            (By.XPATH, "//a[contains(text(), 'login')]",
             "Кнопка Login по XPath (text)"),
            (By.XPATH, "//a[contains(@href, 'login')]",
             "Кнопка Login по XPath (href)"),
            (By.CSS_SELECTOR, "a[href*='login']",
             "Кнопка Login по CSS (href)"),
            (By.XPATH, "//a[contains(@class, 'global_action_link')]",
             "Кнопка Login по классу"),
        ]

        login_button = None
        for by, value, desc in login_locators:
            if check_locator(driver, by, value, desc):
                login_button = driver.find_element(by, value)
                print(f"👉 Используем этот локатор для Login!\n")
                break

        if not login_button:
            print("⛔ Кнопка Login не найдена! Завершаем...")
            return

        # ============= ШАГ 3: Кликаем на Login =============
        print("\n" + "="*60)
        print("ШАГ 3: Кликаем на кнопку Login")
        print("="*60 + "\n")

        login_button.click()
        time.sleep(3)  # Даём время загрузиться форме

        print(f"📍 URL после клика: {driver.current_url}\n")

        # Проверяем есть ли iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"🔍 Найдено iframe на странице: {len(iframes)}")

        if iframes:
            print("⚠️  Обнаружен iframe! Пробуем переключиться...\n")
            for i, iframe in enumerate(iframes):
                print(
                    f"   iframe[{i}]: id='{iframe.get_attribute('id')}', src='{iframe.get_attribute('src')[:50]}'")

            # Переключаемся в первый iframe
            driver.switch_to.frame(iframes[0])
            print("✅ Переключились в iframe[0]\n")
        else:
            print("✅ iframe не найден, работаем в основном окне\n")

        # ============= ШАГ 4: Поиск полей ввода =============
        print("\n" + "="*60)
        print("ШАГ 4: Ищем поле USERNAME")
        print("="*60 + "\n")

        username_locators = [
            (By.NAME, "username", "Username по NAME"),
            (By.ID, "username", "Username по ID"),
            (By.CSS_SELECTOR, "input[type='text']",
             "Username по CSS (type=text)"),
            (By.XPATH, "//input[@type='text']",
             "Username по XPath (type=text)"),
            (By.CSS_SELECTOR, "input[placeholder*='name']",
             "Username по placeholder"),
            (By.XPATH, "//input[contains(@class, 'username')]",
             "Username по классу"),
        ]

        username_field = None
        for by, value, desc in username_locators:
            if check_locator(driver, by, value, desc):
                username_field = driver.find_element(by, value)
                print(f"👉 Используем этот локатор для Username!\n")
                break

        # Проверяем сколько input type=text на странице
        check_multiple_elements(driver, By.XPATH, "//input[@type='text']",
                                "Все input с type='text'")

        # ============= ШАГ 5: Поиск поля пароля =============
        print("\n" + "="*60)
        print("ШАГ 5: Ищем поле PASSWORD")
        print("="*60 + "\n")

        password_locators = [
            (By.NAME, "password", "Password по NAME"),
            (By.ID, "password", "Password по ID"),
            (By.CSS_SELECTOR, "input[type='password']", "Password по CSS"),
            (By.XPATH, "//input[@type='password']", "Password по XPath"),
        ]

        password_field = None
        for by, value, desc in password_locators:
            if check_locator(driver, by, value, desc):
                password_field = driver.find_element(by, value)
                print(f"👉 Используем этот локатор для Password!\n")
                break

        # ============= ШАГ 6: Поиск кнопки Submit =============
        print("\n" + "="*60)
        print("ШАГ 6: Ищем кнопку SUBMIT")
        print("="*60 + "\n")

        submit_locators = [
            (By.CSS_SELECTOR, "button[type='submit']",
             "Submit по CSS (button)"),
            (By.XPATH, "//button[@type='submit']", "Submit по XPath (button)"),
            (By.CSS_SELECTOR, "input[type='submit']", "Submit по CSS (input)"),
            (By.XPATH, "//button[contains(text(), 'Sign in')]",
             "Submit по тексту"),
            (By.XPATH, "//button[contains(@class, 'submit')]",
             "Submit по классу"),
        ]

        submit_button = None
        for by, value, desc in submit_locators:
            if check_locator(driver, by, value, desc):
                submit_button = driver.find_element(by, value)
                print(f"👉 Используем этот локатор для Submit!\n")
                break

        # Проверяем все кнопки на странице
        check_multiple_elements(driver, By.TAG_NAME,
                                "button", "Все кнопки на странице")

        # ============= ШАГ 7: Заполняем форму и отправляем =============
        if username_field and password_field and submit_button:
            print("\n" + "="*60)
            print("ШАГ 7: Заполняем форму и отправляем")
            print("="*60 + "\n")

            username_field.send_keys("test_user_123")
            password_field.send_keys("test_password_456")
            print("✅ Поля заполнены\n")

            submit_button.click()
            print("✅ Форма отправлена\n")

            time.sleep(3)  # Ждём обработки

            # ============= ШАГ 8: Ищем Loading элемент =============
            print("\n" + "="*60)
            print("ШАГ 8: Ищем LOADING элемент")
            print("="*60 + "\n")

            loading_locators = [
                (By.XPATH, "//*[contains(@class, 'loading')]",
                 "Loading по классу 'loading'"),
                (By.XPATH, "//*[contains(@class, 'spinner')]",
                 "Loading по классу 'spinner'"),
                (By.CSS_SELECTOR, ".loading, .spinner", "Loading по CSS"),
                (By.XPATH, "//*[contains(@class, 'throbber')]",
                 "Loading по классу 'throbber'"),
            ]

            for by, value, desc in loading_locators:
                check_locator(driver, by, value, desc)

            # ============= ШАГ 9: Ищем сообщение об ошибке =============
            print("\n" + "="*60)
            print("ШАГ 9: Ищем ERROR сообщение")
            print("="*60 + "\n")

            error_locators = [
                (By.XPATH, "//*[contains(@class, 'error')]",
                 "Error по классу 'error'"),
                (By.XPATH, "//*[contains(@class, 'alert')]",
                 "Error по классу 'alert'"),
                (By.CSS_SELECTOR, ".error, .alert, .form-error", "Error по CSS"),
                (By.XPATH, "//*[@role='alert']", "Error по role='alert'"),
                (By.XPATH, "//*[contains(text(), 'incorrect')]",
                 "Error по тексту 'incorrect'"),
                (By.XPATH, "//*[contains(text(), 'invalid')]",
                 "Error по тексту 'invalid'"),
            ]

            for by, value, desc in error_locators:
                check_locator(driver, by, value, desc)

            # Проверяем все элементы с классом error или alert
            check_multiple_elements(driver, By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert')]",
                                    "Все элементы с классами error/alert")

        # ============= ИТОГИ =============
        print("\n" + "="*60)
        print("📊 ИТОГИ ПРОВЕРКИ")
        print("="*60 + "\n")

        print("✅ Проверка завершена!")
        print("📸 Делаем скриншот текущего состояния...\n")

        driver.save_screenshot("steam_page_state.png")
        print("💾 Скриншот сохранён: steam_page_state.png")

        # Пауза чтобы увидеть результат
        print("\n⏸️  Браузер останется открытым 10 секунд для изучения...")
        time.sleep(10)

    except Exception as e:
        print(f"\n⛔ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("💾 Скриншот ошибки: error_screenshot.png")

    finally:
        print("\n🔚 Закрываем браузер...")
        driver.quit()
        print("✅ Готово!")


if __name__ == "__main__":
    main()
