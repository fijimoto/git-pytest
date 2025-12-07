from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from faker import Faker
import time

fake = Faker()

# Настройки чтобы обойти защиту
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option(
    "excludeSwitches", ["enable-automation"])
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("🔍 Проверяем Steam с нормальным user-agent...")

    driver.get("https://store.steampowered.com")
    time.sleep(3)

    # Нажимаем вход
    login_btn = driver.find_element(
        By.XPATH, "//a[contains(@class, 'global_action_link')]")
    print(f"Нашел кнопку: '{login_btn.text}'")
    login_btn.click()
    time.sleep(3)

    print(f"Текущий URL: {driver.current_url}")
    print(f"Title: {driver.title}")

    # Ищем форму
    forms = driver.find_elements(By.TAG_NAME, "form")
    print(f"Нашел форм: {len(forms)}")

    # Покажем содержимое страницы
    print("\n🔍 Содержимое страницы (первые 2000 символов):")
    print(driver.page_source[:2000])

    # Ищем текст "ошибка", "error", "неверно" в исходном коде
    page_source = driver.page_source.lower()
    keywords = ['ошиб', 'error', 'невер', 'invalid', 'wrong']
    found_keywords = []

    for keyword in keywords:
        if keyword in page_source:
            found_keywords.append(keyword)

    print(f"\n🔍 Нашел ключевые слова в исходном коде: {found_keywords}")

    # Пробуем найти любые видимые сообщения
    all_text = driver.find_elements(By.XPATH, "//*[text()]")
    visible_texts = []

    for element in all_text:
        if element.is_displayed():
            text = element.text.strip()
            if text:
                visible_texts.append(text[:50])

    print(f"\n🔍 Видимый текст на странице (первые 10):")
    for i, text in enumerate(visible_texts[:10]):
        print(f"{i+1}. '{text}'")

    input("\nНажми Enter для ввода тестовых данных...")

    # Пробуем найти форму ввода
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\n🔍 Input поля на странице:")

    text_inputs = []
    password_inputs = []

    for inp in inputs:
        inp_type = inp.get_attribute("type")
        if inp_type == "text":
            text_inputs.append(inp)
        elif inp_type == "password":
            password_inputs.append(inp)

    print(
        f"Text inputs: {len(text_inputs)}, Password inputs: {len(password_inputs)}")

    if text_inputs and password_inputs:
        print("Пробую ввести данные...")
        text_inputs[0].send_keys(fake.email())
        password_inputs[0].send_keys(fake.password())
        time.sleep(1)

        # Ищем кнопку отправки
        buttons = driver.find_elements(By.TAG_NAME, "button")
        submit_buttons = [
            btn for btn in buttons if btn.get_attribute("type") == "submit"]

        if submit_buttons:
            print(f"Нашел кнопку отправки: '{submit_buttons[0].text}'")
            submit_buttons[0].click()
            time.sleep(5)

            print(f"\nПосле отправки URL: {driver.current_url}")
            print(f"После отправки Title: {driver.title}")

            # Проверяем изменился ли URL
            if "login" not in driver.current_url:
                print("⚠️ Похоже нас перенаправило - возможно Steam принял данные?")
            else:
                print("✅ Остались на странице логина - ищем ошибку...")

                # Ищем любой красный текст или сообщения
                all_elements = driver.find_elements(By.XPATH, "//*")
                for element in all_elements:
                    try:
                        color = element.value_of_css_property("color")
                        if "rgb(255, 0, 0)" in color or "rgba(255, 0, 0" in color:
                            text = element.text.strip()
                            if text:
                                print(f"🔴 Нашел красный текст: '{text}'")
                    except:
                        pass
        else:
            print("❌ Не нашел кнопку отправки")
    else:
        print("❌ Не нашел поля для ввода")

    input("\nНажми Enter для завершения...")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
