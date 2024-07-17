# PathLikeDict

借鉴 pathlib.Path 链式操作方式，简化深字典的操作。

## 安装

使用以下命令安装：

`pip install PathLikeDict`

## 使用

```python
import DeepDict

adict = {}
bdict = DeepDict(adict).path('a.b.c').set('d', 1).path(['e', 'f']).set('g', 2)
print(adict)
print(bdict)
# {'a': {'b': {'c': {'d': 1, 'e': {'f': {'g': 2}}}}}}
# {'g': 2}

bdict.path('wow').set(['a', 'b', 'c'], [3, 4, 5])
print(adict)
print(bdict)
# {'a': {'b': {'c': {'d': 1, 'e': {'f': {'g': 2, 'wow': {'a': 3, 'b': 4, 'c': 5}}}}}}}     
# {'a': 3, 'b': 4, 'c': 5}
```

## 贡献

欢迎提交 pull request 来改进 PathLikeDict。

## 许可

MIT
