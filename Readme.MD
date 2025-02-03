# 功能：

制作绿站小说翻译术语表，目前仅支持 ”小说家“ 网

# 安装

1. Git 复制此项目

2. 安装 python3 (只测试过 3.9)

3. 安装 python requirements:
```
pip3 install -r requirements.txt
```
# 使用方法

1. 制作一个配置文档，例如：
```
[syotesu]
novel = n9323jx # 小说家网的小说编号
start = 1 # 开始页数
end = 36  # 最后页数

[translation]
current_mapping_file = book/n9323jx_current.txt
# 当前的术语表文档，会保留及合并到新术语表
output_mapping_file = book/n9323jx_out.txt
# 新术语表储存文档
least_count = 2
# 最低出现次数，默认为 2，少于此次数的词语不会被包含
min_len = 3
# 最低字数，默认为 3，少于此字数的词语不会被包含
dict = JMdict_kata
# 日文字典，如果术语在此字典存在，则不输出，默认为 JMdict_kata
sakura_server = http://localhost:8080
# Sakura 翻译器 URL，默认为 http://localhost:8080
```
2. 下载原有的术语表，放在上述的 current_mapping_file 里

3. 打开 Sakura 翻译器

4. 执行 main.py，提供配置文档路径，例如：
```
python3 main.py example.ini
```

# 操作逻辑

1. 从小说家网站下载相关内容
2. 筛选片假名词语
3. 过滤掉出现太少的词语及太短的词语
4. 过滤掉日文字典已有的词语
5. 过滤掉当前术语表已经有的词语
6. 使用 Sakura 翻译词语
7. 导出新术语表
