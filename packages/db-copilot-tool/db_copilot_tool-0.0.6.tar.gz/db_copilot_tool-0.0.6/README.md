nl2sql tool for prompt flow

# How to create promptflow endpoint your workspace
## 1. Prepare your workspace
Open your workspace in Azure ML studio portal <br>
Example Studio Portal URL: <br>
https://main.ml.azure.com/?wsid=/subscriptions/1b75927d-563b-49d2-bf8a-772f7d6a170e/resourceGroups/ragdev/providers/Microsoft.MachineLearningServices/workspaces/RAGDev&flight=promptDesigner&tid=72f988bf-86f1-41af-91ab-2d7cd011db47
## 2. Create a ci (compute instance)
Create a ci with name with prefix "ci-lin-cpu-0-" , for example ci-lin-cpu-0-alan
## 3. Config Customer Application on your ci
### 3.1 Application Name
Application Name has to be: promptflow-runtime
### 3.2 Port
Target Port and Published Port have to be: 8080
### 3.3 Docker Image
docker image can be modulesdkpreview/prt:tag. <br>
For example: 
modulesdkpreview/prt:v20230420-140738
### 3.4 Restart ci
## 4. Install dbcopilot on your ci
### 4.1 Open Terminal of your ci
### 4.2 upload whl files to your ci
dbcopilot-0.2.0-py3-none-any.whl (get it from https://dev.azure.com/TScience/NL2Code/_artifacts/feed/AIMS.TScience.NL2Code/PyPI/dbcopilot/overview/0.3.0)<br>
db_copilot_tool-0.1.0-py3-none-any.whl <br>
embeddingstore-0.0.1-py3-none-any.whl (optional) <br>
promptflow_sdk-0.0.1-py3-none-any.whl (optional) <br>
### 4.3 Install whl files in promptflow container
Find your promptflow container id with command: docker ps -a <br>
Copy whl files to promptflow container with command: docker cp xxx.whl <container_id>:/xxx.whl <br>
Login promptflow container with command: docker exec -it <container_id> /bin/bash <br>
install whl files with command: pip install xxx.whl
### 4.4 Install Microsoft ODBC in promptflow container
Reference Doc: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=ubuntu18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#18 <br>
Commands: <br>
apt-get update <br>
apt-get install -y curl lsb-core <br>
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - <br>
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list <br>
apt-get update <br>
ACCEPT_EULA=Y apt-get install -y msodbcsql18 <br>
apt-get install -y unixodbc-dev <br>
### 4.5 Restart promptflow container
exit
docker stop container_id <br>
docker start container_id <br>

## 5. Copy Local DB file to promptflow container (optional)

## 6. Get promptflow endpoint url
promptflow endpoint url can be found in the ci overview page, click "promptflow-runtime" link <br>