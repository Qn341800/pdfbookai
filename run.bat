@echo off
echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt

echo 启动Flask应用...
python app.py

pause