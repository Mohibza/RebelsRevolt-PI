import sys
import os
import threading
import webbrowser
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

app = create_app()

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()
    print("=" * 50)
    print("  EyeConExcel Web App")
    print("  Running at: http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
