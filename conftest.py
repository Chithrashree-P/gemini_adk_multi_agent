# import pytest
# from playwright.sync_api import sync_playwright


# @pytest.fixture(scope="session")
# def browser():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         yield browser
#         browser.close()


# @pytest.fixture
# def page(browser):
#     context = browser.new_context()
#     page = context.new_page()
#     yield page
#     context.close()
# import pytest
# from playwright.sync_api import sync_playwright

# import os
# os.makedirs("output/screenshots", exist_ok=True)

# # -------------------------------
# # Browser Fixture
# # -------------------------------
# @pytest.fixture(scope="session")
# def browser():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # set True for CI
#         yield browser
#         browser.close()


# # -------------------------------
# # Context Fixture
# # -------------------------------
# @pytest.fixture
# def context(browser):
#     context = browser.new_context()
#     yield context
#     context.close()


# # -------------------------------
# # Page Fixture
# # -------------------------------
# @pytest.fixture
# def page(context):
#     page = context.new_page()
#     yield page


# # -------------------------------
# #  Screenshot on Failure
# # -------------------------------
# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     outcome = yield
#     report = outcome.get_result()

#     if report.when == "call" and report.failed:
#         page = item.funcargs.get("page")
#         if page:
#             page.screenshot(path=f"output/screenshots/{item.name}.png")

import pytest
from playwright.sync_api import sync_playwright
import os
import time

os.makedirs("output/screenshots", exist_ok=True)

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        yield browser
        browser.close()

@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    page.set_default_timeout(20000)
    yield page

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            page.screenshot(
                path=f"output/screenshots/{item.name}_{int(time.time())}.png"
            )