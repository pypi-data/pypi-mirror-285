
from mtworker.__main__ import app
@app.command()
def setup(api: str,beat: str=None):
    """_summary_
        设置环境，安装相关的组件，及必要的初始化，确保能正常运行本程序。
    Args:
        api (str): _description_
        beat (str, optional): _description_. Defaults to None.
    """
    print("TODO:开始设置playwright")
