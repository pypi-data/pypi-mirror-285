# coding:utf-8
import time
import threading
from uuid import uuid1
import eventlet

mylist = []


def one(name):
    print(name, 'begin')
    mylist.append(name)
    time.sleep(10)
    return name


def main():
    mylist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for num in mylist:
        mylist.remove(num)
        print('removed', num)
    print(len(mylist))
    print(mylist)


class ThreadPool():
    """ 维护一个线程池 """
    
    def __init__(self, size, save_result=False, while_wait_time=0.5, report=False):
        self.size = size
        self.thread_pool = []
        self.pool_status = [0]
        self.result_map = {}
        self.save_result = save_result
        self.while_wait_time = while_wait_time
        self.report = report
        
    def clear(self):
        self.pool_status = [0]
        self.result_map = {}

    def run(self, func, args, kwargs={}, time_out=None):
        """ 主线程命令当前线程池从空闲线程中取一个线程执行给入的方法，如果池满，则主线程等待 """
        if self.pool_status[0] < self.size:
            thread_id = uuid1()
            t = myThread(func, args=args, kwargs=kwargs, thread_id=thread_id, pool_status=self.pool_status, result_map=self.result_map, save_result=self.save_result, time_out=time_out)
            t.start()
            self.thread_pool.append(t)
            return thread_id
        else:
            while self.pool_status[0] >= self.size:
                time.sleep(self.while_wait_time)
            return self.run(func, args, kwargs, time_out)

    def get_results(self):
        return self.result_map
    
    def get_result(self, num):
        return self.result_map[num]
    
    def clear_result(self):
        self.result_map = {}

    def wait(self):
        """ 主线程等待，直到线程池不存在活动线程 """
        while self.pool_status[0] > 0:
            time.sleep(self.while_wait_time)
    
    def get_running_num(self):
        return self.pool_status[0]


class myThread (threading.Thread):

    def __init__(self, func, args, kwargs, thread_id, pool_status, result_map, save_result, time_out):
        threading.Thread.__init__(self)
        threading.Thread.daemon = True
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.thread_id = thread_id
        self.pool_status = pool_status
        self.result_map = result_map
        self.save_result = save_result
        self.time_out = time_out

    def run(self):
        self.pool_status[0] = self.pool_status[0] + 1
        try:
            if self.time_out is None:
                result = self.func(*self.args, **self.kwargs)
                if self.save_result:
                    self.result_map[self.thread_id] = result
            else:
                # 实测效率很低
                eventlet.monkey_patch()
                with eventlet.Timeout(self.time_out, False):
                    result = self.func(*self.args, **self.kwargs)
                    if self.save_result:
                        self.result_map[self.thread_id] = result
        finally:
            self.pool_status[0] = self.pool_status[0] - 1


if __name__ == '__main__':
    main()
