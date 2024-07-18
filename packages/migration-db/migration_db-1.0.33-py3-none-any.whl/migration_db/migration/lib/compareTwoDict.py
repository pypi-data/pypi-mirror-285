"""
Created on Nov 8, 2020

@author: xiaodong.li
"""

from enum import Enum, unique


@unique
class CompareConst(Enum):
    equal = '='  # Equal value
    diff = '!'  # Value varies
    more = '+'  # Unique key
    lack = '-'  # Missing key


class CompareTwoDict(object):

    def __init__(self, dict1, dict2):
        self.dict1 = dict1
        self.dict2 = dict2
        self.key_list = list(set(list(dict1.keys()) + list(dict2.keys())))
        self.result = {}

    def compare(self, key):
        v1 = self.dict1.get(key)
        v2 = self.dict2.get(key)
        if (type(v1) == dict) and (type(v2) == dict):
            if v1 == v2 == dict():
                self.result[key] = CompareConst.equal.value
            else:
                self.result[key] = CompareTwoDict(v1, v2).main()
        else:
            self.result[key] = self.diff(v1, v2)

    @staticmethod
    def diff(v1, v2):
        if (v1 is not None) and (v2 is not None):
            if isinstance(v1, str) and isinstance(v2, str):
                def replace_str(string):
                    return string.replace("\n", "").replace("; ", ";").replace(" ;", ";")

                v1, v2 = replace_str(v1), replace_str(v2)
            if v1 == v2:
                return CompareConst.equal.value
            else:
                return CompareConst.diff.value
        elif (v1 is None) and (v2 is None):
            return CompareConst.equal.value
        elif v1 is not None:
            return CompareConst.more.value
        else:
            return CompareConst.lack.value

    def main(self):
        for k in self.key_list:
            self.compare(k)
        return self.result


class FilterDict(object):

    def __init__(self, dict1):
        self.dict1 = dict1
        self.key_list = list(dict1.keys())
        self.result = {}

    def filter(self, key):
        v1 = self.dict1.get(key)
        if type(v1) == dict:
            if FilterDict(v1).main():
                self.result[key] = FilterDict(v1).main()
        else:
            if v1 in ['-', '+', '!']:
                self.result[key] = v1

    def main(self):
        for key in self.key_list:
            self.filter(key)
        return self.result
