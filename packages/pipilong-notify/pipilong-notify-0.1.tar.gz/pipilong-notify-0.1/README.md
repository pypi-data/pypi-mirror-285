# 钉钉webhook扩展包

## 使用

```python
from notification.template import Text
from notification.dingTalk import DingTalk
text = Text(content="你好啊")

DingTalk().notify(text)


```