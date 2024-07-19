from _typeshed import Incomplete

class Web:
    @staticmethod
    def OpenChrome(url: str = None, chromeExePath: str = None, isMaximize: bool = True, supportUia: bool = True, otherStartupParam: Incomplete | None = None):
        '''
        启动谷歌浏览器

        Web.OpenChrome(url="www.baidu.com", chromeExePath=None, isMaximize=True, supportUia=True, otherStartupParam=None)

        :param url:[可选参数]启动浏览器后打开的链接，字符串类型。默认None
        :param chromeExePath:[可选参数]谷歌浏览器可执行程序的绝对路径，字符串类型，填写None时会自动寻找本地安装的路径。默认None
        :param isMaximize:[可选参数]浏览器启动后是否最大化显示，选择True时最大化启动，选择False默认状态。默认True
        :param supportUia:[可选参数]是否支持uiautomatin，True支持，False不支持。默认True
        :param otherStartupParam:[可选参数]其他启动谷歌浏览器的参数，如：[\'--xxx\', \'--xxx\']。默认None
        :return:None
        '''
    @staticmethod
    def ChromeProcessStatus():
        """
        检查启动的Chrome浏览器进程是否正在运行

        chromeStatus = Web.ChromeProcessStatus()

        :return:返回True时，表示浏览器仍在运行，返回False时，表示浏览器非运行状态
        """
