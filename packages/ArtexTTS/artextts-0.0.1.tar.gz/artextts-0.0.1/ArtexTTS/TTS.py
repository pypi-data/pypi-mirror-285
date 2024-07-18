from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from mtranslate import translate
from pathlib import Path

class Speaker():

    def __init__(self, input_file_path, stop_file_path, translate=True, speak_continous=True):
        self.__input_file_path = input_file_path
        self.__speak_continous = speak_continous
        self.__stop_file_path = stop_file_path
        self.__translate = translate
        self.__fine = True
        if not self.__check_arguments():
              self.__fine = False
        self.__chrome_options = Options()
        self.__user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
        self.__chrome_options.add_argument(f'user-agent={self.__user_agent}')
        self.__chrome_options.add_argument("--use-fake-ui-for-media-stream")
        self.__chrome_options.add_argument("--use-fake-device-for-media-stream")
        self.__chrome_options.add_argument("--headless=new")
        self.__service = Service(ChromeDriverManager().install())
        self.__driver = webdriver.Chrome(service=self.__service, options=self.__chrome_options)

    def __check_arguments(self):
        if not isinstance(self.__speak_continous, bool):
            raise TypeError("Parameter speak_continous must be boolean")
            return False
        if not isinstance(self.__translate, bool):
            raise TypeError("Parameter translate must be boolean")
            return False
        if not isinstance(self.__input_file_path, str):
            raise TypeError("Parameter input_file_path must be string")
            return False
        if not isinstance(self.__stop_file_path, str):
            raise TypeError("Parameter stop_file_path must be string")
            return False
        if not self.__input_file_path:
            raise ValueError("Please provide the input_file_path")
            return False
        if self.__speak_continous and not self.__stop_file_path:
            raise ValueError("Please provide stop_file_paths")
            return False
        return True

    def __translate_to(self, text):
        return translate(text, "en-us")
    
    def __initiate_speak(self):
        with open(self.__stop_file_path, "w") as initiator_file:
            initiator_file.write("A")

    def quit_speak(self):
        with open(self.__stop_file_path, "w") as initiator_file:
            initiator_file.write("B")
        self.__driver.quit()

    def speak(self):
          if not self.__fine:
              return
          self.__initiate_speak()
          print(Path(__file__).resolve().parent / 'TTS.html')
          self.__driver.get(str(Path(__file__).resolve().parent / 'TTS.html'))
          previous_text = None
          if self.__speak_continous:
            while True:
                with open(self.__stop_file_path, "a+") as initiator_file:
                    initiator_file.seek(0)
                    to_speak = initiator_file.read()
                    initiator_file.close()
                if not to_speak == "A":
                    break
                with open(self.__input_file_path, "a+") as data_file:
                    data_file.seek(0)
                    data = data_file.read()
                    data_file.close()
                if previous_text != data:
                    previous_text = data
                    translated_text = self.__translate_to(data) if self.__translate else data
                    input_btn = self.__driver.find_element(By.ID, "text-to-speak")
                    start_btn = self.__driver.find_element(By.ID, "start-speech")
                    input_btn.clear()
                    input_btn.send_keys(translated_text)
                    start_btn.click()
                sleep(0.33)
          else:
              with open(self.__input_file_path, "a+") as data_file:
                    data_file.seek(0)
                    data = data_file.read()
                    data_file.close()
              translated_text = self.__translate_to(data) if self.__translate else data
              input_btn = self.__driver.find_element(By.ID, "text-to-speak")
              start_btn = self.__driver.find_element(By.ID, "start-speech")
              input_btn.clear()
              input_btn.send_keys(translated_text)
              start_btn.click()
              sleep(30)
              self.quit_speak()