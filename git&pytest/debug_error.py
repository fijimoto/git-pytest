"""
debug_error_locator.py - Скрипт для поиска правильного локатора ошибки
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

STEAM_URL = "https://store.steampowered.com"

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

try:
    # Открываем страницу
    driver.get(STEAM_URL)
    time.sleep(2)

    # Кликаем Login
    login_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//a[contains(@class, 'global_action_link') and contains(@href, 'login')]")
    ))
    login_btn.click()
    time.sleep(3)

    # Заполняем форму
    username = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[@data-featuretarget='login']//input[@type='text']")
    ))
    password = wait.until(EC.visibility_of_element_located(
        (By.XPATH,
         "//div[@data-featuretarget='login']//input[@type='password']")
    ))

    username.send_keys("test_user")
    password.send_keys("test_pass")

    # Кликаем Submit
    submit = wait.until(EC.element_to_be_clickable(
        (By.XPATH,
         "//div[@data-featuretarget='login']//button[@type='submit']")
    ))
    submit.click()

    print("Форма отправлена, ждём 5 секунд...")
    time.sleep(5)

    # Пробуем разные варианты локаторов для ошибки
    print("\n" + "="*60)
    print("ПОИСК ЛОКАТОРА ОШИБКИ")
    print("="*60 + "\n")

    error_locators = [
        # Вариант 1: следующий div после кнопки
        (By.XPATH,
         "//div[@data-featuretarget='login']//button[@type='submit']/following-sibling::div[1]"),

        # Вариант 2: любой div после кнопки, содержащий текст
        (By.XPATH,
         "//div[@data-featuretarget='login']//button[@type='submit']/following-sibling::div[text()]"),

        # Вариант 3: div внутри формы, который содержит текст с ошибкой
        (By.XPATH, "//div[@data-featuretarget='login']//form//div[contains(text(), 'пароль') or contains(text(), 'password')]"),

        # Вариант 4: все div'ы в форме
        (By.XPATH, "//div[@data-featuretarget='login']//form//div"),

        # Вариант 5: div после всех input'ов
        (By.XPATH,
         "//div[@data-featuretarget='login']//form//input[@type='password']/following::div[1]"),

        # Вариант 6: любой div который появился и имеет текст
        (By.XPATH,
         "//div[@data-featuretarget='login']//form//*[string-length(text()) > 0]"),
    ]

    for i, locator in enumerate(error_locators, 1):
        print(f"Вариант {i}: {locator[1]}")
        try:
            elements = driver.find_elements(*locator)
            if elements:
                print(f"  ✅ Найдено элементов: {len(elements)}")
                for j, elem in enumerate(elements[:3], 1):
                    try:
                        text = elem.text.strip()
                        if text and text != "\xa0":
                            print(f"    [{j}] Текст: '{text[:100]}'")
                            print(f"    [{j}] Tag: {elem.tag_name}")
                            print(f"    [{j}] Видим: {elem.is_displayed()}")
                    except:
                        pass
            else:
                print(f"  ❌ Элементы не найдены")
        except Exception as e:
            print(f"  ❌ Ошибка: {str(e)[:100]}")
        print()

    # Делаем скриншот
    driver.save_screenshot("debug_error_page.png")
    print("📸 Скриншот сохранён: debug_error_page.png")

    # Выводим HTML формы для анализа
    print("\n" + "="*60)
    print("HTML СТРУКТУРА ФОРМЫ")
    print("="*60 + "\n")

    form = driver.find_element(
        By.XPATH, "//div[@data-featuretarget='login']//form")
    print(form.get_attribute('outerHTML')[:2000])  # Первые 2000 символов

    input("Нажми Enter чтобы закрыть браузер...")

finally:
    driver.quit()
