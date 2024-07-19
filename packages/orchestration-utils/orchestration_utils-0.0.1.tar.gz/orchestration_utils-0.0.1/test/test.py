from orchestration_utils.etl_control import ETLController

etlcontroller = ETLController("hello", environment="dev")

print(etlcontroller._pipeline_name)
