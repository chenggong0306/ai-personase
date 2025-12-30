"""
打包exe脚本_lyl
将前后端打包成单个exe文件
"""
import os
import shutil
import subprocess
import sys
import glob


def find_anaconda_dlls_lyl():
    """查找 Anaconda 中缺失的 DLL 文件_lyl"""
    # Anaconda 安装路径
    anaconda_paths = [
        r'C:\ProgramData\anaconda3',
        r'C:\Users\{}\anaconda3'.format(os.getenv('USERNAME')),
        r'C:\Users\{}\miniconda3'.format(os.getenv('USERNAME')),
    ]

    dlls_needed = [
        'sqlite3.dll',
        'LIBBZ2.dll',
        'libmpdec-4.dll',
        'ffi.dll',
        'libcrypto-3-x64.dll',
        'libssl-3-x64.dll',
    ]

    found_dlls = []

    for anaconda_path in anaconda_paths:
        if not os.path.exists(anaconda_path):
            continue

        # 搜索目录
        search_dirs = [
            os.path.join(anaconda_path, 'Library', 'bin'),
            os.path.join(anaconda_path, 'DLLs'),
            anaconda_path,
        ]

        for dll_name in dlls_needed:
            for search_dir in search_dirs:
                dll_path = os.path.join(search_dir, dll_name)
                if os.path.exists(dll_path):
                    found_dlls.append(dll_path)
                    print(f"  找到: {dll_path}")
                    break

    return found_dlls


def build_exe_lyl():
    """打包exe主函数_lyl"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, 'frontend')
    backend_dir = os.path.join(project_root, 'backend')
    static_dir = os.path.join(backend_dir, 'static')

    print("=" * 50)
    print("开始打包 exe 文件")
    print("=" * 50)

    # 1. 构建前端
    print("\n[1/4] 构建前端...")
    os.chdir(frontend_dir)
    result = subprocess.run(['npm', 'run', 'build'], shell=True)
    if result.returncode != 0:
        print("前端构建失败！")
        return False

    # 2. 复制前端构建产物到后端 static 目录
    print("\n[2/4] 复制前端文件到后端...")
    dist_dir = os.path.join(frontend_dir, 'dist')
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
    shutil.copytree(dist_dir, static_dir)
    print(f"已复制到: {static_dir}")

    # 3. 安装 PyInstaller
    print("\n[3/4] 检查 PyInstaller...")
    os.chdir(project_root)
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], shell=True)

    # 4. 打包
    print("\n[4/4] 打包 exe...")

    # 创建启动脚本
    launcher_path = os.path.join(project_root, 'launcher_lyl.py')
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write('''"""启动器_lyl"""
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
''')

    # PyInstaller 命令
    pyinstaller_cmd = [
        'pyinstaller',
        '--name=知识问答系统',
        '--onefile',
        '--console',
        '--add-data', f'{static_dir};backend/static',
        '--add-data', f'{backend_dir}/app;backend/app',
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.websockets',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',
        '--hidden-import=aiosqlite',
        '--hidden-import=sqlite3',
        '--hidden-import=_sqlite3',
        '--hidden-import=tiktoken',
        '--hidden-import=tiktoken_ext',
        '--hidden-import=tiktoken_ext.openai_public',
        '--hidden-import=markdown',
        '--collect-data=tiktoken_ext.openai_public',
        '--collect-data=unstructured',
        '--collect-data=nltk',
        '--hidden-import=nltk',
        '--collect-binaries=sqlite3',
        '--exclude-module=PIL',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=numpy.distutils',
        launcher_path
    ]

    # 添加 Anaconda 缺失的 DLL
    print("\n查找 Anaconda DLL 文件...")
    found_dlls = find_anaconda_dlls_lyl()
    for dll_path in found_dlls:
        pyinstaller_cmd.insert(-1, '--add-binary')
        pyinstaller_cmd.insert(-1, f'{dll_path};.')

    # 添加 ctypes 相关隐藏导入
    pyinstaller_cmd.insert(-1, '--hidden-import=ctypes')
    pyinstaller_cmd.insert(-1, '--hidden-import=_ctypes')
    pyinstaller_cmd.insert(-1, '--collect-binaries=ctypes')

    subprocess.run(pyinstaller_cmd, shell=True)

    print("\n" + "=" * 50)
    print("打包完成！")
    print(f"exe文件位置: {os.path.join(project_root, 'dist', '知识问答系统.exe')}")
    print("=" * 50)


if __name__ == '__main__':
    build_exe_lyl()

