# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/12/2021 1:50 PM
@Description: Description
@File: admin_db.py
"""

from .base_db import BaseDb


class AdminDb(BaseDb):

    def __init__(self, data_source):
        data_source["db"] = "eclinical_admin"
        super().__init__(data_source)

    def get_sponsor_id(self, study_id):
        return self.fetchone_and_get_value(f"SELECT sponsor_id FROM eclinical_admin_study WHERE "
                                           f"id={study_id} AND active=TRUE AND is_delete=FALSE;", f"study::{study_id}")

    def get_company_id(self, sponsor_id):
        return self.fetchone_and_get_value(f"SELECT company_id FROM eclinical_admin_sponsor WHERE id={sponsor_id} "
                                           f"AND active=TRUE AND is_delete=FALSE;", f"sponsor_id::{sponsor_id}")

    def get_env_id(self, company_id, app_env):
        return self.fetchone_and_get_value(
            f"SELECT id FROM eclinical_admin_company_multiple_env WHERE company_id={company_id} "
            f"AND name='{app_env}' AND is_delete=FALSE", f"company_id:{company_id}::app_env:{app_env}")

    def get_db_route_by_study(self):
        return self.fetchone_and_get_value("SELECT GROUP_CONCAT(CONCAT(\"'\",LOWER(name),\"'\")) names FROM "
                                           "eclinical_system WHERE db_route_by_study=TRUE;", "")

    def get_db_route_by_sponsor(self):
        return self.fetchone_and_get_value("SELECT GROUP_CONCAT(CONCAT(\"'\",LOWER(name),\"'\")) names FROM "
                                           "eclinical_system WHERE db_route_by_study=FALSE;", "")

    def get_system_id(self, system):
        return self.fetchone_and_get_value(f"SELECT id FROM eclinical_system WHERE name='{system}';", f"app::{system}")

    def get_app_route(self, app, app_env, sponsor_id, study_id, company_id):
        return self.fetchone(f"""SELECT
                                    eadc.ip host,
                                    CONVERT(eadc.port, UNSIGNED INTEGER) port,
                                    eadc.user_name user,
                                    eadc.password,
                                    eadr.business_db_name db
                                FROM
                                    eclinical_admin_database_configuration eadc
                                    JOIN eclinical_admin_database_route eadr ON eadc.id = eadr.db_configuration_id
                                    JOIN eclinical_system es ON eadr.system_id = es.id 
                                WHERE
                                    eadc.is_delete=FALSE AND es.name="{app}" AND eadr.env_name="{app_env}"
                                    AND eadr.study_id={study_id} AND eadr.sponsor_id={sponsor_id}
                                    AND eadr.company_id={company_id};""")

    # Business

    def is_db_route_by_study(self, system):
        data = self.get_db_route_by_study()
        db_route_by_study_apps = eval(data)
        return system in db_route_by_study_apps

    def is_db_route_by_sponsor(self, system):
        data = self.get_db_route_by_sponsor()
        db_route_by_sponsor_apps = eval(data)
        return system in db_route_by_sponsor_apps

    def get_study_in_the_sponsor(self, sponsor_id):
        sql = """SELECT CONCAT(id, "-", "(", name, ")") concat_name, id, name, description, active, company_id, 
                 sponsor_id, status, modify_uid, creator_dt, modify_dt, creator_uid, is_delete, subject_management 
                 FROM eclinical_admin_study WHERE sponsor_id={0} AND is_delete=FALSE AND active=TRUE;"""
        return self.fetchall(sql.format(sponsor_id)) or list()

    def check_admin_data(self, study_id, app_env, has_site_check=False, has_role_check=False):
        """
        check that study_dto, site_dto, role_dto from admin.
        @param study_id: int
        @param app_env: dev, uat, prod
        @param has_site_check:
        @param has_role_check:
        @return:
        """
        study_dto = self.fetchone(f"SELECT id, name, sponsor_id FROM eclinical_admin_study WHERE id={study_id};")
        if not study_dto:
            raise Exception(f"The study[{study_id}] is not exist.")
        site_dto = self.fetchall(f"""SELECT
                                        eassr.site_id, eassr.code 
                                    FROM
                                        eclinical_admin_study_site_rel eassr
                                        JOIN eclinical_admin_site eas ON eassr.site_id = eas.id
                                        JOIN eclinical_admin_company_multiple_env eacmee ON eassr.env_id = eacmee.id 
                                        AND eas.company_id = eacmee.company_id 
                                    WHERE
                                        eassr.study_id = {study_id} 
                                        AND eacmee.name = '{app_env}' 
                                        AND eacmee.is_delete = FALSE
                                        AND eas.active = TRUE
                                        AND eas.is_delete = FALSE
                                    ORDER BY eassr.code;""")
        if (not site_dto) and has_site_check:
            raise Exception(f"The study[{study_id}] is not associated with the site, "
                            f"please log in to CTMS to associate the site with the study.")
        role_dto = self.fetchall(f"""SELECT
                                        ear.id,
                                        ear.category,
                                        ear.code
                                    FROM
                                        eclinical_admin_role ear
                                        JOIN eclinical_admin_study eas ON ear.company_id = eas.company_id
                                        JOIN eclinical_admin_company_multiple_env eacmee ON ear.company_id = eacmee.company_id
                                    WHERE
                                        eas.id = {study_id}
                                        AND eacmee.name = '{app_env}'
                                        AND eas.active = TRUE 
                                        AND eas.is_delete = FALSE 
                                        AND ear.active = TRUE 
                                        AND ear.is_delete = FALSE; """)
        if (not role_dto) and has_role_check:
            raise Exception(f"The study[{study_id}] is not associated with the role.")

    def get_sponsor_by_id(self, sponsor_id):
        return self.fetchone_and_get_value(f"SELECT name FROM eclinical_admin_sponsor WHERE id={sponsor_id} "
                                           f"AND active=TRUE AND is_delete=FALSE;", f"sponsor_id::{sponsor_id}")

    def get_study_by_id(self, study_id):
        return self.fetchone_and_get_value(f"SELECT name FROM eclinical_admin_study WHERE "
                                           f"id={study_id} AND active=TRUE AND is_delete=FALSE;", f"study::{study_id}")

    def get_study_in_the_company(self, company_id):
        sql = """
        SELECT 
            CONCAT(sp.id, "/", s.`id`, " (", sp.`name`, "/", s.`name`, ")" ) concat_name, 
            s.id, 
            s.`name`, 
            s.description, 
            s.active, 
            s.company_id, 
            s.sponsor_id, 
            s.`status`, 
            s.modify_uid, 
            s.creator_dt, 
            s.modify_dt, 
            s.creator_uid, 
            s.is_delete, 
            s.subject_management
        FROM eclinical_admin_study s
        JOIN eclinical_admin_sponsor sp ON s.sponsor_id=sp.id
        WHERE s.company_id={0} 
            AND s.is_delete=FALSE AND s.active=TRUE 
            AND sp.is_delete=FALSE AND sp.active=TRUE;
        """
        return self.fetchall(sql.format(company_id)) or list()
