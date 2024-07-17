# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import pysvn


# svn_url = "svn://192.168.3.101/repository"
#
# svn_user_name = "ldq"
# svn_password = "lingdequan"
#
# client = pysvn.Client()
# client.set_default_user_name = svn_user_name
# client.set_default_password = svn_password
#
# print(client)
#
# # print(entries)
#
# print("OK")


# -*- coding:utf-8 -*-
import pysvn
import locale
import datetime
import os
import sys


def setlocale():
    language_code, encoding = locale.getdefaultlocale()
    if language_code is None:
        language_code = 'en_GB'
    if encoding is None:
        encoding = 'UTF-8'
    if encoding.lower == 'utf':
        encoding = 'UTF-8'
    locale.setlocale(locale.LC_ALL, '%s.%s' % (language_code, encoding))


def get_login(realm, username, may_save):
    return True, 'test', 'test', True


# 获取svn地址,url指svn地址，path，指项目拉取到哪个地方
def svncheckout(url, path):
    client = pysvn.Client()
    # client.callback_get_login = get_login
    ret = client.checkout(url, path)

# 更新svn的地址
def svnupdate():
    client = pysvn.Client()
    ret = client.update(path)
    return ret


def svncheckin(url):
    client = pysvn.Client()
    # url=svnurl+"/"+projectname
    # os.makedirs(url)
    client.add(url)
    client.checkin(url, u'项目文件的创建')


# 写入日志到本地,主要用于更新信息使用的
def svninfo(path):
    client = pysvn.Client()
    entry = client.info(path)
    Version = "Version: %s" % entry.commit_revision.number
    Author = "Author: %s" % entry.commit_author
    Update = "Update Date: %s" % str(datetime.datetime.fromtimestamp(entry.commit_time))[:-7]
    url = path + '\log.txt'
    f = file(url, 'a')
    f.write(Version + '\n' + Author + '\n' + Update + '\n' + '-' * 32 + '\n')
    f.close()


def copyFiles(sourceDir, targetDir):  # 文件的复制
    if sourceDir.find(".svn") > 0:
        return
    for file in os.listdir(sourceDir):
        sourceFile = os.path.join(sourceDir, file)
        targetFile = os.path.join(targetDir, file)
        if os.path.isfile(sourceFile):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetFile) or (
                    os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                open(targetFile, "wb").write(open(sourceFile, "rb").read())
        if os.path.isdir(sourceFile):
            First_Directory = False
            copyFiles(sourceFile, targetFile)


def run(svnurl, path, projectname):
    # url为svn的仓库地址，path为本地路径,project为项目路径
    svncheckout(svnurl, path)
    sourceDir = path + "/template"
    targetDir = path + "/" + projectname
    copyFiles(sourceDir, targetDir)  # 资源文件
    # svncheckin(targetDir)


if __name__ == "__main__":

    svnurl = "svn://192.168.3.101/repository"

    # # run(svnurl,"./script/ui",sys.argv[0]) #从控制台接收一个名称，进行文件夹的创建
    #
    # path = './script/ui'
    #
    # run(svnurl, path, sys.argv[0])
    #

    client = pysvn.Client()
    client.cat("svn://192.168.3.101/repository/AJ-安监/wl-围栏/0/0/1/config.ini")
    # ret = client.checkout(svnurl, "./AJ-安监/aqd_zs-中山安全带检测/0/0/2")



















