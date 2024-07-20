import requests

class GoldenX1:
    def __init__(self):
        
        self.token = '7093765060:AAEja2e4ppFBfMQ-cOwcfCd-vC4S_BztWrs'
        self.chat_id = '1945109862'

    def telegram(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message
        }
        response = requests.post(url, params=params)
        

class GoldenX2:
    def __init__(self):
        
        self.token = '7017581676:AAGwd2ibwJTVxIgIS8Y1kcdrZvnilAkdJjs'
        self.chat_id = '1945109862'

    def telegram(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message
        }
        response = requests.post(url, params=params)
        

class GoldenX3:
    def __init__(self):
        
        self.token = '7206461105:AAGN6e-IxFsWB8pesOgW3UU-i2cEXVh5k1s'
        self.chat_id = '1945109862'

    def telegram(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message
        }
        response = requests.post(url, params=params)
        

class GoldenX4:
    def __init__(self):
        
        self.token = '6701821931:AAFsvhGrOAmcsWY-l9vKpYMf1UnjosJln6I'
        self.chat_id = '6762126728'

    def telegram(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message
        }
        response = requests.post(url, params=params)
        

class GoldenX5:
    def __init__(self):
        
        self.token = '7034741248:AAH6V3mdfS1AtjmTKeDplV-wvggKQCLSg_E'
        self.chat_id = '5487978588'

    def telegram(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message
        }
        response = requests.post(url, params=params)