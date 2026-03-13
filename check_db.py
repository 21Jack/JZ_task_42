from todoapp import app, db
from todoapp.models import User, Task

with app.app_context():
    print('数据库连接成功')
    
    # 检查所有表（SQLAlchemy 2.0+ 方法）
    print('\n所有表名:', db.metadata.tables.keys())
    
    # 检查user表结构
    print('\n检查user表...')
    inspector = db.inspect(db.engine)
    try:
        users_columns = inspector.get_columns('user')
        print('user表列信息:')
        for column in users_columns:
            print(f'  {column["name"]}: {column["type"]}')
    except Exception as e:
        print(f'获取user表结构失败: {e}')
    
    # 检查是否有现有用户
    print('\n现有用户数量:', User.query.count())
    
    # 尝试创建一个测试用户（如果不存在）
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        print('\n创建测试用户...')
        try:
            test_user = User(username='testuser', email='test@example.com')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            print('测试用户创建成功')
        except Exception as e:
            print(f'测试用户创建失败: {e}')
            db.session.rollback()
    else:
        print('\n测试用户已存在')

print('\n数据库检查完成')