"""
Type annotations for connect service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_connect/type_defs/)

Usage::

    ```python
    from mypy_boto3_connect.type_defs import ActionSummaryTypeDef

    data: ActionSummaryTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence, Union

from .literals import (
    ActionTypeType,
    AgentAvailabilityTimerType,
    AgentStatusStateType,
    AgentStatusTypeType,
    AnsweringMachineDetectionStatusType,
    ArtifactStatusType,
    BehaviorTypeType,
    ChannelType,
    ChatEventTypeType,
    ContactFlowModuleStateType,
    ContactFlowModuleStatusType,
    ContactFlowStateType,
    ContactFlowStatusType,
    ContactFlowTypeType,
    ContactInitiationMethodType,
    ContactStateType,
    CurrentMetricNameType,
    DirectoryTypeType,
    EndpointTypeType,
    EvaluationFormQuestionTypeType,
    EvaluationFormScoringModeType,
    EvaluationFormScoringStatusType,
    EvaluationFormSingleSelectQuestionDisplayModeType,
    EvaluationFormVersionStatusType,
    EvaluationStatusType,
    EventSourceNameType,
    FailureReasonCodeType,
    FileStatusTypeType,
    GroupingType,
    HierarchyGroupMatchTypeType,
    HistoricalMetricNameType,
    HoursOfOperationDaysType,
    InstanceAttributeTypeType,
    InstanceStatusType,
    InstanceStorageResourceTypeType,
    IntegrationTypeType,
    IntervalPeriodType,
    LexVersionType,
    MeetingFeatureStatusType,
    MonitorCapabilityType,
    NumberComparisonTypeType,
    NumericQuestionPropertyAutomationLabelType,
    ParticipantRoleType,
    ParticipantTimerTypeType,
    PhoneNumberCountryCodeType,
    PhoneNumberTypeType,
    PhoneNumberWorkflowStatusType,
    PhoneTypeType,
    QueueStatusType,
    QueueTypeType,
    QuickConnectTypeType,
    RealTimeContactAnalysisOutputTypeType,
    RealTimeContactAnalysisSegmentTypeType,
    RealTimeContactAnalysisSentimentLabelType,
    RealTimeContactAnalysisStatusType,
    RealTimeContactAnalysisSupportedChannelType,
    ReferenceStatusType,
    ReferenceTypeType,
    RehydrationTypeType,
    RoutingCriteriaStepStatusType,
    RulePublishStatusType,
    SearchContactsMatchTypeType,
    SearchContactsTimeRangeTypeType,
    SingleSelectQuestionRuleCategoryAutomationConditionType,
    SortableFieldNameType,
    SortOrderType,
    SourceTypeType,
    StatisticType,
    StorageTypeType,
    StringComparisonTypeType,
    TaskTemplateFieldTypeType,
    TaskTemplateStatusType,
    TimerEligibleParticipantRolesType,
    TrafficDistributionGroupStatusType,
    TrafficTypeType,
    UnitType,
    UseCaseTypeType,
    ViewStatusType,
    ViewTypeType,
    VocabularyLanguageCodeType,
    VocabularyStateType,
    VoiceRecordingTrackType,
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
    "ActionSummaryTypeDef",
    "ActivateEvaluationFormRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "DistributionTypeDef",
    "QueueReferenceTypeDef",
    "AgentHierarchyGroupTypeDef",
    "AgentHierarchyGroupsTypeDef",
    "DeviceInfoTypeDef",
    "ParticipantCapabilitiesTypeDef",
    "AudioQualityMetricsInfoTypeDef",
    "AgentStatusReferenceTypeDef",
    "StringConditionTypeDef",
    "AgentStatusSummaryTypeDef",
    "AgentStatusTypeDef",
    "AgentsCriteriaTypeDef",
    "AnalyticsDataAssociationResultTypeDef",
    "AnswerMachineDetectionConfigTypeDef",
    "ApplicationExtraOutputTypeDef",
    "ApplicationOutputTypeDef",
    "ApplicationTypeDef",
    "AssociateAnalyticsDataSetRequestRequestTypeDef",
    "AssociateApprovedOriginRequestRequestTypeDef",
    "LexBotTypeDef",
    "LexV2BotTypeDef",
    "AssociateDefaultVocabularyRequestRequestTypeDef",
    "AssociateFlowRequestRequestTypeDef",
    "AssociateLambdaFunctionRequestRequestTypeDef",
    "AssociatePhoneNumberContactFlowRequestRequestTypeDef",
    "AssociateQueueQuickConnectsRequestRequestTypeDef",
    "AssociateSecurityKeyRequestRequestTypeDef",
    "AssociateTrafficDistributionGroupUserRequestRequestTypeDef",
    "UserProficiencyTypeDef",
    "AttachedFileErrorTypeDef",
    "CreatedByInfoTypeDef",
    "AttachmentReferenceTypeDef",
    "AttendeeTypeDef",
    "HierarchyGroupConditionTypeDef",
    "TagConditionTypeDef",
    "AttributeTypeDef",
    "AudioFeaturesTypeDef",
    "AuthenticationProfileSummaryTypeDef",
    "AuthenticationProfileTypeDef",
    "AvailableNumberSummaryTypeDef",
    "BatchAssociateAnalyticsDataSetRequestRequestTypeDef",
    "ErrorResultTypeDef",
    "BatchDisassociateAnalyticsDataSetRequestRequestTypeDef",
    "BatchGetAttachedFileMetadataRequestRequestTypeDef",
    "BatchGetFlowAssociationRequestRequestTypeDef",
    "FlowAssociationSummaryTypeDef",
    "FailedRequestTypeDef",
    "SuccessfulRequestTypeDef",
    "CampaignTypeDef",
    "ChatEventTypeDef",
    "ChatMessageTypeDef",
    "ChatStreamingConfigurationTypeDef",
    "ClaimPhoneNumberRequestRequestTypeDef",
    "PhoneNumberStatusTypeDef",
    "CompleteAttachedFileUploadRequestRequestTypeDef",
    "NumberConditionTypeDef",
    "EndpointTypeDef",
    "ContactFilterTypeDef",
    "ContactFlowModuleSummaryTypeDef",
    "ContactFlowModuleTypeDef",
    "ContactFlowSummaryTypeDef",
    "ContactFlowTypeDef",
    "ContactSearchSummaryAgentInfoTypeDef",
    "ContactSearchSummaryQueueInfoTypeDef",
    "CustomerVoiceActivityTypeDef",
    "DisconnectDetailsTypeDef",
    "QueueInfoTypeDef",
    "SegmentAttributeValueTypeDef",
    "WisdomInfoTypeDef",
    "CreateAgentStatusRequestRequestTypeDef",
    "CreateContactFlowModuleRequestRequestTypeDef",
    "CreateContactFlowRequestRequestTypeDef",
    "EvaluationFormItemUnionTypeDef",
    "EvaluationFormScoringStrategyTypeDef",
    "CreateInstanceRequestRequestTypeDef",
    "CreateIntegrationAssociationRequestRequestTypeDef",
    "ParticipantDetailsToAddTypeDef",
    "ParticipantTokenCredentialsTypeDef",
    "CreatePersistentContactAssociationRequestRequestTypeDef",
    "PredefinedAttributeValuesTypeDef",
    "CreatePromptRequestRequestTypeDef",
    "OutboundCallerConfigTypeDef",
    "RuleTriggerEventSourceTypeDef",
    "CreateTrafficDistributionGroupRequestRequestTypeDef",
    "CreateUseCaseRequestRequestTypeDef",
    "CreateUserHierarchyGroupRequestRequestTypeDef",
    "UserIdentityInfoTypeDef",
    "UserPhoneConfigTypeDef",
    "ViewInputContentTypeDef",
    "CreateViewVersionRequestRequestTypeDef",
    "CreateVocabularyRequestRequestTypeDef",
    "CredentialsTypeDef",
    "CrossChannelBehaviorTypeDef",
    "CurrentMetricTypeDef",
    "CurrentMetricSortCriteriaTypeDef",
    "DateReferenceTypeDef",
    "DeactivateEvaluationFormRequestRequestTypeDef",
    "DefaultVocabularyTypeDef",
    "DeleteAttachedFileRequestRequestTypeDef",
    "DeleteContactEvaluationRequestRequestTypeDef",
    "DeleteContactFlowModuleRequestRequestTypeDef",
    "DeleteContactFlowRequestRequestTypeDef",
    "DeleteEvaluationFormRequestRequestTypeDef",
    "DeleteHoursOfOperationRequestRequestTypeDef",
    "DeleteInstanceRequestRequestTypeDef",
    "DeleteIntegrationAssociationRequestRequestTypeDef",
    "DeletePredefinedAttributeRequestRequestTypeDef",
    "DeletePromptRequestRequestTypeDef",
    "DeleteQueueRequestRequestTypeDef",
    "DeleteQuickConnectRequestRequestTypeDef",
    "DeleteRoutingProfileRequestRequestTypeDef",
    "DeleteRuleRequestRequestTypeDef",
    "DeleteSecurityProfileRequestRequestTypeDef",
    "DeleteTaskTemplateRequestRequestTypeDef",
    "DeleteTrafficDistributionGroupRequestRequestTypeDef",
    "DeleteUseCaseRequestRequestTypeDef",
    "DeleteUserHierarchyGroupRequestRequestTypeDef",
    "DeleteUserRequestRequestTypeDef",
    "DeleteViewRequestRequestTypeDef",
    "DeleteViewVersionRequestRequestTypeDef",
    "DeleteVocabularyRequestRequestTypeDef",
    "DescribeAgentStatusRequestRequestTypeDef",
    "DescribeAuthenticationProfileRequestRequestTypeDef",
    "DescribeContactEvaluationRequestRequestTypeDef",
    "DescribeContactFlowModuleRequestRequestTypeDef",
    "DescribeContactFlowRequestRequestTypeDef",
    "DescribeContactRequestRequestTypeDef",
    "DescribeEvaluationFormRequestRequestTypeDef",
    "DescribeHoursOfOperationRequestRequestTypeDef",
    "DescribeInstanceAttributeRequestRequestTypeDef",
    "DescribeInstanceRequestRequestTypeDef",
    "DescribeInstanceStorageConfigRequestRequestTypeDef",
    "DescribePhoneNumberRequestRequestTypeDef",
    "DescribePredefinedAttributeRequestRequestTypeDef",
    "DescribePromptRequestRequestTypeDef",
    "PromptTypeDef",
    "DescribeQueueRequestRequestTypeDef",
    "DescribeQuickConnectRequestRequestTypeDef",
    "DescribeRoutingProfileRequestRequestTypeDef",
    "DescribeRuleRequestRequestTypeDef",
    "DescribeSecurityProfileRequestRequestTypeDef",
    "SecurityProfileTypeDef",
    "DescribeTrafficDistributionGroupRequestRequestTypeDef",
    "TrafficDistributionGroupTypeDef",
    "DescribeUserHierarchyGroupRequestRequestTypeDef",
    "DescribeUserHierarchyStructureRequestRequestTypeDef",
    "DescribeUserRequestRequestTypeDef",
    "DescribeViewRequestRequestTypeDef",
    "DescribeVocabularyRequestRequestTypeDef",
    "VocabularyTypeDef",
    "RoutingProfileReferenceTypeDef",
    "DisassociateAnalyticsDataSetRequestRequestTypeDef",
    "DisassociateApprovedOriginRequestRequestTypeDef",
    "DisassociateFlowRequestRequestTypeDef",
    "DisassociateInstanceStorageConfigRequestRequestTypeDef",
    "DisassociateLambdaFunctionRequestRequestTypeDef",
    "DisassociateLexBotRequestRequestTypeDef",
    "DisassociatePhoneNumberContactFlowRequestRequestTypeDef",
    "DisassociateQueueQuickConnectsRequestRequestTypeDef",
    "RoutingProfileQueueReferenceTypeDef",
    "DisassociateSecurityKeyRequestRequestTypeDef",
    "DisassociateTrafficDistributionGroupUserRequestRequestTypeDef",
    "UserProficiencyDisassociateTypeDef",
    "DisconnectReasonTypeDef",
    "DismissUserContactRequestRequestTypeDef",
    "DownloadUrlMetadataTypeDef",
    "EmailReferenceTypeDef",
    "EncryptionConfigTypeDef",
    "EvaluationAnswerDataTypeDef",
    "NumericQuestionPropertyValueAutomationTypeDef",
    "EvaluationFormNumericQuestionOptionTypeDef",
    "EvaluationFormSectionOutputTypeDef",
    "EvaluationFormSectionTypeDef",
    "SingleSelectQuestionRuleCategoryAutomationTypeDef",
    "EvaluationFormSingleSelectQuestionOptionTypeDef",
    "EvaluationFormSummaryTypeDef",
    "EvaluationFormVersionSummaryTypeDef",
    "EvaluationScoreTypeDef",
    "EvaluationNoteTypeDef",
    "EventBridgeActionDefinitionTypeDef",
    "ExpiryTypeDef",
    "FieldValueUnionOutputTypeDef",
    "FieldValueUnionTypeDef",
    "FilterV2TypeDef",
    "FiltersTypeDef",
    "GetAttachedFileRequestRequestTypeDef",
    "GetContactAttributesRequestRequestTypeDef",
    "GetFederationTokenRequestRequestTypeDef",
    "GetFlowAssociationRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "TimestampTypeDef",
    "IntervalDetailsTypeDef",
    "GetPromptFileRequestRequestTypeDef",
    "GetTaskTemplateRequestRequestTypeDef",
    "GetTrafficDistributionRequestRequestTypeDef",
    "HierarchyGroupSummaryReferenceTypeDef",
    "HierarchyGroupSummaryTypeDef",
    "HierarchyLevelTypeDef",
    "HierarchyLevelUpdateTypeDef",
    "ThresholdTypeDef",
    "HoursOfOperationTimeSliceTypeDef",
    "HoursOfOperationSummaryTypeDef",
    "ImportPhoneNumberRequestRequestTypeDef",
    "InstanceStatusReasonTypeDef",
    "KinesisFirehoseConfigTypeDef",
    "KinesisStreamConfigTypeDef",
    "InstanceSummaryTypeDef",
    "IntegrationAssociationSummaryTypeDef",
    "TaskTemplateFieldIdentifierTypeDef",
    "ListAgentStatusRequestRequestTypeDef",
    "ListAnalyticsDataAssociationsRequestRequestTypeDef",
    "ListApprovedOriginsRequestRequestTypeDef",
    "ListAuthenticationProfilesRequestRequestTypeDef",
    "ListBotsRequestRequestTypeDef",
    "ListContactEvaluationsRequestRequestTypeDef",
    "ListContactFlowModulesRequestRequestTypeDef",
    "ListContactFlowsRequestRequestTypeDef",
    "ListContactReferencesRequestRequestTypeDef",
    "ListDefaultVocabulariesRequestRequestTypeDef",
    "ListEvaluationFormVersionsRequestRequestTypeDef",
    "ListEvaluationFormsRequestRequestTypeDef",
    "ListFlowAssociationsRequestRequestTypeDef",
    "ListHoursOfOperationsRequestRequestTypeDef",
    "ListInstanceAttributesRequestRequestTypeDef",
    "ListInstanceStorageConfigsRequestRequestTypeDef",
    "ListInstancesRequestRequestTypeDef",
    "ListIntegrationAssociationsRequestRequestTypeDef",
    "ListLambdaFunctionsRequestRequestTypeDef",
    "ListLexBotsRequestRequestTypeDef",
    "ListPhoneNumbersRequestRequestTypeDef",
    "PhoneNumberSummaryTypeDef",
    "ListPhoneNumbersSummaryTypeDef",
    "ListPhoneNumbersV2RequestRequestTypeDef",
    "ListPredefinedAttributesRequestRequestTypeDef",
    "PredefinedAttributeSummaryTypeDef",
    "ListPromptsRequestRequestTypeDef",
    "PromptSummaryTypeDef",
    "ListQueueQuickConnectsRequestRequestTypeDef",
    "QuickConnectSummaryTypeDef",
    "ListQueuesRequestRequestTypeDef",
    "QueueSummaryTypeDef",
    "ListQuickConnectsRequestRequestTypeDef",
    "ListRealtimeContactAnalysisSegmentsV2RequestRequestTypeDef",
    "ListRoutingProfileQueuesRequestRequestTypeDef",
    "RoutingProfileQueueConfigSummaryTypeDef",
    "ListRoutingProfilesRequestRequestTypeDef",
    "RoutingProfileSummaryTypeDef",
    "ListRulesRequestRequestTypeDef",
    "ListSecurityKeysRequestRequestTypeDef",
    "SecurityKeyTypeDef",
    "ListSecurityProfileApplicationsRequestRequestTypeDef",
    "ListSecurityProfilePermissionsRequestRequestTypeDef",
    "ListSecurityProfilesRequestRequestTypeDef",
    "SecurityProfileSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTaskTemplatesRequestRequestTypeDef",
    "TaskTemplateMetadataTypeDef",
    "ListTrafficDistributionGroupUsersRequestRequestTypeDef",
    "TrafficDistributionGroupUserSummaryTypeDef",
    "ListTrafficDistributionGroupsRequestRequestTypeDef",
    "TrafficDistributionGroupSummaryTypeDef",
    "ListUseCasesRequestRequestTypeDef",
    "UseCaseTypeDef",
    "ListUserHierarchyGroupsRequestRequestTypeDef",
    "ListUserProficienciesRequestRequestTypeDef",
    "ListUsersRequestRequestTypeDef",
    "UserSummaryTypeDef",
    "ListViewVersionsRequestRequestTypeDef",
    "ViewVersionSummaryTypeDef",
    "ListViewsRequestRequestTypeDef",
    "ViewSummaryTypeDef",
    "MediaPlacementTypeDef",
    "MetricFilterV2OutputTypeDef",
    "MetricFilterV2TypeDef",
    "MetricIntervalTypeDef",
    "ThresholdV2TypeDef",
    "MonitorContactRequestRequestTypeDef",
    "ParticipantDetailsTypeDef",
    "NotificationRecipientTypeOutputTypeDef",
    "NotificationRecipientTypeTypeDef",
    "NumberReferenceTypeDef",
    "ParticipantTimerValueTypeDef",
    "PauseContactRequestRequestTypeDef",
    "PersistentChatTypeDef",
    "PhoneNumberQuickConnectConfigTypeDef",
    "PredefinedAttributeValuesOutputTypeDef",
    "PredefinedAttributeValuesExtraOutputTypeDef",
    "PutUserStatusRequestRequestTypeDef",
    "QueueQuickConnectConfigTypeDef",
    "UserQuickConnectConfigTypeDef",
    "RealTimeContactAnalysisAttachmentTypeDef",
    "RealTimeContactAnalysisCharacterIntervalTypeDef",
    "RealTimeContactAnalysisTimeDataTypeDef",
    "StringReferenceTypeDef",
    "UrlReferenceTypeDef",
    "ReferenceTypeDef",
    "ReleasePhoneNumberRequestRequestTypeDef",
    "ReplicateInstanceRequestRequestTypeDef",
    "TagSearchConditionTypeDef",
    "ResumeContactRecordingRequestRequestTypeDef",
    "ResumeContactRequestRequestTypeDef",
    "SubmitAutoEvaluationActionDefinitionTypeDef",
    "SearchAvailablePhoneNumbersRequestRequestTypeDef",
    "SortTypeDef",
    "SearchPredefinedAttributesRequestRequestTypeDef",
    "TagSetTypeDef",
    "SecurityProfileSearchSummaryTypeDef",
    "SearchVocabulariesRequestRequestTypeDef",
    "VocabularySummaryTypeDef",
    "SearchableContactAttributesCriteriaTypeDef",
    "SignInDistributionTypeDef",
    "UploadUrlMetadataTypeDef",
    "StartContactEvaluationRequestRequestTypeDef",
    "VoiceRecordingConfigurationTypeDef",
    "StopContactRecordingRequestRequestTypeDef",
    "StopContactStreamingRequestRequestTypeDef",
    "SuspendContactRecordingRequestRequestTypeDef",
    "TagContactRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TranscriptCriteriaTypeDef",
    "TransferContactRequestRequestTypeDef",
    "UntagContactRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateAgentStatusRequestRequestTypeDef",
    "UpdateAuthenticationProfileRequestRequestTypeDef",
    "UpdateContactAttributesRequestRequestTypeDef",
    "UpdateContactFlowContentRequestRequestTypeDef",
    "UpdateContactFlowMetadataRequestRequestTypeDef",
    "UpdateContactFlowModuleContentRequestRequestTypeDef",
    "UpdateContactFlowModuleMetadataRequestRequestTypeDef",
    "UpdateContactFlowNameRequestRequestTypeDef",
    "UpdateContactRoutingDataRequestRequestTypeDef",
    "UpdateInstanceAttributeRequestRequestTypeDef",
    "UpdatePhoneNumberMetadataRequestRequestTypeDef",
    "UpdatePhoneNumberRequestRequestTypeDef",
    "UpdatePromptRequestRequestTypeDef",
    "UpdateQueueHoursOfOperationRequestRequestTypeDef",
    "UpdateQueueMaxContactsRequestRequestTypeDef",
    "UpdateQueueNameRequestRequestTypeDef",
    "UpdateQueueStatusRequestRequestTypeDef",
    "UpdateQuickConnectNameRequestRequestTypeDef",
    "UpdateRoutingProfileAgentAvailabilityTimerRequestRequestTypeDef",
    "UpdateRoutingProfileDefaultOutboundQueueRequestRequestTypeDef",
    "UpdateRoutingProfileNameRequestRequestTypeDef",
    "UpdateUserHierarchyGroupNameRequestRequestTypeDef",
    "UpdateUserHierarchyRequestRequestTypeDef",
    "UpdateUserRoutingProfileRequestRequestTypeDef",
    "UpdateUserSecurityProfilesRequestRequestTypeDef",
    "UpdateViewMetadataRequestRequestTypeDef",
    "UserReferenceTypeDef",
    "UserIdentityInfoLiteTypeDef",
    "ViewContentTypeDef",
    "RuleSummaryTypeDef",
    "ActivateEvaluationFormResponseTypeDef",
    "AssociateAnalyticsDataSetResponseTypeDef",
    "AssociateInstanceStorageConfigResponseTypeDef",
    "AssociateSecurityKeyResponseTypeDef",
    "ClaimPhoneNumberResponseTypeDef",
    "CreateAgentStatusResponseTypeDef",
    "CreateContactFlowModuleResponseTypeDef",
    "CreateContactFlowResponseTypeDef",
    "CreateEvaluationFormResponseTypeDef",
    "CreateHoursOfOperationResponseTypeDef",
    "CreateInstanceResponseTypeDef",
    "CreateIntegrationAssociationResponseTypeDef",
    "CreatePersistentContactAssociationResponseTypeDef",
    "CreatePromptResponseTypeDef",
    "CreateQueueResponseTypeDef",
    "CreateQuickConnectResponseTypeDef",
    "CreateRoutingProfileResponseTypeDef",
    "CreateRuleResponseTypeDef",
    "CreateSecurityProfileResponseTypeDef",
    "CreateTaskTemplateResponseTypeDef",
    "CreateTrafficDistributionGroupResponseTypeDef",
    "CreateUseCaseResponseTypeDef",
    "CreateUserHierarchyGroupResponseTypeDef",
    "CreateUserResponseTypeDef",
    "CreateVocabularyResponseTypeDef",
    "DeactivateEvaluationFormResponseTypeDef",
    "DeleteVocabularyResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetContactAttributesResponseTypeDef",
    "GetFlowAssociationResponseTypeDef",
    "GetPromptFileResponseTypeDef",
    "ImportPhoneNumberResponseTypeDef",
    "ListApprovedOriginsResponseTypeDef",
    "ListLambdaFunctionsResponseTypeDef",
    "ListSecurityProfilePermissionsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "MonitorContactResponseTypeDef",
    "ReplicateInstanceResponseTypeDef",
    "SendChatIntegrationEventResponseTypeDef",
    "StartChatContactResponseTypeDef",
    "StartContactEvaluationResponseTypeDef",
    "StartContactStreamingResponseTypeDef",
    "StartOutboundVoiceContactResponseTypeDef",
    "StartTaskContactResponseTypeDef",
    "SubmitContactEvaluationResponseTypeDef",
    "TransferContactResponseTypeDef",
    "UpdateContactEvaluationResponseTypeDef",
    "UpdateEvaluationFormResponseTypeDef",
    "UpdatePhoneNumberResponseTypeDef",
    "UpdatePromptResponseTypeDef",
    "AgentConfigOutputTypeDef",
    "AgentConfigTypeDef",
    "TelephonyConfigOutputTypeDef",
    "TelephonyConfigTypeDef",
    "AgentContactReferenceTypeDef",
    "HierarchyGroupsTypeDef",
    "AllowedCapabilitiesTypeDef",
    "CustomerTypeDef",
    "AgentQualityMetricsTypeDef",
    "CustomerQualityMetricsTypeDef",
    "AgentStatusSearchCriteriaTypeDef",
    "ContactFlowModuleSearchCriteriaTypeDef",
    "ContactFlowSearchCriteriaTypeDef",
    "HoursOfOperationSearchCriteriaTypeDef",
    "PredefinedAttributeSearchCriteriaTypeDef",
    "PromptSearchCriteriaTypeDef",
    "QueueSearchCriteriaTypeDef",
    "QuickConnectSearchCriteriaTypeDef",
    "RoutingProfileSearchCriteriaTypeDef",
    "SecurityProfileSearchCriteriaTypeDef",
    "UserHierarchyGroupSearchCriteriaTypeDef",
    "ListAgentStatusResponseTypeDef",
    "DescribeAgentStatusResponseTypeDef",
    "SearchAgentStatusesResponseTypeDef",
    "MatchCriteriaTypeDef",
    "ListAnalyticsDataAssociationsResponseTypeDef",
    "ListSecurityProfileApplicationsResponseTypeDef",
    "ApplicationUnionTypeDef",
    "AssociateLexBotRequestRequestTypeDef",
    "ListLexBotsResponseTypeDef",
    "AssociateBotRequestRequestTypeDef",
    "DisassociateBotRequestRequestTypeDef",
    "LexBotConfigTypeDef",
    "AssociateUserProficienciesRequestRequestTypeDef",
    "ListUserProficienciesResponseTypeDef",
    "UpdateUserProficienciesRequestRequestTypeDef",
    "AttachedFileTypeDef",
    "StartAttachedFileUploadRequestRequestTypeDef",
    "AttributeAndConditionTypeDef",
    "CommonAttributeAndConditionTypeDef",
    "ControlPlaneTagFilterTypeDef",
    "DescribeInstanceAttributeResponseTypeDef",
    "ListInstanceAttributesResponseTypeDef",
    "MeetingFeaturesConfigurationTypeDef",
    "ListAuthenticationProfilesResponseTypeDef",
    "DescribeAuthenticationProfileResponseTypeDef",
    "SearchAvailablePhoneNumbersResponseTypeDef",
    "BatchAssociateAnalyticsDataSetResponseTypeDef",
    "BatchDisassociateAnalyticsDataSetResponseTypeDef",
    "BatchGetFlowAssociationResponseTypeDef",
    "ListFlowAssociationsResponseTypeDef",
    "BatchPutContactResponseTypeDef",
    "StartContactStreamingRequestRequestTypeDef",
    "ClaimedPhoneNumberSummaryTypeDef",
    "ConditionTypeDef",
    "ContactDataRequestTypeDef",
    "UserDataFiltersTypeDef",
    "ListContactFlowModulesResponseTypeDef",
    "DescribeContactFlowModuleResponseTypeDef",
    "SearchContactFlowModulesResponseTypeDef",
    "ListContactFlowsResponseTypeDef",
    "DescribeContactFlowResponseTypeDef",
    "SearchContactFlowsResponseTypeDef",
    "ContactSearchSummaryTypeDef",
    "CreateEvaluationFormRequestRequestTypeDef",
    "EvaluationFormContentTypeDef",
    "EvaluationFormTypeDef",
    "UpdateEvaluationFormRequestRequestTypeDef",
    "CreateParticipantRequestRequestTypeDef",
    "CreateParticipantResponseTypeDef",
    "CreatePredefinedAttributeRequestRequestTypeDef",
    "UpdatePredefinedAttributeRequestRequestTypeDef",
    "CreateQueueRequestRequestTypeDef",
    "QueueTypeDef",
    "UpdateQueueOutboundCallerConfigRequestRequestTypeDef",
    "UpdateUserIdentityInfoRequestRequestTypeDef",
    "CreateUserRequestRequestTypeDef",
    "UpdateUserPhoneConfigRequestRequestTypeDef",
    "UserTypeDef",
    "CreateViewRequestRequestTypeDef",
    "UpdateViewContentRequestRequestTypeDef",
    "GetFederationTokenResponseTypeDef",
    "MediaConcurrencyTypeDef",
    "CurrentMetricDataTypeDef",
    "ListDefaultVocabulariesResponseTypeDef",
    "DescribePromptResponseTypeDef",
    "SearchPromptsResponseTypeDef",
    "DescribeSecurityProfileResponseTypeDef",
    "DescribeTrafficDistributionGroupResponseTypeDef",
    "DescribeVocabularyResponseTypeDef",
    "DimensionsTypeDef",
    "DisassociateRoutingProfileQueuesRequestRequestTypeDef",
    "RoutingProfileQueueConfigTypeDef",
    "DisassociateUserProficienciesRequestRequestTypeDef",
    "StopContactRequestRequestTypeDef",
    "GetAttachedFileResponseTypeDef",
    "KinesisVideoStreamConfigTypeDef",
    "S3ConfigTypeDef",
    "EvaluationAnswerInputTypeDef",
    "EvaluationAnswerOutputTypeDef",
    "EvaluationFormNumericQuestionAutomationTypeDef",
    "EvaluationFormSingleSelectQuestionAutomationOptionTypeDef",
    "ListEvaluationFormsResponseTypeDef",
    "ListEvaluationFormVersionsResponseTypeDef",
    "EvaluationMetadataTypeDef",
    "EvaluationSummaryTypeDef",
    "StepTypeDef",
    "FieldValueOutputTypeDef",
    "FieldValueTypeDef",
    "GetCurrentMetricDataRequestRequestTypeDef",
    "ListAgentStatusRequestListAgentStatusesPaginateTypeDef",
    "ListApprovedOriginsRequestListApprovedOriginsPaginateTypeDef",
    "ListAuthenticationProfilesRequestListAuthenticationProfilesPaginateTypeDef",
    "ListBotsRequestListBotsPaginateTypeDef",
    "ListContactEvaluationsRequestListContactEvaluationsPaginateTypeDef",
    "ListContactFlowModulesRequestListContactFlowModulesPaginateTypeDef",
    "ListContactFlowsRequestListContactFlowsPaginateTypeDef",
    "ListContactReferencesRequestListContactReferencesPaginateTypeDef",
    "ListDefaultVocabulariesRequestListDefaultVocabulariesPaginateTypeDef",
    "ListEvaluationFormVersionsRequestListEvaluationFormVersionsPaginateTypeDef",
    "ListEvaluationFormsRequestListEvaluationFormsPaginateTypeDef",
    "ListFlowAssociationsRequestListFlowAssociationsPaginateTypeDef",
    "ListHoursOfOperationsRequestListHoursOfOperationsPaginateTypeDef",
    "ListInstanceAttributesRequestListInstanceAttributesPaginateTypeDef",
    "ListInstanceStorageConfigsRequestListInstanceStorageConfigsPaginateTypeDef",
    "ListInstancesRequestListInstancesPaginateTypeDef",
    "ListIntegrationAssociationsRequestListIntegrationAssociationsPaginateTypeDef",
    "ListLambdaFunctionsRequestListLambdaFunctionsPaginateTypeDef",
    "ListLexBotsRequestListLexBotsPaginateTypeDef",
    "ListPhoneNumbersRequestListPhoneNumbersPaginateTypeDef",
    "ListPhoneNumbersV2RequestListPhoneNumbersV2PaginateTypeDef",
    "ListPredefinedAttributesRequestListPredefinedAttributesPaginateTypeDef",
    "ListPromptsRequestListPromptsPaginateTypeDef",
    "ListQueueQuickConnectsRequestListQueueQuickConnectsPaginateTypeDef",
    "ListQueuesRequestListQueuesPaginateTypeDef",
    "ListQuickConnectsRequestListQuickConnectsPaginateTypeDef",
    "ListRoutingProfileQueuesRequestListRoutingProfileQueuesPaginateTypeDef",
    "ListRoutingProfilesRequestListRoutingProfilesPaginateTypeDef",
    "ListRulesRequestListRulesPaginateTypeDef",
    "ListSecurityKeysRequestListSecurityKeysPaginateTypeDef",
    "ListSecurityProfileApplicationsRequestListSecurityProfileApplicationsPaginateTypeDef",
    "ListSecurityProfilePermissionsRequestListSecurityProfilePermissionsPaginateTypeDef",
    "ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef",
    "ListTaskTemplatesRequestListTaskTemplatesPaginateTypeDef",
    "ListTrafficDistributionGroupUsersRequestListTrafficDistributionGroupUsersPaginateTypeDef",
    "ListTrafficDistributionGroupsRequestListTrafficDistributionGroupsPaginateTypeDef",
    "ListUseCasesRequestListUseCasesPaginateTypeDef",
    "ListUserHierarchyGroupsRequestListUserHierarchyGroupsPaginateTypeDef",
    "ListUserProficienciesRequestListUserProficienciesPaginateTypeDef",
    "ListUsersRequestListUsersPaginateTypeDef",
    "ListViewVersionsRequestListViewVersionsPaginateTypeDef",
    "ListViewsRequestListViewsPaginateTypeDef",
    "SearchAvailablePhoneNumbersRequestSearchAvailablePhoneNumbersPaginateTypeDef",
    "SearchVocabulariesRequestSearchVocabulariesPaginateTypeDef",
    "SearchContactsTimeRangeTypeDef",
    "UpdateContactScheduleRequestRequestTypeDef",
    "HierarchyPathReferenceTypeDef",
    "HierarchyPathTypeDef",
    "ListUserHierarchyGroupsResponseTypeDef",
    "HierarchyStructureTypeDef",
    "HierarchyStructureUpdateTypeDef",
    "HistoricalMetricTypeDef",
    "HoursOfOperationConfigTypeDef",
    "ListHoursOfOperationsResponseTypeDef",
    "InstanceTypeDef",
    "ListInstancesResponseTypeDef",
    "ListIntegrationAssociationsResponseTypeDef",
    "InvisibleFieldInfoTypeDef",
    "ReadOnlyFieldInfoTypeDef",
    "RequiredFieldInfoTypeDef",
    "TaskTemplateDefaultFieldValueTypeDef",
    "TaskTemplateFieldOutputTypeDef",
    "TaskTemplateFieldTypeDef",
    "ListPhoneNumbersResponseTypeDef",
    "ListPhoneNumbersV2ResponseTypeDef",
    "ListPredefinedAttributesResponseTypeDef",
    "ListPromptsResponseTypeDef",
    "ListQueueQuickConnectsResponseTypeDef",
    "ListQuickConnectsResponseTypeDef",
    "ListQueuesResponseTypeDef",
    "ListRoutingProfileQueuesResponseTypeDef",
    "ListRoutingProfilesResponseTypeDef",
    "ListSecurityKeysResponseTypeDef",
    "ListSecurityProfilesResponseTypeDef",
    "ListTaskTemplatesResponseTypeDef",
    "ListTrafficDistributionGroupUsersResponseTypeDef",
    "ListTrafficDistributionGroupsResponseTypeDef",
    "ListUseCasesResponseTypeDef",
    "ListUsersResponseTypeDef",
    "ListViewVersionsResponseTypeDef",
    "ListViewsResponseTypeDef",
    "MetricV2OutputTypeDef",
    "MetricV2TypeDef",
    "NewSessionDetailsTypeDef",
    "SendNotificationActionDefinitionOutputTypeDef",
    "SendNotificationActionDefinitionTypeDef",
    "ParticipantTimerConfigurationTypeDef",
    "StartChatContactRequestRequestTypeDef",
    "PredefinedAttributeTypeDef",
    "PredefinedAttributeValuesUnionTypeDef",
    "QuickConnectConfigTypeDef",
    "RealTimeContactAnalysisTranscriptItemRedactionTypeDef",
    "RealTimeContactAnalysisTranscriptItemWithCharacterOffsetsTypeDef",
    "RealTimeContactAnalysisTranscriptItemWithContentTypeDef",
    "RealTimeContactAnalysisSegmentAttachmentsTypeDef",
    "RealTimeContactAnalysisSegmentEventTypeDef",
    "ReferenceSummaryTypeDef",
    "StartOutboundVoiceContactRequestRequestTypeDef",
    "StartTaskContactRequestRequestTypeDef",
    "TaskActionDefinitionOutputTypeDef",
    "TaskActionDefinitionTypeDef",
    "UpdateContactRequestRequestTypeDef",
    "ResourceTagsSearchCriteriaTypeDef",
    "SearchResourceTagsResponseTypeDef",
    "SearchSecurityProfilesResponseTypeDef",
    "SearchVocabulariesResponseTypeDef",
    "SearchableContactAttributesTypeDef",
    "SignInConfigOutputTypeDef",
    "SignInConfigTypeDef",
    "StartAttachedFileUploadResponseTypeDef",
    "StartContactRecordingRequestRequestTypeDef",
    "TranscriptTypeDef",
    "UserSearchSummaryTypeDef",
    "ViewTypeDef",
    "ListRulesResponseTypeDef",
    "AgentConfigUnionTypeDef",
    "TelephonyConfigUnionTypeDef",
    "AgentInfoTypeDef",
    "StartWebRTCContactRequestRequestTypeDef",
    "QualityMetricsTypeDef",
    "SearchPredefinedAttributesRequestSearchPredefinedAttributesPaginateTypeDef",
    "AttributeConditionTypeDef",
    "CreateSecurityProfileRequestRequestTypeDef",
    "UpdateSecurityProfileRequestRequestTypeDef",
    "ListBotsResponseTypeDef",
    "BatchGetAttachedFileMetadataResponseTypeDef",
    "ControlPlaneUserAttributeFilterTypeDef",
    "ControlPlaneAttributeFilterTypeDef",
    "ContactFlowModuleSearchFilterTypeDef",
    "ContactFlowSearchFilterTypeDef",
    "HoursOfOperationSearchFilterTypeDef",
    "PromptSearchFilterTypeDef",
    "QueueSearchFilterTypeDef",
    "QuickConnectSearchFilterTypeDef",
    "RoutingProfileSearchFilterTypeDef",
    "SecurityProfilesSearchFilterTypeDef",
    "MeetingTypeDef",
    "DescribePhoneNumberResponseTypeDef",
    "ListConditionTypeDef",
    "BatchPutContactRequestRequestTypeDef",
    "GetCurrentUserDataRequestRequestTypeDef",
    "SearchContactsResponseTypeDef",
    "DescribeEvaluationFormResponseTypeDef",
    "DescribeQueueResponseTypeDef",
    "SearchQueuesResponseTypeDef",
    "DescribeUserResponseTypeDef",
    "RoutingProfileTypeDef",
    "UpdateRoutingProfileConcurrencyRequestRequestTypeDef",
    "CurrentMetricResultTypeDef",
    "AssociateRoutingProfileQueuesRequestRequestTypeDef",
    "CreateRoutingProfileRequestRequestTypeDef",
    "UpdateRoutingProfileQueuesRequestRequestTypeDef",
    "InstanceStorageConfigTypeDef",
    "SubmitContactEvaluationRequestRequestTypeDef",
    "UpdateContactEvaluationRequestRequestTypeDef",
    "EvaluationFormNumericQuestionPropertiesOutputTypeDef",
    "EvaluationFormNumericQuestionPropertiesTypeDef",
    "EvaluationFormSingleSelectQuestionAutomationOutputTypeDef",
    "EvaluationFormSingleSelectQuestionAutomationTypeDef",
    "EvaluationTypeDef",
    "ListContactEvaluationsResponseTypeDef",
    "RoutingCriteriaTypeDef",
    "CreateCaseActionDefinitionOutputTypeDef",
    "UpdateCaseActionDefinitionOutputTypeDef",
    "CreateCaseActionDefinitionTypeDef",
    "UpdateCaseActionDefinitionTypeDef",
    "UserDataTypeDef",
    "HierarchyGroupTypeDef",
    "DescribeUserHierarchyStructureResponseTypeDef",
    "UpdateUserHierarchyStructureRequestRequestTypeDef",
    "GetMetricDataRequestGetMetricDataPaginateTypeDef",
    "GetMetricDataRequestRequestTypeDef",
    "HistoricalMetricDataTypeDef",
    "CreateHoursOfOperationRequestRequestTypeDef",
    "HoursOfOperationTypeDef",
    "UpdateHoursOfOperationRequestRequestTypeDef",
    "DescribeInstanceResponseTypeDef",
    "TaskTemplateConstraintsOutputTypeDef",
    "TaskTemplateConstraintsTypeDef",
    "TaskTemplateDefaultsOutputTypeDef",
    "TaskTemplateDefaultsTypeDef",
    "TaskTemplateFieldUnionTypeDef",
    "MetricDataV2TypeDef",
    "MetricV2UnionTypeDef",
    "SendChatIntegrationEventRequestRequestTypeDef",
    "ChatParticipantRoleConfigTypeDef",
    "DescribePredefinedAttributeResponseTypeDef",
    "SearchPredefinedAttributesResponseTypeDef",
    "CreateQuickConnectRequestRequestTypeDef",
    "QuickConnectTypeDef",
    "UpdateQuickConnectConfigRequestRequestTypeDef",
    "RealTimeContactAnalysisSegmentTranscriptTypeDef",
    "RealTimeContactAnalysisPointOfInterestTypeDef",
    "RealTimeContactAnalysisIssueDetectedTypeDef",
    "ListContactReferencesResponseTypeDef",
    "SearchResourceTagsRequestRequestTypeDef",
    "SearchResourceTagsRequestSearchResourceTagsPaginateTypeDef",
    "GetTrafficDistributionResponseTypeDef",
    "SignInConfigUnionTypeDef",
    "UpdateTrafficDistributionRequestRequestTypeDef",
    "ContactAnalysisTypeDef",
    "SearchUsersResponseTypeDef",
    "CreateViewResponseTypeDef",
    "CreateViewVersionResponseTypeDef",
    "DescribeViewResponseTypeDef",
    "UpdateViewContentResponseTypeDef",
    "ExpressionTypeDef",
    "UserSearchFilterTypeDef",
    "AgentStatusSearchFilterTypeDef",
    "UserHierarchyGroupSearchFilterTypeDef",
    "SearchContactFlowModulesRequestRequestTypeDef",
    "SearchContactFlowModulesRequestSearchContactFlowModulesPaginateTypeDef",
    "SearchContactFlowsRequestRequestTypeDef",
    "SearchContactFlowsRequestSearchContactFlowsPaginateTypeDef",
    "SearchHoursOfOperationsRequestRequestTypeDef",
    "SearchHoursOfOperationsRequestSearchHoursOfOperationsPaginateTypeDef",
    "SearchPromptsRequestRequestTypeDef",
    "SearchPromptsRequestSearchPromptsPaginateTypeDef",
    "SearchQueuesRequestRequestTypeDef",
    "SearchQueuesRequestSearchQueuesPaginateTypeDef",
    "SearchQuickConnectsRequestRequestTypeDef",
    "SearchQuickConnectsRequestSearchQuickConnectsPaginateTypeDef",
    "SearchRoutingProfilesRequestRequestTypeDef",
    "SearchRoutingProfilesRequestSearchRoutingProfilesPaginateTypeDef",
    "SearchSecurityProfilesRequestRequestTypeDef",
    "SearchSecurityProfilesRequestSearchSecurityProfilesPaginateTypeDef",
    "ConnectionDataTypeDef",
    "UserSearchCriteriaTypeDef",
    "DescribeRoutingProfileResponseTypeDef",
    "SearchRoutingProfilesResponseTypeDef",
    "GetCurrentMetricDataResponseTypeDef",
    "AssociateInstanceStorageConfigRequestRequestTypeDef",
    "DescribeInstanceStorageConfigResponseTypeDef",
    "ListInstanceStorageConfigsResponseTypeDef",
    "UpdateInstanceStorageConfigRequestRequestTypeDef",
    "EvaluationFormSingleSelectQuestionPropertiesOutputTypeDef",
    "EvaluationFormSingleSelectQuestionPropertiesTypeDef",
    "DescribeContactEvaluationResponseTypeDef",
    "ContactTypeDef",
    "RuleActionOutputTypeDef",
    "RuleActionTypeDef",
    "GetCurrentUserDataResponseTypeDef",
    "DescribeUserHierarchyGroupResponseTypeDef",
    "SearchUserHierarchyGroupsResponseTypeDef",
    "HistoricalMetricResultTypeDef",
    "DescribeHoursOfOperationResponseTypeDef",
    "SearchHoursOfOperationsResponseTypeDef",
    "TaskTemplateConstraintsUnionTypeDef",
    "GetTaskTemplateResponseTypeDef",
    "UpdateTaskTemplateResponseTypeDef",
    "TaskTemplateDefaultsUnionTypeDef",
    "CreateTaskTemplateRequestRequestTypeDef",
    "UpdateTaskTemplateRequestRequestTypeDef",
    "MetricResultV2TypeDef",
    "GetMetricDataV2RequestRequestTypeDef",
    "UpdateParticipantRoleConfigChannelInfoTypeDef",
    "DescribeQuickConnectResponseTypeDef",
    "SearchQuickConnectsResponseTypeDef",
    "RealTimeContactAnalysisCategoryDetailsTypeDef",
    "RealTimeContactAnalysisSegmentIssuesTypeDef",
    "SearchCriteriaTypeDef",
    "SearchUsersRequestRequestTypeDef",
    "SearchAgentStatusesRequestRequestTypeDef",
    "SearchAgentStatusesRequestSearchAgentStatusesPaginateTypeDef",
    "SearchUserHierarchyGroupsRequestRequestTypeDef",
    "SearchUserHierarchyGroupsRequestSearchUserHierarchyGroupsPaginateTypeDef",
    "StartWebRTCContactResponseTypeDef",
    "SearchUsersRequestSearchUsersPaginateTypeDef",
    "EvaluationFormQuestionTypePropertiesOutputTypeDef",
    "EvaluationFormQuestionTypePropertiesTypeDef",
    "DescribeContactResponseTypeDef",
    "RuleTypeDef",
    "RuleActionUnionTypeDef",
    "GetMetricDataResponseTypeDef",
    "GetMetricDataV2ResponseTypeDef",
    "UpdateParticipantRoleConfigRequestRequestTypeDef",
    "RealTimeContactAnalysisSegmentCategoriesTypeDef",
    "SearchContactsRequestRequestTypeDef",
    "SearchContactsRequestSearchContactsPaginateTypeDef",
    "EvaluationFormQuestionOutputTypeDef",
    "EvaluationFormQuestionTypeDef",
    "DescribeRuleResponseTypeDef",
    "CreateRuleRequestRequestTypeDef",
    "UpdateRuleRequestRequestTypeDef",
    "RealtimeContactAnalysisSegmentTypeDef",
    "EvaluationFormItemOutputTypeDef",
    "EvaluationFormItemTypeDef",
    "ListRealtimeContactAnalysisSegmentsV2ResponseTypeDef",
)

ActionSummaryTypeDef = TypedDict(
    "ActionSummaryTypeDef",
    {
        "ActionType": ActionTypeType,
    },
)
ActivateEvaluationFormRequestRequestTypeDef = TypedDict(
    "ActivateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
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
DistributionTypeDef = TypedDict(
    "DistributionTypeDef",
    {
        "Region": str,
        "Percentage": int,
    },
)
QueueReferenceTypeDef = TypedDict(
    "QueueReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)
AgentHierarchyGroupTypeDef = TypedDict(
    "AgentHierarchyGroupTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
AgentHierarchyGroupsTypeDef = TypedDict(
    "AgentHierarchyGroupsTypeDef",
    {
        "L1Ids": NotRequired[Sequence[str]],
        "L2Ids": NotRequired[Sequence[str]],
        "L3Ids": NotRequired[Sequence[str]],
        "L4Ids": NotRequired[Sequence[str]],
        "L5Ids": NotRequired[Sequence[str]],
    },
)
DeviceInfoTypeDef = TypedDict(
    "DeviceInfoTypeDef",
    {
        "PlatformName": NotRequired[str],
        "PlatformVersion": NotRequired[str],
        "OperatingSystem": NotRequired[str],
    },
)
ParticipantCapabilitiesTypeDef = TypedDict(
    "ParticipantCapabilitiesTypeDef",
    {
        "Video": NotRequired[Literal["SEND"]],
    },
)
AudioQualityMetricsInfoTypeDef = TypedDict(
    "AudioQualityMetricsInfoTypeDef",
    {
        "QualityScore": NotRequired[float],
        "PotentialQualityIssues": NotRequired[List[str]],
    },
)
AgentStatusReferenceTypeDef = TypedDict(
    "AgentStatusReferenceTypeDef",
    {
        "StatusStartTimestamp": NotRequired[datetime],
        "StatusArn": NotRequired[str],
        "StatusName": NotRequired[str],
    },
)
StringConditionTypeDef = TypedDict(
    "StringConditionTypeDef",
    {
        "FieldName": NotRequired[str],
        "Value": NotRequired[str],
        "ComparisonType": NotRequired[StringComparisonTypeType],
    },
)
AgentStatusSummaryTypeDef = TypedDict(
    "AgentStatusSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[AgentStatusTypeType],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
AgentStatusTypeDef = TypedDict(
    "AgentStatusTypeDef",
    {
        "AgentStatusARN": NotRequired[str],
        "AgentStatusId": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Type": NotRequired[AgentStatusTypeType],
        "DisplayOrder": NotRequired[int],
        "State": NotRequired[AgentStatusStateType],
        "Tags": NotRequired[Dict[str, str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
AgentsCriteriaTypeDef = TypedDict(
    "AgentsCriteriaTypeDef",
    {
        "AgentIds": NotRequired[List[str]],
    },
)
AnalyticsDataAssociationResultTypeDef = TypedDict(
    "AnalyticsDataAssociationResultTypeDef",
    {
        "DataSetId": NotRequired[str],
        "TargetAccountId": NotRequired[str],
        "ResourceShareId": NotRequired[str],
        "ResourceShareArn": NotRequired[str],
    },
)
AnswerMachineDetectionConfigTypeDef = TypedDict(
    "AnswerMachineDetectionConfigTypeDef",
    {
        "EnableAnswerMachineDetection": NotRequired[bool],
        "AwaitAnswerMachinePrompt": NotRequired[bool],
    },
)
ApplicationExtraOutputTypeDef = TypedDict(
    "ApplicationExtraOutputTypeDef",
    {
        "Namespace": NotRequired[str],
        "ApplicationPermissions": NotRequired[List[str]],
    },
)
ApplicationOutputTypeDef = TypedDict(
    "ApplicationOutputTypeDef",
    {
        "Namespace": NotRequired[str],
        "ApplicationPermissions": NotRequired[List[str]],
    },
)
ApplicationTypeDef = TypedDict(
    "ApplicationTypeDef",
    {
        "Namespace": NotRequired[str],
        "ApplicationPermissions": NotRequired[Sequence[str]],
    },
)
AssociateAnalyticsDataSetRequestRequestTypeDef = TypedDict(
    "AssociateAnalyticsDataSetRequestRequestTypeDef",
    {
        "InstanceId": str,
        "DataSetId": str,
        "TargetAccountId": NotRequired[str],
    },
)
AssociateApprovedOriginRequestRequestTypeDef = TypedDict(
    "AssociateApprovedOriginRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Origin": str,
    },
)
LexBotTypeDef = TypedDict(
    "LexBotTypeDef",
    {
        "Name": str,
        "LexRegion": str,
    },
)
LexV2BotTypeDef = TypedDict(
    "LexV2BotTypeDef",
    {
        "AliasArn": NotRequired[str],
    },
)
AssociateDefaultVocabularyRequestRequestTypeDef = TypedDict(
    "AssociateDefaultVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "VocabularyId": NotRequired[str],
    },
)
AssociateFlowRequestRequestTypeDef = TypedDict(
    "AssociateFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceId": str,
        "FlowId": str,
        "ResourceType": Literal["SMS_PHONE_NUMBER"],
    },
)
AssociateLambdaFunctionRequestRequestTypeDef = TypedDict(
    "AssociateLambdaFunctionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FunctionArn": str,
    },
)
AssociatePhoneNumberContactFlowRequestRequestTypeDef = TypedDict(
    "AssociatePhoneNumberContactFlowRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "InstanceId": str,
        "ContactFlowId": str,
    },
)
AssociateQueueQuickConnectsRequestRequestTypeDef = TypedDict(
    "AssociateQueueQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "QuickConnectIds": Sequence[str],
    },
)
AssociateSecurityKeyRequestRequestTypeDef = TypedDict(
    "AssociateSecurityKeyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Key": str,
    },
)
AssociateTrafficDistributionGroupUserRequestRequestTypeDef = TypedDict(
    "AssociateTrafficDistributionGroupUserRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
        "UserId": str,
        "InstanceId": str,
    },
)
UserProficiencyTypeDef = TypedDict(
    "UserProficiencyTypeDef",
    {
        "AttributeName": str,
        "AttributeValue": str,
        "Level": float,
    },
)
AttachedFileErrorTypeDef = TypedDict(
    "AttachedFileErrorTypeDef",
    {
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
        "FileId": NotRequired[str],
    },
)
CreatedByInfoTypeDef = TypedDict(
    "CreatedByInfoTypeDef",
    {
        "ConnectUserArn": NotRequired[str],
        "AWSIdentityArn": NotRequired[str],
    },
)
AttachmentReferenceTypeDef = TypedDict(
    "AttachmentReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
        "Status": NotRequired[ReferenceStatusType],
    },
)
AttendeeTypeDef = TypedDict(
    "AttendeeTypeDef",
    {
        "AttendeeId": NotRequired[str],
        "JoinToken": NotRequired[str],
    },
)
HierarchyGroupConditionTypeDef = TypedDict(
    "HierarchyGroupConditionTypeDef",
    {
        "Value": NotRequired[str],
        "HierarchyGroupMatchType": NotRequired[HierarchyGroupMatchTypeType],
    },
)
TagConditionTypeDef = TypedDict(
    "TagConditionTypeDef",
    {
        "TagKey": NotRequired[str],
        "TagValue": NotRequired[str],
    },
)
AttributeTypeDef = TypedDict(
    "AttributeTypeDef",
    {
        "AttributeType": NotRequired[InstanceAttributeTypeType],
        "Value": NotRequired[str],
    },
)
AudioFeaturesTypeDef = TypedDict(
    "AudioFeaturesTypeDef",
    {
        "EchoReduction": NotRequired[MeetingFeatureStatusType],
    },
)
AuthenticationProfileSummaryTypeDef = TypedDict(
    "AuthenticationProfileSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "IsDefault": NotRequired[bool],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
AuthenticationProfileTypeDef = TypedDict(
    "AuthenticationProfileTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "AllowedIps": NotRequired[List[str]],
        "BlockedIps": NotRequired[List[str]],
        "IsDefault": NotRequired[bool],
        "CreatedTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
        "PeriodicSessionDuration": NotRequired[int],
        "MaxSessionDuration": NotRequired[int],
    },
)
AvailableNumberSummaryTypeDef = TypedDict(
    "AvailableNumberSummaryTypeDef",
    {
        "PhoneNumber": NotRequired[str],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
    },
)
BatchAssociateAnalyticsDataSetRequestRequestTypeDef = TypedDict(
    "BatchAssociateAnalyticsDataSetRequestRequestTypeDef",
    {
        "InstanceId": str,
        "DataSetIds": Sequence[str],
        "TargetAccountId": NotRequired[str],
    },
)
ErrorResultTypeDef = TypedDict(
    "ErrorResultTypeDef",
    {
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
BatchDisassociateAnalyticsDataSetRequestRequestTypeDef = TypedDict(
    "BatchDisassociateAnalyticsDataSetRequestRequestTypeDef",
    {
        "InstanceId": str,
        "DataSetIds": Sequence[str],
        "TargetAccountId": NotRequired[str],
    },
)
BatchGetAttachedFileMetadataRequestRequestTypeDef = TypedDict(
    "BatchGetAttachedFileMetadataRequestRequestTypeDef",
    {
        "FileIds": Sequence[str],
        "InstanceId": str,
        "AssociatedResourceArn": str,
    },
)
BatchGetFlowAssociationRequestRequestTypeDef = TypedDict(
    "BatchGetFlowAssociationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceIds": Sequence[str],
        "ResourceType": NotRequired[Literal["VOICE_PHONE_NUMBER"]],
    },
)
FlowAssociationSummaryTypeDef = TypedDict(
    "FlowAssociationSummaryTypeDef",
    {
        "ResourceId": NotRequired[str],
        "FlowId": NotRequired[str],
        "ResourceType": NotRequired[Literal["VOICE_PHONE_NUMBER"]],
    },
)
FailedRequestTypeDef = TypedDict(
    "FailedRequestTypeDef",
    {
        "RequestIdentifier": NotRequired[str],
        "FailureReasonCode": NotRequired[FailureReasonCodeType],
        "FailureReasonMessage": NotRequired[str],
    },
)
SuccessfulRequestTypeDef = TypedDict(
    "SuccessfulRequestTypeDef",
    {
        "RequestIdentifier": NotRequired[str],
        "ContactId": NotRequired[str],
    },
)
CampaignTypeDef = TypedDict(
    "CampaignTypeDef",
    {
        "CampaignId": NotRequired[str],
    },
)
ChatEventTypeDef = TypedDict(
    "ChatEventTypeDef",
    {
        "Type": ChatEventTypeType,
        "ContentType": NotRequired[str],
        "Content": NotRequired[str],
    },
)
ChatMessageTypeDef = TypedDict(
    "ChatMessageTypeDef",
    {
        "ContentType": str,
        "Content": str,
    },
)
ChatStreamingConfigurationTypeDef = TypedDict(
    "ChatStreamingConfigurationTypeDef",
    {
        "StreamingEndpointArn": str,
    },
)
ClaimPhoneNumberRequestRequestTypeDef = TypedDict(
    "ClaimPhoneNumberRequestRequestTypeDef",
    {
        "PhoneNumber": str,
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "PhoneNumberDescription": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "ClientToken": NotRequired[str],
    },
)
PhoneNumberStatusTypeDef = TypedDict(
    "PhoneNumberStatusTypeDef",
    {
        "Status": NotRequired[PhoneNumberWorkflowStatusType],
        "Message": NotRequired[str],
    },
)
CompleteAttachedFileUploadRequestRequestTypeDef = TypedDict(
    "CompleteAttachedFileUploadRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FileId": str,
        "AssociatedResourceArn": str,
    },
)
NumberConditionTypeDef = TypedDict(
    "NumberConditionTypeDef",
    {
        "FieldName": NotRequired[str],
        "MinValue": NotRequired[int],
        "MaxValue": NotRequired[int],
        "ComparisonType": NotRequired[NumberComparisonTypeType],
    },
)
EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "Type": NotRequired[EndpointTypeType],
        "Address": NotRequired[str],
    },
)
ContactFilterTypeDef = TypedDict(
    "ContactFilterTypeDef",
    {
        "ContactStates": NotRequired[Sequence[ContactStateType]],
    },
)
ContactFlowModuleSummaryTypeDef = TypedDict(
    "ContactFlowModuleSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "State": NotRequired[ContactFlowModuleStateType],
    },
)
ContactFlowModuleTypeDef = TypedDict(
    "ContactFlowModuleTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "Name": NotRequired[str],
        "Content": NotRequired[str],
        "Description": NotRequired[str],
        "State": NotRequired[ContactFlowModuleStateType],
        "Status": NotRequired[ContactFlowModuleStatusType],
        "Tags": NotRequired[Dict[str, str]],
    },
)
ContactFlowSummaryTypeDef = TypedDict(
    "ContactFlowSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "ContactFlowType": NotRequired[ContactFlowTypeType],
        "ContactFlowState": NotRequired[ContactFlowStateType],
        "ContactFlowStatus": NotRequired[ContactFlowStatusType],
    },
)
ContactFlowTypeDef = TypedDict(
    "ContactFlowTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[ContactFlowTypeType],
        "State": NotRequired[ContactFlowStateType],
        "Status": NotRequired[ContactFlowStatusType],
        "Description": NotRequired[str],
        "Content": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)
ContactSearchSummaryAgentInfoTypeDef = TypedDict(
    "ContactSearchSummaryAgentInfoTypeDef",
    {
        "Id": NotRequired[str],
        "ConnectedToAgentTimestamp": NotRequired[datetime],
    },
)
ContactSearchSummaryQueueInfoTypeDef = TypedDict(
    "ContactSearchSummaryQueueInfoTypeDef",
    {
        "Id": NotRequired[str],
        "EnqueueTimestamp": NotRequired[datetime],
    },
)
CustomerVoiceActivityTypeDef = TypedDict(
    "CustomerVoiceActivityTypeDef",
    {
        "GreetingStartTimestamp": NotRequired[datetime],
        "GreetingEndTimestamp": NotRequired[datetime],
    },
)
DisconnectDetailsTypeDef = TypedDict(
    "DisconnectDetailsTypeDef",
    {
        "PotentialDisconnectIssue": NotRequired[str],
    },
)
QueueInfoTypeDef = TypedDict(
    "QueueInfoTypeDef",
    {
        "Id": NotRequired[str],
        "EnqueueTimestamp": NotRequired[datetime],
    },
)
SegmentAttributeValueTypeDef = TypedDict(
    "SegmentAttributeValueTypeDef",
    {
        "ValueString": NotRequired[str],
    },
)
WisdomInfoTypeDef = TypedDict(
    "WisdomInfoTypeDef",
    {
        "SessionArn": NotRequired[str],
    },
)
CreateAgentStatusRequestRequestTypeDef = TypedDict(
    "CreateAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "State": AgentStatusStateType,
        "Description": NotRequired[str],
        "DisplayOrder": NotRequired[int],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateContactFlowModuleRequestRequestTypeDef = TypedDict(
    "CreateContactFlowModuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Content": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "ClientToken": NotRequired[str],
    },
)
CreateContactFlowRequestRequestTypeDef = TypedDict(
    "CreateContactFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Type": ContactFlowTypeType,
        "Content": str,
        "Description": NotRequired[str],
        "Status": NotRequired[ContactFlowStatusType],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
EvaluationFormItemUnionTypeDef = Union[
    "EvaluationFormItemTypeDef", "EvaluationFormItemOutputTypeDef"
]
EvaluationFormScoringStrategyTypeDef = TypedDict(
    "EvaluationFormScoringStrategyTypeDef",
    {
        "Mode": EvaluationFormScoringModeType,
        "Status": EvaluationFormScoringStatusType,
    },
)
CreateInstanceRequestRequestTypeDef = TypedDict(
    "CreateInstanceRequestRequestTypeDef",
    {
        "IdentityManagementType": DirectoryTypeType,
        "InboundCallsEnabled": bool,
        "OutboundCallsEnabled": bool,
        "ClientToken": NotRequired[str],
        "InstanceAlias": NotRequired[str],
        "DirectoryId": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateIntegrationAssociationRequestRequestTypeDef = TypedDict(
    "CreateIntegrationAssociationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationType": IntegrationTypeType,
        "IntegrationArn": str,
        "SourceApplicationUrl": NotRequired[str],
        "SourceApplicationName": NotRequired[str],
        "SourceType": NotRequired[SourceTypeType],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
ParticipantDetailsToAddTypeDef = TypedDict(
    "ParticipantDetailsToAddTypeDef",
    {
        "ParticipantRole": NotRequired[ParticipantRoleType],
        "DisplayName": NotRequired[str],
    },
)
ParticipantTokenCredentialsTypeDef = TypedDict(
    "ParticipantTokenCredentialsTypeDef",
    {
        "ParticipantToken": NotRequired[str],
        "Expiry": NotRequired[str],
    },
)
CreatePersistentContactAssociationRequestRequestTypeDef = TypedDict(
    "CreatePersistentContactAssociationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "InitialContactId": str,
        "RehydrationType": RehydrationTypeType,
        "SourceContactId": str,
        "ClientToken": NotRequired[str],
    },
)
PredefinedAttributeValuesTypeDef = TypedDict(
    "PredefinedAttributeValuesTypeDef",
    {
        "StringList": NotRequired[Sequence[str]],
    },
)
CreatePromptRequestRequestTypeDef = TypedDict(
    "CreatePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "S3Uri": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
OutboundCallerConfigTypeDef = TypedDict(
    "OutboundCallerConfigTypeDef",
    {
        "OutboundCallerIdName": NotRequired[str],
        "OutboundCallerIdNumberId": NotRequired[str],
        "OutboundFlowId": NotRequired[str],
    },
)
RuleTriggerEventSourceTypeDef = TypedDict(
    "RuleTriggerEventSourceTypeDef",
    {
        "EventSourceName": EventSourceNameType,
        "IntegrationAssociationId": NotRequired[str],
    },
)
CreateTrafficDistributionGroupRequestRequestTypeDef = TypedDict(
    "CreateTrafficDistributionGroupRequestRequestTypeDef",
    {
        "Name": str,
        "InstanceId": str,
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateUseCaseRequestRequestTypeDef = TypedDict(
    "CreateUseCaseRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "UseCaseType": UseCaseTypeType,
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateUserHierarchyGroupRequestRequestTypeDef = TypedDict(
    "CreateUserHierarchyGroupRequestRequestTypeDef",
    {
        "Name": str,
        "InstanceId": str,
        "ParentGroupId": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
UserIdentityInfoTypeDef = TypedDict(
    "UserIdentityInfoTypeDef",
    {
        "FirstName": NotRequired[str],
        "LastName": NotRequired[str],
        "Email": NotRequired[str],
        "SecondaryEmail": NotRequired[str],
        "Mobile": NotRequired[str],
    },
)
UserPhoneConfigTypeDef = TypedDict(
    "UserPhoneConfigTypeDef",
    {
        "PhoneType": PhoneTypeType,
        "AutoAccept": NotRequired[bool],
        "AfterContactWorkTimeLimit": NotRequired[int],
        "DeskPhoneNumber": NotRequired[str],
    },
)
ViewInputContentTypeDef = TypedDict(
    "ViewInputContentTypeDef",
    {
        "Template": NotRequired[str],
        "Actions": NotRequired[Sequence[str]],
    },
)
CreateViewVersionRequestRequestTypeDef = TypedDict(
    "CreateViewVersionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "VersionDescription": NotRequired[str],
        "ViewContentSha256": NotRequired[str],
    },
)
CreateVocabularyRequestRequestTypeDef = TypedDict(
    "CreateVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "VocabularyName": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "Content": str,
        "ClientToken": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CredentialsTypeDef = TypedDict(
    "CredentialsTypeDef",
    {
        "AccessToken": NotRequired[str],
        "AccessTokenExpiration": NotRequired[datetime],
        "RefreshToken": NotRequired[str],
        "RefreshTokenExpiration": NotRequired[datetime],
    },
)
CrossChannelBehaviorTypeDef = TypedDict(
    "CrossChannelBehaviorTypeDef",
    {
        "BehaviorType": BehaviorTypeType,
    },
)
CurrentMetricTypeDef = TypedDict(
    "CurrentMetricTypeDef",
    {
        "Name": NotRequired[CurrentMetricNameType],
        "Unit": NotRequired[UnitType],
    },
)
CurrentMetricSortCriteriaTypeDef = TypedDict(
    "CurrentMetricSortCriteriaTypeDef",
    {
        "SortByMetric": NotRequired[CurrentMetricNameType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
DateReferenceTypeDef = TypedDict(
    "DateReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)
DeactivateEvaluationFormRequestRequestTypeDef = TypedDict(
    "DeactivateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
    },
)
DefaultVocabularyTypeDef = TypedDict(
    "DefaultVocabularyTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "VocabularyId": str,
        "VocabularyName": str,
    },
)
DeleteAttachedFileRequestRequestTypeDef = TypedDict(
    "DeleteAttachedFileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FileId": str,
        "AssociatedResourceArn": str,
    },
)
DeleteContactEvaluationRequestRequestTypeDef = TypedDict(
    "DeleteContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
    },
)
DeleteContactFlowModuleRequestRequestTypeDef = TypedDict(
    "DeleteContactFlowModuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
    },
)
DeleteContactFlowRequestRequestTypeDef = TypedDict(
    "DeleteContactFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
    },
)
DeleteEvaluationFormRequestRequestTypeDef = TypedDict(
    "DeleteEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": NotRequired[int],
    },
)
DeleteHoursOfOperationRequestRequestTypeDef = TypedDict(
    "DeleteHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "HoursOfOperationId": str,
    },
)
DeleteInstanceRequestRequestTypeDef = TypedDict(
    "DeleteInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
DeleteIntegrationAssociationRequestRequestTypeDef = TypedDict(
    "DeleteIntegrationAssociationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
    },
)
DeletePredefinedAttributeRequestRequestTypeDef = TypedDict(
    "DeletePredefinedAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
    },
)
DeletePromptRequestRequestTypeDef = TypedDict(
    "DeletePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
    },
)
DeleteQueueRequestRequestTypeDef = TypedDict(
    "DeleteQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
    },
)
DeleteQuickConnectRequestRequestTypeDef = TypedDict(
    "DeleteQuickConnectRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
    },
)
DeleteRoutingProfileRequestRequestTypeDef = TypedDict(
    "DeleteRoutingProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
    },
)
DeleteRuleRequestRequestTypeDef = TypedDict(
    "DeleteRuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RuleId": str,
    },
)
DeleteSecurityProfileRequestRequestTypeDef = TypedDict(
    "DeleteSecurityProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "SecurityProfileId": str,
    },
)
DeleteTaskTemplateRequestRequestTypeDef = TypedDict(
    "DeleteTaskTemplateRequestRequestTypeDef",
    {
        "InstanceId": str,
        "TaskTemplateId": str,
    },
)
DeleteTrafficDistributionGroupRequestRequestTypeDef = TypedDict(
    "DeleteTrafficDistributionGroupRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
    },
)
DeleteUseCaseRequestRequestTypeDef = TypedDict(
    "DeleteUseCaseRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "UseCaseId": str,
    },
)
DeleteUserHierarchyGroupRequestRequestTypeDef = TypedDict(
    "DeleteUserHierarchyGroupRequestRequestTypeDef",
    {
        "HierarchyGroupId": str,
        "InstanceId": str,
    },
)
DeleteUserRequestRequestTypeDef = TypedDict(
    "DeleteUserRequestRequestTypeDef",
    {
        "InstanceId": str,
        "UserId": str,
    },
)
DeleteViewRequestRequestTypeDef = TypedDict(
    "DeleteViewRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
    },
)
DeleteViewVersionRequestRequestTypeDef = TypedDict(
    "DeleteViewVersionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "ViewVersion": int,
    },
)
DeleteVocabularyRequestRequestTypeDef = TypedDict(
    "DeleteVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "VocabularyId": str,
    },
)
DescribeAgentStatusRequestRequestTypeDef = TypedDict(
    "DescribeAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AgentStatusId": str,
    },
)
DescribeAuthenticationProfileRequestRequestTypeDef = TypedDict(
    "DescribeAuthenticationProfileRequestRequestTypeDef",
    {
        "AuthenticationProfileId": str,
        "InstanceId": str,
    },
)
DescribeContactEvaluationRequestRequestTypeDef = TypedDict(
    "DescribeContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
    },
)
DescribeContactFlowModuleRequestRequestTypeDef = TypedDict(
    "DescribeContactFlowModuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
    },
)
DescribeContactFlowRequestRequestTypeDef = TypedDict(
    "DescribeContactFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
    },
)
DescribeContactRequestRequestTypeDef = TypedDict(
    "DescribeContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
    },
)
DescribeEvaluationFormRequestRequestTypeDef = TypedDict(
    "DescribeEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": NotRequired[int],
    },
)
DescribeHoursOfOperationRequestRequestTypeDef = TypedDict(
    "DescribeHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "HoursOfOperationId": str,
    },
)
DescribeInstanceAttributeRequestRequestTypeDef = TypedDict(
    "DescribeInstanceAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AttributeType": InstanceAttributeTypeType,
    },
)
DescribeInstanceRequestRequestTypeDef = TypedDict(
    "DescribeInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
DescribeInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "DescribeInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
        "ResourceType": InstanceStorageResourceTypeType,
    },
)
DescribePhoneNumberRequestRequestTypeDef = TypedDict(
    "DescribePhoneNumberRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
    },
)
DescribePredefinedAttributeRequestRequestTypeDef = TypedDict(
    "DescribePredefinedAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
    },
)
DescribePromptRequestRequestTypeDef = TypedDict(
    "DescribePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
    },
)
PromptTypeDef = TypedDict(
    "PromptTypeDef",
    {
        "PromptARN": NotRequired[str],
        "PromptId": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
DescribeQueueRequestRequestTypeDef = TypedDict(
    "DescribeQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
    },
)
DescribeQuickConnectRequestRequestTypeDef = TypedDict(
    "DescribeQuickConnectRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
    },
)
DescribeRoutingProfileRequestRequestTypeDef = TypedDict(
    "DescribeRoutingProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
    },
)
DescribeRuleRequestRequestTypeDef = TypedDict(
    "DescribeRuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RuleId": str,
    },
)
DescribeSecurityProfileRequestRequestTypeDef = TypedDict(
    "DescribeSecurityProfileRequestRequestTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
    },
)
SecurityProfileTypeDef = TypedDict(
    "SecurityProfileTypeDef",
    {
        "Id": NotRequired[str],
        "OrganizationResourceId": NotRequired[str],
        "Arn": NotRequired[str],
        "SecurityProfileName": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "AllowedAccessControlTags": NotRequired[Dict[str, str]],
        "TagRestrictedResources": NotRequired[List[str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
        "HierarchyRestrictedResources": NotRequired[List[str]],
        "AllowedAccessControlHierarchyGroupId": NotRequired[str],
    },
)
DescribeTrafficDistributionGroupRequestRequestTypeDef = TypedDict(
    "DescribeTrafficDistributionGroupRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
    },
)
TrafficDistributionGroupTypeDef = TypedDict(
    "TrafficDistributionGroupTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "InstanceArn": NotRequired[str],
        "Status": NotRequired[TrafficDistributionGroupStatusType],
        "Tags": NotRequired[Dict[str, str]],
        "IsDefault": NotRequired[bool],
    },
)
DescribeUserHierarchyGroupRequestRequestTypeDef = TypedDict(
    "DescribeUserHierarchyGroupRequestRequestTypeDef",
    {
        "HierarchyGroupId": str,
        "InstanceId": str,
    },
)
DescribeUserHierarchyStructureRequestRequestTypeDef = TypedDict(
    "DescribeUserHierarchyStructureRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
DescribeUserRequestRequestTypeDef = TypedDict(
    "DescribeUserRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
    },
)
DescribeViewRequestRequestTypeDef = TypedDict(
    "DescribeViewRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
    },
)
DescribeVocabularyRequestRequestTypeDef = TypedDict(
    "DescribeVocabularyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "VocabularyId": str,
    },
)
VocabularyTypeDef = TypedDict(
    "VocabularyTypeDef",
    {
        "Name": str,
        "Id": str,
        "Arn": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "State": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": NotRequired[str],
        "Content": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)
RoutingProfileReferenceTypeDef = TypedDict(
    "RoutingProfileReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)
DisassociateAnalyticsDataSetRequestRequestTypeDef = TypedDict(
    "DisassociateAnalyticsDataSetRequestRequestTypeDef",
    {
        "InstanceId": str,
        "DataSetId": str,
        "TargetAccountId": NotRequired[str],
    },
)
DisassociateApprovedOriginRequestRequestTypeDef = TypedDict(
    "DisassociateApprovedOriginRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Origin": str,
    },
)
DisassociateFlowRequestRequestTypeDef = TypedDict(
    "DisassociateFlowRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceId": str,
        "ResourceType": Literal["SMS_PHONE_NUMBER"],
    },
)
DisassociateInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "DisassociateInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
        "ResourceType": InstanceStorageResourceTypeType,
    },
)
DisassociateLambdaFunctionRequestRequestTypeDef = TypedDict(
    "DisassociateLambdaFunctionRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FunctionArn": str,
    },
)
DisassociateLexBotRequestRequestTypeDef = TypedDict(
    "DisassociateLexBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "BotName": str,
        "LexRegion": str,
    },
)
DisassociatePhoneNumberContactFlowRequestRequestTypeDef = TypedDict(
    "DisassociatePhoneNumberContactFlowRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "InstanceId": str,
    },
)
DisassociateQueueQuickConnectsRequestRequestTypeDef = TypedDict(
    "DisassociateQueueQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "QuickConnectIds": Sequence[str],
    },
)
RoutingProfileQueueReferenceTypeDef = TypedDict(
    "RoutingProfileQueueReferenceTypeDef",
    {
        "QueueId": str,
        "Channel": ChannelType,
    },
)
DisassociateSecurityKeyRequestRequestTypeDef = TypedDict(
    "DisassociateSecurityKeyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
    },
)
DisassociateTrafficDistributionGroupUserRequestRequestTypeDef = TypedDict(
    "DisassociateTrafficDistributionGroupUserRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
        "UserId": str,
        "InstanceId": str,
    },
)
UserProficiencyDisassociateTypeDef = TypedDict(
    "UserProficiencyDisassociateTypeDef",
    {
        "AttributeName": str,
        "AttributeValue": str,
    },
)
DisconnectReasonTypeDef = TypedDict(
    "DisconnectReasonTypeDef",
    {
        "Code": NotRequired[str],
    },
)
DismissUserContactRequestRequestTypeDef = TypedDict(
    "DismissUserContactRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
        "ContactId": str,
    },
)
DownloadUrlMetadataTypeDef = TypedDict(
    "DownloadUrlMetadataTypeDef",
    {
        "Url": NotRequired[str],
        "UrlExpiry": NotRequired[str],
    },
)
EmailReferenceTypeDef = TypedDict(
    "EmailReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)
EncryptionConfigTypeDef = TypedDict(
    "EncryptionConfigTypeDef",
    {
        "EncryptionType": Literal["KMS"],
        "KeyId": str,
    },
)
EvaluationAnswerDataTypeDef = TypedDict(
    "EvaluationAnswerDataTypeDef",
    {
        "StringValue": NotRequired[str],
        "NumericValue": NotRequired[float],
        "NotApplicable": NotRequired[bool],
    },
)
NumericQuestionPropertyValueAutomationTypeDef = TypedDict(
    "NumericQuestionPropertyValueAutomationTypeDef",
    {
        "Label": NumericQuestionPropertyAutomationLabelType,
    },
)
EvaluationFormNumericQuestionOptionTypeDef = TypedDict(
    "EvaluationFormNumericQuestionOptionTypeDef",
    {
        "MinValue": int,
        "MaxValue": int,
        "Score": NotRequired[int],
        "AutomaticFail": NotRequired[bool],
    },
)
EvaluationFormSectionOutputTypeDef = TypedDict(
    "EvaluationFormSectionOutputTypeDef",
    {
        "Title": str,
        "RefId": str,
        "Items": List["EvaluationFormItemOutputTypeDef"],
        "Instructions": NotRequired[str],
        "Weight": NotRequired[float],
    },
)
EvaluationFormSectionTypeDef = TypedDict(
    "EvaluationFormSectionTypeDef",
    {
        "Title": str,
        "RefId": str,
        "Items": Sequence["EvaluationFormItemTypeDef"],
        "Instructions": NotRequired[str],
        "Weight": NotRequired[float],
    },
)
SingleSelectQuestionRuleCategoryAutomationTypeDef = TypedDict(
    "SingleSelectQuestionRuleCategoryAutomationTypeDef",
    {
        "Category": str,
        "Condition": SingleSelectQuestionRuleCategoryAutomationConditionType,
        "OptionRefId": str,
    },
)
EvaluationFormSingleSelectQuestionOptionTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionOptionTypeDef",
    {
        "RefId": str,
        "Text": str,
        "Score": NotRequired[int],
        "AutomaticFail": NotRequired[bool],
    },
)
EvaluationFormSummaryTypeDef = TypedDict(
    "EvaluationFormSummaryTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "Title": str,
        "CreatedTime": datetime,
        "CreatedBy": str,
        "LastModifiedTime": datetime,
        "LastModifiedBy": str,
        "LatestVersion": int,
        "LastActivatedTime": NotRequired[datetime],
        "LastActivatedBy": NotRequired[str],
        "ActiveVersion": NotRequired[int],
    },
)
EvaluationFormVersionSummaryTypeDef = TypedDict(
    "EvaluationFormVersionSummaryTypeDef",
    {
        "EvaluationFormArn": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
        "Locked": bool,
        "Status": EvaluationFormVersionStatusType,
        "CreatedTime": datetime,
        "CreatedBy": str,
        "LastModifiedTime": datetime,
        "LastModifiedBy": str,
    },
)
EvaluationScoreTypeDef = TypedDict(
    "EvaluationScoreTypeDef",
    {
        "Percentage": NotRequired[float],
        "NotApplicable": NotRequired[bool],
        "AutomaticFail": NotRequired[bool],
    },
)
EvaluationNoteTypeDef = TypedDict(
    "EvaluationNoteTypeDef",
    {
        "Value": NotRequired[str],
    },
)
EventBridgeActionDefinitionTypeDef = TypedDict(
    "EventBridgeActionDefinitionTypeDef",
    {
        "Name": str,
    },
)
ExpiryTypeDef = TypedDict(
    "ExpiryTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
        "ExpiryTimestamp": NotRequired[datetime],
    },
)
FieldValueUnionOutputTypeDef = TypedDict(
    "FieldValueUnionOutputTypeDef",
    {
        "BooleanValue": NotRequired[bool],
        "DoubleValue": NotRequired[float],
        "EmptyValue": NotRequired[Dict[str, Any]],
        "StringValue": NotRequired[str],
    },
)
FieldValueUnionTypeDef = TypedDict(
    "FieldValueUnionTypeDef",
    {
        "BooleanValue": NotRequired[bool],
        "DoubleValue": NotRequired[float],
        "EmptyValue": NotRequired[Mapping[str, Any]],
        "StringValue": NotRequired[str],
    },
)
FilterV2TypeDef = TypedDict(
    "FilterV2TypeDef",
    {
        "FilterKey": NotRequired[str],
        "FilterValues": NotRequired[Sequence[str]],
    },
)
FiltersTypeDef = TypedDict(
    "FiltersTypeDef",
    {
        "Queues": NotRequired[Sequence[str]],
        "Channels": NotRequired[Sequence[ChannelType]],
        "RoutingProfiles": NotRequired[Sequence[str]],
        "RoutingStepExpressions": NotRequired[Sequence[str]],
    },
)
GetAttachedFileRequestRequestTypeDef = TypedDict(
    "GetAttachedFileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FileId": str,
        "AssociatedResourceArn": str,
        "UrlExpiryInSeconds": NotRequired[int],
    },
)
GetContactAttributesRequestRequestTypeDef = TypedDict(
    "GetContactAttributesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "InitialContactId": str,
    },
)
GetFederationTokenRequestRequestTypeDef = TypedDict(
    "GetFederationTokenRequestRequestTypeDef",
    {
        "InstanceId": str,
    },
)
GetFlowAssociationRequestRequestTypeDef = TypedDict(
    "GetFlowAssociationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceId": str,
        "ResourceType": Literal["SMS_PHONE_NUMBER"],
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
TimestampTypeDef = Union[datetime, str]
IntervalDetailsTypeDef = TypedDict(
    "IntervalDetailsTypeDef",
    {
        "TimeZone": NotRequired[str],
        "IntervalPeriod": NotRequired[IntervalPeriodType],
    },
)
GetPromptFileRequestRequestTypeDef = TypedDict(
    "GetPromptFileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
    },
)
GetTaskTemplateRequestRequestTypeDef = TypedDict(
    "GetTaskTemplateRequestRequestTypeDef",
    {
        "InstanceId": str,
        "TaskTemplateId": str,
        "SnapshotVersion": NotRequired[str],
    },
)
GetTrafficDistributionRequestRequestTypeDef = TypedDict(
    "GetTrafficDistributionRequestRequestTypeDef",
    {
        "Id": str,
    },
)
HierarchyGroupSummaryReferenceTypeDef = TypedDict(
    "HierarchyGroupSummaryReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)
HierarchyGroupSummaryTypeDef = TypedDict(
    "HierarchyGroupSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
HierarchyLevelTypeDef = TypedDict(
    "HierarchyLevelTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
HierarchyLevelUpdateTypeDef = TypedDict(
    "HierarchyLevelUpdateTypeDef",
    {
        "Name": str,
    },
)
ThresholdTypeDef = TypedDict(
    "ThresholdTypeDef",
    {
        "Comparison": NotRequired[Literal["LT"]],
        "ThresholdValue": NotRequired[float],
    },
)
HoursOfOperationTimeSliceTypeDef = TypedDict(
    "HoursOfOperationTimeSliceTypeDef",
    {
        "Hours": int,
        "Minutes": int,
    },
)
HoursOfOperationSummaryTypeDef = TypedDict(
    "HoursOfOperationSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ImportPhoneNumberRequestRequestTypeDef = TypedDict(
    "ImportPhoneNumberRequestRequestTypeDef",
    {
        "InstanceId": str,
        "SourcePhoneNumberArn": str,
        "PhoneNumberDescription": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "ClientToken": NotRequired[str],
    },
)
InstanceStatusReasonTypeDef = TypedDict(
    "InstanceStatusReasonTypeDef",
    {
        "Message": NotRequired[str],
    },
)
KinesisFirehoseConfigTypeDef = TypedDict(
    "KinesisFirehoseConfigTypeDef",
    {
        "FirehoseArn": str,
    },
)
KinesisStreamConfigTypeDef = TypedDict(
    "KinesisStreamConfigTypeDef",
    {
        "StreamArn": str,
    },
)
InstanceSummaryTypeDef = TypedDict(
    "InstanceSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "IdentityManagementType": NotRequired[DirectoryTypeType],
        "InstanceAlias": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "ServiceRole": NotRequired[str],
        "InstanceStatus": NotRequired[InstanceStatusType],
        "InboundCallsEnabled": NotRequired[bool],
        "OutboundCallsEnabled": NotRequired[bool],
        "InstanceAccessUrl": NotRequired[str],
    },
)
IntegrationAssociationSummaryTypeDef = TypedDict(
    "IntegrationAssociationSummaryTypeDef",
    {
        "IntegrationAssociationId": NotRequired[str],
        "IntegrationAssociationArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "IntegrationType": NotRequired[IntegrationTypeType],
        "IntegrationArn": NotRequired[str],
        "SourceApplicationUrl": NotRequired[str],
        "SourceApplicationName": NotRequired[str],
        "SourceType": NotRequired[SourceTypeType],
    },
)
TaskTemplateFieldIdentifierTypeDef = TypedDict(
    "TaskTemplateFieldIdentifierTypeDef",
    {
        "Name": NotRequired[str],
    },
)
ListAgentStatusRequestRequestTypeDef = TypedDict(
    "ListAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "AgentStatusTypes": NotRequired[Sequence[AgentStatusTypeType]],
    },
)
ListAnalyticsDataAssociationsRequestRequestTypeDef = TypedDict(
    "ListAnalyticsDataAssociationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "DataSetId": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListApprovedOriginsRequestRequestTypeDef = TypedDict(
    "ListApprovedOriginsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListAuthenticationProfilesRequestRequestTypeDef = TypedDict(
    "ListAuthenticationProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListBotsRequestRequestTypeDef = TypedDict(
    "ListBotsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexVersion": LexVersionType,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListContactEvaluationsRequestRequestTypeDef = TypedDict(
    "ListContactEvaluationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "NextToken": NotRequired[str],
    },
)
ListContactFlowModulesRequestRequestTypeDef = TypedDict(
    "ListContactFlowModulesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ContactFlowModuleState": NotRequired[ContactFlowModuleStateType],
    },
)
ListContactFlowsRequestRequestTypeDef = TypedDict(
    "ListContactFlowsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowTypes": NotRequired[Sequence[ContactFlowTypeType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListContactReferencesRequestRequestTypeDef = TypedDict(
    "ListContactReferencesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ReferenceTypes": Sequence[ReferenceTypeType],
        "NextToken": NotRequired[str],
    },
)
ListDefaultVocabulariesRequestRequestTypeDef = TypedDict(
    "ListDefaultVocabulariesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListEvaluationFormVersionsRequestRequestTypeDef = TypedDict(
    "ListEvaluationFormVersionsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListEvaluationFormsRequestRequestTypeDef = TypedDict(
    "ListEvaluationFormsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListFlowAssociationsRequestRequestTypeDef = TypedDict(
    "ListFlowAssociationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceType": NotRequired[Literal["VOICE_PHONE_NUMBER"]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListHoursOfOperationsRequestRequestTypeDef = TypedDict(
    "ListHoursOfOperationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListInstanceAttributesRequestRequestTypeDef = TypedDict(
    "ListInstanceAttributesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListInstanceStorageConfigsRequestRequestTypeDef = TypedDict(
    "ListInstanceStorageConfigsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListInstancesRequestRequestTypeDef = TypedDict(
    "ListInstancesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListIntegrationAssociationsRequestRequestTypeDef = TypedDict(
    "ListIntegrationAssociationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationType": NotRequired[IntegrationTypeType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "IntegrationArn": NotRequired[str],
    },
)
ListLambdaFunctionsRequestRequestTypeDef = TypedDict(
    "ListLambdaFunctionsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListLexBotsRequestRequestTypeDef = TypedDict(
    "ListLexBotsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListPhoneNumbersRequestRequestTypeDef = TypedDict(
    "ListPhoneNumbersRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
PhoneNumberSummaryTypeDef = TypedDict(
    "PhoneNumberSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "PhoneNumber": NotRequired[str],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
    },
)
ListPhoneNumbersSummaryTypeDef = TypedDict(
    "ListPhoneNumbersSummaryTypeDef",
    {
        "PhoneNumberId": NotRequired[str],
        "PhoneNumberArn": NotRequired[str],
        "PhoneNumber": NotRequired[str],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "PhoneNumberDescription": NotRequired[str],
        "SourcePhoneNumberArn": NotRequired[str],
    },
)
ListPhoneNumbersV2RequestRequestTypeDef = TypedDict(
    "ListPhoneNumbersV2RequestRequestTypeDef",
    {
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberPrefix": NotRequired[str],
    },
)
ListPredefinedAttributesRequestRequestTypeDef = TypedDict(
    "ListPredefinedAttributesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
PredefinedAttributeSummaryTypeDef = TypedDict(
    "PredefinedAttributeSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ListPromptsRequestRequestTypeDef = TypedDict(
    "ListPromptsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
PromptSummaryTypeDef = TypedDict(
    "PromptSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ListQueueQuickConnectsRequestRequestTypeDef = TypedDict(
    "ListQueueQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
QuickConnectSummaryTypeDef = TypedDict(
    "QuickConnectSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "QuickConnectType": NotRequired[QuickConnectTypeType],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ListQueuesRequestRequestTypeDef = TypedDict(
    "ListQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueTypes": NotRequired[Sequence[QueueTypeType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
QueueSummaryTypeDef = TypedDict(
    "QueueSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "QueueType": NotRequired[QueueTypeType],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ListQuickConnectsRequestRequestTypeDef = TypedDict(
    "ListQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "QuickConnectTypes": NotRequired[Sequence[QuickConnectTypeType]],
    },
)
ListRealtimeContactAnalysisSegmentsV2RequestRequestTypeDef = TypedDict(
    "ListRealtimeContactAnalysisSegmentsV2RequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "OutputType": RealTimeContactAnalysisOutputTypeType,
        "SegmentTypes": Sequence[RealTimeContactAnalysisSegmentTypeType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "ListRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
RoutingProfileQueueConfigSummaryTypeDef = TypedDict(
    "RoutingProfileQueueConfigSummaryTypeDef",
    {
        "QueueId": str,
        "QueueArn": str,
        "QueueName": str,
        "Priority": int,
        "Delay": int,
        "Channel": ChannelType,
    },
)
ListRoutingProfilesRequestRequestTypeDef = TypedDict(
    "ListRoutingProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
RoutingProfileSummaryTypeDef = TypedDict(
    "RoutingProfileSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ListRulesRequestRequestTypeDef = TypedDict(
    "ListRulesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PublishStatus": NotRequired[RulePublishStatusType],
        "EventSourceName": NotRequired[EventSourceNameType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListSecurityKeysRequestRequestTypeDef = TypedDict(
    "ListSecurityKeysRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
SecurityKeyTypeDef = TypedDict(
    "SecurityKeyTypeDef",
    {
        "AssociationId": NotRequired[str],
        "Key": NotRequired[str],
        "CreationTime": NotRequired[datetime],
    },
)
ListSecurityProfileApplicationsRequestRequestTypeDef = TypedDict(
    "ListSecurityProfileApplicationsRequestRequestTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListSecurityProfilePermissionsRequestRequestTypeDef = TypedDict(
    "ListSecurityProfilePermissionsRequestRequestTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListSecurityProfilesRequestRequestTypeDef = TypedDict(
    "ListSecurityProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
SecurityProfileSummaryTypeDef = TypedDict(
    "SecurityProfileSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
ListTaskTemplatesRequestRequestTypeDef = TypedDict(
    "ListTaskTemplatesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "Status": NotRequired[TaskTemplateStatusType],
        "Name": NotRequired[str],
    },
)
TaskTemplateMetadataTypeDef = TypedDict(
    "TaskTemplateMetadataTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Status": NotRequired[TaskTemplateStatusType],
        "LastModifiedTime": NotRequired[datetime],
        "CreatedTime": NotRequired[datetime],
    },
)
ListTrafficDistributionGroupUsersRequestRequestTypeDef = TypedDict(
    "ListTrafficDistributionGroupUsersRequestRequestTypeDef",
    {
        "TrafficDistributionGroupId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
TrafficDistributionGroupUserSummaryTypeDef = TypedDict(
    "TrafficDistributionGroupUserSummaryTypeDef",
    {
        "UserId": NotRequired[str],
    },
)
ListTrafficDistributionGroupsRequestRequestTypeDef = TypedDict(
    "ListTrafficDistributionGroupsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "InstanceId": NotRequired[str],
    },
)
TrafficDistributionGroupSummaryTypeDef = TypedDict(
    "TrafficDistributionGroupSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "InstanceArn": NotRequired[str],
        "Status": NotRequired[TrafficDistributionGroupStatusType],
        "IsDefault": NotRequired[bool],
    },
)
ListUseCasesRequestRequestTypeDef = TypedDict(
    "ListUseCasesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
UseCaseTypeDef = TypedDict(
    "UseCaseTypeDef",
    {
        "UseCaseId": NotRequired[str],
        "UseCaseArn": NotRequired[str],
        "UseCaseType": NotRequired[UseCaseTypeType],
    },
)
ListUserHierarchyGroupsRequestRequestTypeDef = TypedDict(
    "ListUserHierarchyGroupsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListUserProficienciesRequestRequestTypeDef = TypedDict(
    "ListUserProficienciesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "UserId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListUsersRequestRequestTypeDef = TypedDict(
    "ListUsersRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
UserSummaryTypeDef = TypedDict(
    "UserSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Username": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
ListViewVersionsRequestRequestTypeDef = TypedDict(
    "ListViewVersionsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ViewVersionSummaryTypeDef = TypedDict(
    "ViewVersionSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Description": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[ViewTypeType],
        "Version": NotRequired[int],
        "VersionDescription": NotRequired[str],
    },
)
ListViewsRequestRequestTypeDef = TypedDict(
    "ListViewsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Type": NotRequired[ViewTypeType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ViewSummaryTypeDef = TypedDict(
    "ViewSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Type": NotRequired[ViewTypeType],
        "Status": NotRequired[ViewStatusType],
        "Description": NotRequired[str],
    },
)
MediaPlacementTypeDef = TypedDict(
    "MediaPlacementTypeDef",
    {
        "AudioHostUrl": NotRequired[str],
        "AudioFallbackUrl": NotRequired[str],
        "SignalingUrl": NotRequired[str],
        "TurnControlUrl": NotRequired[str],
        "EventIngestionUrl": NotRequired[str],
    },
)
MetricFilterV2OutputTypeDef = TypedDict(
    "MetricFilterV2OutputTypeDef",
    {
        "MetricFilterKey": NotRequired[str],
        "MetricFilterValues": NotRequired[List[str]],
        "Negate": NotRequired[bool],
    },
)
MetricFilterV2TypeDef = TypedDict(
    "MetricFilterV2TypeDef",
    {
        "MetricFilterKey": NotRequired[str],
        "MetricFilterValues": NotRequired[Sequence[str]],
        "Negate": NotRequired[bool],
    },
)
MetricIntervalTypeDef = TypedDict(
    "MetricIntervalTypeDef",
    {
        "Interval": NotRequired[IntervalPeriodType],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
    },
)
ThresholdV2TypeDef = TypedDict(
    "ThresholdV2TypeDef",
    {
        "Comparison": NotRequired[str],
        "ThresholdValue": NotRequired[float],
    },
)
MonitorContactRequestRequestTypeDef = TypedDict(
    "MonitorContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "UserId": str,
        "AllowedMonitorCapabilities": NotRequired[Sequence[MonitorCapabilityType]],
        "ClientToken": NotRequired[str],
    },
)
ParticipantDetailsTypeDef = TypedDict(
    "ParticipantDetailsTypeDef",
    {
        "DisplayName": str,
    },
)
NotificationRecipientTypeOutputTypeDef = TypedDict(
    "NotificationRecipientTypeOutputTypeDef",
    {
        "UserTags": NotRequired[Dict[str, str]],
        "UserIds": NotRequired[List[str]],
    },
)
NotificationRecipientTypeTypeDef = TypedDict(
    "NotificationRecipientTypeTypeDef",
    {
        "UserTags": NotRequired[Mapping[str, str]],
        "UserIds": NotRequired[Sequence[str]],
    },
)
NumberReferenceTypeDef = TypedDict(
    "NumberReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)
ParticipantTimerValueTypeDef = TypedDict(
    "ParticipantTimerValueTypeDef",
    {
        "ParticipantTimerAction": NotRequired[Literal["Unset"]],
        "ParticipantTimerDurationInMinutes": NotRequired[int],
    },
)
PauseContactRequestRequestTypeDef = TypedDict(
    "PauseContactRequestRequestTypeDef",
    {
        "ContactId": str,
        "InstanceId": str,
        "ContactFlowId": NotRequired[str],
    },
)
PersistentChatTypeDef = TypedDict(
    "PersistentChatTypeDef",
    {
        "RehydrationType": NotRequired[RehydrationTypeType],
        "SourceContactId": NotRequired[str],
    },
)
PhoneNumberQuickConnectConfigTypeDef = TypedDict(
    "PhoneNumberQuickConnectConfigTypeDef",
    {
        "PhoneNumber": str,
    },
)
PredefinedAttributeValuesOutputTypeDef = TypedDict(
    "PredefinedAttributeValuesOutputTypeDef",
    {
        "StringList": NotRequired[List[str]],
    },
)
PredefinedAttributeValuesExtraOutputTypeDef = TypedDict(
    "PredefinedAttributeValuesExtraOutputTypeDef",
    {
        "StringList": NotRequired[List[str]],
    },
)
PutUserStatusRequestRequestTypeDef = TypedDict(
    "PutUserStatusRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
        "AgentStatusId": str,
    },
)
QueueQuickConnectConfigTypeDef = TypedDict(
    "QueueQuickConnectConfigTypeDef",
    {
        "QueueId": str,
        "ContactFlowId": str,
    },
)
UserQuickConnectConfigTypeDef = TypedDict(
    "UserQuickConnectConfigTypeDef",
    {
        "UserId": str,
        "ContactFlowId": str,
    },
)
RealTimeContactAnalysisAttachmentTypeDef = TypedDict(
    "RealTimeContactAnalysisAttachmentTypeDef",
    {
        "AttachmentName": str,
        "AttachmentId": str,
        "ContentType": NotRequired[str],
        "Status": NotRequired[ArtifactStatusType],
    },
)
RealTimeContactAnalysisCharacterIntervalTypeDef = TypedDict(
    "RealTimeContactAnalysisCharacterIntervalTypeDef",
    {
        "BeginOffsetChar": int,
        "EndOffsetChar": int,
    },
)
RealTimeContactAnalysisTimeDataTypeDef = TypedDict(
    "RealTimeContactAnalysisTimeDataTypeDef",
    {
        "AbsoluteTime": NotRequired[datetime],
    },
)
StringReferenceTypeDef = TypedDict(
    "StringReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)
UrlReferenceTypeDef = TypedDict(
    "UrlReferenceTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)
ReferenceTypeDef = TypedDict(
    "ReferenceTypeDef",
    {
        "Value": str,
        "Type": ReferenceTypeType,
    },
)
ReleasePhoneNumberRequestRequestTypeDef = TypedDict(
    "ReleasePhoneNumberRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "ClientToken": NotRequired[str],
    },
)
ReplicateInstanceRequestRequestTypeDef = TypedDict(
    "ReplicateInstanceRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ReplicaRegion": str,
        "ReplicaAlias": str,
        "ClientToken": NotRequired[str],
    },
)
TagSearchConditionTypeDef = TypedDict(
    "TagSearchConditionTypeDef",
    {
        "tagKey": NotRequired[str],
        "tagValue": NotRequired[str],
        "tagKeyComparisonType": NotRequired[StringComparisonTypeType],
        "tagValueComparisonType": NotRequired[StringComparisonTypeType],
    },
)
ResumeContactRecordingRequestRequestTypeDef = TypedDict(
    "ResumeContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
    },
)
ResumeContactRequestRequestTypeDef = TypedDict(
    "ResumeContactRequestRequestTypeDef",
    {
        "ContactId": str,
        "InstanceId": str,
        "ContactFlowId": NotRequired[str],
    },
)
SubmitAutoEvaluationActionDefinitionTypeDef = TypedDict(
    "SubmitAutoEvaluationActionDefinitionTypeDef",
    {
        "EvaluationFormId": str,
    },
)
SearchAvailablePhoneNumbersRequestRequestTypeDef = TypedDict(
    "SearchAvailablePhoneNumbersRequestRequestTypeDef",
    {
        "PhoneNumberCountryCode": PhoneNumberCountryCodeType,
        "PhoneNumberType": PhoneNumberTypeType,
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "PhoneNumberPrefix": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
SortTypeDef = TypedDict(
    "SortTypeDef",
    {
        "FieldName": SortableFieldNameType,
        "Order": SortOrderType,
    },
)
SearchPredefinedAttributesRequestRequestTypeDef = TypedDict(
    "SearchPredefinedAttributesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchCriteria": NotRequired["PredefinedAttributeSearchCriteriaTypeDef"],
    },
)
TagSetTypeDef = TypedDict(
    "TagSetTypeDef",
    {
        "key": NotRequired[str],
        "value": NotRequired[str],
    },
)
SecurityProfileSearchSummaryTypeDef = TypedDict(
    "SecurityProfileSearchSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "OrganizationResourceId": NotRequired[str],
        "Arn": NotRequired[str],
        "SecurityProfileName": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)
SearchVocabulariesRequestRequestTypeDef = TypedDict(
    "SearchVocabulariesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "State": NotRequired[VocabularyStateType],
        "NameStartsWith": NotRequired[str],
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
    },
)
VocabularySummaryTypeDef = TypedDict(
    "VocabularySummaryTypeDef",
    {
        "Name": str,
        "Id": str,
        "Arn": str,
        "LanguageCode": VocabularyLanguageCodeType,
        "State": VocabularyStateType,
        "LastModifiedTime": datetime,
        "FailureReason": NotRequired[str],
    },
)
SearchableContactAttributesCriteriaTypeDef = TypedDict(
    "SearchableContactAttributesCriteriaTypeDef",
    {
        "Key": str,
        "Values": Sequence[str],
    },
)
SignInDistributionTypeDef = TypedDict(
    "SignInDistributionTypeDef",
    {
        "Region": str,
        "Enabled": bool,
    },
)
UploadUrlMetadataTypeDef = TypedDict(
    "UploadUrlMetadataTypeDef",
    {
        "Url": NotRequired[str],
        "UrlExpiry": NotRequired[str],
        "HeadersToInclude": NotRequired[Dict[str, str]],
    },
)
StartContactEvaluationRequestRequestTypeDef = TypedDict(
    "StartContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "EvaluationFormId": str,
        "ClientToken": NotRequired[str],
    },
)
VoiceRecordingConfigurationTypeDef = TypedDict(
    "VoiceRecordingConfigurationTypeDef",
    {
        "VoiceRecordingTrack": NotRequired[VoiceRecordingTrackType],
    },
)
StopContactRecordingRequestRequestTypeDef = TypedDict(
    "StopContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
    },
)
StopContactStreamingRequestRequestTypeDef = TypedDict(
    "StopContactStreamingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "StreamingId": str,
    },
)
SuspendContactRecordingRequestRequestTypeDef = TypedDict(
    "SuspendContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
    },
)
TagContactRequestRequestTypeDef = TypedDict(
    "TagContactRequestRequestTypeDef",
    {
        "ContactId": str,
        "InstanceId": str,
        "Tags": Mapping[str, str],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
TranscriptCriteriaTypeDef = TypedDict(
    "TranscriptCriteriaTypeDef",
    {
        "ParticipantRole": ParticipantRoleType,
        "SearchText": Sequence[str],
        "MatchType": SearchContactsMatchTypeType,
    },
)
TransferContactRequestRequestTypeDef = TypedDict(
    "TransferContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ContactFlowId": str,
        "QueueId": NotRequired[str],
        "UserId": NotRequired[str],
        "ClientToken": NotRequired[str],
    },
)
UntagContactRequestRequestTypeDef = TypedDict(
    "UntagContactRequestRequestTypeDef",
    {
        "ContactId": str,
        "InstanceId": str,
        "TagKeys": Sequence[str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateAgentStatusRequestRequestTypeDef = TypedDict(
    "UpdateAgentStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AgentStatusId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "State": NotRequired[AgentStatusStateType],
        "DisplayOrder": NotRequired[int],
        "ResetOrderNumber": NotRequired[bool],
    },
)
UpdateAuthenticationProfileRequestRequestTypeDef = TypedDict(
    "UpdateAuthenticationProfileRequestRequestTypeDef",
    {
        "AuthenticationProfileId": str,
        "InstanceId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "AllowedIps": NotRequired[Sequence[str]],
        "BlockedIps": NotRequired[Sequence[str]],
        "PeriodicSessionDuration": NotRequired[int],
    },
)
UpdateContactAttributesRequestRequestTypeDef = TypedDict(
    "UpdateContactAttributesRequestRequestTypeDef",
    {
        "InitialContactId": str,
        "InstanceId": str,
        "Attributes": Mapping[str, str],
    },
)
UpdateContactFlowContentRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowContentRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "Content": str,
    },
)
UpdateContactFlowMetadataRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowMetadataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "ContactFlowState": NotRequired[ContactFlowStateType],
    },
)
UpdateContactFlowModuleContentRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowModuleContentRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
        "Content": str,
    },
)
UpdateContactFlowModuleMetadataRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowModuleMetadataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "State": NotRequired[ContactFlowModuleStateType],
    },
)
UpdateContactFlowNameRequestRequestTypeDef = TypedDict(
    "UpdateContactFlowNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)
UpdateContactRoutingDataRequestRequestTypeDef = TypedDict(
    "UpdateContactRoutingDataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "QueueTimeAdjustmentSeconds": NotRequired[int],
        "QueuePriority": NotRequired[int],
    },
)
UpdateInstanceAttributeRequestRequestTypeDef = TypedDict(
    "UpdateInstanceAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AttributeType": InstanceAttributeTypeType,
        "Value": str,
    },
)
UpdatePhoneNumberMetadataRequestRequestTypeDef = TypedDict(
    "UpdatePhoneNumberMetadataRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "PhoneNumberDescription": NotRequired[str],
        "ClientToken": NotRequired[str],
    },
)
UpdatePhoneNumberRequestRequestTypeDef = TypedDict(
    "UpdatePhoneNumberRequestRequestTypeDef",
    {
        "PhoneNumberId": str,
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "ClientToken": NotRequired[str],
    },
)
UpdatePromptRequestRequestTypeDef = TypedDict(
    "UpdatePromptRequestRequestTypeDef",
    {
        "InstanceId": str,
        "PromptId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "S3Uri": NotRequired[str],
    },
)
UpdateQueueHoursOfOperationRequestRequestTypeDef = TypedDict(
    "UpdateQueueHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "HoursOfOperationId": str,
    },
)
UpdateQueueMaxContactsRequestRequestTypeDef = TypedDict(
    "UpdateQueueMaxContactsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "MaxContacts": NotRequired[int],
    },
)
UpdateQueueNameRequestRequestTypeDef = TypedDict(
    "UpdateQueueNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)
UpdateQueueStatusRequestRequestTypeDef = TypedDict(
    "UpdateQueueStatusRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "Status": QueueStatusType,
    },
)
UpdateQuickConnectNameRequestRequestTypeDef = TypedDict(
    "UpdateQuickConnectNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)
UpdateRoutingProfileAgentAvailabilityTimerRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileAgentAvailabilityTimerRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "AgentAvailabilityTimer": AgentAvailabilityTimerType,
    },
)
UpdateRoutingProfileDefaultOutboundQueueRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileDefaultOutboundQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "DefaultOutboundQueueId": str,
    },
)
UpdateRoutingProfileNameRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileNameRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)
UpdateUserHierarchyGroupNameRequestRequestTypeDef = TypedDict(
    "UpdateUserHierarchyGroupNameRequestRequestTypeDef",
    {
        "Name": str,
        "HierarchyGroupId": str,
        "InstanceId": str,
    },
)
UpdateUserHierarchyRequestRequestTypeDef = TypedDict(
    "UpdateUserHierarchyRequestRequestTypeDef",
    {
        "UserId": str,
        "InstanceId": str,
        "HierarchyGroupId": NotRequired[str],
    },
)
UpdateUserRoutingProfileRequestRequestTypeDef = TypedDict(
    "UpdateUserRoutingProfileRequestRequestTypeDef",
    {
        "RoutingProfileId": str,
        "UserId": str,
        "InstanceId": str,
    },
)
UpdateUserSecurityProfilesRequestRequestTypeDef = TypedDict(
    "UpdateUserSecurityProfilesRequestRequestTypeDef",
    {
        "SecurityProfileIds": Sequence[str],
        "UserId": str,
        "InstanceId": str,
    },
)
UpdateViewMetadataRequestRequestTypeDef = TypedDict(
    "UpdateViewMetadataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)
UserReferenceTypeDef = TypedDict(
    "UserReferenceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
    },
)
UserIdentityInfoLiteTypeDef = TypedDict(
    "UserIdentityInfoLiteTypeDef",
    {
        "FirstName": NotRequired[str],
        "LastName": NotRequired[str],
    },
)
ViewContentTypeDef = TypedDict(
    "ViewContentTypeDef",
    {
        "InputSchema": NotRequired[str],
        "Template": NotRequired[str],
        "Actions": NotRequired[List[str]],
    },
)
RuleSummaryTypeDef = TypedDict(
    "RuleSummaryTypeDef",
    {
        "Name": str,
        "RuleId": str,
        "RuleArn": str,
        "EventSourceName": EventSourceNameType,
        "PublishStatus": RulePublishStatusType,
        "ActionSummaries": List[ActionSummaryTypeDef],
        "CreatedTime": datetime,
        "LastUpdatedTime": datetime,
    },
)
ActivateEvaluationFormResponseTypeDef = TypedDict(
    "ActivateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "EvaluationFormVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociateAnalyticsDataSetResponseTypeDef = TypedDict(
    "AssociateAnalyticsDataSetResponseTypeDef",
    {
        "DataSetId": str,
        "TargetAccountId": str,
        "ResourceShareId": str,
        "ResourceShareArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociateInstanceStorageConfigResponseTypeDef = TypedDict(
    "AssociateInstanceStorageConfigResponseTypeDef",
    {
        "AssociationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociateSecurityKeyResponseTypeDef = TypedDict(
    "AssociateSecurityKeyResponseTypeDef",
    {
        "AssociationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClaimPhoneNumberResponseTypeDef = TypedDict(
    "ClaimPhoneNumberResponseTypeDef",
    {
        "PhoneNumberId": str,
        "PhoneNumberArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAgentStatusResponseTypeDef = TypedDict(
    "CreateAgentStatusResponseTypeDef",
    {
        "AgentStatusARN": str,
        "AgentStatusId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateContactFlowModuleResponseTypeDef = TypedDict(
    "CreateContactFlowModuleResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateContactFlowResponseTypeDef = TypedDict(
    "CreateContactFlowResponseTypeDef",
    {
        "ContactFlowId": str,
        "ContactFlowArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateEvaluationFormResponseTypeDef = TypedDict(
    "CreateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHoursOfOperationResponseTypeDef = TypedDict(
    "CreateHoursOfOperationResponseTypeDef",
    {
        "HoursOfOperationId": str,
        "HoursOfOperationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInstanceResponseTypeDef = TypedDict(
    "CreateInstanceResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateIntegrationAssociationResponseTypeDef = TypedDict(
    "CreateIntegrationAssociationResponseTypeDef",
    {
        "IntegrationAssociationId": str,
        "IntegrationAssociationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePersistentContactAssociationResponseTypeDef = TypedDict(
    "CreatePersistentContactAssociationResponseTypeDef",
    {
        "ContinuedFromContactId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePromptResponseTypeDef = TypedDict(
    "CreatePromptResponseTypeDef",
    {
        "PromptARN": str,
        "PromptId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateQueueResponseTypeDef = TypedDict(
    "CreateQueueResponseTypeDef",
    {
        "QueueArn": str,
        "QueueId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateQuickConnectResponseTypeDef = TypedDict(
    "CreateQuickConnectResponseTypeDef",
    {
        "QuickConnectARN": str,
        "QuickConnectId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRoutingProfileResponseTypeDef = TypedDict(
    "CreateRoutingProfileResponseTypeDef",
    {
        "RoutingProfileArn": str,
        "RoutingProfileId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRuleResponseTypeDef = TypedDict(
    "CreateRuleResponseTypeDef",
    {
        "RuleArn": str,
        "RuleId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateSecurityProfileResponseTypeDef = TypedDict(
    "CreateSecurityProfileResponseTypeDef",
    {
        "SecurityProfileId": str,
        "SecurityProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTaskTemplateResponseTypeDef = TypedDict(
    "CreateTaskTemplateResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTrafficDistributionGroupResponseTypeDef = TypedDict(
    "CreateTrafficDistributionGroupResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateUseCaseResponseTypeDef = TypedDict(
    "CreateUseCaseResponseTypeDef",
    {
        "UseCaseId": str,
        "UseCaseArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateUserHierarchyGroupResponseTypeDef = TypedDict(
    "CreateUserHierarchyGroupResponseTypeDef",
    {
        "HierarchyGroupId": str,
        "HierarchyGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateUserResponseTypeDef = TypedDict(
    "CreateUserResponseTypeDef",
    {
        "UserId": str,
        "UserArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateVocabularyResponseTypeDef = TypedDict(
    "CreateVocabularyResponseTypeDef",
    {
        "VocabularyArn": str,
        "VocabularyId": str,
        "State": VocabularyStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeactivateEvaluationFormResponseTypeDef = TypedDict(
    "DeactivateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "EvaluationFormVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteVocabularyResponseTypeDef = TypedDict(
    "DeleteVocabularyResponseTypeDef",
    {
        "VocabularyArn": str,
        "VocabularyId": str,
        "State": VocabularyStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetContactAttributesResponseTypeDef = TypedDict(
    "GetContactAttributesResponseTypeDef",
    {
        "Attributes": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetFlowAssociationResponseTypeDef = TypedDict(
    "GetFlowAssociationResponseTypeDef",
    {
        "ResourceId": str,
        "FlowId": str,
        "ResourceType": Literal["SMS_PHONE_NUMBER"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPromptFileResponseTypeDef = TypedDict(
    "GetPromptFileResponseTypeDef",
    {
        "PromptPresignedUrl": str,
        "LastModifiedTime": datetime,
        "LastModifiedRegion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportPhoneNumberResponseTypeDef = TypedDict(
    "ImportPhoneNumberResponseTypeDef",
    {
        "PhoneNumberId": str,
        "PhoneNumberArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListApprovedOriginsResponseTypeDef = TypedDict(
    "ListApprovedOriginsResponseTypeDef",
    {
        "Origins": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListLambdaFunctionsResponseTypeDef = TypedDict(
    "ListLambdaFunctionsResponseTypeDef",
    {
        "LambdaFunctions": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListSecurityProfilePermissionsResponseTypeDef = TypedDict(
    "ListSecurityProfilePermissionsResponseTypeDef",
    {
        "Permissions": List[str],
        "LastModifiedTime": datetime,
        "LastModifiedRegion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MonitorContactResponseTypeDef = TypedDict(
    "MonitorContactResponseTypeDef",
    {
        "ContactId": str,
        "ContactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ReplicateInstanceResponseTypeDef = TypedDict(
    "ReplicateInstanceResponseTypeDef",
    {
        "Id": str,
        "Arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SendChatIntegrationEventResponseTypeDef = TypedDict(
    "SendChatIntegrationEventResponseTypeDef",
    {
        "InitialContactId": str,
        "NewChatCreated": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartChatContactResponseTypeDef = TypedDict(
    "StartChatContactResponseTypeDef",
    {
        "ContactId": str,
        "ParticipantId": str,
        "ParticipantToken": str,
        "ContinuedFromContactId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartContactEvaluationResponseTypeDef = TypedDict(
    "StartContactEvaluationResponseTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartContactStreamingResponseTypeDef = TypedDict(
    "StartContactStreamingResponseTypeDef",
    {
        "StreamingId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartOutboundVoiceContactResponseTypeDef = TypedDict(
    "StartOutboundVoiceContactResponseTypeDef",
    {
        "ContactId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTaskContactResponseTypeDef = TypedDict(
    "StartTaskContactResponseTypeDef",
    {
        "ContactId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SubmitContactEvaluationResponseTypeDef = TypedDict(
    "SubmitContactEvaluationResponseTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TransferContactResponseTypeDef = TypedDict(
    "TransferContactResponseTypeDef",
    {
        "ContactId": str,
        "ContactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateContactEvaluationResponseTypeDef = TypedDict(
    "UpdateContactEvaluationResponseTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEvaluationFormResponseTypeDef = TypedDict(
    "UpdateEvaluationFormResponseTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "EvaluationFormVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePhoneNumberResponseTypeDef = TypedDict(
    "UpdatePhoneNumberResponseTypeDef",
    {
        "PhoneNumberId": str,
        "PhoneNumberArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePromptResponseTypeDef = TypedDict(
    "UpdatePromptResponseTypeDef",
    {
        "PromptARN": str,
        "PromptId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AgentConfigOutputTypeDef = TypedDict(
    "AgentConfigOutputTypeDef",
    {
        "Distributions": List[DistributionTypeDef],
    },
)
AgentConfigTypeDef = TypedDict(
    "AgentConfigTypeDef",
    {
        "Distributions": Sequence[DistributionTypeDef],
    },
)
TelephonyConfigOutputTypeDef = TypedDict(
    "TelephonyConfigOutputTypeDef",
    {
        "Distributions": List[DistributionTypeDef],
    },
)
TelephonyConfigTypeDef = TypedDict(
    "TelephonyConfigTypeDef",
    {
        "Distributions": Sequence[DistributionTypeDef],
    },
)
AgentContactReferenceTypeDef = TypedDict(
    "AgentContactReferenceTypeDef",
    {
        "ContactId": NotRequired[str],
        "Channel": NotRequired[ChannelType],
        "InitiationMethod": NotRequired[ContactInitiationMethodType],
        "AgentContactState": NotRequired[ContactStateType],
        "StateStartTimestamp": NotRequired[datetime],
        "ConnectedToAgentTimestamp": NotRequired[datetime],
        "Queue": NotRequired[QueueReferenceTypeDef],
    },
)
HierarchyGroupsTypeDef = TypedDict(
    "HierarchyGroupsTypeDef",
    {
        "Level1": NotRequired[AgentHierarchyGroupTypeDef],
        "Level2": NotRequired[AgentHierarchyGroupTypeDef],
        "Level3": NotRequired[AgentHierarchyGroupTypeDef],
        "Level4": NotRequired[AgentHierarchyGroupTypeDef],
        "Level5": NotRequired[AgentHierarchyGroupTypeDef],
    },
)
AllowedCapabilitiesTypeDef = TypedDict(
    "AllowedCapabilitiesTypeDef",
    {
        "Customer": NotRequired[ParticipantCapabilitiesTypeDef],
        "Agent": NotRequired[ParticipantCapabilitiesTypeDef],
    },
)
CustomerTypeDef = TypedDict(
    "CustomerTypeDef",
    {
        "DeviceInfo": NotRequired[DeviceInfoTypeDef],
        "Capabilities": NotRequired[ParticipantCapabilitiesTypeDef],
    },
)
AgentQualityMetricsTypeDef = TypedDict(
    "AgentQualityMetricsTypeDef",
    {
        "Audio": NotRequired[AudioQualityMetricsInfoTypeDef],
    },
)
CustomerQualityMetricsTypeDef = TypedDict(
    "CustomerQualityMetricsTypeDef",
    {
        "Audio": NotRequired[AudioQualityMetricsInfoTypeDef],
    },
)
AgentStatusSearchCriteriaTypeDef = TypedDict(
    "AgentStatusSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
ContactFlowModuleSearchCriteriaTypeDef = TypedDict(
    "ContactFlowModuleSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
ContactFlowSearchCriteriaTypeDef = TypedDict(
    "ContactFlowSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
        "TypeCondition": NotRequired[ContactFlowTypeType],
        "StateCondition": NotRequired[ContactFlowStateType],
        "StatusCondition": NotRequired[ContactFlowStatusType],
    },
)
HoursOfOperationSearchCriteriaTypeDef = TypedDict(
    "HoursOfOperationSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
PredefinedAttributeSearchCriteriaTypeDef = TypedDict(
    "PredefinedAttributeSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
PromptSearchCriteriaTypeDef = TypedDict(
    "PromptSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
QueueSearchCriteriaTypeDef = TypedDict(
    "QueueSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
        "QueueTypeCondition": NotRequired[Literal["STANDARD"]],
    },
)
QuickConnectSearchCriteriaTypeDef = TypedDict(
    "QuickConnectSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
RoutingProfileSearchCriteriaTypeDef = TypedDict(
    "RoutingProfileSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
SecurityProfileSearchCriteriaTypeDef = TypedDict(
    "SecurityProfileSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
UserHierarchyGroupSearchCriteriaTypeDef = TypedDict(
    "UserHierarchyGroupSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
    },
)
ListAgentStatusResponseTypeDef = TypedDict(
    "ListAgentStatusResponseTypeDef",
    {
        "AgentStatusSummaryList": List[AgentStatusSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeAgentStatusResponseTypeDef = TypedDict(
    "DescribeAgentStatusResponseTypeDef",
    {
        "AgentStatus": AgentStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchAgentStatusesResponseTypeDef = TypedDict(
    "SearchAgentStatusesResponseTypeDef",
    {
        "AgentStatuses": List[AgentStatusTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
MatchCriteriaTypeDef = TypedDict(
    "MatchCriteriaTypeDef",
    {
        "AgentsCriteria": NotRequired[AgentsCriteriaTypeDef],
    },
)
ListAnalyticsDataAssociationsResponseTypeDef = TypedDict(
    "ListAnalyticsDataAssociationsResponseTypeDef",
    {
        "Results": List[AnalyticsDataAssociationResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListSecurityProfileApplicationsResponseTypeDef = TypedDict(
    "ListSecurityProfileApplicationsResponseTypeDef",
    {
        "Applications": List[ApplicationExtraOutputTypeDef],
        "LastModifiedTime": datetime,
        "LastModifiedRegion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ApplicationUnionTypeDef = Union[ApplicationTypeDef, ApplicationExtraOutputTypeDef]
AssociateLexBotRequestRequestTypeDef = TypedDict(
    "AssociateLexBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexBot": LexBotTypeDef,
    },
)
ListLexBotsResponseTypeDef = TypedDict(
    "ListLexBotsResponseTypeDef",
    {
        "LexBots": List[LexBotTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
AssociateBotRequestRequestTypeDef = TypedDict(
    "AssociateBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexBot": NotRequired[LexBotTypeDef],
        "LexV2Bot": NotRequired[LexV2BotTypeDef],
    },
)
DisassociateBotRequestRequestTypeDef = TypedDict(
    "DisassociateBotRequestRequestTypeDef",
    {
        "InstanceId": str,
        "LexBot": NotRequired[LexBotTypeDef],
        "LexV2Bot": NotRequired[LexV2BotTypeDef],
    },
)
LexBotConfigTypeDef = TypedDict(
    "LexBotConfigTypeDef",
    {
        "LexBot": NotRequired[LexBotTypeDef],
        "LexV2Bot": NotRequired[LexV2BotTypeDef],
    },
)
AssociateUserProficienciesRequestRequestTypeDef = TypedDict(
    "AssociateUserProficienciesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "UserId": str,
        "UserProficiencies": Sequence[UserProficiencyTypeDef],
    },
)
ListUserProficienciesResponseTypeDef = TypedDict(
    "ListUserProficienciesResponseTypeDef",
    {
        "UserProficiencyList": List[UserProficiencyTypeDef],
        "LastModifiedTime": datetime,
        "LastModifiedRegion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateUserProficienciesRequestRequestTypeDef = TypedDict(
    "UpdateUserProficienciesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "UserId": str,
        "UserProficiencies": Sequence[UserProficiencyTypeDef],
    },
)
AttachedFileTypeDef = TypedDict(
    "AttachedFileTypeDef",
    {
        "CreationTime": str,
        "FileArn": str,
        "FileId": str,
        "FileName": str,
        "FileSizeInBytes": int,
        "FileStatus": FileStatusTypeType,
        "CreatedBy": NotRequired[CreatedByInfoTypeDef],
        "FileUseCaseType": NotRequired[Literal["ATTACHMENT"]],
        "AssociatedResourceArn": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)
StartAttachedFileUploadRequestRequestTypeDef = TypedDict(
    "StartAttachedFileUploadRequestRequestTypeDef",
    {
        "InstanceId": str,
        "FileName": str,
        "FileSizeInBytes": int,
        "FileUseCaseType": Literal["ATTACHMENT"],
        "AssociatedResourceArn": str,
        "ClientToken": NotRequired[str],
        "UrlExpiryInSeconds": NotRequired[int],
        "CreatedBy": NotRequired[CreatedByInfoTypeDef],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
AttributeAndConditionTypeDef = TypedDict(
    "AttributeAndConditionTypeDef",
    {
        "TagConditions": NotRequired[Sequence[TagConditionTypeDef]],
        "HierarchyGroupCondition": NotRequired[HierarchyGroupConditionTypeDef],
    },
)
CommonAttributeAndConditionTypeDef = TypedDict(
    "CommonAttributeAndConditionTypeDef",
    {
        "TagConditions": NotRequired[Sequence[TagConditionTypeDef]],
    },
)
ControlPlaneTagFilterTypeDef = TypedDict(
    "ControlPlaneTagFilterTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Sequence[TagConditionTypeDef]]],
        "AndConditions": NotRequired[Sequence[TagConditionTypeDef]],
        "TagCondition": NotRequired[TagConditionTypeDef],
    },
)
DescribeInstanceAttributeResponseTypeDef = TypedDict(
    "DescribeInstanceAttributeResponseTypeDef",
    {
        "Attribute": AttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListInstanceAttributesResponseTypeDef = TypedDict(
    "ListInstanceAttributesResponseTypeDef",
    {
        "Attributes": List[AttributeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
MeetingFeaturesConfigurationTypeDef = TypedDict(
    "MeetingFeaturesConfigurationTypeDef",
    {
        "Audio": NotRequired[AudioFeaturesTypeDef],
    },
)
ListAuthenticationProfilesResponseTypeDef = TypedDict(
    "ListAuthenticationProfilesResponseTypeDef",
    {
        "AuthenticationProfileSummaryList": List[AuthenticationProfileSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeAuthenticationProfileResponseTypeDef = TypedDict(
    "DescribeAuthenticationProfileResponseTypeDef",
    {
        "AuthenticationProfile": AuthenticationProfileTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchAvailablePhoneNumbersResponseTypeDef = TypedDict(
    "SearchAvailablePhoneNumbersResponseTypeDef",
    {
        "AvailableNumbersList": List[AvailableNumberSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
BatchAssociateAnalyticsDataSetResponseTypeDef = TypedDict(
    "BatchAssociateAnalyticsDataSetResponseTypeDef",
    {
        "Created": List[AnalyticsDataAssociationResultTypeDef],
        "Errors": List[ErrorResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchDisassociateAnalyticsDataSetResponseTypeDef = TypedDict(
    "BatchDisassociateAnalyticsDataSetResponseTypeDef",
    {
        "Deleted": List[str],
        "Errors": List[ErrorResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetFlowAssociationResponseTypeDef = TypedDict(
    "BatchGetFlowAssociationResponseTypeDef",
    {
        "FlowAssociationSummaryList": List[FlowAssociationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListFlowAssociationsResponseTypeDef = TypedDict(
    "ListFlowAssociationsResponseTypeDef",
    {
        "FlowAssociationSummaryList": List[FlowAssociationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
BatchPutContactResponseTypeDef = TypedDict(
    "BatchPutContactResponseTypeDef",
    {
        "SuccessfulRequestList": List[SuccessfulRequestTypeDef],
        "FailedRequestList": List[FailedRequestTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartContactStreamingRequestRequestTypeDef = TypedDict(
    "StartContactStreamingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ChatStreamingConfiguration": ChatStreamingConfigurationTypeDef,
        "ClientToken": str,
    },
)
ClaimedPhoneNumberSummaryTypeDef = TypedDict(
    "ClaimedPhoneNumberSummaryTypeDef",
    {
        "PhoneNumberId": NotRequired[str],
        "PhoneNumberArn": NotRequired[str],
        "PhoneNumber": NotRequired[str],
        "PhoneNumberCountryCode": NotRequired[PhoneNumberCountryCodeType],
        "PhoneNumberType": NotRequired[PhoneNumberTypeType],
        "PhoneNumberDescription": NotRequired[str],
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "PhoneNumberStatus": NotRequired[PhoneNumberStatusTypeDef],
        "SourcePhoneNumberArn": NotRequired[str],
    },
)
ConditionTypeDef = TypedDict(
    "ConditionTypeDef",
    {
        "StringCondition": NotRequired[StringConditionTypeDef],
        "NumberCondition": NotRequired[NumberConditionTypeDef],
    },
)
ContactDataRequestTypeDef = TypedDict(
    "ContactDataRequestTypeDef",
    {
        "SystemEndpoint": NotRequired[EndpointTypeDef],
        "CustomerEndpoint": NotRequired[EndpointTypeDef],
        "RequestIdentifier": NotRequired[str],
        "QueueId": NotRequired[str],
        "Attributes": NotRequired[Mapping[str, str]],
        "Campaign": NotRequired[CampaignTypeDef],
    },
)
UserDataFiltersTypeDef = TypedDict(
    "UserDataFiltersTypeDef",
    {
        "Queues": NotRequired[Sequence[str]],
        "ContactFilter": NotRequired[ContactFilterTypeDef],
        "RoutingProfiles": NotRequired[Sequence[str]],
        "Agents": NotRequired[Sequence[str]],
        "UserHierarchyGroups": NotRequired[Sequence[str]],
    },
)
ListContactFlowModulesResponseTypeDef = TypedDict(
    "ListContactFlowModulesResponseTypeDef",
    {
        "ContactFlowModulesSummaryList": List[ContactFlowModuleSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeContactFlowModuleResponseTypeDef = TypedDict(
    "DescribeContactFlowModuleResponseTypeDef",
    {
        "ContactFlowModule": ContactFlowModuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchContactFlowModulesResponseTypeDef = TypedDict(
    "SearchContactFlowModulesResponseTypeDef",
    {
        "ContactFlowModules": List[ContactFlowModuleTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListContactFlowsResponseTypeDef = TypedDict(
    "ListContactFlowsResponseTypeDef",
    {
        "ContactFlowSummaryList": List[ContactFlowSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeContactFlowResponseTypeDef = TypedDict(
    "DescribeContactFlowResponseTypeDef",
    {
        "ContactFlow": ContactFlowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchContactFlowsResponseTypeDef = TypedDict(
    "SearchContactFlowsResponseTypeDef",
    {
        "ContactFlows": List[ContactFlowTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ContactSearchSummaryTypeDef = TypedDict(
    "ContactSearchSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "InitialContactId": NotRequired[str],
        "PreviousContactId": NotRequired[str],
        "InitiationMethod": NotRequired[ContactInitiationMethodType],
        "Channel": NotRequired[ChannelType],
        "QueueInfo": NotRequired[ContactSearchSummaryQueueInfoTypeDef],
        "AgentInfo": NotRequired[ContactSearchSummaryAgentInfoTypeDef],
        "InitiationTimestamp": NotRequired[datetime],
        "DisconnectTimestamp": NotRequired[datetime],
        "ScheduledTimestamp": NotRequired[datetime],
    },
)
CreateEvaluationFormRequestRequestTypeDef = TypedDict(
    "CreateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Title": str,
        "Items": Sequence[EvaluationFormItemUnionTypeDef],
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
        "ClientToken": NotRequired[str],
    },
)
EvaluationFormContentTypeDef = TypedDict(
    "EvaluationFormContentTypeDef",
    {
        "EvaluationFormVersion": int,
        "EvaluationFormId": str,
        "EvaluationFormArn": str,
        "Title": str,
        "Items": List["EvaluationFormItemOutputTypeDef"],
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
    },
)
EvaluationFormTypeDef = TypedDict(
    "EvaluationFormTypeDef",
    {
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
        "Locked": bool,
        "EvaluationFormArn": str,
        "Title": str,
        "Status": EvaluationFormVersionStatusType,
        "Items": List["EvaluationFormItemOutputTypeDef"],
        "CreatedTime": datetime,
        "CreatedBy": str,
        "LastModifiedTime": datetime,
        "LastModifiedBy": str,
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
        "Tags": NotRequired[Dict[str, str]],
    },
)
UpdateEvaluationFormRequestRequestTypeDef = TypedDict(
    "UpdateEvaluationFormRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "EvaluationFormVersion": int,
        "Title": str,
        "Items": Sequence[EvaluationFormItemUnionTypeDef],
        "CreateNewVersion": NotRequired[bool],
        "Description": NotRequired[str],
        "ScoringStrategy": NotRequired[EvaluationFormScoringStrategyTypeDef],
        "ClientToken": NotRequired[str],
    },
)
CreateParticipantRequestRequestTypeDef = TypedDict(
    "CreateParticipantRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ParticipantDetails": ParticipantDetailsToAddTypeDef,
        "ClientToken": NotRequired[str],
    },
)
CreateParticipantResponseTypeDef = TypedDict(
    "CreateParticipantResponseTypeDef",
    {
        "ParticipantCredentials": ParticipantTokenCredentialsTypeDef,
        "ParticipantId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePredefinedAttributeRequestRequestTypeDef = TypedDict(
    "CreatePredefinedAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Values": PredefinedAttributeValuesTypeDef,
    },
)
UpdatePredefinedAttributeRequestRequestTypeDef = TypedDict(
    "UpdatePredefinedAttributeRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Values": NotRequired[PredefinedAttributeValuesTypeDef],
    },
)
CreateQueueRequestRequestTypeDef = TypedDict(
    "CreateQueueRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "HoursOfOperationId": str,
        "Description": NotRequired[str],
        "OutboundCallerConfig": NotRequired[OutboundCallerConfigTypeDef],
        "MaxContacts": NotRequired[int],
        "QuickConnectIds": NotRequired[Sequence[str]],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
QueueTypeDef = TypedDict(
    "QueueTypeDef",
    {
        "Name": NotRequired[str],
        "QueueArn": NotRequired[str],
        "QueueId": NotRequired[str],
        "Description": NotRequired[str],
        "OutboundCallerConfig": NotRequired[OutboundCallerConfigTypeDef],
        "HoursOfOperationId": NotRequired[str],
        "MaxContacts": NotRequired[int],
        "Status": NotRequired[QueueStatusType],
        "Tags": NotRequired[Dict[str, str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
UpdateQueueOutboundCallerConfigRequestRequestTypeDef = TypedDict(
    "UpdateQueueOutboundCallerConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "OutboundCallerConfig": OutboundCallerConfigTypeDef,
    },
)
UpdateUserIdentityInfoRequestRequestTypeDef = TypedDict(
    "UpdateUserIdentityInfoRequestRequestTypeDef",
    {
        "IdentityInfo": UserIdentityInfoTypeDef,
        "UserId": str,
        "InstanceId": str,
    },
)
CreateUserRequestRequestTypeDef = TypedDict(
    "CreateUserRequestRequestTypeDef",
    {
        "Username": str,
        "PhoneConfig": UserPhoneConfigTypeDef,
        "SecurityProfileIds": Sequence[str],
        "RoutingProfileId": str,
        "InstanceId": str,
        "Password": NotRequired[str],
        "IdentityInfo": NotRequired[UserIdentityInfoTypeDef],
        "DirectoryUserId": NotRequired[str],
        "HierarchyGroupId": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
UpdateUserPhoneConfigRequestRequestTypeDef = TypedDict(
    "UpdateUserPhoneConfigRequestRequestTypeDef",
    {
        "PhoneConfig": UserPhoneConfigTypeDef,
        "UserId": str,
        "InstanceId": str,
    },
)
UserTypeDef = TypedDict(
    "UserTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Username": NotRequired[str],
        "IdentityInfo": NotRequired[UserIdentityInfoTypeDef],
        "PhoneConfig": NotRequired[UserPhoneConfigTypeDef],
        "DirectoryUserId": NotRequired[str],
        "SecurityProfileIds": NotRequired[List[str]],
        "RoutingProfileId": NotRequired[str],
        "HierarchyGroupId": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
CreateViewRequestRequestTypeDef = TypedDict(
    "CreateViewRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Status": ViewStatusType,
        "Content": ViewInputContentTypeDef,
        "Name": str,
        "ClientToken": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
UpdateViewContentRequestRequestTypeDef = TypedDict(
    "UpdateViewContentRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "Status": ViewStatusType,
        "Content": ViewInputContentTypeDef,
    },
)
GetFederationTokenResponseTypeDef = TypedDict(
    "GetFederationTokenResponseTypeDef",
    {
        "Credentials": CredentialsTypeDef,
        "SignInUrl": str,
        "UserArn": str,
        "UserId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MediaConcurrencyTypeDef = TypedDict(
    "MediaConcurrencyTypeDef",
    {
        "Channel": ChannelType,
        "Concurrency": int,
        "CrossChannelBehavior": NotRequired[CrossChannelBehaviorTypeDef],
    },
)
CurrentMetricDataTypeDef = TypedDict(
    "CurrentMetricDataTypeDef",
    {
        "Metric": NotRequired[CurrentMetricTypeDef],
        "Value": NotRequired[float],
    },
)
ListDefaultVocabulariesResponseTypeDef = TypedDict(
    "ListDefaultVocabulariesResponseTypeDef",
    {
        "DefaultVocabularyList": List[DefaultVocabularyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribePromptResponseTypeDef = TypedDict(
    "DescribePromptResponseTypeDef",
    {
        "Prompt": PromptTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchPromptsResponseTypeDef = TypedDict(
    "SearchPromptsResponseTypeDef",
    {
        "Prompts": List[PromptTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeSecurityProfileResponseTypeDef = TypedDict(
    "DescribeSecurityProfileResponseTypeDef",
    {
        "SecurityProfile": SecurityProfileTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeTrafficDistributionGroupResponseTypeDef = TypedDict(
    "DescribeTrafficDistributionGroupResponseTypeDef",
    {
        "TrafficDistributionGroup": TrafficDistributionGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeVocabularyResponseTypeDef = TypedDict(
    "DescribeVocabularyResponseTypeDef",
    {
        "Vocabulary": VocabularyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DimensionsTypeDef = TypedDict(
    "DimensionsTypeDef",
    {
        "Queue": NotRequired[QueueReferenceTypeDef],
        "Channel": NotRequired[ChannelType],
        "RoutingProfile": NotRequired[RoutingProfileReferenceTypeDef],
        "RoutingStepExpression": NotRequired[str],
    },
)
DisassociateRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "DisassociateRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "QueueReferences": Sequence[RoutingProfileQueueReferenceTypeDef],
    },
)
RoutingProfileQueueConfigTypeDef = TypedDict(
    "RoutingProfileQueueConfigTypeDef",
    {
        "QueueReference": RoutingProfileQueueReferenceTypeDef,
        "Priority": int,
        "Delay": int,
    },
)
DisassociateUserProficienciesRequestRequestTypeDef = TypedDict(
    "DisassociateUserProficienciesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "UserId": str,
        "UserProficiencies": Sequence[UserProficiencyDisassociateTypeDef],
    },
)
StopContactRequestRequestTypeDef = TypedDict(
    "StopContactRequestRequestTypeDef",
    {
        "ContactId": str,
        "InstanceId": str,
        "DisconnectReason": NotRequired[DisconnectReasonTypeDef],
    },
)
GetAttachedFileResponseTypeDef = TypedDict(
    "GetAttachedFileResponseTypeDef",
    {
        "FileArn": str,
        "FileId": str,
        "CreationTime": str,
        "FileStatus": FileStatusTypeType,
        "FileName": str,
        "FileSizeInBytes": int,
        "AssociatedResourceArn": str,
        "FileUseCaseType": Literal["ATTACHMENT"],
        "CreatedBy": CreatedByInfoTypeDef,
        "DownloadUrlMetadata": DownloadUrlMetadataTypeDef,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
KinesisVideoStreamConfigTypeDef = TypedDict(
    "KinesisVideoStreamConfigTypeDef",
    {
        "Prefix": str,
        "RetentionPeriodHours": int,
        "EncryptionConfig": EncryptionConfigTypeDef,
    },
)
S3ConfigTypeDef = TypedDict(
    "S3ConfigTypeDef",
    {
        "BucketName": str,
        "BucketPrefix": str,
        "EncryptionConfig": NotRequired[EncryptionConfigTypeDef],
    },
)
EvaluationAnswerInputTypeDef = TypedDict(
    "EvaluationAnswerInputTypeDef",
    {
        "Value": NotRequired[EvaluationAnswerDataTypeDef],
    },
)
EvaluationAnswerOutputTypeDef = TypedDict(
    "EvaluationAnswerOutputTypeDef",
    {
        "Value": NotRequired[EvaluationAnswerDataTypeDef],
        "SystemSuggestedValue": NotRequired[EvaluationAnswerDataTypeDef],
    },
)
EvaluationFormNumericQuestionAutomationTypeDef = TypedDict(
    "EvaluationFormNumericQuestionAutomationTypeDef",
    {
        "PropertyValue": NotRequired[NumericQuestionPropertyValueAutomationTypeDef],
    },
)
EvaluationFormSingleSelectQuestionAutomationOptionTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionAutomationOptionTypeDef",
    {
        "RuleCategory": NotRequired[SingleSelectQuestionRuleCategoryAutomationTypeDef],
    },
)
ListEvaluationFormsResponseTypeDef = TypedDict(
    "ListEvaluationFormsResponseTypeDef",
    {
        "EvaluationFormSummaryList": List[EvaluationFormSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListEvaluationFormVersionsResponseTypeDef = TypedDict(
    "ListEvaluationFormVersionsResponseTypeDef",
    {
        "EvaluationFormVersionSummaryList": List[EvaluationFormVersionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
EvaluationMetadataTypeDef = TypedDict(
    "EvaluationMetadataTypeDef",
    {
        "ContactId": str,
        "EvaluatorArn": str,
        "ContactAgentId": NotRequired[str],
        "Score": NotRequired[EvaluationScoreTypeDef],
    },
)
EvaluationSummaryTypeDef = TypedDict(
    "EvaluationSummaryTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "EvaluationFormTitle": str,
        "EvaluationFormId": str,
        "Status": EvaluationStatusType,
        "EvaluatorArn": str,
        "CreatedTime": datetime,
        "LastModifiedTime": datetime,
        "Score": NotRequired[EvaluationScoreTypeDef],
    },
)
StepTypeDef = TypedDict(
    "StepTypeDef",
    {
        "Expiry": NotRequired[ExpiryTypeDef],
        "Expression": NotRequired["ExpressionTypeDef"],
        "Status": NotRequired[RoutingCriteriaStepStatusType],
    },
)
FieldValueOutputTypeDef = TypedDict(
    "FieldValueOutputTypeDef",
    {
        "Id": str,
        "Value": FieldValueUnionOutputTypeDef,
    },
)
FieldValueTypeDef = TypedDict(
    "FieldValueTypeDef",
    {
        "Id": str,
        "Value": FieldValueUnionTypeDef,
    },
)
GetCurrentMetricDataRequestRequestTypeDef = TypedDict(
    "GetCurrentMetricDataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Filters": FiltersTypeDef,
        "CurrentMetrics": Sequence[CurrentMetricTypeDef],
        "Groupings": NotRequired[Sequence[GroupingType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortCriteria": NotRequired[Sequence[CurrentMetricSortCriteriaTypeDef]],
    },
)
ListAgentStatusRequestListAgentStatusesPaginateTypeDef = TypedDict(
    "ListAgentStatusRequestListAgentStatusesPaginateTypeDef",
    {
        "InstanceId": str,
        "AgentStatusTypes": NotRequired[Sequence[AgentStatusTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListApprovedOriginsRequestListApprovedOriginsPaginateTypeDef = TypedDict(
    "ListApprovedOriginsRequestListApprovedOriginsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAuthenticationProfilesRequestListAuthenticationProfilesPaginateTypeDef = TypedDict(
    "ListAuthenticationProfilesRequestListAuthenticationProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListBotsRequestListBotsPaginateTypeDef = TypedDict(
    "ListBotsRequestListBotsPaginateTypeDef",
    {
        "InstanceId": str,
        "LexVersion": LexVersionType,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListContactEvaluationsRequestListContactEvaluationsPaginateTypeDef = TypedDict(
    "ListContactEvaluationsRequestListContactEvaluationsPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListContactFlowModulesRequestListContactFlowModulesPaginateTypeDef = TypedDict(
    "ListContactFlowModulesRequestListContactFlowModulesPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactFlowModuleState": NotRequired[ContactFlowModuleStateType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListContactFlowsRequestListContactFlowsPaginateTypeDef = TypedDict(
    "ListContactFlowsRequestListContactFlowsPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactFlowTypes": NotRequired[Sequence[ContactFlowTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListContactReferencesRequestListContactReferencesPaginateTypeDef = TypedDict(
    "ListContactReferencesRequestListContactReferencesPaginateTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ReferenceTypes": Sequence[ReferenceTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDefaultVocabulariesRequestListDefaultVocabulariesPaginateTypeDef = TypedDict(
    "ListDefaultVocabulariesRequestListDefaultVocabulariesPaginateTypeDef",
    {
        "InstanceId": str,
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEvaluationFormVersionsRequestListEvaluationFormVersionsPaginateTypeDef = TypedDict(
    "ListEvaluationFormVersionsRequestListEvaluationFormVersionsPaginateTypeDef",
    {
        "InstanceId": str,
        "EvaluationFormId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEvaluationFormsRequestListEvaluationFormsPaginateTypeDef = TypedDict(
    "ListEvaluationFormsRequestListEvaluationFormsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListFlowAssociationsRequestListFlowAssociationsPaginateTypeDef = TypedDict(
    "ListFlowAssociationsRequestListFlowAssociationsPaginateTypeDef",
    {
        "InstanceId": str,
        "ResourceType": NotRequired[Literal["VOICE_PHONE_NUMBER"]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListHoursOfOperationsRequestListHoursOfOperationsPaginateTypeDef = TypedDict(
    "ListHoursOfOperationsRequestListHoursOfOperationsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInstanceAttributesRequestListInstanceAttributesPaginateTypeDef = TypedDict(
    "ListInstanceAttributesRequestListInstanceAttributesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInstanceStorageConfigsRequestListInstanceStorageConfigsPaginateTypeDef = TypedDict(
    "ListInstanceStorageConfigsRequestListInstanceStorageConfigsPaginateTypeDef",
    {
        "InstanceId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInstancesRequestListInstancesPaginateTypeDef = TypedDict(
    "ListInstancesRequestListInstancesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListIntegrationAssociationsRequestListIntegrationAssociationsPaginateTypeDef = TypedDict(
    "ListIntegrationAssociationsRequestListIntegrationAssociationsPaginateTypeDef",
    {
        "InstanceId": str,
        "IntegrationType": NotRequired[IntegrationTypeType],
        "IntegrationArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListLambdaFunctionsRequestListLambdaFunctionsPaginateTypeDef = TypedDict(
    "ListLambdaFunctionsRequestListLambdaFunctionsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListLexBotsRequestListLexBotsPaginateTypeDef = TypedDict(
    "ListLexBotsRequestListLexBotsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPhoneNumbersRequestListPhoneNumbersPaginateTypeDef = TypedDict(
    "ListPhoneNumbersRequestListPhoneNumbersPaginateTypeDef",
    {
        "InstanceId": str,
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPhoneNumbersV2RequestListPhoneNumbersV2PaginateTypeDef = TypedDict(
    "ListPhoneNumbersV2RequestListPhoneNumbersV2PaginateTypeDef",
    {
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "PhoneNumberCountryCodes": NotRequired[Sequence[PhoneNumberCountryCodeType]],
        "PhoneNumberTypes": NotRequired[Sequence[PhoneNumberTypeType]],
        "PhoneNumberPrefix": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPredefinedAttributesRequestListPredefinedAttributesPaginateTypeDef = TypedDict(
    "ListPredefinedAttributesRequestListPredefinedAttributesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPromptsRequestListPromptsPaginateTypeDef = TypedDict(
    "ListPromptsRequestListPromptsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListQueueQuickConnectsRequestListQueueQuickConnectsPaginateTypeDef = TypedDict(
    "ListQueueQuickConnectsRequestListQueueQuickConnectsPaginateTypeDef",
    {
        "InstanceId": str,
        "QueueId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListQueuesRequestListQueuesPaginateTypeDef = TypedDict(
    "ListQueuesRequestListQueuesPaginateTypeDef",
    {
        "InstanceId": str,
        "QueueTypes": NotRequired[Sequence[QueueTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListQuickConnectsRequestListQuickConnectsPaginateTypeDef = TypedDict(
    "ListQuickConnectsRequestListQuickConnectsPaginateTypeDef",
    {
        "InstanceId": str,
        "QuickConnectTypes": NotRequired[Sequence[QuickConnectTypeType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRoutingProfileQueuesRequestListRoutingProfileQueuesPaginateTypeDef = TypedDict(
    "ListRoutingProfileQueuesRequestListRoutingProfileQueuesPaginateTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRoutingProfilesRequestListRoutingProfilesPaginateTypeDef = TypedDict(
    "ListRoutingProfilesRequestListRoutingProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRulesRequestListRulesPaginateTypeDef = TypedDict(
    "ListRulesRequestListRulesPaginateTypeDef",
    {
        "InstanceId": str,
        "PublishStatus": NotRequired[RulePublishStatusType],
        "EventSourceName": NotRequired[EventSourceNameType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSecurityKeysRequestListSecurityKeysPaginateTypeDef = TypedDict(
    "ListSecurityKeysRequestListSecurityKeysPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSecurityProfileApplicationsRequestListSecurityProfileApplicationsPaginateTypeDef = TypedDict(
    "ListSecurityProfileApplicationsRequestListSecurityProfileApplicationsPaginateTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSecurityProfilePermissionsRequestListSecurityProfilePermissionsPaginateTypeDef = TypedDict(
    "ListSecurityProfilePermissionsRequestListSecurityProfilePermissionsPaginateTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef = TypedDict(
    "ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTaskTemplatesRequestListTaskTemplatesPaginateTypeDef = TypedDict(
    "ListTaskTemplatesRequestListTaskTemplatesPaginateTypeDef",
    {
        "InstanceId": str,
        "Status": NotRequired[TaskTemplateStatusType],
        "Name": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTrafficDistributionGroupUsersRequestListTrafficDistributionGroupUsersPaginateTypeDef = (
    TypedDict(
        "ListTrafficDistributionGroupUsersRequestListTrafficDistributionGroupUsersPaginateTypeDef",
        {
            "TrafficDistributionGroupId": str,
            "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
        },
    )
)
ListTrafficDistributionGroupsRequestListTrafficDistributionGroupsPaginateTypeDef = TypedDict(
    "ListTrafficDistributionGroupsRequestListTrafficDistributionGroupsPaginateTypeDef",
    {
        "InstanceId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListUseCasesRequestListUseCasesPaginateTypeDef = TypedDict(
    "ListUseCasesRequestListUseCasesPaginateTypeDef",
    {
        "InstanceId": str,
        "IntegrationAssociationId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListUserHierarchyGroupsRequestListUserHierarchyGroupsPaginateTypeDef = TypedDict(
    "ListUserHierarchyGroupsRequestListUserHierarchyGroupsPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListUserProficienciesRequestListUserProficienciesPaginateTypeDef = TypedDict(
    "ListUserProficienciesRequestListUserProficienciesPaginateTypeDef",
    {
        "InstanceId": str,
        "UserId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListUsersRequestListUsersPaginateTypeDef = TypedDict(
    "ListUsersRequestListUsersPaginateTypeDef",
    {
        "InstanceId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListViewVersionsRequestListViewVersionsPaginateTypeDef = TypedDict(
    "ListViewVersionsRequestListViewVersionsPaginateTypeDef",
    {
        "InstanceId": str,
        "ViewId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListViewsRequestListViewsPaginateTypeDef = TypedDict(
    "ListViewsRequestListViewsPaginateTypeDef",
    {
        "InstanceId": str,
        "Type": NotRequired[ViewTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchAvailablePhoneNumbersRequestSearchAvailablePhoneNumbersPaginateTypeDef = TypedDict(
    "SearchAvailablePhoneNumbersRequestSearchAvailablePhoneNumbersPaginateTypeDef",
    {
        "PhoneNumberCountryCode": PhoneNumberCountryCodeType,
        "PhoneNumberType": PhoneNumberTypeType,
        "TargetArn": NotRequired[str],
        "InstanceId": NotRequired[str],
        "PhoneNumberPrefix": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchVocabulariesRequestSearchVocabulariesPaginateTypeDef = TypedDict(
    "SearchVocabulariesRequestSearchVocabulariesPaginateTypeDef",
    {
        "InstanceId": str,
        "State": NotRequired[VocabularyStateType],
        "NameStartsWith": NotRequired[str],
        "LanguageCode": NotRequired[VocabularyLanguageCodeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchContactsTimeRangeTypeDef = TypedDict(
    "SearchContactsTimeRangeTypeDef",
    {
        "Type": SearchContactsTimeRangeTypeType,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
    },
)
UpdateContactScheduleRequestRequestTypeDef = TypedDict(
    "UpdateContactScheduleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ScheduledTime": TimestampTypeDef,
    },
)
HierarchyPathReferenceTypeDef = TypedDict(
    "HierarchyPathReferenceTypeDef",
    {
        "LevelOne": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelTwo": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelThree": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelFour": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
        "LevelFive": NotRequired[HierarchyGroupSummaryReferenceTypeDef],
    },
)
HierarchyPathTypeDef = TypedDict(
    "HierarchyPathTypeDef",
    {
        "LevelOne": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelTwo": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelThree": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelFour": NotRequired[HierarchyGroupSummaryTypeDef],
        "LevelFive": NotRequired[HierarchyGroupSummaryTypeDef],
    },
)
ListUserHierarchyGroupsResponseTypeDef = TypedDict(
    "ListUserHierarchyGroupsResponseTypeDef",
    {
        "UserHierarchyGroupSummaryList": List[HierarchyGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
HierarchyStructureTypeDef = TypedDict(
    "HierarchyStructureTypeDef",
    {
        "LevelOne": NotRequired[HierarchyLevelTypeDef],
        "LevelTwo": NotRequired[HierarchyLevelTypeDef],
        "LevelThree": NotRequired[HierarchyLevelTypeDef],
        "LevelFour": NotRequired[HierarchyLevelTypeDef],
        "LevelFive": NotRequired[HierarchyLevelTypeDef],
    },
)
HierarchyStructureUpdateTypeDef = TypedDict(
    "HierarchyStructureUpdateTypeDef",
    {
        "LevelOne": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelTwo": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelThree": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelFour": NotRequired[HierarchyLevelUpdateTypeDef],
        "LevelFive": NotRequired[HierarchyLevelUpdateTypeDef],
    },
)
HistoricalMetricTypeDef = TypedDict(
    "HistoricalMetricTypeDef",
    {
        "Name": NotRequired[HistoricalMetricNameType],
        "Threshold": NotRequired[ThresholdTypeDef],
        "Statistic": NotRequired[StatisticType],
        "Unit": NotRequired[UnitType],
    },
)
HoursOfOperationConfigTypeDef = TypedDict(
    "HoursOfOperationConfigTypeDef",
    {
        "Day": HoursOfOperationDaysType,
        "StartTime": HoursOfOperationTimeSliceTypeDef,
        "EndTime": HoursOfOperationTimeSliceTypeDef,
    },
)
ListHoursOfOperationsResponseTypeDef = TypedDict(
    "ListHoursOfOperationsResponseTypeDef",
    {
        "HoursOfOperationSummaryList": List[HoursOfOperationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
InstanceTypeDef = TypedDict(
    "InstanceTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "IdentityManagementType": NotRequired[DirectoryTypeType],
        "InstanceAlias": NotRequired[str],
        "CreatedTime": NotRequired[datetime],
        "ServiceRole": NotRequired[str],
        "InstanceStatus": NotRequired[InstanceStatusType],
        "StatusReason": NotRequired[InstanceStatusReasonTypeDef],
        "InboundCallsEnabled": NotRequired[bool],
        "OutboundCallsEnabled": NotRequired[bool],
        "InstanceAccessUrl": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
    },
)
ListInstancesResponseTypeDef = TypedDict(
    "ListInstancesResponseTypeDef",
    {
        "InstanceSummaryList": List[InstanceSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListIntegrationAssociationsResponseTypeDef = TypedDict(
    "ListIntegrationAssociationsResponseTypeDef",
    {
        "IntegrationAssociationSummaryList": List[IntegrationAssociationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
InvisibleFieldInfoTypeDef = TypedDict(
    "InvisibleFieldInfoTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
    },
)
ReadOnlyFieldInfoTypeDef = TypedDict(
    "ReadOnlyFieldInfoTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
    },
)
RequiredFieldInfoTypeDef = TypedDict(
    "RequiredFieldInfoTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
    },
)
TaskTemplateDefaultFieldValueTypeDef = TypedDict(
    "TaskTemplateDefaultFieldValueTypeDef",
    {
        "Id": NotRequired[TaskTemplateFieldIdentifierTypeDef],
        "DefaultValue": NotRequired[str],
    },
)
TaskTemplateFieldOutputTypeDef = TypedDict(
    "TaskTemplateFieldOutputTypeDef",
    {
        "Id": TaskTemplateFieldIdentifierTypeDef,
        "Description": NotRequired[str],
        "Type": NotRequired[TaskTemplateFieldTypeType],
        "SingleSelectOptions": NotRequired[List[str]],
    },
)
TaskTemplateFieldTypeDef = TypedDict(
    "TaskTemplateFieldTypeDef",
    {
        "Id": TaskTemplateFieldIdentifierTypeDef,
        "Description": NotRequired[str],
        "Type": NotRequired[TaskTemplateFieldTypeType],
        "SingleSelectOptions": NotRequired[Sequence[str]],
    },
)
ListPhoneNumbersResponseTypeDef = TypedDict(
    "ListPhoneNumbersResponseTypeDef",
    {
        "PhoneNumberSummaryList": List[PhoneNumberSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListPhoneNumbersV2ResponseTypeDef = TypedDict(
    "ListPhoneNumbersV2ResponseTypeDef",
    {
        "ListPhoneNumbersSummaryList": List[ListPhoneNumbersSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListPredefinedAttributesResponseTypeDef = TypedDict(
    "ListPredefinedAttributesResponseTypeDef",
    {
        "PredefinedAttributeSummaryList": List[PredefinedAttributeSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListPromptsResponseTypeDef = TypedDict(
    "ListPromptsResponseTypeDef",
    {
        "PromptSummaryList": List[PromptSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListQueueQuickConnectsResponseTypeDef = TypedDict(
    "ListQueueQuickConnectsResponseTypeDef",
    {
        "QuickConnectSummaryList": List[QuickConnectSummaryTypeDef],
        "LastModifiedTime": datetime,
        "LastModifiedRegion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListQuickConnectsResponseTypeDef = TypedDict(
    "ListQuickConnectsResponseTypeDef",
    {
        "QuickConnectSummaryList": List[QuickConnectSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListQueuesResponseTypeDef = TypedDict(
    "ListQueuesResponseTypeDef",
    {
        "QueueSummaryList": List[QueueSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListRoutingProfileQueuesResponseTypeDef = TypedDict(
    "ListRoutingProfileQueuesResponseTypeDef",
    {
        "RoutingProfileQueueConfigSummaryList": List[RoutingProfileQueueConfigSummaryTypeDef],
        "LastModifiedTime": datetime,
        "LastModifiedRegion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListRoutingProfilesResponseTypeDef = TypedDict(
    "ListRoutingProfilesResponseTypeDef",
    {
        "RoutingProfileSummaryList": List[RoutingProfileSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListSecurityKeysResponseTypeDef = TypedDict(
    "ListSecurityKeysResponseTypeDef",
    {
        "SecurityKeys": List[SecurityKeyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListSecurityProfilesResponseTypeDef = TypedDict(
    "ListSecurityProfilesResponseTypeDef",
    {
        "SecurityProfileSummaryList": List[SecurityProfileSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListTaskTemplatesResponseTypeDef = TypedDict(
    "ListTaskTemplatesResponseTypeDef",
    {
        "TaskTemplates": List[TaskTemplateMetadataTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListTrafficDistributionGroupUsersResponseTypeDef = TypedDict(
    "ListTrafficDistributionGroupUsersResponseTypeDef",
    {
        "TrafficDistributionGroupUserSummaryList": List[TrafficDistributionGroupUserSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListTrafficDistributionGroupsResponseTypeDef = TypedDict(
    "ListTrafficDistributionGroupsResponseTypeDef",
    {
        "TrafficDistributionGroupSummaryList": List[TrafficDistributionGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListUseCasesResponseTypeDef = TypedDict(
    "ListUseCasesResponseTypeDef",
    {
        "UseCaseSummaryList": List[UseCaseTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListUsersResponseTypeDef = TypedDict(
    "ListUsersResponseTypeDef",
    {
        "UserSummaryList": List[UserSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListViewVersionsResponseTypeDef = TypedDict(
    "ListViewVersionsResponseTypeDef",
    {
        "ViewVersionSummaryList": List[ViewVersionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListViewsResponseTypeDef = TypedDict(
    "ListViewsResponseTypeDef",
    {
        "ViewsSummaryList": List[ViewSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
MetricV2OutputTypeDef = TypedDict(
    "MetricV2OutputTypeDef",
    {
        "Name": NotRequired[str],
        "Threshold": NotRequired[List[ThresholdV2TypeDef]],
        "MetricFilters": NotRequired[List[MetricFilterV2OutputTypeDef]],
    },
)
MetricV2TypeDef = TypedDict(
    "MetricV2TypeDef",
    {
        "Name": NotRequired[str],
        "Threshold": NotRequired[Sequence[ThresholdV2TypeDef]],
        "MetricFilters": NotRequired[Sequence[MetricFilterV2TypeDef]],
    },
)
NewSessionDetailsTypeDef = TypedDict(
    "NewSessionDetailsTypeDef",
    {
        "SupportedMessagingContentTypes": NotRequired[Sequence[str]],
        "ParticipantDetails": NotRequired[ParticipantDetailsTypeDef],
        "Attributes": NotRequired[Mapping[str, str]],
        "StreamingConfiguration": NotRequired[ChatStreamingConfigurationTypeDef],
    },
)
SendNotificationActionDefinitionOutputTypeDef = TypedDict(
    "SendNotificationActionDefinitionOutputTypeDef",
    {
        "DeliveryMethod": Literal["EMAIL"],
        "Content": str,
        "ContentType": Literal["PLAIN_TEXT"],
        "Recipient": NotificationRecipientTypeOutputTypeDef,
        "Subject": NotRequired[str],
    },
)
SendNotificationActionDefinitionTypeDef = TypedDict(
    "SendNotificationActionDefinitionTypeDef",
    {
        "DeliveryMethod": Literal["EMAIL"],
        "Content": str,
        "ContentType": Literal["PLAIN_TEXT"],
        "Recipient": NotificationRecipientTypeTypeDef,
        "Subject": NotRequired[str],
    },
)
ParticipantTimerConfigurationTypeDef = TypedDict(
    "ParticipantTimerConfigurationTypeDef",
    {
        "ParticipantRole": TimerEligibleParticipantRolesType,
        "TimerType": ParticipantTimerTypeType,
        "TimerValue": ParticipantTimerValueTypeDef,
    },
)
StartChatContactRequestRequestTypeDef = TypedDict(
    "StartChatContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactFlowId": str,
        "ParticipantDetails": ParticipantDetailsTypeDef,
        "Attributes": NotRequired[Mapping[str, str]],
        "InitialMessage": NotRequired[ChatMessageTypeDef],
        "ClientToken": NotRequired[str],
        "ChatDurationInMinutes": NotRequired[int],
        "SupportedMessagingContentTypes": NotRequired[Sequence[str]],
        "PersistentChat": NotRequired[PersistentChatTypeDef],
        "RelatedContactId": NotRequired[str],
        "SegmentAttributes": NotRequired[Mapping[str, SegmentAttributeValueTypeDef]],
    },
)
PredefinedAttributeTypeDef = TypedDict(
    "PredefinedAttributeTypeDef",
    {
        "Name": NotRequired[str],
        "Values": NotRequired[PredefinedAttributeValuesOutputTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
PredefinedAttributeValuesUnionTypeDef = Union[
    PredefinedAttributeValuesTypeDef, PredefinedAttributeValuesExtraOutputTypeDef
]
QuickConnectConfigTypeDef = TypedDict(
    "QuickConnectConfigTypeDef",
    {
        "QuickConnectType": QuickConnectTypeType,
        "UserConfig": NotRequired[UserQuickConnectConfigTypeDef],
        "QueueConfig": NotRequired[QueueQuickConnectConfigTypeDef],
        "PhoneConfig": NotRequired[PhoneNumberQuickConnectConfigTypeDef],
    },
)
RealTimeContactAnalysisTranscriptItemRedactionTypeDef = TypedDict(
    "RealTimeContactAnalysisTranscriptItemRedactionTypeDef",
    {
        "CharacterOffsets": NotRequired[List[RealTimeContactAnalysisCharacterIntervalTypeDef]],
    },
)
RealTimeContactAnalysisTranscriptItemWithCharacterOffsetsTypeDef = TypedDict(
    "RealTimeContactAnalysisTranscriptItemWithCharacterOffsetsTypeDef",
    {
        "Id": str,
        "CharacterOffsets": NotRequired[RealTimeContactAnalysisCharacterIntervalTypeDef],
    },
)
RealTimeContactAnalysisTranscriptItemWithContentTypeDef = TypedDict(
    "RealTimeContactAnalysisTranscriptItemWithContentTypeDef",
    {
        "Id": str,
        "Content": NotRequired[str],
        "CharacterOffsets": NotRequired[RealTimeContactAnalysisCharacterIntervalTypeDef],
    },
)
RealTimeContactAnalysisSegmentAttachmentsTypeDef = TypedDict(
    "RealTimeContactAnalysisSegmentAttachmentsTypeDef",
    {
        "Id": str,
        "ParticipantId": str,
        "ParticipantRole": ParticipantRoleType,
        "Attachments": List[RealTimeContactAnalysisAttachmentTypeDef],
        "Time": RealTimeContactAnalysisTimeDataTypeDef,
        "DisplayName": NotRequired[str],
    },
)
RealTimeContactAnalysisSegmentEventTypeDef = TypedDict(
    "RealTimeContactAnalysisSegmentEventTypeDef",
    {
        "Id": str,
        "EventType": str,
        "Time": RealTimeContactAnalysisTimeDataTypeDef,
        "ParticipantId": NotRequired[str],
        "ParticipantRole": NotRequired[ParticipantRoleType],
        "DisplayName": NotRequired[str],
    },
)
ReferenceSummaryTypeDef = TypedDict(
    "ReferenceSummaryTypeDef",
    {
        "Url": NotRequired[UrlReferenceTypeDef],
        "Attachment": NotRequired[AttachmentReferenceTypeDef],
        "String": NotRequired[StringReferenceTypeDef],
        "Number": NotRequired[NumberReferenceTypeDef],
        "Date": NotRequired[DateReferenceTypeDef],
        "Email": NotRequired[EmailReferenceTypeDef],
    },
)
StartOutboundVoiceContactRequestRequestTypeDef = TypedDict(
    "StartOutboundVoiceContactRequestRequestTypeDef",
    {
        "DestinationPhoneNumber": str,
        "ContactFlowId": str,
        "InstanceId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
        "RelatedContactId": NotRequired[str],
        "ClientToken": NotRequired[str],
        "SourcePhoneNumber": NotRequired[str],
        "QueueId": NotRequired[str],
        "Attributes": NotRequired[Mapping[str, str]],
        "AnswerMachineDetectionConfig": NotRequired[AnswerMachineDetectionConfigTypeDef],
        "CampaignId": NotRequired[str],
        "TrafficType": NotRequired[TrafficTypeType],
    },
)
StartTaskContactRequestRequestTypeDef = TypedDict(
    "StartTaskContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "PreviousContactId": NotRequired[str],
        "ContactFlowId": NotRequired[str],
        "Attributes": NotRequired[Mapping[str, str]],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
        "Description": NotRequired[str],
        "ClientToken": NotRequired[str],
        "ScheduledTime": NotRequired[TimestampTypeDef],
        "TaskTemplateId": NotRequired[str],
        "QuickConnectId": NotRequired[str],
        "RelatedContactId": NotRequired[str],
    },
)
TaskActionDefinitionOutputTypeDef = TypedDict(
    "TaskActionDefinitionOutputTypeDef",
    {
        "Name": str,
        "ContactFlowId": str,
        "Description": NotRequired[str],
        "References": NotRequired[Dict[str, ReferenceTypeDef]],
    },
)
TaskActionDefinitionTypeDef = TypedDict(
    "TaskActionDefinitionTypeDef",
    {
        "Name": str,
        "ContactFlowId": str,
        "Description": NotRequired[str],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
    },
)
UpdateContactRequestRequestTypeDef = TypedDict(
    "UpdateContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
    },
)
ResourceTagsSearchCriteriaTypeDef = TypedDict(
    "ResourceTagsSearchCriteriaTypeDef",
    {
        "TagSearchCondition": NotRequired[TagSearchConditionTypeDef],
    },
)
SearchResourceTagsResponseTypeDef = TypedDict(
    "SearchResourceTagsResponseTypeDef",
    {
        "Tags": List[TagSetTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
SearchSecurityProfilesResponseTypeDef = TypedDict(
    "SearchSecurityProfilesResponseTypeDef",
    {
        "SecurityProfiles": List[SecurityProfileSearchSummaryTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
SearchVocabulariesResponseTypeDef = TypedDict(
    "SearchVocabulariesResponseTypeDef",
    {
        "VocabularySummaryList": List[VocabularySummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
SearchableContactAttributesTypeDef = TypedDict(
    "SearchableContactAttributesTypeDef",
    {
        "Criteria": Sequence[SearchableContactAttributesCriteriaTypeDef],
        "MatchType": NotRequired[SearchContactsMatchTypeType],
    },
)
SignInConfigOutputTypeDef = TypedDict(
    "SignInConfigOutputTypeDef",
    {
        "Distributions": List[SignInDistributionTypeDef],
    },
)
SignInConfigTypeDef = TypedDict(
    "SignInConfigTypeDef",
    {
        "Distributions": Sequence[SignInDistributionTypeDef],
    },
)
StartAttachedFileUploadResponseTypeDef = TypedDict(
    "StartAttachedFileUploadResponseTypeDef",
    {
        "FileArn": str,
        "FileId": str,
        "CreationTime": str,
        "FileStatus": FileStatusTypeType,
        "CreatedBy": CreatedByInfoTypeDef,
        "UploadUrlMetadata": UploadUrlMetadataTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartContactRecordingRequestRequestTypeDef = TypedDict(
    "StartContactRecordingRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "InitialContactId": str,
        "VoiceRecordingConfiguration": VoiceRecordingConfigurationTypeDef,
    },
)
TranscriptTypeDef = TypedDict(
    "TranscriptTypeDef",
    {
        "Criteria": Sequence[TranscriptCriteriaTypeDef],
        "MatchType": NotRequired[SearchContactsMatchTypeType],
    },
)
UserSearchSummaryTypeDef = TypedDict(
    "UserSearchSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "DirectoryUserId": NotRequired[str],
        "HierarchyGroupId": NotRequired[str],
        "Id": NotRequired[str],
        "IdentityInfo": NotRequired[UserIdentityInfoLiteTypeDef],
        "PhoneConfig": NotRequired[UserPhoneConfigTypeDef],
        "RoutingProfileId": NotRequired[str],
        "SecurityProfileIds": NotRequired[List[str]],
        "Tags": NotRequired[Dict[str, str]],
        "Username": NotRequired[str],
    },
)
ViewTypeDef = TypedDict(
    "ViewTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "Status": NotRequired[ViewStatusType],
        "Type": NotRequired[ViewTypeType],
        "Description": NotRequired[str],
        "Version": NotRequired[int],
        "VersionDescription": NotRequired[str],
        "Content": NotRequired[ViewContentTypeDef],
        "Tags": NotRequired[Dict[str, str]],
        "CreatedTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "ViewContentSha256": NotRequired[str],
    },
)
ListRulesResponseTypeDef = TypedDict(
    "ListRulesResponseTypeDef",
    {
        "RuleSummaryList": List[RuleSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
AgentConfigUnionTypeDef = Union[AgentConfigTypeDef, AgentConfigOutputTypeDef]
TelephonyConfigUnionTypeDef = Union[TelephonyConfigTypeDef, TelephonyConfigOutputTypeDef]
AgentInfoTypeDef = TypedDict(
    "AgentInfoTypeDef",
    {
        "Id": NotRequired[str],
        "ConnectedToAgentTimestamp": NotRequired[datetime],
        "AgentPauseDurationInSeconds": NotRequired[int],
        "HierarchyGroups": NotRequired[HierarchyGroupsTypeDef],
        "DeviceInfo": NotRequired[DeviceInfoTypeDef],
        "Capabilities": NotRequired[ParticipantCapabilitiesTypeDef],
    },
)
StartWebRTCContactRequestRequestTypeDef = TypedDict(
    "StartWebRTCContactRequestRequestTypeDef",
    {
        "ContactFlowId": str,
        "InstanceId": str,
        "ParticipantDetails": ParticipantDetailsTypeDef,
        "Attributes": NotRequired[Mapping[str, str]],
        "ClientToken": NotRequired[str],
        "AllowedCapabilities": NotRequired[AllowedCapabilitiesTypeDef],
        "RelatedContactId": NotRequired[str],
        "References": NotRequired[Mapping[str, ReferenceTypeDef]],
        "Description": NotRequired[str],
    },
)
QualityMetricsTypeDef = TypedDict(
    "QualityMetricsTypeDef",
    {
        "Agent": NotRequired[AgentQualityMetricsTypeDef],
        "Customer": NotRequired[CustomerQualityMetricsTypeDef],
    },
)
SearchPredefinedAttributesRequestSearchPredefinedAttributesPaginateTypeDef = TypedDict(
    "SearchPredefinedAttributesRequestSearchPredefinedAttributesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchCriteria": NotRequired[PredefinedAttributeSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
AttributeConditionTypeDef = TypedDict(
    "AttributeConditionTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
        "ProficiencyLevel": NotRequired[float],
        "MatchCriteria": NotRequired[MatchCriteriaTypeDef],
        "ComparisonOperator": NotRequired[str],
    },
)
CreateSecurityProfileRequestRequestTypeDef = TypedDict(
    "CreateSecurityProfileRequestRequestTypeDef",
    {
        "SecurityProfileName": str,
        "InstanceId": str,
        "Description": NotRequired[str],
        "Permissions": NotRequired[Sequence[str]],
        "Tags": NotRequired[Mapping[str, str]],
        "AllowedAccessControlTags": NotRequired[Mapping[str, str]],
        "TagRestrictedResources": NotRequired[Sequence[str]],
        "Applications": NotRequired[Sequence[ApplicationUnionTypeDef]],
        "HierarchyRestrictedResources": NotRequired[Sequence[str]],
        "AllowedAccessControlHierarchyGroupId": NotRequired[str],
    },
)
UpdateSecurityProfileRequestRequestTypeDef = TypedDict(
    "UpdateSecurityProfileRequestRequestTypeDef",
    {
        "SecurityProfileId": str,
        "InstanceId": str,
        "Description": NotRequired[str],
        "Permissions": NotRequired[Sequence[str]],
        "AllowedAccessControlTags": NotRequired[Mapping[str, str]],
        "TagRestrictedResources": NotRequired[Sequence[str]],
        "Applications": NotRequired[Sequence[ApplicationUnionTypeDef]],
        "HierarchyRestrictedResources": NotRequired[Sequence[str]],
        "AllowedAccessControlHierarchyGroupId": NotRequired[str],
    },
)
ListBotsResponseTypeDef = TypedDict(
    "ListBotsResponseTypeDef",
    {
        "LexBots": List[LexBotConfigTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
BatchGetAttachedFileMetadataResponseTypeDef = TypedDict(
    "BatchGetAttachedFileMetadataResponseTypeDef",
    {
        "Files": List[AttachedFileTypeDef],
        "Errors": List[AttachedFileErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ControlPlaneUserAttributeFilterTypeDef = TypedDict(
    "ControlPlaneUserAttributeFilterTypeDef",
    {
        "OrConditions": NotRequired[Sequence[AttributeAndConditionTypeDef]],
        "AndCondition": NotRequired[AttributeAndConditionTypeDef],
        "TagCondition": NotRequired[TagConditionTypeDef],
        "HierarchyGroupCondition": NotRequired[HierarchyGroupConditionTypeDef],
    },
)
ControlPlaneAttributeFilterTypeDef = TypedDict(
    "ControlPlaneAttributeFilterTypeDef",
    {
        "OrConditions": NotRequired[Sequence[CommonAttributeAndConditionTypeDef]],
        "AndCondition": NotRequired[CommonAttributeAndConditionTypeDef],
        "TagCondition": NotRequired[TagConditionTypeDef],
    },
)
ContactFlowModuleSearchFilterTypeDef = TypedDict(
    "ContactFlowModuleSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
ContactFlowSearchFilterTypeDef = TypedDict(
    "ContactFlowSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
HoursOfOperationSearchFilterTypeDef = TypedDict(
    "HoursOfOperationSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
PromptSearchFilterTypeDef = TypedDict(
    "PromptSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
QueueSearchFilterTypeDef = TypedDict(
    "QueueSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
QuickConnectSearchFilterTypeDef = TypedDict(
    "QuickConnectSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
RoutingProfileSearchFilterTypeDef = TypedDict(
    "RoutingProfileSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
SecurityProfilesSearchFilterTypeDef = TypedDict(
    "SecurityProfilesSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
    },
)
MeetingTypeDef = TypedDict(
    "MeetingTypeDef",
    {
        "MediaRegion": NotRequired[str],
        "MediaPlacement": NotRequired[MediaPlacementTypeDef],
        "MeetingFeatures": NotRequired[MeetingFeaturesConfigurationTypeDef],
        "MeetingId": NotRequired[str],
    },
)
DescribePhoneNumberResponseTypeDef = TypedDict(
    "DescribePhoneNumberResponseTypeDef",
    {
        "ClaimedPhoneNumberSummary": ClaimedPhoneNumberSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListConditionTypeDef = TypedDict(
    "ListConditionTypeDef",
    {
        "TargetListType": NotRequired[Literal["PROFICIENCIES"]],
        "Conditions": NotRequired[Sequence[ConditionTypeDef]],
    },
)
BatchPutContactRequestRequestTypeDef = TypedDict(
    "BatchPutContactRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactDataRequestList": Sequence[ContactDataRequestTypeDef],
        "ClientToken": NotRequired[str],
    },
)
GetCurrentUserDataRequestRequestTypeDef = TypedDict(
    "GetCurrentUserDataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Filters": UserDataFiltersTypeDef,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
SearchContactsResponseTypeDef = TypedDict(
    "SearchContactsResponseTypeDef",
    {
        "Contacts": List[ContactSearchSummaryTypeDef],
        "TotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeEvaluationFormResponseTypeDef = TypedDict(
    "DescribeEvaluationFormResponseTypeDef",
    {
        "EvaluationForm": EvaluationFormTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeQueueResponseTypeDef = TypedDict(
    "DescribeQueueResponseTypeDef",
    {
        "Queue": QueueTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchQueuesResponseTypeDef = TypedDict(
    "SearchQueuesResponseTypeDef",
    {
        "Queues": List[QueueTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeUserResponseTypeDef = TypedDict(
    "DescribeUserResponseTypeDef",
    {
        "User": UserTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RoutingProfileTypeDef = TypedDict(
    "RoutingProfileTypeDef",
    {
        "InstanceId": NotRequired[str],
        "Name": NotRequired[str],
        "RoutingProfileArn": NotRequired[str],
        "RoutingProfileId": NotRequired[str],
        "Description": NotRequired[str],
        "MediaConcurrencies": NotRequired[List[MediaConcurrencyTypeDef]],
        "DefaultOutboundQueueId": NotRequired[str],
        "Tags": NotRequired[Dict[str, str]],
        "NumberOfAssociatedQueues": NotRequired[int],
        "NumberOfAssociatedUsers": NotRequired[int],
        "AgentAvailabilityTimer": NotRequired[AgentAvailabilityTimerType],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
        "IsDefault": NotRequired[bool],
        "AssociatedQueueIds": NotRequired[List[str]],
    },
)
UpdateRoutingProfileConcurrencyRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileConcurrencyRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "MediaConcurrencies": Sequence[MediaConcurrencyTypeDef],
    },
)
CurrentMetricResultTypeDef = TypedDict(
    "CurrentMetricResultTypeDef",
    {
        "Dimensions": NotRequired[DimensionsTypeDef],
        "Collections": NotRequired[List[CurrentMetricDataTypeDef]],
    },
)
AssociateRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "AssociateRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "QueueConfigs": Sequence[RoutingProfileQueueConfigTypeDef],
    },
)
CreateRoutingProfileRequestRequestTypeDef = TypedDict(
    "CreateRoutingProfileRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Description": str,
        "DefaultOutboundQueueId": str,
        "MediaConcurrencies": Sequence[MediaConcurrencyTypeDef],
        "QueueConfigs": NotRequired[Sequence[RoutingProfileQueueConfigTypeDef]],
        "Tags": NotRequired[Mapping[str, str]],
        "AgentAvailabilityTimer": NotRequired[AgentAvailabilityTimerType],
    },
)
UpdateRoutingProfileQueuesRequestRequestTypeDef = TypedDict(
    "UpdateRoutingProfileQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "RoutingProfileId": str,
        "QueueConfigs": Sequence[RoutingProfileQueueConfigTypeDef],
    },
)
InstanceStorageConfigTypeDef = TypedDict(
    "InstanceStorageConfigTypeDef",
    {
        "StorageType": StorageTypeType,
        "AssociationId": NotRequired[str],
        "S3Config": NotRequired[S3ConfigTypeDef],
        "KinesisVideoStreamConfig": NotRequired[KinesisVideoStreamConfigTypeDef],
        "KinesisStreamConfig": NotRequired[KinesisStreamConfigTypeDef],
        "KinesisFirehoseConfig": NotRequired[KinesisFirehoseConfigTypeDef],
    },
)
SubmitContactEvaluationRequestRequestTypeDef = TypedDict(
    "SubmitContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
        "Answers": NotRequired[Mapping[str, EvaluationAnswerInputTypeDef]],
        "Notes": NotRequired[Mapping[str, EvaluationNoteTypeDef]],
    },
)
UpdateContactEvaluationRequestRequestTypeDef = TypedDict(
    "UpdateContactEvaluationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "EvaluationId": str,
        "Answers": NotRequired[Mapping[str, EvaluationAnswerInputTypeDef]],
        "Notes": NotRequired[Mapping[str, EvaluationNoteTypeDef]],
    },
)
EvaluationFormNumericQuestionPropertiesOutputTypeDef = TypedDict(
    "EvaluationFormNumericQuestionPropertiesOutputTypeDef",
    {
        "MinValue": int,
        "MaxValue": int,
        "Options": NotRequired[List[EvaluationFormNumericQuestionOptionTypeDef]],
        "Automation": NotRequired[EvaluationFormNumericQuestionAutomationTypeDef],
    },
)
EvaluationFormNumericQuestionPropertiesTypeDef = TypedDict(
    "EvaluationFormNumericQuestionPropertiesTypeDef",
    {
        "MinValue": int,
        "MaxValue": int,
        "Options": NotRequired[Sequence[EvaluationFormNumericQuestionOptionTypeDef]],
        "Automation": NotRequired[EvaluationFormNumericQuestionAutomationTypeDef],
    },
)
EvaluationFormSingleSelectQuestionAutomationOutputTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionAutomationOutputTypeDef",
    {
        "Options": List[EvaluationFormSingleSelectQuestionAutomationOptionTypeDef],
        "DefaultOptionRefId": NotRequired[str],
    },
)
EvaluationFormSingleSelectQuestionAutomationTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionAutomationTypeDef",
    {
        "Options": Sequence[EvaluationFormSingleSelectQuestionAutomationOptionTypeDef],
        "DefaultOptionRefId": NotRequired[str],
    },
)
EvaluationTypeDef = TypedDict(
    "EvaluationTypeDef",
    {
        "EvaluationId": str,
        "EvaluationArn": str,
        "Metadata": EvaluationMetadataTypeDef,
        "Answers": Dict[str, EvaluationAnswerOutputTypeDef],
        "Notes": Dict[str, EvaluationNoteTypeDef],
        "Status": EvaluationStatusType,
        "CreatedTime": datetime,
        "LastModifiedTime": datetime,
        "Scores": NotRequired[Dict[str, EvaluationScoreTypeDef]],
        "Tags": NotRequired[Dict[str, str]],
    },
)
ListContactEvaluationsResponseTypeDef = TypedDict(
    "ListContactEvaluationsResponseTypeDef",
    {
        "EvaluationSummaryList": List[EvaluationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
RoutingCriteriaTypeDef = TypedDict(
    "RoutingCriteriaTypeDef",
    {
        "Steps": NotRequired[List[StepTypeDef]],
        "ActivationTimestamp": NotRequired[datetime],
        "Index": NotRequired[int],
    },
)
CreateCaseActionDefinitionOutputTypeDef = TypedDict(
    "CreateCaseActionDefinitionOutputTypeDef",
    {
        "Fields": List[FieldValueOutputTypeDef],
        "TemplateId": str,
    },
)
UpdateCaseActionDefinitionOutputTypeDef = TypedDict(
    "UpdateCaseActionDefinitionOutputTypeDef",
    {
        "Fields": List[FieldValueOutputTypeDef],
    },
)
CreateCaseActionDefinitionTypeDef = TypedDict(
    "CreateCaseActionDefinitionTypeDef",
    {
        "Fields": Sequence[FieldValueTypeDef],
        "TemplateId": str,
    },
)
UpdateCaseActionDefinitionTypeDef = TypedDict(
    "UpdateCaseActionDefinitionTypeDef",
    {
        "Fields": Sequence[FieldValueTypeDef],
    },
)
UserDataTypeDef = TypedDict(
    "UserDataTypeDef",
    {
        "User": NotRequired[UserReferenceTypeDef],
        "RoutingProfile": NotRequired[RoutingProfileReferenceTypeDef],
        "HierarchyPath": NotRequired[HierarchyPathReferenceTypeDef],
        "Status": NotRequired[AgentStatusReferenceTypeDef],
        "AvailableSlotsByChannel": NotRequired[Dict[ChannelType, int]],
        "MaxSlotsByChannel": NotRequired[Dict[ChannelType, int]],
        "ActiveSlotsByChannel": NotRequired[Dict[ChannelType, int]],
        "Contacts": NotRequired[List[AgentContactReferenceTypeDef]],
        "NextStatus": NotRequired[str],
    },
)
HierarchyGroupTypeDef = TypedDict(
    "HierarchyGroupTypeDef",
    {
        "Id": NotRequired[str],
        "Arn": NotRequired[str],
        "Name": NotRequired[str],
        "LevelId": NotRequired[str],
        "HierarchyPath": NotRequired[HierarchyPathTypeDef],
        "Tags": NotRequired[Dict[str, str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
DescribeUserHierarchyStructureResponseTypeDef = TypedDict(
    "DescribeUserHierarchyStructureResponseTypeDef",
    {
        "HierarchyStructure": HierarchyStructureTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateUserHierarchyStructureRequestRequestTypeDef = TypedDict(
    "UpdateUserHierarchyStructureRequestRequestTypeDef",
    {
        "HierarchyStructure": HierarchyStructureUpdateTypeDef,
        "InstanceId": str,
    },
)
GetMetricDataRequestGetMetricDataPaginateTypeDef = TypedDict(
    "GetMetricDataRequestGetMetricDataPaginateTypeDef",
    {
        "InstanceId": str,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
        "Filters": FiltersTypeDef,
        "HistoricalMetrics": Sequence[HistoricalMetricTypeDef],
        "Groupings": NotRequired[Sequence[GroupingType]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetMetricDataRequestRequestTypeDef = TypedDict(
    "GetMetricDataRequestRequestTypeDef",
    {
        "InstanceId": str,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
        "Filters": FiltersTypeDef,
        "HistoricalMetrics": Sequence[HistoricalMetricTypeDef],
        "Groupings": NotRequired[Sequence[GroupingType]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
HistoricalMetricDataTypeDef = TypedDict(
    "HistoricalMetricDataTypeDef",
    {
        "Metric": NotRequired[HistoricalMetricTypeDef],
        "Value": NotRequired[float],
    },
)
CreateHoursOfOperationRequestRequestTypeDef = TypedDict(
    "CreateHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "TimeZone": str,
        "Config": Sequence[HoursOfOperationConfigTypeDef],
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
HoursOfOperationTypeDef = TypedDict(
    "HoursOfOperationTypeDef",
    {
        "HoursOfOperationId": NotRequired[str],
        "HoursOfOperationArn": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "TimeZone": NotRequired[str],
        "Config": NotRequired[List[HoursOfOperationConfigTypeDef]],
        "Tags": NotRequired[Dict[str, str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
UpdateHoursOfOperationRequestRequestTypeDef = TypedDict(
    "UpdateHoursOfOperationRequestRequestTypeDef",
    {
        "InstanceId": str,
        "HoursOfOperationId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "TimeZone": NotRequired[str],
        "Config": NotRequired[Sequence[HoursOfOperationConfigTypeDef]],
    },
)
DescribeInstanceResponseTypeDef = TypedDict(
    "DescribeInstanceResponseTypeDef",
    {
        "Instance": InstanceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TaskTemplateConstraintsOutputTypeDef = TypedDict(
    "TaskTemplateConstraintsOutputTypeDef",
    {
        "RequiredFields": NotRequired[List[RequiredFieldInfoTypeDef]],
        "ReadOnlyFields": NotRequired[List[ReadOnlyFieldInfoTypeDef]],
        "InvisibleFields": NotRequired[List[InvisibleFieldInfoTypeDef]],
    },
)
TaskTemplateConstraintsTypeDef = TypedDict(
    "TaskTemplateConstraintsTypeDef",
    {
        "RequiredFields": NotRequired[Sequence[RequiredFieldInfoTypeDef]],
        "ReadOnlyFields": NotRequired[Sequence[ReadOnlyFieldInfoTypeDef]],
        "InvisibleFields": NotRequired[Sequence[InvisibleFieldInfoTypeDef]],
    },
)
TaskTemplateDefaultsOutputTypeDef = TypedDict(
    "TaskTemplateDefaultsOutputTypeDef",
    {
        "DefaultFieldValues": NotRequired[List[TaskTemplateDefaultFieldValueTypeDef]],
    },
)
TaskTemplateDefaultsTypeDef = TypedDict(
    "TaskTemplateDefaultsTypeDef",
    {
        "DefaultFieldValues": NotRequired[Sequence[TaskTemplateDefaultFieldValueTypeDef]],
    },
)
TaskTemplateFieldUnionTypeDef = Union[TaskTemplateFieldTypeDef, TaskTemplateFieldOutputTypeDef]
MetricDataV2TypeDef = TypedDict(
    "MetricDataV2TypeDef",
    {
        "Metric": NotRequired[MetricV2OutputTypeDef],
        "Value": NotRequired[float],
    },
)
MetricV2UnionTypeDef = Union[MetricV2TypeDef, MetricV2OutputTypeDef]
SendChatIntegrationEventRequestRequestTypeDef = TypedDict(
    "SendChatIntegrationEventRequestRequestTypeDef",
    {
        "SourceId": str,
        "DestinationId": str,
        "Event": ChatEventTypeDef,
        "Subtype": NotRequired[str],
        "NewSessionDetails": NotRequired[NewSessionDetailsTypeDef],
    },
)
ChatParticipantRoleConfigTypeDef = TypedDict(
    "ChatParticipantRoleConfigTypeDef",
    {
        "ParticipantTimerConfigList": Sequence[ParticipantTimerConfigurationTypeDef],
    },
)
DescribePredefinedAttributeResponseTypeDef = TypedDict(
    "DescribePredefinedAttributeResponseTypeDef",
    {
        "PredefinedAttribute": PredefinedAttributeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchPredefinedAttributesResponseTypeDef = TypedDict(
    "SearchPredefinedAttributesResponseTypeDef",
    {
        "PredefinedAttributes": List[PredefinedAttributeTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
CreateQuickConnectRequestRequestTypeDef = TypedDict(
    "CreateQuickConnectRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "QuickConnectConfig": QuickConnectConfigTypeDef,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
QuickConnectTypeDef = TypedDict(
    "QuickConnectTypeDef",
    {
        "QuickConnectARN": NotRequired[str],
        "QuickConnectId": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "QuickConnectConfig": NotRequired[QuickConnectConfigTypeDef],
        "Tags": NotRequired[Dict[str, str]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedRegion": NotRequired[str],
    },
)
UpdateQuickConnectConfigRequestRequestTypeDef = TypedDict(
    "UpdateQuickConnectConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "QuickConnectId": str,
        "QuickConnectConfig": QuickConnectConfigTypeDef,
    },
)
RealTimeContactAnalysisSegmentTranscriptTypeDef = TypedDict(
    "RealTimeContactAnalysisSegmentTranscriptTypeDef",
    {
        "Id": str,
        "ParticipantId": str,
        "ParticipantRole": ParticipantRoleType,
        "Content": str,
        "Time": RealTimeContactAnalysisTimeDataTypeDef,
        "DisplayName": NotRequired[str],
        "ContentType": NotRequired[str],
        "Redaction": NotRequired[RealTimeContactAnalysisTranscriptItemRedactionTypeDef],
        "Sentiment": NotRequired[RealTimeContactAnalysisSentimentLabelType],
    },
)
RealTimeContactAnalysisPointOfInterestTypeDef = TypedDict(
    "RealTimeContactAnalysisPointOfInterestTypeDef",
    {
        "TranscriptItems": NotRequired[
            List[RealTimeContactAnalysisTranscriptItemWithCharacterOffsetsTypeDef]
        ],
    },
)
RealTimeContactAnalysisIssueDetectedTypeDef = TypedDict(
    "RealTimeContactAnalysisIssueDetectedTypeDef",
    {
        "TranscriptItems": List[RealTimeContactAnalysisTranscriptItemWithContentTypeDef],
    },
)
ListContactReferencesResponseTypeDef = TypedDict(
    "ListContactReferencesResponseTypeDef",
    {
        "ReferenceSummaryList": List[ReferenceSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
SearchResourceTagsRequestRequestTypeDef = TypedDict(
    "SearchResourceTagsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceTypes": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchCriteria": NotRequired[ResourceTagsSearchCriteriaTypeDef],
    },
)
SearchResourceTagsRequestSearchResourceTagsPaginateTypeDef = TypedDict(
    "SearchResourceTagsRequestSearchResourceTagsPaginateTypeDef",
    {
        "InstanceId": str,
        "ResourceTypes": NotRequired[Sequence[str]],
        "SearchCriteria": NotRequired[ResourceTagsSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetTrafficDistributionResponseTypeDef = TypedDict(
    "GetTrafficDistributionResponseTypeDef",
    {
        "TelephonyConfig": TelephonyConfigOutputTypeDef,
        "Id": str,
        "Arn": str,
        "SignInConfig": SignInConfigOutputTypeDef,
        "AgentConfig": AgentConfigOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SignInConfigUnionTypeDef = Union[SignInConfigTypeDef, SignInConfigOutputTypeDef]
UpdateTrafficDistributionRequestRequestTypeDef = TypedDict(
    "UpdateTrafficDistributionRequestRequestTypeDef",
    {
        "Id": str,
        "TelephonyConfig": NotRequired[TelephonyConfigTypeDef],
        "SignInConfig": NotRequired[SignInConfigTypeDef],
        "AgentConfig": NotRequired[AgentConfigTypeDef],
    },
)
ContactAnalysisTypeDef = TypedDict(
    "ContactAnalysisTypeDef",
    {
        "Transcript": NotRequired[TranscriptTypeDef],
    },
)
SearchUsersResponseTypeDef = TypedDict(
    "SearchUsersResponseTypeDef",
    {
        "Users": List[UserSearchSummaryTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
CreateViewResponseTypeDef = TypedDict(
    "CreateViewResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateViewVersionResponseTypeDef = TypedDict(
    "CreateViewVersionResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeViewResponseTypeDef = TypedDict(
    "DescribeViewResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateViewContentResponseTypeDef = TypedDict(
    "UpdateViewContentResponseTypeDef",
    {
        "View": ViewTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ExpressionTypeDef = TypedDict(
    "ExpressionTypeDef",
    {
        "AttributeCondition": NotRequired[AttributeConditionTypeDef],
        "AndExpression": NotRequired[List[Dict[str, Any]]],
        "OrExpression": NotRequired[List[Dict[str, Any]]],
    },
)
UserSearchFilterTypeDef = TypedDict(
    "UserSearchFilterTypeDef",
    {
        "TagFilter": NotRequired[ControlPlaneTagFilterTypeDef],
        "UserAttributeFilter": NotRequired[ControlPlaneUserAttributeFilterTypeDef],
    },
)
AgentStatusSearchFilterTypeDef = TypedDict(
    "AgentStatusSearchFilterTypeDef",
    {
        "AttributeFilter": NotRequired[ControlPlaneAttributeFilterTypeDef],
    },
)
UserHierarchyGroupSearchFilterTypeDef = TypedDict(
    "UserHierarchyGroupSearchFilterTypeDef",
    {
        "AttributeFilter": NotRequired[ControlPlaneAttributeFilterTypeDef],
    },
)
SearchContactFlowModulesRequestRequestTypeDef = TypedDict(
    "SearchContactFlowModulesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[ContactFlowModuleSearchFilterTypeDef],
        "SearchCriteria": NotRequired["ContactFlowModuleSearchCriteriaTypeDef"],
    },
)
SearchContactFlowModulesRequestSearchContactFlowModulesPaginateTypeDef = TypedDict(
    "SearchContactFlowModulesRequestSearchContactFlowModulesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[ContactFlowModuleSearchFilterTypeDef],
        "SearchCriteria": NotRequired[ContactFlowModuleSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchContactFlowsRequestRequestTypeDef = TypedDict(
    "SearchContactFlowsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[ContactFlowSearchFilterTypeDef],
        "SearchCriteria": NotRequired["ContactFlowSearchCriteriaTypeDef"],
    },
)
SearchContactFlowsRequestSearchContactFlowsPaginateTypeDef = TypedDict(
    "SearchContactFlowsRequestSearchContactFlowsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[ContactFlowSearchFilterTypeDef],
        "SearchCriteria": NotRequired[ContactFlowSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchHoursOfOperationsRequestRequestTypeDef = TypedDict(
    "SearchHoursOfOperationsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[HoursOfOperationSearchFilterTypeDef],
        "SearchCriteria": NotRequired["HoursOfOperationSearchCriteriaTypeDef"],
    },
)
SearchHoursOfOperationsRequestSearchHoursOfOperationsPaginateTypeDef = TypedDict(
    "SearchHoursOfOperationsRequestSearchHoursOfOperationsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[HoursOfOperationSearchFilterTypeDef],
        "SearchCriteria": NotRequired[HoursOfOperationSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchPromptsRequestRequestTypeDef = TypedDict(
    "SearchPromptsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[PromptSearchFilterTypeDef],
        "SearchCriteria": NotRequired["PromptSearchCriteriaTypeDef"],
    },
)
SearchPromptsRequestSearchPromptsPaginateTypeDef = TypedDict(
    "SearchPromptsRequestSearchPromptsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[PromptSearchFilterTypeDef],
        "SearchCriteria": NotRequired[PromptSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchQueuesRequestRequestTypeDef = TypedDict(
    "SearchQueuesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[QueueSearchFilterTypeDef],
        "SearchCriteria": NotRequired["QueueSearchCriteriaTypeDef"],
    },
)
SearchQueuesRequestSearchQueuesPaginateTypeDef = TypedDict(
    "SearchQueuesRequestSearchQueuesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[QueueSearchFilterTypeDef],
        "SearchCriteria": NotRequired[QueueSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchQuickConnectsRequestRequestTypeDef = TypedDict(
    "SearchQuickConnectsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[QuickConnectSearchFilterTypeDef],
        "SearchCriteria": NotRequired["QuickConnectSearchCriteriaTypeDef"],
    },
)
SearchQuickConnectsRequestSearchQuickConnectsPaginateTypeDef = TypedDict(
    "SearchQuickConnectsRequestSearchQuickConnectsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[QuickConnectSearchFilterTypeDef],
        "SearchCriteria": NotRequired[QuickConnectSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchRoutingProfilesRequestRequestTypeDef = TypedDict(
    "SearchRoutingProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[RoutingProfileSearchFilterTypeDef],
        "SearchCriteria": NotRequired["RoutingProfileSearchCriteriaTypeDef"],
    },
)
SearchRoutingProfilesRequestSearchRoutingProfilesPaginateTypeDef = TypedDict(
    "SearchRoutingProfilesRequestSearchRoutingProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[RoutingProfileSearchFilterTypeDef],
        "SearchCriteria": NotRequired[RoutingProfileSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchSecurityProfilesRequestRequestTypeDef = TypedDict(
    "SearchSecurityProfilesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchCriteria": NotRequired["SecurityProfileSearchCriteriaTypeDef"],
        "SearchFilter": NotRequired[SecurityProfilesSearchFilterTypeDef],
    },
)
SearchSecurityProfilesRequestSearchSecurityProfilesPaginateTypeDef = TypedDict(
    "SearchSecurityProfilesRequestSearchSecurityProfilesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchCriteria": NotRequired[SecurityProfileSearchCriteriaTypeDef],
        "SearchFilter": NotRequired[SecurityProfilesSearchFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ConnectionDataTypeDef = TypedDict(
    "ConnectionDataTypeDef",
    {
        "Attendee": NotRequired[AttendeeTypeDef],
        "Meeting": NotRequired[MeetingTypeDef],
    },
)
UserSearchCriteriaTypeDef = TypedDict(
    "UserSearchCriteriaTypeDef",
    {
        "OrConditions": NotRequired[Sequence[Dict[str, Any]]],
        "AndConditions": NotRequired[Sequence[Dict[str, Any]]],
        "StringCondition": NotRequired[StringConditionTypeDef],
        "ListCondition": NotRequired[ListConditionTypeDef],
        "HierarchyGroupCondition": NotRequired[HierarchyGroupConditionTypeDef],
    },
)
DescribeRoutingProfileResponseTypeDef = TypedDict(
    "DescribeRoutingProfileResponseTypeDef",
    {
        "RoutingProfile": RoutingProfileTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchRoutingProfilesResponseTypeDef = TypedDict(
    "SearchRoutingProfilesResponseTypeDef",
    {
        "RoutingProfiles": List[RoutingProfileTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
GetCurrentMetricDataResponseTypeDef = TypedDict(
    "GetCurrentMetricDataResponseTypeDef",
    {
        "MetricResults": List[CurrentMetricResultTypeDef],
        "DataSnapshotTime": datetime,
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
AssociateInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "AssociateInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "StorageConfig": InstanceStorageConfigTypeDef,
    },
)
DescribeInstanceStorageConfigResponseTypeDef = TypedDict(
    "DescribeInstanceStorageConfigResponseTypeDef",
    {
        "StorageConfig": InstanceStorageConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListInstanceStorageConfigsResponseTypeDef = TypedDict(
    "ListInstanceStorageConfigsResponseTypeDef",
    {
        "StorageConfigs": List[InstanceStorageConfigTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateInstanceStorageConfigRequestRequestTypeDef = TypedDict(
    "UpdateInstanceStorageConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "AssociationId": str,
        "ResourceType": InstanceStorageResourceTypeType,
        "StorageConfig": InstanceStorageConfigTypeDef,
    },
)
EvaluationFormSingleSelectQuestionPropertiesOutputTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionPropertiesOutputTypeDef",
    {
        "Options": List[EvaluationFormSingleSelectQuestionOptionTypeDef],
        "DisplayAs": NotRequired[EvaluationFormSingleSelectQuestionDisplayModeType],
        "Automation": NotRequired[EvaluationFormSingleSelectQuestionAutomationOutputTypeDef],
    },
)
EvaluationFormSingleSelectQuestionPropertiesTypeDef = TypedDict(
    "EvaluationFormSingleSelectQuestionPropertiesTypeDef",
    {
        "Options": Sequence[EvaluationFormSingleSelectQuestionOptionTypeDef],
        "DisplayAs": NotRequired[EvaluationFormSingleSelectQuestionDisplayModeType],
        "Automation": NotRequired[EvaluationFormSingleSelectQuestionAutomationTypeDef],
    },
)
DescribeContactEvaluationResponseTypeDef = TypedDict(
    "DescribeContactEvaluationResponseTypeDef",
    {
        "Evaluation": EvaluationTypeDef,
        "EvaluationForm": EvaluationFormContentTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ContactTypeDef = TypedDict(
    "ContactTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "InitialContactId": NotRequired[str],
        "PreviousContactId": NotRequired[str],
        "InitiationMethod": NotRequired[ContactInitiationMethodType],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Channel": NotRequired[ChannelType],
        "QueueInfo": NotRequired[QueueInfoTypeDef],
        "AgentInfo": NotRequired[AgentInfoTypeDef],
        "InitiationTimestamp": NotRequired[datetime],
        "DisconnectTimestamp": NotRequired[datetime],
        "LastUpdateTimestamp": NotRequired[datetime],
        "LastPausedTimestamp": NotRequired[datetime],
        "LastResumedTimestamp": NotRequired[datetime],
        "TotalPauseCount": NotRequired[int],
        "TotalPauseDurationInSeconds": NotRequired[int],
        "ScheduledTimestamp": NotRequired[datetime],
        "RelatedContactId": NotRequired[str],
        "WisdomInfo": NotRequired[WisdomInfoTypeDef],
        "QueueTimeAdjustmentSeconds": NotRequired[int],
        "QueuePriority": NotRequired[int],
        "Tags": NotRequired[Dict[str, str]],
        "ConnectedToSystemTimestamp": NotRequired[datetime],
        "RoutingCriteria": NotRequired[RoutingCriteriaTypeDef],
        "Customer": NotRequired[CustomerTypeDef],
        "Campaign": NotRequired[CampaignTypeDef],
        "AnsweringMachineDetectionStatus": NotRequired[AnsweringMachineDetectionStatusType],
        "CustomerVoiceActivity": NotRequired[CustomerVoiceActivityTypeDef],
        "QualityMetrics": NotRequired[QualityMetricsTypeDef],
        "DisconnectDetails": NotRequired[DisconnectDetailsTypeDef],
        "SegmentAttributes": NotRequired[Dict[str, SegmentAttributeValueTypeDef]],
    },
)
RuleActionOutputTypeDef = TypedDict(
    "RuleActionOutputTypeDef",
    {
        "ActionType": ActionTypeType,
        "TaskAction": NotRequired[TaskActionDefinitionOutputTypeDef],
        "EventBridgeAction": NotRequired[EventBridgeActionDefinitionTypeDef],
        "AssignContactCategoryAction": NotRequired[Dict[str, Any]],
        "SendNotificationAction": NotRequired[SendNotificationActionDefinitionOutputTypeDef],
        "CreateCaseAction": NotRequired[CreateCaseActionDefinitionOutputTypeDef],
        "UpdateCaseAction": NotRequired[UpdateCaseActionDefinitionOutputTypeDef],
        "EndAssociatedTasksAction": NotRequired[Dict[str, Any]],
        "SubmitAutoEvaluationAction": NotRequired[SubmitAutoEvaluationActionDefinitionTypeDef],
    },
)
RuleActionTypeDef = TypedDict(
    "RuleActionTypeDef",
    {
        "ActionType": ActionTypeType,
        "TaskAction": NotRequired[TaskActionDefinitionTypeDef],
        "EventBridgeAction": NotRequired[EventBridgeActionDefinitionTypeDef],
        "AssignContactCategoryAction": NotRequired[Mapping[str, Any]],
        "SendNotificationAction": NotRequired[SendNotificationActionDefinitionTypeDef],
        "CreateCaseAction": NotRequired[CreateCaseActionDefinitionTypeDef],
        "UpdateCaseAction": NotRequired[UpdateCaseActionDefinitionTypeDef],
        "EndAssociatedTasksAction": NotRequired[Mapping[str, Any]],
        "SubmitAutoEvaluationAction": NotRequired[SubmitAutoEvaluationActionDefinitionTypeDef],
    },
)
GetCurrentUserDataResponseTypeDef = TypedDict(
    "GetCurrentUserDataResponseTypeDef",
    {
        "UserDataList": List[UserDataTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeUserHierarchyGroupResponseTypeDef = TypedDict(
    "DescribeUserHierarchyGroupResponseTypeDef",
    {
        "HierarchyGroup": HierarchyGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchUserHierarchyGroupsResponseTypeDef = TypedDict(
    "SearchUserHierarchyGroupsResponseTypeDef",
    {
        "UserHierarchyGroups": List[HierarchyGroupTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
HistoricalMetricResultTypeDef = TypedDict(
    "HistoricalMetricResultTypeDef",
    {
        "Dimensions": NotRequired[DimensionsTypeDef],
        "Collections": NotRequired[List[HistoricalMetricDataTypeDef]],
    },
)
DescribeHoursOfOperationResponseTypeDef = TypedDict(
    "DescribeHoursOfOperationResponseTypeDef",
    {
        "HoursOfOperation": HoursOfOperationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchHoursOfOperationsResponseTypeDef = TypedDict(
    "SearchHoursOfOperationsResponseTypeDef",
    {
        "HoursOfOperations": List[HoursOfOperationTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
TaskTemplateConstraintsUnionTypeDef = Union[
    TaskTemplateConstraintsTypeDef, TaskTemplateConstraintsOutputTypeDef
]
GetTaskTemplateResponseTypeDef = TypedDict(
    "GetTaskTemplateResponseTypeDef",
    {
        "InstanceId": str,
        "Id": str,
        "Arn": str,
        "Name": str,
        "Description": str,
        "ContactFlowId": str,
        "Constraints": TaskTemplateConstraintsOutputTypeDef,
        "Defaults": TaskTemplateDefaultsOutputTypeDef,
        "Fields": List[TaskTemplateFieldOutputTypeDef],
        "Status": TaskTemplateStatusType,
        "LastModifiedTime": datetime,
        "CreatedTime": datetime,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTaskTemplateResponseTypeDef = TypedDict(
    "UpdateTaskTemplateResponseTypeDef",
    {
        "InstanceId": str,
        "Id": str,
        "Arn": str,
        "Name": str,
        "Description": str,
        "ContactFlowId": str,
        "Constraints": TaskTemplateConstraintsOutputTypeDef,
        "Defaults": TaskTemplateDefaultsOutputTypeDef,
        "Fields": List[TaskTemplateFieldOutputTypeDef],
        "Status": TaskTemplateStatusType,
        "LastModifiedTime": datetime,
        "CreatedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TaskTemplateDefaultsUnionTypeDef = Union[
    TaskTemplateDefaultsTypeDef, TaskTemplateDefaultsOutputTypeDef
]
CreateTaskTemplateRequestRequestTypeDef = TypedDict(
    "CreateTaskTemplateRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "Fields": Sequence[TaskTemplateFieldUnionTypeDef],
        "Description": NotRequired[str],
        "ContactFlowId": NotRequired[str],
        "Constraints": NotRequired[TaskTemplateConstraintsTypeDef],
        "Defaults": NotRequired[TaskTemplateDefaultsTypeDef],
        "Status": NotRequired[TaskTemplateStatusType],
        "ClientToken": NotRequired[str],
    },
)
UpdateTaskTemplateRequestRequestTypeDef = TypedDict(
    "UpdateTaskTemplateRequestRequestTypeDef",
    {
        "TaskTemplateId": str,
        "InstanceId": str,
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "ContactFlowId": NotRequired[str],
        "Constraints": NotRequired[TaskTemplateConstraintsTypeDef],
        "Defaults": NotRequired[TaskTemplateDefaultsTypeDef],
        "Status": NotRequired[TaskTemplateStatusType],
        "Fields": NotRequired[Sequence[TaskTemplateFieldUnionTypeDef]],
    },
)
MetricResultV2TypeDef = TypedDict(
    "MetricResultV2TypeDef",
    {
        "Dimensions": NotRequired[Dict[str, str]],
        "MetricInterval": NotRequired[MetricIntervalTypeDef],
        "Collections": NotRequired[List[MetricDataV2TypeDef]],
    },
)
GetMetricDataV2RequestRequestTypeDef = TypedDict(
    "GetMetricDataV2RequestRequestTypeDef",
    {
        "ResourceArn": str,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
        "Filters": Sequence[FilterV2TypeDef],
        "Metrics": Sequence[MetricV2UnionTypeDef],
        "Interval": NotRequired[IntervalDetailsTypeDef],
        "Groupings": NotRequired[Sequence[str]],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
UpdateParticipantRoleConfigChannelInfoTypeDef = TypedDict(
    "UpdateParticipantRoleConfigChannelInfoTypeDef",
    {
        "Chat": NotRequired[ChatParticipantRoleConfigTypeDef],
    },
)
DescribeQuickConnectResponseTypeDef = TypedDict(
    "DescribeQuickConnectResponseTypeDef",
    {
        "QuickConnect": QuickConnectTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchQuickConnectsResponseTypeDef = TypedDict(
    "SearchQuickConnectsResponseTypeDef",
    {
        "QuickConnects": List[QuickConnectTypeDef],
        "ApproximateTotalCount": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
RealTimeContactAnalysisCategoryDetailsTypeDef = TypedDict(
    "RealTimeContactAnalysisCategoryDetailsTypeDef",
    {
        "PointsOfInterest": List[RealTimeContactAnalysisPointOfInterestTypeDef],
    },
)
RealTimeContactAnalysisSegmentIssuesTypeDef = TypedDict(
    "RealTimeContactAnalysisSegmentIssuesTypeDef",
    {
        "IssuesDetected": List[RealTimeContactAnalysisIssueDetectedTypeDef],
    },
)
SearchCriteriaTypeDef = TypedDict(
    "SearchCriteriaTypeDef",
    {
        "AgentIds": NotRequired[Sequence[str]],
        "AgentHierarchyGroups": NotRequired[AgentHierarchyGroupsTypeDef],
        "Channels": NotRequired[Sequence[ChannelType]],
        "ContactAnalysis": NotRequired[ContactAnalysisTypeDef],
        "InitiationMethods": NotRequired[Sequence[ContactInitiationMethodType]],
        "QueueIds": NotRequired[Sequence[str]],
        "SearchableContactAttributes": NotRequired[SearchableContactAttributesTypeDef],
    },
)
SearchUsersRequestRequestTypeDef = TypedDict(
    "SearchUsersRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[UserSearchFilterTypeDef],
        "SearchCriteria": NotRequired["UserSearchCriteriaTypeDef"],
    },
)
SearchAgentStatusesRequestRequestTypeDef = TypedDict(
    "SearchAgentStatusesRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[AgentStatusSearchFilterTypeDef],
        "SearchCriteria": NotRequired["AgentStatusSearchCriteriaTypeDef"],
    },
)
SearchAgentStatusesRequestSearchAgentStatusesPaginateTypeDef = TypedDict(
    "SearchAgentStatusesRequestSearchAgentStatusesPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[AgentStatusSearchFilterTypeDef],
        "SearchCriteria": NotRequired[AgentStatusSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchUserHierarchyGroupsRequestRequestTypeDef = TypedDict(
    "SearchUserHierarchyGroupsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SearchFilter": NotRequired[UserHierarchyGroupSearchFilterTypeDef],
        "SearchCriteria": NotRequired["UserHierarchyGroupSearchCriteriaTypeDef"],
    },
)
SearchUserHierarchyGroupsRequestSearchUserHierarchyGroupsPaginateTypeDef = TypedDict(
    "SearchUserHierarchyGroupsRequestSearchUserHierarchyGroupsPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[UserHierarchyGroupSearchFilterTypeDef],
        "SearchCriteria": NotRequired[UserHierarchyGroupSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
StartWebRTCContactResponseTypeDef = TypedDict(
    "StartWebRTCContactResponseTypeDef",
    {
        "ConnectionData": ConnectionDataTypeDef,
        "ContactId": str,
        "ParticipantId": str,
        "ParticipantToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchUsersRequestSearchUsersPaginateTypeDef = TypedDict(
    "SearchUsersRequestSearchUsersPaginateTypeDef",
    {
        "InstanceId": str,
        "SearchFilter": NotRequired[UserSearchFilterTypeDef],
        "SearchCriteria": NotRequired[UserSearchCriteriaTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
EvaluationFormQuestionTypePropertiesOutputTypeDef = TypedDict(
    "EvaluationFormQuestionTypePropertiesOutputTypeDef",
    {
        "Numeric": NotRequired[EvaluationFormNumericQuestionPropertiesOutputTypeDef],
        "SingleSelect": NotRequired[EvaluationFormSingleSelectQuestionPropertiesOutputTypeDef],
    },
)
EvaluationFormQuestionTypePropertiesTypeDef = TypedDict(
    "EvaluationFormQuestionTypePropertiesTypeDef",
    {
        "Numeric": NotRequired[EvaluationFormNumericQuestionPropertiesTypeDef],
        "SingleSelect": NotRequired[EvaluationFormSingleSelectQuestionPropertiesTypeDef],
    },
)
DescribeContactResponseTypeDef = TypedDict(
    "DescribeContactResponseTypeDef",
    {
        "Contact": ContactTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "Name": str,
        "RuleId": str,
        "RuleArn": str,
        "TriggerEventSource": RuleTriggerEventSourceTypeDef,
        "Function": str,
        "Actions": List[RuleActionOutputTypeDef],
        "PublishStatus": RulePublishStatusType,
        "CreatedTime": datetime,
        "LastUpdatedTime": datetime,
        "LastUpdatedBy": str,
        "Tags": NotRequired[Dict[str, str]],
    },
)
RuleActionUnionTypeDef = Union[RuleActionTypeDef, RuleActionOutputTypeDef]
GetMetricDataResponseTypeDef = TypedDict(
    "GetMetricDataResponseTypeDef",
    {
        "MetricResults": List[HistoricalMetricResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
GetMetricDataV2ResponseTypeDef = TypedDict(
    "GetMetricDataV2ResponseTypeDef",
    {
        "MetricResults": List[MetricResultV2TypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateParticipantRoleConfigRequestRequestTypeDef = TypedDict(
    "UpdateParticipantRoleConfigRequestRequestTypeDef",
    {
        "InstanceId": str,
        "ContactId": str,
        "ChannelConfiguration": UpdateParticipantRoleConfigChannelInfoTypeDef,
    },
)
RealTimeContactAnalysisSegmentCategoriesTypeDef = TypedDict(
    "RealTimeContactAnalysisSegmentCategoriesTypeDef",
    {
        "MatchedDetails": Dict[str, RealTimeContactAnalysisCategoryDetailsTypeDef],
    },
)
SearchContactsRequestRequestTypeDef = TypedDict(
    "SearchContactsRequestRequestTypeDef",
    {
        "InstanceId": str,
        "TimeRange": SearchContactsTimeRangeTypeDef,
        "SearchCriteria": NotRequired[SearchCriteriaTypeDef],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Sort": NotRequired[SortTypeDef],
    },
)
SearchContactsRequestSearchContactsPaginateTypeDef = TypedDict(
    "SearchContactsRequestSearchContactsPaginateTypeDef",
    {
        "InstanceId": str,
        "TimeRange": SearchContactsTimeRangeTypeDef,
        "SearchCriteria": NotRequired[SearchCriteriaTypeDef],
        "Sort": NotRequired[SortTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
EvaluationFormQuestionOutputTypeDef = TypedDict(
    "EvaluationFormQuestionOutputTypeDef",
    {
        "Title": str,
        "RefId": str,
        "QuestionType": EvaluationFormQuestionTypeType,
        "Instructions": NotRequired[str],
        "NotApplicableEnabled": NotRequired[bool],
        "QuestionTypeProperties": NotRequired[EvaluationFormQuestionTypePropertiesOutputTypeDef],
        "Weight": NotRequired[float],
    },
)
EvaluationFormQuestionTypeDef = TypedDict(
    "EvaluationFormQuestionTypeDef",
    {
        "Title": str,
        "RefId": str,
        "QuestionType": EvaluationFormQuestionTypeType,
        "Instructions": NotRequired[str],
        "NotApplicableEnabled": NotRequired[bool],
        "QuestionTypeProperties": NotRequired[EvaluationFormQuestionTypePropertiesTypeDef],
        "Weight": NotRequired[float],
    },
)
DescribeRuleResponseTypeDef = TypedDict(
    "DescribeRuleResponseTypeDef",
    {
        "Rule": RuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRuleRequestRequestTypeDef = TypedDict(
    "CreateRuleRequestRequestTypeDef",
    {
        "InstanceId": str,
        "Name": str,
        "TriggerEventSource": RuleTriggerEventSourceTypeDef,
        "Function": str,
        "Actions": Sequence[RuleActionUnionTypeDef],
        "PublishStatus": RulePublishStatusType,
        "ClientToken": NotRequired[str],
    },
)
UpdateRuleRequestRequestTypeDef = TypedDict(
    "UpdateRuleRequestRequestTypeDef",
    {
        "RuleId": str,
        "InstanceId": str,
        "Name": str,
        "Function": str,
        "Actions": Sequence[RuleActionUnionTypeDef],
        "PublishStatus": RulePublishStatusType,
    },
)
RealtimeContactAnalysisSegmentTypeDef = TypedDict(
    "RealtimeContactAnalysisSegmentTypeDef",
    {
        "Transcript": NotRequired[RealTimeContactAnalysisSegmentTranscriptTypeDef],
        "Categories": NotRequired[RealTimeContactAnalysisSegmentCategoriesTypeDef],
        "Issues": NotRequired[RealTimeContactAnalysisSegmentIssuesTypeDef],
        "Event": NotRequired[RealTimeContactAnalysisSegmentEventTypeDef],
        "Attachments": NotRequired[RealTimeContactAnalysisSegmentAttachmentsTypeDef],
    },
)
EvaluationFormItemOutputTypeDef = TypedDict(
    "EvaluationFormItemOutputTypeDef",
    {
        "Section": NotRequired[Dict[str, Any]],
        "Question": NotRequired[EvaluationFormQuestionOutputTypeDef],
    },
)
EvaluationFormItemTypeDef = TypedDict(
    "EvaluationFormItemTypeDef",
    {
        "Section": NotRequired[Dict[str, Any]],
        "Question": NotRequired[EvaluationFormQuestionTypeDef],
    },
)
ListRealtimeContactAnalysisSegmentsV2ResponseTypeDef = TypedDict(
    "ListRealtimeContactAnalysisSegmentsV2ResponseTypeDef",
    {
        "Channel": RealTimeContactAnalysisSupportedChannelType,
        "Status": RealTimeContactAnalysisStatusType,
        "Segments": List[RealtimeContactAnalysisSegmentTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
