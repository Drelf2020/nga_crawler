import re
import os
import time
import requests
from tqdm import tqdm
from lxml import etree


class nga(object):
    def __init__(self, user: str = None, pwd: str = None):
        if user and pwd:
            # 想写个用账号密码登录自动获取Cookie但验证码不好处理
            pass
        else:
            # 没有账号密码时用默认Cookie
            self.headers = {
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
            }

    def get_reply(self, tid: str) -> bool:
        """
        :param tid: 帖子的id，可在网址中找到\n
        :return bool: 执行成功返回True，否则False
        """
        try:
            # 先跑一遍网页 用于获取总页数和主楼
            r = requests.get(f'https://bbs.nga.cn/read.php?tid={tid}', headers=self.headers)
            # 奇怪的正则表达式
            total = int(re.search(r"',\d+:\d+", r.text).group().split(':')[1])
            # 从谷歌浏览器Copy的xpath
            main = ','.join(etree.HTML(r.text).xpath('//*[@id="postcontent0"]/text()'))
            # 网页可爬 新建文件夹用于存放帖子
            if not os.path.exists(tid):
                os.makedirs(tid)
        except Exception:
            return False
        for i in tqdm(range(1, total+1)):
            # 遍历帖子
            s = ''
            try:
                r = requests.get(f'https://bbs.nga.cn/read.php?tid={tid}&page={i}', headers=self.headers)
            except Exception:
                return False
            if r.status_code == 200:
                data = etree.HTML(r.text)
                for post in data.xpath('//table[@class="forumbox postbox"]'):
                    # 遍历该页面中每个回复
                    uid, floor = post.xpath('.//a[@class="author b"]/@*')[:-1]  # 回复人uid以及楼层
                    reply = ','.join(post.xpath('.//span[@class="postcontent ubbcode"]//text()'))  # 回复内容
                    s += '{},{},{}\n'.format(uid.split('=')[-1], floor.replace('postauthor', ''), main if floor == 'postauthor0' else reply)
                # 导出
                with open(f'{tid}\\{i}.csv', 'w', encoding='utf-8') as f:
                    f.write(s)
            else:
                return False
            time.sleep(1)  # 休眠1s防止爬虫进入过载模式
        return True


if __name__ == '__main__':
    nga().get_reply('21141255')
