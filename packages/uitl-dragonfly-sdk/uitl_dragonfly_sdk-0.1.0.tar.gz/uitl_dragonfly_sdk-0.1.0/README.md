# UTIL Dragonfly SDK
## Introduction
This is the SDK for [Dragonfly, The Data Quality Tool](https://dragonflydatahq.com/).
Dragonfly is a data quality monitoring and assessment tool developed by [Upshot Ideas Technology Lab](http://upshotideas.com/).
This is the SDK for use in your applications to trigger a quality assessment evaluation on demand.
Feel free to get in touch with [Dragonfly support](https://dragonflydatahq.com/contact.html) for more information or help.

## Usage
### Prerequisites
Before you begin, please acquire the following details:
#### Auth Server URL
Example: `https://authenticate.dragonflydatahq.com/realms/dragonfly`  
This need not be a publicly accessible URL. Your deployment may be configured to work only within your organization's network and the link may appear to be internal.

#### Client Credentials
Example:
```
client_id = "df-plugin"
client_secret = "asdf78687ADf78asndFAsdf786asdfasdcvfa3"
```  
You can find these by logging into your auth server as an admin and navigating to the Dragonfly realm/clients, and finding your "plugin" client.

#### API Server URL
Example: `https://apibackend.dragonflydatahq.com/dragonfly`  
This need not be a publicly accessible URL. Your deployment may be configured to work only within your organization's network and the link may appear to be internal.

### Learning Through Examples
#### Simple API call to Dragonfly
```python
from uitl_dragonfly_sdk.DragonflyClient import DragonflyClient

df_client = DragonflyClient(client_id="df-plugin",
                            client_secret="asdf78687ADf78asndFAsdf786asdfasdcvfa3",
                            auth_server_realm_baseurl="https://authenticate.dragonflydatahq.com/realms/dragonfly",
                            api_server_baseurl="https://apibackend.dragonflydatahq.com/dragonfly")

output = df_client.run_health_report(pipeline_id=1, component_id=43, log_result=True, fail_on_low_dcr=True)
print(output)
```

#### Changing the minimum DCR threshold
The default value is `95.0`. To completely disable the check, set the value to `-1`.
```python
df_client.minimum_dcr = 80.0
```

#### Invoking with names
```python
output = df_client.run_health_report(pipeline_name="Sales Pipeline", component_name="Aggregate Sales Report", log_result=True, fail_on_low_dcr=True)
```

#### Evaluating the whole pipeline
```python
output = df_client.run_health_report(pipeline_name="Sales Pipeline", log_result=True, fail_on_low_dcr=True)
```
OR
```python
output = df_client.run_health_report(pipeline_id=1, log_result=True, fail_on_low_dcr=True)
```

#### Using environment variables
```shell
export UITL_DRAGONFLY_CLIENT_ID="df-plugin"
export UITL_DRAGONFLY_CLIENT_SECRET="asdf78687ADf78asndFAsdf786asdfasdcvfa3"
export UITL_DRAGONFLY_AUTH_SERVER_REALM_BASEURL="https://authenticate.dragonflydatahq.com/realms/dragonfly"
export UITL_DRAGONFLY_API_SERVER_BASEURL="https://apibackend.dragonflydatahq.com/dragonfly"
export UITL_DRAGONFLY_MINIMUM_DCR=-1.0

python3 run_dragonfly.py
```

```python
# run_dragonfly.py
from uitl_dragonfly_sdk.DragonflyClient import DragonflyClient

df_client = DragonflyClient()
output = df_client.run_health_report(pipeline_id=1, component_id=43, log_result=True, fail_on_low_dcr=True)
print(output)
```

### Documentation
#### Dragonfly Client
Below is the list of constructor parameters for the `DragonflyClient`.

| parameter name            | environment variable                     | description                                                  | default value | Mandatory |
|---------------------------|------------------------------------------|--------------------------------------------------------------|---------------|-----------|
| client_id                 | UITL_DRAGONFLY_CLIENT_ID                 | Client ID to authenticate with the Dragonfly auth server     | ""            | Y         |
| client_secret             | UITL_DRAGONFLY_CLIENT_SECRET             | Client Secret to authenticate with the Dragonfly auth server | ""            | Y         |
| auth_server_realm_baseurl | UITL_DRAGONFLY_AUTH_SERVER_REALM_BASEURL | Base URL of the Dragonfly auth server's Dragonfly realm      | ""            | Y         |
| api_server_baseurl        | UITL_DRAGONFLY_API_SERVER_BASEURL        | Base URL of the Dragonfly API server                         | ""            | Y         |


### Running Health Report
#### Params
`DragonflyClient#run_health_report` can be invoked with the following parameters

| parameter       | description                                                                                                                                               | default value | Mandatory                      |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|--------------------------------|
| pipeline_name   | Name of the pipeline to run verification                                                                                                                  | ""            | If pipeline_id not provided.   |
| pipeline_id     | ID of the pipeline to run verification                                                                                                                    | 0             | If pipeline_name not provided. |
| component_name  | This is a filter to restrict the verification up-to the component name in the provided pipeline.                                                          | ""            | N                              |
| component_id    | This is a filter to restrict the verification up-to the component ID in the provided pipeline.                                                            | 0             | N                              |
| run_id          | A unique identifier for a health run to connect disjointed or partial runs of the pipeline. If not provided, a new RunId will be automatically generated. | ""            | N                              |
| log_result      | If to log formatted verification result to the default output stream. All the information is included in the returned result object.                      | False         | N                              |
| fail_on_low_dcr | If to throw exception when the result of the verification is below the set DCR value (minimum_dcr) on the client.                                         | False         | N                              |


#### Output
Here is a sample output object:
```json
{
  "id": 1, // Health verification execution Id, automatically generated and assgined
  "clientId": 10000, // Client Id on Dragonfly
  "name": "Laptop Sales Report Simple", // Name of the pipeline
  "filtered": true, // If the run was partial, filtered with componentId or full
  "runId": "7ef257d7-7c17-4852-a7d3-f74edc8a76a3", // Provided run_id or randomly generated
  "reportRequestId": "9116517c-b35a-4d41-bf7e-0ebe3fa2c389", // Request Id
  "nodes":[{
    "id": 43, // Id of the component in the pipeline
    "type": "PROCESS", // type of the compnoent
    "name": "Aggregate Sale Calc Process", // name of the component
    "health":{
      "value": 100.0, // health result value.
      "executedChecks":[{ // list of checks executed on this component in this run and their results.
        "value": 100.0, // check's result.
        "meta": { // metadata captured in the check.
          "min_units_sold": "100",
          "health": "true",
          "min_revenue": "1000.0"
        },
        "error": null,
        "checkId": 3, // Id of the the check
        "healthCheckName": "" // name of the check
      }],
      "error": null,
      "dependenciesHealth": 50.0, // health of the dependencies of this component, if any are present.
      "meta": {}
    }
  }, {
    "id": 42,
    "type": "PROCESS",
    "name": "Data Ingestion ETL",
    "health": {
      "value": 0.0,
      "executedChecks": [{
        "value": 0.0,
        "meta": {
          "max_batch_date": "2024-06-26",
          "health": "false"
        },
        "error": null,
        "checkId": 1,
        "healthCheckName": "Laptop sales data should be recent"
      }, {
        "value": 0.0,
        "meta": {
          "max_batch_date": "2024-06-25",
          "health": "false"
        },
        "error": null,
        "checkId": 2,
        "healthCheckName": "Tablet sales data should be recent"
      }],
      "error": null,
      "dependenciesHealth": 0.0,
      "meta": {}
    }
  }],
  "edges": [{ // relationship of the components in the filtered/full pipeline.
    "source": 43,
    "target": 42,
    "weight": 1.0
  }]
}
```


#### Environment Variables
Additional environment variables that can be set

| environment variable       | description                                                                                      | default value | Mandatory |
|----------------------------|--------------------------------------------------------------------------------------------------|---------------|-----------|
| UITL_DRAGONFLY_MINIMUM_DCR | Minimum DCR threshold. If the quality is reported below this value, the SDK throws an exception. | 95.0          | N         |