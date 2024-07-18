# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/21/2022 4:35 PM
@Description: Description
@File: match_ids.py
"""
import random


class Match:

    def __init__(self, v1, v2):
        self.new_value = v1
        self.replace_value = v2

    def handle(self, filed, from_field, is_combine=False):
        if not is_combine:
            if len(self.new_value) == len(self.replace_value) == 1:
                new_value = list(self.new_value[0].values())[0]
                replace_value = list(self.replace_value[0].values())[0]
                return new_value != replace_value and {new_value: replace_value} or dict()
            else:
                raise Exception(f"is_combine error. new_value: {self.new_value}. replace_value: {self.replace_value}")
        new_value_len = len(self.new_value)
        # new_value_code_label = "code"
        # new_value_id_label = "id"
        # replace_code_label = "code"
        # replace_id_label = "id"
        new_value_id_label, new_value_code_label = filed.split(",")
        replace_id_label, replace_code_label = from_field.split(",")
        replace_id = "replace_id"
        replace_code = "replace_code"
        used = 'used'
        count = 0
        result = list()
        for new_value in self.new_value:
            new_value[replace_id] = -1
            new_value[replace_code] = ""
            for replace_value in self.replace_value:
                if new_value[new_value_code_label] == replace_value[replace_code_label]:
                    if new_value[new_value_id_label] != replace_value[replace_id_label]:
                        result.append({new_value_id_label: new_value[new_value_id_label],
                                       new_value_code_label: new_value[new_value_code_label],
                                       replace_id: replace_value[replace_id_label],
                                       replace_code: replace_value[replace_code_label]})
                    replace_value[used] = True
                    count += 1
                    break
            else:
                result.append({new_value_id_label: new_value[new_value_id_label],
                               new_value_code_label: new_value[new_value_code_label]})
        tmp_count, result = self.fuzzy_match(result, filed, from_field)
        count += tmp_count
        if new_value_len == count:
            pass
        elif new_value_len < count:
            raise Exception("new_value_len < count.")
        else:
            for new_value in result:
                for replace_value in self.replace_value:
                    if not new_value.get(replace_id, False) and not replace_value.get(used, False):
                        new_value[replace_id] = replace_value[replace_id_label]
                        new_value[replace_code] = replace_value[replace_code_label]
                        replace_value[used] = True
                        break
        result = [(item.get(new_value_id_label), item.get(replace_id), item.get(new_value_code_label),
                   item.get(replace_code)) for item in result if item.get(replace_id) is not None]
        rebuild_res = list()
        if result:
            if len(result) == 1:
                return result
            old_ids = [i[1] for i in result]
            self.sort_by_old_id(result, old_ids, rebuild_res)
        return rebuild_res

    def sort_by_old_id(self, items, old_items, pass_result):
        """
        由于在数据库执行update语句，新的id可能在旧的id已存在，需要先修改旧的id，再赋给新的id
        """
        fail_result = list()
        for item in items:
            old = item[1]
            new = item[0]
            if old == new:
                pass_result.append(item)
                continue
            if new not in old_items:
                old_items.append(new)
                old_items.remove(old)
                pass_result.append(item)
            else:
                fail_result.append(item)
        if fail_result:
            random.shuffle(fail_result)
            return self.sort_by_old_id(fail_result, old_items, pass_result)

    def fuzzy_match(self, result, filed, from_field):
        new_value_id_label, new_value_code_label = filed.split(",")
        replace_id_label, replace_code_label = from_field.split(",")
        replace_id = "replace_id"
        replace_code = "replace_code"
        used = 'used'
        count = 0
        for new_value in result:
            for replace_value in self.replace_value:
                if not new_value.get(replace_id, False) and not replace_value.get(used, False):
                    if replace_value[replace_code_label] is not None and new_value[new_value_code_label] in replace_value[replace_code_label]:
                        new_value[replace_id] = replace_value[replace_id_label]
                        new_value[replace_code] = replace_value[replace_code_label]
                        replace_value[used] = True
                        count += 1
                        break
        return count, result
