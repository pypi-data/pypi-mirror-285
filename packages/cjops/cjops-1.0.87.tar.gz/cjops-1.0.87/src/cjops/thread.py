import threading
import queue
import concurrent.futures
from functools import partial

def run_single_thread(target, *args, join_thread=True, **kwargs):
    """
    启动一个线程,支持是否等待其执行结果

    :param target: 目标函数
    :param args: 目标函数的位置参数
    :param join_thread: 是否等待线程完成,再执行主线程的程序
    :param kwargs: 目标函数的关键字参数
    :return: 目标函数的执行结果（如果等待线程完成），否则返回 None
    """
    result_queue = queue.Queue()

    def wrapper(*args, **kwargs):
        result = target(*args, **kwargs)
        result_queue.put(result)

    t = threading.Thread(target=wrapper, args=args, kwargs=kwargs)
    t.start()

    if join_thread:
        t.join()  # 等待线程完成
        return result_queue.get()
    else:
        return None

def run_thread_pool(func, items, workers=5, **kwargs):
    """
    使用线程池执行指定的函数，支持传递参数和设置线程数。

    Args:
        func (callable): 要执行的函数。
        items (iterable): 函数的输入数据。
        workers (int): 线程数，默认为 5。
        **kwargs: 传递给函数的关键字参数。

    Returns:
        list: 所有线程执行的结果的列表。
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # 使用 partial 函数将固定参数传递给 func
        worker = partial(func, **kwargs)
        # 获取每个线程执行的结果，统一处理
        futures = [executor.submit(worker, item) for item in items]
        for future in concurrent.futures.as_completed(futures):
            try:
                future_result = future.result()
                if future_result:
                    # 判断数据类型，如果是List则extend
                    if isinstance(future_result, list):
                        results.extend(future_result)
                    else:
                        results.append(future_result)
            except Exception as e:
                print(f"An error occurred: {e}")
    return results


if __name__ == '__main__':
    # run_single_thread 单线程执行案例
    def _test_send_message(ws, title):
        result = []
        for i in range(0, 10):
            print(f"Message {i} to {ws} in {title}")
            result.append(f"Message {i} to {ws}")
        return result

    ws = "参数"
    # 需要等待子线程完成
    result = run_single_thread(_test_send_message, ws, '线程1')
    print("主线程")
    if result:
        print("线程执行结果:", result)

    # 不等待子线程完成,无法获取线程执行的结果
    run_single_thread(_test_send_message, ws, '线程2', join_thread=False)
    print("主线程，不等待子线程,让子线程在后台执行代码")
# ================================================================================
    # run_thread_pool 线程池执行案例
    def shuangshu(item, **kwargs):
        key = kwargs.get("key", "")
        return str(int(item) * 2) + f'==={key}'

    items = [n for n in range(10)]

    res = run_thread_pool(shuangshu, items, key="123")
    print(res)