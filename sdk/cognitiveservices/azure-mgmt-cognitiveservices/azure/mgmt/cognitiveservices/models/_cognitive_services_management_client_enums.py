# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class AbusePenaltyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The action of AbusePenalty."""

    THROTTLE = "Throttle"
    BLOCK = "Block"


class ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enum. Indicates the action type. "Internal" refers to actions that are for internal only APIs."""

    INTERNAL = "Internal"


class ByPassSelection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Setting for trusted services."""

    NONE = "None"
    AZURE_SERVICES = "AzureServices"


class CapabilityHostKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """CapabilityHostKind."""

    AGENTS = "Agents"


class CapabilityHostProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of capability host."""

    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"
    CREATING = "Creating"
    UPDATING = "Updating"
    DELETING = "Deleting"


class CommitmentPlanProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Gets the status of the resource at the time the operation was called."""

    ACCEPTED = "Accepted"
    CREATING = "Creating"
    DELETING = "Deleting"
    MOVING = "Moving"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    CANCELED = "Canceled"


class ConnectionAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Authentication type of the connection target."""

    PAT = "PAT"
    MANAGED_IDENTITY = "ManagedIdentity"
    USERNAME_PASSWORD = "UsernamePassword"
    NONE = "None"
    SAS = "SAS"
    ACCOUNT_KEY = "AccountKey"
    SERVICE_PRINCIPAL = "ServicePrincipal"
    ACCESS_KEY = "AccessKey"
    API_KEY = "ApiKey"
    CUSTOM_KEYS = "CustomKeys"
    O_AUTH2 = "OAuth2"
    AAD = "AAD"


class ConnectionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Category of the connection."""

    PYTHON_FEED = "PythonFeed"
    CONTAINER_REGISTRY = "ContainerRegistry"
    GIT = "Git"
    S3 = "S3"
    SNOWFLAKE = "Snowflake"
    AZURE_SQL_DB = "AzureSqlDb"
    AZURE_SYNAPSE_ANALYTICS = "AzureSynapseAnalytics"
    AZURE_MY_SQL_DB = "AzureMySqlDb"
    AZURE_POSTGRES_DB = "AzurePostgresDb"
    ADLS_GEN2 = "ADLSGen2"
    REDIS = "Redis"
    API_KEY = "ApiKey"
    AZURE_OPEN_AI = "AzureOpenAI"
    AI_SERVICES = "AIServices"
    COGNITIVE_SEARCH = "CognitiveSearch"
    COGNITIVE_SERVICE = "CognitiveService"
    CUSTOM_KEYS = "CustomKeys"
    AZURE_BLOB = "AzureBlob"
    AZURE_ONE_LAKE = "AzureOneLake"
    COSMOS_DB = "CosmosDb"
    COSMOS_DB_MONGO_DB_API = "CosmosDbMongoDbApi"
    AZURE_DATA_EXPLORER = "AzureDataExplorer"
    AZURE_MARIA_DB = "AzureMariaDb"
    AZURE_DATABRICKS_DELTA_LAKE = "AzureDatabricksDeltaLake"
    AZURE_SQL_MI = "AzureSqlMi"
    AZURE_TABLE_STORAGE = "AzureTableStorage"
    AMAZON_RDS_FOR_ORACLE = "AmazonRdsForOracle"
    AMAZON_RDS_FOR_SQL_SERVER = "AmazonRdsForSqlServer"
    AMAZON_REDSHIFT = "AmazonRedshift"
    DB2 = "Db2"
    DRILL = "Drill"
    GOOGLE_BIG_QUERY = "GoogleBigQuery"
    GREENPLUM = "Greenplum"
    HBASE = "Hbase"
    HIVE = "Hive"
    IMPALA = "Impala"
    INFORMIX = "Informix"
    MARIA_DB = "MariaDb"
    MICROSOFT_ACCESS = "MicrosoftAccess"
    MY_SQL = "MySql"
    NETEZZA = "Netezza"
    ORACLE = "Oracle"
    PHOENIX = "Phoenix"
    POSTGRE_SQL = "PostgreSql"
    PRESTO = "Presto"
    SAP_OPEN_HUB = "SapOpenHub"
    SAP_BW = "SapBw"
    SAP_HANA = "SapHana"
    SAP_TABLE = "SapTable"
    SPARK = "Spark"
    SQL_SERVER = "SqlServer"
    SYBASE = "Sybase"
    TERADATA = "Teradata"
    VERTICA = "Vertica"
    PINECONE = "Pinecone"
    CASSANDRA = "Cassandra"
    COUCHBASE = "Couchbase"
    MONGO_DB_V2 = "MongoDbV2"
    MONGO_DB_ATLAS = "MongoDbAtlas"
    AMAZON_S3_COMPATIBLE = "AmazonS3Compatible"
    FILE_SERVER = "FileServer"
    FTP_SERVER = "FtpServer"
    GOOGLE_CLOUD_STORAGE = "GoogleCloudStorage"
    HDFS = "Hdfs"
    ORACLE_CLOUD_STORAGE = "OracleCloudStorage"
    SFTP = "Sftp"
    GENERIC_HTTP = "GenericHttp"
    O_DATA_REST = "ODataRest"
    ODBC = "Odbc"
    GENERIC_REST = "GenericRest"
    AMAZON_MWS = "AmazonMws"
    CONCUR = "Concur"
    DYNAMICS = "Dynamics"
    DYNAMICS_AX = "DynamicsAx"
    DYNAMICS_CRM = "DynamicsCrm"
    GOOGLE_AD_WORDS = "GoogleAdWords"
    HUBSPOT = "Hubspot"
    JIRA = "Jira"
    MAGENTO = "Magento"
    MARKETO = "Marketo"
    OFFICE365 = "Office365"
    ELOQUA = "Eloqua"
    RESPONSYS = "Responsys"
    ORACLE_SERVICE_CLOUD = "OracleServiceCloud"
    PAY_PAL = "PayPal"
    QUICK_BOOKS = "QuickBooks"
    SALESFORCE = "Salesforce"
    SALESFORCE_SERVICE_CLOUD = "SalesforceServiceCloud"
    SALESFORCE_MARKETING_CLOUD = "SalesforceMarketingCloud"
    SAP_CLOUD_FOR_CUSTOMER = "SapCloudForCustomer"
    SAP_ECC = "SapEcc"
    SERVICE_NOW = "ServiceNow"
    SHARE_POINT_ONLINE_LIST = "SharePointOnlineList"
    SHOPIFY = "Shopify"
    SQUARE = "Square"
    WEB_TABLE = "WebTable"
    XERO = "Xero"
    ZOHO = "Zoho"
    GENERIC_CONTAINER_REGISTRY = "GenericContainerRegistry"
    ELASTICSEARCH = "Elasticsearch"
    OPEN_AI = "OpenAI"
    SERP = "Serp"
    BING_LLM_SEARCH = "BingLLMSearch"
    SERVERLESS = "Serverless"
    MANAGED_ONLINE_ENDPOINT = "ManagedOnlineEndpoint"


class ConnectionGroup(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Group based on connection category."""

    AZURE = "Azure"
    AZURE_AI = "AzureAI"
    DATABASE = "Database"
    NO_SQL = "NoSQL"
    FILE = "File"
    GENERIC_PROTOCOL = "GenericProtocol"
    SERVICES_AND_APPS = "ServicesAndApps"


class ContentLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Level at which content is filtered."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of identity that created the resource."""

    USER = "User"
    APPLICATION = "Application"
    MANAGED_IDENTITY = "ManagedIdentity"
    KEY = "Key"


class DefenderForAISettingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Defender for AI state on the AI resource."""

    DISABLED = "Disabled"
    ENABLED = "Enabled"


class DeploymentModelVersionUpgradeOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Deployment model version upgrade option."""

    ONCE_NEW_DEFAULT_VERSION_AVAILABLE = "OnceNewDefaultVersionAvailable"
    ONCE_CURRENT_VERSION_EXPIRED = "OnceCurrentVersionExpired"
    NO_AUTO_UPGRADE = "NoAutoUpgrade"


class DeploymentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Gets the status of the resource at the time the operation was called."""

    ACCEPTED = "Accepted"
    CREATING = "Creating"
    DELETING = "Deleting"
    MOVING = "Moving"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    DISABLED = "Disabled"
    CANCELED = "Canceled"


class DeploymentScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Deployment scale type."""

    STANDARD = "Standard"
    MANUAL = "Manual"


class EncryptionScopeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Gets the status of the resource at the time the operation was called."""

    ACCEPTED = "Accepted"
    CREATING = "Creating"
    DELETING = "Deleting"
    MOVING = "Moving"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    CANCELED = "Canceled"


class EncryptionScopeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The encryptionScope state."""

    DISABLED = "Disabled"
    ENABLED = "Enabled"


class HostingModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Account hosting model."""

    WEB = "Web"
    CONNECTED_CONTAINER = "ConnectedContainer"
    DISCONNECTED_CONTAINER = "DisconnectedContainer"
    PROVISIONED_WEB = "ProvisionedWeb"


class KeyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """key name to generate (Key1|Key2)."""

    KEY1 = "Key1"
    KEY2 = "Key2"


class KeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Enumerates the possible value of keySource for Encryption."""

    MICROSOFT_COGNITIVE_SERVICES = "Microsoft.CognitiveServices"
    MICROSOFT_KEY_VAULT = "Microsoft.KeyVault"


class ManagedPERequirement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """ManagedPERequirement."""

    REQUIRED = "Required"
    NOT_REQUIRED = "NotRequired"
    NOT_APPLICABLE = "NotApplicable"


class ManagedPEStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """ManagedPEStatus."""

    INACTIVE = "Inactive"
    ACTIVE = "Active"
    NOT_APPLICABLE = "NotApplicable"


class ModelLifecycleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Model lifecycle status."""

    STABLE = "Stable"
    PREVIEW = "Preview"
    GENERALLY_AVAILABLE = "GenerallyAvailable"
    DEPRECATING = "Deprecating"
    DEPRECATED = "Deprecated"


class NetworkRuleAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only
    used after the bypass property has been evaluated.
    """

    ALLOW = "Allow"
    DENY = "Deny"


class NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Direction of Access Rule."""

    INBOUND = "Inbound"
    OUTBOUND = "Outbound"


class Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The intended executor of the operation; as in Resource Based Access Control (RBAC) and audit
    logs UX. Default value is "user,system".
    """

    USER = "user"
    SYSTEM = "system"
    USER_SYSTEM = "user,system"


class PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The current provisioning state."""

    SUCCEEDED = "Succeeded"
    CREATING = "Creating"
    DELETING = "Deleting"
    FAILED = "Failed"


class PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The private endpoint connection status."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Gets the status of the cognitive services account at the time the operation was called."""

    ACCEPTED = "Accepted"
    CREATING = "Creating"
    DELETING = "Deleting"
    MOVING = "Moving"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    RESOLVING_DNS = "ResolvingDNS"
    CANCELED = "Canceled"


class PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Whether or not public endpoint access is allowed for this account."""

    ENABLED = "Enabled"
    DISABLED = "Disabled"


class QuotaUsageStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Cognitive Services account quota usage status."""

    INCLUDED = "Included"
    BLOCKED = "Blocked"
    IN_OVERAGE = "InOverage"
    UNKNOWN = "Unknown"


class RaiPolicyContentSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Content source to apply the Content Filters."""

    PROMPT = "Prompt"
    COMPLETION = "Completion"


class RaiPolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Rai policy mode. The enum value mapping is as below: Default = 0, Deferred=1, Blocking=2,
    Asynchronous_filter =3. Please use 'Asynchronous_filter' after 2025-06-01. It is the same as
    'Deferred' in previous version.
    """

    DEFAULT = "Default"
    DEFERRED = "Deferred"
    BLOCKING = "Blocking"
    ASYNCHRONOUS_FILTER = "Asynchronous_filter"


class RaiPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Content Filters policy type."""

    USER_MANAGED = "UserManaged"
    SYSTEM_MANAGED = "SystemManaged"


class ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The identity type."""

    NONE = "None"
    SYSTEM_ASSIGNED = "SystemAssigned"
    USER_ASSIGNED = "UserAssigned"
    SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"


class ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The reason for restriction."""

    QUOTA_ID = "QuotaId"
    NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"


class ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of restrictions."""

    LOCATION = "Location"
    ZONE = "Zone"


class RoutingMethods(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Multiregion routing methods."""

    PRIORITY = "Priority"
    WEIGHTED = "Weighted"
    PERFORMANCE = "Performance"


class ScenarioType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies what features in AI Foundry network injection applies to. Currently only supports
    'agent' for agent scenarios. 'none' means no network injection.
    """

    NONE = "none"
    AGENT = "agent"


class SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """This field is required to be implemented by the Resource Provider if the service has more than
    one tier, but is not required on a PUT.
    """

    FREE = "Free"
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"
    ENTERPRISE = "Enterprise"


class UnitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The unit of the metric."""

    COUNT = "Count"
    BYTES = "Bytes"
    SECONDS = "Seconds"
    PERCENT = "Percent"
    COUNT_PER_SECOND = "CountPerSecond"
    BYTES_PER_SECOND = "BytesPerSecond"
    MILLISECONDS = "Milliseconds"
