"""启动器_lyl"""
import os
import sys
import webbrowser
import threading
import time

os.environ.setdefault('DATABASE_PATH', 'data/knowledge_qa.db')
os.environ.setdefault('VECTOR_STORE_PATH', 'data/vector_store')
os.environ.setdefault('DOCUMENTS_PATH', 'data/documents')

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    os.chdir(os.path.dirname(sys.executable))
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)

def open_browser_lyl():
    time.sleep(2)
    webbrowser.open('http://localhost:8000')

if __name__ == '__main__':
    os.makedirs('data/documents', exist_ok=True)
    os.makedirs('data/vector_store', exist_ok=True)
    print("=" * 50)
    print("个性化知识问答系统")
    print("访问地址: http://localhost:8000")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    threading.Thread(target=open_browser_lyl, daemon=True).start()
    import uvicorn
    from backend.app.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)
