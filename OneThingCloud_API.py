import json
import requests
import random
import ipaddress
from random import randint

requests.packages.urllib3.disable_warnings()

APP_VERSION = "1.6.2"
API_ACCOUNT_URL = "https://account.onethingpcs.com"
API_CONTROL_URL = "https://control.onethingpcs.com"
API_REMOTE_DOWNLOAD_URL= "http://control-remotedl.onethingpcs.com"



#####################################
# Help function
#####################################

# MD5函数
def md5(s):
    import hashlib
    return hashlib.md5(s.encode('utf-8')).hexdigest().lower()

# 获取pwd值（密码MD5后加密再取MD5值）
def get_pwd(passwd):
    s = md5(passwd)
    s = s[0:2] + s[8] + s[3:8] + s[2] +s[9:17] + s[27] + s[18:27] + s[17] + s[28:]
    return md5(s)

# 获取sign值
def get_sign(body, k=''):
    l = []
    while len(body) != 0:
        v = body.popitem()
        l.append(v[0]+ '=' + v[1])
    l.sort()
    t = 0
    s = ''
    while t != len(l):
        s = s + l[t] + '&'
        t = t+1
    signInput = s + 'key=' + k
    sign = md5(signInput)
    return sign, s

# random ip
def rip():
	ip = '.'.join([str(int(''.join(
	[str(random.randint(0, 2)), 
	 str(random.randint(0, 5)), 
	 str(random.randint(0, 5))]
	))) 
	for _ in range(4)])
	if ipaddress.IPv4Address(ip).is_global:
		return ip
	else:
		return rip()

# get random number with len defined
# >>>random_with_N_digits(5)
# ---49616
def random_with_N_digits(n):
    range_start=10**(n-1)
    range_end=(10**n)-1
    return randint(range_start,range_end)

nowIp = rip()


class OTC(object):
    user_phone_number=None                  #登录账号,手机号
    user_password=None                        #登录密码
    phone_device_id=str(random_with_N_digits(16))  # 虚拟设备ID 16位
    imei_id=str(random_with_N_digits(15))    # 虚拟imei 15位
    session_id=None                       # 用户登录有获取的session
    user_id=None                          # 用户登录有获取的user_id
    is_logined=False                    # 当前用户是否登录标识符
    devices_info=None                      #设备信息{list}
    otc_pid = None                     #玩客云设备pid
    otc_device_id = None              #玩客云设备id
    usb_info=''
    usb_num=0                                        #硬盘数目
    download_json=None                      #获取正在进行的任务

    HEADERS = {
            'user-agent': "Mozilla/5.0",
            'Proxy-Client-IP' : nowIp,
            "cache-control": "no-cache"
        }
    def __init__(self,user_phone_number,user_password):
        ######################
        #  初始化 
        # `user_phone_number`
        # `user_password`
        # `session_id`
        # `user_id`
        ######################
        self.user_phone_number=user_phone_number
        self.user_password=user_password

        pwd = get_pwd(self.user_password)
        body = dict(
            deviceid = self.phone_device_id, 
            imeiid = self.imei_id, 
            phone = self.user_phone_number,    
            pwd = pwd, 
            account_type = '4'
        )
        sign, _ = get_sign(body)
        body = dict(
            deviceid = self.phone_device_id,
            imeiid = self.imei_id,
            phone = self.user_phone_number,
            pwd = pwd,
            account_type = '4',
            sign = sign
        )
        nowUrl = API_ACCOUNT_URL + '/user/login?appversion={appVersion}'.format(appVersion=APP_VERSION)
        cookies = None
        r = requests.post(url = nowUrl, data = body, verify = False, headers = self.HEADERS, cookies = cookies, timeout = 10)
        if r.ok!=False:
            self.session_id=r.cookies.get('sessionid')
            self.user_id = r.cookies.get('userid')
            self.is_logined=True
        # 初始化其他设备信息
        _,_=self.getListPeer()
        _,_,_=self.getUSBInfo()
        
    def getListPeer(self):
        # 获取设备信息
        try:
            body = {
                "appversion" : APP_VERSION,
                'ct' : '1',
                'v' : '1',
            }
            sign, _ = get_sign(body,self.session_id)
            url = API_CONTROL_URL + '/listPeer?appversion={appVersion}&ct=1&v=1&sign={sign}'.format(appVersion=APP_VERSION, sign=sign)
            cookies = dict(sessionid=self.session_id, userid=self.user_id)
            r = requests.get(url=url, headers=self.HEADERS, cookies=cookies, timeout=10)
            if r.ok == False:
                return False, r.reason
            tmpJson = r.json()
            if tmpJson['rtn'] != 0:
                return False, tmpJson['msg']

            devices_info = tmpJson['result'][1]['devices']
            self.devices_info=devices_info  #初始化玩客云设备信息变量 {list}
            self.otc_pid = devices_info[0]['peerid']                     #玩客云设备pid
            self.otc_device_id = devices_info[0]['device_id'] 
            return True, devices_info
        except Exception as ex:
            return False, str(ex)
    
    def getUSBInfo(self):
        try:
            body = {
                'appversion' : APP_VERSION,
                'ct' : '1',
                'deviceid' : self.otc_device_id,
                'v' : '1'
            }
            sign, signInput = get_sign(body, self.session_id)
            url = API_CONTROL_URL  + "/getUSBInfo?{signInput}sign={sign}".format(signInput=signInput, sign=sign)
            cookies = dict(sessionid=self.session_id, userid=self.user_id) # , origin='1'
            r = requests.get(url=url, headers=self.HEADERS, cookies=cookies, timeout=10)
            if r.ok == False:
                return False, r.reason
            usb_info = r.json()
            if usb_info['rtn'] != 0:
                return False, usb_info['msg']
            usb_num=len(usb_info['result'][1]['partitions'])
            self.usb_info=usb_info
            self.usb_num=usb_num
            return True, usb_info,usb_num
        except Exception as ex:
            return False, str(ex)

    def remote_download_login(self):
        # 暂时不知道干什么用
        try:
            body = {
                "pid" : self.otc_pid,
                'v' : '1',
                'ct' : '32',
            }
            sign, nouse = get_sign(body, self.session_id)
            url = API_REMOTE_DOWNLOAD_URL + '/login?' +  nouse + 'sign={sign}'.format(sign=sign)#mypid=mypid,
            cookies = dict(sessionid=self.session_id, userid=self.user_id)
            r = requests.get(url=url, headers=self.HEADERS, cookies=cookies, timeout=10)
            if r.ok == False:
                return False, r.reason
            tmpJson = r.json()
            if tmpJson['rtn'] != 0:
                return False, tmpJson['msg']
            
            return True, tmpJson
    
        except Exception as ex:
            False, ex

    def get_remote_download_info(self,str_type='0'):
        try:
            body = {
                "pid" : self.otc_pid,
                'v' : '2',
                'ct' : '32',
                'pos' : '0',
                'number' : '100',
                'type' : str_type,
                'needUrl' : '0',
            }
            sign, nouse = get_sign(body, self.session_id)
            url = API_REMOTE_DOWNLOAD_URL + '/list?' + nouse +  'sign={sign}'    \
                                            .format(
                                                # mypid=mypid, 
                                                # strType=strType, 
                                                sign=sign)
            cookies = dict(sessionid=self.session_id, userid=self.user_id)
            r = requests.get(url=url, headers=self.HEADERS, cookies=cookies, timeout=10)
            if r.ok == False:
                return False, r.reason
            download_json = r.json()
            if download_json['rtn'] != 0:
                return False, download_json['msg']
            self.download_json=download_json
            return True, download_json
    
        except Exception as ex:
            False, ex

    def createTask(self,job_list,file_download_path):
        ############################
        # one_job = {
        # "filesize": 0,
        # "name": '6a23cae9532b90a50d76101a688791f5edf1e716_ONE_PUNCH_MAN_01_12_OVA01_06_OAD_BDrip_BIG5_MP4_1280X720.torrent',
        # "url" : 'https://bt.agefans.com/torrent/6a23cae9532b90a50d76101a688791f5edf1e716_ONE_PUNCH_MAN_01_12_OVA01_06_OAD_BDrip_BIG5_MP4_1280X720.torrent?xxx=b8',
        # }
        # job_list=[one_job]
        #
        # file_download_path='/media/sda1/onecloud/tddownload' (must be lowwer)
        # file_download_path='/media/sda2/onecloud/tddownload' 
        # 
        try:

            temp_list = []
            for job in job_list:        
                temp_list.append(job)
                
            data = {
                'path': file_download_path,
                'tasks': temp_list
            }

            body = json.dumps(data)

            url = API_REMOTE_DOWNLOAD_URL  + "/createTask?pid={mypid}&v=2&ct=32".format(mypid=self.otc_pid)
            cookies = dict(sessionid=self.session_id, userid=self.user_id) # , origin='1'
            r = requests.post(url=url, data=body, headers=self.HEADERS, cookies=cookies, timeout=10)
            if r.ok == False:
                return False, r.reason
            tmpJson = r.json()
            if tmpJson['rtn'] != 0:
                return False, tmpJson['msg']
            
            return True, tmpJson
            
        except Exception as ex:
            False, ex
    
    def control_download_task(self,task_id,sign=0):
        #############################
        # sign=0 ,1 or 2
        # 0='start'
        # 1='pause'
        # 2='restore'
        ############################# 
        assert sign in [0,1,2]
        if sign==0:
            s='start'
        elif sign==1:
            s='pause'
        else:
            s='restore'
        try:
            body = {
                "pid" : self.otc_pid,
                'v' : '1',
                'ct' : '32',
                'tasks' : task_id + "_9",
            }
            sign, nouse = get_sign(body, self.session_id)
            url = API_REMOTE_DOWNLOAD_URL + '/'+s+'?' + nouse + 'sign={sign}'    \
                                            .format(
                                                # mypid=mypid, 
                                                # taskid=taskid, 
                                                sign=sign)
            cookies = dict(sessionid=self.session_id, userid=self.user_id)
            r = requests.get(url=url, headers=self.HEADERS, cookies=cookies, timeout=10)
            if r.ok == False:
                return False, r.reason
            tmpJson = r.json()
            if tmpJson['rtn'] != 0:
                return False, tmpJson['msg']
            
            return True, tmpJson
    
        except Exception as ex:
            False, ex

    def get_wkb_history(self,type='income',page='0'):
        # type must in ['income','outcome']
        assert type in ['income','outcome']
        pwd = get_pwd(self.user_password)
        body = dict(
            deviceid = self.phone_device_id, 
            imeiid = self.imei_id, 
            phone = self.user_phone_number,    
            pwd = pwd, 
            account_type = '4'
        )
        sign, _ = get_sign(body)
        body=dict(
            page=page,
            appversion=APP_VERSION,
            sign=sign
        )
        cookies = dict(
            sessionid=self.session_id,
            userid=self.user_id,
            origin='1'
        )
        url=API_ACCOUNT_URL+'/wkb/'+type+'-history'
        try:
            r=requests.post(url=url,data=body,headers=self.HEADERS,cookies=cookies,timeout=10)
            income_json=r.json()
            return True,income_json
        except Exception as e:
            False,e

# one_job = {
# "filesize": 0,
# "name": '100小时的夜晚.mp4',
# "url" : 'magnet:?xt=urn:btih:7G5ALSYYGODBSBE3ZLREDU2HY2UXXRDA'
# }
# job_list=[one_job]

# file_download_path='/media/sda1/onecloud/tddownload' 
# my_otc=OTC('17746648901','beautiful123')
# my_otc.createTask(job_list,file_download_path)
# _,_=my_otc.remote_download_login()
# q,info=my_otc.get_remote_download_info()
# print(info)

my_otc=OTC('17746648901','beautiful123')
_,info=my_otc.get_wkb_history(type='income' ,page=0)
print(info)