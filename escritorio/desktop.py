import threading
import webview
from app import app  # tu archivo flask

def run_flask():
    app.run(port=5000)

if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    webview.create_window("Grand Build App", "http://127.0.0.1:5000")
    webview.start()