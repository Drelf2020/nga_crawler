import re
import os
import time
import json
import requests
import js2md
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
                'Cookie': 'taihe_bi_sdk_uid=9f6b3350fa4f95f39ae629d7d6d2433d; taihe=a1747dcebbecee5a50f8dfa53cd7005c; UM_distinctid=177b9ce533354b-0a9bab952bd6fb-73e356b-144000-177b9ce5334617; CNZZDATA30043604=cnzz_eid=1103191160-1594714273-https%3A%2F%2Fbbs.nga.cn%2F&ntime=1623134901; ngacn0comUserInfo=Drelf	Drelf	39	39		10	200	4	0	0	61_2; ngacn0comUserInfoCheck=731861771366f61e88f3af515823dbec; ngacn0comInfoCheckTime=1623137434; ngaPassportUid=61710301; ngaPassportUrlencodedUname=Drelf; ngaPassportCid=X95hemmhg11gme0ll3gusboc7ilo2r3p6fbcu0am; lastvisit=1623137722; lastpath=/thread.php?fid=734&ff=-34587507; bbsmisccookies={"uisetting":{0:0,1:1624459883},"pv_count_for_insad":{0:-157,1:1623171704},"insad_views":{0:2,1:1623171704}}; _cnzz_CV30043604=forum|fid-34587507|0'
            }

    def get_reply(self, tid: str, folder: str = '') -> int:
        """
        :param tid: 帖子的id，可在网址中找到\n
        :param folder: 保存文件夹名\n
        :return int: 执行成功返回1，否则返回错误代码
        """
        try:
            # 先跑一遍网页 用于获取总页数和主楼
            r = requests.get(f'https://bbs.nga.cn/read.php?tid={tid}', headers=self.headers)
            # 网页可爬 新建文件夹用于存放帖子
        except Exception:
            return 101
        try:
            # 奇怪的正则表达式 爬不到这个表达式是因为总页数只有一页
            total = int(re.search(r"',\d+:\d+", r.text).group().split(':')[1])
        except Exception:
            total = 1
        # 从谷歌浏览器Copy的主楼的xpath
        main = etree.HTML(r.text).xpath('//*[@id="postcontent0"]/text()')
        if not folder:
            folder = etree.HTML(r.text).xpath('//*[@id="postsubject0"]/text()')[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        for i in tqdm(range(1, total+1)):
            # 遍历帖子
            s = []
            try:
                r = requests.get(f'https://bbs.nga.cn/read.php?tid={tid}&page={i}', headers=self.headers)
            except Exception:
                return 102
            if r.status_code == 200:
                data = etree.HTML(r.text)
                for post in data.xpath('//table[@class="forumbox postbox"]'):
                    # 遍历该页面中每个回复
                    uid, floor = post.xpath('.//a[@class="author b"]/@*')[:-1]  # 回复人uid以及楼层
                    reply = post.xpath('.//span[@class="postcontent ubbcode"]//text()')  # 回复内容
                    # s += '{},{},{}\n'.format(uid.split('=')[-1], floor.replace('postauthor', ''), main if floor == 'postauthor0' else reply)
                    s.append({'uid': int(uid.split('=')[-1]), 'floor': int(floor.replace('postauthor', '')), 'reply': main if floor == 'postauthor0' else reply})
                # 导出
                with open(f'{folder}\\{i}.json', 'w', encoding='utf-8') as f:
                    f.write(json.dumps(s, ensure_ascii=False, indent=4))
                js2md.write(folder+'\\'+folder, s)
            else:
                return 103
            time.sleep(0.25)  # 休眠 防止爬虫进入过载模式
        return 1

    def get_post(self, fid: str, n: list):
        """
        :param fid: 版id，可在网址中找到\n
        :param n: 要爬取的页 如n=[1, 3, 4]表示爬取第1、3、4页的帖子\n
        :return int: 执行成功返回该版所有帖子id，否则返回错误代码\n
        常用fid: 主板-34587507 安科733 酒馆734 问答室735 拉特兰736
        """
        try:
            # 先跑一遍网页 用于获取总页数
            r = requests.get(f'https://bbs.nga.cn/thread.php?fid={fid}', headers=self.headers)
        except Exception:
            return 101
        try:
            # 奇怪的正则表达式 爬不到这个表达式是因为总页数只有一页
            total = int(re.search(r"',\d+:\d+", r.text).group().split(':')[1])
        except Exception:
            total = 1
        url = []
        for i in tqdm(n):
            if i > total:
                continue
            try:
                r = requests.get(f'https://bbs.nga.cn/thread.php?fid={fid}&page={i}', headers=self.headers)
            except Exception:
                return 102
            if r.status_code == 200:
                data = etree.HTML(r.text)
                for post in data.xpath('//table[@id="topicrows"]/tbody'):
                    url.append({'title': post.xpath('.//td[2]/a//text()')[0], 'tid': post.xpath('.//td[2]/a/@href')[0].split('=')[1]})
            else:
                return 103
            time.sleep(0.5)
        return url


if __name__ == '__main__':
    print(nga().get_reply('25608284'))
    '''
    url = nga().get_post('733', [1])
    for u in tqdm(url):
        if not u['tid'] in ['22984478', '17190139', '27065807']:
            print(f'\n{u["title"]}({u["tid"]}):')
            nga().get_reply(u['tid'], u['title'])
        print('\n已完成备份:')
    '''
