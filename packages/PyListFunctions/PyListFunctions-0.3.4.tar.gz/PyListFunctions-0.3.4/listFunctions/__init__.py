# Author: BL_30G
# Version: 0.3Fixed(2)
import gc


def tidy_up_list(lst: list, bool_mode: bool = False, eval_mode: bool = False, float_mode: bool = False,
                 int_mode: bool = False, none_mode: bool = False) -> list:
    """
    A function to tidy up list(●ˇ∀ˇ●)

    :param bool_mode: If you want to turn such as 'True' into True which it is in this list, you can turn on 'bool_mode' (～￣▽￣)～
    :param eval_mode: If you want to turn such as '[]' into [] which it is in this list, you can turn on 'eval_mode' (￣◡￣)
    :param lst:put list which you need to sorting and clean（￣︶￣）
    :return: the perfect list  ( ´◡` )

    """

    # 判断是否是list类型，否则返回形参原本值
    if type(lst) is not list and not (len(lst) <= 0):
        return lst

    bool_mode = bool(bool_mode)
    eval_mode = bool(eval_mode)
    float_mode = bool(float_mode)
    int_mode = bool(int_mode)

    _lst_types: list = []
    _point_j: int = 0
    _point_l: list = []
    _str_app_l: list = []
    _type_content: dict = {'str': [], 'int': [], 'float': [], 'lst': [], 'dic': [], 'set': [], 'tuple': [],
                           'complex': [],
                           'None': []}

    # 保存原有特殊变量原本值
    for i in range(len(lst)):
        if isinstance(lst[i], str) and (lst[i] not in _type_content['str']):
            _type_content['str'].append(lst[i])

        if isinstance(lst[i], int) and (lst[i] not in _type_content['int']):
            _type_content['int'].append(lst[i])

        if isinstance(lst[i], float) and (lst[i] not in _type_content['float']):
            _type_content['float'].append(lst[i])

        if type(lst[i]) is None and (lst[i] not in _type_content['None']):
            _type_content['None'].append(lst[i])

        if type(lst[i]) is list and (lst[i] not in _type_content['lst']):
            _type_content['lst'].append(lst[i])

        if type(lst[i]) is dict and (lst[i] not in _type_content['dic']):
            _type_content['dic'].append(lst[i])

        if type(lst[i]) is set and (lst[i] not in _type_content['set']):
            _type_content['set'].append(lst[i])

        if type(lst[i]) is tuple and (lst[i] not in _type_content['tuple']):
            _type_content['tuple'].append(lst[i])
        if type(lst[i]) is complex and (lst[i] not in _type_content['complex']):
            _type_content['complex'].append(lst[i])

        lst[i] = str(lst[i])

    # 排序+去除重复值
    lst = list(set(lst))
    for i in range(len(lst)):
        lst[i] = str(lst[i])
    lst = sorted(lst, key=str.lower)

    # 判断列表值是何类型1
    for i in range(len(lst)):
        _point_l.append([])
        _str_app_l.append([])
        for j in lst[i]:
            if 48 <= ord(j) <= 57:
                continue
            elif j == '.':
                if not _point_l[i]:
                    _point_l[i].append(True)
                else:
                    continue
            else:
                if not _str_app_l[i]:
                    _str_app_l[i].append(True)
                else:
                    continue

    # 判断列表值是何类型2
    for i in range(len(_point_l)):
        if True in _str_app_l[i]:
            _lst_types.append('str')
        elif True in _point_l[i] and _str_app_l[i] == []:
            for j in range(len(lst[i])):
                if lst[i][j] == '.':
                    _point_j += 1
            if _point_j == 1:
                _lst_types.append('float')
                _point_j = 0
            else:
                _lst_types.append('str')
                _point_j = 0
        else:
            _lst_types.append('int')

    # 转换类型
    for i in range(len(_lst_types)):
        if _lst_types[i] == 'str':
            if eval_mode:
                try:
                    lst[i] = eval(lst[i])
                except:
                    pass
            pass
        try:
            if _lst_types[i] == 'float':
                lst[i] = float(lst[i])
            if _lst_types[i] == 'int':
                lst[i] = int(lst[i])
        except ValueError:
            pass

    # code burger(bushi     (将收集到的特殊数据插入回列表)
    for i in range(len(_type_content['complex'])):
        lst.remove(str(_type_content['complex'][i]))
        lst.append(_type_content['complex'][i])
    for i in range(len(_type_content['tuple'])):
        lst.remove(str(_type_content['tuple'][i]))
        lst.append(_type_content['tuple'][i])
    for i in range(len(_type_content['lst'])):
        lst.remove(str(_type_content['lst'][i]))
        lst.append(_type_content['lst'][i])
    for i in range(len(_type_content['set'])):
        lst.remove(str(_type_content['set'][i]))
        lst.append(_type_content['set'][i])
    for i in range(len(_type_content['dic'])):
        lst.remove(str(_type_content['dic'][i]))
        lst.append(_type_content['dic'][i])

    if bool_mode:
        for i in range(len(lst)):
            if lst[i] == 'True':
                lst[i] = bool(1)
            elif lst[i] == 'False':
                lst[i] = bool(0)

    del _lst_types, _point_j, _point_l, _str_app_l, _type_content
    gc.collect()

    return lst


def deeply_tidy_up_list(lst: list) -> list:
    """
    This Function can search list elements and tidy up it too(‾◡◝)

    :param lst:put list which you need to sorting and clean（￣︶￣）
    :return: the perfect list  ( ´◡` )
    """

    if type(lst) is not list:
        return lst

    _j: int = 0
    lst = tidy_up_list(lst)

    for _i in lst:
        if type(_i) is list:
            lst[_j] = deeply_tidy_up_list(_i)
        _j += 1
    return lst


def bubble_sort(lst: list) -> list:
    """
    A simple bubble sort function ~(￣▽￣)~*\n
    (elements cannot be 'str')

    :param lst:
    :return: The sorted list
    """

    if type(lst) is not list:
        return lst

    _i: int = 0

    for _i in range(len(lst)):
        if isinstance(lst[_i], int) or isinstance(lst[_i], float):
            continue
        else:
            return lst

    lst_len = len(lst)
    for _i in range(lst_len):
        for _j in range(lst_len - 1 - _i):
            if lst[_j + 1] <= lst[_j]:
                lst[_j], lst[_j + 1] = lst[_j + 1], lst[_j]

    del _i, _j
    gc.collect()

    return lst


# This Function is Finished!~ (*^▽^*)
def replace_str(string: str, __c: str, __nc: str, num=0) -> str:
    """
    Change the character in the string to a new character, but unlike "str.replace()", num specifies the number of original strs that that need to change (not the maximum times of changes)
    :param string: The string
    :param __c: Original character
    :param __nc: New character
    :param num: How many character(default is Zero(replace all Eligible character))
    :return:
    """

    if len(str(__c)) == 0:
        raise ValueError("Original character cannot be empty!")

    if len(__c) == 1 and __c not in list(str(string)):
        return string

    string = str(string)
    lst_string = list(string)

    if len(__c) == 1 and num == 0:
        for _i in range(len(lst_string)):
            try:
                if lst_string[_i] == __c:
                    if len(__nc) == 0:
                        lst_string.pop(_i)
                    else:
                        lst_string[_i] = __nc
            except IndexError:
                pass
        new_string = str("".join(lst_string))
        del _i, lst_string
        gc.collect()
        return new_string

    elif len(__c) == 1 and num != 0:
        times: int = 0
        _i: int = 0
        for _i in range(len(lst_string)):
            if lst_string[_i] == __c:
                times += 1
                if times == num:
                    break
        if times != num:
            return string
        if len(__nc) == 0:
            lst_string.pop(_i)
        else:
            lst_string[_i] = __nc
        new_string = str("".join(lst_string))
        del _i, times, lst_string
        gc.collect()
        return new_string

    elif len(__c) > 1 and num == 0:
        temp_bool: bool = False
        for _i in range(len(lst_string)):
            if _i == len(lst_string)-len(__c):
                break
            temp = lst_string[_i:len(__c)+_i:]
            temp = str("".join(temp))
            if temp == __c:
                temp2 = list(__nc)
                for _j in range(len(__nc)):
                    if len(__nc) > len(__c):
                        if _j >= len(__c):
                            lst_string.insert(int(_i + _j), temp2[_j])
                        else:
                            lst_string[_i + _j] = temp2[_j]
                    else:
                        temp_bool = True
                        break
                if temp_bool and len(__nc) != 0:
                    for _j in range(len(__c) - len(__nc)):
                        lst_string.pop(_i)
                    for _j in range(len(__nc)):
                        lst_string[_i + _j] = temp2[_j]
                elif len(__nc) == 0:
                    for _j in range(len(__c)):
                        lst_string.pop(_i)
        new_string = str("".join(lst_string))
        try:
            del _i, temp, temp2, temp_bool
            del _j
        except UnboundLocalError:
            pass
        gc.collect()
        return new_string

    elif len(__c) > 1 and num != 0:
        temp_bool: bool = False
        times: int = 0
        _i: int = 0
        for _i in range(len(lst_string)):
            if _i == len(lst_string)-len(__c) or times >= num:
                break
            temp = lst_string[_i:len(__c)+_i:]
            temp = str("".join(temp))
            if temp == __c:
                times += 1
        if times != num:
            return string
        temp2 = list(__nc)
        _i -= 1
        for _j in range(len(__nc)):
            if len(__nc) > len(__c):
                if _j >= len(__c):
                    lst_string.insert(int(_i + _j), temp2[_j])
                else:
                    lst_string[_i + _j] = temp2[_j]
            else:
                temp_bool = True
                break
        if temp_bool and len(__nc) != 0:
            for _j in range(len(__c) - len(__nc)):
                lst_string.pop(_i)
            for _j in range(len(__nc)):
                lst_string[_i + _j] = temp2[_j]
        elif len(__nc) == 0:
            for _j in range(len(__c)):
                lst_string.pop(_i)
        new_string = str("".join(lst_string))
        try:
            del _i, temp, temp2, temp_bool, times
            del _j
        except UnboundLocalError:
            pass
        gc.collect()
        return new_string
