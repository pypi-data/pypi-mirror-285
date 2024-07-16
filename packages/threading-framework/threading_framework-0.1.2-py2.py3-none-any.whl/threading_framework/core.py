# Insert your code here. 
import abc
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor


class ThreadingAssistantBasicClass(metaclass=abc.ABCMeta):

    lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        pass

    def __del__(self):
        pass

    @classmethod
    def threading_framework(cls, max_thread_num, assistant_init_args, task_args_list, shared_variable):
        """
        作用：多线程竞争
        说明：通过 kwargs 的方式传入 assistant_init_args, task_args_list, shared_variable
        assistant_init_args 将会被解包用于 assistant 初始化
        task_args_list 和 shared_variable 将会被解包用于 threading_run
        参数：
        - max_thread_num: 最大线程数量
        - assistant_init_args: 初始化参数
        - task_args_list: 任务参数列表
        - shared_variable: 共享变量
        """
        def get_idle_assistant(idle_assistant):
            """
            获取空闲assistant的函数
            """
            while True:
                try:
                    assistant = idle_assistant.get(timeout=0)  # 立即尝试从队列中获取可用assistant
                    return assistant
                except queue.Empty:
                    time.sleep(0.1)  # 如果没有可用的assistant，稍等片刻再次尝试

        # 创建 assistant 对象列表
        assistant_list = []
        for _ in range(max_thread_num):
            try:
                assistant = cls(**assistant_init_args)
                assistant_list.append(assistant)
            except Exception as e:
                print(e)
        # 初始化空闲assistant队列
        idle_assistant = queue.Queue()
        for driver_pair in assistant_list:
            idle_assistant.put(driver_pair)
        # 创建信号量以限制并发任务数量
        semaphore = threading.Semaphore(max_thread_num)

        # 定义任务包装器函数
        def wrapped_task(task_args, shared_variable):
            with semaphore:  # 获取信号量
                assistant = get_idle_assistant(idle_assistant)  # 获取空闲assistant
                try:
                    assistant.threading_task(**task_args, **shared_variable)
                except Exception as e:
                    raise e
                idle_assistant.put(assistant)  # 将assistant放回空闲队列

        # 使用 ThreadPoolExecutor 运行任务
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(wrapped_task, task_args, shared_variable) for task_args in task_args_list]

        # 关闭 assistant 对象
        for assistant in assistant_list:
            del assistant

    @abc.abstractmethod
    def threading_task(self, *args, **kwargs):
        """
        通过解包 task_args 进入正常的流程，并加锁读写数据
        """
        pass

    @classmethod
    @abc.abstractmethod
    def threading_run(cls, *args, **kwargs):
        """
        通过转换参数调用 threading_framework
        """
        pass