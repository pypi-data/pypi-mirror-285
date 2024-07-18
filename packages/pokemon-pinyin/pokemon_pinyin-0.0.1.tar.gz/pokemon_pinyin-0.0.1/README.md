## 字体

默认需要下载simhei字体

也可以使用你自己喜欢的字体,只需要在main.py里面修改对应的字体路径即可

## 使用

```shell
# 绘画1-10号（包含10）
ppinyin 1..10
# 绘画1 3 5 7号
ppinyin 1,3,5,7
# 绘画绘画1-10号，过滤某个字只包含m,a
ppinyin 1..10 -fb l,v

```


## package

Publish package
```
python -m build
```

Development mode
```
pip install --editable .
```