# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2/4/2022 9:36 PM
@Description: Description
@File: build_update_sql.py
"""
import os
import re
import traceback

from common_utils.calc_time import calc_func_time
from common_utils.log import Logger
from .base import Base
from .handle_external_condition_mapping_data import handle_external_condition_mapping_data
from .handle_procedures import handle_procedures
from .handle_special_field import handle_special_table_field, judge_special_table_field, generate_sql_for_special_rule
from .handle_sql_statement import handle_sql_statement
from .handle_table_action import handle_actions
from .match_ids import Match
from .models.table_detail import ReplaceField, BuildSqlDto, FieldGroup
from ..db.admin_db import AdminDb
from ..db.base_db import BaseDb
from ..docs.template.parse import parse
from ..lib.constant import DataType, ValTypeEnum, AdminFieldEnum, OR_PLACEHOLDER, NEWLINE_PLACEHOLDER_PATTERN
from ..lib.handle_str import sql_escape_symbol
from ..lib.path import build_sql_file_parent_path


class BuildUpdateSQL(Base):

    def __init__(self, database, data_source, assigned_study_id=None, assigned_replace_study_id=None):
        Base.__init__(self, database, data_source, assigned_study_id)
        Base.init_args(self)
        self.val_type_mapping = dict()
        self.assigned_replace_study_id = assigned_replace_study_id
        self.all_tables = list()
        self.rel_mapping = dict()
        self.update_sql_file_path = None
        self.external_condition_fields_mapping = dict()
        self.table_field_mapping = dict()
        self.assigned_replace_study_name = None
        self.context = dict()
        self.init_args()

    def init_args(self):
        self.all_tables = BaseDb(self.app_db_route).get_all_tables()
        self.build_val_type_mapping()
        self.rel_mapping = {ValTypeEnum.STUDY_ID.code: ValTypeEnum.ASSIGNED_REPLACE_STUDY_ID.code}

    def build_val_type_mapping(self):
        params = dict()
        for member in ValTypeEnum.__members__.values():
            if member.val is not None:
                params.update({member.code: member.val})
        params.update({ValTypeEnum.STUDY_ID.code: self.study_id,
                       ValTypeEnum.SPONSOR_ID.code: self.sponsor_id,
                       ValTypeEnum.ENV_ID.code: self.env_id,
                       ValTypeEnum.ASSIGNED_REPLACE_STUDY_ID.code: self.assigned_replace_study_id,
                       ValTypeEnum.COMPANY_ID.code: self.company_id,
                       })
        self.val_type_mapping.update(params)

    def parse_fields(self, fields, code, comment):
        li = list()
        t = re.split(NEWLINE_PLACEHOLDER_PATTERN, fields)
        for i in t:
            if not i or judge_special_table_field(i):
                continue
            i = i.strip()
            table, field_name = i.split(".")
            if table not in self.all_tables or field_name not in self.table_field_mapping.get(table):
                continue
            replace_field = ReplaceField()
            replace_field.table = table
            replace_field.field = field_name
            replace_field.external_condition = self.get_condition(table, self.system_id, external=True, code=code,
                                                                  admin_comment=comment, field_name=field_name)
            li.append(replace_field)
        return li

    @calc_func_time
    def build(self, config_info=None, update_sql_dir=None):
        data = config_info.get('data')
        table_actions = config_info.get('table_actions') or list()
        sql_statement = config_info.get('sql_statement') or list()
        self.table_field_mapping = self.build_table_field_mapping(data, table_actions)
        self.external_condition_fields_mapping = config_info.get('external_condition_fields_mapping', {})
        build_sql_dto = BuildSqlDto()
        build_sql_dto.database = self.database
        build_sql_dto.replace_fields = list()
        for item in data:
            app_source_field = item.get("app_source_field")
            admin_source_field = item.get("admin_source_field")
            code = item.get("code")
            admin_field_id = item.get("id")
            fields = item.get("fields")
            data_type = item.get("data_type")
            comment = item.get("comment")
            # 捕获异常并打印至日志
            try:
                values = self.get_new_replace_values(app_source_field, admin_source_field, data_type,
                                                     {code: admin_field_id}, comment)
            except BaseException as e:
                Logger().error(str(e))
                traceback.print_exc()
                values = dict()
            replace_fields = self.parse_fields(fields, code, comment)
            if len(replace_fields) > 0:
                for new_value, replace_value in values.items():
                    if new_value == replace_value:
                        continue
                    field_group = FieldGroup()
                    field_group.data_type = data_type
                    field_group.new_value = new_value if data_type == DataType.int else f"\"{sql_escape_symbol(new_value)}\""
                    field_group.replace_value = replace_value if data_type == DataType.int else f"\"{sql_escape_symbol(replace_value)}\""
                    handle_external_condition_mapping_data(replace_fields, self.context.get(code).get(replace_value))
                    field_group.fields.extend(replace_fields)
                    build_sql_dto.replace_fields.append(field_group)
            procedures = handle_procedures(fields, values, self.all_tables, self.table_field_mapping)
            build_sql_dto.procedures.extend(procedures)
        build_sql_dto.table_actions = handle_actions(table_actions, self.all_tables, self.table_field_mapping)
        build_sql_dto.sql_statement = handle_sql_statement(sql_statement)
        if build_sql_dto.replace_fields or build_sql_dto.table_actions or build_sql_dto.procedures:
            build_sql_dto.replace_fields = sorted(build_sql_dto.replace_fields, key=lambda r: r.data_type, reverse=True)
            self.write_in_file(build_sql_dto, update_sql_dir)
        return self.update_sql_file_path

    @calc_func_time
    def write_in_file(self, build_sql_dto, update_sql_dir=None):
        sql = parse("update_id_template", build_sql_dto=build_sql_dto)
        if update_sql_dir is None:
            sql_file_parent_path = build_sql_file_parent_path(self.data_source.get("host", "tmp"))
        else:
            sql_file_parent_path = os.path.join(update_sql_dir, self.data_source.get("host", "tmp"))
        os.makedirs(sql_file_parent_path, exist_ok=True)
        self.update_sql_file_path = os.path.join(sql_file_parent_path, self.database + ".sql")
        with open(self.update_sql_file_path, "w", encoding="utf-8") as f:
            f.write(sql)

    def get_condition(self, table_name, system_id, external=False, code=None, admin_comment=None, field_name=None):
        """

        :param table_name:
        :param system_id:
        :param external:
        :param code:
        :param admin_comment:
        :param field_name: 用于排除重复field
        :return:
        """
        tmp_external_condition_fields = self.external_condition_fields_mapping.get(f"{system_id}_{table_name}", list())
        condition = list()
        # 按comment过滤数据
        external_condition_fields = list()
        for item in tmp_external_condition_fields:
            comment = item.get("comment")
            if comment is not None and comment != admin_comment:
                continue
            external_condition_fields.append(item)
        fields = list()
        if field_name is not None:
            fields.append(field_name)
        for index, external_condition_field in enumerate(external_condition_fields):
            if index == 0:
                condition.append(" ")
                condition.append("AND" if external else "WHERE")
            field_name = external_condition_field.get("field_name")
            # 排除重复field
            if field_name in fields:
                if len(external_condition_fields) == 1:
                    condition.pop()
                if index == len(external_condition_fields) - 1:
                    condition.pop()
                continue
            val_type = external_condition_field.get("val_type")
            val = self.val_type_mapping.get(val_type)
            connector = " " if "is" in str(val).lower() else "="
            if connector == "=" and type(val) is str and "@replace_value" not in val:
                val = "'{0}'".format(val)
            if external is True and connector != "=":
                condition.pop()
                continue
            if external is True and table_name == "eclinical_entry_form_item_record" and system_id == 8 and field_name == "uuid":
                # 针对PV的特殊逻辑
                connector = " IN "
                current_value = None
                if code == AdminFieldEnum.STUDY_ID.code:
                    current_value = self.assigned_replace_study_id
                elif code == AdminFieldEnum.STUDY_NAME.code:
                    current_value = self.assigned_replace_study_name
                if current_value is None:
                    condition.pop()
                    continue
                val = self.pv_eclinical_entry_form_item_record(current_value)
                if val is None:
                    condition.pop()
                    continue
            condition.append(f"{field_name}{connector}{val}")
            fields.append(field_name)
            if index != len(external_condition_fields) - 1:
                condition.append("AND")
        return " ".join(condition)

    @calc_func_time
    def get_new_replace_values(self, app_source_field, admin_source_field, data_type, admin_field_mapping,
                               admin_comment):
        # get replaced data // todo edc中role code可能修改过，可能出现同一id的多条数据
        app_items = list()
        app_filed = list()
        has_or_placeholder = False
        if app_source_field is not None and app_source_field:
            if OR_PLACEHOLDER in app_source_field:
                has_or_placeholder = True
                app_source_fields = app_source_field.split(OR_PLACEHOLDER)
            else:
                app_source_fields = [app_source_field]
            app_sql_list = list()
            for index, item in enumerate(app_source_fields):
                handled_special_table_field = handle_special_table_field(item)
                if handled_special_table_field is not None:
                    tmp_item = handled_special_table_field
                else:
                    tmp_item = item
                app_table, app_filed = tmp_item.split(".")
                condition = self.get_condition(app_table, self.system_id, admin_comment=admin_comment)
                if app_table not in self.all_tables or (
                        "," not in app_filed and app_filed not in self.table_field_mapping.get(app_table)):
                    return dict()
                query_field = app_filed
                if handled_special_table_field is not None:
                    query_field = generate_sql_for_special_rule(item)
                app_sql_list.append(f"SELECT DISTINCT {query_field} FROM {app_table}{condition}")
                if has_or_placeholder and index != len(app_source_fields) - 1:
                    app_sql_list.append("UNION")
            app_sql = " ".join(app_sql_list)
            app_items = BaseDb(self.app_db_route).fetchall(app_sql)
        else:
            for k, v in admin_field_mapping.items():
                v = self.val_type_mapping.get(self.rel_mapping.get(v))
                app_filed.append(k)
                app_items.append({k: v})
            app_filed = ",".join(app_filed)
        if not app_items:
            return dict()
        is_combine = True if "," in app_filed else False
        if is_combine and app_source_field is not None and has_or_placeholder is False:
            items = app_filed.split(",")
            handled_special_table_field = handle_special_table_field(app_source_field)
            if handled_special_table_field is not None:
                tmp_item = handled_special_table_field
            else:
                tmp_item = app_source_field
            app_table, app_filed = tmp_item.split(".")
            for item in items:
                if item not in self.table_field_mapping.get(app_table):
                    return dict()
        # get admin data
        admin_table, admin_filed = admin_source_field.split(".")
        condition = self.get_condition(admin_table, 1)
        admin_items = AdminDb(self.data_source).fetchall(f"SELECT {admin_filed} FROM {admin_table}{condition}")
        is_combine = (True if "," in admin_filed else False) and is_combine
        result = Match(admin_items, app_items).handle(admin_filed, app_filed, is_combine)

        # todo 维护mapping关系并缓存，后续使用
        mapping = dict()
        if is_combine:
            k = None
            for item in result:
                if data_type == DataType.int:
                    mapping.update({item[1]: item[3]})
                else:
                    mapping.update({item[3]: item[1]})
        self.context.update({list(admin_field_mapping.keys())[0]: mapping})

        if is_combine:
            if data_type == DataType.int:
                return {i[0]: i[1] for i in result}
            else:
                return {i[2]: i[3] for i in result}
        else:
            if admin_field_mapping.get(AdminFieldEnum.STUDY_NAME.code) == AdminFieldEnum.STUDY_NAME.id and result:
                self.assigned_replace_study_name = list(result.values())[0]
            return result

    @calc_func_time
    def build_table_field_mapping(self, data, table_actions):
        tables = self.get_tables_from_app_field(data, table_actions)
        mapping = dict()
        if len(tables) == 0:
            return mapping
        sql = """SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.COLUMNS 
                 WHERE table_schema = '{0}' AND table_name IN ({1});"""
        items = BaseDb(self.data_source).fetchall(sql.format(self.database, ",".join(tables))) or list()
        for item in items:
            table = item.get("TABLE_NAME")
            column = item.get("COLUMN_NAME")
            if mapping.get(table):
                mapping[table].append(column)
            else:
                columns = list()
                columns.append(column)
                mapping.update({table: columns})
        return mapping

    def get_tables_from_app_field(self, items, table_actions):
        tables = list()
        for item in items:
            app_source_field = item.get("app_source_field")
            if app_source_field is not None:
                self._parse_table_field(app_source_field, tables)
            fields = item.get("fields")
            self._parse_table_fields(fields, tables)
        for item in table_actions:
            details = item.get("details")
            self._parse_table_fields(details, tables)
        return set(tables)

    def _parse_table_field(self, table_field, tables):
        table_field = table_field.strip()
        handled_table_field = handle_special_table_field(table_field)
        if handled_table_field is not None:
            table_field = handled_table_field
        table = table_field.split(".")[0]
        if table in self.all_tables and table not in tables:
            tables.append(f"'{table}'")

    def _parse_table_fields(self, table_fields, tables):
        table_fields = re.split(NEWLINE_PLACEHOLDER_PATTERN, table_fields)
        for table_field in table_fields:
            if not table_field:
                continue
            self._parse_table_field(table_field, tables)

    def pv_eclinical_entry_form_item_record(self, current_value):
        sql = """SELECT
                    r.uuid 
                FROM
                    eclinical_entry_form_item_record r
                    JOIN eclinical_design_form_item i ON r.item_uuid = i.uuid AND r.form_uuid = i.form_uuid 
                WHERE
                    i.business_uuid IN ( "study_name", "study_select" ) 
                    AND r.delete_version = 2147483647 
                    AND i.delete_version = 2147483647 
                    AND r.current_value = '{0}'"""
        sql = sql.format(current_value)
        items = BaseDb(self.app_db_route).fetchall(sql) or list()
        uuids = [item.get('uuid') for item in items]
        condition = ",".join(map(str, uuids))
        return condition != "" and f"({condition})" or None
