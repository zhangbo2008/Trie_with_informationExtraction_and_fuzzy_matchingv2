#!/usr/bin/env python   Trie树在信息抽取上的应用. 并发加速.
# -*- coding:utf-8 -*-
from collections import defaultdict
import re

__all__ = ['NaiveFilter', 'BSFilter', 'DFAFilter']
__author__ = 'observer'
__date__ = '2012.01.05'


class NaiveFilter():

    '''Filter Messages from keywords
    very simple filter implementation
    >>> f = NaiveFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keywords = set([])

    def parse(self, path):
        for keyword in open(path):
            self.keywords.add(keyword.strip().decode('utf-8').lower())

    def filter(self, message, repl="*"):
        message = unicode(message).lower()
        for kw in self.keywords:
            message = message.replace(kw, repl)
        return message


class BSFilter:

    '''Filter Messages from keywords
    Use Back Sorted Mapping to reduce replacement times
    >>> f = BSFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keywords = []
        self.kwsets = set([])
        self.bsdict = defaultdict(set)
        self.pat_en = re.compile(r'^[0-9a-zA-Z]+$')  # english phrase or not

    def add(self, keyword):
        if not isinstance(keyword, unicode):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        if keyword not in self.kwsets:
            self.keywords.append(keyword)
            self.kwsets.add(keyword)
            index = len(self.keywords) - 1
            for word in keyword.split():
                if self.pat_en.search(word):
                    self.bsdict[word].add(index)
                else:
                    for char in word:
                        self.bsdict[char].add(index)

    def parse(self, path):
        with open(path, "r") as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')
        message = message.lower()
        for word in message.split():
            if self.pat_en.search(word):
                for index in self.bsdict[word]:
                    message = message.replace(self.keywords[index], repl)
            else:
                for char in word:
                    for index in self.bsdict[char]:
                        message = message.replace(self.keywords[index], repl)
        return message


class DFAFilter():

    '''Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'  #这是一个不可见字符,看起来跟''一样,但是实际上不一样! 他作为结尾符很适合!


    def delete(self, keyword):
        pass










    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)): #对字符串里面每一个字符建立trie树.
            if chars[i] in level: #如果当前这个汉子存在,那么就level进入下一层.
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):#走到头了.
                    break
                for j in range(i, len(chars)):#建立新的子字典.
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0} #然后写入结束符.
                break
        if i == len(chars) - 1: # 说明已经有过这个字符串,那么我们就写入结束符即可.
            level[self.delimit] = 0

    def parse(self, path):
        with open(path,encoding='utf-8') as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)




#==============这个函数,输入message,返回 跟trie树中匹配上的所有字符串的start end索引,组成的二维数组.
#==============这个函数,输入message,返回 跟trie树中匹配上的所有字符串的start end索引,组成的二维数组. 这里面end是按照python规范来!==============这个是最短匹配,从头到尾找子串,只要匹配成功就跳过这个成功的. 找后面匹配的部分!
    #==========现在我们把这个最短匹配当做默认情况,因为这个算法是最快的.一般也足够用了!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def pipei_shortest(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        out=[]
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for index,char in enumerate( message[start:]):
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:#无脑进入.
                        level = level[char]
                    else:#===============匹配成功了!#===========这个地方好像有问题, 如果字典里面有a 也有ab,那么运行到a就停了,不会继续找更长的!!!!!!!!!!!!!!!!
                        ret.append(repl * step_ins)
                        old_start=start
                        start += step_ins - 1
                        out.append([old_start,start+1])
                        break
                else:#如果char不存在,
                    ret.append(message[start])
                    break
            else: # for else: 上面的break都没触发,就走这个else. 说明一直进入到了最后一层.并且里面一直都没有结束符!!!!!说明当前位置字符串只是一个前缀,不能成为单词.所以不是我们要的.
                ret.append(message[start])

            start += 1#=========这里也是可以直接跳过.

        return out



#最长匹配, 尽量找跟字典中最长的匹配, 尽可能让找到的字符串最长!!!!!!!!!!!!!!!!!!!性能会比上面的低很多!
    def pipei_longest(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        out=[]
        message = message.lower()
        ret = []
        start = 0

        while start < len(message):
            level = self.keyword_chains
            step_ins = 0#用来记录当前遍历到字典的第几层.
            start2 = None
            for index,char in enumerate( message[start:]):
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:#无脑进入.
                        level = level[char]
                    else:#===============匹配成功了!#===========这个地方好像有问题, 如果字典里面有a 也有ab,那么运行到a就停了,不会继续找更长的!!!!!!!!!!!!!!!!
                        level = level[char]
                        old_start=start
                        start2 =start+ step_ins - 1 #保证找到的不会重叠.


                else:#如果char不存在,
                    # ret.append(message[start])
                    break

            #=================遍历玩了当前字符为起始字符的全排列.
            if start2!=None:
                out.append([start, start2 + 1])
            if start2!=None:
                start=start2+1 #因为已经匹配最长了,直接跳过即可!!!!!!!!!!
            else:
                start += 1

        return out











#全匹配,也是最浪费性能的!!!!!!!!!!!!!!!!!!!!!!!!!!!!性能会比上面的低很多!
    def pipei_all(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        out=[]
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0#用来记录当前遍历到字典的第几层.
            for index,char in enumerate( message[start:]):
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:#无脑进入.
                        level = level[char]
                    else:#===============匹配成功了!#===========这个地方好像有问题, 如果字典里面有a 也有ab,那么运行到a就停了,不会继续找更长的!!!!!!!!!!!!!!!!
                        level = level[char]
                        old_start=start
                        start2 =start+ step_ins - 1 #保证找到的不会重叠.
                        out.append([old_start,start2+1])

                else:#如果char不存在,
                    # ret.append(message[start])
                    break
            else: # for else: 上面的break都没触发,就走这个else. 说明一直进入到了最后一层.并且里面一直都没有结束符!!!!!说明当前位置字符串只是一个前缀,不能成为单词.所以不是我们要的.
                # ret.append(message[start])
                pass
            start += 1

        return out


#===========提供一个队列q接口.
    def pipei_longest2(self, message, q):
            if not isinstance(message, str):
                message = message.decode('utf-8')
            out=[]
            message = message.lower()
            ret = []
            start = 0

            while start < len(message):
                level = self.keyword_chains
                step_ins = 0#用来记录当前遍历到字典的第几层.
                start2 = None
                for index,char in enumerate( message[start:]):
                    if char in level:
                        step_ins += 1
                        if self.delimit not in level[char]:#无脑进入.
                            level = level[char]
                        else:#===============匹配成功了!#===========这个地方好像有问题, 如果字典里面有a 也有ab,那么运行到a就停了,不会继续找更长的!!!!!!!!!!!!!!!!
                            level = level[char]
                            old_start=start
                            start2 =start+ step_ins - 1 #保证找到的不会重叠.


                    else:#如果char不存在,
                        # ret.append(message[start])
                        break

                #=================遍历玩了当前字符为起始字符的全排列.
                if start2!=None:
                    out.append([start, start2 + 1])
                if start2!=None:
                    start=start2+1 #因为已经匹配最长了,直接跳过即可!!!!!!!!!!
                else:
                    start += 1
            q.put(out)
            # return out











def test_first_character():
    gfw = DFAFilter()
    gfw.add("1989年")
    assert gfw.filter("1989", "*") == "1989"


if __name__ == "__main__":

    import random

    if 0:
        def Unicode():
            val = random.randint(0x4e00, 0x9fbf)
            return chr(val)


        a = []
        for i in range(int(1e9)):
            a.append(Unicode() + Unicode() + Unicode() + Unicode() + Unicode() + Unicode() + '\n')
        with open('keywordstest1e9', 'w', encoding='utf-8') as f:
            f.writelines(a)








    # gfw = NaiveFilter()
    # gfw = BSFilter()
    import time

    t=time.time()
    gfw = DFAFilter() # 本质就是中文trie树的实现. 很简单.
    gfw.parse("keywords")
    print('建立trie树需要的时间',time.time()-t)

    import time
    t = time.time()



    if 0:
        gfw = DFAFilter()  # 本质就是中文trie树的实现. 很简单.
        gfw.parse("keywords_explaning_3_method")
        print('if you are confused withe the 3 method you can set this if =true, and run the code below')
        print('性能pipei_shorest>pipei_longest>>pipei_all')


        print('pipei_shorest')
        print(gfw.pipei_shortest("啊"))
        print(gfw.pipei_shortest("啊啊啊啊"))
        print(gfw.pipei_shortest("嗷嗷"))
        print(gfw.pipei_shortest("苹果干"))
        print(gfw.pipei_shortest("苹果干什"))
        print(gfw.pipei_shortest("苹果干什么苹果干什么"))



        print('pipei_longest')
        print(gfw.pipei_longest("啊"))
        print(gfw.pipei_longest("啊啊啊啊"))
        print(gfw.pipei_longest("嗷嗷"))
        print(gfw.pipei_longest("苹果干"))
        print(gfw.pipei_longest("苹果干什"))
        print(gfw.pipei_longest("苹果干什么苹果干什么"))


        print('pipei_all')
        print(gfw.pipei_all("啊"))
        print(gfw.pipei_all("啊啊啊啊"))
        print(gfw.pipei_all("嗷嗷"))
        print(gfw.pipei_all("苹果干"))
        print(gfw.pipei_all("苹果干什"))
        print(gfw.pipei_all("苹果干什么苹果干什么"))


#==========
    print('我推荐使用pipei_shortest,或者 pipei_longest')
    wenben='浭澼亾庉舙簭卯蒵鐛峜褙椿浭澼鐛浜奔姎鶄鉼渼賳璲贌俰槏晾e4r32dsf顼夸劙俤軸記ds 43邃灴靭乴跆亽543534543克匁逢鸣蛝壩祘括馈畍欤甲顼43534夸劙俤軸記'*3000
    max_token_len=6
    if 1:
        a=(gfw.pipei_longest(wenben))
        print(len(a),'第一个方案找到多少个匹配的')


    print('单进程查询使用的时间',time.time() - t)

    # test_first_character()


    if 0:
        #进行并行加速.比如在一本百万字的书里面搜索你要的一堆keyword在哪里出现过.
        import os,time
        from multiprocessing import Process
        import multiprocessing
        t=time.time()
        def worker():
            print("子进程执行中>>> pid={0},ppid={1}".format(os.getpid(),os.getppid()))
            time.sleep(2)
            print("子进程终止>>> pid={0}".format(os.getpid()))
        def main():
            half=len(wenben)//2





            q=multiprocessing.Queue()
            print("主进程执行中>>> pid={0}".format(os.getpid()))
            ps=[]
            # 创建子进程实例
            if 1:
                p=Process(target=gfw.pipei_longest2,args=(wenben[:half],q))
                ps.append(p)
                p=Process(target=gfw.pipei_longest2,args=(wenben[half:],q))
                ps.append(p)
                p=Process(target=gfw.pipei_longest2,args=(wenben[half-max_token_len-1:half+max_token_len-1],q))
                ps.append(p)
            # 开启进程
            for i in ps:
                i.start()
            # 阻塞进程
            for i in ps:
                i.join()
            print("主进程终止")
            # print(q.get(),'qsize大小!')
 
        main()
    # print('查询使用的时间',time.time() - t)
if 0:
        #进行并行加速.比如在一本百万字的书里面搜索你要的一堆keyword在哪里出现过.
        import os,time
        from multiprocessing import Process
        import multiprocessing
        t=time.time()
        def worker():
            print("子进程执行中>>> pid={0},ppid={1}".format(os.getpid(),os.getppid()))
            time.sleep(2)
            print("子进程终止>>> pid={0}".format(os.getpid()))
        def main():
            half=len(wenben)//2





            q=multiprocessing.Queue()
            print("主进程执行中>>> pid={0}".format(os.getpid()))
            ps=[]
            # 创建子进程实例
            if 1:
                p=Process(target=gfw.pipei_longest,args=(wenben[:half],q))
                ps.append(p)
                p=Process(target=gfw.pipei_longest,args=(wenben[half:],q))
                ps.append(p)
                p=Process(target=gfw.pipei_longest,args=(wenben[half-max_token_len-1:half+max_token_len-1],q))
                ps.append(p)
            # 开启进程
            for i in ps:
                i.start()
            # 阻塞进程
            for i in ps:
                i.join()
            print("主进程终止")
            # print(q.get(),'qsize大小!')
 
        main()
# print('查询使用的时间',time.time() - t)





from multiprocessing import Process
import multiprocessing
import os
if 1:
    print('cpushulaign',os.cpu_count())
    cpu_c=os.cpu_count()
    t=time.time()
    pool = multiprocessing.Pool(processes=cpu_c) # 创建4个进程
    results = []
    half=len(wenben)//2

    results+=(pool.apply_async(gfw.pipei_longest, (wenben[:half], )).get())
    results+=(pool.apply_async(gfw.pipei_longest, (wenben[half:], )).get())
    results+=(pool.apply_async(gfw.pipei_longest, (wenben[half-max_token_len-1:half+max_token_len-1], )).get())
   





    pool.close() # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
    pool.join() # 等待进程池中的所有进程执行完毕
    # print ("Sub-process(es) done.")
  
    # for res in results:
    #     print (res.get())
    print(len(results),'并发匹配到的结果数量.')

    print('并发查询时间',time.time()-t)



print('下面测试更高的并发.')
from multiprocessing import Process
import multiprocessing
import os
if 1:
    print('cpushulaign',os.cpu_count())
    cpu_c=os.cpu_count()
    t=time.time()
    pool = multiprocessing.Pool(processes=cpu_c) # 创建4个进程
    results = []
    bingfa=3
    p1=len(wenben)//bingfa
    p2=p1*2


    results+=(pool.apply_async(gfw.pipei_longest, (wenben[:p1], )).get())
    results+=(pool.apply_async(gfw.pipei_longest, (wenben[p1:p2], )).get())
    results+=(pool.apply_async(gfw.pipei_longest, (wenben[p2:], )).get())
    results+=(pool.apply_async(gfw.pipei_longest, (wenben[p1-max_token_len-1:p1+max_token_len-1], )).get())
    results+=(pool.apply_async(gfw.pipei_longest, (wenben[p2-max_token_len-1:p2+max_token_len-1], )).get())





    pool.close() # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
    pool.join() # 等待进程池中的所有进程执行完毕
    # print ("Sub-process(es) done.")
  
    # for res in results:
    #     print (res.get())
    print(len(results),'并发匹配到的结果数量.')

    print('并发查询时间',time.time()-t)


#=trie树资料:======https://maimai.cn/article/detail?fid=1390986695&efid=n4cfuX764RO4_UAMy84PRQ    