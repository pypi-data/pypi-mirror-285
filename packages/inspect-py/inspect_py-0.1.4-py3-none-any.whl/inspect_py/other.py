import inspect
def D_Get_FuncName():
    frame = inspect.currentframe()
    temp = inspect.getouterframes(frame)
    func_name = temp[1].function
    return func_name
def D_OffsetVal(direction):
    if direction in ['up']:
        row_offset = -1
        col_offset = 0
    if direction in ['down']:
        row_offset = 1
        col_offset = 0
    if direction in ['left']:
        row_offset = 0
        col_offset = -1
    if direction in ['right']:
        row_offset = 0
        col_offset = 1
    return [row_offset,col_offset]