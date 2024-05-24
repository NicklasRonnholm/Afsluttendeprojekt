import qrcode
from flask import Flask, make_response
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import string
import secrets

app = Flask(__name__)

def change_guest_network_password(router_ip, router_password, new_password):
    chromedriver_path = 'chromedriver.exe'

    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service)

    driver.maximize_window()

    driver.get(f"http://{router_ip}/")

    password_field = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']")))

    password_field.send_keys(router_password)

    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/a")))
    login_button.click()
    time.sleep(2)

    wireless_section = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[3]/div/div[1]/ul/li[3]/a")
    wireless_section.click()
    time.sleep(3)

    new_password_field = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div[6]/div[2]/div/div[2]/div[1]/span[2]/input")
    driver.execute_script("arguments[0].scrollIntoView();", new_password_field)
    time.sleep(1)
    new_password_field.clear()  # Clear existing password
    new_password_field.send_keys(new_password)

    save_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/div[3]/div[2]/div[1]/a")))
    save_button.click()

    driver.quit()

def generate_qr_code(ssid, new_password):
    wifi_uri = f'WIFI:S:{ssid};T:WPA;P:{new_password};;'

    qr = qrcode.make(wifi_uri)

    qr_img = BytesIO()
    qr.save(qr_img, 'PNG')
    qr_img.seek(0)

    response = make_response(qr_img.getvalue())
    response.headers['Content-Type'] = 'image/png'

    return response

def generate_random_password(length=20):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3
                and any(c in string.punctuation for c in password)):
            break
    return password

@app.route('/')
def main():
    ssid = 'TP-Link_Guest_8328'
    new_password = generate_random_password()

    router_ip = "192.168.0.1"
    router_password = "Vedikke1"
    change_guest_network_password(router_ip, router_password, new_password)

    qr_code = generate_qr_code(ssid, new_password)

    return qr_code

if __name__ == '__main__':
    app.run(debug=True)
