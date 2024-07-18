from sidraconnector.sdk.log.logging import Logger
from datetime import datetime
from dateutil.parser import parse, ParserError

class TabularIngestionPostProcessing():
    def __init__(self, spark):
        self.spark = spark
        self.logger = Logger(spark, self.__class__.__name__)

    def process(self, data_intake_process_item_id : str, provider_item_id : str, run_id : str, execution_date : datetime):  
        execution_date = self._get_execution_date(execution_date)
        # Data Quality validations
        self._data_quality_report_generation(provider_item_id, run_id, execution_date)
   
    def _data_quality_report_generation(self, provider_item_id, run_id, execution_date):
        try:
            import sidradataquality.sdk.databricks.utils as ValidationDatabricksUtils
            databricks_utils = ValidationDatabricksUtils.Utils(self.spark)

            if databricks_utils.service_is_enabled():
                self.logger.debug(f"Creating data quality report for provider '{provider_item_id}'.")
                from sidradataquality.sdk.report.reportservice import ReportService
                report_service = ReportService(self.spark)
                report_service.generate_report(provider_item_id, run_id, execution_date)
            else:
                self.logger.debug("Data Quality not deployed in current DSU.")

        except Exception:
            self.logger.exception(f"Exception on Provider {provider_item_id} generating the Data Quality report.")

    def _get_execution_date(self, intake_execution_date):
        try:
            if type(intake_execution_date) is datetime:
                execution_date = intake_execution_date
            else:
                execution_date = parse(intake_execution_date)
        except ParserError:
            self.logger.error(f"Incorrect format for the execution date: {intake_execution_date}")
        except Exception:
            self.logger.error(f"Incorrect type for the execution date: {intake_execution_date}")

        return execution_date