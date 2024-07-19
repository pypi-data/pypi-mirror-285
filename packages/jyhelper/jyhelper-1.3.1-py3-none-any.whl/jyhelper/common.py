from jyhelper import timeHelper
import hashlib
from urllib.parse import quote, unquote
import concurrent.futures
import base64


class common:

    # 打印日志
    @staticmethod
    def debug(*args, path=None):
        path = './debug.log' if path is None else path
        with open(path, 'a', encoding='utf-8') as f:
            f.write("\n---------------" + timeHelper.getDate() + "---------------\n")
            for arg in args:
                f.write(str(arg) + "\n")

    # 带时间输出
    @staticmethod
    def print(*args):
        print(timeHelper.getDate(), '--->', *args)

    # 将列表分割 每一份n的长度
    @staticmethod
    def explodeList(data, n):
        if isinstance(data, list):
            return [data[i:i + n] for i in range(0, len(data), n)]
        else:
            return []

    # 把英文的引号转换程中文的引号
    @staticmethod
    def replaceYinHao(strings):
        return strings.replace('"', '“').replace("'", "‘")

    # 把值转为int
    @staticmethod
    def transInt(val, default=0):
        try:
            val = int(val)
        except ValueError:
            val = default
        return val

    @staticmethod
    def transFloat(val, default=0):
        try:
            val = float(val)
        except ValueError:
            val = default
        return val

    # 转化为保留两位小数的格式
    @staticmethod
    def switch2(data1, data2=None, returnDefault=0.00, precision=2):
        if data1 == 0 or data2 == 0:
            return returnDefault
        if data2 is not None:
            data = data1 / data2
        else:
            data = data1
        return round(data, precision)

    # 转换为百分比
    @staticmethod
    def switchRate(data1, data2=None, returnDefault='0.00%', precision=2):
        if data1 == 0 or data2 == 0:
            return returnDefault
        if data2 is not None:
            data = data1 / data2 * 100
        else:
            data = data1 * 100
        return ('{:.%sf}' % precision).format(data) + '%'

    # 从list中删除数据
    @staticmethod
    def delListValue(needList, delValues):
        if not isinstance(delValues, list):
            delValues = [delValues]
        for delValue in delValues:
            needList = [x for x in needList if x != delValue]
        return needList

    # 排序字典的key
    @staticmethod
    def sortDictByKey(myDict, reverse=False):
        return dict(sorted(myDict.items(), key=lambda x: x[0], reverse=reverse))

    # 排序字典的value
    @staticmethod
    def sortDictByValue(myDict, reverse=False):
        return dict(sorted(myDict.items(), key=lambda x: x[1], reverse=reverse))

    """
    根据条件，删除字典中的数据
    myDict = {'key1': 1, 'key2': 2, 'key3': 3}
    common.delDictItem(myDict, "key == 'key1'")
    common.delDictItem(myDict, "value == 1")
    common.delDictItem(myDict, "value > 1")
    """

    @staticmethod
    def delDictItem(myDict=None, delWhere=None):
        if not isinstance(myDict, dict):
            return {}
        if delWhere is None:
            return myDict
        # 使用字典推导式创建新字典，排除要删除的键
        myDict = {key: value for key, value in myDict.items() if not eval(delWhere)}
        return myDict

    @staticmethod
    def getMD5(string):
        string = string if isinstance(string, str) else str(string)
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        return md5.hexdigest()

    @staticmethod
    def urlEncode(string):
        string = string if isinstance(string, str) else str(string)
        return quote(string, 'utf-8')

    @staticmethod
    def urlDecode(string):
        string = string if isinstance(string, str) else str(string)
        return unquote(string, 'utf-8')

    # 多线程运行任务
    """
    tasks = [[funcName, p1,p2],[funcName, p1,p2],[funcName, p1,p2],[funcName, p1,p2]]
    返回的exception里面是None就表示正常
    返回的result里面有None，大概率就是出现异常了 None not in result 表示全部正常
    """

    @staticmethod
    def multipleThreadRunTasks(max_workers, tasks, get_result=False, get_exceptions=False, print_info=True):
        # 创建一个拥有 max_workers 个线程的线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for oneTask in tasks:
                #  executor.submit(funcName, p1, p2,..)
                future = executor.submit(*oneTask)
                futures.append(future)
            # 监控线程池中剩余的任务数量
            all_futures = futures.__len__()
            while True:
                timeHelper.sleep(1)
                unfinished_count = sum(not future.done() for future in futures)
                if print_info:
                    common.print(f"完成进度: {all_futures - unfinished_count}/{all_futures}")
                if unfinished_count == 0:
                    break
            results = []
            exceptions = []
            if get_result:
                for future in futures:
                    if future.exception() is None:
                        results.append(future.result())
                    else:
                        results.append(None)
            if get_exceptions:
                for future in futures:
                    exceptions.append(future.exception())
            if get_result and not get_exceptions:
                return results
            if not get_result and get_exceptions:
                return exceptions
            if get_result and get_exceptions:
                return results, exceptions
            return None

    # 多进程运行任务
    @staticmethod
    def multipleProcessRunTasks(max_workers, tasks, get_result=False, get_exceptions=False, print_info=True):
        # 创建一个拥有 max_workers 个线程的线程池
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for oneTask in tasks:
                #  executor.submit(funcName, p1, p2,..)
                future = executor.submit(*oneTask)
                futures.append(future)
            # 监控线程池中剩余的任务数量
            all_futures = futures.__len__()
            while True:
                timeHelper.sleep(1)
                unfinished_count = sum(not future.done() for future in futures)
                if print_info:
                    common.print(f"完成进度: {all_futures - unfinished_count}/{all_futures}")
                if unfinished_count == 0:
                    break
            results = []
            exceptions = []
            if get_result:
                for future in futures:
                    if future.exception() is None:
                        results.append(future.result())
                    else:
                        results.append(None)
            if get_exceptions:
                for future in futures:
                    exceptions.append(future.exception())
            if get_result and not get_exceptions:
                return results
            if not get_result and get_exceptions:
                return exceptions
            if get_result and get_exceptions:
                return results, exceptions
            return None

    # base64编码
    @staticmethod
    def base64Encode(string):
        string = str(string) if not isinstance(string, str) else string
        return base64.b64encode(string.encode('utf-8')).decode('utf-8')

    # Base64 编码在最后可能需要添加填充字符 '=' 以使编码后的字符串长度是 4 的倍数。如果输入的字符串没有正确的填充，就会导致解码错误。
    @staticmethod
    def base64Decode(string):
        string = str(string)
        stringLen = string.__len__()
        yuShu = stringLen % 4
        addString = ''
        if yuShu > 0:
            addString = (4 - yuShu) * '='
        return base64.b64decode(string + addString).decode('utf-8')


if __name__ == '__main__':

    print(common.base64Decode(''))

    """
    def test(p1):
        return p1

    tasks = []
    for i in range(100):
        tasks.append([common.urlEncode, i])
    common.print('start')
    result = common.multipleThreadRunTasks(50,tasks=tasks,get_result=True)
    print(result)
    common.print('end')
    exit()
    """

    # test = ['a','b','a','c','d',None]
    # print(common.delListValue(test,['f',None,'a']))
    # print(test)
    # print(common.delDictItem({'c_actual收入': 900.0, 'a日期': '2023-11-09', 'b新增': 62, 'd留存1': 62, 'e收入1': 0, 'f付费人数1': 0, 'd留存2': 0, 'e收入2': 0, 'f付费人数2': 0, 'd留存3': 0, 'e收入3': 0, 'f付费人数3': 0},"key=='c_actual收入' and value==900"))
    # print(common.switchRate(0,0,precision=4,returnDefault='0.0000%'))
    # print(common.urlDecode('%E4%BD%A0%E5%A5%BD'))
