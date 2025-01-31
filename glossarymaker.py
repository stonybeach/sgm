from collections import Counter
import re, requests, os, html, lxml.html

class glossarymaker:

    __kata_finder = re.compile('[\u30a1-\u30fa\u30fc-\u30fe]+')
    __site_url = 'https://ncode.syosetu.com/'
    __headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept-Languages": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br"
    }
    __encoding = 'utf-8'
    __counter = Counter()
    __glossary = {}

    def count_page_kata(self, novel, page):
        url = self.__site_url + novel + '/' + str(page)
        response = requests.get(url, headers=self.__headers)
        if not response.ok:
            raise Exception('Response error')
        tree = lxml.html.fromstring(response.text.encode(self.__encoding))
        title_elem = tree.xpath('//h1')[0]
        title_text = title_elem.text_content()
        self.__counter.update(self.__kata_finder.findall(title_text))
        para_elems = tree.xpath('//div[@class="p-novel__body"]//p')
        count = 0
        for para_elem in para_elems:
            para_text = para_elem.text_content().strip()
            if len(para_text) > 0:
                self.__counter.update(self.__kata_finder.findall(para_text))
                count += 1
        print("Processed " + str(count) + " paragraphs from "+ url)

    def count_novel_kata(self, novel, start, end):
        for page in range(start, end+1):
            try:
                self.count_page_kata (novel, page)
            except:
                break

    def get_counts(self):
        return dict(self.__counter)

    def get_top(self, number):
        return dict(self.__counter.most_common(number))

    def load_dict(self, dict_file):
        self.__kata_dict = set()
        with open(dict_file) as file:
            for line in file:
                self.__kata_dict.add(line.strip())

    def del_simple(self, number):
        for key in list(self.__counter.keys()):
            if len(key) < number:
                del self.__counter[key]

    def del_kata_in_dict(self):
        for key in list(self.__counter.keys()):
            if key in self.__kata_dict:
                print("Found in dict: " + key)
                del self.__counter[key]
        for key in list(self.__counter.keys()):
            for item in self.__kata_dict:
                if len(item) > 2 and len(key)-len(item) > 2 and key.startswith(item):
                    remaining = key[len(item):]
                    if remaining in self.__kata_dict:
                        print("Found in dict (composite): " + key)
                        del self.__counter[key]

    def del_least(self, number):
        for k,v in dict(self.__counter).items():
            if v < number:
                del self.__counter[k]

    def del_current(self, file_name):
        with open(file_name) as file:
            for line in file:
                if len(line.strip()) > 0:
                    kv = line.strip().split('=>')
                    key = kv[0].strip()
                    value = kv[1].strip()
                    self.__glossary[key] = value
                    if key in self.__counter:
                        #print("Added from current: " + key + " = " + value)
                        del self.__counter[key]

    def is_sound(self, text):
        return (len(text)>2 and len(text.replace(text[0],''))==0) \
            or text.endswith('~') or text.endswith('～') \
            or text.endswith('-') or text.endswith('—') \
            or text.endswith('！') or text.endswith('!')

    def use_sakura(self, server):
        keys = list(self.__counter.keys())
        keys.sort()
        for i in range(0, len(keys), 10):
            self.use_sakura_batch(server, keys[i:i+10])

    def use_sakura_batch(self, server, keys):
        url = server + "/v1/chat/completions"
        i = 1
        ja_text = ""
        mapping = {}
        for key in keys:
            ja_text += str(i) + "." + key + "\n"
            mapping[i] = key
            i += 1
        body = {
            "model":"",
            "messages":[
                {
                    "role":"system",
                    "content":"你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
                }, {
                    "role":"user",
                    "content":"将下面的日文文本翻译成中文：" + ja_text
                }],
            "temperature":0.1,
            "top_p":0.3,
            "max_tokens":100,
            "frequency_penalty":0
        }
        print("Calling Sakura at: " + url + " for " + str(i-1) + " items")
        response = requests.post(url, json=body)
        result = response.json()
        if "choices" in result:
            choice1 = result["choices"][0]
            if "message" in choice1:
                lines = choice1["message"]["content"]
                print (lines)
                for line in lines.split('\n'):
                    kv = line.split('.')
                    if len(kv) == 2:
                        index = int(kv[0])
                        key = mapping[index]
                        value = kv[1].strip()
                        if len(value) > 0 and not self.is_sound(value):
                            self.__glossary[key] = value
                        #print("Adding " + key + " = " + value)

    def get_glossary(self):
        result = ""
        output = list(self.__glossary.items())
        output.sort()
        for k,v in output:
            result += k + " => " + v + "\n"
        return result
