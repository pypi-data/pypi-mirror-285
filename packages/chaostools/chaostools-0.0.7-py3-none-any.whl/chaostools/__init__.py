#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json

# class BdbkParseError(Exception):
#     print("BdbkParseError: The content you are looking for cannot be found on the page.It may be because: 1. The word is incorrect and may not be in the Baidu Encyclopedia database. 2. The program itself has an error in parsing. 3. The format of the page content has changed. 4. An unexpected error occurred during the request process. 5. Other unknown unexpected errors. If it is not due to usage, please contact the developer")
#     print("百度百科解析错误：在页面中找不到您想要的内容。可能是因为： 1.这个词不正确，也许不在百度百科数据库中。 2.程序本身解析有误。 3.页面内容格式已有变化。 4.请求过程出现意外错误。 5.其他未知的意外错误。如果非使用原因，清联系开发者")

def meanAgree(text,lang='zh-cn'):
    zh_cn_list = ["是的", "是", "同意", "对", "没错", "正是", "正合我意", "非常同意", "完全同意", "绝对同意", "非常赞同", "我同意", "我支持", "赞同", "对啊", "就是这样", "完全正确", "没错儿", "嗯", "对对", "就是那样", "完全同意你的观点", "哇，这说得对", "对哩，我完全同意", "是呀，说得一点也没错", "对啊对啊，就这么回事儿", "哼唧，完全正确", "嗯呐，完全同意", "哼哈，你说得对极了", "得啦，我跟你站一边儿", "哎呦，这个可以有", "中", "是哩", "对哩", "没错哩", "没叉哩", "实在是中", "没毛病", "没问题", "实对", "实对哩", "实实对哩", "实实是对哩", "一点儿也没问题", "一点儿也没毛病", "可对哩", "可是对哩", "真是对哩", "真对", "可真对", "对着哩", "对们", "对的了", "就是", "就是哩", "就是嘞"]
    en_list = ["Yes", "OK", "Agree", "Correct", "True", "Absolutely", "Exactly", "I couldn't agree more", "I fully agree with you", "I absolutely agree with you", "I strongly agree with you", "I totally agree with you", "I second that motion", "I'm in agreement with you on that point", "I agree with your viewpoint", "You got it right", "That's spot on", "That's correct", "Correctamundo", "Yep", "Yup", "That's the ticket", "I couldn't agree more with you there", "I fully support your idea/proposal/motion/decision/plan/vision/position/viewpoint/argument/standpoint/conviction/decision/theory/hypothesis/conclusion/proposition/plan/motion/decision/plan/vision/position/viewpoint/argument/standpoint/conviction/decision/theory/hypothesis/conclusion/proposition", "Yer right, I'm with you all the way", "Aye, ye got it spot on", "Aw yeah, couldn't be more right", "Absolutely bang on, mate", "Dang, you're dead-on, partner", "I'm all for it", "You got it", "That's the ticket", "Yeah", "You're right"]
    if lang=="zh-cn":
        if text in zh_cn_list:
            return True
        else:
            return False
    elif lang=="en":
        if text in en_list:
            return True
        else:
            return False

def bdbk(word, id=None, mu_first=False):
    if id != None:
        bdbk_page = requests.get("https://baike.baidu.com/item/%s/%s"%(word,id))
    else:
        bdbk_page = requests.get("https://baike.baidu.com/item/%s"%word)
    
    bdbk_html = bdbk_page.content
    bdbk_bs4 = BeautifulSoup(bdbk_html, 'lxml')
    bdbk_result = bdbk_bs4.find_all("meta")
    bdbk_contents = bdbk_result[4]["content"].split(", ")
    for content in bdbk_contents:
        bdbk_contents[bdbk_contents.index(content)] = content.replace(bdbk_result[7]["content"], "")
    bdbk_contents = bdbk_contents[1:]
    for content_item in bdbk_contents:
        bdbk_text = bdbk_bs4.find_all(class_="J-lemma-content")[0].get_text().replace("播报编辑", "").replace(content_item, "\n"+content_item+"\n")

    if bdbk_result[3]["content"] == "百度百科是一部内容开放、自由的网络百科全书，旨在创造一个涵盖所有领域知识，服务所有互联网用户的中文知识性百科全书。在这里你可以参与词条编辑，分享贡献你的知识。":
        bdbk_multimeanings = []
        for bdbk_multimeaning in bdbk_bs4.find_all("a", re.compile("contentItemChild")):
            bdbk_multimeanings.append({"meaning": bdbk_multimeaning.find("span", re.compile("contentItemChildText")).string, "id": bdbk_multimeaning["href"].split("/")[3].split("?")[0]})
        if mu_first:
            bdbk_html = requests.get("https://baike.baidu.com/item/%s/%s"%(word,bdbk_multimeanings[0]["id"])).content
            bdbk_bs4 = BeautifulSoup(bdbk_html, 'lxml')
            bdbk_result = bdbk_bs4.find_all("meta")
            return {"status": "OK", "id": bdbk_bs4.find("link")["href"].split("/")[5], "description": bdbk_result[3]["content"], "contents": bdbk_contents, "contents_len": len(bdbk_contents), "text": bdbk_text}
        else:
            return {"status": "MU", "bdbk_multimeanings": bdbk_multimeanings}
    else:
        return {"status": "OK", "id": bdbk_bs4.find("link")["href"].split("/")[5], "description": bdbk_result[3]["content"], "contents": bdbk_contents, "contents_len": len(bdbk_contents), "text": bdbk_text}

def hitokoto(c="", t=False, i=False, min_length=0, max_length=30):
    if i:
        hitokoto_baseurl = "https://international.v1.hitokoto.cn/"
    else:
        hitokoto_baseurl = "https://v1.hitokoto.cn/"
    if t:
        if c == "":
            return str(requests.get(hitokoto_baseurl + "?encode=text&min_length=%d&max_length=%d"%(min_length, max_length)).content, encoding="utf-8")
        else:
            return str(requests.get(hitokoto_baseurl + "?c=%s&encode=text&min_length=%d&max_length=%d"%(c, min_length, max_length)).content, encoding="utf-8")
    else:
        if c == "":
            return json.loads(str(requests.get(hitokoto_baseurl + "?min_length=%d&max_length=%d"%(min_length, max_length)).content, encoding="utf-8"))
        else:
            return json.loads(str(requests.get(hitokoto_baseurl + "?c=%s&min_length=%d&max_length=%d"%(c, min_length, max_length)).content, encoding="utf-8"))
yiyan = hitokoto

def calories(kind, appId, appSecret, key="苹果", foodId="befa2163948534a9", page=1, id=1):
    calories_baseurl = "https://www.mxnzp.com/api/food_heat/%s"%kind
    if kind == "type/list":
        return json.loads(str(requests.get(calories_baseurl + "?app_id=%s&app_secret=%s"%(appId, appSecret)).content, encoding="utf-8"))
    elif kind == "food/list":
        return json.loads(str(requests.get(calories_baseurl + "?id=%d&page=%d&app_id=%s&app_secret=%s"%(id, page, appId, appSecret)).content, encoding="utf-8"))
    elif kind == "food/search":
        return json.loads(str(requests.get(calories_baseurl + "?keyword=%s&page=%d&app_id=%s&app_secret=%s"%(key, page, appId, appSecret)).content, encoding="utf-8"))
    elif kind == "food/details":
        return json.loads(str(requests.get(calories_baseurl + "?foodId=%s&app_id=%s&app_secret=%s"%(foodId, appId, appSecret)).content, encoding="utf-8"))

print(calories("type/list","n9lcyvsmekkphmoo","VUFYaml2VU9Lb0ZVRDlpRkxiRW9EQT09")["data"])