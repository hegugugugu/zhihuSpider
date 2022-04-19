# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 14:49:04 2022

@author: maotuo
"""
import pandas as pd
import time
import requests
import execjs
import hashlib
import urllib
import urllib.parse
from bs4 import BeautifulSoup

userId = []  # 保存用户id
userTime = []  # 保存用户发表评论的时间
userName = []  # 保存用户姓名
userContent = []  # 保存用户回答内容
userComment = []  # 保存该回答的评论数
userLike = []  # 保存该回答的赞同数
totals = []  # 记录回答的总条数

def zhuhuSipder(page):
    url = '/api/v4/questions/267209533/answers?'
    
    params = {
        'include':'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,attachment,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,is_labeled,paid_info,paid_info_content,reaction_instruction,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_recognized;data[*].mark_infos[*].url;data[*].author.follower_count,vip_info,badge[*].topics;data[*].settings.table_of_content.enabled',
        'offset':str(page),
        'limit':'5',
        'sort_by':'default',
        'platform':'desktop',
        }
    
    s = "+".join(["101_3_2.0", url+urllib.parse.urlencode(params), '"cookie的d_c0值"'])
     
    fmd5 = hashlib.new('md5', s.encode()).hexdigest()
     
    with open('g_encrypt.js', 'r') as s:
        ctx1 = execjs.compile(s.read(), cwd=r'Nodejs的node_modules路径')
    encrypt_str = ctx1.call('b', fmd5)
    
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        "cookie": 'd_c0="cookie的d_c0值";',
        "x-api-version": "3.0.91",
        "x-zse-93": "101_3_2.0",
        "x-zse-96": "2.0_%s" % encrypt_str,
    }
    
    response = requests.get("https://www.zhihu.com" + url, headers=headers,params=params).json()

    def timestamp_to_date(time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
        time_array = time.localtime(time_stamp)
        str_date = time.strftime(format_string, time_array)
        return str_date

 
    for i in response["data"]:
        id = i['author']['id']
        name = i['author']['name']
        content = i['content']
        like = i['voteup_count']
        comment = i['comment_count']
        soup = BeautifulSoup(content,'lxml')
        line = soup.get_text()
        time_ = timestamp_to_date(i["created_time"])
        # print(name + str(id) + ":" + comment)
        userId.append(id)
        userTime.append(time_)
        userName.append(name)
        userContent.append(line)
        userComment.append(comment)
        userLike.append(like)
 
    totals_ = response["paging"]["totals"]  # 回答总条数
    totals.append(totals_)
    return totals[0]


def mulitypage():
    page = 0
    zhuhuSipder(page)
    time.sleep(10)
    while (page < totals[0]):
        print("正在抓取第{}页".format(int(page / 5)))
        page += 5
        zhuhuSipder(page)
# 保存数据
def savedata():
    v = list(zip(userId, userTime, userName, userLike, userComment,userContent))
    # print(v)
    pd.DataFrame(v, columns=["id", "time", "name", "like", "comment", "cotent"]).to_excel("cat.xlsx")
 
 
if __name__ == "__main__":
    mulitypage()
    savedata()