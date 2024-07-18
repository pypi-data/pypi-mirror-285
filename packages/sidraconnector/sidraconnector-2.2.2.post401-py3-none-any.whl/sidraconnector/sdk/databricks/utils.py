import uuid
from sidraconnector.sdk import  constants as sdk_constants

class Utils():
    def __init__(self, spark):
        self.spark = spark
        self.dbutils = self.get_db_utils()
    
    def execute_sql_queries(self, queries):
        for query in queries:
            self.spark.sql(query)

    def get_databricks_secret(self, scope, key):
        try:
            return self.dbutils.secrets.get(scope=scope, key=key)
        except:
            return ''

    def get_db_utils(self):
        dbutils = None      
        if self.spark.conf.get("spark.databricks.service.client.enabled") == "true":            
            from pyspark.dbutils import DBUtils
            dbutils = DBUtils(self.spark)        
        else:            
            import IPython
            dbutils = IPython.get_ipython().user_ns["dbutils"]        
        return dbutils
    
    def get_notebook_parameter(self, key):
        try:
            return self.dbutils.widgets.get(key)
        except:
            return None 
        
    def get_default_catalog(self):
        default_catalog = self.dbutils.secrets.get(scope='resources', key='default_catalog')
        # WE USE CREDENTIAL PASSTHROUGH FROM DATABRICKS TO FABRIC, WHICH IS NOT COMPATIBLE WITH UNITY CATALOG
        dsu_type = self.dbutils.secrets.get(scope='resources', key='dsu_type')       
        if (dsu_type == sdk_constants.DSU_TYPE_FABRIC):
            default_catalog = "hive_metastore"     
        return default_catalog