from selenium.webdriver.common.by import By

driver.get("https://www.example.com")  # noqa
links = driver.find_elements(By.TAG_NAME, "a")  # noqa
links[0].click()
driver.implicitly_wait(2)  # noqa
actions_output["current_url"] = driver.current_url  # noqa
