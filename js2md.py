import re


def write(filename: str, data: list):
    md = open(f'{filename}.md', 'a+', encoding='utf-8')
    for reply in data:
        md.write("#### {}***({}L)***:\n\n".format(reply['uid'], reply['floor']))
        quote = 0  # 用于统计引用层数
        for sent in reply['reply']:
            # 去除无用代码
            s = sent.replace('[quote]', '').replace('[/quote]', '')
            s = s.replace('[collapse= ]', '').replace('[/collapse]', '')
            s = s.replace('[list]', '').replace('[/list]', '')
            # 加重
            s = s.replace('===', '**').replace('[b]', '**').replace('[/b]', '**')
            # 下划线
            s = s.replace('[u]', '<u>').replace('[/u]', '</u>')
            # 列表每项前的点
            s = s.replace('[*]', '* ')
            # 替换颜色代码
            colors = re.findall(r'\[color=\w+\]', s)
            for color in colors:
                s = s.replace(color, '<font '+color[1:-1]+'>')
            s = s.replace('[/color]', '</font>')
            # 替换超链接
            urls = re.findall(r'\[url][ a-zA-z]+://[^\s^]*\[/url\]', s)
            for url in urls:
                s = s.replace(url, '<a href="'+url[5:-6]+'">链接</a>')
            urls = re.findall(r'\[url=[ a-zA-z]+://[^\s^\]]*\]', s)
            for url in urls:
                s = s.replace(url, '<a href="'+url[5:-1]+'">')
            s = s.replace('[/url]', '</a>')
            # 替换图片
            imgs = re.findall(r'\[img\][^\[]+\[/img\]', s)
            for img in imgs:
                s = s.replace(img, '<img src="'+img[5:-6].replace('./', 'https://img.nga.178.com/attachments/')+'"/>')
            # 计算引用层数
            if '[/quote]' in sent:
                quote -= 1
            # 写语句
            md.write('>'*quote+' '+s+('\n\n' if quote == 0 else '\n'))
            if '[quote]' in sent:
                quote += 1
        md.write('---\n\n')
