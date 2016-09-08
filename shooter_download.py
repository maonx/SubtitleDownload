#!/usr/bin/python
# -*- coding:utf-8 -*-
# API说明：https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview#


"""通过射手API自动获取并下载字幕文件

Usage:
    shooter_download [-ce] <szFilePath>

Options:
    -h,--help        显示帮助菜单
    -c               中文字幕(默认)
    -e               英文字幕

Example:
    shooter_download D:\test.avi
    shooter_download -c D:\test.avi
"""

import urllib
import urllib2
import json
import os
import hashlib
import sys
from docopt import docopt

reload(sys)
sys.setdefaultencoding( "utf-8" )


def ComputerFileHash(szFilePath):
    file_object = open(szFilePath, 'rb')
    FileSize = 0L
    offsets = [0 for i in range(4)]
    szRet = ''
    try:
        FileSize = os.path.getsize(szFilePath)
        if(FileSize < 8192):
            #a video file less then 8k? impossible!
            pass
        else:
            offsets[3] = FileSize - 8192
            offsets[2] = FileSize / 3
            offsets[1] = FileSize / 3 * 2
            offsets[0] = 4096
            for offset in offsets:
                file_object.seek(offset, 0)
                data = file_object.read(4096)
                szMD5 = hashlib.md5(data)
                if szRet:
                    szRet += ';'
                szRet += str(szMD5.hexdigest())
    finally:
        file_object.close( )
    return szRet


def get_sub_address(szFilePath, languages):
    url = 'https://www.shooter.cn/api/subapi.php'
    sublist = []
    if os.path.exists(szFilePath):
        filehash = ComputerFileHash(szFilePath)
        for lang in languages:
            values = {'filehash': filehash, 'pathinfo': szFilePath, 'format': 'json', 'lang' : lang}
            values = urllib.urlencode(values)
            try:
                req = urllib2.Request(url, values)
                response = urllib2.urlopen(req)
                text = response.read()
                if text == '\xff':
                    pass
                else:
                    sublist = sublist + (json.loads(text))
            except:
                print u'网络连接错误！'
                exit()
        return sublist
    else:
        print u'文件路径错误！'
        exit()


def download_sub(sublist):
    if sublist:
        print u'找到了 %d 个字幕文件！' % len(sublist)
        number = 0
        for subjson in sublist:
            download_url = subjson['Files'][0]['Link']
            sub_ext = '.' + subjson['Files'][0]['Ext']
            req = urllib2.Request(download_url)
            response = urllib2.urlopen(req)
            number += 1
            filename = response.info()['Content-Disposition'].split('filename=')[1].rstrip(sub_ext) + '(' + str(number) + ')' + sub_ext
            urllib.urlretrieve(download_url, filename)
        print u'下载完成！'
    else:
        print u'没有找到字幕！'


def main():
    """command-line interface"""
    arguments = docopt(__doc__)
    szFilePath = arguments['<szFilePath>'].decode('GB2312')
    if arguments['-c'] and arguments['-e']:
        lang = ['eng', 'chn']
    elif arguments['-e']:
        lang = ['eng']
    else:
        lang = ['chn']
    download_sub(get_sub_address(szFilePath, lang))


if __name__ == '__main__':
    main()
