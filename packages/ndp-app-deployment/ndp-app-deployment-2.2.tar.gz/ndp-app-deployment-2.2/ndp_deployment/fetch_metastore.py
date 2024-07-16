#-------------------------------------------------------------------------#
#Import Libraries
import sys
import jaydebeapi
import pandas as pd
from getpass import getpass
import re
from datetime import datetime
import itertools
import warnings
from base64 import b64encode
from base64 import b64decode
from Cryptodome.Cipher import AES
import hashlib
from datetime import datetime
import os
import yaml
from sqlalchemy import create_engine
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Util.Padding import unpad
from Cryptodome.Hash import SHA256
import logging
from logging.handlers import RotatingFileHandler
import uuid
import requests
from github import Github
import uuid
import base64
import urllib
import os.path
import json
from datetime import *
#-------------------------------------------------------------------------#
warnings.filterwarnings("ignore")
dt = datetime.now()
ts = datetime.timestamp(dt)
#-------------------------------------------------------------------------#
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
maxByteSize = 1.5*1024*1024
file_handler = RotatingFileHandler('backup_versioncontrol.log', maxBytes=maxByteSize,backupCount=10)
file_format = logging.Formatter('%(asctime)s: %(message)s', datefmt='%d-%m-%Y || %I:%M:%S %p')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)
#-------------------------------------------------------------------------#
def set_api_base_url(url:str):
    global api_url
    api_url = url

def get_auth(orgid, token:str=None):
    if token == None:
        global bearer_token
        token = bearer_token
    return {
        "Authorization": token,
        "X-Request-ID": str(uuid.uuid1()),
        "X-Org-ID":str(orgid)
      }

def basic_auth(username:str,password:str):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

def login(username:str,password:str,orgid:str):
    global bearer_token
    global refresh_token
    auth=get_auth(orgid, basic_auth(username, password))
    response = requests.get(url=f'{api_url}/api/v1.0/auth/login',headers=auth)
    response = json.loads(response.text)
    bearer_token = f"Bearer {response['idToken']}"
    refresh_token = f"Bearer {response['refreshToken']}"

def refresh_tokens():
    global bearer_token
    global refresh_token
    auth = get_auth(refresh_token)
    response = requests.get(url=f'{api_url}/api/v1.0/auth/refresh',headers=auth)
    response = json.loads(response.text)
    bearer_token = f"Bearer {response['idToken']}"
    refresh_token = f"Bearer {response['refreshToken']}"

def get_pipeline_containers():
    auth = get_auth()
    response = requests.get(url=f'{api_url}/api/v1.0/pipeline/containers',headers=auth)
    response = json.loads(response.text)
    return response

def get_pipeline_relations(pipeline_container_id:int):
    auth = get_auth()
    response = requests.get(url=f'{api_url}/api/v1.0/pipeline/containers/{pipeline_container_id}/relations',headers=auth)
    response = json.loads(response.text)
    return response

def execute_pipeline(pipeline_container_id:int, pipeline_relation_id:int, pageLimit:int):
    auth = get_auth()
    body = json.dumps({
    "pageLimit": pageLimit
    })
    response = requests.post(url=f'{api_url}/api/v1.0/pipeline/containers/{pipeline_container_id}/relations/{pipeline_relation_id}/execute',headers=auth,data=body)
    print(response.text)
    response = json.loads(response.text)
    return response

def open_sql_query(sql_query:str, pageLimit:int,orgid:str):
    auth = get_auth(orgid)
    body = json.dumps({
    "select": sql_query,
    "pageLimit": pageLimit
    })
    response = requests.post(url=f'{api_url}/api/v1.0/query/sql/start',headers=auth,data=body)
    response = json.loads(response.text)
    return response

def register_table(datasource_name:str, table_name:str):
    auth = get_auth()
    body = json.dumps({
    "dataSourceName": datasource_name,
      "tableName": table_name
    })
    response = requests.post(url=f'{api_url}/api/v1.0/query/sql/register-table',headers=auth,data=body)
    response = json.loads(response.text)
    return response

def generic_query(sql_query:str):
    auth = get_auth()
    body = json.dumps({
    "sql": sql_query
    })
    response = requests.post(url=f'{api_url}/api/v1.0/query/sql/generic-query',headers=auth,data=body)
    response = json.loads(response.text)
    return response

def page_sql_query(queryToken:str, pageLimit:int, pageNumber:int,orgid:str):
    auth = get_auth(orgid)
    params = {
    "queryToken": queryToken,
    "pageLimit": pageLimit,
    "pageNumber": pageNumber
    }
    response = requests.get(url=f'{api_url}/api/v1.0/query/sql/page',headers=auth,params=params)
    response = json.loads(response.text)
    return response

def close_sql_query(query_token:str):
    auth = get_auth()
    requests.delete(url=f'{api_url}/api/v1.0/query/sql/close/{query_token}',headers=auth)

def clear_query_cache(username:str):
    auth = get_auth()
    requests.delete(url=f'{api_url}/api/v1.0/query/sql/clear/{username}',headers=auth)
#-------------------------------------------------------------------------#
def exec_query_get_res(sql_query_res,orgid):
    print('SQL Query to be executed')
    print(sql_query_res)
    page_limit = 100
    x = open_sql_query(sql_query_res,page_limit,orgid)
    print(x)
    res = x['records']
    query_token = x['queryToken']
    max_pages = x['totalPages']
    for i in range(2,max_pages+1):
        page_data=page_sql_query(query_token,page_limit,i,orgid)
        res += page_data['records']
    return res
#-------------------------------------------------------------------------#
def get_org_id_from_email(lightning_username,orgid):
    orgId_query = 'select fk_organisation_id as id from metastore.lightning_user where lower(trim(email))='+"\'"+str(lightning_username)+"\'"
    x = open_sql_query(orgId_query,100,orgid)
    orgid_dict = x['records']
    if isinstance(orgid_dict[0],dict):
        orgId = orgid_dict[0]['id']
    return orgId
#-------------------------------------------------------------------------#
def serverDetails(api_url,lightning_username,lightning_pass,folder_path,orgid):
    try:
        set_api_base_url(api_url)
        login(lightning_username,lightning_pass, orgid)
    except:
        logger.info("\nCannot connect to Zetaris API\n")
        logger.info("Please try again.\n")
        serverDetails(api_url,lightning_username,lightning_pass,folder_path,orgid)
#-------------------------------------------------------------------------#           
def mainMenu(option,arg1,arg2,arg3,lightning_username,folder_path,orgid):
    if option != 10000:
        print("\n Select the following option to migrate: \n")
        print("1. Data Pipeline container")
        print("2. Individual Data Pipeline")
        print("3. Data Quality container")
        print("4. Individual Data Quality Pipeline")
        print("5. Data Mart")
        print("6. Individual Table/View in the existing Datamart")
        print("7. Permanent Views")
        print("8. View the list of Container/Pipeline Name")
        print("9. Exit")
        try:
            option = int(str(arg1).lower().strip())
            if option == 1:
                DataPipelineContainer_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid)
            elif option == 2:
                IndivdualDataPipeline_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid)
            elif option == 3:
                DataPipelineContainer_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid)
            elif option == 4:
                IndivdualDataPipeline_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid)
            elif option == 5:
                DataMart_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid)
            elif option == 6:
                DataMart_IndTable_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid)
            elif option == 7:
                PermanentViews_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid)
            elif option == 9:
                print("\nThanks for using the system")
                exit
            else:
                print("\n Invalid option\n")
                print("\n Thanks for using the system")
                exit
        except:
            logger.info("\nInvalid selection. Please select between 1-8.\n")
    else:
        print("\n Thanks for using the system")
        exit
#-------------------------------------------------------------------------#
def checkcontainername(container_name,orgid):
    logger.info("Container Name CHECK "+str(container_name))
    try:
        sql_containername_check="""select 'INSERT INTO pipeline_container (id, case_sensitive_name,description, name, fk_organisation_id)  VALUES (' || id || ',''' || CHAR(39)||COALESCE(case_sensitive_name, '')||CHAR(39)|| ''',''' ||CHAR(39)||COALESCE(description, '')||CHAR(39) || ''',''' ||CHAR(39)||COALESCE(name,'')||CHAR(39) || ''',' || COALESCE(fk_organisation_id, 0) ||''')'  from metastore.pipeline_container where name='%s';"""%(container_name)
        res = exec_query_get_res(sql_containername_check,orgid)
        if res:
            if isinstance(res[0],dict):
                return True
        else:
            return False
    except Exception as e:
        logger.info("Checking Container Name")
        logger.info(e)
#-------------------------------------------------------------------------#
def checkcontainer_pipeline_name(container_name,pipeline_name,orgid):
    logger.info("Container Name "+str(container_name))
    logger.info("Pipeline Name "+str(pipeline_name))
    try:
        sql_container_pipeline_chk="""select 'INSERT INTO pipeline_relation (id, case_sensitive_name,description, name, fk_pipeline_container_id) VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(case_sensitive_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(description, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(name, '')||CHAR(39) || ''',' || COALESCE(fk_pipeline_container_id, 0) || ')'     from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s') and case_sensitive_name = '%s';"""%(container_name,pipeline_name)
        res = exec_query_get_res(sql_container_pipeline_chk,orgid)
        if res:
            if isinstance(res[0],dict):
                print('Result after query')
                print(res)
                return True
        else:
            return False
    except Exception as e:
        logger.info("Checking Pipeline Name")
        logger.info(e)
#-------------------------------------------------------------------------#
def chk_datamart_name(datamart_name,orgid):
    logger.info("Data Mart Name "+str(datamart_name))
    try:
        sql_data_mart_ck = """SELECT 'INSERT INTO data_mart (id, case_sensitive_name ,default_view , name , fk_organisation_id ) VALUES (' || id || ',''' || CHAR(39)|| COALESCE(case_sensitive_name, '') ||CHAR(39)|| ''',''' ||CHAR(39)|| COALESCE(default_view, '')||CHAR(39)||''',''' ||CHAR(39)|| COALESCE(name,'')||CHAR(39) ||''','|| COALESCE(fk_organisation_id,'') ||')' FROM metastore.data_mart where name= '%s';"""%(datamart_name)
        res = exec_query_get_res(sql_data_mart_ck,orgid)
        if res:
            if isinstance(res[0],dict):
                return True
        else:
            return False
    except Exception as e:
        logger.info("Checking DataMart Name")
        logger.info(e)
#-------------------------------------------------------------------------#    
def chk_datamart_table_name(datamart_name,table_name,orgid):
    logger.info("Data Mart Name "+str(datamart_name))
    logger.info("Table Name "+str(table_name))
    try:
        sql_data_mart_ck = """SELECT 'INSERT INTO data_mart_table (id, case_sensitive_name , name , source_table  ,fk_data_mart_id  )  VALUES (' || id || ',''' || CHAR(39) || COALESCE(case_sensitive_name, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(name, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(source_table, '') || CHAR(39) || ''',' || COALESCE(fk_data_mart_id, 0) || ')' FROM metastore.data_mart_table where fk_data_mart_id in ( select id from metastore.data_mart where name = '%s') and name='%s';"""%(datamart_name,table_name) 
        res = exec_query_get_res(sql_data_mart_ck,orgid)
        if res:
            if isinstance(res[0],dict):
                return True
        else:
            return False
    except Exception as e:
        logger.info("Checking Data Mart Table Name")
        logger.info(e)  
#-------------------------------------------------------------------------#   
def chk_view_name(View_name,orgid):
    logger.info("View Name "+str(View_name))
    try:
        sql_view_name_ck = """select 'INSERT INTO schema_store_view (id, description ,generator, materialized_table,name,query,fk_organisation_id   )  VALUES (' || id || ',''' || CHAR(39) || COALESCE(description, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(generator, '') || char(39) || ''',''' || CHAR(39) || COALESCE(materialized_table, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(name, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(query, '') || CHAR(39) || ''',' || COALESCE(fk_organisation_id, 0) || ')' FROM metastore.schema_store_view where name = '%s';"""%(View_name)
        res = exec_query_get_res(sql_view_name_ck,orgid)
        if res:
            if isinstance(res[0],dict):
                return True
        else:
            return False
    except Exception as e:
        logger.info("Checking View Name")
        logger.info(e)  
#-------------------------------------------------------------------------#
def DataPipelineContainer_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid):
    try:
        container_name = str(arg2).strip()
        container_name = container_name.lower()
        chk_container_name= checkcontainername(container_name,orgid)
        if chk_container_name == False:
            logger.info("\nIncorrect container name. Please check the container name & try again.")
        else:
            list_queries = []
            sql_pipeline_container = """select 'INSERT INTO pipeline_container  (id, case_sensitive_name,description, name, fk_organisation_id)  VALUES (' || id || ',''' || CHAR(39)||COALESCE(case_sensitive_name, '')||CHAR(39)|| ''',''' ||CHAR(39)||COALESCE(description, '')||CHAR(39) || ''',''' ||CHAR(39)||COALESCE(name,'')||CHAR(39) || ''',' || COALESCE(fk_organisation_id, 0) ||''') using metastore'  as sql_query_con from metastore.pipeline_container where name='%s';"""%(container_name)
            res = exec_query_get_res(sql_pipeline_container,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_con']))
            
            sql_pipeline_relation = """select 'INSERT INTO pipeline_relation (id, case_sensitive_name,description, name, fk_pipeline_container_id) VALUES (' || id || ',''' || CHAR(39)||COALESCE(case_sensitive_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(description, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(name, '')||CHAR(39) || ''',' || COALESCE(fk_pipeline_container_id, 0) || ') using metastore' as sql_query_rel from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s');"""%(container_name)
            res = exec_query_get_res(sql_pipeline_relation,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_rel']))
                
            sql_pipeline_node="""select 'INSERT INTO pipeline_node (id, case_sensitive_name,description, name, fk_pipeline_relation_id, pipeline_type)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(case_sensitive_name, '')||CHAR(39) || ''',''' ||CHAR(39)||COALESCE(description, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(name,'')||CHAR(39) || ''',' || COALESCE(fk_pipeline_relation_id, 0) ||',''' ||char(39)|| COALESCE(pipeline_type,'')||char(39) ||''') using metastore'  as sql_query_node from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s'));"""%(container_name)
            res = exec_query_get_res(sql_pipeline_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_node']))
            
            sql_pipeline_node_schema="""select 'INSERT INTO pipeline_node_schema (id, column_alias,column_name, data_type, sql_expression, fk_pipeline_node_id)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(column_alias, '')||CHAR(39)|| ''',''' ||CHAR(39)|| COALESCE(column_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(data_type,'')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(sql_expression, '')||CHAR(39) ||''',' || COALESCE(fk_pipeline_node_id, 0) ||') using metastore'  as sql_query_node_schema FROM metastore.pipeline_node_schema where fk_pipeline_node_id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s')));"""%(container_name)
            res = exec_query_get_res(sql_pipeline_node_schema,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        temp_str=str(i['sql_query_node_schema']).replace("'",'"')
                        temp_str_list=list(temp_str)
                        result_comma = [_.start() for _ in re.finditer(",", temp_str)]
                        if("decimal(38" not in temp_str):
                            temp_str_list[result_comma[8]+1] = "'"
                            temp_str_list[result_comma[-1]-1] = "'"
                        temp_str_1 = "".join(temp_str_list)
                        list_queries.append(temp_str_1)
            
            sql_pipeline_node_property="""select 'INSERT INTO pipeline_node_property (id, property_key,property_value, fk_pipeline_node_id)  VALUES (' || id || ',''' ||CHAR(39)||COALESCE(property_key, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(property_value, '')||CHAR(39) ||''',' || COALESCE(fk_pipeline_node_id, 0) ||') using metastore'  as sql_query_prop FROM metastore.pipeline_node_property  where fk_pipeline_node_id in (select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s')));"""%(container_name)
            res = exec_query_get_res(sql_pipeline_node_property,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_prop']))

            sql_datasource_Node="""select 'INSERT INTO pipeline_datasource(id,datasource_table) VALUES(' || id || ',''' ||CHAR(39)|| COALESCE(datasource_table, '')||CHAR(39) || ''') using metastore' as sql_query_ds FROM metastore.pipeline_datasource where id in (select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s')));"""%(container_name) 
            res = exec_query_get_res(sql_datasource_Node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_ds']))

            sql_sql_table="""select 'INSERT INTO pipeline_sqltable (id, sql_query,source_tables)
             VALUES(' || id || ',''' ||CHAR(39)||COALESCE(sql_query, '')||CHAR(39) || ''',''' ||CHAR(39)|| 
             COALESCE(source_tables, '')||CHAR(39) || ''') using metastore' as sql_query_sql FROM metastore.pipeline_sqltable where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s')));"""%(container_name)
            res = exec_query_get_res(sql_sql_table,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        to_substitute = "''"
                        temp_str=str(i['sql_query_sql']).replace("'",'"')
                        temp_str_list=list(temp_str)
                        result_comma = [_.start() for _ in re.finditer(",", temp_str)]
                        temp_str_list[result_comma[2]+1] = "'"
                        temp_str_list[result_comma[-1]-1] = "'"
                        temp_str_1 = "".join(temp_str_list)
                        list_queries.append(temp_str_1)
            
            sql_projection_node="""select 'INSERT INTO pipeline_projection (id, filter_expression,order_by, windows_spec)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(filter_expression, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(order_by, '')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(windows_spec,'')||CHAR(39)||''') using metastore'  as sql_query_proj FROM metastore.pipeline_projection where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s')));"""%(container_name)
            res = exec_query_get_res(sql_projection_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        temp_str=str(i['sql_query_proj']).replace("'",'"')
                        temp_str_list=list(temp_str)
                        result_comma = [_.start() for _ in re.finditer(",", temp_str)]
                        temp_str_list[result_comma[3]+1] = "'"
                        result_comma = [_.start() for _ in re.finditer("\"", temp_str)]
                        temp_str_list[result_comma[-5]] = "'"
                        temp_str_1 = "".join(temp_str_list)
                        list_queries.append(temp_str_1)
            
            sql_join_node="""select 'INSERT INTO pipeline_join (id, filter_expression,join_predicate, join_tables, order_by)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(filter_expression, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(join_predicate, '')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(join_tables,'')||CHAR(39) ||''',''' || CHAR(39)||COALESCE(order_by,'')||CHAR(39) ||''') using metastore'  as sql_query_join FROM metastore.pipeline_join where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name='%s')));"""%(container_name)
            res = exec_query_get_res(sql_join_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_join']))

            sql_aggregation_node="""select 'INSERT INTO pipeline_aggregation (id, filter_expression,group_expression, having_expression, order_by)  VALUES (' || id || ',''' ||CHAR(39)||COALESCE(filter_expression, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(group_expression, '')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(having_expression,'')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(order_by,'')||CHAR(39) ||''') using metastore'  as sql_query_agg FROM metastore.pipeline_aggregation where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s')));"""%(container_name)
            res = exec_query_get_res(sql_aggregation_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_agg']))

            sql_sink_node="""select 'INSERT INTO pipeline_sink (id, sink_type)  VALUES (' || id || ',''' ||char(39)|| COALESCE(sink_type, '')||char(39) ||''') using metastore'  as sql_query_sink FROM metastore.pipeline_sink where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s')));"""%(container_name)
            res = exec_query_get_res(sql_sink_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_sink']))

            sql_DQ_pipeline = """select 'INSERT INTO pipeline_simple_dq (id) VALUES ('||id||') using metastore' as sql_query_simdq FROM metastore.pipeline_simple_dq where id in (select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name='%s')));"""%(container_name)
            res = exec_query_get_res(sql_DQ_pipeline,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_simdq']))
                
            sql_pipeline_simple_dq_rule = """SELECT 'INSERT INTO pipeline_simple_dq_rule (id, columns ,expression , filter , name,fk_pipeline_simple_dq_id  ) VALUES (' || id || ',''' ||CHAR(39)||COALESCE(columns, '')||CHAR(39) || ''',''' ||CHAR(34)|| COALESCE(expression, '')||CHAR(34) || ''',''' ||CHAR(34)|| COALESCE(filter, '')||CHAR(34) || ''',''' ||CHAR(39)|| COALESCE(name, '')||CHAR(39) || ''',' || COALESCE(fk_pipeline_simple_dq_id, 0) || ') using metastore' as sql_query_simdq_rule FROM metastore.pipeline_simple_dq_rule where fk_pipeline_simple_dq_id in (select id from metastore.pipeline_simple_dq where id in (select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s'))));"""%(container_name)
            res = exec_query_get_res(sql_pipeline_simple_dq_rule,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_simdq_rule']))
                        
            generateSQLfile(list_queries,container_name,'pipeline','',lightning_username,folder_path,orgid)
            print('Script Generated...')
    except Exception as e:
        print(e)
        logger.info("Inside Full Pipeline container backup function")
        logger.info(e)
#-------------------------------------------------------------------------#
def IndivdualDataPipeline_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid):
    try:
        container_name = str(arg2).strip()
        container_name = container_name.lower()
        pipeline_name=str(arg3).strip()
        pipeline_name=pipeline_name.lower()
        chk_con_pipe_name= checkcontainer_pipeline_name(container_name,pipeline_name,orgid)
        if chk_con_pipe_name == False:
            print("\n Incorrect container or pipeline name. Please check the container/pipeline name & try again")  
        else:
            list_queries = []            
            sql_pipeline_relation = """select 'INSERT INTO pipeline_relation (id, case_sensitive_name,description, name, fk_pipeline_container_id)VALUES(' || id || ',''' ||CHAR(39)|| COALESCE(case_sensitive_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(description, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(name, '')||CHAR(39) || ''',' || COALESCE(fk_pipeline_container_id, 0) || ') using metastore' as sql_query_rel from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s') and case_sensitive_name = '%s';"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_pipeline_relation,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_rel']))
                
            sql_pipeline_node="""select 'INSERT INTO pipeline_node (id, case_sensitive_name,description, name, fk_pipeline_relation_id, pipeline_type)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(case_sensitive_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(description, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(name,'')||CHAR(39) || ''',' || COALESCE(fk_pipeline_relation_id, 0) ||',''' ||CHAR(39)|| COALESCE(pipeline_type,'')||CHAR(39) ||''') using metastore'  as sql_query_node from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s') and case_sensitive_name = '%s');"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_pipeline_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_node']))
                
            sql_pipeline_node_schema="""select 'INSERT INTO pipeline_node_schema (id, column_alias,column_name, data_type, sql_expression, fk_pipeline_node_id)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(column_alias, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(column_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(data_type,'')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(sql_expression, '')||CHAR(39) ||''',' || COALESCE(fk_pipeline_node_id, 0) ||') using metastore'  as sql_query_node_schema FROM metastore.pipeline_node_schema where fk_pipeline_node_id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_pipeline_node_schema,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_node_schema']))
                # if isinstance(res[0],dict):
                #     for i in res:
                #         temp_str=str(i['sql_query_node_schema']).replace("'",'"')
                #         temp_str_list=list(temp_str)
                #         result_comma = [_.start() for _ in re.finditer(",", temp_str)]
                #         temp_str_list[result_comma[8]+1] = "'"
                #         temp_str_list[result_comma[-1]-1] = "'"
                #         temp_str_1 = "".join(temp_str_list)
                #         list_queries.append(temp_str_1)
            
            sql_pipeline_node_property="""select 'INSERT INTO pipeline_node_property (id, property_key,property_value, fk_pipeline_node_id)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(property_key, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(property_value, '')||CHAR(39) ||''',' || COALESCE(fk_pipeline_node_id, 0) ||') using metastore'  as sql_query_prop FROM metastore.pipeline_node_property  where fk_pipeline_node_id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_pipeline_node_property,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_prop']))
                
            sql_datasource_Node="""select 'INSERT INTO pipeline_datasource(id,datasource_table) VALUES(' || id || ',''' ||CHAR(39)|| COALESCE(datasource_table, '')||CHAR(39) || ''') using metastore' as sql_query_ds FROM metastore.pipeline_datasource where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_datasource_Node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_ds']))
                
            sql_sql_table="""select 'INSERT INTO pipeline_sqltable (id, sql_query,source_tables) VALUES(' || id || ',''' ||CHAR(39)||COALESCE(sql_query, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(source_tables, '')||CHAR(39) || ''') using metastore'  as sql_query_sql FROM metastore.pipeline_sqltable where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_sql_table,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_sql']))
                # if isinstance(res[0],dict):
                #     for i in res:
                #         to_substitute = "''"
                #         temp_str=str(i['sql_query_sql']).replace("'",'"')
                #         temp_str_list=list(temp_str)
                #         result_comma = [_.start() for _ in re.finditer(",", temp_str)]
                #         temp_str_list[result_comma[2]+1] = "'"
                #         temp_str_list[result_comma[-1]-1] = "'"
                #         temp_str_1 = "".join(temp_str_list)
                #         list_queries.append(temp_str_1)

            sql_projection_node="""select 'INSERT INTO pipeline_projection (id, filter_expression,order_by, windows_spec)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(filter_expression, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(order_by, '')||CHAR(39) ||''',''' || CHAR(39)||COALESCE(windows_spec,'')||CHAR(39) ||''') using metastore'  as sql_query_proj FROM metastore.pipeline_projection where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_projection_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_proj']))
                # if isinstance(res[0],dict):
                #     for i in res:
                #         temp_str=str(i['sql_query_proj']).replace("'",'"')
                #         temp_str_list=list(temp_str)
                #         result_comma = [_.start() for _ in re.finditer(",", temp_str)]
                #         temp_str_list[result_comma[3]+1] = "'"
                #         result_comma = [_.start() for _ in re.finditer("\"", temp_str)]
                #         temp_str_list[result_comma[-5]] = "'"
                #         temp_str_1 = "".join(temp_str_list)
                #         list_queries.append(temp_str_1)

            sql_join_node="""select 'INSERT INTO pipeline_join (id, filter_expression,join_predicate, join_tables, order_by)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(filter_expression, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(join_predicate, '')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(join_tables,'')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(order_by,'')||CHAR(39) ||''') using metastore'  as sql_query_join FROM metastore.pipeline_join where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name='%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_join_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_join']))

            sql_aggregation_node="""select 'INSERT INTO pipeline_aggregation (id, filter_expression,group_expression, having_expression, order_by)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(filter_expression, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(group_expression, '')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(having_expression,'')||CHAR(39) ||''',''' ||CHAR(39)|| COALESCE(order_by,'')||CHAR(39) ||''') using metastore'  as sql_query_agg FROM metastore.pipeline_aggregation where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_aggregation_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_agg']))

            sql_sink_node="""select 'INSERT INTO pipeline_sink (id, sink_type)  VALUES (' || id || ',''' ||char(39)|| COALESCE(sink_type, '')||char(39) ||''') using metastore'  as sql_query_sink FROM metastore.pipeline_sink where id in(select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from  metastore.pipeline_container where name='%s') and case_sensitive_name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_sink_node,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_sink']))

            sql_DQ_pipeline = """select 'INSERT INTO pipeline_simple_dq (id) VALUES ('||id||') using metastore' as sql_query_simdq FROM metastore.pipeline_simple_dq where id in (select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name='%s') and name = '%s'));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_DQ_pipeline,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_simdq']))

            sql_pipeline_simple_dq_rule = """SELECT 'INSERT INTO pipeline_simple_dq_rule (id, columns ,expression , filter , name,fk_pipeline_simple_dq_id  ) VALUES (' || id || ',''' ||CHAR(39)||COALESCE(columns, '')||CHAR(39)|| ''',''' ||CHAR(34)||COALESCE(expression, '')||CHAR(34) || ''',''' ||CHAR(34)|| COALESCE(filter, '')||CHAR(34) || ''',''' ||CHAR(39)||COALESCE(name, '')||CHAR(39)|| ''',' || COALESCE(fk_pipeline_simple_dq_id, 0) || ') using metastore' as sql_query_simdq_rule FROM metastore.pipeline_simple_dq_rule where fk_pipeline_simple_dq_id in (select id from metastore.pipeline_simple_dq where id in (select id from metastore.pipeline_node where fk_pipeline_relation_id in (select id from metastore.pipeline_relation where fk_pipeline_container_id in (select id from metastore.pipeline_container where name = '%s') and name='%s')));"""%(container_name,pipeline_name)
            res = exec_query_get_res(sql_pipeline_simple_dq_rule,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_simdq_rule']))
            
            generateSQLfile(list_queries,container_name,pipeline_name,'Pipeline',lightning_username,folder_path,orgid)
            print('Script Generated...')
    except Exception as e:
        print(e)
        logger.info("Inside Individual Pipeline Backup Function")
        logger.info(e)
#-------------------------------------------------------------------------#    
def PermanentViews_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid):
    try:
        View_name=str(arg2).strip()
        View_name = View_name.upper().strip()
        chk_viewname= chk_view_name(View_name,orgid)
        if chk_viewname == False:
            print("\n Incorrect view name.")  
        else:
            list_queries = []
            
            sql_Permanent_View = """select 'INSERT INTO schema_store_view (id, description ,generator, materialized_table,name,query,fk_organisation_id   )  VALUES (' || id || ',''' || CHAR(39) || COALESCE(description, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(generator, '') || char(39) || ''',''' || CHAR(39) || COALESCE(materialized_table, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(name, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(query, '') || CHAR(39) || ''',' || COALESCE(fk_organisation_id, 0) || ') using metastore' as sql_query_pmvw FROM metastore.schema_store_view where name = '%s';"""%(View_name)
            res = exec_query_get_res(sql_Permanent_View,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_pmvw']))
                
            sql_schema_store_view_schema = """select  'INSERT INTO schema_store_view_schema  (id, column_name  ,data_type , fk_schema_store_view_id) VALUES (' || id || ',''' || CHAR(39) || COALESCE(column_name, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(data_type, '') || char(39) || ''',' || COALESCE(fk_schema_store_view_id, 0) || ') using metastore' as sql_query_pmvw_schema FROM metastore.schema_store_view_schema where fk_schema_store_view_id in (select id from metastore.schema_store_view where name = '%s');"""%(View_name)
            res = exec_query_get_res(sql_schema_store_view_schema,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_pmvw_schema']))
                        
            generateSQLfile(list_queries,View_name,'Permanent_View','',lightning_username,folder_path)
            print('Script Generated...')
    except Exception as e:
        logger.info("Inside Permanent View Backup Function")
        logger.info(e)
#-------------------------------------------------------------------------#
def DataMart_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid):
    try:
        datamart_name=str(arg2).strip()
        datamart_name = datamart_name.upper().strip()
        chk_dm_name= chk_datamart_name(datamart_name,orgid)
        if chk_dm_name == False:
            print("\n Incorrect data mart name.")  
        else:
            list_queries = []
            sql_data_mart = """SELECT 'INSERT INTO data_mart (id, case_sensitive_name ,description, name , fk_organisation_id ) VALUES (' || id || ',''' || CHAR(39)|| COALESCE(case_sensitive_name, '') ||CHAR(39)|| ''',''' ||CHAR(39)|| COALESCE(description, '')||char(39)||''','''||char(39)||COALESCE(name,'')||CHAR(39) ||''','|| COALESCE(fk_organisation_id,'') ||') using metastore' as sql_query_dm FROM metastore.data_mart where name= '%s';"""%(datamart_name)
            res = exec_query_get_res(sql_data_mart,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_dm']))

            sql_data_mart_table = """SELECT 'INSERT INTO data_mart_table (id, case_sensitive_name , name , source_table  ,fk_data_mart_id  )  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(case_sensitive_name, '')||CHAR(39)|| ''',''' ||CHAR(39)|| COALESCE(name, '')||CHAR(39)||''',''' ||CHAR(39)||COALESCE(source_table ,'')||CHAR(39) ||''','|| COALESCE(fk_data_mart_id,0) ||') using metastore'  as sql_query_dm_table FROM metastore.data_mart_table where fk_data_mart_id in (select id from metastore.data_mart where name = '%s');"""%(datamart_name)
            res = exec_query_get_res(sql_data_mart_table,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_dm_table']))
            
            sql_data_mart_table_schema = """select  'INSERT INTO data_mart_table_schema (id, real_column_name , virtual_name, fk_data_mart_table_id)  VALUES (' || id || ',''' ||CHAR(39)||COALESCE(real_column_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(virtual_name, '')||CHAR(39) ||''','|| COALESCE(fk_data_mart_table_id,0) ||') using metastore' as sql_query_dm_schema from metastore.data_mart_table_schema where fk_data_mart_table_id in (select id from metastore.data_mart_table where fk_data_mart_id in (select id from  metastore.data_mart where name = '%s'));"""%(datamart_name)
            res = exec_query_get_res(sql_data_mart_table_schema,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_dm_schema']))

            generateSQLfile(list_queries,datamart_name,'DataMart','',lightning_username,folder_path,orgid)
            print('Script Generated...')
    except Exception as e:
        logger.info("Inside Data Mart backup Function")
        logger.info(e)
#-------------------------------------------------------------------------#        
def DataMart_IndTable_InsertQueries(arg1,arg2,arg3,lightning_username,folder_path,orgid):
    try:
        datamart_name=str(arg2).strip()
        datamart_name = datamart_name.upper().strip()
        table_name=str(arg3).strip()
        table_name = table_name.upper().strip()
        chk_dm_name= chk_datamart_table_name(datamart_name,table_name,orgid)
        if chk_dm_name == False:
            print("\n Incorrect data mart name.")
        else:
            list_queries = []
            sql_data_mart_table = """SELECT 'INSERT INTO data_mart_table (id, case_sensitive_name , name , source_table  ,fk_data_mart_id  )  VALUES (' || id || ',''' || CHAR(39) || COALESCE(case_sensitive_name, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(name, '') || CHAR(39) || ''',''' || CHAR(39) || COALESCE(source_table, '') || CHAR(39) || ''',' || COALESCE(fk_data_mart_id, 0) || ') using metastore' as sql_query_dm FROM metastore.data_mart_table where fk_data_mart_id in ( select id from metastore.data_mart where name = '%s') and name='%s';"""%(datamart_name,table_name)
            res = exec_query_get_res(sql_data_mart_table,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_dm']))
            
            sql_data_mart_table_schema = """select  'INSERT INTO data_mart_table_schema (id, real_column_name , virtual_name, fk_data_mart_table_id)  VALUES (' || id || ',''' ||CHAR(39)|| COALESCE(real_column_name, '')||CHAR(39) || ''',''' ||CHAR(39)|| COALESCE(virtual_name, '')||CHAR(39) ||''','|| COALESCE(fk_data_mart_table_id,0) ||') using metastore' as sql_query_dm_schema from metastore.data_mart_table_schema where fk_data_mart_table_id in (select id from metastore.data_mart_table where fk_data_mart_id in (select id from  metastore.data_mart where name = '%s')and name='%s');"""%(datamart_name,table_name)
            res = exec_query_get_res(sql_data_mart_table_schema,orgid)
            if res:
                if isinstance(res[0],dict):
                    for i in res:
                        list_queries.append(str(i['sql_query_dm_schema']))
            
            generateSQLfile(list_queries,datamart_name,table_name,'DataMart',lightning_username,folder_path,folder_path,orgid)
            print('Script Generated...')
    except Exception as e:
        logger.info("Inside Data Mart Individual Tables Backup Function")
        logger.info(e)
#-------------------------------------------------------------------------#    
def generateSQLfile(list_queries,filename1,filename2,filename3,lightning_username,folder_path,orgid):
    try:
        orgId = get_org_id_from_email(lightning_username,orgid)
        filename1=filename1.lower()
        filename2=filename2.lower()
        filename3=filename3.lower()
        if (len(filename3)>1):
            output_filename =filename1+'-'+filename2+ '-'+ filename3 +'-'+str(orgId)+'.sql'
        else:
            output_filename=filename1+'-'+filename2+'-'+str(orgId)+'.sql'
        df = open(folder_path+output_filename, 'w+')
        for i in range(len(list_queries)):
            df.write(list_queries[i])
            df.write('\n')
        df.close()
    except Exception as e:
        logger.info("Inside Generating Files with SQL Queries Function")
        logger.info(e)
#-------------------------------------------------------------------------#    
def object_deployment(api_url,lightning_username,lightning_pass,folder_path,arg1,arg2,arg3,orgid):
    try:
        serverDetails(api_url,lightning_username,lightning_pass,folder_path,orgid)
        mainMenu('',arg1,arg2,arg3,lightning_username,folder_path,orgid)
    except Exception as e:
        print(e)
        logger.info("Inside Main Object Deployment / Backup of Metastore Main Function")
        logger.info(e)
#-------------------------------------------------------------------------#