import inspect


def D_Get_FuncName():
    frame = inspect.currentframe()
    temp = inspect.getouterframes(frame)
    func_name = temp[1].function
    return func_name

def what_name_is_this(): 
    frame = inspect.currentframe()
    return inspect.getframeinfo(frame).function

def what_name_is_this02(): 
    func_name = D_Get_FuncName()
    print(func_name)
    return func_name

def get_func_name():
    print(what_name_is_this02())

# get_func_name()
get_func_name()