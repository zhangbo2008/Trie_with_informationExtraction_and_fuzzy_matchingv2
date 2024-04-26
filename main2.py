#!/usr/bin/env python   Trie树在信息抽取上的应用. 并发加速.
# -*- coding:utf-8 -*-    
#  添加信息抽取模式.(也就是光抽取完,还要进行标注.) # keywords_ie里面每一行都是key,cat的中间空2个空格. 
# 返回的区间指的是左闭右闭的闭区间.
from collections import defaultdict
import re

__all__ = ['NaiveFilter', 'BSFilter', 'DFAFilter']
__author__ = 'observer'
__date__ = '2012.01.05'




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

#=========删除成功返回1, 删除失败返回0.(因为有可能你要删除的东西在树里面就不存在.)
    def delete(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains#代表当前层的字典.

        #进入到树的里层.
        for i in range(len(chars)): #对字符串里面每一个字符建立trie树.
            if chars[i] in level: #如果当前这个汉子存在,那么就level进入下一层.
                level = level[chars[i]]
            else:
             
                return 0#========说明字典中没有这个word,删除失败.
        #如果最里层是
        # if i == len(chars) - 1: # 说明已经有过这个字符串,那么我们就写入结束符即可.
        if self.delimit in level:
                del level[self.delimit]
                return 1
        return 0
            








        pass










    def add(self, keyword,cat):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        cat=cat.lower().strip()
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
                last_level[last_char] = {self.delimit: cat} #然后写入结束符.
                break
        if i == len(chars) - 1: # 说明已经有过这个字符串,那么我们就写入结束符即可.
            level[self.delimit] = cat

    def parse(self, path):
        with open(path,encoding='utf-8') as f:
            for line in f:
                line=line.strip().split('  ')
                keyword,cat=line[0],line[1]
                self.add(keyword,cat)

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
        outdex=[] #输出key索引
        outkey=[]
        outcat=[] #输出cat
        
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
                        outdex.append([old_start,start])
                        outkey.append(message[old_start:start+1])
                        outcat.append(level[char][self.delimit])
                        break
                else:#如果char不存在,
                    ret.append(message[start])
                    break
            else: # for else: 上面的break都没触发,就走这个else. 说明一直进入到了最后一层.并且里面一直都没有结束符!!!!!说明当前位置字符串只是一个前缀,不能成为单词.所以不是我们要的.
                ret.append(message[start])

            start += 1#=========这里也是可以直接跳过.

        return outdex,outkey,outcat



#最长匹配, 尽量找跟字典中最长的匹配, 尽可能让找到的字符串最长!!!!!!!!!!!!!!!!!!!性能会比上面的低很多!
    def pipei_longest(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        outdex=[] #输出key索引
        outkey=[]
        outcat=[] #输出cat
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
                        level = level[char]# 一样进入
                        old_start=start
                        start2 =start+ step_ins - 1 #保证找到的不会重叠.


                else:#如果char不存在,
                    # ret.append(message[start])
                    break

            #=================遍历玩了当前字符为起始字符的全排列.
            if start2!=None:
                outdex.append([start, start2 ])
                outkey.append(message[start:start2+1])
                outcat.append(level[self.delimit])
            if start2!=None:
                start=start2+1 #因为已经匹配最长了,直接跳过即可!!!!!!!!!!
            else:
                start += 1

        return outdex,outkey,outcat










#============这个性能太慢,  2024-04-26,13点36 不打算继续更新了. 也不是主流的需求, 可以根据自己需要自己修改.
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













def test_first_character():
    gfw = DFAFilter()
    gfw.add("1989年")
    assert gfw.filter("1989", "*") == "1989"



if 1:
        gfw = DFAFilter()  # 本质就是中文trie树的实现. 很简单.
        gfw.parse("keywords_ie")
        print('if you are confused withe the 3 method you can set this if =true, and run the code below')
      


        print('最短匹配关键字查询算法')
        print(gfw.pipei_shortest("啊"))
        print(gfw.pipei_shortest("啊啊啊啊"))
        print(gfw.pipei_shortest("嗷嗷"))
        print(gfw.pipei_shortest("苹果干"))
        print(gfw.pipei_shortest("苹果干什"))
        print(gfw.pipei_shortest("苹果干什么苹果干什么"))

        print('删除节点啊再最短查询')
        print(gfw.delete('啊'))
        print(gfw.pipei_shortest("啊"))
        print(gfw.pipei_shortest("啊啊啊啊"))
        print(gfw.pipei_shortest("嗷嗷"))
        print(gfw.pipei_shortest("苹果干"))
        print(gfw.pipei_shortest("苹果干什"))
        print(gfw.pipei_shortest("苹果干什么苹果干什么"))
        print('删除节点啊啊啊啊再最短查询')
        print(gfw.delete('啊啊啊啊'))
        print(gfw.pipei_shortest("啊"))
        print(gfw.pipei_shortest("啊啊啊啊"))
        print(gfw.pipei_shortest("嗷嗷"))
        print(gfw.pipei_shortest("苹果干"))
        print(gfw.pipei_shortest("苹果干什"))
        print(gfw.pipei_shortest("苹果干什么苹果干什么"))
        print('删除节点苹果干再最短查询')
        print(gfw.delete('苹果干'))
        print(gfw.pipei_shortest("啊"))
        print(gfw.pipei_shortest("啊啊啊啊"))
        print(gfw.pipei_shortest("嗷嗷"))
        print(gfw.pipei_shortest("苹果干"))
        print(gfw.pipei_shortest("苹果干什"))
        print(gfw.pipei_shortest("苹果干什么苹果干什么"))
        print('最长查询')
        print(gfw.pipei_longest("啊"))
        print(gfw.pipei_longest("啊啊啊啊"))
        print(gfw.pipei_longest("嗷嗷"))
        print(gfw.pipei_longest("苹果干"))
        print(gfw.pipei_longest("苹果干什"))
        print(gfw.pipei_longest("苹果干什么苹果干什么"))
        