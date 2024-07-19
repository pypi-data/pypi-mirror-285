# CellTasker

CellTasker是一个高效的任务调度和管理系统，它允许用户定义并行运行的任务，每个任务被视为一个'cell'。这些'cell'可以根据预定的时间表自动启动和管理，每个'cell'的状态都会被持续监控并在需要时进行更新。CellTasker提供了一种灵活且可靠的方式来处理并行任务，使任务管理和调度变得更加简单和高效。

## 安装

使用以下命令安装CellTasker：

`pip install CellTasker`

## 使用

首先，定义你的任务。每个任务都是一个'cell'，可以使用task函数来定义：

```python
from CellTasker.cell import task

@task(name='my_task', timerange='00:00:00 - 23:59:59', interval=60)
def my_task(change_status: callable):
    # 你的任务代码
    pass
```

然后，使用Controller来管理你的任务：

```python
from CellTasker.controller import Controller
import logging

aclog = logging.getLogger('CellTasker')
aclog.setLevel(logging.INFO)
controller = Controller(5)
controller.run()
```

## 贡献

欢迎提交pull request来改进CellTasker。

## 许可

MIT
