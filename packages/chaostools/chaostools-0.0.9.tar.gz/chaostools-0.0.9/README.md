# Chaostools
They're really some ***great tools***!

超棒的一些工具！

In chaos, order and hope will also be revealed.

混沌中，也会透露出有序与希望。

If you want to add your tools, please contact the author of this library! (E-mail: admin@wcfstudio.cn)

如果你想添加你的工具，请联系这个库的作者！（电子邮箱：admin@wcfstudio.cn)

## Simple Tutorial

1. meanAgree(text,lang='zh-cn')
    -  Example 例子
    ```python
    import chaostools

    # Chinese
    print(chaostools.meanAgree("是的"))
    # True
    print(chaostools.meanAgree("你好"))
    # False
    print(chaostools.meanAgree("123"))
    # False
    print(chaostools.meanAgree("Yes"))
    # False

    # English
    print(chaostools.meanAgree("Yes"))
    # True
    print(chaostools.meanAgree("Hello"))
    # False
    print(chaostools.meanAgree("456"))
    # False
    print(chaostools.meanAgree("是的"))
    # False
    ```
    - Explanation 解释

        This is a function that can determine whether it represents agreement, approval, and permission, supporting both Chinese and English.

        这是一个可以判断是否表示同意、认可、允许的函数，支持中英双语。

        **Note**: The first letter of English should be *capitalized*. *Sentence ending punctuation* (such as . ... ! ?) is not allowed in both Chinese and English.

        **注意**：英文的首字母要*大写*。中英文均不得出现*句末标点*（如。 …… ！ ？）。

2. bdbk(word, id=None, mu_first=False)
    -  Example 例子
    ```python
    import chaostools

    # Basic
    print(chaostools.bdbk("昔阳县"))
    # {'status': 'OK', 'id': '5631351', 'description': '昔阳县，隶属于山西省晋中市，位于晋中市东部、太行山西麓，东与河北省赞皇县、内丘县、井陉县、邢台市接壤，西与寿阳县为邻，南与和顺县毗连，北与平定县相衔。总面积1954平方千米。截至2022年末，昔阳县常住人口186614人。商朝时期，属微。东汉建安末年（219年）为乐平郡，隋大业初年改为乐平县。民国元年（1912年），恢复乐平县，归中路道。1968年，晋中专区改设晋中地区，昔阳县仍属之。截至2021年10月，昔阳县下辖5个镇、5个乡和1个管委会。县政府驻乐平镇育新巷10号。昔阳县地方特产有昔阳小米、杏鲍菇。有大寨、龙岩大峡谷等风景名胜。2023年，昔阳县地区生产总值163.0亿元，比2022年增长5.1%。', 'contents': ['昔阳县', '昔阳县历史沿革', '昔阳县行政区划', '昔阳县地理环境', '昔阳县自然资源', '昔阳县人口', '昔阳县政治', '昔阳县经济', '昔阳县交通运输', '昔阳县社会事业', '昔阳县风景名胜', '昔阳县地方特产', '昔阳县著名人物', '昔阳县荣誉称号', '昔阳县现任领导'], 'contents_len': 15, 'text': '...'}
    print(chaostools.bdbk("昔阳县")["status"])
    # OK
    print(chaostools.bdbk("昔阳县")["id"])
    # 5631351
    print(chaostools.bdbk("昔阳县")["description"])
    # 昔阳县，隶属于山西省晋中市，位于晋中市东部、太行山西麓，东与河北省赞皇县、内丘县、井陉县、邢台市接壤，西与寿阳县为邻，南与和顺县毗连，北与平定县相衔。总面积1954平方千米。截至2022年末，昔阳县常住人口186614人。商朝时期，属微。东汉建安末年（219年）为乐平郡，隋大业初年改为乐平县。民国元年（1912年），恢复乐平县，归中路道。1968年，晋中专区改设晋中地区，昔阳县仍属之。截至2021年10月，昔阳县下辖5个镇、5个乡和1个管委会。县政府驻乐平镇育新巷10号。昔阳县地方特产有昔阳小米、杏鲍菇。有大寨、龙岩大峡谷等风景名胜。2023年，昔阳县地区生产总值163.0亿元，比2022年增长5.1%。
    print(chaostools.bdbk("keyword")["text"])
    '''
    Item's #1 Title 1
    ...
    Item's #1 Title 2
    ...
    Item's #1 Title 3
    ...
    '''

    # Others
    print(chaostools.bdbk("1450"))
    # {'status': 'MU', 'bdbk_multimeanings': [{'meaning': '中国台湾人对民进党网军的戏称', 'id': '56654602'}, {'meaning': '在爱情里表示“你是我的”', 'id': '63224232'}]}
    print(chaostools.bdbk("1450", id=chaostools.bdbk("1450")["bdbk_multimeanings"][1]["id"]))
    # {'status': 'OK', 'id': '63224232', 'description': '1450，在爱情里表示“你是我的”。', 'contents': ['1450'], 'contents_len': 1}
    print(chaostools.bdbk("1450", mu_first=True))
    # {'status': 'OK', 'id': '56654602', 'description': '1450，网络流行语，中国台湾人对民进党网军的戏称。', 'contents': ['1450', '1450引申含义', '1450社会评价'], 'contents_len': 3}
    ```
    - Explanation 解释

        This is a function used to crawl information from Baidu Baike.

        这是一个用来爬取百度百科信息的函数。

        > Parameter 参数

        - word

            Keyword. 关键词。
        
        - id=None

            The unique ID of the specified entry. 指定的词条唯一ID。
        
        - mu_first=False

            When the keyword is a polysemous word, does it default to obtaining the content of the first semantic item. 当关键词是一个多义词时，是否默认获取第一个义项的内容。

        > Return 返回

        - status

            Status value: OK represents successful acquisition, ML represents polysemous words (and there is no ID or default setting for the first item).
            
            状态值：OK代表获取成功，ML表示多义词（且没有ID和默认第一项的设置）。
        
        - The rest have literal meanings and do not need to be repeated. 其余的就是字面意思，无需赘述。

        **Note**: The description is only a brief and overview section.

        **注意**：description只是简述、概述部分。

3. hitokoto(c="", t=False, i=False, min_length=0, max_length=30)

    No nonsense, [direct official link](https://developer.hitokoto.cn/sentence/).

    不废话，[官方链接直达](https://developer.hitokoto.cn/sentence/)。

    **Note**: The parameter `t` is whether to return plain text results (if `t=False` or the default value, a Python dictionary object after parsing the request results is returned), and the parameter `i` is whether to use overseas lines with higher QPS values. `yiyan()` is equivalent to this function.

    **注意**：参数 `t` 是是否返回纯文字结果（如果 `t=False` 即默认值，则返回一个请求结果解析后的 Python 字典对象），参数 `i` 是是否使用 QPS 值更高的海外线路。`yiyan()` 等同于此函数。

    - Example 例子
    ```python
    import chaostools

    print(chaostools.hitokoto())
    # {'id': 6054, 'uuid': '36d1f4a5-2a34-4489-b776-f2857c8baf47', 'hitokoto': '想一个人有多想念，那又是文字失效瞬间。', 'type': 'j', 'from': '仓颉', 'from_who': '五月天', 'creator': '小杨', 'creator_uid': 5943, 'reviewer': 1044, 'commit_from': 'web', 'created_at': '1587639189', 'length': 19}
    print(chaostools.hitokoto(t=True))
    # 世界上是没有会消失的无影无踪的事物的，亲人也是，梦想也是。
    print(chaostools.hitokoto(max_length=3))
    # {'id': 5031, 'uuid': 'b10c93c2-281d-4000-919d-fd344c355691', 'hitokoto': '加油', 'type': 'a', 'from': '自编', 'from_who': None, 'creator': 'chibin', 'creator_uid': 4532, 'reviewer': 4756, 'commit_from': 'web', 'created_at': '1577117480', 'length': 2}{'id': 5031, 'uuid': 'b10c93c2-281d-4000-919d-fd344c355691', 'hitokoto': '加油', 'type': 'a', 'from': '自编', 'from_who': None, 'creator': 'chibin', 'creator_uid': 4532, 'reviewer': 4756, 'commit_from': 'web', 'created_at': '1577117480', 'length': 2}
    print(chaostools.yiyan())
    # {'id': 9122, 'uuid': '51d2a015-6df3-4507-8d75-a5e48863d1a5', 'hitokoto': '神即道，道即法，道法自然，如来。', 'type': 'l', 'from': '遥远的救世主', 'from_who': '豆豆', 'creator': 'erfie', 'creator_uid': 13776, 'reviewer': 1044, 'commit_from': 'web', 'created_at': '1671076363', 'length': 16}
    ```

4. calories(kind, appId, appSecret, key="苹果", foodId="befa2163948534a9", page=1, id=1)

    [Official link](https://www.mxnzp.com/doc/detail?id=32).
    
    [官方链接](https://www.mxnzp.com/doc/detail?id=32)。

    **Note**: One of the Roll API series, so you need to apply for ID and Secret first. The main information content returned is in the "data" key.

    **注意**：Roll API 系列之一，因此需要先申请 ID 和 Secret 。返回的主要信息内容在“data”键中。

    > Parameter 参数

    - kind

        The requested data type. 请求的数据类型。

        - `"type/list"`

            Get a categorized list of food. 获取食物的分类列表。

        - `"food/list"`

            Get a list of foods under the category. 获取分类下的食物列表。

        - `"food/search"`

            Search for food. 搜索食物。

        - `"food/details"`

            Get food details. 获取食物详情。

    - Example 例子
    ```python
    import chaostools

    print(chaostools.calories("type/list", "Your APP ID", "Your APP Secret")["data"])
    # [{'id': 1, 'name': '主食类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/1_v1.png'}, {'id': 2, 'name': '肉蛋类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/2_v1.png'}, {'id': 3, 'name': '大豆及制品', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/3_v1.png'}, {'id': 4, 'name': '蔬菜菌藻类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/4_v1.png'}, {'id': 5, 'name': '水果类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/5_v1.png'}, {'id': 6, 'name': '奶类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/6_v1.png'}, {'id': 7, 'name': '油脂类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/7_v1.png'}, {'id': 8, 'name': '坚果类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/8_v1.png'}, {'id': 9, 'name': '调味品', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/9_v1.png'}, {'id': 10, 'name': '饮料类', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/10_v1.png'}, {'id': 11, 'name': '零食及冷饮', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/11_v1.png'}, {'id': 12, 'name': '其他', 'icon': 'http://power-api.cretinzp.com:8000/foods_file/category/12_v1.png'}]
    ```