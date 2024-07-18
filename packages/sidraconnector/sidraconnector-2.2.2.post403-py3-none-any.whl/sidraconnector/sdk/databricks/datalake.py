from sidraconnector.sdk import constants
from sidraconnector.sdk.log.logging import Logger
from sidraconnector.sdk.databricks.utils import Utils
from sidraconnector.sdk.api.sidra.core.utils import Utils as CoreApiUtils
from sidraconnector.sdk.storage.storageservice import StorageService
from SidraCoreApiPythonClient.api.metadata_entities_entity_api import MetadataEntitiesEntityApi
from SidraCoreApiPythonClient.models.persistence_common_entities_data_ingestion_table_format_enum import PersistenceCommonEntitiesDataIngestionTableFormatEnum
from SidraCoreApiPythonClient.models.data_ingestion_entity_type_enum import DataIngestionEntityTypeEnum
from SidraCoreApiPythonClient.models.metadata_entities_entity_recreate_table_dto import MetadataEntitiesEntityRecreateTableDTO
from SidraCoreApiPythonClient.api.metadata_providers_provider_api import MetadataProvidersProviderApi
from SidraCoreApiPythonClient.api.fabric_fabric_api import FabricFabricApi

from collections import namedtuple


class Datalake():
    def __init__(self, spark):
        self.spark = spark
        self.databricks_utils = Utils(spark)
        self.api_utils = CoreApiUtils(spark)        
        self.dbutils = self.databricks_utils.get_db_utils()
        self.logger = Logger(spark, self.__class__.__name__)

    def create_tables(self, id_entities):
        self.spark.conf.set("fs.azure.createRemoteFileSystemDuringInitialization", "true")
        client = self.api_utils.get_SidraCoreApiClient()

        principal_storage_name = self.dbutils.secrets.get(scope='resources', key='principal_storage_account_name')               
        default_catalog = self.databricks_utils.get_default_catalog()
        dsu_type = self.dbutils.secrets.get(scope='resources', key='dsu_type')       

        print (f"Creating tables. DSU Type: {dsu_type}, default_catalog: {default_catalog}, principal_storage_name: {principal_storage_name} ")

        entities = self._get_entities(id_entities, client)
        provider_info = {}
        create_table_statements = []
        entity_views_added = []
        EntityView = namedtuple('EntityView', 'id_entity view_name')
        for entity in entities:
            if entity.id_provider in provider_info:
                provider = provider_info[entity.id_provider]
            else:
                # First create necessary databases if not already created                   
                provider = self._get_provider(entity.id_provider, client)
                provider = self._create_provider_database(provider, dsu_type, client, default_catalog)
                provider_info[provider.id_provider] = provider

            statements, entity_view = self._get_create_table_sql_statements(entity.attributes,
                                        default_catalog, 
                                        provider.database_name,
                                        provider.fabric_lakehouse_id,
                                        provider.fabric_workspace_id,
                                        dsu_type,
                                        entity.table_name,
                                        entity.table_format,
                                        entity.recreate_table,
                                        entity.generate_delta_table,
                                        entity.entity_type, 
                                        entity.view_definition,
                                        principal_storage_name)
            create_table_statements.extend(statements)
            if entity_view:
                entity_views_added.append(EntityView(id_entity = entity.id_entity, view_name = entity_view))
                   
        # Create the tables       
        for statement in create_table_statements:    
            print(f"Executing SQL statement: {statement}")
            #before creating the table we need to delete the actual files from the unmanaged table so we don't get error "The specified partitioning does not match the existing partitioning" if the table schema is updated
            if 'CREATE TABLE IF NOT EXISTS' in statement:
                table_file_location=statement.split("LOCATION ",1)[1].replace("'","")
                self.dbutils.fs.rm(table_file_location, True)
                self.logger.event('DSU Table created', {'statement' : statement})
            else:
                self.logger.event('DSU View created', {'statement' : statement})
            self.spark.sql(statement)
            
        client = self.api_utils.get_SidraCoreApiClient() # this would not be needed if client had auto-refresh
        for view in entity_views_added:
            print(f"Updating attributes for {view}")
            attributes = self._get_view_fields(view.view_name)
            self._set_view_attributes(view.id_entity, attributes, client)

        if (dsu_type == constants.DSU_TYPE_FABRIC):
            fabric_api = FabricFabricApi(client)
            for entity in entities:
                fabric_api.api_fabric_shortcut_entity_entity_id_post(entity.id_entity)
            
        self.logger.flush()
        # Update the recreate table flag
        client = self.api_utils.get_SidraCoreApiClient() # this would not be needed if client had auto-refresh
        metadata_entity_api = MetadataEntitiesEntityApi(client)
        metadata_entity_api.api_metadata_entities_updaterecreatetable_put(body=MetadataEntitiesEntityRecreateTableDTO(id_entities=id_entities,recreate_table=False))
        self.spark.conf.set("fs.azure.createRemoteFileSystemDuringInitialization", "false")

    def _create_provider_database(self, provider, dsu_type, client, catalog_name):
        statement = self._get_create_database_sql_statement(catalog_name, provider.database_name)                  
        df = self.spark.sql(f"show databases in `{catalog_name}`")
        df.show()        
        print(f"Executing SQL statement: {statement}")
        self.spark.sql(statement)
        df = self.spark.sql(f"show databases in `{catalog_name}`")
        df.show()        

        if (dsu_type == constants.DSU_TYPE_FABRIC):
            # Create a LakeHouse as well
            print(f"Creating Fabric Lakehouse: {provider.database_name}")
            fabric_api = FabricFabricApi(client)
            lakehouse = fabric_api.api_fabric_lakehouse_provider_provider_id_post(provider.id_provider)
            provider = provider._replace(fabric_lakehouse_id = lakehouse.fabric_lake_house_id)
            provider = provider._replace(fabric_workspace_id = lakehouse.fabric_workspace_id)            

        return provider


    def _get_entities(self, id_entities, client):
        metadata_entity_api = MetadataEntitiesEntityApi(client)
        KEY_ID_ENTITY = 'id'
        KEY_ID_PROVIDER = 'id_provider'
        KEY_TABLE_NAME = 'table_name'
        KEY_ID_TABLE_FORMAT = 'id_table_format'
        KEY_RECREATE_TABLE_ON_DEPLOYMENT = 're_create_table_on_deployment'
        KEY_GENERATE_DELTA_TABLE = 'generate_delta_table'
        KEY_ATTRIBUTES = 'attributes'
        KEY_ENTITY_TYPE = 'entity_type'
        KEY_VIEW_DEFINITION = 'view_definition'
        entities=metadata_entity_api.api_metadata_entities_withattributes_get(body=id_entities)   
        EntityModel = namedtuple('EntityModel', 'id_entity id_provider table_name table_format recreate_table generate_delta_table attributes entity_type view_definition')
        entities_model = []
        for entity in entities:
            self._validate_model(entity.to_dict(), KEY_ID_ENTITY, KEY_ID_PROVIDER, KEY_TABLE_NAME, KEY_ID_TABLE_FORMAT, KEY_RECREATE_TABLE_ON_DEPLOYMENT, KEY_GENERATE_DELTA_TABLE, KEY_ATTRIBUTES)
            id_entity = entity.id
            id_provider = entity.id_provider
            table_name = entity.table_name
            table_format = self._get_table_format(entity.id_table_format)
            recreate_table = entity.re_create_table_on_deployment
            generate_delta_table = entity.generate_delta_table
            entity_type = self._get_entity_type(entity.entity_type)
            view_definition = entity.view_definition
            attributes = self._parse_attributes(entity.attributes)
            entities_model.append(EntityModel(id_entity = id_entity, id_provider = id_provider, table_name = table_name, table_format =table_format, recreate_table = recreate_table, generate_delta_table = generate_delta_table, attributes =attributes, entity_type = entity_type, view_definition = view_definition))
        return entities_model        

    def _get_provider(self, id_provider, client):
        providers_cache = dict()
        metadata_provider_api = MetadataProvidersProviderApi(client)
        KEY_DATABASE_NAME = 'database_name'
        if id_provider not in providers_cache:
            providers_cache[id_provider] = metadata_provider_api.api_metadata_providers_id_get(id_provider)
        
        provider=providers_cache[id_provider]

        self._validate_model(provider.to_dict(), KEY_DATABASE_NAME)
        ProviderModel = namedtuple('ProviderModel', 'id_provider database_name data_storage_unit_id fabric_lakehouse_id fabric_workspace_id')
        database_name = provider.database_name
        return ProviderModel(id_provider = id_provider, database_name = database_name, data_storage_unit_id = provider.data_storage_unit_id, fabric_lakehouse_id = provider.fabric_lakehouse_id, fabric_workspace_id=provider.fabric_workspace_id)        

    def _get_create_table_sql_statements(self, attributes, catalog_name, database_name, fabric_lakehouse_id, fabric_workspace_id, dsu_type, table_name, table_format, recreate_table, generate_delta_table, entity_type, view_definition, storage_account_name):
        statements = []
        entity_view = None
        if entity_type == DataIngestionEntityTypeEnum.VIEW:
            if recreate_table:
                view_statement, view_name = self._get_view_definition_statements(catalog_name, database_name, table_name, view_definition)
                statements.extend(view_statement)
                entity_view = view_name
        else: 
            if recreate_table:
                statements.extend(self._get_normal_table_statements(attributes, catalog_name, database_name, fabric_lakehouse_id, fabric_workspace_id, dsu_type, table_name, table_format, storage_account_name))
            
            statements.extend(self._get_delta_statements(catalog_name, database_name, table_name, generate_delta_table))
        return statements, entity_view        

    def _get_create_database_sql_statement(self, catalog_name, database_name):
        return f"CREATE DATABASE IF NOT EXISTS `{catalog_name}`.`{database_name}`"

    def _get_view_fields(self, view_name):
        df = self.spark.sql(f"SELECT * FROM {view_name} LIMIT 1")
        return df.dtypes        

    def _set_view_attributes(self, id_entity, attributes, client):
        attributes_list = []
        order = 0
        for attribute in attributes:
            attributes_list.append({"Order": order, "HiveType": attribute[1], "Name": attribute[0], "IdEntity": id_entity})
            order = order + 1

        metadata_entity_api = MetadataEntitiesEntityApi(client)
        metadata_entity_api.api_metadata_entities_id_entity_attributes_put(id_entity=id_entity, body=attributes_list)
        return        

    def _validate_model(self, model, *keys):
        errors = [f"Missing key: {key}" for key in filter(lambda x: x not in model, keys)]
        if errors:
            raise ValueError(f"Model is invalid. Errors: {', '.join(errors)}")        

    def _get_table_format(self, table_format_id):
        DEFAULT_VALUE = PersistenceCommonEntitiesDataIngestionTableFormatEnum.DELTA
        if table_format_id is None:
            return DEFAULT_VALUE
        elif table_format_id == 1:
            return PersistenceCommonEntitiesDataIngestionTableFormatEnum.ORC
        elif table_format_id == 2:
            return PersistenceCommonEntitiesDataIngestionTableFormatEnum.PARQUET
        elif table_format_id == 3:
            return PersistenceCommonEntitiesDataIngestionTableFormatEnum.DELTA
        raise AttributeError(f"table format {table_format_id} is not supported")              

    def _get_entity_type(self, entity_type_id):
        if entity_type_id == 0:
            return DataIngestionEntityTypeEnum.OTHER
        elif entity_type_id == 1:
            return DataIngestionEntityTypeEnum.TABLE
        elif entity_type_id == 2:
            return DataIngestionEntityTypeEnum.VIEW        

    def _parse_attributes(self, attributes_from_api):
        attribute_tuples = []
        AttributeModel = namedtuple('AttributeModel', 'name hive_type is_partition is_calculated order')
        for attribute in attributes_from_api:
            name = attribute.name
            hive_type = 'STRING' if attribute.is_encrypted else attribute.hive_type
            is_partition = attribute.is_partition_column
            is_calculated = attribute.is_calculated
            order = attribute.order
            attribute_tuples.append(AttributeModel(name = name, hive_type = hive_type, is_partition = is_partition, is_calculated = is_calculated, order = order))
        return sorted(attribute_tuples, key = lambda x: x.order)
   
    def _get_delta_statements(self, catalog_name, database_name, table_name, generate_delta_table : bool):
        statements = []
        table = f"`{catalog_name}`.`{database_name}`.`{table_name}`"
        statements.append(f"ALTER TABLE {table} SET TBLPROPERTIES (delta.enableChangeDataFeed = {generate_delta_table})")   
            
        return statements

    def _get_normal_table_statements(self, attributes, catalog_name, database_name, fabric_lakehouse_id, fabric_workspace_id, dsu_type, table_name, table_format, storage_account_name):
        statements = []
        table = f"`{catalog_name}`.`{database_name}`.`{table_name}`"
        statements.append(f"DROP TABLE IF EXISTS {table}")
        columns = ', '.join([f"`{attribute.name}` {attribute.hive_type}" for attribute in attributes])

        if (dsu_type == constants.DSU_TYPE_FABRIC):
            # Fabric path
            statements.append(f"CREATE TABLE IF NOT EXISTS {table}({columns}) USING {table_format} {self._get_partition_snippet(attributes)} LOCATION 'abfss://{fabric_workspace_id}@onelake.dfs.fabric.microsoft.com/{fabric_lakehouse_id}/Files/{database_name}/{table_name}'")
        else:
            statements.append(f"CREATE TABLE IF NOT EXISTS {table}({columns}) USING {table_format} {self._get_partition_snippet(attributes)} LOCATION 'abfss://{StorageService.sanitize_container(catalog_name)}@{storage_account_name}.dfs.core.windows.net/{database_name}/{table_name}'")
            # Unity Catalog path
        return statements

    def _get_partition_snippet(self, attributes):
        entityAttributesForPartition = list(filter(lambda x: x.is_partition, attributes))
        if not entityAttributesForPartition:
            partitionByColumns = ''
        else:
            partitionByColumns = 'PARTITIONED BY (' + ', '.join(f"`{attribute.name}`" for attribute in entityAttributesForPartition) + ')'

        return partitionByColumns

    def _get_view_definition_statements(self, catalog_name, database_name, view_name, view_definition):
        statements = []
        view_name = f"`{catalog_name}`.`{database_name}`.`{view_name}`"
        statements.append(f"DROP VIEW IF EXISTS {view_name}")
        statements.append(f"CREATE VIEW IF NOT EXISTS {view_name} AS {view_definition}")
        return statements, view_name
