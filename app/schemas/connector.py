from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

class ConnectorType(str, Enum):
    CSV = "csv"
    PDF = "pdf"
    TXT = "txt"
    XLSX = "xlsx"
    IMAGE = "image"
    CLICKHOUSE = "clickhouse"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    REST = "rest"
    SOAP = "soap"
    GRAPHQL = "graphql"
    FTP = "ftp"
    SFTP = "sftp"
    SSH = "ssh"
    TELNET = "telnet"
    SNMP = "snmp"
    LDAP = "ldap"
    SMTP = "smtp"
    POP3 = "pop3"
    IMAP = "imap"
    DNS = "dns"
    DHCP = "dhcp"
    NTP = "ntp"
    SYSLOG = "syslog"
    NETFLOW = "netflow"
    IPFIX = "ipfix"
    SFLOW = "sflow"
    JFLOW = "jflow"
    NETCONF = "netconf"
    RESTCONF = "restconf"
    YANG = "yang"
    OPENCONFIG = "openconfig"
    NETMIKO = "netmiko"
    NAPALM = "napalm"
    ANSIBLE = "ansible"
    TERRAFORM = "terraform"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    VMWARE = "vmware"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    OCI = "oci"
    ALIBABA = "alibaba"
    IBM = "ibm"
    ORACLE = "oracle"
    SAP = "sap"
    SALESFORCE = "salesforce"
    WORKDAY = "workday"
    SERVICENOW = "servicenow"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    BITBUCKET = "bitbucket"
    GITHUB = "github"
    GITLAB = "gitlab"
    JENKINS = "jenkins"
    TEAMCITY = "teamcity"
    BAMBOO = "bamboo"
    ARTIFACTORY = "artifactory"
    NEXUS = "nexus"
    SONARQUBE = "sonarqube"
    FORTIFY = "fortify"
    CHECKMARX = "checkmarx"
    VERACODE = "veracode"
    BLACKDUCK = "blackduck"
    WHITESOURCE = "whitesource"
    SNYK = "snyk"
    DEPENDABOT = "dependabot"
    RENOVATE = "renovate"
    GREENKEEPER = "greenkeeper"
    NPM_AUDIT = "npm_audit"
    YARN_AUDIT = "yarn_audit"
    PIP_AUDIT = "pip_audit"
    BUNDLE_AUDIT = "bundle_audit"
    COMPOSER_AUDIT = "composer_audit"
    CARGO_AUDIT = "cargo_audit"
    GO_AUDIT = "go_audit"
    MAVEN_AUDIT = "maven_audit"
    GRADLE_AUDIT = "gradle_audit"
    NUGET_AUDIT = "nuget_audit"
    PUB_AUDIT = "pub_audit"
    SWIFT_AUDIT = "swift_audit"
    COCOAPODS_AUDIT = "cocoapods_audit"
    CARTHAGE_AUDIT = "carthage_audit"
    SPM_AUDIT = "spm_audit"

class ConnectorConfig(BaseModel):
    name: str
    type: str  # e.g., "clickhouse", "postgres", etc.
    connector_type: str  # "source" or "destination"
    file_path: Optional[str] = None
    connection_details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class ConnectorCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: ConnectorType
    config: Dict[str, Any]

class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class ConnectorResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: ConnectorType
    config: Dict[str, Any]
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConnectorListResponse(BaseModel):
    total: int
    items: List[ConnectorResponse]

class WriteRequest(BaseModel):
    """Schema for writing data to a destination connector."""
    connector_id: str
    table_name: str
    data: List[Dict[str, Any]]  # List of records to write
    table_schema: Optional[Dict[str, str]] = None  # Optional schema definition for creating table
