import requests
import re
import os
import json

from mytelnet import MyTelnet


class TestBase(object):
    
    def getCpuAndSensorType(self):  # 获取cpu和sensor信息
        r = requests.get('http://'+self.IP+'/?jcpcmd=bootargs -act list',cookies=dict(loginflag='1'))
        if r.status_code == 200:
            res = r.text
            sensor = re.findall('.*?sensor=(.*?);', res)[0]
            cpu = re.findall('.*?cpu=(.*?);', res)[0]
            self.sensor = sensor
            self.cpu = cpu
            return cpu, sensor
        else:
            return False

    def debug(self, *args, **kw):
        msg = ''
        for val in args:
            msg = '{}{}'.format(msg, val)
        print(msg, **kw)

    def getMd5sum(self, cpu, sensor):   # 获取sensor_bin的md5值
        self.md5_data = {}
        tel = MyTelnet(self.IP, port=24)
        tel.login()
        if re.match('^T\d+\w*$', cpu):  # 君正cpu
            path = '/ipc/sensor/'
        else:
            path = '/ipc/effect/'   # 其他cpu
        cmd = "ls {}|xargs -n1".format(path)
        r = tel.write(cmd, return_flag=True)
        res = re.split('\r|\n', r)
        files = []
        color_print_rule =  '^\x1b.*?\d+m(.*?)\x1b\[\d+m$'  # 匹配是否为带颜色的打印
        for txt in res:
            if re.match(color_print_rule, txt): # 如果是带颜色的打印就提取其中的纯文本,过滤颜色字符串
                txt = re.match(color_print_rule, txt).groups()[0]
            if txt == cmd or txt == tel.finished_flag.decode() or txt == '':
                continue
            files.append(txt)
        for file in files:
            cmd = "md5sum {}".format(path+file)
            r = tel.write(cmd, return_flag=True)
            res = re.split('\r|\n', r)
            r1 = ''
            for txt in res:
                if txt == cmd or txt == tel.finished_flag.decode() or txt == '':
                    continue
                r1 += txt
            self.md5_data[file] = r1
        self.result['md5_val'] = self.md5_data
        tel.exit()
    
    def get_filepath_from_version(self):    # 从设备版本号中得到相应的路径
        rule = '^(.*?)A?\d?\..*-(.*?)$' #对版本进行匹配
        res = re.findall(rule, self.version)
        if res != None:
            tmp = self.getCpuAndSensorType()
            if tmp:
                cpu_type, sensor_type = tmp
                version_type = res[0][0]
                custom_type  = res[0][1]
                file_full_path = "result/"+cpu_type+'/'+custom_type+'/'+version_type+'/'+sensor_type+'.txt'
                file_path = "result/"+cpu_type+'/'+custom_type+'/'+version_type+'/'
                return [file_full_path, file_path, sensor_type] # 完整的文件路径、文件夹路径以及sensor类型
            else:
                return False
        else:
            return False      

    def match_version(self):
        print(self.version)
    
    def find_file_from_version(self):
        result_file = False
        #  = self.get_filepath_from_version()[1]
        _, dir, sensor_name = self.get_filepath_from_version()
        for root, dirs, files in os.walk(dir):
            for file in files:
                file_array = str(file)
                file_array = file_array.split('.')[0].split('-')
                if sensor_name in file_array:
                    result_file = file
                    break
        if result_file:
            return dir + result_file
        else:
            return False

    def make_dir(self,path):
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
        
    def make_all_dir(self, filepath):   # 创建所有的目录
        self.debug('[make_all_dir] ',filepath)
        filepath = filepath.split('/')
        tmp = ''
        for dir in filepath:
            if tmp == '':
                tmp = dir
            else:
                tmp = tmp+'/'+dir
            self.make_dir(tmp)

    def my_test(self):
        self.match_result()
    
    def get_new_file_path(self):
        base_path = ''
    
    def match_result(self): # 对比版本信息
        result_file = self.find_file_from_version()
        self.getMd5sum(self.cpu, self.sensor)
        if result_file:
            self.debug("[match_result] 目标文件:{}".format(result_file))
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            except Exception as e:
                self.debug('[match_result] ', e)
                self.debug('[match_result] 打开对比文件异常,无法对比')
            else:
                self.comparesion_dict(json_data, self.result)                 
        else:
            while True:
                ans = input("无法找到匹配文件,是否指定文件进行匹配? Y:指定文件匹配/N:不指定并取消对比\r\n")
                if ans == 'N' or ans == 'Y':
                    break
            if ans == 'Y':
                while True:
                    target_dir = input('请输入匹配模板路径(路径如`result/T31/GEN/V/JXF23.txt`):\r\n')
                    if os.path.exists(target_dir):
                        try:
                            with open(target_dir, encoding='utf-8') as fd:
                                dict1 = json.load(fd)
                        except:
                            self.debug('[match_result] 导入json文件异常')
                        else:
                            self.comparesion_dict(dict1, self.result)
                    else:
                        self.debug('[match_result] 文件不存在!')
                    a = input('是否退出? Y/y退出\r\n')
                    if a == 'Y' or a == 'y':
                        break
        while True:
            answer = input("是否将当前结果保存? Y:保存退出/N:不保存退出\r\n")
            if answer == 'Y':
                self.dump_json_to_file()
                break
            elif answer == 'N':
                break
            else:
                self.debug("[match_result] input error")
    
    def dump_json_to_file(self):    # 将结果保存到json
        file, file1, _ = self.get_filepath_from_version()    # 完整路径,包含文件名
        self.make_all_dir(file1)    # 创建目录
        if file:
            self.debug("[dump_json_to_file] dump to {}".format(file))
            if os.path.exists(file):
                while True:
                    answer = input("文件已存在,是否更新? Y:更新/N:不更新并退出\r\n")
                    if answer == 'Y':
                        with open(file, 'r', encoding='utf-8') as fd:
                            data = json.load(fd)
                        new_file = file+'.'+data['version']
                        if os.path.exists(new_file):
                            os.remove(new_file)
                        os.rename(file, new_file)
                        self.dump_json_to_file()
                        break
                    elif answer == 'N':
                        break
                    else:
                        self.debug('[dump_json_to_file] input error')
            else:
                with open(file,'a', encoding='utf-8') as fd:
                    json.dump(self.result, fd, indent=4, ensure_ascii=False)
                self.debug('[dump_json_to_file] success')
        else:
            self.debug("[dump_json_to_file] can't find file")
            
    def comparesion_dict(self, dict1, dict2, index=0):  # 对比两个字典的不同,dict2为当前版本的结果,dict1为之前版本的结果
        err_list = []
        for key in dict1:
            try:
                dict1[key], dict2[key]
            except:#有不存在的
                err_list.append(key)
            else:#都存在
                if dict1[key] == dict2[key]:
                    pass
                else:
                    err_list.append(key)
        for key in dict2:
            try:
                dict1[key], dict2[key]
            except:#有不存在的
                err_list.append(key)
            else:#都存在
                if dict1[key] == dict2[key]:
                    pass
                else:
                    err_list.append(key)
        err_list = list(set(err_list))
        newindex = index+1
        for key in err_list:
            print('     '*index+'[{}][ERROR]'.format(key))
            try:
                dict1[key], dict2[key]
            except:
                try:
                    print('     '*newindex+'之前版本:', dict1[key])
                except:
                    print('     '*newindex+'之前版本: empty')
                try:
                    print('     '*newindex+'当前版本:', dict2[key])
                except:
                    print('     '*newindex+'当前版本: empty')
            else:#都存在
                if type(dict1[key]) == type(dict2[key]) == dict:
                    self.comparesion_dict(dict1[key], dict2[key], newindex) # 如果都是字典类型继续递归对比
                else:
                    print('     '*newindex+'之前版本:', dict1[key])
                    print('     '*newindex+'当前版本:', dict2[key])
                
    def end_test(self): # 脚本运行完成后浏览器弹窗提示
        js = 'alert("运行完毕!")'
        self.driver.execute_script(js)

if __name__ == '__main__':
    a= TestBase()
    a.IP = '192.168.150.45'
    cpu,sensor = a.getCpuAndSensorType()
    a.result = {}
    a.getMd5sum(cpu,sensor)
    for key in a.result['md5_val']:
        print(key,a.result['md5_val'][key])
