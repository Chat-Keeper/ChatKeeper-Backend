# 聊效管家-后端

v1.0已发布

# 聊效管家后端服务用户部署指南

## 技术栈概要
- **框架**: Flask (Python 3.11)
- **数据库**: MongoDB
- **API规范**: RESTful
- **依赖管理**: requirements.txt

---

## 本地开发环境快速部署

### 1. 获取项目代码
```bash
# 克隆项目到本地
git clone https://github.com/Chat-Keeper/ChatKeeper-Backend.git
cd ChatKeeper-Backend  # 进入项目目录
```
### 2. python环境配置
#### 重要提示：项目推荐版本为Python 3.11，使用其他版本的Python可能导致不可预料的错误
```bash
# 创建并激活虚拟环境（推荐）
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows

# 安装依赖库（注意：必须使用Python 3.11）
pip install -r requirements.txt
```
### 3. 数据库配置
```bash

# 安装MongoDB Community Edition（若未安装）
# 下载地址：https://www.mongodb.com/try/download/community

# 启动MongoDB服务（后台运行）
mongod --dbpath /data/db --fork --logpath /var/log/mongodb.log
```
MongoDB Compass 连接配置：

    打开 MongoDB Compass 应用程序

    点击顶部 "New Connection" 按钮

    在连接字符串输入框填写：
    text

    mongodb://localhost:27017

    点击右下角 "CONNECT" 按钮建立本地连接

    连接成功后左侧将显示默认数据库

### 4. 环境变量配置
```bash
# .env放置位置为/app目录下
# 复制环境模板文件
cp .env.template .env

# 编辑配置文件（按实际参数修改）
nano .env  # 或使用其他文本编辑器
```
配置文件内容示例：

```env

# ====== 数据库配置 ======
MONGODB_URI=mongodb://localhost:27017/chat_analyzer

# ====== DeepSeek API ======
DEEPSEEK_API_KEY=your_api_key_here  # 前往 https://platform.deepseek.com/ 获取

# ====== 服务端口 ======
FLASK_PORT=5000
```
### 5. 启动后端服务
```bash

# 运行主程序（开发模式）
python run.py

# 成功启动将显示：
#  * Running on http://127.0.0.1:5000
```


## 目录结构：
```
ChatKeeper-Backend
├─ app
│  ├─ models
│  │  ├─ group.py
│  │  ├─ mongo.py
│  │  ├─ speaker.py
│  │  ├─ token.py
│  │  └─ user.py
│  ├─ routes
│  │  ├─ analysis.py
│  │  ├─ auth.py
│  │  └─ data.py
│  ├─ services
│  │  ├─ auth_service.py
│  │  ├─ chat_parser.py
│  │  ├─ data_service.py
│  │  └─ deppseek_service.py
│  ├─ utils
│  │  ├─ auth.py
│  │  └─ utils.py
│  └─ __init__.py
├─ README.md
├─ requirements.txt
└─ run.py

```

## Compass连接失败解决方案

    确认MongoDB服务正在运行

    检查防火墙是否开放27017端口

    尝试使用连接字符串：mongodb://127.0.0.1:27017

    重启MongoDB服务：sudo systemctl restart mongod