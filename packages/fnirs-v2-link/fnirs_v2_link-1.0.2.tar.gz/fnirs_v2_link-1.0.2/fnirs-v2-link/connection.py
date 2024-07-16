# -*- coding:utf8 -*-

from get_server_data import GetServerData
from socket_server import SocketServer
from web_request import WebRequest
from url_name import UrlName
from exception import CustomError
from response import Response
import threading
import time


class Connection:
    # ip port
    # IP = "192.168.8.1"
    IP = "192.180.0.132"
    SERVER_NAME = "brainScope"
    # 测试url
    BASEURL = "http://" + IP + ":8082/" + SERVER_NAME;
    WS_GET_PAGE_DATA_URL = "ws://" + IP + ":8080/" + SERVER_NAME + "/websocket/pageData";
    WS_GET_ORIGIN_DATA_URL = "ws://" + IP + ":8080/" + SERVER_NAME + "/websocket/sdkData";

    headers = {}
    server_data = GetServerData()
    thread = None

    def start(self):
        """
        开始测试
        :return:
        """
        url = self.BASEURL + UrlName.START
        print(url)
        para = {}
        try:
            WebRequest.get(url, para, self.headers)
            # 开启获取服务器数据线程
            # self.start_thread()
            # 开启推送数据websocket
            # server = SocketServer()
            # server.start()
            return Response.success()
        except CustomError as e:
            return_data = Response.fail(1001, e.error_info)
        return return_data

    def stop(self):
        """
        结束测试
        :return:
        """
        url = self.BASEURL + UrlName.STOP
        para = {"testStatus": 3}
        try:
            self.terminate()
            # server = SocketServer()
            # server.terminate()
            WebRequest.post(url, para, self.headers)
            # print('总读取计数...... , count = ',self.server_data.count)
            # print('总推送计数...... , send count = ',self.server_data.split_count)
            # print('总丢失服务器计数...... , lost count = ',self.server_data.lost_count)
            # print('总丢失推送计数...... , lost send count = ',self.server_data.lost_split_count)
            return Response.success()
        except CustomError as e:
            return_data = Response.fail(1001, e.error_info)
        return return_data

    def read_data(self):
        """
        获取服务器数据
        :return:
        """
        url = self.BASEURL + UrlName.READ_DATA
        para = {}

        try:
            data = WebRequest.get(url, para, self.headers)
            if data is not None:
                return Response.success_data(data['data'])
            else:
                return Response.success()
        except CustomError as e:
            return_data = Response.fail(1001, e.error_info)
        return return_data

    def mark(self, mark):
        """
        科研mark
        :return:
        """
        url = self.BASEURL + UrlName.MARK
        para = {"mark": mark}

        try:
            WebRequest.post(url, para, self.headers)
            return Response.success()
        except CustomError as e:
            return_data = Response.fail(1001, e.error_info)
        return return_data

    def get_server_data(self):
        # 获取当前数据
        temp_data = self.read_data();
        if temp_data is None:
            return
        # 判断是否是字典类型
        if isinstance(temp_data, dict):
            if temp_data.__contains__('data') and temp_data['data'] is not None:
                self.server_data.count = self.server_data.count + 1
                if not self.server_data.data.full():
                    self.server_data.data.put_nowait(temp_data['data'])
                else:
                    self.server_data.lost_count = self.server_data.lost_count + 1
                    print('读取服务器队列满了......,lost count = ', self.server_data.lost_count)
                    # print("1:data:", self.server_data.data.qsize())

    def start_thread(self):
        self.thread = GetDataThread()
        self.thread.start()

    def terminate(self):
        if self.thread is not None:
            self.thread.stop()


class GetDataThread(threading.Thread):
    exit_flag = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'Thread-Get-Data'
        self.exit_flag = True

    def run(self):
        while self.exit_flag:
            Connection().get_server_data()
            time.sleep(0.3)

    def stop(self):
        self.exit_flag = False
