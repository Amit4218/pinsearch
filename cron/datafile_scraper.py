from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from pathlib import Path
from logging import Logger
import time
import requests
import ddddocr
import os
import json


class DataFileScraper:
    def __init__(self, logger:Logger):
        self.options = webdriver.ChromeOptions()
        self._add_webdriver_arguments()
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(driver=self.driver, timeout=10)
        self._base_url = "https://www.data.gov.in/resource/all-india-pincode-directory-till-last-month"
        self._file_download_dir = Path("temp")
        self._req_session = requests.Session()
        self.logger = logger

    def _add_webdriver_arguments(self):
        """An helper to add arguments to the webdriver options."""
        
        self.options.set_capability("goog:loggingPrefs",{"performance": "ALL"})
        self.options.add_argument("--headless=new")
        self.driver.execute_cdp_cmd("Network.enable", {})
        
    def _response_listiner(self) -> str | None:
        """listens to the response request after the form submission"""
        
        logs = self.driver.get_log("performance")

        for log in logs:
            msg = json.loads(log["message"])["message"]

            if msg["method"] == "Network.responseReceived":
                url = msg["params"]["response"]["url"]

                if "download_purpose?_format=json" in url:
                    request_id = msg["params"]["requestId"]

                    body = self.driver.execute_cdp_cmd(
                        "Network.getResponseBody",
                        {"requestId": request_id}
                    )

                    response_body = body["body"]
                    
                    return str(response_body["download_url"]).replace("\\","")
                
        return None


    def _captcha_image_downloader(self, src:str) -> str:
        
        self.logger.info("[CSV FILE DOWNLOAD] Captca image download started...")
        
        self.request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        if not os.path.exists(self._file_download_dir):
            os.makedirs(self._file_download_dir)
            
        file_path = f"{self._file_download_dir}/captcha.png"
        
        res = self._req_session.get(src, headers=self.request_headers)
        
        if not res.status_code == 200:
            raise requests.RequestException
        
        self.logger.info("[CSV FILE DOWNLOAD] Download successfull...")
        with open(file_path, mode="wb") as f:
            f.write(res.content)
        
        return file_path


    def _ocr_captcha_image(self, image_path:str) -> str:
        ocr = ddddocr.DdddOcr()
        self.logger.info("[CSV FILE DOWNLOAD] Captcha ocr started...")
        with open(image_path, "rb") as f:
            img = f.read()

        result = ocr.classification(img)
        
        if not result:
            raise Exception("Error solving image captcha")

        self.logger.info("[CSV FILE DOWNLOAD] Captcha solved successfully...")
        os.remove(image_path)
        return str(result).upper()

        
    
    def _pincode_csv_downloader(self, download_url:str) -> None:
        self.logger.info("[CSV FILE DOWNLOAD] Downloadind csv file started...")
        file_name = "datafile.csv"
        file_contents = self._req_session.get(url=download_url, headers=self.request_headers)

        with open(file_name, "wb") as f:
            f.write(file_contents.content)
        
        self.logger.info("[CSV FILE DOWNLOAD] Download complete...")
    
    def start(self):
        try:
            
            self.logger.info("[CSV FILE DOWNLOAD] Pincode csv file download task started...")
            
            self.driver.get(self._base_url)
            
            self.logger.info("[CSV FILE DOWNLOAD] Waiting document load...")
            time.sleep(5) # waiting for the element to be present at the dom
            download_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Download File']")))
            download_btn.click()
            self.logger.info("[CSV FILE DOWNLOAD] Download btn clicked")
            
            
            download_form = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modal-body")))
            
            if download_form:
                self.logger.info("[CSV FILE DOWNLOAD] Form filling started...")
                # selecting the no-comercial radio input
                use_case_radio = self.driver.find_element(By.CSS_SELECTOR, "input[value='2']")
                radio_id = use_case_radio.get_attribute("id")
                use_case_label = self.driver.find_element(By.CSS_SELECTOR,f"label[for='{radio_id}']")
                use_case_label.click()
                
                # selecting the academic radio input
                academic_radio = self.driver.find_element(By.CSS_SELECTOR, "input[value='3']")
                radio_id = academic_radio.get_attribute("id")
                academic_label = self.driver.find_element(By.CSS_SELECTOR,f"label[for='{radio_id}']")
                academic_label.click()
            
                time.sleep(2) # waiting for the captcha image to load
                captcha_image_link = download_form.find_element(By.CLASS_NAME, "img-fluid")
                src = captcha_image_link.get_attribute("src")
                
                if src:
                    
                    # download captcha image
                    image_path =  self._captcha_image_downloader(src=src)
                
                    # extract the captcha text
                    captch_text = self._ocr_captcha_image(image_path=image_path)
            
                    # input the captcha
                    captcha_input = download_form.find_element(By.CSS_SELECTOR, "input[id='input-3']")
                    captcha_input.send_keys(captch_text)
                    
                    # click the download btn
                    download_btn =  download_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    download_btn.click()
                    
                    time.sleep(3) # wait for the request to happen

                    # listening to the req and fetching the download url from the response data
                    download_url = self._response_listiner()
                    self.driver.quit() # exit the browser
                    
                    # download the csv file
                    if download_url:
                        csv_file_path = self._pincode_csv_downloader(download_url=download_url)
                        self.logger.info("[CSV FILE DOWNLOAD] Csv file downloaded successfully %s", csv_file_path)
                        return csv_file_path

        
        except Exception as e:
            raise Exception("[CSV FILE DOWNLOAD] Error downloading the csv file",e)
        finally:
            self.driver.quit()

