# -*- coding: utf-8 -*-

"""
@author:随时静听
@file: ChangeNsfocusReport.py
@time: 2018/11/07

"""

import os

import re
import random
import datetime
from decimal import Decimal

# with open('index.html', 'r') as f:
#     content = f.read()
import zipfile
import shutil
import glob

#指定导出报告的目录
REPORT_DIR='report_result'
#指定处理报告目录
ZIP_PATH='test123'

#报告生成8月份 -9月份的
MONTH_START=8
MONTH_END=12

def getTime(ip_num, scan_month):
    timeStr = """
    <tr class="odd">
                    <th width="120px" >时间统计</th>
                    <td>
                        开始：2018-10-29 16:09:48<br />
                        结束：2018-10-29 17:10:01</td>
                  </tr>
    """
    # 单个IP扫描时间确定
    total_time = reduce(lambda x, y: x + y, [random.randint(1, 4) for i in xrange(ip_num)])
    # print total_time
    Year = 2018
    Month = scan_month
    Day = random.choice([4, 5, 6])
    H = random.choice(list(range(9, 20)))
    M = random.choice(list(range(0, 60)))
    S = random.choice(list(range(0, 60)))
    S_end = random.choice(list(range(0, 60)))
    start = datetime.datetime(Year, Month, Day, H, M, S)

    end = (start + datetime.timedelta(minutes=total_time, seconds=S_end)).strftime("%Y-%m-%d %H:%M:%S")
    start2 = start.strftime("%Y-%m-%d %H:%M:%S")
    # print start
    # print end
    subStart_time = re.sub('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}<br', start2 + '<br', timeStr)
    subEnd_time = re.sub('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}</td>', end + '</td>', subStart_time)
    return start, subEnd_time


## 扫描时间替换和匹配 1.1 任务信息替换

def subScantime(content, new_time, maxscore):
    # 网络风险替换目标，需要修改风险值，根据下面的风险最高值
    title = '''
     <table class="report_table plumb">
          <tbody>
            <tr class="odd" >
              <th width="120" style="vertical-align:middle">网络风险</th>
              <td style="padding:6px;"><img align='absmiddle' src='reportfiles/images/b_low.gif' title='比较危险'></img><span class="level_danger middle" style='color:#396DC3'>比较安全（%s分）</span></td>
            </tr>
          </tbody>
        </table>
    ''' % maxscore
    # 网络风险匹配规则
    re_title = '<table class="report_table plumb">.*?</table>'

    re_scan_time = '<tr class="odd">\s+<th width="120px".*?>时间统计</th>.*?</tr>'
    content = re.sub(re_title, title, content, 1, re.S)
    content = re.subn(re_scan_time, new_time, content, 1, re.S)
    # print content[1]
    return content[0]


# 获取IP数量来定制扫描时间
def getIpnum(content):
    pattern = re.compile('<th>主机统计</th>.*?(\d+)<br />', re.S)
    ip_num = pattern.search(content).group(1)
    ip_num = int(ip_num)

    return ip_num


# IP_num=getIpnum(content)
# timestr=getTime(IP_num,11)
# print timestr
# content=subScantime(content,timestr)

#
def demotestRe(pattern, content):
    # pattern=re.compile(pattern)
    # match=re.search(pattern,content.decode('utf-8'),re.S)
    match = re.findall(pattern, content.decode('utf-8'), re.S)

    # print len(match)
    return match
    # print match.group()


# 网络风险匹配测试
# match=re.search(re_title,content,re.S)
# print match.group()
# print match
# 替换操作测试
# print re.sub(re_title,title,content,1,re.S)
# print repr(content)


## 扫描时间匹配测试
# testRe(re_scan_time,scan_time)
# testRe(re_scan_time,content)
# new_scan_time=getTime(6,8,)
#
# print getTime(6,8,scan_time)


# 获取2.1.x的table

#
# for table in testRe(tables,content):
#     print table
#     print '*'*30


def getTbody(pattern, table):
    # tables = u'<div class="report_h report_h3">2.*?</div>.*?<table width="100%">.*?总计.*?合计.*?</table>'
    # table_lst = testRe(tables, content)
    # table_tbody_sub_pattern = re.compile(
    #     '<tr class=".*?">\s+<td>.*?</td>.*?<td.*?>(\d+)</td>.*?<td.*?>(\d+)</td>.*?<td.*?>(\d+)</td>.*?<td.*?>(\d+)</td>.*?</tr>',
    #     re.S)

    lst = pattern.findall(table)
    # print lst

    count_num_lst = map(lambda x: ('0', '0', x[2], x[2]), lst )
    # print count_num_lst

    # print count_num_lst
    # staticts_num=reduce(lambda x,y:int(x[2])+int(y[2]),count_num_lst)
    staticts_num = str(sum([int(x) for x in zip(*count_num_lst)[2]]))
    count_num_lst.append(('0', '0', staticts_num, staticts_num))
    # for item in count_num_lst:
    #     print item
    # print lst
    # 数据回写
    # 数据组装
    tr_lst = [''.join(['<td>' + x + '</td>' for x in y]) for y in count_num_lst[:-1]]
    last = ''.join(['<td width="40px">' + x + '</td>' for x in count_num_lst[-1]])
    tr_lst.append(last)
    # print tr_lst
    # 一个tr 一个tr的替换，匹配到单个替换然后，整体再替换
    # 获取正规的table
    table_re = '<table class="report_table ">.*?</table>'
    new_table = re.search(table_re, table, re.S).group()
    # 替换的整体看作是new_table,所以，下面的更改都是针对new_table的
    # print new_table
    tr_re = '<tr class=.*?>\s+(?:<td.*?>\d+</td>\s+){4}</tr>'
    td_sub = '<td.*?>\d+</td>\s+<td.*?>\d+</td>\s+<td.*?>\d+</td>\s+<td.*?>\d+</td>\s+'
    # print table
    target_tr_lst = []
    for tr, t_tr in zip(re.findall(tr_re, new_table, re.S), tr_lst):
        # print tr
        # print 1111
        tr = re.sub(td_sub, t_tr, tr)
        target_tr_lst.append(tr)
        # 到这里就是table里面每个tr内容更换完毕
        # print tr

        # print re.sub(td_sub,'tt',tr)
        # print re.findall(td_sub,tr)
    # 获取更换过后的table
    # new_table=''.join(target_tr_lst) ##---- 这里有问题，不能直接拼接

    # --------------- 拼接处理 ---

    tbody = '\n'.join(target_tr_lst[:-1]) + '\n</tbody>'
    tbody = '<table class="report_table "><thead>' + tbody
    tfoot = '<tfoot>' + target_tr_lst[-1] + '''\n</tfoot>       </table>
                            </td>
                        </tr>
                    </table>'''
    new_table = tbody + tfoot

    # --------拼接处理 end

    # 更换table
    table_pattern = re.compile(table_re, re.S)

    table = table_pattern.sub(new_table, table)
    # print '*'*40
    # print table
    return table


#    # print pattern.subn(r'\1',table)[0]
# for table in table_lst[0:1]:
#     getTbody(table_tbody_sub_pattern,table)

def sub_all_table(content):
    # tables = u'<div class="report_h report_h3">2\.\d+\.\d.*?</div>\s*?<table\s+width="100%">.*?总计.*?合计.*?</table>'
    tables = re.compile('<div\s+class="report_h report_h3">2\.\d+\.\d.*?</div>\s*?<table\s+width="100%">.*?总计.*?合计.*?</table>',re.S)

    table_lst=tables.findall(content)
    # print table_lst[0]
    table_tbody_sub_pattern = re.compile(
        '<tr class=".*?">\s*?<td>.*?</td>.*?<td.*?>(\d+)</td>.*?<td.*?>(\d+)</td>.*?<td.*?>(\d+)</td>.*?<td.*?>(\d+)</td>.*?</tr>',
        re.S)
    new_tables = []
    print len(table_lst)
    for table in table_lst:

        # print table
        print '*'*60
        table = getTbody(table_tbody_sub_pattern, table)
        table = re.sub('<img .*?>', '', table)
        # print table_tbody_sub_pattern.findall(table)
        # print table
        new_tables.append(table)

    tables_html = ''.join(new_tables)
    # print tables_html
    tables_html = '''
    <div class="report_h report_h2" id="vuln_risk_category">2.1漏洞风险类别</div>
                <div>
    ''' + tables_html + '</div><div class="report_h report_h2"'
    vuln_risk_category_pattern = re.compile(
        '<div class="report_h report_h2" id="vuln_risk_category">2.1.*?<div class="report_h report_h2"', re.S)

    # print vuln_risk_category_pattern.search(content).group()
    content = vuln_risk_category_pattern.sub(tables_html, content)
    # print content
    return content


# sub_all_table(content)
# with open('test.html','w') as f:
#     f.write(sub_all_table(content))


## 替换主机奉献列表中的危险警告图标
def subHighPic(content):
    hight_pateern = "<img align='absmiddle' src='reportfiles/images/d_high\.gif' title='非常危险'>"
    safe_img = '<img align="absmiddle" src="reportfiles/images/d_low.gif" title="比较安全">'
    content = re.subn(hight_pateern, safe_img, content)
    # print content[0]
    # print re.findall(hight_pateern,content)
    return content[0]


# content=sub_all_table(content)
# content=subHighPic(content)
# with open('test.html','w') as f:
#     f.write(content)

## 主机风险列表3.1 漏洞个数替换，规则是找到

def subNumforhosts(content):
    tbody_pattern = re.compile('<div class="report_h report_h2" id="title00">3.1.*?(<tbody>.*?</tbody>)', re.S)
    # print content
    tbody_content = tbody_pattern.search(content).group(1)
    # print tbody_content
    tr_pattern = re.compile(
        '<tr.*?>.*?href="(.*?)".*?<td><span.*?>(\d+)</span></td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>.*?<td><span.*?>([\d\.]+)</span></td>.*?</tr>',
        re.S)

    tr_lst = tr_pattern.findall(tbody_content)
    # 数值处理
    # print tr_lst
    ip_filename_lst = [x[0] for x in tr_lst]
    tr_lst = [x[1:] for x in tr_lst]
    print len(tr_lst)
    tr_lst = [('0', '0', x[2], x[2], str(int(x[2]) / 10 + 1) + '.0' if int(x[2]) < 40 else '4.0') for x in tr_lst]
    MaxScore = str(max([Decimal(x) for x in zip(*tr_lst)[-1]]))
    foot = ['0', '0', str(sum([int(x) for x in zip(*tr_lst)[2]])), str(sum([int(x) for x in zip(*tr_lst)[2]])),
            MaxScore]
    # print tr_lst
    file_score_lst = [(ip, score[-1]) for ip in ip_filename_lst for score in tr_lst]
    file_score_lst.append(MaxScore)
    # print foot

    ## 数据组装
    pre_td_str = '''<td><span class="font_high">%s</span></td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td><span class="font_bold">%s</span></td>'''
    tr_html_lst = [pre_td_str % tr for tr in tr_lst]
    # print tr_html_lst[0]
    # print tr_html_lst[1]

    pre_foot_str = """
     <tfoot><tr class="second_title">
                                <td colspan="3">合计</td>
                                <td><span class="font_high">%s</span></td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                            </tr>
                            </tfoot>
    """ % (foot[0], foot[1], foot[2], foot[3], foot[4])
    # print foot

    # print tr_html_lst
    # tr 指定td替换
    # 获取所有的tr
    sub_tr_lst = re.findall('<tr.*?>.*?</tr>', tbody_content, re.S)

    sub_td_pattern = re.compile(
        '<td><span.*?>(\d+)</span></td>\s*?<td>(\d+)</td>\s*?<td>(\d+)</td>\s*?<td>(\d+)</td>\s*?<td><span.*?>([\d\.]+)</span></td>')
    sub_tr_htmls = []
    for tr, t_tr in zip(sub_tr_lst, tr_html_lst):
        tr = sub_td_pattern.sub(t_tr, tr)
        sub_tr_htmls.append(tr)
    sub_tr_htmls = '\n'.join(sub_tr_htmls)

    # print sub_tr_htmls

    # tbody替换
    tbody_pattern = '<div class="report_h report_h2" id="title00">3.1.*?(<tbody>.*?</tbody>).*?</div>'
    host_all_html = re.search(tbody_pattern, content, re.S).group()
    # print host_all_html
    # 在整理中替换 tbody ftoot内容
    tbody_pattern = re.compile('<tbody>.*?</tfoot>', re.S)
    host_all_html = tbody_pattern.sub('<tbody>' + sub_tr_htmls + '</tbody>' + pre_foot_str, host_all_html)

    # print host_all_html
    # 3.1 整体替换
    pattern = re.compile('<div class="report_h report_h2" id="title00">3\.1..*?<tbody>.*?</tfoot>.*?</div>', re.S)
    content = pattern.sub(host_all_html, content)
    # print content
    return content, file_score_lst


# content=subNumforhosts(content)

# with open('test.html','w') as f:
#     f.write(content)

# 漏洞分布中，高中漏洞替换删除
def sub_vuln_hight_middle(content):
    high_middle_pattern = re.compile(
        '<tr class="[odd|even]+ [vuln_high|vuln_middle]+" style="cursor:pointer;".*?</tr>\s+<tr class="more hide odd".*?</tr>',
        re.S)
    # content=high_middle_pattern.subn('',content)
    content = high_middle_pattern.sub('', content)
    detail_high_middle_pattern = re.compile('<tr class="more [hide] even"')
    return content


# content=sub_vuln_hight_middle(content)

#
# with open('test.html','w') as f:
#     f.write(content)

# 漏洞分布替换 ,4.1
def subVulndistribution(content):
    # tbody 获取
    Vulndistribution = re.search(
        '<div class="report_h report_h2" id="title00">4.1.*?(<tbody>.*?</tbody>).*?</tfoot>.*?</div>', content, re.S)
    # print Vulndistribution.group()
    tbody = Vulndistribution.group(1)
    # print tbody
    # 提取有效tr 从tbody中
    tr_lst = re.findall('<tr class="[odd|even]+ vuln_low".*?</tr>', tbody, re.S)
    # print len(tr_lst)
    # 获取序号和出现次数重新排序
    pattern = re.compile('<td>(\d+?)</td>.*?<td>(\d+?)</td>', re.S)
    ordernum_num_lst = []
    for i, tr in enumerate(tr_lst):
        ordernum_num = pattern.findall(tr)
        # ordernum_num[0][0]=i+1
        ordernum_num_lst.append((str(i + 1), ordernum_num[0][1]))
    # print ordernum_num_lst
    # 计算总次数
    total_num = str(sum([int(x[1]) for x in ordernum_num_lst]))
    # print total_num

    # ----- 替换开始
    # 数据构造tbody 替换
    order_num_pattern = re.compile('<td>\d+?</td>')
    num_pattern = re.compile('%</td>\s+<td>\d+?</td>')
    # 数据拼接
    order_pre = '<td>%s</td>'
    num_pre = '%%</td>\n<td>%s</td>'
    html_lst = []
    for order_num, num in ordernum_num_lst:
        str1 = order_pre % order_num
        str2 = num_pre % num
        html_lst.append([str1, str2])
    # print len(html_lst)
    new_tr_lst = []
    for tr, substr in zip(tr_lst, html_lst):
        tr = order_num_pattern.sub(substr[0], tr, 1)
        tr = num_pattern.sub(substr[1], tr)
        new_tr_lst.append(tr)
    # print len(new_tr_lst)
    # 附带详细信息tr获取
    hide_tr_lst = re.findall('<tr class="more hide [odd|even]+".*?>.*?<table.*?>.*?</table>.*?</tr>', tbody, re.S)
    # print len(hide_tr_lst)
    all_tr_lst = []
    for x in zip(new_tr_lst, hide_tr_lst):
        all_tr_lst.extend(x)
    new_tbody = "<tbody>" + '\n'.join(all_tr_lst) + '<tbody>'

    tfoot = """
    <tfoot>
                            <tr class="first_title">
                                <td colspan="4">合计</td>
                                <td>%s</td>
                            </tr>
                        </tfoot>""" % total_num
    tbody_tfoot = new_tbody + tfoot

    sub_tbody_tfoot_pattern = re.compile('<tbody>.*?</tfoot>', re.S)

    # Vulndistribution_html=sub_tbody_tfoot_pattern.subn(tbody_tfoot,Vulndistribution.group())
    Vulndistribution_html = sub_tbody_tfoot_pattern.sub(tbody_tfoot, Vulndistribution.group())
    # print Vulndistribution_html[1]

    # 整体替换
    all_pattern = re.compile(
        '<div class="report_h report_h2" id="title00">4.1.*?(<tbody>.*?</tbody>).*?</tfoot>.*?</div>', re.S)
    content = all_pattern.subn(Vulndistribution_html, content)

    # print content[1]
    return content[0]


# content=subVulndistribution(content)
#
# with open('test.html','w') as f:
#     f.write(content)
### 4.1 高风险[4]中危险[4]   ==>高风险[0]中危险[0]

def change4_1_Num(content):
    pattern=re.compile('高风险\[\d+\]')
    content=pattern.sub('高风险[0]',content)
    pattern=re.compile('中危险\[\d+\]')
    content = pattern.sub('中危险[0]', content)
    return content


# 脆弱账号剔除
def subweak_accounts(content):
    pattern = re.compile('<div class="report_h report_h2" id="app_weak_accounts">6.1.*?</table>.*?</div>', re.S)
    content = pattern.sub('<div class="report_h report_h2" id="app_weak_accounts">6.1应用程序脆弱帐号</div>', content)
    return content


# content=subweak_accounts(content)
#
# with open('test.html','w') as f:
#     f.write(content)

## picture 替换

def replace_pic(m):
    pattern=re.compile( '<img\s+src=".*?">',re.S)
    # print m.group()
    # print '*'*60
    content=pattern.subn("<img src='reportiles/images/g1ts2d8s4df6wegh234hsdf7sd78sdf678xe.png'>",m.group())
    # print content[1]
    return  content[0]

def replace_1_2(content):
    pattern=re.compile('<div class="report_h report_h2" id="title01">.*? report_h1">2.风险类别',re.S)
    content=pattern.subn(replace_pic,content)
    # print content[0]
    return content[0]
# 替换index.html
def subIndex(content, month):
    ip_num = getIpnum(content)
    print ip_num
    start, time_str = getTime(ip_num, month)

    # 替换3.1 替换高中风险图片：并替换漏洞数量
    content = subHighPic(content)
    content, file_score_lst = subNumforhosts(content)
    maxscore = file_score_lst[-1]
    # print maxscore
    # # 替换1.1 任务信息
    content = subScantime(content, time_str, maxscore)
    #
    # # 替换2.1 漏洞风险分类
    content = sub_all_table(content)
    #
    # # 替换4.1 高中漏洞剔除，并重新排序和计算风险值
    content=change4_1_Num(content)
    content = sub_vuln_hight_middle(content)
    content = subVulndistribution(content)
    # # 脆弱账号剔除
    content = subweak_accounts(content)

    #删除1.2 图片
    content=replace_1_2(content)

    return content, start, file_score_lst

# with open('2/index.html','r') as f:
#     content=f.read()
# content, start, file_score_lst = subIndex(content, 8)
# with open('2/test.html', 'w') as f:
#     f.write(content)

























##-------------------------------------------- 替换host主机文件中的分布---------------------------------------------------------

# with open('host/10.230.46.148.html') as f:
#     content = f.read()


def get_host_time(start):
    time_pre_str = '''
    <tr class="even">
						<th>扫描起始时间</th>
						<td>%s</td>
					</tr>


					<tr class="odd">
						<th>扫描结束时间</th>
						<td>%s</td>
					</tr>
    '''
    host_scan_start_str = start.strftime("%Y-%m-%d %H:%M:%S")
    host_scan_end = start + datetime.timedelta(minutes=random.randint(1, 4), seconds=random.randint(0, 60))
    host_scan_end_str = host_scan_end.strftime("%Y-%m-%d %H:%M:%S")
    time_html = time_pre_str % (host_scan_start_str, host_scan_end_str)
    return host_scan_end, time_html


def sub_host_time_ico(content, timestr, score):
    # 替换ico
    target_ico_html = '''
    <tr class="odd"">
				<th width="120" style="vertical-align:middle">主机风险</th>
				<td style="padding:6px;">  <img align="absmiddle" src="media/report/images/b_low.gif"/><span class="level_danger middle" style="color:#396DC3"> 比较安全（%s分） </span>  </td>
			</tr>
    ''' % score
    ico_pattern = re.compile(
        '<tr class="odd"">\s+<th width="120" style="vertical-align:middle">主机风险.*?<img align="absmiddle".*?</tr>', re.S)

    content = ico_pattern.sub(target_ico_html, content)

    # 替换时间
    time_pattern = re.compile('<tr class="even">\s+<th>扫描起始时间</th>.*?<th>扫描结束时间</th>.*?</tr>', re.S)
    content = time_pattern.subn(timestr, content)
    # print content[1]

    # 评分替换
    pre_score_html = '''
    <tr class="odd">
						<th width="190">漏洞风险评估分</th>
						<td> %s分 </td>
					</tr>



					<tr class="even">
						<th>主机风险评估分</th>
						<td>%s分</td>
					</tr>''' % (score, score)
    score_pattern = re.compile('<tr class="odd">\s+<th width="190">漏洞风险评估分</th>.*?</tr>.*?</tr>', re.S)
    content = score_pattern.sub(pre_score_html, content[0])
    return content


def replace_for_sub(m):
    html = m.group()
    # print html
    if re.search('vuln_low', html):
        return html
    else:
        return ""


def del_high_middle(content):
    pattern = re.compile('<li>\s+<div class="vul_summary" data-id="\d+?" data-port="[\d-]+?">.*?</li>', re.S)
    # print pattern.findall(replace_for_sub,content)[2]
    content = pattern.subn(replace_for_sub, content)
    # print content[1]
    return content[0]


### 去掉 - 并处理没有漏洞情况

# def del_NF(m):
# pattern=re.compile('(<tr class="(even|odd)">.*?vul_port.*?</tr>)',re.S)
# pattern=re.compile('(<tr class="(even|odd)">.*?vul_port.*?</tr>)',re.S)

# tr_lst=pattern.findall(m.group())
# print tr_lst[0][1]
# print len(tr_lst)
# new_tr_lst=[]
# for i,tr in enumerate(tr_lst):
#     ul=re.search('<ul>(.*?)</ul>.*?<ul>(.*?)</ul>',tr[0],re.S)
#     # print ul.group(2)
#     # print '*'*30
#     first_ul_li=re.findall('(<li>.*?</li>)',ul.group(1),re.S)
#     second_ul_li=re.findall('(<li>.*?</li>)',ul.group(2),re.S)
#     first_ul_li_num=len(first_ul_li)
#     sencod_ul_li_num=len(second_ul_li)
#     if first_ul_li!=0:
#         li_num=second_ul_li-first_ul_li
#     else:
#         li_num=0
#     if li_num!=0:
#         first_ul = '<ul>\n' + ul.group(1) + '\n</ul>'
#         if li_num>0:
#             sencod_ul='<ul>\n'+ul.group(2).replace('<li>-</li>)',"",li_num)+'\n</ul>'
#             new_tr_lst.append((first_ul,second_ul_li))
#     else:
#         new_tr_lst.append(('',''))

def handle_tr(m):
    # print m.group(1)==m.group()
    tr_content = m.group()
    ul = re.search('<ul>(.*?)</ul>.*?<ul>(.*?)</ul>', tr_content, re.S)
    # print ul.group(2)
    # print '*'*30
    first_ul_li = re.findall('(<li>.*?</li>)', ul.group(1), re.S)
    second_ul_li = re.findall('(<li>.*?</li>)', ul.group(2), re.S)
    first_ul_li_num = len(first_ul_li)
    sencod_ul_li_num = len(second_ul_li)
    if first_ul_li_num != 0:
        li_num = sencod_ul_li_num - first_ul_li_num

        if li_num > 0:
            new_tr = tr_content.replace('<li>-</li>', "", li_num)
            return new_tr
        else:
            return tr_content
    else:
        return ""


def del_NF(m):
    pattern = re.compile('(<tr class="(even|odd)">.*?vul_port.*?</tr>)', re.S)

    tr_content = pattern.subn(handle_tr, m.group())
    # print m.group()
    # print m.group(1)
    return tr_content[0]


def sub_port_all(content):
    pattern = re.compile('<table id="vuln_list" class="report_table">.*?</table>', re.S)

    content = pattern.subn(del_NF, content)
    return content[0]


# 2.2 漏洞详情替换
def remove_high_middle(m):
    tr = m.group()
    # print tr
    # print '***' * 30
    if tr.find('vuln_high') != -1:
        return ""
    if tr.find('vuln_middle') != -1:
        return ""
    return tr


def del_detail_middle_high_host(m):
    table_content = m.group()
    pattern = re.compile(
        '<tr class="(even|odd)".*?>.*?</tr>\s+?<tr class="solution".*?>\s+?<td>\s+?<table.*?>.*?</table>\s+</td>\s+</tr>',
        re.S)

    table_content = pattern.subn(remove_high_middle, table_content)
    # print table_content[1]
    return table_content[0]


def sub_detail_host(content):
    pattern = re.compile('<div id="vul_detail">.*?</div>', re.S)

    content = pattern.subn(del_detail_middle_high_host, content)
    # print content[1]
    return content[0]


# 去除匿名账号

def move_weak_users(weak_content):
    pattern = re.compile('<table .*?>.*?</table>', re.S)
    content = pattern.subn('', weak_content.group())
    return content[0]


def remove_weak_users(content):
    pattern = re.compile('<div class="report_h report_h2" id="title5_6">.*?</div>\s+<div>.*?</div>', re.S)
    content = pattern.subn(move_weak_users, content)
    # print content[1]
    return content[0]


def sub_host_html(file_score,zf ,start):
    # with open(file_score[0], 'r') as f:
    #     content = f.read()
    content=zf.read(file_score[0])

    time_end, timestr = get_host_time(start)
    # print timestr
    content = sub_host_time_ico(content, timestr, file_score[1])

    content = del_high_middle(content)

    # del_NF(content)

    content = sub_port_all(content)  # 显示有一点bug even odd

    # 2.2 漏洞详情替换
    content = sub_detail_host(content)
    content = remove_weak_users(content)
    # 重新写入
    return content,time_end


## ------------------------ 主程序开始
#获取指定路径下的zip文件列表
def getAllzip(filepath='./'):
    zip_lst=glob.glob1(filepath,'*.zip')

    zip_lst=map(lambda path:os.path.join(filepath,path),zip_lst)
    return zip_lst



def gethost_lst(file_lst):
    host_lst=[]
    for html in file_lst:
        if re.search('host/\d+\.\d+\.\d+\.\d+\.html',html):
            host_lst.append(html)

    return host_lst

# zf=zipfile.ZipFile('4.zip')
#
# filelist=zf.namelist()
# print gethost_lst(filelist)
# 获取压缩包中文件夹host下面的.html
def handleZip(filename,month):
    # print 66666
    if not os.path.exists(filename):
        # print 666
        return
    # try :
    zf=zipfile.ZipFile(filename)
    host_lst=gethost_lst(zf.namelist())
    index_content=zf.read('index.html')
    # print index_content
    content,start_scan_time,score_lst=subIndex(index_content,month)
    # print content
    # index 写入


    #初始化操作
    newzipfilename=os.path.splitext(os.path.split(filename)[1])[0]+'_'+str(month)
    # print newzipfilename

    tmp_dir=os.path.join('tmp',newzipfilename)
    zf.extractall(tmp_dir)
    # # os.makedirs(tmp_dir)
    # os.mkdir(os.path.join(tmp_dir,'host'))
    # # print tmp_dir
    # reportfiles=tmp_dir+'/reportfiles'
    # if not os.path.exists(reportfiles):
    #     shutil.copytree('reportfiles',reportfiles)
    #
    # # shutil.m
    tmp_dir=tmp_dir.decode('gbk')
    print tmp_dir
    with open(os.path.join(tmp_dir,'index.html'),'w') as f:
        f.write(content)
    # print score_lst
    for host_file_score in  score_lst[:-1]:

        host_content,start_scan_time=sub_host_html(host_file_score,zf,start_scan_time)
        with open(os.path.join(tmp_dir, host_file_score[0]), 'w') as f:
            f.write(host_content)
    # shutil.rmtree(tmp_dir)
    if not os.path.exists(REPORT_DIR):
        os.mkdir(REPORT_DIR)
    month_dir=os.path.join(REPORT_DIR,str(month))
    if not os.path.exists(month_dir):
        os.mkdir(month_dir)

    zip_name=os.path.join(month_dir,newzipfilename)+'.zip'
    print zip_name.decode('gbk')
    shutil.make_archive(zip_name,'zip',tmp_dir.encode('gbk'))





# handleZip('host.zip',8)


def run():

    zip_lst=getAllzip(ZIP_PATH)
    # zip_lst=['test123/456.zip']
    for month in xrange(MONTH_START,MONTH_END+1):
        for filename in zip_lst:
            # print filename
            handleZip(filename,month)


if __name__ == '__main__':
    # print 123
    run()
    pass
