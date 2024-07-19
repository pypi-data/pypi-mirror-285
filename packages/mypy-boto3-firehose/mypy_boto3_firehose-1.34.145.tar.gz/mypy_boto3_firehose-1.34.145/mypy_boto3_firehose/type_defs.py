"""
Type annotations for firehose service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_firehose/type_defs/)

Usage::

    ```python
    from mypy_boto3_firehose.type_defs import AmazonOpenSearchServerlessBufferingHintsTypeDef

    data: AmazonOpenSearchServerlessBufferingHintsTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AmazonOpenSearchServerlessS3BackupModeType,
    AmazonopensearchserviceIndexRotationPeriodType,
    AmazonopensearchserviceS3BackupModeType,
    CompressionFormatType,
    ConnectivityType,
    ContentEncodingType,
    DefaultDocumentIdFormatType,
    DeliveryStreamEncryptionStatusType,
    DeliveryStreamFailureTypeType,
    DeliveryStreamStatusType,
    DeliveryStreamTypeType,
    ElasticsearchIndexRotationPeriodType,
    ElasticsearchS3BackupModeType,
    HECEndpointTypeType,
    HttpEndpointS3BackupModeType,
    IcebergS3BackupModeType,
    KeyTypeType,
    OrcCompressionType,
    OrcFormatVersionType,
    ParquetCompressionType,
    ParquetWriterVersionType,
    ProcessorParameterNameType,
    ProcessorTypeType,
    RedshiftS3BackupModeType,
    S3BackupModeType,
    SnowflakeDataLoadingOptionType,
    SnowflakeS3BackupModeType,
    SplunkS3BackupModeType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AmazonOpenSearchServerlessBufferingHintsTypeDef",
    "AmazonOpenSearchServerlessRetryOptionsTypeDef",
    "CloudWatchLoggingOptionsTypeDef",
    "VpcConfigurationTypeDef",
    "VpcConfigurationDescriptionTypeDef",
    "AmazonopensearchserviceBufferingHintsTypeDef",
    "AmazonopensearchserviceRetryOptionsTypeDef",
    "DocumentIdOptionsTypeDef",
    "AuthenticationConfigurationTypeDef",
    "BlobTypeDef",
    "BufferingHintsTypeDef",
    "CatalogConfigurationTypeDef",
    "CopyCommandTypeDef",
    "DeliveryStreamEncryptionConfigurationInputTypeDef",
    "KinesisStreamSourceConfigurationTypeDef",
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "SchemaConfigurationTypeDef",
    "DeleteDeliveryStreamInputRequestTypeDef",
    "FailureDescriptionTypeDef",
    "DescribeDeliveryStreamInputRequestTypeDef",
    "HiveJsonSerDeOutputTypeDef",
    "OpenXJsonSerDeOutputTypeDef",
    "HiveJsonSerDeTypeDef",
    "OpenXJsonSerDeTypeDef",
    "DestinationTableConfigurationOutputTypeDef",
    "DestinationTableConfigurationTypeDef",
    "RetryOptionsTypeDef",
    "ElasticsearchBufferingHintsTypeDef",
    "ElasticsearchRetryOptionsTypeDef",
    "KMSEncryptionConfigTypeDef",
    "HttpEndpointBufferingHintsTypeDef",
    "HttpEndpointCommonAttributeTypeDef",
    "HttpEndpointConfigurationTypeDef",
    "HttpEndpointDescriptionTypeDef",
    "HttpEndpointRetryOptionsTypeDef",
    "SecretsManagerConfigurationTypeDef",
    "KinesisStreamSourceDescriptionTypeDef",
    "ListDeliveryStreamsInputRequestTypeDef",
    "ListTagsForDeliveryStreamInputRequestTypeDef",
    "TimestampTypeDef",
    "OrcSerDeOutputTypeDef",
    "OrcSerDeTypeDef",
    "ParquetSerDeTypeDef",
    "ProcessorParameterTypeDef",
    "PutRecordBatchResponseEntryTypeDef",
    "RedshiftRetryOptionsTypeDef",
    "SnowflakeBufferingHintsTypeDef",
    "SnowflakeRetryOptionsTypeDef",
    "SnowflakeRoleConfigurationTypeDef",
    "SnowflakeVpcConfigurationTypeDef",
    "SplunkBufferingHintsTypeDef",
    "SplunkRetryOptionsTypeDef",
    "StopDeliveryStreamEncryptionInputRequestTypeDef",
    "UntagDeliveryStreamInputRequestTypeDef",
    "MSKSourceDescriptionTypeDef",
    "RecordTypeDef",
    "StartDeliveryStreamEncryptionInputRequestTypeDef",
    "TagDeliveryStreamInputRequestTypeDef",
    "CreateDeliveryStreamOutputTypeDef",
    "ListDeliveryStreamsOutputTypeDef",
    "ListTagsForDeliveryStreamOutputTypeDef",
    "PutRecordOutputTypeDef",
    "DeliveryStreamEncryptionConfigurationTypeDef",
    "DeserializerOutputTypeDef",
    "DeserializerTypeDef",
    "DynamicPartitioningConfigurationTypeDef",
    "EncryptionConfigurationTypeDef",
    "HttpEndpointRequestConfigurationOutputTypeDef",
    "HttpEndpointRequestConfigurationTypeDef",
    "MSKSourceConfigurationTypeDef",
    "SerializerOutputTypeDef",
    "SerializerTypeDef",
    "ProcessorOutputTypeDef",
    "ProcessorTypeDef",
    "PutRecordBatchOutputTypeDef",
    "SourceDescriptionTypeDef",
    "PutRecordBatchInputRequestTypeDef",
    "PutRecordInputRequestTypeDef",
    "InputFormatConfigurationOutputTypeDef",
    "InputFormatConfigurationTypeDef",
    "S3DestinationConfigurationTypeDef",
    "S3DestinationDescriptionTypeDef",
    "S3DestinationUpdateTypeDef",
    "OutputFormatConfigurationOutputTypeDef",
    "OutputFormatConfigurationTypeDef",
    "ProcessingConfigurationOutputTypeDef",
    "ProcessingConfigurationTypeDef",
    "DataFormatConversionConfigurationOutputTypeDef",
    "DataFormatConversionConfigurationTypeDef",
    "AmazonOpenSearchServerlessDestinationDescriptionTypeDef",
    "AmazonopensearchserviceDestinationDescriptionTypeDef",
    "ElasticsearchDestinationDescriptionTypeDef",
    "HttpEndpointDestinationDescriptionTypeDef",
    "IcebergDestinationDescriptionTypeDef",
    "RedshiftDestinationDescriptionTypeDef",
    "SnowflakeDestinationDescriptionTypeDef",
    "SplunkDestinationDescriptionTypeDef",
    "AmazonOpenSearchServerlessDestinationConfigurationTypeDef",
    "AmazonOpenSearchServerlessDestinationUpdateTypeDef",
    "AmazonopensearchserviceDestinationConfigurationTypeDef",
    "AmazonopensearchserviceDestinationUpdateTypeDef",
    "ElasticsearchDestinationConfigurationTypeDef",
    "ElasticsearchDestinationUpdateTypeDef",
    "HttpEndpointDestinationConfigurationTypeDef",
    "HttpEndpointDestinationUpdateTypeDef",
    "IcebergDestinationConfigurationTypeDef",
    "IcebergDestinationUpdateTypeDef",
    "RedshiftDestinationConfigurationTypeDef",
    "RedshiftDestinationUpdateTypeDef",
    "SnowflakeDestinationConfigurationTypeDef",
    "SnowflakeDestinationUpdateTypeDef",
    "SplunkDestinationConfigurationTypeDef",
    "SplunkDestinationUpdateTypeDef",
    "ExtendedS3DestinationDescriptionTypeDef",
    "ExtendedS3DestinationConfigurationTypeDef",
    "ExtendedS3DestinationUpdateTypeDef",
    "DestinationDescriptionTypeDef",
    "CreateDeliveryStreamInputRequestTypeDef",
    "UpdateDestinationInputRequestTypeDef",
    "DeliveryStreamDescriptionTypeDef",
    "DescribeDeliveryStreamOutputTypeDef",
)

AmazonOpenSearchServerlessBufferingHintsTypeDef = TypedDict(
    "AmazonOpenSearchServerlessBufferingHintsTypeDef",
    {
        "IntervalInSeconds": NotRequired[int],
        "SizeInMBs": NotRequired[int],
    },
)
AmazonOpenSearchServerlessRetryOptionsTypeDef = TypedDict(
    "AmazonOpenSearchServerlessRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
CloudWatchLoggingOptionsTypeDef = TypedDict(
    "CloudWatchLoggingOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
        "LogGroupName": NotRequired[str],
        "LogStreamName": NotRequired[str],
    },
)
VpcConfigurationTypeDef = TypedDict(
    "VpcConfigurationTypeDef",
    {
        "SubnetIds": Sequence[str],
        "RoleARN": str,
        "SecurityGroupIds": Sequence[str],
    },
)
VpcConfigurationDescriptionTypeDef = TypedDict(
    "VpcConfigurationDescriptionTypeDef",
    {
        "SubnetIds": List[str],
        "RoleARN": str,
        "SecurityGroupIds": List[str],
        "VpcId": str,
    },
)
AmazonopensearchserviceBufferingHintsTypeDef = TypedDict(
    "AmazonopensearchserviceBufferingHintsTypeDef",
    {
        "IntervalInSeconds": NotRequired[int],
        "SizeInMBs": NotRequired[int],
    },
)
AmazonopensearchserviceRetryOptionsTypeDef = TypedDict(
    "AmazonopensearchserviceRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
DocumentIdOptionsTypeDef = TypedDict(
    "DocumentIdOptionsTypeDef",
    {
        "DefaultDocumentIdFormat": DefaultDocumentIdFormatType,
    },
)
AuthenticationConfigurationTypeDef = TypedDict(
    "AuthenticationConfigurationTypeDef",
    {
        "RoleARN": str,
        "Connectivity": ConnectivityType,
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
BufferingHintsTypeDef = TypedDict(
    "BufferingHintsTypeDef",
    {
        "SizeInMBs": NotRequired[int],
        "IntervalInSeconds": NotRequired[int],
    },
)
CatalogConfigurationTypeDef = TypedDict(
    "CatalogConfigurationTypeDef",
    {
        "CatalogARN": NotRequired[str],
    },
)
CopyCommandTypeDef = TypedDict(
    "CopyCommandTypeDef",
    {
        "DataTableName": str,
        "DataTableColumns": NotRequired[str],
        "CopyOptions": NotRequired[str],
    },
)
DeliveryStreamEncryptionConfigurationInputTypeDef = TypedDict(
    "DeliveryStreamEncryptionConfigurationInputTypeDef",
    {
        "KeyType": KeyTypeType,
        "KeyARN": NotRequired[str],
    },
)
KinesisStreamSourceConfigurationTypeDef = TypedDict(
    "KinesisStreamSourceConfigurationTypeDef",
    {
        "KinesisStreamARN": str,
        "RoleARN": str,
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": NotRequired[str],
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
        "HostId": NotRequired[str],
    },
)
SchemaConfigurationTypeDef = TypedDict(
    "SchemaConfigurationTypeDef",
    {
        "RoleARN": NotRequired[str],
        "CatalogId": NotRequired[str],
        "DatabaseName": NotRequired[str],
        "TableName": NotRequired[str],
        "Region": NotRequired[str],
        "VersionId": NotRequired[str],
    },
)
DeleteDeliveryStreamInputRequestTypeDef = TypedDict(
    "DeleteDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "AllowForceDelete": NotRequired[bool],
    },
)
FailureDescriptionTypeDef = TypedDict(
    "FailureDescriptionTypeDef",
    {
        "Type": DeliveryStreamFailureTypeType,
        "Details": str,
    },
)
DescribeDeliveryStreamInputRequestTypeDef = TypedDict(
    "DescribeDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Limit": NotRequired[int],
        "ExclusiveStartDestinationId": NotRequired[str],
    },
)
HiveJsonSerDeOutputTypeDef = TypedDict(
    "HiveJsonSerDeOutputTypeDef",
    {
        "TimestampFormats": NotRequired[List[str]],
    },
)
OpenXJsonSerDeOutputTypeDef = TypedDict(
    "OpenXJsonSerDeOutputTypeDef",
    {
        "ConvertDotsInJsonKeysToUnderscores": NotRequired[bool],
        "CaseInsensitive": NotRequired[bool],
        "ColumnToJsonKeyMappings": NotRequired[Dict[str, str]],
    },
)
HiveJsonSerDeTypeDef = TypedDict(
    "HiveJsonSerDeTypeDef",
    {
        "TimestampFormats": NotRequired[Sequence[str]],
    },
)
OpenXJsonSerDeTypeDef = TypedDict(
    "OpenXJsonSerDeTypeDef",
    {
        "ConvertDotsInJsonKeysToUnderscores": NotRequired[bool],
        "CaseInsensitive": NotRequired[bool],
        "ColumnToJsonKeyMappings": NotRequired[Mapping[str, str]],
    },
)
DestinationTableConfigurationOutputTypeDef = TypedDict(
    "DestinationTableConfigurationOutputTypeDef",
    {
        "DestinationTableName": str,
        "DestinationDatabaseName": str,
        "UniqueKeys": NotRequired[List[str]],
        "S3ErrorOutputPrefix": NotRequired[str],
    },
)
DestinationTableConfigurationTypeDef = TypedDict(
    "DestinationTableConfigurationTypeDef",
    {
        "DestinationTableName": str,
        "DestinationDatabaseName": str,
        "UniqueKeys": NotRequired[Sequence[str]],
        "S3ErrorOutputPrefix": NotRequired[str],
    },
)
RetryOptionsTypeDef = TypedDict(
    "RetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
ElasticsearchBufferingHintsTypeDef = TypedDict(
    "ElasticsearchBufferingHintsTypeDef",
    {
        "IntervalInSeconds": NotRequired[int],
        "SizeInMBs": NotRequired[int],
    },
)
ElasticsearchRetryOptionsTypeDef = TypedDict(
    "ElasticsearchRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
KMSEncryptionConfigTypeDef = TypedDict(
    "KMSEncryptionConfigTypeDef",
    {
        "AWSKMSKeyARN": str,
    },
)
HttpEndpointBufferingHintsTypeDef = TypedDict(
    "HttpEndpointBufferingHintsTypeDef",
    {
        "SizeInMBs": NotRequired[int],
        "IntervalInSeconds": NotRequired[int],
    },
)
HttpEndpointCommonAttributeTypeDef = TypedDict(
    "HttpEndpointCommonAttributeTypeDef",
    {
        "AttributeName": str,
        "AttributeValue": str,
    },
)
HttpEndpointConfigurationTypeDef = TypedDict(
    "HttpEndpointConfigurationTypeDef",
    {
        "Url": str,
        "Name": NotRequired[str],
        "AccessKey": NotRequired[str],
    },
)
HttpEndpointDescriptionTypeDef = TypedDict(
    "HttpEndpointDescriptionTypeDef",
    {
        "Url": NotRequired[str],
        "Name": NotRequired[str],
    },
)
HttpEndpointRetryOptionsTypeDef = TypedDict(
    "HttpEndpointRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
SecretsManagerConfigurationTypeDef = TypedDict(
    "SecretsManagerConfigurationTypeDef",
    {
        "Enabled": bool,
        "SecretARN": NotRequired[str],
        "RoleARN": NotRequired[str],
    },
)
KinesisStreamSourceDescriptionTypeDef = TypedDict(
    "KinesisStreamSourceDescriptionTypeDef",
    {
        "KinesisStreamARN": NotRequired[str],
        "RoleARN": NotRequired[str],
        "DeliveryStartTimestamp": NotRequired[datetime],
    },
)
ListDeliveryStreamsInputRequestTypeDef = TypedDict(
    "ListDeliveryStreamsInputRequestTypeDef",
    {
        "Limit": NotRequired[int],
        "DeliveryStreamType": NotRequired[DeliveryStreamTypeType],
        "ExclusiveStartDeliveryStreamName": NotRequired[str],
    },
)
ListTagsForDeliveryStreamInputRequestTypeDef = TypedDict(
    "ListTagsForDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "ExclusiveStartTagKey": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
TimestampTypeDef = Union[datetime, str]
OrcSerDeOutputTypeDef = TypedDict(
    "OrcSerDeOutputTypeDef",
    {
        "StripeSizeBytes": NotRequired[int],
        "BlockSizeBytes": NotRequired[int],
        "RowIndexStride": NotRequired[int],
        "EnablePadding": NotRequired[bool],
        "PaddingTolerance": NotRequired[float],
        "Compression": NotRequired[OrcCompressionType],
        "BloomFilterColumns": NotRequired[List[str]],
        "BloomFilterFalsePositiveProbability": NotRequired[float],
        "DictionaryKeyThreshold": NotRequired[float],
        "FormatVersion": NotRequired[OrcFormatVersionType],
    },
)
OrcSerDeTypeDef = TypedDict(
    "OrcSerDeTypeDef",
    {
        "StripeSizeBytes": NotRequired[int],
        "BlockSizeBytes": NotRequired[int],
        "RowIndexStride": NotRequired[int],
        "EnablePadding": NotRequired[bool],
        "PaddingTolerance": NotRequired[float],
        "Compression": NotRequired[OrcCompressionType],
        "BloomFilterColumns": NotRequired[Sequence[str]],
        "BloomFilterFalsePositiveProbability": NotRequired[float],
        "DictionaryKeyThreshold": NotRequired[float],
        "FormatVersion": NotRequired[OrcFormatVersionType],
    },
)
ParquetSerDeTypeDef = TypedDict(
    "ParquetSerDeTypeDef",
    {
        "BlockSizeBytes": NotRequired[int],
        "PageSizeBytes": NotRequired[int],
        "Compression": NotRequired[ParquetCompressionType],
        "EnableDictionaryCompression": NotRequired[bool],
        "MaxPaddingBytes": NotRequired[int],
        "WriterVersion": NotRequired[ParquetWriterVersionType],
    },
)
ProcessorParameterTypeDef = TypedDict(
    "ProcessorParameterTypeDef",
    {
        "ParameterName": ProcessorParameterNameType,
        "ParameterValue": str,
    },
)
PutRecordBatchResponseEntryTypeDef = TypedDict(
    "PutRecordBatchResponseEntryTypeDef",
    {
        "RecordId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
RedshiftRetryOptionsTypeDef = TypedDict(
    "RedshiftRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
SnowflakeBufferingHintsTypeDef = TypedDict(
    "SnowflakeBufferingHintsTypeDef",
    {
        "SizeInMBs": NotRequired[int],
        "IntervalInSeconds": NotRequired[int],
    },
)
SnowflakeRetryOptionsTypeDef = TypedDict(
    "SnowflakeRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
SnowflakeRoleConfigurationTypeDef = TypedDict(
    "SnowflakeRoleConfigurationTypeDef",
    {
        "Enabled": NotRequired[bool],
        "SnowflakeRole": NotRequired[str],
    },
)
SnowflakeVpcConfigurationTypeDef = TypedDict(
    "SnowflakeVpcConfigurationTypeDef",
    {
        "PrivateLinkVpceId": str,
    },
)
SplunkBufferingHintsTypeDef = TypedDict(
    "SplunkBufferingHintsTypeDef",
    {
        "IntervalInSeconds": NotRequired[int],
        "SizeInMBs": NotRequired[int],
    },
)
SplunkRetryOptionsTypeDef = TypedDict(
    "SplunkRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)
StopDeliveryStreamEncryptionInputRequestTypeDef = TypedDict(
    "StopDeliveryStreamEncryptionInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
    },
)
UntagDeliveryStreamInputRequestTypeDef = TypedDict(
    "UntagDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "TagKeys": Sequence[str],
    },
)
MSKSourceDescriptionTypeDef = TypedDict(
    "MSKSourceDescriptionTypeDef",
    {
        "MSKClusterARN": NotRequired[str],
        "TopicName": NotRequired[str],
        "AuthenticationConfiguration": NotRequired[AuthenticationConfigurationTypeDef],
        "DeliveryStartTimestamp": NotRequired[datetime],
        "ReadFromTimestamp": NotRequired[datetime],
    },
)
RecordTypeDef = TypedDict(
    "RecordTypeDef",
    {
        "Data": BlobTypeDef,
    },
)
StartDeliveryStreamEncryptionInputRequestTypeDef = TypedDict(
    "StartDeliveryStreamEncryptionInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "DeliveryStreamEncryptionConfigurationInput": NotRequired[
            DeliveryStreamEncryptionConfigurationInputTypeDef
        ],
    },
)
TagDeliveryStreamInputRequestTypeDef = TypedDict(
    "TagDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Tags": Sequence[TagTypeDef],
    },
)
CreateDeliveryStreamOutputTypeDef = TypedDict(
    "CreateDeliveryStreamOutputTypeDef",
    {
        "DeliveryStreamARN": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDeliveryStreamsOutputTypeDef = TypedDict(
    "ListDeliveryStreamsOutputTypeDef",
    {
        "DeliveryStreamNames": List[str],
        "HasMoreDeliveryStreams": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForDeliveryStreamOutputTypeDef = TypedDict(
    "ListTagsForDeliveryStreamOutputTypeDef",
    {
        "Tags": List[TagTypeDef],
        "HasMoreTags": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutRecordOutputTypeDef = TypedDict(
    "PutRecordOutputTypeDef",
    {
        "RecordId": str,
        "Encrypted": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeliveryStreamEncryptionConfigurationTypeDef = TypedDict(
    "DeliveryStreamEncryptionConfigurationTypeDef",
    {
        "KeyARN": NotRequired[str],
        "KeyType": NotRequired[KeyTypeType],
        "Status": NotRequired[DeliveryStreamEncryptionStatusType],
        "FailureDescription": NotRequired[FailureDescriptionTypeDef],
    },
)
DeserializerOutputTypeDef = TypedDict(
    "DeserializerOutputTypeDef",
    {
        "OpenXJsonSerDe": NotRequired[OpenXJsonSerDeOutputTypeDef],
        "HiveJsonSerDe": NotRequired[HiveJsonSerDeOutputTypeDef],
    },
)
DeserializerTypeDef = TypedDict(
    "DeserializerTypeDef",
    {
        "OpenXJsonSerDe": NotRequired[OpenXJsonSerDeTypeDef],
        "HiveJsonSerDe": NotRequired[HiveJsonSerDeTypeDef],
    },
)
DynamicPartitioningConfigurationTypeDef = TypedDict(
    "DynamicPartitioningConfigurationTypeDef",
    {
        "RetryOptions": NotRequired[RetryOptionsTypeDef],
        "Enabled": NotRequired[bool],
    },
)
EncryptionConfigurationTypeDef = TypedDict(
    "EncryptionConfigurationTypeDef",
    {
        "NoEncryptionConfig": NotRequired[Literal["NoEncryption"]],
        "KMSEncryptionConfig": NotRequired[KMSEncryptionConfigTypeDef],
    },
)
HttpEndpointRequestConfigurationOutputTypeDef = TypedDict(
    "HttpEndpointRequestConfigurationOutputTypeDef",
    {
        "ContentEncoding": NotRequired[ContentEncodingType],
        "CommonAttributes": NotRequired[List[HttpEndpointCommonAttributeTypeDef]],
    },
)
HttpEndpointRequestConfigurationTypeDef = TypedDict(
    "HttpEndpointRequestConfigurationTypeDef",
    {
        "ContentEncoding": NotRequired[ContentEncodingType],
        "CommonAttributes": NotRequired[Sequence[HttpEndpointCommonAttributeTypeDef]],
    },
)
MSKSourceConfigurationTypeDef = TypedDict(
    "MSKSourceConfigurationTypeDef",
    {
        "MSKClusterARN": str,
        "TopicName": str,
        "AuthenticationConfiguration": AuthenticationConfigurationTypeDef,
        "ReadFromTimestamp": NotRequired[TimestampTypeDef],
    },
)
SerializerOutputTypeDef = TypedDict(
    "SerializerOutputTypeDef",
    {
        "ParquetSerDe": NotRequired[ParquetSerDeTypeDef],
        "OrcSerDe": NotRequired[OrcSerDeOutputTypeDef],
    },
)
SerializerTypeDef = TypedDict(
    "SerializerTypeDef",
    {
        "ParquetSerDe": NotRequired[ParquetSerDeTypeDef],
        "OrcSerDe": NotRequired[OrcSerDeTypeDef],
    },
)
ProcessorOutputTypeDef = TypedDict(
    "ProcessorOutputTypeDef",
    {
        "Type": ProcessorTypeType,
        "Parameters": NotRequired[List[ProcessorParameterTypeDef]],
    },
)
ProcessorTypeDef = TypedDict(
    "ProcessorTypeDef",
    {
        "Type": ProcessorTypeType,
        "Parameters": NotRequired[Sequence[ProcessorParameterTypeDef]],
    },
)
PutRecordBatchOutputTypeDef = TypedDict(
    "PutRecordBatchOutputTypeDef",
    {
        "FailedPutCount": int,
        "Encrypted": bool,
        "RequestResponses": List[PutRecordBatchResponseEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SourceDescriptionTypeDef = TypedDict(
    "SourceDescriptionTypeDef",
    {
        "KinesisStreamSourceDescription": NotRequired[KinesisStreamSourceDescriptionTypeDef],
        "MSKSourceDescription": NotRequired[MSKSourceDescriptionTypeDef],
    },
)
PutRecordBatchInputRequestTypeDef = TypedDict(
    "PutRecordBatchInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Records": Sequence[RecordTypeDef],
    },
)
PutRecordInputRequestTypeDef = TypedDict(
    "PutRecordInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Record": RecordTypeDef,
    },
)
InputFormatConfigurationOutputTypeDef = TypedDict(
    "InputFormatConfigurationOutputTypeDef",
    {
        "Deserializer": NotRequired[DeserializerOutputTypeDef],
    },
)
InputFormatConfigurationTypeDef = TypedDict(
    "InputFormatConfigurationTypeDef",
    {
        "Deserializer": NotRequired[DeserializerTypeDef],
    },
)
S3DestinationConfigurationTypeDef = TypedDict(
    "S3DestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)
S3DestinationDescriptionTypeDef = TypedDict(
    "S3DestinationDescriptionTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "BufferingHints": BufferingHintsTypeDef,
        "CompressionFormat": CompressionFormatType,
        "EncryptionConfiguration": EncryptionConfigurationTypeDef,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)
S3DestinationUpdateTypeDef = TypedDict(
    "S3DestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "BucketARN": NotRequired[str],
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)
OutputFormatConfigurationOutputTypeDef = TypedDict(
    "OutputFormatConfigurationOutputTypeDef",
    {
        "Serializer": NotRequired[SerializerOutputTypeDef],
    },
)
OutputFormatConfigurationTypeDef = TypedDict(
    "OutputFormatConfigurationTypeDef",
    {
        "Serializer": NotRequired[SerializerTypeDef],
    },
)
ProcessingConfigurationOutputTypeDef = TypedDict(
    "ProcessingConfigurationOutputTypeDef",
    {
        "Enabled": NotRequired[bool],
        "Processors": NotRequired[List[ProcessorOutputTypeDef]],
    },
)
ProcessingConfigurationTypeDef = TypedDict(
    "ProcessingConfigurationTypeDef",
    {
        "Enabled": NotRequired[bool],
        "Processors": NotRequired[Sequence[ProcessorTypeDef]],
    },
)
DataFormatConversionConfigurationOutputTypeDef = TypedDict(
    "DataFormatConversionConfigurationOutputTypeDef",
    {
        "SchemaConfiguration": NotRequired[SchemaConfigurationTypeDef],
        "InputFormatConfiguration": NotRequired[InputFormatConfigurationOutputTypeDef],
        "OutputFormatConfiguration": NotRequired[OutputFormatConfigurationOutputTypeDef],
        "Enabled": NotRequired[bool],
    },
)
DataFormatConversionConfigurationTypeDef = TypedDict(
    "DataFormatConversionConfigurationTypeDef",
    {
        "SchemaConfiguration": NotRequired[SchemaConfigurationTypeDef],
        "InputFormatConfiguration": NotRequired[InputFormatConfigurationTypeDef],
        "OutputFormatConfiguration": NotRequired[OutputFormatConfigurationTypeDef],
        "Enabled": NotRequired[bool],
    },
)
AmazonOpenSearchServerlessDestinationDescriptionTypeDef = TypedDict(
    "AmazonOpenSearchServerlessDestinationDescriptionTypeDef",
    {
        "RoleARN": NotRequired[str],
        "CollectionEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "BufferingHints": NotRequired[AmazonOpenSearchServerlessBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonOpenSearchServerlessRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonOpenSearchServerlessS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfigurationDescription": NotRequired[VpcConfigurationDescriptionTypeDef],
    },
)
AmazonopensearchserviceDestinationDescriptionTypeDef = TypedDict(
    "AmazonopensearchserviceDestinationDescriptionTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[AmazonopensearchserviceIndexRotationPeriodType],
        "BufferingHints": NotRequired[AmazonopensearchserviceBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonopensearchserviceRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonopensearchserviceS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfigurationDescription": NotRequired[VpcConfigurationDescriptionTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)
ElasticsearchDestinationDescriptionTypeDef = TypedDict(
    "ElasticsearchDestinationDescriptionTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[ElasticsearchIndexRotationPeriodType],
        "BufferingHints": NotRequired[ElasticsearchBufferingHintsTypeDef],
        "RetryOptions": NotRequired[ElasticsearchRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[ElasticsearchS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfigurationDescription": NotRequired[VpcConfigurationDescriptionTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)
HttpEndpointDestinationDescriptionTypeDef = TypedDict(
    "HttpEndpointDestinationDescriptionTypeDef",
    {
        "EndpointConfiguration": NotRequired[HttpEndpointDescriptionTypeDef],
        "BufferingHints": NotRequired[HttpEndpointBufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "RequestConfiguration": NotRequired[HttpEndpointRequestConfigurationOutputTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[HttpEndpointRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[HttpEndpointS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
IcebergDestinationDescriptionTypeDef = TypedDict(
    "IcebergDestinationDescriptionTypeDef",
    {
        "DestinationTableConfigurationList": NotRequired[
            List[DestinationTableConfigurationOutputTypeDef]
        ],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "S3BackupMode": NotRequired[IcebergS3BackupModeType],
        "RetryOptions": NotRequired[RetryOptionsTypeDef],
        "RoleARN": NotRequired[str],
        "CatalogConfiguration": NotRequired[CatalogConfigurationTypeDef],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
    },
)
RedshiftDestinationDescriptionTypeDef = TypedDict(
    "RedshiftDestinationDescriptionTypeDef",
    {
        "RoleARN": str,
        "ClusterJDBCURL": str,
        "CopyCommand": CopyCommandTypeDef,
        "S3DestinationDescription": S3DestinationDescriptionTypeDef,
        "Username": NotRequired[str],
        "RetryOptions": NotRequired[RedshiftRetryOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "S3BackupMode": NotRequired[RedshiftS3BackupModeType],
        "S3BackupDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
SnowflakeDestinationDescriptionTypeDef = TypedDict(
    "SnowflakeDestinationDescriptionTypeDef",
    {
        "AccountUrl": NotRequired[str],
        "User": NotRequired[str],
        "Database": NotRequired[str],
        "Schema": NotRequired[str],
        "Table": NotRequired[str],
        "SnowflakeRoleConfiguration": NotRequired[SnowflakeRoleConfigurationTypeDef],
        "DataLoadingOption": NotRequired[SnowflakeDataLoadingOptionType],
        "MetaDataColumnName": NotRequired[str],
        "ContentColumnName": NotRequired[str],
        "SnowflakeVpcConfiguration": NotRequired[SnowflakeVpcConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[SnowflakeRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SnowflakeS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
        "BufferingHints": NotRequired[SnowflakeBufferingHintsTypeDef],
    },
)
SplunkDestinationDescriptionTypeDef = TypedDict(
    "SplunkDestinationDescriptionTypeDef",
    {
        "HECEndpoint": NotRequired[str],
        "HECEndpointType": NotRequired[HECEndpointTypeType],
        "HECToken": NotRequired[str],
        "HECAcknowledgmentTimeoutInSeconds": NotRequired[int],
        "RetryOptions": NotRequired[SplunkRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SplunkS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "BufferingHints": NotRequired[SplunkBufferingHintsTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
AmazonOpenSearchServerlessDestinationConfigurationTypeDef = TypedDict(
    "AmazonOpenSearchServerlessDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "IndexName": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "CollectionEndpoint": NotRequired[str],
        "BufferingHints": NotRequired[AmazonOpenSearchServerlessBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonOpenSearchServerlessRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonOpenSearchServerlessS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfiguration": NotRequired[VpcConfigurationTypeDef],
    },
)
AmazonOpenSearchServerlessDestinationUpdateTypeDef = TypedDict(
    "AmazonOpenSearchServerlessDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "CollectionEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "BufferingHints": NotRequired[AmazonOpenSearchServerlessBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonOpenSearchServerlessRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)
AmazonopensearchserviceDestinationConfigurationTypeDef = TypedDict(
    "AmazonopensearchserviceDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "IndexName": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[AmazonopensearchserviceIndexRotationPeriodType],
        "BufferingHints": NotRequired[AmazonopensearchserviceBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonopensearchserviceRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonopensearchserviceS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfiguration": NotRequired[VpcConfigurationTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)
AmazonopensearchserviceDestinationUpdateTypeDef = TypedDict(
    "AmazonopensearchserviceDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[AmazonopensearchserviceIndexRotationPeriodType],
        "BufferingHints": NotRequired[AmazonopensearchserviceBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonopensearchserviceRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)
ElasticsearchDestinationConfigurationTypeDef = TypedDict(
    "ElasticsearchDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "IndexName": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[ElasticsearchIndexRotationPeriodType],
        "BufferingHints": NotRequired[ElasticsearchBufferingHintsTypeDef],
        "RetryOptions": NotRequired[ElasticsearchRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[ElasticsearchS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfiguration": NotRequired[VpcConfigurationTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)
ElasticsearchDestinationUpdateTypeDef = TypedDict(
    "ElasticsearchDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[ElasticsearchIndexRotationPeriodType],
        "BufferingHints": NotRequired[ElasticsearchBufferingHintsTypeDef],
        "RetryOptions": NotRequired[ElasticsearchRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)
HttpEndpointDestinationConfigurationTypeDef = TypedDict(
    "HttpEndpointDestinationConfigurationTypeDef",
    {
        "EndpointConfiguration": HttpEndpointConfigurationTypeDef,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "BufferingHints": NotRequired[HttpEndpointBufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "RequestConfiguration": NotRequired[HttpEndpointRequestConfigurationTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[HttpEndpointRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[HttpEndpointS3BackupModeType],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
HttpEndpointDestinationUpdateTypeDef = TypedDict(
    "HttpEndpointDestinationUpdateTypeDef",
    {
        "EndpointConfiguration": NotRequired[HttpEndpointConfigurationTypeDef],
        "BufferingHints": NotRequired[HttpEndpointBufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "RequestConfiguration": NotRequired[HttpEndpointRequestConfigurationTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[HttpEndpointRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[HttpEndpointS3BackupModeType],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
IcebergDestinationConfigurationTypeDef = TypedDict(
    "IcebergDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "CatalogConfiguration": CatalogConfigurationTypeDef,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "DestinationTableConfigurationList": NotRequired[
            Sequence[DestinationTableConfigurationTypeDef]
        ],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[IcebergS3BackupModeType],
        "RetryOptions": NotRequired[RetryOptionsTypeDef],
    },
)
IcebergDestinationUpdateTypeDef = TypedDict(
    "IcebergDestinationUpdateTypeDef",
    {
        "DestinationTableConfigurationList": NotRequired[
            Sequence[DestinationTableConfigurationTypeDef]
        ],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[IcebergS3BackupModeType],
        "RetryOptions": NotRequired[RetryOptionsTypeDef],
        "RoleARN": NotRequired[str],
        "CatalogConfiguration": NotRequired[CatalogConfigurationTypeDef],
        "S3Configuration": NotRequired[S3DestinationConfigurationTypeDef],
    },
)
RedshiftDestinationConfigurationTypeDef = TypedDict(
    "RedshiftDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "ClusterJDBCURL": str,
        "CopyCommand": CopyCommandTypeDef,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "Username": NotRequired[str],
        "Password": NotRequired[str],
        "RetryOptions": NotRequired[RedshiftRetryOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[RedshiftS3BackupModeType],
        "S3BackupConfiguration": NotRequired[S3DestinationConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
RedshiftDestinationUpdateTypeDef = TypedDict(
    "RedshiftDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "ClusterJDBCURL": NotRequired[str],
        "CopyCommand": NotRequired[CopyCommandTypeDef],
        "Username": NotRequired[str],
        "Password": NotRequired[str],
        "RetryOptions": NotRequired[RedshiftRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[RedshiftS3BackupModeType],
        "S3BackupUpdate": NotRequired[S3DestinationUpdateTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
SnowflakeDestinationConfigurationTypeDef = TypedDict(
    "SnowflakeDestinationConfigurationTypeDef",
    {
        "AccountUrl": str,
        "Database": str,
        "Schema": str,
        "Table": str,
        "RoleARN": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "PrivateKey": NotRequired[str],
        "KeyPassphrase": NotRequired[str],
        "User": NotRequired[str],
        "SnowflakeRoleConfiguration": NotRequired[SnowflakeRoleConfigurationTypeDef],
        "DataLoadingOption": NotRequired[SnowflakeDataLoadingOptionType],
        "MetaDataColumnName": NotRequired[str],
        "ContentColumnName": NotRequired[str],
        "SnowflakeVpcConfiguration": NotRequired[SnowflakeVpcConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "RetryOptions": NotRequired[SnowflakeRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SnowflakeS3BackupModeType],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
        "BufferingHints": NotRequired[SnowflakeBufferingHintsTypeDef],
    },
)
SnowflakeDestinationUpdateTypeDef = TypedDict(
    "SnowflakeDestinationUpdateTypeDef",
    {
        "AccountUrl": NotRequired[str],
        "PrivateKey": NotRequired[str],
        "KeyPassphrase": NotRequired[str],
        "User": NotRequired[str],
        "Database": NotRequired[str],
        "Schema": NotRequired[str],
        "Table": NotRequired[str],
        "SnowflakeRoleConfiguration": NotRequired[SnowflakeRoleConfigurationTypeDef],
        "DataLoadingOption": NotRequired[SnowflakeDataLoadingOptionType],
        "MetaDataColumnName": NotRequired[str],
        "ContentColumnName": NotRequired[str],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[SnowflakeRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SnowflakeS3BackupModeType],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
        "BufferingHints": NotRequired[SnowflakeBufferingHintsTypeDef],
    },
)
SplunkDestinationConfigurationTypeDef = TypedDict(
    "SplunkDestinationConfigurationTypeDef",
    {
        "HECEndpoint": str,
        "HECEndpointType": HECEndpointTypeType,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "HECToken": NotRequired[str],
        "HECAcknowledgmentTimeoutInSeconds": NotRequired[int],
        "RetryOptions": NotRequired[SplunkRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SplunkS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "BufferingHints": NotRequired[SplunkBufferingHintsTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
SplunkDestinationUpdateTypeDef = TypedDict(
    "SplunkDestinationUpdateTypeDef",
    {
        "HECEndpoint": NotRequired[str],
        "HECEndpointType": NotRequired[HECEndpointTypeType],
        "HECToken": NotRequired[str],
        "HECAcknowledgmentTimeoutInSeconds": NotRequired[int],
        "RetryOptions": NotRequired[SplunkRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SplunkS3BackupModeType],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "BufferingHints": NotRequired[SplunkBufferingHintsTypeDef],
        "SecretsManagerConfiguration": NotRequired[SecretsManagerConfigurationTypeDef],
    },
)
ExtendedS3DestinationDescriptionTypeDef = TypedDict(
    "ExtendedS3DestinationDescriptionTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "BufferingHints": BufferingHintsTypeDef,
        "CompressionFormat": CompressionFormatType,
        "EncryptionConfiguration": EncryptionConfigurationTypeDef,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationOutputTypeDef],
        "S3BackupMode": NotRequired[S3BackupModeType],
        "S3BackupDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "DataFormatConversionConfiguration": NotRequired[
            DataFormatConversionConfigurationOutputTypeDef
        ],
        "DynamicPartitioningConfiguration": NotRequired[DynamicPartitioningConfigurationTypeDef],
        "FileExtension": NotRequired[str],
        "CustomTimeZone": NotRequired[str],
    },
)
ExtendedS3DestinationConfigurationTypeDef = TypedDict(
    "ExtendedS3DestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[S3BackupModeType],
        "S3BackupConfiguration": NotRequired[S3DestinationConfigurationTypeDef],
        "DataFormatConversionConfiguration": NotRequired[DataFormatConversionConfigurationTypeDef],
        "DynamicPartitioningConfiguration": NotRequired[DynamicPartitioningConfigurationTypeDef],
        "FileExtension": NotRequired[str],
        "CustomTimeZone": NotRequired[str],
    },
)
ExtendedS3DestinationUpdateTypeDef = TypedDict(
    "ExtendedS3DestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "BucketARN": NotRequired[str],
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[S3BackupModeType],
        "S3BackupUpdate": NotRequired[S3DestinationUpdateTypeDef],
        "DataFormatConversionConfiguration": NotRequired[DataFormatConversionConfigurationTypeDef],
        "DynamicPartitioningConfiguration": NotRequired[DynamicPartitioningConfigurationTypeDef],
        "FileExtension": NotRequired[str],
        "CustomTimeZone": NotRequired[str],
    },
)
DestinationDescriptionTypeDef = TypedDict(
    "DestinationDescriptionTypeDef",
    {
        "DestinationId": str,
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ExtendedS3DestinationDescription": NotRequired[ExtendedS3DestinationDescriptionTypeDef],
        "RedshiftDestinationDescription": NotRequired[RedshiftDestinationDescriptionTypeDef],
        "ElasticsearchDestinationDescription": NotRequired[
            ElasticsearchDestinationDescriptionTypeDef
        ],
        "AmazonopensearchserviceDestinationDescription": NotRequired[
            AmazonopensearchserviceDestinationDescriptionTypeDef
        ],
        "SplunkDestinationDescription": NotRequired[SplunkDestinationDescriptionTypeDef],
        "HttpEndpointDestinationDescription": NotRequired[
            HttpEndpointDestinationDescriptionTypeDef
        ],
        "SnowflakeDestinationDescription": NotRequired[SnowflakeDestinationDescriptionTypeDef],
        "AmazonOpenSearchServerlessDestinationDescription": NotRequired[
            AmazonOpenSearchServerlessDestinationDescriptionTypeDef
        ],
        "IcebergDestinationDescription": NotRequired[IcebergDestinationDescriptionTypeDef],
    },
)
CreateDeliveryStreamInputRequestTypeDef = TypedDict(
    "CreateDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "DeliveryStreamType": NotRequired[DeliveryStreamTypeType],
        "KinesisStreamSourceConfiguration": NotRequired[KinesisStreamSourceConfigurationTypeDef],
        "DeliveryStreamEncryptionConfigurationInput": NotRequired[
            DeliveryStreamEncryptionConfigurationInputTypeDef
        ],
        "S3DestinationConfiguration": NotRequired[S3DestinationConfigurationTypeDef],
        "ExtendedS3DestinationConfiguration": NotRequired[
            ExtendedS3DestinationConfigurationTypeDef
        ],
        "RedshiftDestinationConfiguration": NotRequired[RedshiftDestinationConfigurationTypeDef],
        "ElasticsearchDestinationConfiguration": NotRequired[
            ElasticsearchDestinationConfigurationTypeDef
        ],
        "AmazonopensearchserviceDestinationConfiguration": NotRequired[
            AmazonopensearchserviceDestinationConfigurationTypeDef
        ],
        "SplunkDestinationConfiguration": NotRequired[SplunkDestinationConfigurationTypeDef],
        "HttpEndpointDestinationConfiguration": NotRequired[
            HttpEndpointDestinationConfigurationTypeDef
        ],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "AmazonOpenSearchServerlessDestinationConfiguration": NotRequired[
            AmazonOpenSearchServerlessDestinationConfigurationTypeDef
        ],
        "MSKSourceConfiguration": NotRequired[MSKSourceConfigurationTypeDef],
        "SnowflakeDestinationConfiguration": NotRequired[SnowflakeDestinationConfigurationTypeDef],
        "IcebergDestinationConfiguration": NotRequired[IcebergDestinationConfigurationTypeDef],
    },
)
UpdateDestinationInputRequestTypeDef = TypedDict(
    "UpdateDestinationInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "CurrentDeliveryStreamVersionId": str,
        "DestinationId": str,
        "S3DestinationUpdate": NotRequired[S3DestinationUpdateTypeDef],
        "ExtendedS3DestinationUpdate": NotRequired[ExtendedS3DestinationUpdateTypeDef],
        "RedshiftDestinationUpdate": NotRequired[RedshiftDestinationUpdateTypeDef],
        "ElasticsearchDestinationUpdate": NotRequired[ElasticsearchDestinationUpdateTypeDef],
        "AmazonopensearchserviceDestinationUpdate": NotRequired[
            AmazonopensearchserviceDestinationUpdateTypeDef
        ],
        "SplunkDestinationUpdate": NotRequired[SplunkDestinationUpdateTypeDef],
        "HttpEndpointDestinationUpdate": NotRequired[HttpEndpointDestinationUpdateTypeDef],
        "AmazonOpenSearchServerlessDestinationUpdate": NotRequired[
            AmazonOpenSearchServerlessDestinationUpdateTypeDef
        ],
        "SnowflakeDestinationUpdate": NotRequired[SnowflakeDestinationUpdateTypeDef],
        "IcebergDestinationUpdate": NotRequired[IcebergDestinationUpdateTypeDef],
    },
)
DeliveryStreamDescriptionTypeDef = TypedDict(
    "DeliveryStreamDescriptionTypeDef",
    {
        "DeliveryStreamName": str,
        "DeliveryStreamARN": str,
        "DeliveryStreamStatus": DeliveryStreamStatusType,
        "DeliveryStreamType": DeliveryStreamTypeType,
        "VersionId": str,
        "Destinations": List[DestinationDescriptionTypeDef],
        "HasMoreDestinations": bool,
        "FailureDescription": NotRequired[FailureDescriptionTypeDef],
        "DeliveryStreamEncryptionConfiguration": NotRequired[
            DeliveryStreamEncryptionConfigurationTypeDef
        ],
        "CreateTimestamp": NotRequired[datetime],
        "LastUpdateTimestamp": NotRequired[datetime],
        "Source": NotRequired[SourceDescriptionTypeDef],
    },
)
DescribeDeliveryStreamOutputTypeDef = TypedDict(
    "DescribeDeliveryStreamOutputTypeDef",
    {
        "DeliveryStreamDescription": DeliveryStreamDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
