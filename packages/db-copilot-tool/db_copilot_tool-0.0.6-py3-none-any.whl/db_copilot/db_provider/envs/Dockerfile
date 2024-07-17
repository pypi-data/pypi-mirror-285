FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest

# ODBC
# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
# install SQL Server tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

# Python installs
COPY requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt

