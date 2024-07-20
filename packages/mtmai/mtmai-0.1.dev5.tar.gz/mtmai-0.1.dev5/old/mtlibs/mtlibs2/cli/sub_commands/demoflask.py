

from flask import Flask



def on_command(args):
    # 实例化，可视为固定格式
    app = Flask(__name__)
    # route()方法用于设定路由；类似spring路由配置
    @app.route('/helloworld')
    def hello_world():
        return 'Hello, World!'

    app.run(host="0.0.0.0", port=5000)

