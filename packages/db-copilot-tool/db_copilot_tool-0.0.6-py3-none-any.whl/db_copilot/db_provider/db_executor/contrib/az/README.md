# AzExecutor
This executor will take your **Azure Resource Graph** and **Log Analytics Workspace** as datasource and enable LLM's interaction via **TSQL** query.

## Contact
Dashi (alias: `shida`)


# Quickstart

1. Things to prepare:
> - Az credential / service principal
> - A KustoDB instance, note above credential must has write access
> - Virtual table definiation, take below [example](#example) as reference, also note above credential must has read access
2. Install `az.cli==0.5.0` in your conda environment.
3. Compose your **`db_flask_config.json`** containing your az executor configuration & virtual table definiation.
> Notes:
> - Currently, access to LA only supported **1 specific** subscription (the `subscription_id` field) and **1 specific** target resource type (the `la_monitor_resource_type` field), hardcoded in **`db_flask_config.json`**
> - `recreate_kusto_db` flag is suggest to set to `false` in production, when virtual table schema will no longger be changed
4. One more thing to do comparing to other DBCopilot executor:
> Login your az.cli to credential you prepared before, you can either:
> - Run `az login` in your server, BEFORE starting your DBCopilot db flask app
> - For service principal, modify your DBCopilot db_flask.py, insert:
> ```python
>    import az.cli
>    az.cli.az(
>        f'login --service-principal -u <APP_ID> -p "{os.environ["ID_APP_SECRET"]}" -t <TENANT_ID>'
>    )
> ```

## Architecture
![Architecture](https://dev.azure.com/TScience/c6d48a8b-86c1-4670-93fa-3cebbbb17583/_apis/git/repositories/eec32394-e2b1-4b7d-9110-5ec5c313dba1/pullRequests/5975/attachments/image.png)
## Design 
![image (3).png](https://dev.azure.com/TScience/c6d48a8b-86c1-4670-93fa-3cebbbb17583/_apis/git/repositories/eec32394-e2b1-4b7d-9110-5ec5c313dba1/pullRequests/5571/attachments/image%20%283%29.png)


[one-pager doc](https://microsoftapc-my.sharepoint.com/:w:/g/personal/shida_microsoft_com/ESplPc1HW3ZCovgcmIVeXQABkvIBWFUSeqrHtXh2kJTGQA?e=BFe3eg)

## Example
### db_flask_config.json
https://microsoftapc-my.sharepoint.com/:u:/g/personal/shida_microsoft_com/EfPH9XrdBNZLk7OCedxH9xcB4cbWVIy21qZvkXdLbTKEWw?e=vAMCQg

### Sample conversation
![image.png](https://dev.azure.com/TScience/c6d48a8b-86c1-4670-93fa-3cebbbb17583/_apis/git/repositories/eec32394-e2b1-4b7d-9110-5ec5c313dba1/pullRequests/5571/attachments/image.png) 


- "are there any alerts on this cluster?"
```sql
-- Origin SQL by LLM
SELECT
    [FaultShortDescription],
    [FaultSubResourceType],
    [FaultSubResourceId],
    [FaultRemediation],
    [FaultDescription],
    [Severity]
FROM [dbo].[cluster_alerts]
WHERE [cluster_id] = '....';

-- Actual LA query executed
let _cluster_last_correlation_id=Event | where EventLog =~  'Microsoft-Windows-Health/Operational' | where TimeGenerated > ago(4h) | extend description = parse_json(RenderedDescription) | where description.IsLastMessage =~ 'true' | extend CorrelationId = tostring(description.CorrelationId) | summarize arg_max(TimeGenerated, CorrelationId) by _ResourceId | project _ResourceId,CorrelationId;
let cluster_alerts=Event| where EventLog =~ 'Microsoft-Windows-Health/Operational'| extend description = parse_json(RenderedDescription)| extend CorrelationId = tostring(description.CorrelationId)| where tostring(description.Fault.RootObjectType) == 'Microsoft.Health.EntityType.Cluster' | join kind=inner (_cluster_last_correlation_id) on CorrelationId, _ResourceId | extend Fault = description.Fault | extend FaultShortDescription = tostring(split(tostring(Fault.Type), '.')[-1]) | extend Severity = toint(Fault.Severity) | extend FaultingResourceType = tostring(split(tostring(Fault.ObjectType), '.')[-1]) | extend FaultingResourceId = tostring(Fault.ObjectId) | extend ReportedTime = datetime_add('Microsecond', tolong(Fault.Timestamp) / 10, make_datetime(1601, 1, 1)) | sort by ReportedTime asc | project     cluster_id=tolower(_ResourceId),     FaultShortDescription,     FaultSubResourceType=FaultingResourceType,     FaultSubResourceId=FaultingResourceId,     FaultRemediation=tostring(Fault.Remediation),     FaultDescription=tostring(Fault.Description),     Severity=iff(Severity == 0,  'Healthy', iff(Severity == 1,  'Warning', iff(Severity == 2,  'Critical',  'Unknown'))),     SeverityLevel=Severity,     ReportedTime;
cluster_alerts
| where (cluster_id == "....")
| project FaultShortDescription, FaultSubResourceType, FaultSubResourceId, FaultRemediation, FaultDescription, Severity
```
- "which cluster has highest number of nodes?"
```sql
-- Origin SQL by LLM
SELECT TOP 1
    [cluster_id],
    COUNT(*) as [node_count]
FROM [dbo].[nodes]
GROUP BY [cluster_id]
ORDER BY [node_count] DESC;

-- Actual ARG query executed
resources | where type =~ 'Microsoft.HybridCompute/machines' | where properties['parentClusterResourceId'] contains '/providers/microsoft.azurestackhci/clusters/' | project id, cluster_id = tolower(tostring(properties['parentClusterResourceId'])), location, resourceGroup, name, status = tostring(properties['status']), osType=tostring(properties['osType']),     osVersion=tostring(properties['osVersion']),     osSku=tostring(properties['osSku']),     domainName=tostring(properties['domainName']), logicalCoreCount=toint(properties['detectedProperties']['logicalCoreCount']),     manufacturer=tostring(properties['detectedProperties']['manufacturer']),     model=tostring(properties['detectedProperties']['model']), tagsJson=iff(isempty(tags), '{}', tostring(tags))
| summarize node_count=toint(count()) by cluster_id
| project cluster_id, node_count
| sort by node_count desc nulls first
| take int(1)
```