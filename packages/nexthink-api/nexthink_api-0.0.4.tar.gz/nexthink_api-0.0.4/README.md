# nexthink_api Module

This module provides functionality to interact with the Nexthink **Infinity** API.

## Installation

To install the Nexthink module, use the following command:

```bash
pip install nexthink_api
```


# Usage

## authentification:
```python
from nexthink_api import NxtApiClient, NxtRegionName

# Fill these in with your Nexthink environment details
client_id = 'your_client_id'
client_secret = 'your_client_secret'
tenant = "tenant_string"
# proxies = { https=os.getenv('https_proxy'), http=os.getenv('http_proxy')}

# Create an instance of the client with the proxy parameters and credentials
nxtClient = NxtApiClient(tenant, 
                         NxtRegionName.eu, 
                         client_id=client_id, 
                         client_secret=client_secret,
                         # proxies=proxies       # If you need a proxy
                         )
```
## Enrichment:

```python
from datetime import datetime, timedelta
from nexthink_api import (
  NxtIdentification,
  NxtIdentificationName,
  NxtField,
  NxtFieldName,
  NxtEnrichment,
  NxtEndpoint,
  NxtEnrichmentRequest,
) 

# Will update Custom Fields for PC12345
# The 3 Custom Fields have been created before in Nexthink admin
# For demo, the 3 CF are named cf_demo1, cf_demo2, cf_demo3

# Data to set in CF
now = datetime.now()
tomorrow = now + timedelta(days=1)
yesterday = now - timedelta(days=1)

# Identification of the device where CF will be updated
identification = NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value="PC12345")

# The 3 CF with  their value (value should be a string)
field1 = NxtField(name=NxtFieldName.CUSTOM_DEVICE, value=str(now), customValue="cf_demo1")
field2 = NxtField(name=NxtFieldName.CUSTOM_DEVICE, value=str(tomorrow), customValue="cf_demo2")
field3 = NxtField(name=NxtFieldName.CUSTOM_DEVICE, value=str(yesterday), customValue="cf_demo3")

# Create the Enrichment record
enrichments = [NxtEnrichment(identification=[identification], fields=[field1, field2, field3])]
# Prepare the enrichment Request object
enrichmentRequest = NxtEnrichmentRequest(enrichments=enrichments, domain="test_fdj")

# This is the way to see the json payload of the enrichment request 
payload = enrichmentRequest.model_dump()
print(payload)

# use the client to run perform the enrichment on the Enrichment endpoint
response = nxtClient.run_enrichment(endpoint=NxtEndpoint.Enrichment, data=enrichmentRequest)
print(response)
```

## NQL Requests:

* NQL Queries are optimized for relatively small requests at a high frequency. 

The NQL query must have been previously created in the Nexthink admin (admin/NQL API queries)
For the example, the NQL query ID will be #get_pilot_collector_devices

The NQL query is :
```nql
devices | where collector.update_group == 'Pilot'
```

```python
from nexthink_api import (
    NxtNqlApiExecuteRequest,
    NxtEndpoint
)

# Query ID
MyRequestID = "#get_pilot_collector_devices"
# Create a nql request object 
nqlRequest = NxtNqlApiExecuteRequest(queryId=MyRequestID)
# Use the client to run the query on the Nql endpoint
response = nxtClient.run_nql(NxtEndpoint.Nql, data=nqlRequest)
print(response)
```

## NQL Export:

* NQL Export are optimized for large queries at low frequency

This request is asynchronous. You start the execution and get an exportID.
You have to wait the end of export by querying the exportID status.
Once the export is ready, you will get the S3 URL to download the export.

The NQL query must have been previously created in the Nexthink admin (admin/NQL API queries)
For the example, the NQL query ID will be **#get_windows_devices**.

The NQL query is : 
```nql
devices | where operating_system.platform == windows
```
```python
from nexthink_api import (
    NxtNqlApiExecuteRequest,
    NxtEndpoint,
    NxtNqlApiExportResponse,
    NxtErrorResponse
)

# Query ID
MyRequestID = "#get_pilot_collector_devices"
# Create a nql request object 
nqlRequest = NxtNqlApiExecuteRequest(queryId=MyRequestID)
# This time, use the client to run the query on the NqlExport endpoint
response = nxtClient.run_nql(NxtEndpoint.NqlExport, data=nqlRequest)
# If response is NqlNqlApiExportResponse, there is no error
if isinstance(response, NxtNqlApiExportResponse):
    # Response will contain the exportID
    print(response)
    # The client can wait for end of query
    response = nxtClient.wait_status(response)
    # This response will contain the S3 URL
    print(response)
    # You can use the nxtClient to download the export
    # The export will be a csv data 
    res = nxtClient.download_export(response)
    # Print first 5 lines
    first_lines = [ line for line in res.text.split('\n')[:5]]
    for line in first_lines:
        print(line)
# Probably an NxtErrorResponse
else:
    print(response)
```

## API Classes
All Classes of the nexthink_api are build with Pydantic, so they can be serialize to dict 
with the method **model_dump()**

In the same way, any serialized version of a class can be transformed into an object 
with the **model_validate(json_data)** method.
