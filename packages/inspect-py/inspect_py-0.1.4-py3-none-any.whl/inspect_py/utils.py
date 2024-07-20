
# get_all_functions_names
def obj_function(Classobj,print_list=False):
    method_list = [attribute for attribute in dir(Classobj) if callable(getattr(Classobj, attribute)) and attribute.startswith('__') is False]
    if print_list:
        print(method_list)
    return method_list

def obj_property(Classobj,print_list=False):
    property_list = [attribute for attribute in dir(Classobj) if not callable(getattr(Classobj, attribute)) and attribute.startswith('__') is False]
    if print_list:
        print(property_list)
    return property_list


def code_text(filename = ""):
    # little tested
    # no functions needed
    ans = []
    if filename == "":
        _filename = __file__
    with open(_filename) as myFile:
        for num, line in enumerate(myFile, 1):
            ans.append(line)
    return ans

def search_code_index(search, filename = ""):
    # little tested
    # need code_text
    ans = []
    if isinstance(search,str):
        code = code_text(filename)
        for i,line in enumerate(code):
            if search in line:
                ans.append(i+1)
    return ans

def search_code_line(search, filename = ""):
    # little tested
    # need code_text
    ans = []
    if isinstance(search,str):
        code = code_text(filename)
        for i,line in enumerate(code):
            if search in line:
                ans.append(line)
    elif isinstance(search,list):
        for x in search:
            temp = search_code_line(x, filename)
            ans.append(temp)

    return ans

def get_var_name(variable_name,filename = ""):
    # little tested
    # need code_text,search_code_line
    if isinstance(variable_name,str):
        code_line = search_code_line(variable_name,filename)
        _code_line = []

        for line in code_line:
            if (" " in line):
                if line.split(" ")[0] == variable_name:
                    _code_line.append(line)

        _code_line = _code_line[0]
        ans = _code_line.split("=")[1].strip()

    elif isinstance(variable_name,list):
        ans = []
        for variable in variable_name:
            temp = get_var_name(variable,filename)
            ans.append(temp)

    return ans