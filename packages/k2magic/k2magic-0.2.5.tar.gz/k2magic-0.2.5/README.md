# k2magic
K2Magic是K2Assets提供的数据分析开发包（以下简称SDK），用于简化Python里访问各类数据库的操作。

以下内容面向此SDK开发者，普通用户不需要了解（SDK使用方法见QUICKSTART.md）。

### 测试
执行测试用例，注意需要确保各个目标数据库可用：
```
python -m pytest
```

生成测试报告：
```
pip install pytest-html
python -m pytest --html=report.html
```

### 打包
在`setup.py`中修改当前版本号，然后用下面的命令将源码打成wheel包：
```
python setup.py clean --all
python setup.py sdist bdist_wheel
```

### 发布

发布到`pypi.org`，按提示输入自己的api token（或预先写在$HOME/.pypirc里则不需要输入）：
```
twine upload dist/*
```

发布到k2a环境自带的私有pypi，用户名和密码一般都为空：
```
twine upload --repository-url http://dev.kstonedata.k2:18080/ dist/*
```

### 生成使用文档

用以下命令生成html格式的使用文档`dataframe_db.html`：
```
pydoc -w k2magic\dataframe_db.py
```