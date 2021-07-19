#coding:utf-8
import datetime
from ftplib import FTP, error_perm
import os
import os.path
import re,time
import shutil

# from dateutil import parser
class MyFTP(FTP):
    encoding = "utf-8"  # 默认编码
    pattern = re.compile(r'(\d+)\s+[a-zA-Z]{3}\s+\d{2}\s+[\d:]{4,}\s(.*)$')

    def getdirs(self, *args):
        '''拷贝了 nlst() 和 dir() 代码修改，返回详细信息而不打印'''
        cmd = 'LIST'
        # func = None
        # if args[-1:] and type(args[-1]) != type(''):
        #     args, func = args[:-1], args[-1]
        for arg in args:
            cmd = cmd + (' ' + arg)
        files = []

        def filter(file):
            #print(file)
            if file.startswith('d'):
                file = self.pattern.findall(file)[0]
                files.append(file)

        self.retrlines(cmd, filter)
        return files

    def getfiles(self, *args):
        """返回文件列表，简要信息"""
        cmd = 'LIST'
        for arg in args:
            cmd = cmd + (' ' + arg)
        files = []

        def filter(file):
            print(file)
            if file.startswith('-'):
                # print(file)
                # r'(\d+)\s+[a-zA-Z]{3}\s+\d{2}\s+[\d:]{4,}\s(.*)$'
                match_file = self.pattern.findall(file)[0]
                files.append(match_file)

        self.retrlines(cmd, filter)
        return files


LOCAL_PATH = os.getcwd()
print(LOCAL_PATH)
REMOTE_PATH = '/syncftp'


def list_dirs_files(dirpath):
    dirs = []
    files = []
    for filename in os.listdir(dirpath):
        path = dirpath + '/' + filename
        if os.path.isfile(path):
            files.append(filename)
        else:
            dirs.append(filename)
    return dirs, files


def sync_ftp_files(ftp, rem_path):
    r_dirs = ftp.getdirs(rem_path)
    r_file_tuples = ftp.getfiles(rem_path)
    r_files = [x[1] for x in r_file_tuples]
    # print(r_dirs)
    # print(r_files)

    loc_path = rem_path.replace(REMOTE_PATH, LOCAL_PATH)
    l_dirs, l_files = list_dirs_files(loc_path)
    # print(l_dirs)
    # print(l_files)

    print('\n----------------' + rem_path + '----------------')
    # 删除 本地多余的文件
    del_files = list(set(l_files).difference(set(r_files)))
    for f in del_files:
        dp = loc_path+'/'+f
        print('删除文件：' + dp)
        os.remove(dp)

    # 下载 ftp多出的文件
    add_files = list(set(r_files).difference(set(l_files)))
    for f in add_files:
        fp = open(loc_path + '/' + f, 'wb')
        bufsize = 1024
        dp = rem_path+'/'+f
        print('下载文件：' + dp)
        ftp.retrbinary('RETR ' + dp, fp.write, bufsize)
    ftp.set_debuglevel(0)

    # 上传 本地最近修改的文件
    cmp_files = list(set(l_files).intersection(set(r_files)))
    for f in cmp_files:
        rem_f = rem_path + '/' +f
        # size_r = ftp.size(rem_f)
        size_r = int([x[0] for x in r_file_tuples if x[1]==f][0])

        loc_f = loc_path + '/' + f
        size_l = os.path.getsize(loc_f)

        if size_r!=size_l:
            mtime_r = ftp.sendcmd("MDTM "+rem_f)[4:].strip()
            mtime_r = datetime.datetime.strptime(mtime_r, '%Y%m%d%H%M%S').timestamp()
            mtime_l = os.path.getmtime(loc_f)

            if mtime_l > mtime_r:
                print("上传", f, size_l, mtime_l, "=>", size_r, mtime_r)
                try:
                    with open(loc_f, 'rb') as file :
                        #覆盖上传
                        ftp.cwd(rem_path)
                        ftp.storbinary('STOR %s' % os.path.basename(rem_f), file)
                except Exception as err:
                    print(err)
                    result = False


        # files = ftp.mlsd(f)
        # print(files)
        # for file in files:
        #     name = file[0]
        #     timestamp = file[1]['modify']
        #     print(timestamp)
            # time = parser.parse(timestamp)
            # print(name + ' - ' + str(time))


    # 删除 本地多余的目录
    del_dirs = list(set(l_dirs).difference(set(r_dirs)))
    for f in del_dirs:
        dp = rem_path+'/'+f
        print('删除目录：' + dp)
        shutil.rmtree(dp)

    # 下载 ftp多出的目录
    add_dirs = list(set(r_dirs).difference(set(l_dirs)))
    for f in add_dirs:
        dp = rem_path+'/'+f
        print('创建目录：' + dp)
        os.mkdir(dp)
        sync_ftp_files(ftp, dp)

    # 检查已经存在ftp是否和本地相同
    for dp in r_dirs:
        sync_ftp_files(ftp, rem_path + '/' + dp)


def test():
    ftp = MyFTP()
    ftp.connect("cddyys.ddns.net", 94)  # 连接
    ftp.login("gjh", "hbdl9431")

    sync_ftp_files(ftp, REMOTE_PATH)

    ftp.quit()  # 退出


if __name__ == '__main__':
    test()
