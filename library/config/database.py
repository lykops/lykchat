redis_config = {
    'default' : {
        'host' : '127.0.0.1',  # IP地址
        'port' : 6379,  # 端口
        'db' : 0,  # 数据库名
        'max_connections' : 100,  # 最大连接数
        'pwd' : '1qaz2wsx',  # 如果密码为空，None
        'type' : 'default',  # 读写模式
    },
    'socket_timeout' : None,
    'socket_connect_timeout' : None,
    'socket_keepalive' : 90,
}

mongo_config = {
    'default' : {
        'host' : 'localhost',  # IP地址
        'port' : 27017,  # 端口
        'db' : 'lykchat',  # 数据库名
        'user' : 'lykchat',  # 连接用户名
        'pwd' : '1qaz2wsx',  # 连接密码
        'type' : 'default',  # 读写模式
    },
    # 默认连接方式。
    'log' : {
        'host' : 'localhost',
        'port' : 27017,
        'db' : 'lykchat',
        'user' : 'lykchat',
        'pwd' : '1qaz2wsx',
        'type' : 'default',
    },
    'mechanism':"SCRAM-SHA-1"
}

