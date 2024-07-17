
class GlobalObject(object):
    """
    全局变量对象
    如果g中的某个变量不想被序列化, 可以让变量以 '__' 开头, 在序列化时会被忽略

    要在Python中通过pickle序列化自定义类，需要满足以下两个条件：

    1. 自定义类必须实现__getstate__()和__setstate__()方法。
        1) getstate() 方法应该返回一个包含对象状态的字典。这个字典将是 pickle 用于序列化对象的内容。
        2) setstate() 方法接收一个字典作为参数，并使用它来恢复对象状态。
    2. 自定义类必须是全局可访问的。

    """

    def __getstate__(self):
        return {name: getattr(self, name) for name in dir(self) if not name.startswith("__")}

    def __setstate__(self, state):
        # reset g
        for k, v in state.items():
            setattr(self, k, v)


# ---------------------------------------------------------
# 外部可以访问的列表
# ---------------------------------------------------------
__all__ = ["GlobalObject"]
__all__.extend([name for name in globals().keys() if name.startswith("get")])
