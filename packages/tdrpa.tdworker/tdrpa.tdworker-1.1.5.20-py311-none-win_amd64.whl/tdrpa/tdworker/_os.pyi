class App:
    @staticmethod
    def Kill(processName: str | int):
        """
        强制停止应用程序的运行（结束进程）

        App.Kill('chrome.exe')

        :param processName:[必选参数]应用程序进程名或进程PID
        :return:None
        """
