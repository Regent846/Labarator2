import pytest
import time
import re
from playwright.sync_api import Page, expect

# Базовый URL приложения
BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="function")
def goto_main_page(page: Page):
    """Фикстура для перехода на главную страницу"""
    page.goto(BASE_URL)
    # Ждем загрузки ключевых элементов
    expect(page.locator("h1")).to_have_text("Добро пожаловать!")
    return page


def test_open_main_page(goto_main_page):
    """Тест открытия главной страницы и проверки основных элементов."""
    page = goto_main_page

    expect(page).to_have_title("Главная страница")
    expect(page.locator("form")).to_be_visible()
    expect(page.locator("input#username")).to_be_visible()
    expect(page.locator("input[type='submit']")).to_have_value("Отправить")


def test_navigation_to_about_page(goto_main_page):
    """Тест перехода на страницу 'О нас' и обратно."""
    page = goto_main_page

    # Кликаем на ссылку "О нас"
    with page.expect_navigation():
        page.click("text=О нас")

    # Проверяем, что перешли на нужную страницу
    expect(page).to_have_url(f"{BASE_URL}/about")
    expect(page.locator("h1")).to_have_text('Это страница "О нас"')

    # Возвращаемся на главную
    with page.expect_navigation():
        page.click("text=На главную")

    expect(page).to_have_url(BASE_URL + "/")


def test_form_submission(goto_main_page):
    """Тест отправки формы с данными."""
    page = goto_main_page
    test_name = "Ivan"

    print("=== НАЧАЛО ТЕСТА ===")
    print(f"Текущий URL: {page.url}")

    # Заполняем поле ввода
    username_input = page.locator("input#username")
    username_input.click()
    username_input.fill("")
    username_input.fill(test_name)

    # Проверяем, что значение установилось
    expect(username_input).to_have_value(test_name)
    print(f"Значение в поле: {username_input.input_value()}")

    # Отправляем форму и ждем навигации
    print("Нажимаем кнопку отправки...")
    with page.expect_navigation():
        page.click("input[type='submit']")

    print(f"URL после отправки: {page.url}")

    # Проверяем результат
    expect(page).to_have_url(f"{BASE_URL}/result?name={test_name}")
    expect(page.locator("h1")).to_have_text(f"Привет, {test_name}!")
    print("Тест завершен успешно!")
    print("===================")


def test_form_submission_alternative(goto_main_page):
    """Альтернативный тест отправки формы."""
    page = goto_main_page
    test_name = "TestUser"

    # Заполняем форму
    page.fill("input#username", test_name)

    # Используем expect_navigation для явного ожидания
    with page.expect_navigation():
        page.locator("input[type='submit']").click()

    expect(page).to_have_url(f"{BASE_URL}/result?name={test_name}")
    expect(page.locator("h1")).to_contain_text("Привет")


def test_form_submission_cyrillic(goto_main_page):
    """Тест отправки формы с кириллицей."""
    page = goto_main_page
    test_name = "Иван"

    # Заполняем форму
    page.fill("input#username", test_name)

    # Отправляем форму
    with page.expect_navigation():
        page.click("input[type='submit']")

    # Для кириллицы проверяем только наличие ключевых элементов
    expect(page.locator("h1")).to_contain_text("Привет")

    # ИСПРАВЛЕНИЕ: используем регулярное выражение вместо лямбды
    expect(page).to_have_url(re.compile(r".*/result.*"))

    # Дополнительная проверка: видим ли мы имя на странице
    expect(page.locator("body")).to_contain_text(test_name)


def test_form_submission_press_enter(goto_main_page):
    """Тест отправки формы нажатием Enter."""
    page = goto_main_page
    test_name = "EnterUser"

    page.fill("input#username", test_name)

    # Отправляем форму нажатием Enter
    with page.expect_navigation():
        page.press("input#username", "Enter")

    expect(page.locator("h1")).to_contain_text(test_name)


def test_empty_form_submission(goto_main_page):
    """Негативный тест: отправка пустой формы."""
    page = goto_main_page

    # Очищаем поле (если оно не пустое)
    page.fill("input#username", "")

    # Отправляем пустую форму
    page.click("input[type='submit']")

    # Ждем немного и проверяем, что остались на главной
    page.wait_for_timeout(1000)
    expect(page).to_have_url(BASE_URL + "/")


def test_main_page_link_from_about(goto_main_page):
    """Тест ссылки с главной на 'О нас' и наличия обратной ссылки."""
    page = goto_main_page

    with page.expect_navigation():
        page.click("text=О нас")

    expect(page).to_have_url(f"{BASE_URL}/about")
    expect(page.locator("text=На главную")).to_be_visible()


# ДИАГНОСТИЧЕСКИЕ ТЕСТЫ
def test_diagnostic_simple_submission(page: Page):
    """Диагностический тест - максимально простой."""
    page.goto(BASE_URL)

    print("=== ДИАГНОСТИКА ===")
    print(f"Начальный URL: {page.url}")

    # Просто заполняем поле и отправляем
    page.fill("input#username", "Test")
    print("Заполнили поле")

    # Кликаем и ждем 5 секунд
    page.click("input[type='submit']")
    print("Нажали кнопку")

    # Ждем и смотрим что произошло
    page.wait_for_timeout(5000)
    print(f"Конечный URL: {page.url}")
    print(f"Заголовок страницы: {page.title()}")
    print(f"Текст h1: {page.locator('h1').text_content()}")
    print("===================")


def test_diagnostic_form_action(page: Page):
    """Проверяем атрибуты формы."""
    page.goto(BASE_URL)

    form = page.locator("form")
    print("=== ПРОВЕРКА ФОРМЫ ===")
    print(f"Action формы: {form.get_attribute('action')}")
    print(f"Method формы: {form.get_attribute('method')}")
    print("=====================")

    # ИСПРАВЛЕНИЕ: используем правильный регистр для проверки
    expect(form).to_have_attribute("action", "/submit")
    expect(form).to_have_attribute("method", "POST")  # Большими буквами!


def test_url_encoding_behavior(page: Page):
    """Тестируем как обрабатываются URL с кириллицей."""
    page.goto(BASE_URL)

    # Тест с кириллицей
    cyrillic_name = "Иван"
    page.fill("input#username", cyrillic_name)

    with page.expect_navigation():
        page.click("input[type='submit']")

    final_url = page.url
    print(f"=== ПОВЕДЕНИЕ URL ===")
    print(f"Введенное имя: {cyrillic_name}")
    print(f"Финальный URL: {final_url}")
    print(f"Декодированный параметр: {page.locator('h1').text_content()}")
    print("=====================")

    # Проверяем что мы на странице результата
    expect(page).to_have_url(re.compile(r".*\/result.*"))
    expect(page.locator("h1")).to_contain_text("Привет")