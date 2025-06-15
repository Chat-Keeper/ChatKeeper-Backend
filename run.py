from app import create_app
import os

config_name = os.getenv('FLASK_ENV', 'development')

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    # 运行应用
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG'))