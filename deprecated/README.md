# 准备
使用前请从 `config.example.json` 复制一份到 `config.json`，然后在 `config.json` 中填入灰机维基的机器人用户名、密码和机器人操作所需的 header（没有的话在群里找 Revela255 要）

记得安装依赖
```bat
pip install -r requirements.txt
```

运行解包工具：https://github.com/OceanUwU/sts2-exporter

# 使用
各种`update_xxx.py`用途都很直观就不说了

`find_duplicate.py`可以检查重复的 ID 和 name（中文名）
如果存在重复 ID，则需要修改其中一个的 image。目前重复 ID 只有 LOST_WISP，既是遗物又是事件
如果存在重复 name，则需要检查 wiki 的对应页面