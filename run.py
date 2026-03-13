#!/usr/bin/env python3
"""
TodoList 应用入口
"""
import os
from todoapp import create_app

# 创建应用实例
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # 开发服务器配置
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', True)
    )
