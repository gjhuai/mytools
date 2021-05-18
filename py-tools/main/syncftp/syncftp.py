#coding:utf-8
import datetime
from ftplib import FTP, error_perm
import os
import os.path
import re,time
import shutil

class MyFTP(FTP):
    encoding = "utf-8"  # 默认编码
    dir_pattern = re.compile(r'[a-zA-Z]{3}\s+\d{2}\s+[\d:]{4,}\s(.*)$')
    file_pattern = re.compile(r'(\d+)\s+[a-zA-Z]{3}\s+\d{2}\s+[\d:]{4,}\s(.*)$')

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
                file = self.dir_pattern.findall(file)[0]
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
            # print(file)
            if file.startswith('-'):
                # print(file)
                # r'(\d+)\s+[a-zA-Z]{3}\s+\d{2}\s+[\d:]{4,}\s(.*)$'
                match_file = self.file_pattern.findall(file)[0]
                files.append(match_file)

        self.retrlines(cmd, filter)
        return files


class SyncFile(FTP):
    LOCAL_PATH = os.getcwd()
    REMOTE_PATH = None

    def __list_dirs_files(self, dirpath):
        dirs = []
        files = []
        for filename in os.listdir(dirpath):
            path = dirpath + '/' + filename
            if os.path.isfile(path):
                files.append(filename)
            else:
                dirs.append(filename)
        return dirs, files


    def __sync_ftp_files(self, ftp, rem_path):
        if not SyncFile.REMOTE_PATH:
            SyncFile.REMOTE_PATH = input("请输入需要同步的目录:")
            self.__sync_ftp_files(ftp, SyncFile.REMOTE_PATH)
            return

        try:
            ftp.cwd(SyncFile.REMOTE_PATH)
        except error_perm:
            SyncFile.REMOTE_PATH = input("请输入需要同步的目录:")
            self.__sync_ftp_files(ftp, SyncFile.REMOTE_PATH)
            return

        r_dirs = ftp.getdirs(rem_path)
        r_file_tuples = ftp.getfiles(rem_path)
        r_files = [x[1] for x in r_file_tuples]
        # print(r_dirs)
        # print(r_files)

        loc_path = rem_path.replace(SyncFile.REMOTE_PATH, SyncFile.LOCAL_PATH)
        l_dirs, l_files = self.__list_dirs_files(loc_path)
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
                            ftp.cwd(rem_path) #覆盖上传
                            ftp.storbinary('STOR %s' % os.path.basename(rem_f), file)
                    except Exception as err:
                        print(err)


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
            self.__sync_ftp_files(ftp, dp)

        # 检查已经存在ftp是否和本地相同
        for dp in r_dirs:
            self.__sync_ftp_files(ftp, rem_path + '/' + dp)


    def sync(self):
        ftp = MyFTP()
        ftp.connect("cddyys.ddns.net", 94)  # 连接
        ftp.login("gjh", "hbdl9431")

        self.__sync_ftp_files(ftp, SyncFile.REMOTE_PATH)

        ftp.quit()  # 退出


if __name__ == '__main__':
    SyncFile.REMOTE_PATH = '/syncftp'
    sf = SyncFile()
    sf.sync()
