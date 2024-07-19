from dataclasses import dataclass
import re

@dataclass
class Parse:
    def parseMan(self, file: str) -> dict:
        """
        解析man手册
        
        1、匹配man手册的标题，格式：位于行起始，一个或多个大写字母+任意字符
        2、将man手册按标题分割成列表，提取段落内容
        """
        data = {}
        kp = r"^([A-Z]+.*)"
        pattern = re.compile(kp, re.MULTILINE)
        with open(file, 'r') as f:
            lines = f.readlines()
            start = 0
            for index, line in enumerate(lines):
                match = re.search(r'^NAME.*',line)
                if match:
                    start = index - 1
                    break

            text = ''.join(lines[start:-1]) # 将man手册头尾部分去除
            res = pattern.findall(text) # 匹配所有标题
            titles = [repr(i.strip())[1:-1] for i in res]
            kp2 = "("+"|".join(titles)+")"
            # 以标题分割
            section = re.split(r"\n"+kp2+r"\n", text)
            section = [i for i in section if i is not None]
            for title in titles:
                if title in section and section.index(title) < len(section) - 1:
                    if title == 'OPTIONS':
                        data[title] = section[section.index(title)+1]
                        continue
                    
                    data[title] = self.parseContent(section[section.index(title)+1])
        return data

    def parseOpt(self, text:str) -> list:
        """
        解析man手册的OPTIONS
        """
        kp = r'\n\s*\n'
        res = re.split(kp, text)
        result = []

        # 初始化一个变量来存储上一个以短横线开头的元素
        pre = None

        for item in res:
            if item.strip().startswith("-"):
                # 如果当前元素以短横线开头，将其添加到结果列表中
                result.append(item)
                pre = len(result) - 1
            elif pre is not None:
                # 如果当前元素不以短横线开头，但上一个元素以短横线开头，
                # 将当前元素拼接到上一个元素上
                result[pre] += item

        return [i.strip() for i in result]
    
    def parseContent(self, text:str):
        """
        将内容段落划分为一行
        """
        # 提取段落，以空行将内容段落分隔
        paragraphs = re.split(r'\n\s*\n', text.strip())

        # 清除段落\n字符，并将1个以上的空白字符换成空格
        clearned = [re.sub(r'\s+', ' ', p.replace('\n', '')).strip() for p in paragraphs]
        
        return "\n\n".join(clearned)
    
    def splitContent(self, text:str):
        """
        将内容以空行划分为多行
        """
        # 提取段落，以空行将内容段落分隔
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        return paragraphs