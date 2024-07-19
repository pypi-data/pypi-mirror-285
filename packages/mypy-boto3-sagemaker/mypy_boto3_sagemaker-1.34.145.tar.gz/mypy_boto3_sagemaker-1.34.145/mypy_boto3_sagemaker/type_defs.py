"""
Type annotations for sagemaker service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_sagemaker/type_defs/)

Usage::

    ```python
    from mypy_boto3_sagemaker.type_defs import ActionSourceTypeDef

    data: ActionSourceTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence, Union

from .literals import (
    ActionStatusType,
    AdditionalS3DataSourceDataTypeType,
    AggregationTransformationValueType,
    AlgorithmSortByType,
    AlgorithmStatusType,
    AppImageConfigSortKeyType,
    AppInstanceTypeType,
    AppNetworkAccessTypeType,
    AppSecurityGroupManagementType,
    AppStatusType,
    AppTypeType,
    ArtifactSourceIdTypeType,
    AssemblyTypeType,
    AssociationEdgeTypeType,
    AsyncNotificationTopicTypesType,
    AthenaResultCompressionTypeType,
    AthenaResultFormatType,
    AuthModeType,
    AutoMLAlgorithmType,
    AutoMLChannelTypeType,
    AutoMLJobObjectiveTypeType,
    AutoMLJobSecondaryStatusType,
    AutoMLJobStatusType,
    AutoMLMetricEnumType,
    AutoMLMetricExtendedEnumType,
    AutoMLModeType,
    AutoMLProblemTypeConfigNameType,
    AutoMLProcessingUnitType,
    AutoMLS3DataTypeType,
    AutoMLSortByType,
    AutoMLSortOrderType,
    AwsManagedHumanLoopRequestSourceType,
    BatchStrategyType,
    BooleanOperatorType,
    CandidateSortByType,
    CandidateStatusType,
    CandidateStepTypeType,
    CapacitySizeTypeType,
    CaptureModeType,
    CaptureStatusType,
    ClarifyFeatureTypeType,
    ClarifyTextGranularityType,
    ClarifyTextLanguageType,
    ClusterInstanceStatusType,
    ClusterInstanceTypeType,
    ClusterSortByType,
    ClusterStatusType,
    CodeRepositorySortByType,
    CodeRepositorySortOrderType,
    CollectionTypeType,
    CompilationJobStatusType,
    CompleteOnConvergenceType,
    CompressionTypeType,
    ConditionOutcomeType,
    ContainerModeType,
    ContentClassifierType,
    CrossAccountFilterOptionType,
    DataDistributionTypeType,
    DataSourceNameType,
    DetailedAlgorithmStatusType,
    DetailedModelPackageStatusType,
    DeviceDeploymentStatusType,
    DeviceSubsetTypeType,
    DirectInternetAccessType,
    DirectionType,
    DomainStatusType,
    EdgePackagingJobStatusType,
    EdgePresetDeploymentStatusType,
    EnabledOrDisabledType,
    EndpointConfigSortKeyType,
    EndpointSortKeyType,
    EndpointStatusType,
    ExecutionRoleIdentityConfigType,
    ExecutionStatusType,
    FailureHandlingPolicyType,
    FeatureGroupSortByType,
    FeatureGroupSortOrderType,
    FeatureGroupStatusType,
    FeatureStatusType,
    FeatureTypeType,
    FileSystemAccessModeType,
    FileSystemTypeType,
    FillingTypeType,
    FlatInvocationsType,
    FlowDefinitionStatusType,
    FrameworkType,
    HubContentSortByType,
    HubContentStatusType,
    HubContentSupportStatusType,
    HubContentTypeType,
    HubSortByType,
    HubStatusType,
    HumanTaskUiStatusType,
    HyperParameterScalingTypeType,
    HyperParameterTuningJobObjectiveTypeType,
    HyperParameterTuningJobSortByOptionsType,
    HyperParameterTuningJobStatusType,
    HyperParameterTuningJobStrategyTypeType,
    HyperParameterTuningJobWarmStartTypeType,
    ImageSortByType,
    ImageSortOrderType,
    ImageStatusType,
    ImageVersionSortByType,
    ImageVersionSortOrderType,
    ImageVersionStatusType,
    InferenceComponentSortKeyType,
    InferenceComponentStatusType,
    InferenceExecutionModeType,
    InferenceExperimentStatusType,
    InferenceExperimentStopDesiredStateType,
    InputModeType,
    InstanceTypeType,
    IsTrackingServerActiveType,
    JobTypeType,
    JoinSourceType,
    LabelingJobStatusType,
    LastUpdateStatusValueType,
    LineageTypeType,
    ListCompilationJobsSortByType,
    ListDeviceFleetsSortByType,
    ListEdgeDeploymentPlansSortByType,
    ListEdgePackagingJobsSortByType,
    ListInferenceRecommendationsJobsSortByType,
    ListOptimizationJobsSortByType,
    ListWorkforcesSortByOptionsType,
    ListWorkteamsSortByOptionsType,
    ManagedInstanceScalingStatusType,
    MetricSetSourceType,
    MlToolsType,
    ModelApprovalStatusType,
    ModelCacheSettingType,
    ModelCardExportJobSortByType,
    ModelCardExportJobSortOrderType,
    ModelCardExportJobStatusType,
    ModelCardProcessingStatusType,
    ModelCardSortByType,
    ModelCardSortOrderType,
    ModelCardStatusType,
    ModelCompressionTypeType,
    ModelMetadataFilterTypeType,
    ModelPackageGroupSortByType,
    ModelPackageGroupStatusType,
    ModelPackageSortByType,
    ModelPackageStatusType,
    ModelPackageTypeType,
    ModelSortKeyType,
    ModelVariantActionType,
    ModelVariantStatusType,
    MonitoringAlertHistorySortKeyType,
    MonitoringAlertStatusType,
    MonitoringExecutionSortKeyType,
    MonitoringJobDefinitionSortKeyType,
    MonitoringProblemTypeType,
    MonitoringScheduleSortKeyType,
    MonitoringTypeType,
    NotebookInstanceAcceleratorTypeType,
    NotebookInstanceLifecycleConfigSortKeyType,
    NotebookInstanceLifecycleConfigSortOrderType,
    NotebookInstanceSortKeyType,
    NotebookInstanceSortOrderType,
    NotebookInstanceStatusType,
    NotebookOutputOptionType,
    ObjectiveStatusType,
    OfflineStoreStatusValueType,
    OperatorType,
    OptimizationJobDeploymentInstanceTypeType,
    OptimizationJobStatusType,
    OrderKeyType,
    OutputCompressionTypeType,
    ParameterTypeType,
    PipelineExecutionStatusType,
    PipelineStatusType,
    ProblemTypeType,
    ProcessingInstanceTypeType,
    ProcessingJobStatusType,
    ProcessingS3CompressionTypeType,
    ProcessingS3DataDistributionTypeType,
    ProcessingS3DataTypeType,
    ProcessingS3InputModeType,
    ProcessingS3UploadModeType,
    ProcessorType,
    ProductionVariantAcceleratorTypeType,
    ProductionVariantInstanceTypeType,
    ProfilingStatusType,
    ProjectSortByType,
    ProjectSortOrderType,
    ProjectStatusType,
    RecommendationJobStatusType,
    RecommendationJobSupportedEndpointTypeType,
    RecommendationJobTypeType,
    RecommendationStatusType,
    RecordWrapperType,
    RedshiftResultCompressionTypeType,
    RedshiftResultFormatType,
    RepositoryAccessModeType,
    ResourceCatalogSortOrderType,
    ResourceTypeType,
    RetentionTypeType,
    RootAccessType,
    RoutingStrategyType,
    RStudioServerProAccessStatusType,
    RStudioServerProUserGroupType,
    RuleEvaluationStatusType,
    S3DataDistributionType,
    S3DataTypeType,
    S3ModelDataTypeType,
    SagemakerServicecatalogStatusType,
    ScheduleStatusType,
    SearchSortOrderType,
    SecondaryStatusType,
    SharingTypeType,
    SkipModelValidationType,
    SortActionsByType,
    SortAssociationsByType,
    SortByType,
    SortContextsByType,
    SortExperimentsByType,
    SortInferenceExperimentsByType,
    SortLineageGroupsByType,
    SortOrderType,
    SortPipelineExecutionsByType,
    SortPipelinesByType,
    SortTrackingServerByType,
    SortTrialComponentsByType,
    SortTrialsByType,
    SpaceSortKeyType,
    SpaceStatusType,
    SplitTypeType,
    StageStatusType,
    StatisticType,
    StepStatusType,
    StorageTypeType,
    StudioLifecycleConfigAppTypeType,
    StudioLifecycleConfigSortKeyType,
    StudioWebPortalType,
    TableFormatType,
    TargetDeviceType,
    TargetPlatformAcceleratorType,
    TargetPlatformArchType,
    TargetPlatformOsType,
    ThroughputModeType,
    TrackingServerSizeType,
    TrackingServerStatusType,
    TrafficRoutingConfigTypeType,
    TrafficTypeType,
    TrainingInputModeType,
    TrainingInstanceTypeType,
    TrainingJobEarlyStoppingTypeType,
    TrainingJobSortByOptionsType,
    TrainingJobStatusType,
    TrainingRepositoryAccessModeType,
    TransformInstanceTypeType,
    TransformJobStatusType,
    TrialComponentPrimaryStatusType,
    TtlDurationUnitType,
    UserProfileSortKeyType,
    UserProfileStatusType,
    VariantPropertyTypeType,
    VariantStatusType,
    VendorGuidanceType,
    WarmPoolResourceStatusType,
    WorkforceStatusType,
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
    "ActionSourceTypeDef",
    "AddAssociationRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "TagTypeDef",
    "AdditionalS3DataSourceTypeDef",
    "AgentVersionTypeDef",
    "AlarmTypeDef",
    "MetricDefinitionTypeDef",
    "AlgorithmStatusItemTypeDef",
    "AlgorithmSummaryTypeDef",
    "AmazonQSettingsTypeDef",
    "AnnotationConsolidationConfigTypeDef",
    "ResourceSpecTypeDef",
    "AppSpecificationExtraOutputTypeDef",
    "AppSpecificationOutputTypeDef",
    "AppSpecificationTypeDef",
    "ArtifactSourceTypeTypeDef",
    "AssociateTrialComponentRequestRequestTypeDef",
    "AsyncInferenceClientConfigTypeDef",
    "AsyncInferenceNotificationConfigOutputTypeDef",
    "AsyncInferenceNotificationConfigTypeDef",
    "AthenaDatasetDefinitionTypeDef",
    "AutoMLAlgorithmConfigOutputTypeDef",
    "AutoMLAlgorithmConfigTypeDef",
    "AutoMLCandidateStepTypeDef",
    "AutoMLContainerDefinitionTypeDef",
    "FinalAutoMLJobObjectiveMetricTypeDef",
    "AutoMLS3DataSourceTypeDef",
    "AutoMLDataSplitConfigTypeDef",
    "AutoMLJobArtifactsTypeDef",
    "AutoMLJobCompletionCriteriaTypeDef",
    "AutoMLJobObjectiveTypeDef",
    "AutoMLJobStepMetadataTypeDef",
    "AutoMLPartialFailureReasonTypeDef",
    "AutoMLOutputDataConfigTypeDef",
    "TabularResolvedAttributesTypeDef",
    "TextGenerationResolvedAttributesTypeDef",
    "VpcConfigOutputTypeDef",
    "VpcConfigTypeDef",
    "AutoParameterTypeDef",
    "AutotuneTypeDef",
    "BatchDataCaptureConfigTypeDef",
    "BatchDescribeModelPackageErrorTypeDef",
    "BatchDescribeModelPackageInputRequestTypeDef",
    "BestObjectiveNotImprovingTypeDef",
    "MetricsSourceTypeDef",
    "CacheHitResultTypeDef",
    "OutputParameterTypeDef",
    "CandidateArtifactLocationsTypeDef",
    "MetricDatumTypeDef",
    "DirectDeploySettingsTypeDef",
    "GenerativeAiSettingsTypeDef",
    "IdentityProviderOAuthSettingTypeDef",
    "KendraSettingsTypeDef",
    "ModelRegisterSettingsTypeDef",
    "TimeSeriesForecastingSettingsTypeDef",
    "WorkspaceSettingsTypeDef",
    "CapacitySizeTypeDef",
    "CaptureContentTypeHeaderOutputTypeDef",
    "CaptureContentTypeHeaderTypeDef",
    "CaptureOptionTypeDef",
    "CategoricalParameterOutputTypeDef",
    "CategoricalParameterRangeExtraOutputTypeDef",
    "CategoricalParameterRangeOutputTypeDef",
    "CategoricalParameterRangeSpecificationOutputTypeDef",
    "CategoricalParameterRangeSpecificationTypeDef",
    "CategoricalParameterRangeTypeDef",
    "CategoricalParameterTypeDef",
    "ShuffleConfigTypeDef",
    "ChannelSpecificationOutputTypeDef",
    "ChannelSpecificationTypeDef",
    "CheckpointConfigTypeDef",
    "ClarifyCheckStepMetadataTypeDef",
    "ClarifyInferenceConfigOutputTypeDef",
    "ClarifyInferenceConfigTypeDef",
    "ClarifyShapBaselineConfigTypeDef",
    "ClarifyTextConfigTypeDef",
    "ClusterEbsVolumeConfigTypeDef",
    "ClusterLifeCycleConfigTypeDef",
    "ClusterInstancePlacementTypeDef",
    "ClusterInstanceStatusDetailsTypeDef",
    "ClusterSummaryTypeDef",
    "ContainerConfigExtraOutputTypeDef",
    "FileSystemConfigTypeDef",
    "ContainerConfigOutputTypeDef",
    "ContainerConfigTypeDef",
    "CustomImageTypeDef",
    "GitConfigTypeDef",
    "CodeRepositoryTypeDef",
    "CognitoConfigTypeDef",
    "CognitoMemberDefinitionTypeDef",
    "VectorConfigTypeDef",
    "CollectionConfigurationExtraOutputTypeDef",
    "CollectionConfigurationOutputTypeDef",
    "CollectionConfigurationTypeDef",
    "CompilationJobSummaryTypeDef",
    "ConditionStepMetadataTypeDef",
    "MultiModelConfigTypeDef",
    "ContextSourceTypeDef",
    "ContinuousParameterRangeSpecificationTypeDef",
    "ContinuousParameterRangeTypeDef",
    "ConvergenceDetectedTypeDef",
    "MetadataPropertiesTypeDef",
    "ModelDeployConfigTypeDef",
    "InputConfigTypeDef",
    "NeoVpcConfigTypeDef",
    "StoppingConditionTypeDef",
    "DataQualityAppSpecificationTypeDef",
    "MonitoringStoppingConditionTypeDef",
    "EdgeOutputConfigTypeDef",
    "EdgeDeploymentModelConfigTypeDef",
    "ThroughputConfigTypeDef",
    "FlowDefinitionOutputConfigTypeDef",
    "HumanLoopRequestSourceTypeDef",
    "HubS3StorageConfigTypeDef",
    "UiTemplateTypeDef",
    "CreateImageVersionRequestRequestTypeDef",
    "InferenceComponentRuntimeConfigTypeDef",
    "LabelingJobOutputConfigTypeDef",
    "LabelingJobStoppingConditionsTypeDef",
    "ModelBiasAppSpecificationTypeDef",
    "ModelCardExportOutputConfigTypeDef",
    "ModelCardSecurityConfigTypeDef",
    "ModelExplainabilityAppSpecificationTypeDef",
    "InferenceExecutionConfigTypeDef",
    "ModelPackageModelCardTypeDef",
    "ModelPackageSecurityConfigTypeDef",
    "ModelQualityAppSpecificationTypeDef",
    "InstanceMetadataServiceConfigurationTypeDef",
    "NotebookInstanceLifecycleHookTypeDef",
    "OptimizationJobOutputConfigTypeDef",
    "OptimizationVpcConfigTypeDef",
    "ParallelismConfigurationTypeDef",
    "PipelineDefinitionS3LocationTypeDef",
    "CreatePresignedDomainUrlRequestRequestTypeDef",
    "CreatePresignedMlflowTrackingServerUrlRequestRequestTypeDef",
    "CreatePresignedNotebookInstanceUrlInputRequestTypeDef",
    "ExperimentConfigTypeDef",
    "ProcessingStoppingConditionTypeDef",
    "OwnershipSettingsTypeDef",
    "SpaceSharingSettingsTypeDef",
    "InfraCheckConfigTypeDef",
    "OutputDataConfigTypeDef",
    "ProfilerConfigTypeDef",
    "RemoteDebugConfigTypeDef",
    "RetryStrategyTypeDef",
    "SessionChainingConfigTypeDef",
    "TensorBoardOutputConfigTypeDef",
    "DataProcessingTypeDef",
    "ModelClientConfigTypeDef",
    "TransformOutputTypeDef",
    "TransformResourcesTypeDef",
    "TimestampTypeDef",
    "TrialComponentArtifactTypeDef",
    "TrialComponentParameterValueTypeDef",
    "TrialComponentStatusTypeDef",
    "OidcConfigTypeDef",
    "SourceIpConfigTypeDef",
    "WorkforceVpcConfigRequestTypeDef",
    "NotificationConfigurationTypeDef",
    "EFSFileSystemConfigTypeDef",
    "EFSFileSystemTypeDef",
    "CustomPosixUserConfigTypeDef",
    "CustomizedMetricSpecificationTypeDef",
    "DataCaptureConfigSummaryTypeDef",
    "DataCatalogConfigTypeDef",
    "DataQualityAppSpecificationOutputTypeDef",
    "MonitoringConstraintsResourceTypeDef",
    "MonitoringStatisticsResourceTypeDef",
    "EndpointInputTypeDef",
    "FileSystemDataSourceTypeDef",
    "S3DataSourceExtraOutputTypeDef",
    "S3DataSourceOutputTypeDef",
    "S3DataSourceTypeDef",
    "RedshiftDatasetDefinitionTypeDef",
    "DebugRuleConfigurationExtraOutputTypeDef",
    "DebugRuleConfigurationOutputTypeDef",
    "DebugRuleConfigurationTypeDef",
    "DebugRuleEvaluationStatusTypeDef",
    "DefaultEbsStorageSettingsTypeDef",
    "DeleteActionRequestRequestTypeDef",
    "DeleteAlgorithmInputRequestTypeDef",
    "DeleteAppImageConfigRequestRequestTypeDef",
    "DeleteAppRequestRequestTypeDef",
    "DeleteAssociationRequestRequestTypeDef",
    "DeleteClusterRequestRequestTypeDef",
    "DeleteCodeRepositoryInputRequestTypeDef",
    "DeleteCompilationJobRequestRequestTypeDef",
    "DeleteContextRequestRequestTypeDef",
    "DeleteDataQualityJobDefinitionRequestRequestTypeDef",
    "DeleteDeviceFleetRequestRequestTypeDef",
    "RetentionPolicyTypeDef",
    "DeleteEdgeDeploymentPlanRequestRequestTypeDef",
    "DeleteEdgeDeploymentStageRequestRequestTypeDef",
    "DeleteEndpointConfigInputRequestTypeDef",
    "DeleteEndpointInputRequestTypeDef",
    "DeleteExperimentRequestRequestTypeDef",
    "DeleteFeatureGroupRequestRequestTypeDef",
    "DeleteFlowDefinitionRequestRequestTypeDef",
    "DeleteHubContentReferenceRequestRequestTypeDef",
    "DeleteHubContentRequestRequestTypeDef",
    "DeleteHubRequestRequestTypeDef",
    "DeleteHumanTaskUiRequestRequestTypeDef",
    "DeleteHyperParameterTuningJobRequestRequestTypeDef",
    "DeleteImageRequestRequestTypeDef",
    "DeleteImageVersionRequestRequestTypeDef",
    "DeleteInferenceComponentInputRequestTypeDef",
    "DeleteInferenceExperimentRequestRequestTypeDef",
    "DeleteMlflowTrackingServerRequestRequestTypeDef",
    "DeleteModelBiasJobDefinitionRequestRequestTypeDef",
    "DeleteModelCardRequestRequestTypeDef",
    "DeleteModelExplainabilityJobDefinitionRequestRequestTypeDef",
    "DeleteModelInputRequestTypeDef",
    "DeleteModelPackageGroupInputRequestTypeDef",
    "DeleteModelPackageGroupPolicyInputRequestTypeDef",
    "DeleteModelPackageInputRequestTypeDef",
    "DeleteModelQualityJobDefinitionRequestRequestTypeDef",
    "DeleteMonitoringScheduleRequestRequestTypeDef",
    "DeleteNotebookInstanceInputRequestTypeDef",
    "DeleteNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "DeleteOptimizationJobRequestRequestTypeDef",
    "DeletePipelineRequestRequestTypeDef",
    "DeleteProjectInputRequestTypeDef",
    "DeleteSpaceRequestRequestTypeDef",
    "DeleteStudioLifecycleConfigRequestRequestTypeDef",
    "DeleteTagsInputRequestTypeDef",
    "DeleteTrialComponentRequestRequestTypeDef",
    "DeleteTrialRequestRequestTypeDef",
    "DeleteUserProfileRequestRequestTypeDef",
    "DeleteWorkforceRequestRequestTypeDef",
    "DeleteWorkteamRequestRequestTypeDef",
    "DeployedImageTypeDef",
    "RealTimeInferenceRecommendationTypeDef",
    "DeviceSelectionConfigOutputTypeDef",
    "EdgeDeploymentConfigTypeDef",
    "EdgeDeploymentStatusTypeDef",
    "DeviceSelectionConfigTypeDef",
    "DeregisterDevicesRequestRequestTypeDef",
    "DerivedInformationTypeDef",
    "DescribeActionRequestRequestTypeDef",
    "DescribeAlgorithmInputRequestTypeDef",
    "DescribeAppImageConfigRequestRequestTypeDef",
    "DescribeAppRequestRequestTypeDef",
    "DescribeArtifactRequestRequestTypeDef",
    "DescribeAutoMLJobRequestRequestTypeDef",
    "ModelDeployResultTypeDef",
    "DescribeAutoMLJobV2RequestRequestTypeDef",
    "DescribeClusterNodeRequestRequestTypeDef",
    "DescribeClusterRequestRequestTypeDef",
    "DescribeCodeRepositoryInputRequestTypeDef",
    "DescribeCompilationJobRequestRequestTypeDef",
    "ModelArtifactsTypeDef",
    "ModelDigestsTypeDef",
    "NeoVpcConfigOutputTypeDef",
    "DescribeContextRequestRequestTypeDef",
    "DescribeDataQualityJobDefinitionRequestRequestTypeDef",
    "DescribeDeviceFleetRequestRequestTypeDef",
    "DescribeDeviceRequestRequestTypeDef",
    "EdgeModelTypeDef",
    "DescribeDomainRequestRequestTypeDef",
    "DescribeEdgeDeploymentPlanRequestRequestTypeDef",
    "DescribeEdgePackagingJobRequestRequestTypeDef",
    "EdgePresetDeploymentOutputTypeDef",
    "DescribeEndpointConfigInputRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeEndpointInputRequestTypeDef",
    "DescribeExperimentRequestRequestTypeDef",
    "ExperimentSourceTypeDef",
    "DescribeFeatureGroupRequestRequestTypeDef",
    "LastUpdateStatusTypeDef",
    "OfflineStoreStatusTypeDef",
    "ThroughputConfigDescriptionTypeDef",
    "DescribeFeatureMetadataRequestRequestTypeDef",
    "FeatureParameterTypeDef",
    "DescribeFlowDefinitionRequestRequestTypeDef",
    "DescribeHubContentRequestRequestTypeDef",
    "HubContentDependencyTypeDef",
    "DescribeHubRequestRequestTypeDef",
    "DescribeHumanTaskUiRequestRequestTypeDef",
    "UiTemplateInfoTypeDef",
    "DescribeHyperParameterTuningJobRequestRequestTypeDef",
    "HyperParameterTuningJobCompletionDetailsTypeDef",
    "HyperParameterTuningJobConsumedResourcesTypeDef",
    "ObjectiveStatusCountersTypeDef",
    "TrainingJobStatusCountersTypeDef",
    "DescribeImageRequestRequestTypeDef",
    "DescribeImageVersionRequestRequestTypeDef",
    "DescribeInferenceComponentInputRequestTypeDef",
    "InferenceComponentRuntimeConfigSummaryTypeDef",
    "DescribeInferenceExperimentRequestRequestTypeDef",
    "EndpointMetadataTypeDef",
    "InferenceExperimentScheduleOutputTypeDef",
    "DescribeInferenceRecommendationsJobRequestRequestTypeDef",
    "DescribeLabelingJobRequestRequestTypeDef",
    "LabelCountersTypeDef",
    "LabelingJobOutputTypeDef",
    "DescribeLineageGroupRequestRequestTypeDef",
    "DescribeMlflowTrackingServerRequestRequestTypeDef",
    "DescribeModelBiasJobDefinitionRequestRequestTypeDef",
    "ModelBiasAppSpecificationOutputTypeDef",
    "DescribeModelCardExportJobRequestRequestTypeDef",
    "ModelCardExportArtifactsTypeDef",
    "DescribeModelCardRequestRequestTypeDef",
    "DescribeModelExplainabilityJobDefinitionRequestRequestTypeDef",
    "ModelExplainabilityAppSpecificationOutputTypeDef",
    "DescribeModelInputRequestTypeDef",
    "DescribeModelPackageGroupInputRequestTypeDef",
    "DescribeModelPackageInputRequestTypeDef",
    "DescribeModelQualityJobDefinitionRequestRequestTypeDef",
    "ModelQualityAppSpecificationOutputTypeDef",
    "DescribeMonitoringScheduleRequestRequestTypeDef",
    "MonitoringExecutionSummaryTypeDef",
    "DescribeNotebookInstanceInputRequestTypeDef",
    "DescribeNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "DescribeOptimizationJobRequestRequestTypeDef",
    "OptimizationOutputTypeDef",
    "OptimizationVpcConfigOutputTypeDef",
    "DescribePipelineDefinitionForExecutionRequestRequestTypeDef",
    "DescribePipelineExecutionRequestRequestTypeDef",
    "PipelineExperimentConfigTypeDef",
    "DescribePipelineRequestRequestTypeDef",
    "DescribeProcessingJobRequestRequestTypeDef",
    "DescribeProjectInputRequestTypeDef",
    "ServiceCatalogProvisionedProductDetailsTypeDef",
    "DescribeSpaceRequestRequestTypeDef",
    "DescribeStudioLifecycleConfigRequestRequestTypeDef",
    "DescribeSubscribedWorkteamRequestRequestTypeDef",
    "SubscribedWorkteamTypeDef",
    "DescribeTrainingJobRequestRequestTypeDef",
    "MetricDataTypeDef",
    "ProfilerConfigOutputTypeDef",
    "ProfilerRuleConfigurationOutputTypeDef",
    "ProfilerRuleEvaluationStatusTypeDef",
    "SecondaryStatusTransitionTypeDef",
    "WarmPoolStatusTypeDef",
    "DescribeTransformJobRequestRequestTypeDef",
    "DescribeTrialComponentRequestRequestTypeDef",
    "TrialComponentMetricSummaryTypeDef",
    "TrialComponentSourceTypeDef",
    "DescribeTrialRequestRequestTypeDef",
    "TrialSourceTypeDef",
    "DescribeUserProfileRequestRequestTypeDef",
    "DescribeWorkforceRequestRequestTypeDef",
    "DescribeWorkteamRequestRequestTypeDef",
    "ProductionVariantServerlessUpdateConfigTypeDef",
    "DeviceDeploymentSummaryTypeDef",
    "DeviceFleetSummaryTypeDef",
    "DeviceStatsTypeDef",
    "EdgeModelSummaryTypeDef",
    "DeviceTypeDef",
    "DisassociateTrialComponentRequestRequestTypeDef",
    "DockerSettingsOutputTypeDef",
    "DockerSettingsTypeDef",
    "DomainDetailsTypeDef",
    "FileSourceTypeDef",
    "EMRStepMetadataTypeDef",
    "EbsStorageSettingsTypeDef",
    "EdgeDeploymentPlanSummaryTypeDef",
    "EdgeModelStatTypeDef",
    "EdgePackagingJobSummaryTypeDef",
    "EdgeTypeDef",
    "EndpointConfigSummaryTypeDef",
    "EndpointInfoTypeDef",
    "ProductionVariantServerlessConfigTypeDef",
    "InferenceMetricsTypeDef",
    "EndpointSummaryTypeDef",
    "EnvironmentParameterTypeDef",
    "FailStepMetadataTypeDef",
    "FilterTypeDef",
    "FinalHyperParameterTuningJobObjectiveMetricTypeDef",
    "FlowDefinitionSummaryTypeDef",
    "GetDeviceFleetReportRequestRequestTypeDef",
    "GetLineageGroupPolicyRequestRequestTypeDef",
    "GetModelPackageGroupPolicyInputRequestTypeDef",
    "ScalingPolicyObjectiveTypeDef",
    "ScalingPolicyMetricTypeDef",
    "PropertyNameSuggestionTypeDef",
    "GitConfigForUpdateTypeDef",
    "HolidayConfigAttributesTypeDef",
    "HubContentInfoTypeDef",
    "HubInfoTypeDef",
    "HumanLoopActivationConditionsConfigTypeDef",
    "UiConfigTypeDef",
    "HumanTaskUiSummaryTypeDef",
    "HyperParameterTuningJobObjectiveTypeDef",
    "VpcConfigExtraOutputTypeDef",
    "HyperParameterTuningInstanceConfigTypeDef",
    "ResourceLimitsTypeDef",
    "HyperbandStrategyConfigTypeDef",
    "ParentHyperParameterTuningJobTypeDef",
    "IamIdentityTypeDef",
    "IamPolicyConstraintsTypeDef",
    "RepositoryAuthConfigTypeDef",
    "ImageTypeDef",
    "ImageVersionTypeDef",
    "InferenceComponentComputeResourceRequirementsTypeDef",
    "InferenceComponentContainerSpecificationTypeDef",
    "InferenceComponentStartupParametersTypeDef",
    "InferenceComponentSummaryTypeDef",
    "InferenceExperimentScheduleExtraOutputTypeDef",
    "InferenceHubAccessConfigTypeDef",
    "RecommendationMetricsTypeDef",
    "InferenceRecommendationsJobTypeDef",
    "InstanceGroupTypeDef",
    "IntegerParameterRangeSpecificationTypeDef",
    "IntegerParameterRangeTypeDef",
    "KernelSpecTypeDef",
    "LabelCountersForWorkteamTypeDef",
    "LabelingJobDataAttributesExtraOutputTypeDef",
    "LabelingJobDataAttributesOutputTypeDef",
    "LabelingJobDataAttributesTypeDef",
    "LabelingJobS3DataSourceTypeDef",
    "LabelingJobSnsDataSourceTypeDef",
    "LineageGroupSummaryTypeDef",
    "PaginatorConfigTypeDef",
    "ListAliasesRequestRequestTypeDef",
    "ListAppsRequestRequestTypeDef",
    "ListCandidatesForAutoMLJobRequestRequestTypeDef",
    "MonitoringJobDefinitionSummaryTypeDef",
    "ListDomainsRequestRequestTypeDef",
    "ListInferenceRecommendationsJobStepsRequestRequestTypeDef",
    "TrackingServerSummaryTypeDef",
    "ModelCardExportJobSummaryTypeDef",
    "ModelCardVersionSummaryTypeDef",
    "ModelCardSummaryTypeDef",
    "ModelMetadataSummaryTypeDef",
    "ModelPackageGroupSummaryTypeDef",
    "ModelPackageSummaryTypeDef",
    "ModelSummaryTypeDef",
    "MonitoringAlertHistorySummaryTypeDef",
    "ListMonitoringAlertsRequestRequestTypeDef",
    "MonitoringScheduleSummaryTypeDef",
    "NotebookInstanceLifecycleConfigSummaryTypeDef",
    "NotebookInstanceSummaryTypeDef",
    "OptimizationJobSummaryTypeDef",
    "ListPipelineExecutionStepsRequestRequestTypeDef",
    "PipelineExecutionSummaryTypeDef",
    "ListPipelineParametersForExecutionRequestRequestTypeDef",
    "ParameterTypeDef",
    "PipelineSummaryTypeDef",
    "ProcessingJobSummaryTypeDef",
    "ProjectSummaryTypeDef",
    "ResourceCatalogTypeDef",
    "ListSpacesRequestRequestTypeDef",
    "ListStageDevicesRequestRequestTypeDef",
    "StudioLifecycleConfigDetailsTypeDef",
    "ListSubscribedWorkteamsRequestRequestTypeDef",
    "ListTagsInputRequestTypeDef",
    "ListTrainingJobsForHyperParameterTuningJobRequestRequestTypeDef",
    "TransformJobSummaryTypeDef",
    "ListUserProfilesRequestRequestTypeDef",
    "UserProfileDetailsTypeDef",
    "ListWorkforcesRequestRequestTypeDef",
    "ListWorkteamsRequestRequestTypeDef",
    "OidcMemberDefinitionExtraOutputTypeDef",
    "OidcMemberDefinitionOutputTypeDef",
    "OidcMemberDefinitionTypeDef",
    "PredefinedMetricSpecificationTypeDef",
    "ModelAccessConfigTypeDef",
    "MonitoringGroundTruthS3InputTypeDef",
    "ModelCompilationConfigOutputTypeDef",
    "ModelCompilationConfigTypeDef",
    "ModelDashboardEndpointTypeDef",
    "ModelDashboardIndicatorActionTypeDef",
    "RealTimeInferenceConfigTypeDef",
    "ModelInputTypeDef",
    "ModelLatencyThresholdTypeDef",
    "ModelMetadataFilterTypeDef",
    "ModelPackageStatusItemTypeDef",
    "ModelQuantizationConfigOutputTypeDef",
    "ModelQuantizationConfigTypeDef",
    "ModelStepMetadataTypeDef",
    "MonitoringAppSpecificationExtraOutputTypeDef",
    "MonitoringAppSpecificationOutputTypeDef",
    "MonitoringAppSpecificationTypeDef",
    "MonitoringClusterConfigTypeDef",
    "MonitoringCsvDatasetFormatTypeDef",
    "MonitoringJsonDatasetFormatTypeDef",
    "MonitoringS3OutputTypeDef",
    "ScheduleConfigTypeDef",
    "S3StorageConfigTypeDef",
    "OidcConfigForResponseTypeDef",
    "OnlineStoreSecurityConfigTypeDef",
    "TtlDurationTypeDef",
    "OptimizationModelAccessConfigTypeDef",
    "TargetPlatformTypeDef",
    "OwnershipSettingsSummaryTypeDef",
    "ParentTypeDef",
    "ProductionVariantManagedInstanceScalingTypeDef",
    "ProductionVariantRoutingConfigTypeDef",
    "ProductionVariantStatusTypeDef",
    "PhaseTypeDef",
    "ProcessingJobStepMetadataTypeDef",
    "QualityCheckStepMetadataTypeDef",
    "RegisterModelStepMetadataTypeDef",
    "TrainingJobStepMetadataTypeDef",
    "TransformJobStepMetadataTypeDef",
    "TuningJobStepMetaDataTypeDef",
    "SelectiveExecutionResultTypeDef",
    "ProcessingClusterConfigTypeDef",
    "ProcessingFeatureStoreOutputTypeDef",
    "ProcessingS3InputTypeDef",
    "ProcessingS3OutputTypeDef",
    "ProductionVariantCoreDumpConfigTypeDef",
    "ProfilerConfigExtraOutputTypeDef",
    "ProfilerConfigForUpdateTypeDef",
    "ProfilerRuleConfigurationTypeDef",
    "PropertyNameQueryTypeDef",
    "ProvisioningParameterTypeDef",
    "USDTypeDef",
    "PutModelPackageGroupPolicyInputRequestTypeDef",
    "VertexTypeDef",
    "RStudioServerProAppSettingsTypeDef",
    "RecommendationJobCompiledOutputConfigTypeDef",
    "RecommendationJobPayloadConfigOutputTypeDef",
    "RecommendationJobPayloadConfigTypeDef",
    "RecommendationJobResourceLimitTypeDef",
    "RecommendationJobVpcConfigOutputTypeDef",
    "RecommendationJobVpcConfigTypeDef",
    "RemoteDebugConfigForUpdateTypeDef",
    "RenderableTaskTypeDef",
    "RenderingErrorTypeDef",
    "ResourceConfigForUpdateTypeDef",
    "VisibilityConditionsTypeDef",
    "SelectedStepTypeDef",
    "SendPipelineExecutionStepFailureRequestRequestTypeDef",
    "ShadowModelVariantConfigTypeDef",
    "SharingSettingsTypeDef",
    "SourceIpConfigExtraOutputTypeDef",
    "SourceIpConfigOutputTypeDef",
    "SpaceSharingSettingsSummaryTypeDef",
    "StairsTypeDef",
    "StartEdgeDeploymentStageRequestRequestTypeDef",
    "StartInferenceExperimentRequestRequestTypeDef",
    "StartMlflowTrackingServerRequestRequestTypeDef",
    "StartMonitoringScheduleRequestRequestTypeDef",
    "StartNotebookInstanceInputRequestTypeDef",
    "StopAutoMLJobRequestRequestTypeDef",
    "StopCompilationJobRequestRequestTypeDef",
    "StopEdgeDeploymentStageRequestRequestTypeDef",
    "StopEdgePackagingJobRequestRequestTypeDef",
    "StopHyperParameterTuningJobRequestRequestTypeDef",
    "StopInferenceRecommendationsJobRequestRequestTypeDef",
    "StopLabelingJobRequestRequestTypeDef",
    "StopMlflowTrackingServerRequestRequestTypeDef",
    "StopMonitoringScheduleRequestRequestTypeDef",
    "StopNotebookInstanceInputRequestTypeDef",
    "StopOptimizationJobRequestRequestTypeDef",
    "StopPipelineExecutionRequestRequestTypeDef",
    "StopProcessingJobRequestRequestTypeDef",
    "StopTrainingJobRequestRequestTypeDef",
    "StopTransformJobRequestRequestTypeDef",
    "StudioWebPortalSettingsOutputTypeDef",
    "StudioWebPortalSettingsTypeDef",
    "ThroughputConfigUpdateTypeDef",
    "TimeSeriesConfigOutputTypeDef",
    "TimeSeriesConfigTypeDef",
    "TimeSeriesTransformationsOutputTypeDef",
    "TimeSeriesTransformationsTypeDef",
    "TrainingRepositoryAuthConfigTypeDef",
    "TransformS3DataSourceTypeDef",
    "UpdateActionRequestRequestTypeDef",
    "UpdateArtifactRequestRequestTypeDef",
    "UpdateClusterSoftwareRequestRequestTypeDef",
    "UpdateContextRequestRequestTypeDef",
    "VariantPropertyTypeDef",
    "UpdateExperimentRequestRequestTypeDef",
    "UpdateHubRequestRequestTypeDef",
    "UpdateImageRequestRequestTypeDef",
    "UpdateImageVersionRequestRequestTypeDef",
    "UpdateMlflowTrackingServerRequestRequestTypeDef",
    "UpdateModelCardRequestRequestTypeDef",
    "UpdateMonitoringAlertRequestRequestTypeDef",
    "UpdateTrialRequestRequestTypeDef",
    "WorkforceVpcConfigResponseTypeDef",
    "ActionSummaryTypeDef",
    "AddAssociationResponseTypeDef",
    "AssociateTrialComponentResponseTypeDef",
    "CreateActionResponseTypeDef",
    "CreateAlgorithmOutputTypeDef",
    "CreateAppImageConfigResponseTypeDef",
    "CreateAppResponseTypeDef",
    "CreateArtifactResponseTypeDef",
    "CreateAutoMLJobResponseTypeDef",
    "CreateAutoMLJobV2ResponseTypeDef",
    "CreateClusterResponseTypeDef",
    "CreateCodeRepositoryOutputTypeDef",
    "CreateCompilationJobResponseTypeDef",
    "CreateContextResponseTypeDef",
    "CreateDataQualityJobDefinitionResponseTypeDef",
    "CreateDomainResponseTypeDef",
    "CreateEdgeDeploymentPlanResponseTypeDef",
    "CreateEndpointConfigOutputTypeDef",
    "CreateEndpointOutputTypeDef",
    "CreateExperimentResponseTypeDef",
    "CreateFeatureGroupResponseTypeDef",
    "CreateFlowDefinitionResponseTypeDef",
    "CreateHubContentReferenceResponseTypeDef",
    "CreateHubResponseTypeDef",
    "CreateHumanTaskUiResponseTypeDef",
    "CreateHyperParameterTuningJobResponseTypeDef",
    "CreateImageResponseTypeDef",
    "CreateImageVersionResponseTypeDef",
    "CreateInferenceComponentOutputTypeDef",
    "CreateInferenceExperimentResponseTypeDef",
    "CreateInferenceRecommendationsJobResponseTypeDef",
    "CreateLabelingJobResponseTypeDef",
    "CreateMlflowTrackingServerResponseTypeDef",
    "CreateModelBiasJobDefinitionResponseTypeDef",
    "CreateModelCardExportJobResponseTypeDef",
    "CreateModelCardResponseTypeDef",
    "CreateModelExplainabilityJobDefinitionResponseTypeDef",
    "CreateModelOutputTypeDef",
    "CreateModelPackageGroupOutputTypeDef",
    "CreateModelPackageOutputTypeDef",
    "CreateModelQualityJobDefinitionResponseTypeDef",
    "CreateMonitoringScheduleResponseTypeDef",
    "CreateNotebookInstanceLifecycleConfigOutputTypeDef",
    "CreateNotebookInstanceOutputTypeDef",
    "CreateOptimizationJobResponseTypeDef",
    "CreatePipelineResponseTypeDef",
    "CreatePresignedDomainUrlResponseTypeDef",
    "CreatePresignedMlflowTrackingServerUrlResponseTypeDef",
    "CreatePresignedNotebookInstanceUrlOutputTypeDef",
    "CreateProcessingJobResponseTypeDef",
    "CreateProjectOutputTypeDef",
    "CreateSpaceResponseTypeDef",
    "CreateStudioLifecycleConfigResponseTypeDef",
    "CreateTrainingJobResponseTypeDef",
    "CreateTransformJobResponseTypeDef",
    "CreateTrialComponentResponseTypeDef",
    "CreateTrialResponseTypeDef",
    "CreateUserProfileResponseTypeDef",
    "CreateWorkforceResponseTypeDef",
    "CreateWorkteamResponseTypeDef",
    "DeleteActionResponseTypeDef",
    "DeleteArtifactResponseTypeDef",
    "DeleteAssociationResponseTypeDef",
    "DeleteClusterResponseTypeDef",
    "DeleteContextResponseTypeDef",
    "DeleteExperimentResponseTypeDef",
    "DeleteInferenceExperimentResponseTypeDef",
    "DeleteMlflowTrackingServerResponseTypeDef",
    "DeletePipelineResponseTypeDef",
    "DeleteTrialComponentResponseTypeDef",
    "DeleteTrialResponseTypeDef",
    "DeleteWorkteamResponseTypeDef",
    "DescribeImageResponseTypeDef",
    "DescribeImageVersionResponseTypeDef",
    "DescribePipelineDefinitionForExecutionResponseTypeDef",
    "DescribeStudioLifecycleConfigResponseTypeDef",
    "DisassociateTrialComponentResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetLineageGroupPolicyResponseTypeDef",
    "GetModelPackageGroupPolicyOutputTypeDef",
    "GetSagemakerServicecatalogPortfolioStatusOutputTypeDef",
    "ImportHubContentResponseTypeDef",
    "ListAliasesResponseTypeDef",
    "PutModelPackageGroupPolicyOutputTypeDef",
    "RetryPipelineExecutionResponseTypeDef",
    "SendPipelineExecutionStepFailureResponseTypeDef",
    "SendPipelineExecutionStepSuccessResponseTypeDef",
    "StartInferenceExperimentResponseTypeDef",
    "StartMlflowTrackingServerResponseTypeDef",
    "StartPipelineExecutionResponseTypeDef",
    "StopInferenceExperimentResponseTypeDef",
    "StopMlflowTrackingServerResponseTypeDef",
    "StopPipelineExecutionResponseTypeDef",
    "UpdateActionResponseTypeDef",
    "UpdateAppImageConfigResponseTypeDef",
    "UpdateArtifactResponseTypeDef",
    "UpdateClusterResponseTypeDef",
    "UpdateClusterSoftwareResponseTypeDef",
    "UpdateCodeRepositoryOutputTypeDef",
    "UpdateContextResponseTypeDef",
    "UpdateDomainResponseTypeDef",
    "UpdateEndpointOutputTypeDef",
    "UpdateEndpointWeightsAndCapacitiesOutputTypeDef",
    "UpdateExperimentResponseTypeDef",
    "UpdateFeatureGroupResponseTypeDef",
    "UpdateHubResponseTypeDef",
    "UpdateImageResponseTypeDef",
    "UpdateImageVersionResponseTypeDef",
    "UpdateInferenceComponentOutputTypeDef",
    "UpdateInferenceComponentRuntimeConfigOutputTypeDef",
    "UpdateInferenceExperimentResponseTypeDef",
    "UpdateMlflowTrackingServerResponseTypeDef",
    "UpdateModelCardResponseTypeDef",
    "UpdateModelPackageOutputTypeDef",
    "UpdateMonitoringAlertResponseTypeDef",
    "UpdateMonitoringScheduleResponseTypeDef",
    "UpdatePipelineExecutionResponseTypeDef",
    "UpdatePipelineResponseTypeDef",
    "UpdateProjectOutputTypeDef",
    "UpdateSpaceResponseTypeDef",
    "UpdateTrainingJobResponseTypeDef",
    "UpdateTrialComponentResponseTypeDef",
    "UpdateTrialResponseTypeDef",
    "UpdateUserProfileResponseTypeDef",
    "AddTagsInputRequestTypeDef",
    "AddTagsOutputTypeDef",
    "CreateExperimentRequestRequestTypeDef",
    "CreateHubContentReferenceRequestRequestTypeDef",
    "CreateImageRequestRequestTypeDef",
    "CreateMlflowTrackingServerRequestRequestTypeDef",
    "CreateModelPackageGroupInputRequestTypeDef",
    "CreateStudioLifecycleConfigRequestRequestTypeDef",
    "ImportHubContentRequestRequestTypeDef",
    "ListTagsOutputTypeDef",
    "AutoRollbackConfigOutputTypeDef",
    "AutoRollbackConfigTypeDef",
    "HyperParameterAlgorithmSpecificationExtraOutputTypeDef",
    "HyperParameterAlgorithmSpecificationOutputTypeDef",
    "HyperParameterAlgorithmSpecificationTypeDef",
    "AlgorithmStatusDetailsTypeDef",
    "ListAlgorithmsOutputTypeDef",
    "AppDetailsTypeDef",
    "CreateAppRequestRequestTypeDef",
    "DescribeAppResponseTypeDef",
    "RStudioServerProDomainSettingsForUpdateTypeDef",
    "RStudioServerProDomainSettingsTypeDef",
    "SpaceCodeEditorAppSettingsTypeDef",
    "TensorBoardAppSettingsTypeDef",
    "AppSpecificationUnionTypeDef",
    "ArtifactSourceExtraOutputTypeDef",
    "ArtifactSourceOutputTypeDef",
    "ArtifactSourceTypeDef",
    "AsyncInferenceOutputConfigOutputTypeDef",
    "AsyncInferenceOutputConfigTypeDef",
    "AutoMLCandidateGenerationConfigOutputTypeDef",
    "CandidateGenerationConfigOutputTypeDef",
    "AutoMLCandidateGenerationConfigTypeDef",
    "CandidateGenerationConfigTypeDef",
    "AutoMLDataSourceTypeDef",
    "ImageClassificationJobConfigTypeDef",
    "TextClassificationJobConfigTypeDef",
    "ResolvedAttributesTypeDef",
    "AutoMLJobSummaryTypeDef",
    "AutoMLProblemTypeResolvedAttributesTypeDef",
    "AutoMLSecurityConfigOutputTypeDef",
    "LabelingJobResourceConfigOutputTypeDef",
    "MonitoringNetworkConfigOutputTypeDef",
    "NetworkConfigOutputTypeDef",
    "AutoMLSecurityConfigTypeDef",
    "LabelingJobResourceConfigTypeDef",
    "MonitoringNetworkConfigTypeDef",
    "NetworkConfigTypeDef",
    "BiasTypeDef",
    "DriftCheckModelDataQualityTypeDef",
    "DriftCheckModelQualityTypeDef",
    "ExplainabilityTypeDef",
    "ModelDataQualityTypeDef",
    "ModelQualityTypeDef",
    "CallbackStepMetadataTypeDef",
    "LambdaStepMetadataTypeDef",
    "SendPipelineExecutionStepSuccessRequestRequestTypeDef",
    "CandidatePropertiesTypeDef",
    "CanvasAppSettingsOutputTypeDef",
    "CanvasAppSettingsTypeDef",
    "RollingUpdatePolicyTypeDef",
    "TrafficRoutingConfigTypeDef",
    "InferenceExperimentDataStorageConfigOutputTypeDef",
    "InferenceExperimentDataStorageConfigTypeDef",
    "DataCaptureConfigOutputTypeDef",
    "DataCaptureConfigTypeDef",
    "EnvironmentParameterRangesOutputTypeDef",
    "EnvironmentParameterRangesTypeDef",
    "ClarifyShapConfigTypeDef",
    "ClusterInstanceStorageConfigTypeDef",
    "ClusterNodeSummaryTypeDef",
    "ListClustersResponseTypeDef",
    "CodeEditorAppImageConfigExtraOutputTypeDef",
    "JupyterLabAppImageConfigExtraOutputTypeDef",
    "CodeEditorAppImageConfigOutputTypeDef",
    "JupyterLabAppImageConfigOutputTypeDef",
    "CodeEditorAppImageConfigTypeDef",
    "JupyterLabAppImageConfigTypeDef",
    "CodeEditorAppSettingsOutputTypeDef",
    "CodeEditorAppSettingsTypeDef",
    "KernelGatewayAppSettingsOutputTypeDef",
    "KernelGatewayAppSettingsTypeDef",
    "RSessionAppSettingsOutputTypeDef",
    "RSessionAppSettingsTypeDef",
    "CodeRepositorySummaryTypeDef",
    "CreateCodeRepositoryInputRequestTypeDef",
    "DescribeCodeRepositoryOutputTypeDef",
    "JupyterLabAppSettingsOutputTypeDef",
    "JupyterLabAppSettingsTypeDef",
    "JupyterServerAppSettingsOutputTypeDef",
    "JupyterServerAppSettingsTypeDef",
    "SpaceJupyterLabAppSettingsOutputTypeDef",
    "SpaceJupyterLabAppSettingsTypeDef",
    "CollectionConfigTypeDef",
    "DebugHookConfigExtraOutputTypeDef",
    "DebugHookConfigOutputTypeDef",
    "DebugHookConfigTypeDef",
    "ListCompilationJobsResponseTypeDef",
    "ContextSummaryTypeDef",
    "CreateContextRequestRequestTypeDef",
    "TuningJobCompletionCriteriaTypeDef",
    "CreateActionRequestRequestTypeDef",
    "CreateTrialRequestRequestTypeDef",
    "CreateDeviceFleetRequestRequestTypeDef",
    "CreateEdgePackagingJobRequestRequestTypeDef",
    "DescribeDeviceFleetResponseTypeDef",
    "UpdateDeviceFleetRequestRequestTypeDef",
    "CreateHubRequestRequestTypeDef",
    "DescribeHubResponseTypeDef",
    "CreateHumanTaskUiRequestRequestTypeDef",
    "UpdateInferenceComponentRuntimeConfigInputRequestTypeDef",
    "CreateModelCardExportJobRequestRequestTypeDef",
    "CreateModelCardRequestRequestTypeDef",
    "CreateNotebookInstanceInputRequestTypeDef",
    "DescribeNotebookInstanceOutputTypeDef",
    "UpdateNotebookInstanceInputRequestTypeDef",
    "CreateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "DescribeNotebookInstanceLifecycleConfigOutputTypeDef",
    "UpdateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "RetryPipelineExecutionRequestRequestTypeDef",
    "UpdatePipelineExecutionRequestRequestTypeDef",
    "CreatePipelineRequestRequestTypeDef",
    "UpdatePipelineRequestRequestTypeDef",
    "InferenceExperimentScheduleTypeDef",
    "ListActionsRequestRequestTypeDef",
    "ListAlgorithmsInputRequestTypeDef",
    "ListAppImageConfigsRequestRequestTypeDef",
    "ListArtifactsRequestRequestTypeDef",
    "ListAssociationsRequestRequestTypeDef",
    "ListAutoMLJobsRequestRequestTypeDef",
    "ListClusterNodesRequestRequestTypeDef",
    "ListClustersRequestRequestTypeDef",
    "ListCodeRepositoriesInputRequestTypeDef",
    "ListCompilationJobsRequestRequestTypeDef",
    "ListContextsRequestRequestTypeDef",
    "ListDataQualityJobDefinitionsRequestRequestTypeDef",
    "ListDeviceFleetsRequestRequestTypeDef",
    "ListDevicesRequestRequestTypeDef",
    "ListEdgeDeploymentPlansRequestRequestTypeDef",
    "ListEdgePackagingJobsRequestRequestTypeDef",
    "ListEndpointConfigsInputRequestTypeDef",
    "ListEndpointsInputRequestTypeDef",
    "ListExperimentsRequestRequestTypeDef",
    "ListFeatureGroupsRequestRequestTypeDef",
    "ListFlowDefinitionsRequestRequestTypeDef",
    "ListHubContentVersionsRequestRequestTypeDef",
    "ListHubContentsRequestRequestTypeDef",
    "ListHubsRequestRequestTypeDef",
    "ListHumanTaskUisRequestRequestTypeDef",
    "ListHyperParameterTuningJobsRequestRequestTypeDef",
    "ListImageVersionsRequestRequestTypeDef",
    "ListImagesRequestRequestTypeDef",
    "ListInferenceComponentsInputRequestTypeDef",
    "ListInferenceExperimentsRequestRequestTypeDef",
    "ListInferenceRecommendationsJobsRequestRequestTypeDef",
    "ListLabelingJobsForWorkteamRequestRequestTypeDef",
    "ListLabelingJobsRequestRequestTypeDef",
    "ListLineageGroupsRequestRequestTypeDef",
    "ListMlflowTrackingServersRequestRequestTypeDef",
    "ListModelBiasJobDefinitionsRequestRequestTypeDef",
    "ListModelCardExportJobsRequestRequestTypeDef",
    "ListModelCardVersionsRequestRequestTypeDef",
    "ListModelCardsRequestRequestTypeDef",
    "ListModelExplainabilityJobDefinitionsRequestRequestTypeDef",
    "ListModelPackageGroupsInputRequestTypeDef",
    "ListModelPackagesInputRequestTypeDef",
    "ListModelQualityJobDefinitionsRequestRequestTypeDef",
    "ListModelsInputRequestTypeDef",
    "ListMonitoringAlertHistoryRequestRequestTypeDef",
    "ListMonitoringExecutionsRequestRequestTypeDef",
    "ListMonitoringSchedulesRequestRequestTypeDef",
    "ListNotebookInstanceLifecycleConfigsInputRequestTypeDef",
    "ListNotebookInstancesInputRequestTypeDef",
    "ListOptimizationJobsRequestRequestTypeDef",
    "ListPipelineExecutionsRequestRequestTypeDef",
    "ListPipelinesRequestRequestTypeDef",
    "ListProcessingJobsRequestRequestTypeDef",
    "ListProjectsInputRequestTypeDef",
    "ListResourceCatalogsRequestRequestTypeDef",
    "ListStudioLifecycleConfigsRequestRequestTypeDef",
    "ListTrainingJobsRequestRequestTypeDef",
    "ListTransformJobsRequestRequestTypeDef",
    "ListTrialComponentsRequestRequestTypeDef",
    "ListTrialsRequestRequestTypeDef",
    "QueryFiltersTypeDef",
    "CreateTrialComponentRequestRequestTypeDef",
    "UpdateTrialComponentRequestRequestTypeDef",
    "CreateWorkforceRequestRequestTypeDef",
    "UpdateWorkforceRequestRequestTypeDef",
    "CustomFileSystemConfigTypeDef",
    "CustomFileSystemTypeDef",
    "DataQualityAppSpecificationUnionTypeDef",
    "ModelBiasBaselineConfigTypeDef",
    "ModelExplainabilityBaselineConfigTypeDef",
    "ModelQualityBaselineConfigTypeDef",
    "DataQualityBaselineConfigTypeDef",
    "MonitoringBaselineConfigTypeDef",
    "DataSourceExtraOutputTypeDef",
    "DataSourceOutputTypeDef",
    "DataSourceTypeDef",
    "DatasetDefinitionTypeDef",
    "DebugRuleConfigurationUnionTypeDef",
    "DefaultSpaceStorageSettingsTypeDef",
    "DeleteDomainRequestRequestTypeDef",
    "InferenceComponentContainerSpecificationSummaryTypeDef",
    "DeploymentRecommendationTypeDef",
    "DeploymentStageStatusSummaryTypeDef",
    "DeploymentStageTypeDef",
    "NeoVpcConfigUnionTypeDef",
    "DescribeDeviceResponseTypeDef",
    "DescribeEdgePackagingJobResponseTypeDef",
    "DescribeEndpointInputEndpointDeletedWaitTypeDef",
    "DescribeEndpointInputEndpointInServiceWaitTypeDef",
    "DescribeImageRequestImageCreatedWaitTypeDef",
    "DescribeImageRequestImageDeletedWaitTypeDef",
    "DescribeImageRequestImageUpdatedWaitTypeDef",
    "DescribeImageVersionRequestImageVersionCreatedWaitTypeDef",
    "DescribeImageVersionRequestImageVersionDeletedWaitTypeDef",
    "DescribeNotebookInstanceInputNotebookInstanceDeletedWaitTypeDef",
    "DescribeNotebookInstanceInputNotebookInstanceInServiceWaitTypeDef",
    "DescribeNotebookInstanceInputNotebookInstanceStoppedWaitTypeDef",
    "DescribeProcessingJobRequestProcessingJobCompletedOrStoppedWaitTypeDef",
    "DescribeTrainingJobRequestTrainingJobCompletedOrStoppedWaitTypeDef",
    "DescribeTransformJobRequestTransformJobCompletedOrStoppedWaitTypeDef",
    "ExperimentSummaryTypeDef",
    "FeatureGroupSummaryTypeDef",
    "DescribeFeatureMetadataResponseTypeDef",
    "FeatureMetadataTypeDef",
    "UpdateFeatureMetadataRequestRequestTypeDef",
    "DescribeHubContentResponseTypeDef",
    "DescribeHumanTaskUiResponseTypeDef",
    "InferenceExperimentSummaryTypeDef",
    "ModelBiasAppSpecificationUnionTypeDef",
    "DescribeModelCardExportJobResponseTypeDef",
    "ModelExplainabilityAppSpecificationUnionTypeDef",
    "ModelQualityAppSpecificationUnionTypeDef",
    "ListMonitoringExecutionsResponseTypeDef",
    "OptimizationVpcConfigUnionTypeDef",
    "DescribeSubscribedWorkteamResponseTypeDef",
    "ListSubscribedWorkteamsResponseTypeDef",
    "TrainingJobSummaryTypeDef",
    "TrialSummaryTypeDef",
    "DesiredWeightAndCapacityTypeDef",
    "ListStageDevicesResponseTypeDef",
    "ListDeviceFleetsResponseTypeDef",
    "DeviceSummaryTypeDef",
    "RegisterDevicesRequestRequestTypeDef",
    "UpdateDevicesRequestRequestTypeDef",
    "ListDomainsResponseTypeDef",
    "DriftCheckBiasTypeDef",
    "DriftCheckExplainabilityTypeDef",
    "SpaceStorageSettingsTypeDef",
    "ListEdgeDeploymentPlansResponseTypeDef",
    "GetDeviceFleetReportResponseTypeDef",
    "ListEdgePackagingJobsResponseTypeDef",
    "ListEndpointConfigsOutputTypeDef",
    "EndpointOutputConfigurationTypeDef",
    "EndpointPerformanceTypeDef",
    "ListEndpointsOutputTypeDef",
    "ModelConfigurationTypeDef",
    "NestedFiltersTypeDef",
    "HyperParameterTrainingJobSummaryTypeDef",
    "ListFlowDefinitionsResponseTypeDef",
    "GetScalingConfigurationRecommendationRequestRequestTypeDef",
    "GetSearchSuggestionsResponseTypeDef",
    "UpdateCodeRepositoryInputRequestTypeDef",
    "ListHubContentVersionsResponseTypeDef",
    "ListHubContentsResponseTypeDef",
    "ListHubsResponseTypeDef",
    "HumanLoopActivationConfigTypeDef",
    "ListHumanTaskUisResponseTypeDef",
    "NetworkConfigExtraOutputTypeDef",
    "VpcConfigUnionTypeDef",
    "HyperParameterTuningResourceConfigExtraOutputTypeDef",
    "HyperParameterTuningResourceConfigOutputTypeDef",
    "HyperParameterTuningResourceConfigTypeDef",
    "HyperParameterTuningJobSummaryTypeDef",
    "HyperParameterTuningJobStrategyConfigTypeDef",
    "HyperParameterTuningJobWarmStartConfigExtraOutputTypeDef",
    "HyperParameterTuningJobWarmStartConfigOutputTypeDef",
    "HyperParameterTuningJobWarmStartConfigTypeDef",
    "UserContextTypeDef",
    "S3PresignTypeDef",
    "ImageConfigTypeDef",
    "ListImagesResponseTypeDef",
    "ListImageVersionsResponseTypeDef",
    "InferenceComponentSpecificationTypeDef",
    "ListInferenceComponentsOutputTypeDef",
    "ListInferenceRecommendationsJobsResponseTypeDef",
    "ResourceConfigExtraOutputTypeDef",
    "ResourceConfigOutputTypeDef",
    "ResourceConfigTypeDef",
    "ParameterRangeOutputTypeDef",
    "ParameterRangeTypeDef",
    "ParameterRangesExtraOutputTypeDef",
    "ParameterRangesOutputTypeDef",
    "ParameterRangesTypeDef",
    "KernelGatewayImageConfigExtraOutputTypeDef",
    "KernelGatewayImageConfigOutputTypeDef",
    "KernelGatewayImageConfigTypeDef",
    "LabelingJobForWorkteamSummaryTypeDef",
    "LabelingJobDataSourceTypeDef",
    "ListLineageGroupsResponseTypeDef",
    "ListActionsRequestListActionsPaginateTypeDef",
    "ListAlgorithmsInputListAlgorithmsPaginateTypeDef",
    "ListAliasesRequestListAliasesPaginateTypeDef",
    "ListAppImageConfigsRequestListAppImageConfigsPaginateTypeDef",
    "ListAppsRequestListAppsPaginateTypeDef",
    "ListArtifactsRequestListArtifactsPaginateTypeDef",
    "ListAssociationsRequestListAssociationsPaginateTypeDef",
    "ListAutoMLJobsRequestListAutoMLJobsPaginateTypeDef",
    "ListCandidatesForAutoMLJobRequestListCandidatesForAutoMLJobPaginateTypeDef",
    "ListClusterNodesRequestListClusterNodesPaginateTypeDef",
    "ListClustersRequestListClustersPaginateTypeDef",
    "ListCodeRepositoriesInputListCodeRepositoriesPaginateTypeDef",
    "ListCompilationJobsRequestListCompilationJobsPaginateTypeDef",
    "ListContextsRequestListContextsPaginateTypeDef",
    "ListDataQualityJobDefinitionsRequestListDataQualityJobDefinitionsPaginateTypeDef",
    "ListDeviceFleetsRequestListDeviceFleetsPaginateTypeDef",
    "ListDevicesRequestListDevicesPaginateTypeDef",
    "ListDomainsRequestListDomainsPaginateTypeDef",
    "ListEdgeDeploymentPlansRequestListEdgeDeploymentPlansPaginateTypeDef",
    "ListEdgePackagingJobsRequestListEdgePackagingJobsPaginateTypeDef",
    "ListEndpointConfigsInputListEndpointConfigsPaginateTypeDef",
    "ListEndpointsInputListEndpointsPaginateTypeDef",
    "ListExperimentsRequestListExperimentsPaginateTypeDef",
    "ListFeatureGroupsRequestListFeatureGroupsPaginateTypeDef",
    "ListFlowDefinitionsRequestListFlowDefinitionsPaginateTypeDef",
    "ListHumanTaskUisRequestListHumanTaskUisPaginateTypeDef",
    "ListHyperParameterTuningJobsRequestListHyperParameterTuningJobsPaginateTypeDef",
    "ListImageVersionsRequestListImageVersionsPaginateTypeDef",
    "ListImagesRequestListImagesPaginateTypeDef",
    "ListInferenceComponentsInputListInferenceComponentsPaginateTypeDef",
    "ListInferenceExperimentsRequestListInferenceExperimentsPaginateTypeDef",
    "ListInferenceRecommendationsJobStepsRequestListInferenceRecommendationsJobStepsPaginateTypeDef",
    "ListInferenceRecommendationsJobsRequestListInferenceRecommendationsJobsPaginateTypeDef",
    "ListLabelingJobsForWorkteamRequestListLabelingJobsForWorkteamPaginateTypeDef",
    "ListLabelingJobsRequestListLabelingJobsPaginateTypeDef",
    "ListLineageGroupsRequestListLineageGroupsPaginateTypeDef",
    "ListMlflowTrackingServersRequestListMlflowTrackingServersPaginateTypeDef",
    "ListModelBiasJobDefinitionsRequestListModelBiasJobDefinitionsPaginateTypeDef",
    "ListModelCardExportJobsRequestListModelCardExportJobsPaginateTypeDef",
    "ListModelCardVersionsRequestListModelCardVersionsPaginateTypeDef",
    "ListModelCardsRequestListModelCardsPaginateTypeDef",
    "ListModelExplainabilityJobDefinitionsRequestListModelExplainabilityJobDefinitionsPaginateTypeDef",
    "ListModelPackageGroupsInputListModelPackageGroupsPaginateTypeDef",
    "ListModelPackagesInputListModelPackagesPaginateTypeDef",
    "ListModelQualityJobDefinitionsRequestListModelQualityJobDefinitionsPaginateTypeDef",
    "ListModelsInputListModelsPaginateTypeDef",
    "ListMonitoringAlertHistoryRequestListMonitoringAlertHistoryPaginateTypeDef",
    "ListMonitoringAlertsRequestListMonitoringAlertsPaginateTypeDef",
    "ListMonitoringExecutionsRequestListMonitoringExecutionsPaginateTypeDef",
    "ListMonitoringSchedulesRequestListMonitoringSchedulesPaginateTypeDef",
    "ListNotebookInstanceLifecycleConfigsInputListNotebookInstanceLifecycleConfigsPaginateTypeDef",
    "ListNotebookInstancesInputListNotebookInstancesPaginateTypeDef",
    "ListOptimizationJobsRequestListOptimizationJobsPaginateTypeDef",
    "ListPipelineExecutionStepsRequestListPipelineExecutionStepsPaginateTypeDef",
    "ListPipelineExecutionsRequestListPipelineExecutionsPaginateTypeDef",
    "ListPipelineParametersForExecutionRequestListPipelineParametersForExecutionPaginateTypeDef",
    "ListPipelinesRequestListPipelinesPaginateTypeDef",
    "ListProcessingJobsRequestListProcessingJobsPaginateTypeDef",
    "ListResourceCatalogsRequestListResourceCatalogsPaginateTypeDef",
    "ListSpacesRequestListSpacesPaginateTypeDef",
    "ListStageDevicesRequestListStageDevicesPaginateTypeDef",
    "ListStudioLifecycleConfigsRequestListStudioLifecycleConfigsPaginateTypeDef",
    "ListSubscribedWorkteamsRequestListSubscribedWorkteamsPaginateTypeDef",
    "ListTagsInputListTagsPaginateTypeDef",
    "ListTrainingJobsForHyperParameterTuningJobRequestListTrainingJobsForHyperParameterTuningJobPaginateTypeDef",
    "ListTrainingJobsRequestListTrainingJobsPaginateTypeDef",
    "ListTransformJobsRequestListTransformJobsPaginateTypeDef",
    "ListTrialComponentsRequestListTrialComponentsPaginateTypeDef",
    "ListTrialsRequestListTrialsPaginateTypeDef",
    "ListUserProfilesRequestListUserProfilesPaginateTypeDef",
    "ListWorkforcesRequestListWorkforcesPaginateTypeDef",
    "ListWorkteamsRequestListWorkteamsPaginateTypeDef",
    "ListDataQualityJobDefinitionsResponseTypeDef",
    "ListModelBiasJobDefinitionsResponseTypeDef",
    "ListModelExplainabilityJobDefinitionsResponseTypeDef",
    "ListModelQualityJobDefinitionsResponseTypeDef",
    "ListMlflowTrackingServersResponseTypeDef",
    "ListModelCardExportJobsResponseTypeDef",
    "ListModelCardVersionsResponseTypeDef",
    "ListModelCardsResponseTypeDef",
    "ListModelMetadataResponseTypeDef",
    "ListModelPackageGroupsOutputTypeDef",
    "ListModelPackagesOutputTypeDef",
    "ListModelsOutputTypeDef",
    "ListMonitoringAlertHistoryResponseTypeDef",
    "ListMonitoringSchedulesResponseTypeDef",
    "ListNotebookInstanceLifecycleConfigsOutputTypeDef",
    "ListNotebookInstancesOutputTypeDef",
    "ListOptimizationJobsResponseTypeDef",
    "ListPipelineExecutionsResponseTypeDef",
    "ListPipelineParametersForExecutionResponseTypeDef",
    "ListPipelinesResponseTypeDef",
    "ListProcessingJobsResponseTypeDef",
    "ListProjectsOutputTypeDef",
    "ListResourceCatalogsResponseTypeDef",
    "ListStudioLifecycleConfigsResponseTypeDef",
    "ListTransformJobsResponseTypeDef",
    "ListUserProfilesResponseTypeDef",
    "MemberDefinitionExtraOutputTypeDef",
    "MemberDefinitionOutputTypeDef",
    "MemberDefinitionTypeDef",
    "MetricSpecificationTypeDef",
    "S3ModelDataSourceTypeDef",
    "TextGenerationJobConfigOutputTypeDef",
    "TextGenerationJobConfigTypeDef",
    "MonitoringAlertActionsTypeDef",
    "ModelInfrastructureConfigTypeDef",
    "RecommendationJobStoppingConditionsOutputTypeDef",
    "RecommendationJobStoppingConditionsTypeDef",
    "ModelMetadataSearchExpressionTypeDef",
    "ModelPackageStatusDetailsTypeDef",
    "OptimizationConfigOutputTypeDef",
    "OptimizationConfigTypeDef",
    "MonitoringResourcesTypeDef",
    "MonitoringDatasetFormatExtraOutputTypeDef",
    "MonitoringDatasetFormatOutputTypeDef",
    "MonitoringDatasetFormatTypeDef",
    "MonitoringOutputTypeDef",
    "OfflineStoreConfigTypeDef",
    "OnlineStoreConfigTypeDef",
    "OnlineStoreConfigUpdateTypeDef",
    "OptimizationJobModelSourceS3TypeDef",
    "OutputConfigTypeDef",
    "PendingProductionVariantSummaryTypeDef",
    "ProductionVariantSummaryTypeDef",
    "ProcessingResourcesTypeDef",
    "ProcessingOutputTypeDef",
    "ProductionVariantTypeDef",
    "ProfilerConfigUnionTypeDef",
    "ProfilerRuleConfigurationUnionTypeDef",
    "SuggestionQueryTypeDef",
    "ServiceCatalogProvisioningDetailsExtraOutputTypeDef",
    "ServiceCatalogProvisioningDetailsOutputTypeDef",
    "ServiceCatalogProvisioningDetailsTypeDef",
    "ServiceCatalogProvisioningUpdateDetailsTypeDef",
    "PublicWorkforceTaskPriceTypeDef",
    "QueryLineageResponseTypeDef",
    "RecommendationJobOutputConfigTypeDef",
    "RecommendationJobContainerConfigOutputTypeDef",
    "RecommendationJobContainerConfigTypeDef",
    "RenderUiTemplateRequestRequestTypeDef",
    "RenderUiTemplateResponseTypeDef",
    "SearchRequestRequestTypeDef",
    "SelectiveExecutionConfigExtraOutputTypeDef",
    "SelectiveExecutionConfigOutputTypeDef",
    "SelectiveExecutionConfigTypeDef",
    "ShadowModeConfigOutputTypeDef",
    "ShadowModeConfigTypeDef",
    "SourceIpConfigUnionTypeDef",
    "TrafficPatternOutputTypeDef",
    "TrafficPatternTypeDef",
    "TrainingImageConfigTypeDef",
    "TransformDataSourceTypeDef",
    "WorkforceTypeDef",
    "ListActionsResponseTypeDef",
    "ListAppsResponseTypeDef",
    "DomainSettingsForUpdateTypeDef",
    "DomainSettingsOutputTypeDef",
    "DomainSettingsTypeDef",
    "ArtifactSummaryTypeDef",
    "ArtifactSourceUnionTypeDef",
    "CreateArtifactRequestRequestTypeDef",
    "DeleteArtifactRequestRequestTypeDef",
    "AsyncInferenceConfigOutputTypeDef",
    "AsyncInferenceConfigTypeDef",
    "TabularJobConfigOutputTypeDef",
    "TimeSeriesForecastingJobConfigOutputTypeDef",
    "TabularJobConfigTypeDef",
    "TimeSeriesForecastingJobConfigTypeDef",
    "AutoMLChannelTypeDef",
    "AutoMLJobChannelTypeDef",
    "ListAutoMLJobsResponseTypeDef",
    "AutoMLResolvedAttributesTypeDef",
    "AutoMLJobConfigOutputTypeDef",
    "LabelingJobAlgorithmsConfigOutputTypeDef",
    "AutoMLJobConfigTypeDef",
    "AutoMLSecurityConfigUnionTypeDef",
    "LabelingJobAlgorithmsConfigTypeDef",
    "MonitoringNetworkConfigUnionTypeDef",
    "ModelMetricsTypeDef",
    "PipelineExecutionStepMetadataTypeDef",
    "AutoMLCandidateTypeDef",
    "BlueGreenUpdatePolicyTypeDef",
    "InferenceExperimentDataStorageConfigUnionTypeDef",
    "DataCaptureConfigUnionTypeDef",
    "EndpointInputConfigurationOutputTypeDef",
    "EndpointInputConfigurationTypeDef",
    "ClarifyExplainerConfigOutputTypeDef",
    "ClarifyExplainerConfigTypeDef",
    "ClusterInstanceGroupDetailsTypeDef",
    "ClusterInstanceGroupSpecificationTypeDef",
    "ClusterNodeDetailsTypeDef",
    "ListClusterNodesResponseTypeDef",
    "CodeEditorAppImageConfigUnionTypeDef",
    "JupyterLabAppImageConfigUnionTypeDef",
    "ListCodeRepositoriesOutputTypeDef",
    "FeatureDefinitionTypeDef",
    "DebugHookConfigUnionTypeDef",
    "ListContextsResponseTypeDef",
    "InferenceExperimentScheduleUnionTypeDef",
    "QueryLineageRequestRequestTypeDef",
    "ChannelExtraOutputTypeDef",
    "ChannelOutputTypeDef",
    "ChannelTypeDef",
    "ProcessingInputTypeDef",
    "DefaultSpaceSettingsOutputTypeDef",
    "DefaultSpaceSettingsTypeDef",
    "UserSettingsOutputTypeDef",
    "UserSettingsTypeDef",
    "InferenceComponentSpecificationSummaryTypeDef",
    "DescribeEdgeDeploymentPlanResponseTypeDef",
    "CreateEdgeDeploymentPlanRequestRequestTypeDef",
    "CreateEdgeDeploymentStageRequestRequestTypeDef",
    "ListExperimentsResponseTypeDef",
    "ListFeatureGroupsResponseTypeDef",
    "ListInferenceExperimentsResponseTypeDef",
    "ListTrainingJobsResponseTypeDef",
    "ListTrialsResponseTypeDef",
    "UpdateEndpointWeightsAndCapacitiesInputRequestTypeDef",
    "ListDevicesResponseTypeDef",
    "DriftCheckBaselinesTypeDef",
    "SpaceSettingsOutputTypeDef",
    "SpaceSettingsSummaryTypeDef",
    "SpaceSettingsTypeDef",
    "InferenceRecommendationTypeDef",
    "RecommendationJobInferenceBenchmarkTypeDef",
    "SearchExpressionTypeDef",
    "ListTrainingJobsForHyperParameterTuningJobResponseTypeDef",
    "NetworkConfigUnionTypeDef",
    "ListHyperParameterTuningJobsResponseTypeDef",
    "HyperParameterTuningJobWarmStartConfigUnionTypeDef",
    "AssociationSummaryTypeDef",
    "DescribeActionResponseTypeDef",
    "DescribeArtifactResponseTypeDef",
    "DescribeContextResponseTypeDef",
    "DescribeExperimentResponseTypeDef",
    "DescribeLineageGroupResponseTypeDef",
    "DescribeMlflowTrackingServerResponseTypeDef",
    "DescribeModelCardResponseTypeDef",
    "DescribeModelPackageGroupOutputTypeDef",
    "DescribePipelineResponseTypeDef",
    "DescribeTrialComponentResponseTypeDef",
    "DescribeTrialResponseTypeDef",
    "ExperimentTypeDef",
    "ModelCardTypeDef",
    "ModelDashboardModelCardTypeDef",
    "ModelPackageGroupTypeDef",
    "PipelineTypeDef",
    "TrialComponentSimpleSummaryTypeDef",
    "TrialComponentSummaryTypeDef",
    "WorkerAccessConfigurationTypeDef",
    "CreateInferenceComponentInputRequestTypeDef",
    "UpdateInferenceComponentInputRequestTypeDef",
    "ResourceConfigUnionTypeDef",
    "HyperParameterSpecificationOutputTypeDef",
    "HyperParameterSpecificationTypeDef",
    "HyperParameterTuningJobConfigExtraOutputTypeDef",
    "HyperParameterTuningJobConfigOutputTypeDef",
    "HyperParameterTuningJobConfigTypeDef",
    "AppImageConfigDetailsTypeDef",
    "DescribeAppImageConfigResponseTypeDef",
    "CreateAppImageConfigRequestRequestTypeDef",
    "KernelGatewayImageConfigUnionTypeDef",
    "UpdateAppImageConfigRequestRequestTypeDef",
    "ListLabelingJobsForWorkteamResponseTypeDef",
    "LabelingJobInputConfigExtraOutputTypeDef",
    "LabelingJobInputConfigOutputTypeDef",
    "LabelingJobInputConfigTypeDef",
    "MemberDefinitionUnionTypeDef",
    "TargetTrackingScalingPolicyConfigurationTypeDef",
    "AdditionalModelDataSourceTypeDef",
    "ModelDataSourceTypeDef",
    "MonitoringAlertSummaryTypeDef",
    "ModelVariantConfigSummaryTypeDef",
    "ModelVariantConfigTypeDef",
    "RecommendationJobStoppingConditionsUnionTypeDef",
    "ListModelMetadataRequestListModelMetadataPaginateTypeDef",
    "ListModelMetadataRequestRequestTypeDef",
    "OptimizationConfigUnionTypeDef",
    "BatchTransformInputExtraOutputTypeDef",
    "BatchTransformInputOutputTypeDef",
    "BatchTransformInputTypeDef",
    "MonitoringOutputConfigExtraOutputTypeDef",
    "MonitoringOutputConfigOutputTypeDef",
    "MonitoringOutputConfigTypeDef",
    "OptimizationJobModelSourceTypeDef",
    "CreateCompilationJobRequestRequestTypeDef",
    "DescribeCompilationJobResponseTypeDef",
    "PendingDeploymentSummaryTypeDef",
    "ProcessingOutputConfigExtraOutputTypeDef",
    "ProcessingOutputConfigOutputTypeDef",
    "ProcessingOutputConfigTypeDef",
    "UpdateTrainingJobRequestRequestTypeDef",
    "GetSearchSuggestionsRequestRequestTypeDef",
    "DescribeProjectOutputTypeDef",
    "ProjectTypeDef",
    "CreateProjectInputRequestTypeDef",
    "ServiceCatalogProvisioningDetailsUnionTypeDef",
    "UpdateProjectInputRequestTypeDef",
    "HumanLoopConfigOutputTypeDef",
    "HumanLoopConfigTypeDef",
    "HumanTaskConfigOutputTypeDef",
    "HumanTaskConfigTypeDef",
    "DescribePipelineExecutionResponseTypeDef",
    "PipelineExecutionTypeDef",
    "SelectiveExecutionConfigUnionTypeDef",
    "StartPipelineExecutionRequestRequestTypeDef",
    "ShadowModeConfigUnionTypeDef",
    "AlgorithmSpecificationExtraOutputTypeDef",
    "AlgorithmSpecificationOutputTypeDef",
    "AlgorithmSpecificationTypeDef",
    "TransformInputTypeDef",
    "DescribeWorkforceResponseTypeDef",
    "ListWorkforcesResponseTypeDef",
    "UpdateWorkforceResponseTypeDef",
    "DomainSettingsUnionTypeDef",
    "ListArtifactsResponseTypeDef",
    "AsyncInferenceConfigUnionTypeDef",
    "AutoMLProblemTypeConfigOutputTypeDef",
    "AutoMLProblemTypeConfigTypeDef",
    "AutoMLJobConfigUnionTypeDef",
    "CreateAutoMLJobRequestRequestTypeDef",
    "LabelingJobAlgorithmsConfigUnionTypeDef",
    "PipelineExecutionStepTypeDef",
    "DescribeAutoMLJobResponseTypeDef",
    "ListCandidatesForAutoMLJobResponseTypeDef",
    "DeploymentConfigOutputTypeDef",
    "DeploymentConfigTypeDef",
    "RecommendationJobInputConfigOutputTypeDef",
    "RecommendationJobInputConfigTypeDef",
    "ExplainerConfigOutputTypeDef",
    "ExplainerConfigTypeDef",
    "DescribeClusterResponseTypeDef",
    "CreateClusterRequestRequestTypeDef",
    "UpdateClusterRequestRequestTypeDef",
    "DescribeClusterNodeResponseTypeDef",
    "CreateFeatureGroupRequestRequestTypeDef",
    "DescribeFeatureGroupResponseTypeDef",
    "FeatureGroupTypeDef",
    "UpdateFeatureGroupRequestRequestTypeDef",
    "HyperParameterTrainingJobDefinitionExtraOutputTypeDef",
    "HyperParameterTrainingJobDefinitionOutputTypeDef",
    "TrainingJobDefinitionOutputTypeDef",
    "ChannelUnionTypeDef",
    "HyperParameterTrainingJobDefinitionTypeDef",
    "TrainingJobDefinitionTypeDef",
    "DefaultSpaceSettingsUnionTypeDef",
    "DescribeDomainResponseTypeDef",
    "DescribeUserProfileResponseTypeDef",
    "CreateDomainRequestRequestTypeDef",
    "CreateUserProfileRequestRequestTypeDef",
    "UpdateDomainRequestRequestTypeDef",
    "UpdateUserProfileRequestRequestTypeDef",
    "UserSettingsUnionTypeDef",
    "DescribeInferenceComponentOutputTypeDef",
    "DescribeSpaceResponseTypeDef",
    "SpaceDetailsTypeDef",
    "CreateSpaceRequestRequestTypeDef",
    "SpaceSettingsUnionTypeDef",
    "UpdateSpaceRequestRequestTypeDef",
    "InferenceRecommendationsJobStepTypeDef",
    "SearchRequestSearchPaginateTypeDef",
    "ListAssociationsResponseTypeDef",
    "TrialTypeDef",
    "ListTrialComponentsResponseTypeDef",
    "WorkteamTypeDef",
    "TrainingSpecificationOutputTypeDef",
    "TrainingSpecificationTypeDef",
    "HyperParameterTuningJobConfigUnionTypeDef",
    "ListAppImageConfigsResponseTypeDef",
    "LabelingJobSummaryTypeDef",
    "LabelingJobInputConfigUnionTypeDef",
    "CreateWorkteamRequestRequestTypeDef",
    "UpdateWorkteamRequestRequestTypeDef",
    "ScalingPolicyTypeDef",
    "ContainerDefinitionExtraOutputTypeDef",
    "ContainerDefinitionOutputTypeDef",
    "ContainerDefinitionTypeDef",
    "ModelPackageContainerDefinitionExtraOutputTypeDef",
    "ModelPackageContainerDefinitionOutputTypeDef",
    "ModelPackageContainerDefinitionTypeDef",
    "SourceAlgorithmTypeDef",
    "ListMonitoringAlertsResponseTypeDef",
    "DescribeInferenceExperimentResponseTypeDef",
    "CreateInferenceExperimentRequestRequestTypeDef",
    "StopInferenceExperimentRequestRequestTypeDef",
    "UpdateInferenceExperimentRequestRequestTypeDef",
    "MonitoringInputExtraOutputTypeDef",
    "DataQualityJobInputOutputTypeDef",
    "ModelBiasJobInputOutputTypeDef",
    "ModelExplainabilityJobInputOutputTypeDef",
    "ModelQualityJobInputOutputTypeDef",
    "MonitoringInputOutputTypeDef",
    "DataQualityJobInputTypeDef",
    "ModelBiasJobInputTypeDef",
    "ModelExplainabilityJobInputTypeDef",
    "ModelQualityJobInputTypeDef",
    "MonitoringInputTypeDef",
    "MonitoringOutputConfigUnionTypeDef",
    "CreateOptimizationJobRequestRequestTypeDef",
    "DescribeOptimizationJobResponseTypeDef",
    "DescribeProcessingJobResponseTypeDef",
    "ProcessingJobTypeDef",
    "CreateProcessingJobRequestRequestTypeDef",
    "ProcessingOutputConfigUnionTypeDef",
    "DescribeFlowDefinitionResponseTypeDef",
    "CreateFlowDefinitionRequestRequestTypeDef",
    "HumanLoopConfigUnionTypeDef",
    "DescribeLabelingJobResponseTypeDef",
    "CreateLabelingJobRequestRequestTypeDef",
    "HumanTaskConfigUnionTypeDef",
    "DescribeTrainingJobResponseTypeDef",
    "TrainingJobTypeDef",
    "AlgorithmSpecificationUnionTypeDef",
    "CreateTransformJobRequestRequestTypeDef",
    "DescribeTransformJobResponseTypeDef",
    "TransformJobDefinitionExtraOutputTypeDef",
    "TransformJobDefinitionOutputTypeDef",
    "TransformJobDefinitionTypeDef",
    "TransformJobTypeDef",
    "DescribeAutoMLJobV2ResponseTypeDef",
    "AutoMLProblemTypeConfigUnionTypeDef",
    "CreateAutoMLJobV2RequestRequestTypeDef",
    "ListPipelineExecutionStepsResponseTypeDef",
    "CreateEndpointInputRequestTypeDef",
    "DeploymentConfigUnionTypeDef",
    "UpdateEndpointInputRequestTypeDef",
    "DescribeInferenceRecommendationsJobResponseTypeDef",
    "CreateInferenceRecommendationsJobRequestRequestTypeDef",
    "RecommendationJobInputConfigUnionTypeDef",
    "DescribeEndpointConfigOutputTypeDef",
    "DescribeEndpointOutputTypeDef",
    "CreateEndpointConfigInputRequestTypeDef",
    "ExplainerConfigUnionTypeDef",
    "DescribeHyperParameterTuningJobResponseTypeDef",
    "HyperParameterTuningJobSearchEntityTypeDef",
    "CreateTrainingJobRequestRequestTypeDef",
    "HyperParameterTrainingJobDefinitionUnionTypeDef",
    "ListSpacesResponseTypeDef",
    "ListInferenceRecommendationsJobStepsResponseTypeDef",
    "DescribeWorkteamResponseTypeDef",
    "ListWorkteamsResponseTypeDef",
    "UpdateWorkteamResponseTypeDef",
    "TrainingSpecificationUnionTypeDef",
    "ListLabelingJobsResponseTypeDef",
    "DynamicScalingConfigurationTypeDef",
    "DescribeModelOutputTypeDef",
    "ModelTypeDef",
    "ContainerDefinitionUnionTypeDef",
    "AdditionalInferenceSpecificationDefinitionExtraOutputTypeDef",
    "InferenceSpecificationExtraOutputTypeDef",
    "AdditionalInferenceSpecificationDefinitionOutputTypeDef",
    "InferenceSpecificationOutputTypeDef",
    "AdditionalInferenceSpecificationDefinitionTypeDef",
    "InferenceSpecificationTypeDef",
    "SourceAlgorithmSpecificationExtraOutputTypeDef",
    "SourceAlgorithmSpecificationOutputTypeDef",
    "SourceAlgorithmSpecificationTypeDef",
    "MonitoringJobDefinitionExtraOutputTypeDef",
    "DescribeDataQualityJobDefinitionResponseTypeDef",
    "DescribeModelBiasJobDefinitionResponseTypeDef",
    "DescribeModelExplainabilityJobDefinitionResponseTypeDef",
    "DescribeModelQualityJobDefinitionResponseTypeDef",
    "MonitoringJobDefinitionOutputTypeDef",
    "CreateDataQualityJobDefinitionRequestRequestTypeDef",
    "DataQualityJobInputUnionTypeDef",
    "CreateModelBiasJobDefinitionRequestRequestTypeDef",
    "ModelBiasJobInputUnionTypeDef",
    "CreateModelExplainabilityJobDefinitionRequestRequestTypeDef",
    "ModelExplainabilityJobInputUnionTypeDef",
    "CreateModelQualityJobDefinitionRequestRequestTypeDef",
    "ModelQualityJobInputUnionTypeDef",
    "MonitoringJobDefinitionTypeDef",
    "ModelPackageValidationProfileExtraOutputTypeDef",
    "AlgorithmValidationProfileOutputTypeDef",
    "ModelPackageValidationProfileOutputTypeDef",
    "AlgorithmValidationProfileTypeDef",
    "ModelPackageValidationProfileTypeDef",
    "TrialComponentSourceDetailTypeDef",
    "CreateHyperParameterTuningJobRequestRequestTypeDef",
    "GetScalingConfigurationRecommendationResponseTypeDef",
    "CreateModelInputRequestTypeDef",
    "BatchDescribeModelPackageSummaryTypeDef",
    "AdditionalInferenceSpecificationDefinitionUnionTypeDef",
    "InferenceSpecificationUnionTypeDef",
    "SourceAlgorithmSpecificationUnionTypeDef",
    "MonitoringScheduleConfigExtraOutputTypeDef",
    "MonitoringScheduleConfigOutputTypeDef",
    "MonitoringScheduleConfigTypeDef",
    "ModelPackageValidationSpecificationExtraOutputTypeDef",
    "AlgorithmValidationSpecificationOutputTypeDef",
    "ModelPackageValidationSpecificationOutputTypeDef",
    "AlgorithmValidationSpecificationTypeDef",
    "ModelPackageValidationSpecificationTypeDef",
    "TrialComponentTypeDef",
    "BatchDescribeModelPackageOutputTypeDef",
    "UpdateModelPackageInputRequestTypeDef",
    "DescribeMonitoringScheduleResponseTypeDef",
    "ModelDashboardMonitoringScheduleTypeDef",
    "MonitoringScheduleTypeDef",
    "CreateMonitoringScheduleRequestRequestTypeDef",
    "MonitoringScheduleConfigUnionTypeDef",
    "UpdateMonitoringScheduleRequestRequestTypeDef",
    "DescribeAlgorithmOutputTypeDef",
    "DescribeModelPackageOutputTypeDef",
    "ModelPackageTypeDef",
    "AlgorithmValidationSpecificationUnionTypeDef",
    "CreateAlgorithmInputRequestTypeDef",
    "CreateModelPackageInputRequestTypeDef",
    "ModelPackageValidationSpecificationUnionTypeDef",
    "ModelDashboardModelTypeDef",
    "EndpointTypeDef",
    "SearchRecordTypeDef",
    "SearchResponseTypeDef",
)

ActionSourceTypeDef = TypedDict(
    "ActionSourceTypeDef",
    {
        "SourceUri": str,
        "SourceType": NotRequired[str],
        "SourceId": NotRequired[str],
    },
)
AddAssociationRequestRequestTypeDef = TypedDict(
    "AddAssociationRequestRequestTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
        "AssociationType": NotRequired[AssociationEdgeTypeType],
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
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)
AdditionalS3DataSourceTypeDef = TypedDict(
    "AdditionalS3DataSourceTypeDef",
    {
        "S3DataType": AdditionalS3DataSourceDataTypeType,
        "S3Uri": str,
        "CompressionType": NotRequired[CompressionTypeType],
    },
)
AgentVersionTypeDef = TypedDict(
    "AgentVersionTypeDef",
    {
        "Version": str,
        "AgentCount": int,
    },
)
AlarmTypeDef = TypedDict(
    "AlarmTypeDef",
    {
        "AlarmName": NotRequired[str],
    },
)
MetricDefinitionTypeDef = TypedDict(
    "MetricDefinitionTypeDef",
    {
        "Name": str,
        "Regex": str,
    },
)
AlgorithmStatusItemTypeDef = TypedDict(
    "AlgorithmStatusItemTypeDef",
    {
        "Name": str,
        "Status": DetailedAlgorithmStatusType,
        "FailureReason": NotRequired[str],
    },
)
AlgorithmSummaryTypeDef = TypedDict(
    "AlgorithmSummaryTypeDef",
    {
        "AlgorithmName": str,
        "AlgorithmArn": str,
        "CreationTime": datetime,
        "AlgorithmStatus": AlgorithmStatusType,
        "AlgorithmDescription": NotRequired[str],
    },
)
AmazonQSettingsTypeDef = TypedDict(
    "AmazonQSettingsTypeDef",
    {
        "Status": NotRequired[FeatureStatusType],
        "QProfileArn": NotRequired[str],
    },
)
AnnotationConsolidationConfigTypeDef = TypedDict(
    "AnnotationConsolidationConfigTypeDef",
    {
        "AnnotationConsolidationLambdaArn": str,
    },
)
ResourceSpecTypeDef = TypedDict(
    "ResourceSpecTypeDef",
    {
        "SageMakerImageArn": NotRequired[str],
        "SageMakerImageVersionArn": NotRequired[str],
        "SageMakerImageVersionAlias": NotRequired[str],
        "InstanceType": NotRequired[AppInstanceTypeType],
        "LifecycleConfigArn": NotRequired[str],
    },
)
AppSpecificationExtraOutputTypeDef = TypedDict(
    "AppSpecificationExtraOutputTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
    },
)
AppSpecificationOutputTypeDef = TypedDict(
    "AppSpecificationOutputTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
    },
)
AppSpecificationTypeDef = TypedDict(
    "AppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
    },
)
ArtifactSourceTypeTypeDef = TypedDict(
    "ArtifactSourceTypeTypeDef",
    {
        "SourceIdType": ArtifactSourceIdTypeType,
        "Value": str,
    },
)
AssociateTrialComponentRequestRequestTypeDef = TypedDict(
    "AssociateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "TrialName": str,
    },
)
AsyncInferenceClientConfigTypeDef = TypedDict(
    "AsyncInferenceClientConfigTypeDef",
    {
        "MaxConcurrentInvocationsPerInstance": NotRequired[int],
    },
)
AsyncInferenceNotificationConfigOutputTypeDef = TypedDict(
    "AsyncInferenceNotificationConfigOutputTypeDef",
    {
        "SuccessTopic": NotRequired[str],
        "ErrorTopic": NotRequired[str],
        "IncludeInferenceResponseIn": NotRequired[List[AsyncNotificationTopicTypesType]],
    },
)
AsyncInferenceNotificationConfigTypeDef = TypedDict(
    "AsyncInferenceNotificationConfigTypeDef",
    {
        "SuccessTopic": NotRequired[str],
        "ErrorTopic": NotRequired[str],
        "IncludeInferenceResponseIn": NotRequired[Sequence[AsyncNotificationTopicTypesType]],
    },
)
AthenaDatasetDefinitionTypeDef = TypedDict(
    "AthenaDatasetDefinitionTypeDef",
    {
        "Catalog": str,
        "Database": str,
        "QueryString": str,
        "OutputS3Uri": str,
        "OutputFormat": AthenaResultFormatType,
        "WorkGroup": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "OutputCompression": NotRequired[AthenaResultCompressionTypeType],
    },
)
AutoMLAlgorithmConfigOutputTypeDef = TypedDict(
    "AutoMLAlgorithmConfigOutputTypeDef",
    {
        "AutoMLAlgorithms": List[AutoMLAlgorithmType],
    },
)
AutoMLAlgorithmConfigTypeDef = TypedDict(
    "AutoMLAlgorithmConfigTypeDef",
    {
        "AutoMLAlgorithms": Sequence[AutoMLAlgorithmType],
    },
)
AutoMLCandidateStepTypeDef = TypedDict(
    "AutoMLCandidateStepTypeDef",
    {
        "CandidateStepType": CandidateStepTypeType,
        "CandidateStepArn": str,
        "CandidateStepName": str,
    },
)
AutoMLContainerDefinitionTypeDef = TypedDict(
    "AutoMLContainerDefinitionTypeDef",
    {
        "Image": str,
        "ModelDataUrl": str,
        "Environment": NotRequired[Dict[str, str]],
    },
)
FinalAutoMLJobObjectiveMetricTypeDef = TypedDict(
    "FinalAutoMLJobObjectiveMetricTypeDef",
    {
        "MetricName": AutoMLMetricEnumType,
        "Value": float,
        "Type": NotRequired[AutoMLJobObjectiveTypeType],
        "StandardMetricName": NotRequired[AutoMLMetricEnumType],
    },
)
AutoMLS3DataSourceTypeDef = TypedDict(
    "AutoMLS3DataSourceTypeDef",
    {
        "S3DataType": AutoMLS3DataTypeType,
        "S3Uri": str,
    },
)
AutoMLDataSplitConfigTypeDef = TypedDict(
    "AutoMLDataSplitConfigTypeDef",
    {
        "ValidationFraction": NotRequired[float],
    },
)
AutoMLJobArtifactsTypeDef = TypedDict(
    "AutoMLJobArtifactsTypeDef",
    {
        "CandidateDefinitionNotebookLocation": NotRequired[str],
        "DataExplorationNotebookLocation": NotRequired[str],
    },
)
AutoMLJobCompletionCriteriaTypeDef = TypedDict(
    "AutoMLJobCompletionCriteriaTypeDef",
    {
        "MaxCandidates": NotRequired[int],
        "MaxRuntimePerTrainingJobInSeconds": NotRequired[int],
        "MaxAutoMLJobRuntimeInSeconds": NotRequired[int],
    },
)
AutoMLJobObjectiveTypeDef = TypedDict(
    "AutoMLJobObjectiveTypeDef",
    {
        "MetricName": AutoMLMetricEnumType,
    },
)
AutoMLJobStepMetadataTypeDef = TypedDict(
    "AutoMLJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
AutoMLPartialFailureReasonTypeDef = TypedDict(
    "AutoMLPartialFailureReasonTypeDef",
    {
        "PartialFailureMessage": NotRequired[str],
    },
)
AutoMLOutputDataConfigTypeDef = TypedDict(
    "AutoMLOutputDataConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
    },
)
TabularResolvedAttributesTypeDef = TypedDict(
    "TabularResolvedAttributesTypeDef",
    {
        "ProblemType": NotRequired[ProblemTypeType],
    },
)
TextGenerationResolvedAttributesTypeDef = TypedDict(
    "TextGenerationResolvedAttributesTypeDef",
    {
        "BaseModelName": NotRequired[str],
    },
)
VpcConfigOutputTypeDef = TypedDict(
    "VpcConfigOutputTypeDef",
    {
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
    },
)
VpcConfigTypeDef = TypedDict(
    "VpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)
AutoParameterTypeDef = TypedDict(
    "AutoParameterTypeDef",
    {
        "Name": str,
        "ValueHint": str,
    },
)
AutotuneTypeDef = TypedDict(
    "AutotuneTypeDef",
    {
        "Mode": Literal["Enabled"],
    },
)
BatchDataCaptureConfigTypeDef = TypedDict(
    "BatchDataCaptureConfigTypeDef",
    {
        "DestinationS3Uri": str,
        "KmsKeyId": NotRequired[str],
        "GenerateInferenceId": NotRequired[bool],
    },
)
BatchDescribeModelPackageErrorTypeDef = TypedDict(
    "BatchDescribeModelPackageErrorTypeDef",
    {
        "ErrorCode": str,
        "ErrorResponse": str,
    },
)
BatchDescribeModelPackageInputRequestTypeDef = TypedDict(
    "BatchDescribeModelPackageInputRequestTypeDef",
    {
        "ModelPackageArnList": Sequence[str],
    },
)
BestObjectiveNotImprovingTypeDef = TypedDict(
    "BestObjectiveNotImprovingTypeDef",
    {
        "MaxNumberOfTrainingJobsNotImproving": NotRequired[int],
    },
)
MetricsSourceTypeDef = TypedDict(
    "MetricsSourceTypeDef",
    {
        "ContentType": str,
        "S3Uri": str,
        "ContentDigest": NotRequired[str],
    },
)
CacheHitResultTypeDef = TypedDict(
    "CacheHitResultTypeDef",
    {
        "SourcePipelineExecutionArn": NotRequired[str],
    },
)
OutputParameterTypeDef = TypedDict(
    "OutputParameterTypeDef",
    {
        "Name": str,
        "Value": str,
    },
)
CandidateArtifactLocationsTypeDef = TypedDict(
    "CandidateArtifactLocationsTypeDef",
    {
        "Explainability": str,
        "ModelInsights": NotRequired[str],
        "BacktestResults": NotRequired[str],
    },
)
MetricDatumTypeDef = TypedDict(
    "MetricDatumTypeDef",
    {
        "MetricName": NotRequired[AutoMLMetricEnumType],
        "Value": NotRequired[float],
        "Set": NotRequired[MetricSetSourceType],
        "StandardMetricName": NotRequired[AutoMLMetricExtendedEnumType],
    },
)
DirectDeploySettingsTypeDef = TypedDict(
    "DirectDeploySettingsTypeDef",
    {
        "Status": NotRequired[FeatureStatusType],
    },
)
GenerativeAiSettingsTypeDef = TypedDict(
    "GenerativeAiSettingsTypeDef",
    {
        "AmazonBedrockRoleArn": NotRequired[str],
    },
)
IdentityProviderOAuthSettingTypeDef = TypedDict(
    "IdentityProviderOAuthSettingTypeDef",
    {
        "DataSourceName": NotRequired[DataSourceNameType],
        "Status": NotRequired[FeatureStatusType],
        "SecretArn": NotRequired[str],
    },
)
KendraSettingsTypeDef = TypedDict(
    "KendraSettingsTypeDef",
    {
        "Status": NotRequired[FeatureStatusType],
    },
)
ModelRegisterSettingsTypeDef = TypedDict(
    "ModelRegisterSettingsTypeDef",
    {
        "Status": NotRequired[FeatureStatusType],
        "CrossAccountModelRegisterRoleArn": NotRequired[str],
    },
)
TimeSeriesForecastingSettingsTypeDef = TypedDict(
    "TimeSeriesForecastingSettingsTypeDef",
    {
        "Status": NotRequired[FeatureStatusType],
        "AmazonForecastRoleArn": NotRequired[str],
    },
)
WorkspaceSettingsTypeDef = TypedDict(
    "WorkspaceSettingsTypeDef",
    {
        "S3ArtifactPath": NotRequired[str],
        "S3KmsKeyId": NotRequired[str],
    },
)
CapacitySizeTypeDef = TypedDict(
    "CapacitySizeTypeDef",
    {
        "Type": CapacitySizeTypeType,
        "Value": int,
    },
)
CaptureContentTypeHeaderOutputTypeDef = TypedDict(
    "CaptureContentTypeHeaderOutputTypeDef",
    {
        "CsvContentTypes": NotRequired[List[str]],
        "JsonContentTypes": NotRequired[List[str]],
    },
)
CaptureContentTypeHeaderTypeDef = TypedDict(
    "CaptureContentTypeHeaderTypeDef",
    {
        "CsvContentTypes": NotRequired[Sequence[str]],
        "JsonContentTypes": NotRequired[Sequence[str]],
    },
)
CaptureOptionTypeDef = TypedDict(
    "CaptureOptionTypeDef",
    {
        "CaptureMode": CaptureModeType,
    },
)
CategoricalParameterOutputTypeDef = TypedDict(
    "CategoricalParameterOutputTypeDef",
    {
        "Name": str,
        "Value": List[str],
    },
)
CategoricalParameterRangeExtraOutputTypeDef = TypedDict(
    "CategoricalParameterRangeExtraOutputTypeDef",
    {
        "Name": str,
        "Values": List[str],
    },
)
CategoricalParameterRangeOutputTypeDef = TypedDict(
    "CategoricalParameterRangeOutputTypeDef",
    {
        "Name": str,
        "Values": List[str],
    },
)
CategoricalParameterRangeSpecificationOutputTypeDef = TypedDict(
    "CategoricalParameterRangeSpecificationOutputTypeDef",
    {
        "Values": List[str],
    },
)
CategoricalParameterRangeSpecificationTypeDef = TypedDict(
    "CategoricalParameterRangeSpecificationTypeDef",
    {
        "Values": Sequence[str],
    },
)
CategoricalParameterRangeTypeDef = TypedDict(
    "CategoricalParameterRangeTypeDef",
    {
        "Name": str,
        "Values": Sequence[str],
    },
)
CategoricalParameterTypeDef = TypedDict(
    "CategoricalParameterTypeDef",
    {
        "Name": str,
        "Value": Sequence[str],
    },
)
ShuffleConfigTypeDef = TypedDict(
    "ShuffleConfigTypeDef",
    {
        "Seed": int,
    },
)
ChannelSpecificationOutputTypeDef = TypedDict(
    "ChannelSpecificationOutputTypeDef",
    {
        "Name": str,
        "SupportedContentTypes": List[str],
        "SupportedInputModes": List[TrainingInputModeType],
        "Description": NotRequired[str],
        "IsRequired": NotRequired[bool],
        "SupportedCompressionTypes": NotRequired[List[CompressionTypeType]],
    },
)
ChannelSpecificationTypeDef = TypedDict(
    "ChannelSpecificationTypeDef",
    {
        "Name": str,
        "SupportedContentTypes": Sequence[str],
        "SupportedInputModes": Sequence[TrainingInputModeType],
        "Description": NotRequired[str],
        "IsRequired": NotRequired[bool],
        "SupportedCompressionTypes": NotRequired[Sequence[CompressionTypeType]],
    },
)
CheckpointConfigTypeDef = TypedDict(
    "CheckpointConfigTypeDef",
    {
        "S3Uri": str,
        "LocalPath": NotRequired[str],
    },
)
ClarifyCheckStepMetadataTypeDef = TypedDict(
    "ClarifyCheckStepMetadataTypeDef",
    {
        "CheckType": NotRequired[str],
        "BaselineUsedForDriftCheckConstraints": NotRequired[str],
        "CalculatedBaselineConstraints": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ViolationReport": NotRequired[str],
        "CheckJobArn": NotRequired[str],
        "SkipCheck": NotRequired[bool],
        "RegisterNewBaseline": NotRequired[bool],
    },
)
ClarifyInferenceConfigOutputTypeDef = TypedDict(
    "ClarifyInferenceConfigOutputTypeDef",
    {
        "FeaturesAttribute": NotRequired[str],
        "ContentTemplate": NotRequired[str],
        "MaxRecordCount": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "ProbabilityIndex": NotRequired[int],
        "LabelIndex": NotRequired[int],
        "ProbabilityAttribute": NotRequired[str],
        "LabelAttribute": NotRequired[str],
        "LabelHeaders": NotRequired[List[str]],
        "FeatureHeaders": NotRequired[List[str]],
        "FeatureTypes": NotRequired[List[ClarifyFeatureTypeType]],
    },
)
ClarifyInferenceConfigTypeDef = TypedDict(
    "ClarifyInferenceConfigTypeDef",
    {
        "FeaturesAttribute": NotRequired[str],
        "ContentTemplate": NotRequired[str],
        "MaxRecordCount": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "ProbabilityIndex": NotRequired[int],
        "LabelIndex": NotRequired[int],
        "ProbabilityAttribute": NotRequired[str],
        "LabelAttribute": NotRequired[str],
        "LabelHeaders": NotRequired[Sequence[str]],
        "FeatureHeaders": NotRequired[Sequence[str]],
        "FeatureTypes": NotRequired[Sequence[ClarifyFeatureTypeType]],
    },
)
ClarifyShapBaselineConfigTypeDef = TypedDict(
    "ClarifyShapBaselineConfigTypeDef",
    {
        "MimeType": NotRequired[str],
        "ShapBaseline": NotRequired[str],
        "ShapBaselineUri": NotRequired[str],
    },
)
ClarifyTextConfigTypeDef = TypedDict(
    "ClarifyTextConfigTypeDef",
    {
        "Language": ClarifyTextLanguageType,
        "Granularity": ClarifyTextGranularityType,
    },
)
ClusterEbsVolumeConfigTypeDef = TypedDict(
    "ClusterEbsVolumeConfigTypeDef",
    {
        "VolumeSizeInGB": int,
    },
)
ClusterLifeCycleConfigTypeDef = TypedDict(
    "ClusterLifeCycleConfigTypeDef",
    {
        "SourceS3Uri": str,
        "OnCreate": str,
    },
)
ClusterInstancePlacementTypeDef = TypedDict(
    "ClusterInstancePlacementTypeDef",
    {
        "AvailabilityZone": NotRequired[str],
        "AvailabilityZoneId": NotRequired[str],
    },
)
ClusterInstanceStatusDetailsTypeDef = TypedDict(
    "ClusterInstanceStatusDetailsTypeDef",
    {
        "Status": ClusterInstanceStatusType,
        "Message": NotRequired[str],
    },
)
ClusterSummaryTypeDef = TypedDict(
    "ClusterSummaryTypeDef",
    {
        "ClusterArn": str,
        "ClusterName": str,
        "CreationTime": datetime,
        "ClusterStatus": ClusterStatusType,
    },
)
ContainerConfigExtraOutputTypeDef = TypedDict(
    "ContainerConfigExtraOutputTypeDef",
    {
        "ContainerArguments": NotRequired[List[str]],
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerEnvironmentVariables": NotRequired[Dict[str, str]],
    },
)
FileSystemConfigTypeDef = TypedDict(
    "FileSystemConfigTypeDef",
    {
        "MountPath": NotRequired[str],
        "DefaultUid": NotRequired[int],
        "DefaultGid": NotRequired[int],
    },
)
ContainerConfigOutputTypeDef = TypedDict(
    "ContainerConfigOutputTypeDef",
    {
        "ContainerArguments": NotRequired[List[str]],
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerEnvironmentVariables": NotRequired[Dict[str, str]],
    },
)
ContainerConfigTypeDef = TypedDict(
    "ContainerConfigTypeDef",
    {
        "ContainerArguments": NotRequired[Sequence[str]],
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerEnvironmentVariables": NotRequired[Mapping[str, str]],
    },
)
CustomImageTypeDef = TypedDict(
    "CustomImageTypeDef",
    {
        "ImageName": str,
        "AppImageConfigName": str,
        "ImageVersionNumber": NotRequired[int],
    },
)
GitConfigTypeDef = TypedDict(
    "GitConfigTypeDef",
    {
        "RepositoryUrl": str,
        "Branch": NotRequired[str],
        "SecretArn": NotRequired[str],
    },
)
CodeRepositoryTypeDef = TypedDict(
    "CodeRepositoryTypeDef",
    {
        "RepositoryUrl": str,
    },
)
CognitoConfigTypeDef = TypedDict(
    "CognitoConfigTypeDef",
    {
        "UserPool": str,
        "ClientId": str,
    },
)
CognitoMemberDefinitionTypeDef = TypedDict(
    "CognitoMemberDefinitionTypeDef",
    {
        "UserPool": str,
        "UserGroup": str,
        "ClientId": str,
    },
)
VectorConfigTypeDef = TypedDict(
    "VectorConfigTypeDef",
    {
        "Dimension": int,
    },
)
CollectionConfigurationExtraOutputTypeDef = TypedDict(
    "CollectionConfigurationExtraOutputTypeDef",
    {
        "CollectionName": NotRequired[str],
        "CollectionParameters": NotRequired[Dict[str, str]],
    },
)
CollectionConfigurationOutputTypeDef = TypedDict(
    "CollectionConfigurationOutputTypeDef",
    {
        "CollectionName": NotRequired[str],
        "CollectionParameters": NotRequired[Dict[str, str]],
    },
)
CollectionConfigurationTypeDef = TypedDict(
    "CollectionConfigurationTypeDef",
    {
        "CollectionName": NotRequired[str],
        "CollectionParameters": NotRequired[Mapping[str, str]],
    },
)
CompilationJobSummaryTypeDef = TypedDict(
    "CompilationJobSummaryTypeDef",
    {
        "CompilationJobName": str,
        "CompilationJobArn": str,
        "CreationTime": datetime,
        "CompilationJobStatus": CompilationJobStatusType,
        "CompilationStartTime": NotRequired[datetime],
        "CompilationEndTime": NotRequired[datetime],
        "CompilationTargetDevice": NotRequired[TargetDeviceType],
        "CompilationTargetPlatformOs": NotRequired[TargetPlatformOsType],
        "CompilationTargetPlatformArch": NotRequired[TargetPlatformArchType],
        "CompilationTargetPlatformAccelerator": NotRequired[TargetPlatformAcceleratorType],
        "LastModifiedTime": NotRequired[datetime],
    },
)
ConditionStepMetadataTypeDef = TypedDict(
    "ConditionStepMetadataTypeDef",
    {
        "Outcome": NotRequired[ConditionOutcomeType],
    },
)
MultiModelConfigTypeDef = TypedDict(
    "MultiModelConfigTypeDef",
    {
        "ModelCacheSetting": NotRequired[ModelCacheSettingType],
    },
)
ContextSourceTypeDef = TypedDict(
    "ContextSourceTypeDef",
    {
        "SourceUri": str,
        "SourceType": NotRequired[str],
        "SourceId": NotRequired[str],
    },
)
ContinuousParameterRangeSpecificationTypeDef = TypedDict(
    "ContinuousParameterRangeSpecificationTypeDef",
    {
        "MinValue": str,
        "MaxValue": str,
    },
)
ContinuousParameterRangeTypeDef = TypedDict(
    "ContinuousParameterRangeTypeDef",
    {
        "Name": str,
        "MinValue": str,
        "MaxValue": str,
        "ScalingType": NotRequired[HyperParameterScalingTypeType],
    },
)
ConvergenceDetectedTypeDef = TypedDict(
    "ConvergenceDetectedTypeDef",
    {
        "CompleteOnConvergence": NotRequired[CompleteOnConvergenceType],
    },
)
MetadataPropertiesTypeDef = TypedDict(
    "MetadataPropertiesTypeDef",
    {
        "CommitId": NotRequired[str],
        "Repository": NotRequired[str],
        "GeneratedBy": NotRequired[str],
        "ProjectId": NotRequired[str],
    },
)
ModelDeployConfigTypeDef = TypedDict(
    "ModelDeployConfigTypeDef",
    {
        "AutoGenerateEndpointName": NotRequired[bool],
        "EndpointName": NotRequired[str],
    },
)
InputConfigTypeDef = TypedDict(
    "InputConfigTypeDef",
    {
        "S3Uri": str,
        "Framework": FrameworkType,
        "DataInputConfig": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
    },
)
NeoVpcConfigTypeDef = TypedDict(
    "NeoVpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)
StoppingConditionTypeDef = TypedDict(
    "StoppingConditionTypeDef",
    {
        "MaxRuntimeInSeconds": NotRequired[int],
        "MaxWaitTimeInSeconds": NotRequired[int],
        "MaxPendingTimeInSeconds": NotRequired[int],
    },
)
DataQualityAppSpecificationTypeDef = TypedDict(
    "DataQualityAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
        "Environment": NotRequired[Mapping[str, str]],
    },
)
MonitoringStoppingConditionTypeDef = TypedDict(
    "MonitoringStoppingConditionTypeDef",
    {
        "MaxRuntimeInSeconds": int,
    },
)
EdgeOutputConfigTypeDef = TypedDict(
    "EdgeOutputConfigTypeDef",
    {
        "S3OutputLocation": str,
        "KmsKeyId": NotRequired[str],
        "PresetDeploymentType": NotRequired[Literal["GreengrassV2Component"]],
        "PresetDeploymentConfig": NotRequired[str],
    },
)
EdgeDeploymentModelConfigTypeDef = TypedDict(
    "EdgeDeploymentModelConfigTypeDef",
    {
        "ModelHandle": str,
        "EdgePackagingJobName": str,
    },
)
ThroughputConfigTypeDef = TypedDict(
    "ThroughputConfigTypeDef",
    {
        "ThroughputMode": ThroughputModeType,
        "ProvisionedReadCapacityUnits": NotRequired[int],
        "ProvisionedWriteCapacityUnits": NotRequired[int],
    },
)
FlowDefinitionOutputConfigTypeDef = TypedDict(
    "FlowDefinitionOutputConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
    },
)
HumanLoopRequestSourceTypeDef = TypedDict(
    "HumanLoopRequestSourceTypeDef",
    {
        "AwsManagedHumanLoopRequestSource": AwsManagedHumanLoopRequestSourceType,
    },
)
HubS3StorageConfigTypeDef = TypedDict(
    "HubS3StorageConfigTypeDef",
    {
        "S3OutputPath": NotRequired[str],
    },
)
UiTemplateTypeDef = TypedDict(
    "UiTemplateTypeDef",
    {
        "Content": str,
    },
)
CreateImageVersionRequestRequestTypeDef = TypedDict(
    "CreateImageVersionRequestRequestTypeDef",
    {
        "BaseImage": str,
        "ClientToken": str,
        "ImageName": str,
        "Aliases": NotRequired[Sequence[str]],
        "VendorGuidance": NotRequired[VendorGuidanceType],
        "JobType": NotRequired[JobTypeType],
        "MLFramework": NotRequired[str],
        "ProgrammingLang": NotRequired[str],
        "Processor": NotRequired[ProcessorType],
        "Horovod": NotRequired[bool],
        "ReleaseNotes": NotRequired[str],
    },
)
InferenceComponentRuntimeConfigTypeDef = TypedDict(
    "InferenceComponentRuntimeConfigTypeDef",
    {
        "CopyCount": int,
    },
)
LabelingJobOutputConfigTypeDef = TypedDict(
    "LabelingJobOutputConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
        "SnsTopicArn": NotRequired[str],
    },
)
LabelingJobStoppingConditionsTypeDef = TypedDict(
    "LabelingJobStoppingConditionsTypeDef",
    {
        "MaxHumanLabeledObjectCount": NotRequired[int],
        "MaxPercentageOfInputDatasetLabeled": NotRequired[int],
    },
)
ModelBiasAppSpecificationTypeDef = TypedDict(
    "ModelBiasAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ConfigUri": str,
        "Environment": NotRequired[Mapping[str, str]],
    },
)
ModelCardExportOutputConfigTypeDef = TypedDict(
    "ModelCardExportOutputConfigTypeDef",
    {
        "S3OutputPath": str,
    },
)
ModelCardSecurityConfigTypeDef = TypedDict(
    "ModelCardSecurityConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
    },
)
ModelExplainabilityAppSpecificationTypeDef = TypedDict(
    "ModelExplainabilityAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ConfigUri": str,
        "Environment": NotRequired[Mapping[str, str]],
    },
)
InferenceExecutionConfigTypeDef = TypedDict(
    "InferenceExecutionConfigTypeDef",
    {
        "Mode": InferenceExecutionModeType,
    },
)
ModelPackageModelCardTypeDef = TypedDict(
    "ModelPackageModelCardTypeDef",
    {
        "ModelCardContent": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
    },
)
ModelPackageSecurityConfigTypeDef = TypedDict(
    "ModelPackageSecurityConfigTypeDef",
    {
        "KmsKeyId": str,
    },
)
ModelQualityAppSpecificationTypeDef = TypedDict(
    "ModelQualityAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
        "ProblemType": NotRequired[MonitoringProblemTypeType],
        "Environment": NotRequired[Mapping[str, str]],
    },
)
InstanceMetadataServiceConfigurationTypeDef = TypedDict(
    "InstanceMetadataServiceConfigurationTypeDef",
    {
        "MinimumInstanceMetadataServiceVersion": str,
    },
)
NotebookInstanceLifecycleHookTypeDef = TypedDict(
    "NotebookInstanceLifecycleHookTypeDef",
    {
        "Content": NotRequired[str],
    },
)
OptimizationJobOutputConfigTypeDef = TypedDict(
    "OptimizationJobOutputConfigTypeDef",
    {
        "S3OutputLocation": str,
        "KmsKeyId": NotRequired[str],
    },
)
OptimizationVpcConfigTypeDef = TypedDict(
    "OptimizationVpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)
ParallelismConfigurationTypeDef = TypedDict(
    "ParallelismConfigurationTypeDef",
    {
        "MaxParallelExecutionSteps": int,
    },
)
PipelineDefinitionS3LocationTypeDef = TypedDict(
    "PipelineDefinitionS3LocationTypeDef",
    {
        "Bucket": str,
        "ObjectKey": str,
        "VersionId": NotRequired[str],
    },
)
CreatePresignedDomainUrlRequestRequestTypeDef = TypedDict(
    "CreatePresignedDomainUrlRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
        "SessionExpirationDurationInSeconds": NotRequired[int],
        "ExpiresInSeconds": NotRequired[int],
        "SpaceName": NotRequired[str],
        "LandingUri": NotRequired[str],
    },
)
CreatePresignedMlflowTrackingServerUrlRequestRequestTypeDef = TypedDict(
    "CreatePresignedMlflowTrackingServerUrlRequestRequestTypeDef",
    {
        "TrackingServerName": str,
        "ExpiresInSeconds": NotRequired[int],
        "SessionExpirationDurationInSeconds": NotRequired[int],
    },
)
CreatePresignedNotebookInstanceUrlInputRequestTypeDef = TypedDict(
    "CreatePresignedNotebookInstanceUrlInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
        "SessionExpirationDurationInSeconds": NotRequired[int],
    },
)
ExperimentConfigTypeDef = TypedDict(
    "ExperimentConfigTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
        "TrialComponentDisplayName": NotRequired[str],
        "RunName": NotRequired[str],
    },
)
ProcessingStoppingConditionTypeDef = TypedDict(
    "ProcessingStoppingConditionTypeDef",
    {
        "MaxRuntimeInSeconds": int,
    },
)
OwnershipSettingsTypeDef = TypedDict(
    "OwnershipSettingsTypeDef",
    {
        "OwnerUserProfileName": str,
    },
)
SpaceSharingSettingsTypeDef = TypedDict(
    "SpaceSharingSettingsTypeDef",
    {
        "SharingType": SharingTypeType,
    },
)
InfraCheckConfigTypeDef = TypedDict(
    "InfraCheckConfigTypeDef",
    {
        "EnableInfraCheck": NotRequired[bool],
    },
)
OutputDataConfigTypeDef = TypedDict(
    "OutputDataConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
        "CompressionType": NotRequired[OutputCompressionTypeType],
    },
)
ProfilerConfigTypeDef = TypedDict(
    "ProfilerConfigTypeDef",
    {
        "S3OutputPath": NotRequired[str],
        "ProfilingIntervalInMilliseconds": NotRequired[int],
        "ProfilingParameters": NotRequired[Mapping[str, str]],
        "DisableProfiler": NotRequired[bool],
    },
)
RemoteDebugConfigTypeDef = TypedDict(
    "RemoteDebugConfigTypeDef",
    {
        "EnableRemoteDebug": NotRequired[bool],
    },
)
RetryStrategyTypeDef = TypedDict(
    "RetryStrategyTypeDef",
    {
        "MaximumRetryAttempts": int,
    },
)
SessionChainingConfigTypeDef = TypedDict(
    "SessionChainingConfigTypeDef",
    {
        "EnableSessionTagChaining": NotRequired[bool],
    },
)
TensorBoardOutputConfigTypeDef = TypedDict(
    "TensorBoardOutputConfigTypeDef",
    {
        "S3OutputPath": str,
        "LocalPath": NotRequired[str],
    },
)
DataProcessingTypeDef = TypedDict(
    "DataProcessingTypeDef",
    {
        "InputFilter": NotRequired[str],
        "OutputFilter": NotRequired[str],
        "JoinSource": NotRequired[JoinSourceType],
    },
)
ModelClientConfigTypeDef = TypedDict(
    "ModelClientConfigTypeDef",
    {
        "InvocationsTimeoutInSeconds": NotRequired[int],
        "InvocationsMaxRetries": NotRequired[int],
    },
)
TransformOutputTypeDef = TypedDict(
    "TransformOutputTypeDef",
    {
        "S3OutputPath": str,
        "Accept": NotRequired[str],
        "AssembleWith": NotRequired[AssemblyTypeType],
        "KmsKeyId": NotRequired[str],
    },
)
TransformResourcesTypeDef = TypedDict(
    "TransformResourcesTypeDef",
    {
        "InstanceType": TransformInstanceTypeType,
        "InstanceCount": int,
        "VolumeKmsKeyId": NotRequired[str],
    },
)
TimestampTypeDef = Union[datetime, str]
TrialComponentArtifactTypeDef = TypedDict(
    "TrialComponentArtifactTypeDef",
    {
        "Value": str,
        "MediaType": NotRequired[str],
    },
)
TrialComponentParameterValueTypeDef = TypedDict(
    "TrialComponentParameterValueTypeDef",
    {
        "StringValue": NotRequired[str],
        "NumberValue": NotRequired[float],
    },
)
TrialComponentStatusTypeDef = TypedDict(
    "TrialComponentStatusTypeDef",
    {
        "PrimaryStatus": NotRequired[TrialComponentPrimaryStatusType],
        "Message": NotRequired[str],
    },
)
OidcConfigTypeDef = TypedDict(
    "OidcConfigTypeDef",
    {
        "ClientId": str,
        "ClientSecret": str,
        "Issuer": str,
        "AuthorizationEndpoint": str,
        "TokenEndpoint": str,
        "UserInfoEndpoint": str,
        "LogoutEndpoint": str,
        "JwksUri": str,
        "Scope": NotRequired[str],
        "AuthenticationRequestExtraParams": NotRequired[Mapping[str, str]],
    },
)
SourceIpConfigTypeDef = TypedDict(
    "SourceIpConfigTypeDef",
    {
        "Cidrs": Sequence[str],
    },
)
WorkforceVpcConfigRequestTypeDef = TypedDict(
    "WorkforceVpcConfigRequestTypeDef",
    {
        "VpcId": NotRequired[str],
        "SecurityGroupIds": NotRequired[Sequence[str]],
        "Subnets": NotRequired[Sequence[str]],
    },
)
NotificationConfigurationTypeDef = TypedDict(
    "NotificationConfigurationTypeDef",
    {
        "NotificationTopicArn": NotRequired[str],
    },
)
EFSFileSystemConfigTypeDef = TypedDict(
    "EFSFileSystemConfigTypeDef",
    {
        "FileSystemId": str,
        "FileSystemPath": NotRequired[str],
    },
)
EFSFileSystemTypeDef = TypedDict(
    "EFSFileSystemTypeDef",
    {
        "FileSystemId": str,
    },
)
CustomPosixUserConfigTypeDef = TypedDict(
    "CustomPosixUserConfigTypeDef",
    {
        "Uid": int,
        "Gid": int,
    },
)
CustomizedMetricSpecificationTypeDef = TypedDict(
    "CustomizedMetricSpecificationTypeDef",
    {
        "MetricName": NotRequired[str],
        "Namespace": NotRequired[str],
        "Statistic": NotRequired[StatisticType],
    },
)
DataCaptureConfigSummaryTypeDef = TypedDict(
    "DataCaptureConfigSummaryTypeDef",
    {
        "EnableCapture": bool,
        "CaptureStatus": CaptureStatusType,
        "CurrentSamplingPercentage": int,
        "DestinationS3Uri": str,
        "KmsKeyId": str,
    },
)
DataCatalogConfigTypeDef = TypedDict(
    "DataCatalogConfigTypeDef",
    {
        "TableName": str,
        "Catalog": str,
        "Database": str,
    },
)
DataQualityAppSpecificationOutputTypeDef = TypedDict(
    "DataQualityAppSpecificationOutputTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
        "Environment": NotRequired[Dict[str, str]],
    },
)
MonitoringConstraintsResourceTypeDef = TypedDict(
    "MonitoringConstraintsResourceTypeDef",
    {
        "S3Uri": NotRequired[str],
    },
)
MonitoringStatisticsResourceTypeDef = TypedDict(
    "MonitoringStatisticsResourceTypeDef",
    {
        "S3Uri": NotRequired[str],
    },
)
EndpointInputTypeDef = TypedDict(
    "EndpointInputTypeDef",
    {
        "EndpointName": str,
        "LocalPath": str,
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "FeaturesAttribute": NotRequired[str],
        "InferenceAttribute": NotRequired[str],
        "ProbabilityAttribute": NotRequired[str],
        "ProbabilityThresholdAttribute": NotRequired[float],
        "StartTimeOffset": NotRequired[str],
        "EndTimeOffset": NotRequired[str],
        "ExcludeFeaturesAttribute": NotRequired[str],
    },
)
FileSystemDataSourceTypeDef = TypedDict(
    "FileSystemDataSourceTypeDef",
    {
        "FileSystemId": str,
        "FileSystemAccessMode": FileSystemAccessModeType,
        "FileSystemType": FileSystemTypeType,
        "DirectoryPath": str,
    },
)
S3DataSourceExtraOutputTypeDef = TypedDict(
    "S3DataSourceExtraOutputTypeDef",
    {
        "S3DataType": S3DataTypeType,
        "S3Uri": str,
        "S3DataDistributionType": NotRequired[S3DataDistributionType],
        "AttributeNames": NotRequired[List[str]],
        "InstanceGroupNames": NotRequired[List[str]],
    },
)
S3DataSourceOutputTypeDef = TypedDict(
    "S3DataSourceOutputTypeDef",
    {
        "S3DataType": S3DataTypeType,
        "S3Uri": str,
        "S3DataDistributionType": NotRequired[S3DataDistributionType],
        "AttributeNames": NotRequired[List[str]],
        "InstanceGroupNames": NotRequired[List[str]],
    },
)
S3DataSourceTypeDef = TypedDict(
    "S3DataSourceTypeDef",
    {
        "S3DataType": S3DataTypeType,
        "S3Uri": str,
        "S3DataDistributionType": NotRequired[S3DataDistributionType],
        "AttributeNames": NotRequired[Sequence[str]],
        "InstanceGroupNames": NotRequired[Sequence[str]],
    },
)
RedshiftDatasetDefinitionTypeDef = TypedDict(
    "RedshiftDatasetDefinitionTypeDef",
    {
        "ClusterId": str,
        "Database": str,
        "DbUser": str,
        "QueryString": str,
        "ClusterRoleArn": str,
        "OutputS3Uri": str,
        "OutputFormat": RedshiftResultFormatType,
        "KmsKeyId": NotRequired[str],
        "OutputCompression": NotRequired[RedshiftResultCompressionTypeType],
    },
)
DebugRuleConfigurationExtraOutputTypeDef = TypedDict(
    "DebugRuleConfigurationExtraOutputTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Dict[str, str]],
    },
)
DebugRuleConfigurationOutputTypeDef = TypedDict(
    "DebugRuleConfigurationOutputTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Dict[str, str]],
    },
)
DebugRuleConfigurationTypeDef = TypedDict(
    "DebugRuleConfigurationTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Mapping[str, str]],
    },
)
DebugRuleEvaluationStatusTypeDef = TypedDict(
    "DebugRuleEvaluationStatusTypeDef",
    {
        "RuleConfigurationName": NotRequired[str],
        "RuleEvaluationJobArn": NotRequired[str],
        "RuleEvaluationStatus": NotRequired[RuleEvaluationStatusType],
        "StatusDetails": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
    },
)
DefaultEbsStorageSettingsTypeDef = TypedDict(
    "DefaultEbsStorageSettingsTypeDef",
    {
        "DefaultEbsVolumeSizeInGb": int,
        "MaximumEbsVolumeSizeInGb": int,
    },
)
DeleteActionRequestRequestTypeDef = TypedDict(
    "DeleteActionRequestRequestTypeDef",
    {
        "ActionName": str,
    },
)
DeleteAlgorithmInputRequestTypeDef = TypedDict(
    "DeleteAlgorithmInputRequestTypeDef",
    {
        "AlgorithmName": str,
    },
)
DeleteAppImageConfigRequestRequestTypeDef = TypedDict(
    "DeleteAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
    },
)
DeleteAppRequestRequestTypeDef = TypedDict(
    "DeleteAppRequestRequestTypeDef",
    {
        "DomainId": str,
        "AppType": AppTypeType,
        "AppName": str,
        "UserProfileName": NotRequired[str],
        "SpaceName": NotRequired[str],
    },
)
DeleteAssociationRequestRequestTypeDef = TypedDict(
    "DeleteAssociationRequestRequestTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
    },
)
DeleteClusterRequestRequestTypeDef = TypedDict(
    "DeleteClusterRequestRequestTypeDef",
    {
        "ClusterName": str,
    },
)
DeleteCodeRepositoryInputRequestTypeDef = TypedDict(
    "DeleteCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
    },
)
DeleteCompilationJobRequestRequestTypeDef = TypedDict(
    "DeleteCompilationJobRequestRequestTypeDef",
    {
        "CompilationJobName": str,
    },
)
DeleteContextRequestRequestTypeDef = TypedDict(
    "DeleteContextRequestRequestTypeDef",
    {
        "ContextName": str,
    },
)
DeleteDataQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteDataQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
DeleteDeviceFleetRequestRequestTypeDef = TypedDict(
    "DeleteDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
    },
)
RetentionPolicyTypeDef = TypedDict(
    "RetentionPolicyTypeDef",
    {
        "HomeEfsFileSystem": NotRequired[RetentionTypeType],
    },
)
DeleteEdgeDeploymentPlanRequestRequestTypeDef = TypedDict(
    "DeleteEdgeDeploymentPlanRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
    },
)
DeleteEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "DeleteEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
    },
)
DeleteEndpointConfigInputRequestTypeDef = TypedDict(
    "DeleteEndpointConfigInputRequestTypeDef",
    {
        "EndpointConfigName": str,
    },
)
DeleteEndpointInputRequestTypeDef = TypedDict(
    "DeleteEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
    },
)
DeleteExperimentRequestRequestTypeDef = TypedDict(
    "DeleteExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
    },
)
DeleteFeatureGroupRequestRequestTypeDef = TypedDict(
    "DeleteFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
    },
)
DeleteFlowDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteFlowDefinitionRequestRequestTypeDef",
    {
        "FlowDefinitionName": str,
    },
)
DeleteHubContentReferenceRequestRequestTypeDef = TypedDict(
    "DeleteHubContentReferenceRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "HubContentName": str,
    },
)
DeleteHubContentRequestRequestTypeDef = TypedDict(
    "DeleteHubContentRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "HubContentName": str,
        "HubContentVersion": str,
    },
)
DeleteHubRequestRequestTypeDef = TypedDict(
    "DeleteHubRequestRequestTypeDef",
    {
        "HubName": str,
    },
)
DeleteHumanTaskUiRequestRequestTypeDef = TypedDict(
    "DeleteHumanTaskUiRequestRequestTypeDef",
    {
        "HumanTaskUiName": str,
    },
)
DeleteHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "DeleteHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
    },
)
DeleteImageRequestRequestTypeDef = TypedDict(
    "DeleteImageRequestRequestTypeDef",
    {
        "ImageName": str,
    },
)
DeleteImageVersionRequestRequestTypeDef = TypedDict(
    "DeleteImageVersionRequestRequestTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
    },
)
DeleteInferenceComponentInputRequestTypeDef = TypedDict(
    "DeleteInferenceComponentInputRequestTypeDef",
    {
        "InferenceComponentName": str,
    },
)
DeleteInferenceExperimentRequestRequestTypeDef = TypedDict(
    "DeleteInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
    },
)
DeleteMlflowTrackingServerRequestRequestTypeDef = TypedDict(
    "DeleteMlflowTrackingServerRequestRequestTypeDef",
    {
        "TrackingServerName": str,
    },
)
DeleteModelBiasJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteModelBiasJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
DeleteModelCardRequestRequestTypeDef = TypedDict(
    "DeleteModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
    },
)
DeleteModelExplainabilityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteModelExplainabilityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
DeleteModelInputRequestTypeDef = TypedDict(
    "DeleteModelInputRequestTypeDef",
    {
        "ModelName": str,
    },
)
DeleteModelPackageGroupInputRequestTypeDef = TypedDict(
    "DeleteModelPackageGroupInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)
DeleteModelPackageGroupPolicyInputRequestTypeDef = TypedDict(
    "DeleteModelPackageGroupPolicyInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)
DeleteModelPackageInputRequestTypeDef = TypedDict(
    "DeleteModelPackageInputRequestTypeDef",
    {
        "ModelPackageName": str,
    },
)
DeleteModelQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteModelQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
DeleteMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "DeleteMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)
DeleteNotebookInstanceInputRequestTypeDef = TypedDict(
    "DeleteNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)
DeleteNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "DeleteNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
    },
)
DeleteOptimizationJobRequestRequestTypeDef = TypedDict(
    "DeleteOptimizationJobRequestRequestTypeDef",
    {
        "OptimizationJobName": str,
    },
)
DeletePipelineRequestRequestTypeDef = TypedDict(
    "DeletePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
        "ClientRequestToken": str,
    },
)
DeleteProjectInputRequestTypeDef = TypedDict(
    "DeleteProjectInputRequestTypeDef",
    {
        "ProjectName": str,
    },
)
DeleteSpaceRequestRequestTypeDef = TypedDict(
    "DeleteSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
    },
)
DeleteStudioLifecycleConfigRequestRequestTypeDef = TypedDict(
    "DeleteStudioLifecycleConfigRequestRequestTypeDef",
    {
        "StudioLifecycleConfigName": str,
    },
)
DeleteTagsInputRequestTypeDef = TypedDict(
    "DeleteTagsInputRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)
DeleteTrialComponentRequestRequestTypeDef = TypedDict(
    "DeleteTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
    },
)
DeleteTrialRequestRequestTypeDef = TypedDict(
    "DeleteTrialRequestRequestTypeDef",
    {
        "TrialName": str,
    },
)
DeleteUserProfileRequestRequestTypeDef = TypedDict(
    "DeleteUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
    },
)
DeleteWorkforceRequestRequestTypeDef = TypedDict(
    "DeleteWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
    },
)
DeleteWorkteamRequestRequestTypeDef = TypedDict(
    "DeleteWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
    },
)
DeployedImageTypeDef = TypedDict(
    "DeployedImageTypeDef",
    {
        "SpecifiedImage": NotRequired[str],
        "ResolvedImage": NotRequired[str],
        "ResolutionTime": NotRequired[datetime],
    },
)
RealTimeInferenceRecommendationTypeDef = TypedDict(
    "RealTimeInferenceRecommendationTypeDef",
    {
        "RecommendationId": str,
        "InstanceType": ProductionVariantInstanceTypeType,
        "Environment": NotRequired[Dict[str, str]],
    },
)
DeviceSelectionConfigOutputTypeDef = TypedDict(
    "DeviceSelectionConfigOutputTypeDef",
    {
        "DeviceSubsetType": DeviceSubsetTypeType,
        "Percentage": NotRequired[int],
        "DeviceNames": NotRequired[List[str]],
        "DeviceNameContains": NotRequired[str],
    },
)
EdgeDeploymentConfigTypeDef = TypedDict(
    "EdgeDeploymentConfigTypeDef",
    {
        "FailureHandlingPolicy": FailureHandlingPolicyType,
    },
)
EdgeDeploymentStatusTypeDef = TypedDict(
    "EdgeDeploymentStatusTypeDef",
    {
        "StageStatus": StageStatusType,
        "EdgeDeploymentSuccessInStage": int,
        "EdgeDeploymentPendingInStage": int,
        "EdgeDeploymentFailedInStage": int,
        "EdgeDeploymentStatusMessage": NotRequired[str],
        "EdgeDeploymentStageStartTime": NotRequired[datetime],
    },
)
DeviceSelectionConfigTypeDef = TypedDict(
    "DeviceSelectionConfigTypeDef",
    {
        "DeviceSubsetType": DeviceSubsetTypeType,
        "Percentage": NotRequired[int],
        "DeviceNames": NotRequired[Sequence[str]],
        "DeviceNameContains": NotRequired[str],
    },
)
DeregisterDevicesRequestRequestTypeDef = TypedDict(
    "DeregisterDevicesRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "DeviceNames": Sequence[str],
    },
)
DerivedInformationTypeDef = TypedDict(
    "DerivedInformationTypeDef",
    {
        "DerivedDataInputConfig": NotRequired[str],
    },
)
DescribeActionRequestRequestTypeDef = TypedDict(
    "DescribeActionRequestRequestTypeDef",
    {
        "ActionName": str,
    },
)
DescribeAlgorithmInputRequestTypeDef = TypedDict(
    "DescribeAlgorithmInputRequestTypeDef",
    {
        "AlgorithmName": str,
    },
)
DescribeAppImageConfigRequestRequestTypeDef = TypedDict(
    "DescribeAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
    },
)
DescribeAppRequestRequestTypeDef = TypedDict(
    "DescribeAppRequestRequestTypeDef",
    {
        "DomainId": str,
        "AppType": AppTypeType,
        "AppName": str,
        "UserProfileName": NotRequired[str],
        "SpaceName": NotRequired[str],
    },
)
DescribeArtifactRequestRequestTypeDef = TypedDict(
    "DescribeArtifactRequestRequestTypeDef",
    {
        "ArtifactArn": str,
    },
)
DescribeAutoMLJobRequestRequestTypeDef = TypedDict(
    "DescribeAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
    },
)
ModelDeployResultTypeDef = TypedDict(
    "ModelDeployResultTypeDef",
    {
        "EndpointName": NotRequired[str],
    },
)
DescribeAutoMLJobV2RequestRequestTypeDef = TypedDict(
    "DescribeAutoMLJobV2RequestRequestTypeDef",
    {
        "AutoMLJobName": str,
    },
)
DescribeClusterNodeRequestRequestTypeDef = TypedDict(
    "DescribeClusterNodeRequestRequestTypeDef",
    {
        "ClusterName": str,
        "NodeId": str,
    },
)
DescribeClusterRequestRequestTypeDef = TypedDict(
    "DescribeClusterRequestRequestTypeDef",
    {
        "ClusterName": str,
    },
)
DescribeCodeRepositoryInputRequestTypeDef = TypedDict(
    "DescribeCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
    },
)
DescribeCompilationJobRequestRequestTypeDef = TypedDict(
    "DescribeCompilationJobRequestRequestTypeDef",
    {
        "CompilationJobName": str,
    },
)
ModelArtifactsTypeDef = TypedDict(
    "ModelArtifactsTypeDef",
    {
        "S3ModelArtifacts": str,
    },
)
ModelDigestsTypeDef = TypedDict(
    "ModelDigestsTypeDef",
    {
        "ArtifactDigest": NotRequired[str],
    },
)
NeoVpcConfigOutputTypeDef = TypedDict(
    "NeoVpcConfigOutputTypeDef",
    {
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
    },
)
DescribeContextRequestRequestTypeDef = TypedDict(
    "DescribeContextRequestRequestTypeDef",
    {
        "ContextName": str,
    },
)
DescribeDataQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeDataQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
DescribeDeviceFleetRequestRequestTypeDef = TypedDict(
    "DescribeDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
    },
)
DescribeDeviceRequestRequestTypeDef = TypedDict(
    "DescribeDeviceRequestRequestTypeDef",
    {
        "DeviceName": str,
        "DeviceFleetName": str,
        "NextToken": NotRequired[str],
    },
)
EdgeModelTypeDef = TypedDict(
    "EdgeModelTypeDef",
    {
        "ModelName": str,
        "ModelVersion": str,
        "LatestSampleTime": NotRequired[datetime],
        "LatestInference": NotRequired[datetime],
    },
)
DescribeDomainRequestRequestTypeDef = TypedDict(
    "DescribeDomainRequestRequestTypeDef",
    {
        "DomainId": str,
    },
)
DescribeEdgeDeploymentPlanRequestRequestTypeDef = TypedDict(
    "DescribeEdgeDeploymentPlanRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
DescribeEdgePackagingJobRequestRequestTypeDef = TypedDict(
    "DescribeEdgePackagingJobRequestRequestTypeDef",
    {
        "EdgePackagingJobName": str,
    },
)
EdgePresetDeploymentOutputTypeDef = TypedDict(
    "EdgePresetDeploymentOutputTypeDef",
    {
        "Type": Literal["GreengrassV2Component"],
        "Artifact": NotRequired[str],
        "Status": NotRequired[EdgePresetDeploymentStatusType],
        "StatusMessage": NotRequired[str],
    },
)
DescribeEndpointConfigInputRequestTypeDef = TypedDict(
    "DescribeEndpointConfigInputRequestTypeDef",
    {
        "EndpointConfigName": str,
    },
)
WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)
DescribeEndpointInputRequestTypeDef = TypedDict(
    "DescribeEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
    },
)
DescribeExperimentRequestRequestTypeDef = TypedDict(
    "DescribeExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
    },
)
ExperimentSourceTypeDef = TypedDict(
    "ExperimentSourceTypeDef",
    {
        "SourceArn": str,
        "SourceType": NotRequired[str],
    },
)
DescribeFeatureGroupRequestRequestTypeDef = TypedDict(
    "DescribeFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "NextToken": NotRequired[str],
    },
)
LastUpdateStatusTypeDef = TypedDict(
    "LastUpdateStatusTypeDef",
    {
        "Status": LastUpdateStatusValueType,
        "FailureReason": NotRequired[str],
    },
)
OfflineStoreStatusTypeDef = TypedDict(
    "OfflineStoreStatusTypeDef",
    {
        "Status": OfflineStoreStatusValueType,
        "BlockedReason": NotRequired[str],
    },
)
ThroughputConfigDescriptionTypeDef = TypedDict(
    "ThroughputConfigDescriptionTypeDef",
    {
        "ThroughputMode": ThroughputModeType,
        "ProvisionedReadCapacityUnits": NotRequired[int],
        "ProvisionedWriteCapacityUnits": NotRequired[int],
    },
)
DescribeFeatureMetadataRequestRequestTypeDef = TypedDict(
    "DescribeFeatureMetadataRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureName": str,
    },
)
FeatureParameterTypeDef = TypedDict(
    "FeatureParameterTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
    },
)
DescribeFlowDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeFlowDefinitionRequestRequestTypeDef",
    {
        "FlowDefinitionName": str,
    },
)
DescribeHubContentRequestRequestTypeDef = TypedDict(
    "DescribeHubContentRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "HubContentName": str,
        "HubContentVersion": NotRequired[str],
    },
)
HubContentDependencyTypeDef = TypedDict(
    "HubContentDependencyTypeDef",
    {
        "DependencyOriginPath": NotRequired[str],
        "DependencyCopyPath": NotRequired[str],
    },
)
DescribeHubRequestRequestTypeDef = TypedDict(
    "DescribeHubRequestRequestTypeDef",
    {
        "HubName": str,
    },
)
DescribeHumanTaskUiRequestRequestTypeDef = TypedDict(
    "DescribeHumanTaskUiRequestRequestTypeDef",
    {
        "HumanTaskUiName": str,
    },
)
UiTemplateInfoTypeDef = TypedDict(
    "UiTemplateInfoTypeDef",
    {
        "Url": NotRequired[str],
        "ContentSha256": NotRequired[str],
    },
)
DescribeHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "DescribeHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
    },
)
HyperParameterTuningJobCompletionDetailsTypeDef = TypedDict(
    "HyperParameterTuningJobCompletionDetailsTypeDef",
    {
        "NumberOfTrainingJobsObjectiveNotImproving": NotRequired[int],
        "ConvergenceDetectedTime": NotRequired[datetime],
    },
)
HyperParameterTuningJobConsumedResourcesTypeDef = TypedDict(
    "HyperParameterTuningJobConsumedResourcesTypeDef",
    {
        "RuntimeInSeconds": NotRequired[int],
    },
)
ObjectiveStatusCountersTypeDef = TypedDict(
    "ObjectiveStatusCountersTypeDef",
    {
        "Succeeded": NotRequired[int],
        "Pending": NotRequired[int],
        "Failed": NotRequired[int],
    },
)
TrainingJobStatusCountersTypeDef = TypedDict(
    "TrainingJobStatusCountersTypeDef",
    {
        "Completed": NotRequired[int],
        "InProgress": NotRequired[int],
        "RetryableError": NotRequired[int],
        "NonRetryableError": NotRequired[int],
        "Stopped": NotRequired[int],
    },
)
DescribeImageRequestRequestTypeDef = TypedDict(
    "DescribeImageRequestRequestTypeDef",
    {
        "ImageName": str,
    },
)
DescribeImageVersionRequestRequestTypeDef = TypedDict(
    "DescribeImageVersionRequestRequestTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
    },
)
DescribeInferenceComponentInputRequestTypeDef = TypedDict(
    "DescribeInferenceComponentInputRequestTypeDef",
    {
        "InferenceComponentName": str,
    },
)
InferenceComponentRuntimeConfigSummaryTypeDef = TypedDict(
    "InferenceComponentRuntimeConfigSummaryTypeDef",
    {
        "DesiredCopyCount": NotRequired[int],
        "CurrentCopyCount": NotRequired[int],
    },
)
DescribeInferenceExperimentRequestRequestTypeDef = TypedDict(
    "DescribeInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
    },
)
EndpointMetadataTypeDef = TypedDict(
    "EndpointMetadataTypeDef",
    {
        "EndpointName": str,
        "EndpointConfigName": NotRequired[str],
        "EndpointStatus": NotRequired[EndpointStatusType],
        "FailureReason": NotRequired[str],
    },
)
InferenceExperimentScheduleOutputTypeDef = TypedDict(
    "InferenceExperimentScheduleOutputTypeDef",
    {
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
    },
)
DescribeInferenceRecommendationsJobRequestRequestTypeDef = TypedDict(
    "DescribeInferenceRecommendationsJobRequestRequestTypeDef",
    {
        "JobName": str,
    },
)
DescribeLabelingJobRequestRequestTypeDef = TypedDict(
    "DescribeLabelingJobRequestRequestTypeDef",
    {
        "LabelingJobName": str,
    },
)
LabelCountersTypeDef = TypedDict(
    "LabelCountersTypeDef",
    {
        "TotalLabeled": NotRequired[int],
        "HumanLabeled": NotRequired[int],
        "MachineLabeled": NotRequired[int],
        "FailedNonRetryableError": NotRequired[int],
        "Unlabeled": NotRequired[int],
    },
)
LabelingJobOutputTypeDef = TypedDict(
    "LabelingJobOutputTypeDef",
    {
        "OutputDatasetS3Uri": str,
        "FinalActiveLearningModelArn": NotRequired[str],
    },
)
DescribeLineageGroupRequestRequestTypeDef = TypedDict(
    "DescribeLineageGroupRequestRequestTypeDef",
    {
        "LineageGroupName": str,
    },
)
DescribeMlflowTrackingServerRequestRequestTypeDef = TypedDict(
    "DescribeMlflowTrackingServerRequestRequestTypeDef",
    {
        "TrackingServerName": str,
    },
)
DescribeModelBiasJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeModelBiasJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
ModelBiasAppSpecificationOutputTypeDef = TypedDict(
    "ModelBiasAppSpecificationOutputTypeDef",
    {
        "ImageUri": str,
        "ConfigUri": str,
        "Environment": NotRequired[Dict[str, str]],
    },
)
DescribeModelCardExportJobRequestRequestTypeDef = TypedDict(
    "DescribeModelCardExportJobRequestRequestTypeDef",
    {
        "ModelCardExportJobArn": str,
    },
)
ModelCardExportArtifactsTypeDef = TypedDict(
    "ModelCardExportArtifactsTypeDef",
    {
        "S3ExportArtifacts": str,
    },
)
DescribeModelCardRequestRequestTypeDef = TypedDict(
    "DescribeModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "ModelCardVersion": NotRequired[int],
    },
)
DescribeModelExplainabilityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeModelExplainabilityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
ModelExplainabilityAppSpecificationOutputTypeDef = TypedDict(
    "ModelExplainabilityAppSpecificationOutputTypeDef",
    {
        "ImageUri": str,
        "ConfigUri": str,
        "Environment": NotRequired[Dict[str, str]],
    },
)
DescribeModelInputRequestTypeDef = TypedDict(
    "DescribeModelInputRequestTypeDef",
    {
        "ModelName": str,
    },
)
DescribeModelPackageGroupInputRequestTypeDef = TypedDict(
    "DescribeModelPackageGroupInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)
DescribeModelPackageInputRequestTypeDef = TypedDict(
    "DescribeModelPackageInputRequestTypeDef",
    {
        "ModelPackageName": str,
    },
)
DescribeModelQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeModelQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)
ModelQualityAppSpecificationOutputTypeDef = TypedDict(
    "ModelQualityAppSpecificationOutputTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
        "ProblemType": NotRequired[MonitoringProblemTypeType],
        "Environment": NotRequired[Dict[str, str]],
    },
)
DescribeMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "DescribeMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)
MonitoringExecutionSummaryTypeDef = TypedDict(
    "MonitoringExecutionSummaryTypeDef",
    {
        "MonitoringScheduleName": str,
        "ScheduledTime": datetime,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "MonitoringExecutionStatus": ExecutionStatusType,
        "ProcessingJobArn": NotRequired[str],
        "EndpointName": NotRequired[str],
        "FailureReason": NotRequired[str],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)
DescribeNotebookInstanceInputRequestTypeDef = TypedDict(
    "DescribeNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)
DescribeNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "DescribeNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
    },
)
DescribeOptimizationJobRequestRequestTypeDef = TypedDict(
    "DescribeOptimizationJobRequestRequestTypeDef",
    {
        "OptimizationJobName": str,
    },
)
OptimizationOutputTypeDef = TypedDict(
    "OptimizationOutputTypeDef",
    {
        "RecommendedInferenceImage": NotRequired[str],
    },
)
OptimizationVpcConfigOutputTypeDef = TypedDict(
    "OptimizationVpcConfigOutputTypeDef",
    {
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
    },
)
DescribePipelineDefinitionForExecutionRequestRequestTypeDef = TypedDict(
    "DescribePipelineDefinitionForExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
    },
)
DescribePipelineExecutionRequestRequestTypeDef = TypedDict(
    "DescribePipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
    },
)
PipelineExperimentConfigTypeDef = TypedDict(
    "PipelineExperimentConfigTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
    },
)
DescribePipelineRequestRequestTypeDef = TypedDict(
    "DescribePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
    },
)
DescribeProcessingJobRequestRequestTypeDef = TypedDict(
    "DescribeProcessingJobRequestRequestTypeDef",
    {
        "ProcessingJobName": str,
    },
)
DescribeProjectInputRequestTypeDef = TypedDict(
    "DescribeProjectInputRequestTypeDef",
    {
        "ProjectName": str,
    },
)
ServiceCatalogProvisionedProductDetailsTypeDef = TypedDict(
    "ServiceCatalogProvisionedProductDetailsTypeDef",
    {
        "ProvisionedProductId": NotRequired[str],
        "ProvisionedProductStatusMessage": NotRequired[str],
    },
)
DescribeSpaceRequestRequestTypeDef = TypedDict(
    "DescribeSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
    },
)
DescribeStudioLifecycleConfigRequestRequestTypeDef = TypedDict(
    "DescribeStudioLifecycleConfigRequestRequestTypeDef",
    {
        "StudioLifecycleConfigName": str,
    },
)
DescribeSubscribedWorkteamRequestRequestTypeDef = TypedDict(
    "DescribeSubscribedWorkteamRequestRequestTypeDef",
    {
        "WorkteamArn": str,
    },
)
SubscribedWorkteamTypeDef = TypedDict(
    "SubscribedWorkteamTypeDef",
    {
        "WorkteamArn": str,
        "MarketplaceTitle": NotRequired[str],
        "SellerName": NotRequired[str],
        "MarketplaceDescription": NotRequired[str],
        "ListingId": NotRequired[str],
    },
)
DescribeTrainingJobRequestRequestTypeDef = TypedDict(
    "DescribeTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
    },
)
MetricDataTypeDef = TypedDict(
    "MetricDataTypeDef",
    {
        "MetricName": NotRequired[str],
        "Value": NotRequired[float],
        "Timestamp": NotRequired[datetime],
    },
)
ProfilerConfigOutputTypeDef = TypedDict(
    "ProfilerConfigOutputTypeDef",
    {
        "S3OutputPath": NotRequired[str],
        "ProfilingIntervalInMilliseconds": NotRequired[int],
        "ProfilingParameters": NotRequired[Dict[str, str]],
        "DisableProfiler": NotRequired[bool],
    },
)
ProfilerRuleConfigurationOutputTypeDef = TypedDict(
    "ProfilerRuleConfigurationOutputTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Dict[str, str]],
    },
)
ProfilerRuleEvaluationStatusTypeDef = TypedDict(
    "ProfilerRuleEvaluationStatusTypeDef",
    {
        "RuleConfigurationName": NotRequired[str],
        "RuleEvaluationJobArn": NotRequired[str],
        "RuleEvaluationStatus": NotRequired[RuleEvaluationStatusType],
        "StatusDetails": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
    },
)
SecondaryStatusTransitionTypeDef = TypedDict(
    "SecondaryStatusTransitionTypeDef",
    {
        "Status": SecondaryStatusType,
        "StartTime": datetime,
        "EndTime": NotRequired[datetime],
        "StatusMessage": NotRequired[str],
    },
)
WarmPoolStatusTypeDef = TypedDict(
    "WarmPoolStatusTypeDef",
    {
        "Status": WarmPoolResourceStatusType,
        "ResourceRetainedBillableTimeInSeconds": NotRequired[int],
        "ReusedByJob": NotRequired[str],
    },
)
DescribeTransformJobRequestRequestTypeDef = TypedDict(
    "DescribeTransformJobRequestRequestTypeDef",
    {
        "TransformJobName": str,
    },
)
DescribeTrialComponentRequestRequestTypeDef = TypedDict(
    "DescribeTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
    },
)
TrialComponentMetricSummaryTypeDef = TypedDict(
    "TrialComponentMetricSummaryTypeDef",
    {
        "MetricName": NotRequired[str],
        "SourceArn": NotRequired[str],
        "TimeStamp": NotRequired[datetime],
        "Max": NotRequired[float],
        "Min": NotRequired[float],
        "Last": NotRequired[float],
        "Count": NotRequired[int],
        "Avg": NotRequired[float],
        "StdDev": NotRequired[float],
    },
)
TrialComponentSourceTypeDef = TypedDict(
    "TrialComponentSourceTypeDef",
    {
        "SourceArn": str,
        "SourceType": NotRequired[str],
    },
)
DescribeTrialRequestRequestTypeDef = TypedDict(
    "DescribeTrialRequestRequestTypeDef",
    {
        "TrialName": str,
    },
)
TrialSourceTypeDef = TypedDict(
    "TrialSourceTypeDef",
    {
        "SourceArn": str,
        "SourceType": NotRequired[str],
    },
)
DescribeUserProfileRequestRequestTypeDef = TypedDict(
    "DescribeUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
    },
)
DescribeWorkforceRequestRequestTypeDef = TypedDict(
    "DescribeWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
    },
)
DescribeWorkteamRequestRequestTypeDef = TypedDict(
    "DescribeWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
    },
)
ProductionVariantServerlessUpdateConfigTypeDef = TypedDict(
    "ProductionVariantServerlessUpdateConfigTypeDef",
    {
        "MaxConcurrency": NotRequired[int],
        "ProvisionedConcurrency": NotRequired[int],
    },
)
DeviceDeploymentSummaryTypeDef = TypedDict(
    "DeviceDeploymentSummaryTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "EdgeDeploymentPlanName": str,
        "StageName": str,
        "DeviceName": str,
        "DeviceArn": str,
        "DeployedStageName": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
        "DeviceDeploymentStatus": NotRequired[DeviceDeploymentStatusType],
        "DeviceDeploymentStatusMessage": NotRequired[str],
        "Description": NotRequired[str],
        "DeploymentStartTime": NotRequired[datetime],
    },
)
DeviceFleetSummaryTypeDef = TypedDict(
    "DeviceFleetSummaryTypeDef",
    {
        "DeviceFleetArn": str,
        "DeviceFleetName": str,
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
DeviceStatsTypeDef = TypedDict(
    "DeviceStatsTypeDef",
    {
        "ConnectedDeviceCount": int,
        "RegisteredDeviceCount": int,
    },
)
EdgeModelSummaryTypeDef = TypedDict(
    "EdgeModelSummaryTypeDef",
    {
        "ModelName": str,
        "ModelVersion": str,
    },
)
DeviceTypeDef = TypedDict(
    "DeviceTypeDef",
    {
        "DeviceName": str,
        "Description": NotRequired[str],
        "IotThingName": NotRequired[str],
    },
)
DisassociateTrialComponentRequestRequestTypeDef = TypedDict(
    "DisassociateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "TrialName": str,
    },
)
DockerSettingsOutputTypeDef = TypedDict(
    "DockerSettingsOutputTypeDef",
    {
        "EnableDockerAccess": NotRequired[FeatureStatusType],
        "VpcOnlyTrustedAccounts": NotRequired[List[str]],
    },
)
DockerSettingsTypeDef = TypedDict(
    "DockerSettingsTypeDef",
    {
        "EnableDockerAccess": NotRequired[FeatureStatusType],
        "VpcOnlyTrustedAccounts": NotRequired[Sequence[str]],
    },
)
DomainDetailsTypeDef = TypedDict(
    "DomainDetailsTypeDef",
    {
        "DomainArn": NotRequired[str],
        "DomainId": NotRequired[str],
        "DomainName": NotRequired[str],
        "Status": NotRequired[DomainStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "Url": NotRequired[str],
    },
)
FileSourceTypeDef = TypedDict(
    "FileSourceTypeDef",
    {
        "S3Uri": str,
        "ContentType": NotRequired[str],
        "ContentDigest": NotRequired[str],
    },
)
EMRStepMetadataTypeDef = TypedDict(
    "EMRStepMetadataTypeDef",
    {
        "ClusterId": NotRequired[str],
        "StepId": NotRequired[str],
        "StepName": NotRequired[str],
        "LogFilePath": NotRequired[str],
    },
)
EbsStorageSettingsTypeDef = TypedDict(
    "EbsStorageSettingsTypeDef",
    {
        "EbsVolumeSizeInGb": int,
    },
)
EdgeDeploymentPlanSummaryTypeDef = TypedDict(
    "EdgeDeploymentPlanSummaryTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "EdgeDeploymentPlanName": str,
        "DeviceFleetName": str,
        "EdgeDeploymentSuccess": int,
        "EdgeDeploymentPending": int,
        "EdgeDeploymentFailed": int,
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
EdgeModelStatTypeDef = TypedDict(
    "EdgeModelStatTypeDef",
    {
        "ModelName": str,
        "ModelVersion": str,
        "OfflineDeviceCount": int,
        "ConnectedDeviceCount": int,
        "ActiveDeviceCount": int,
        "SamplingDeviceCount": int,
    },
)
EdgePackagingJobSummaryTypeDef = TypedDict(
    "EdgePackagingJobSummaryTypeDef",
    {
        "EdgePackagingJobArn": str,
        "EdgePackagingJobName": str,
        "EdgePackagingJobStatus": EdgePackagingJobStatusType,
        "CompilationJobName": NotRequired[str],
        "ModelName": NotRequired[str],
        "ModelVersion": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
EdgeTypeDef = TypedDict(
    "EdgeTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
    },
)
EndpointConfigSummaryTypeDef = TypedDict(
    "EndpointConfigSummaryTypeDef",
    {
        "EndpointConfigName": str,
        "EndpointConfigArn": str,
        "CreationTime": datetime,
    },
)
EndpointInfoTypeDef = TypedDict(
    "EndpointInfoTypeDef",
    {
        "EndpointName": NotRequired[str],
    },
)
ProductionVariantServerlessConfigTypeDef = TypedDict(
    "ProductionVariantServerlessConfigTypeDef",
    {
        "MemorySizeInMB": int,
        "MaxConcurrency": int,
        "ProvisionedConcurrency": NotRequired[int],
    },
)
InferenceMetricsTypeDef = TypedDict(
    "InferenceMetricsTypeDef",
    {
        "MaxInvocations": int,
        "ModelLatency": int,
    },
)
EndpointSummaryTypeDef = TypedDict(
    "EndpointSummaryTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "EndpointStatus": EndpointStatusType,
    },
)
EnvironmentParameterTypeDef = TypedDict(
    "EnvironmentParameterTypeDef",
    {
        "Key": str,
        "ValueType": str,
        "Value": str,
    },
)
FailStepMetadataTypeDef = TypedDict(
    "FailStepMetadataTypeDef",
    {
        "ErrorMessage": NotRequired[str],
    },
)
FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": str,
        "Operator": NotRequired[OperatorType],
        "Value": NotRequired[str],
    },
)
FinalHyperParameterTuningJobObjectiveMetricTypeDef = TypedDict(
    "FinalHyperParameterTuningJobObjectiveMetricTypeDef",
    {
        "MetricName": str,
        "Value": float,
        "Type": NotRequired[HyperParameterTuningJobObjectiveTypeType],
    },
)
FlowDefinitionSummaryTypeDef = TypedDict(
    "FlowDefinitionSummaryTypeDef",
    {
        "FlowDefinitionName": str,
        "FlowDefinitionArn": str,
        "FlowDefinitionStatus": FlowDefinitionStatusType,
        "CreationTime": datetime,
        "FailureReason": NotRequired[str],
    },
)
GetDeviceFleetReportRequestRequestTypeDef = TypedDict(
    "GetDeviceFleetReportRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
    },
)
GetLineageGroupPolicyRequestRequestTypeDef = TypedDict(
    "GetLineageGroupPolicyRequestRequestTypeDef",
    {
        "LineageGroupName": str,
    },
)
GetModelPackageGroupPolicyInputRequestTypeDef = TypedDict(
    "GetModelPackageGroupPolicyInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)
ScalingPolicyObjectiveTypeDef = TypedDict(
    "ScalingPolicyObjectiveTypeDef",
    {
        "MinInvocationsPerMinute": NotRequired[int],
        "MaxInvocationsPerMinute": NotRequired[int],
    },
)
ScalingPolicyMetricTypeDef = TypedDict(
    "ScalingPolicyMetricTypeDef",
    {
        "InvocationsPerInstance": NotRequired[int],
        "ModelLatency": NotRequired[int],
    },
)
PropertyNameSuggestionTypeDef = TypedDict(
    "PropertyNameSuggestionTypeDef",
    {
        "PropertyName": NotRequired[str],
    },
)
GitConfigForUpdateTypeDef = TypedDict(
    "GitConfigForUpdateTypeDef",
    {
        "SecretArn": NotRequired[str],
    },
)
HolidayConfigAttributesTypeDef = TypedDict(
    "HolidayConfigAttributesTypeDef",
    {
        "CountryCode": NotRequired[str],
    },
)
HubContentInfoTypeDef = TypedDict(
    "HubContentInfoTypeDef",
    {
        "HubContentName": str,
        "HubContentArn": str,
        "HubContentVersion": str,
        "HubContentType": HubContentTypeType,
        "DocumentSchemaVersion": str,
        "HubContentStatus": HubContentStatusType,
        "CreationTime": datetime,
        "SageMakerPublicHubContentArn": NotRequired[str],
        "HubContentDisplayName": NotRequired[str],
        "HubContentDescription": NotRequired[str],
        "SupportStatus": NotRequired[HubContentSupportStatusType],
        "HubContentSearchKeywords": NotRequired[List[str]],
        "OriginalCreationTime": NotRequired[datetime],
    },
)
HubInfoTypeDef = TypedDict(
    "HubInfoTypeDef",
    {
        "HubName": str,
        "HubArn": str,
        "HubStatus": HubStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "HubDisplayName": NotRequired[str],
        "HubDescription": NotRequired[str],
        "HubSearchKeywords": NotRequired[List[str]],
    },
)
HumanLoopActivationConditionsConfigTypeDef = TypedDict(
    "HumanLoopActivationConditionsConfigTypeDef",
    {
        "HumanLoopActivationConditions": str,
    },
)
UiConfigTypeDef = TypedDict(
    "UiConfigTypeDef",
    {
        "UiTemplateS3Uri": NotRequired[str],
        "HumanTaskUiArn": NotRequired[str],
    },
)
HumanTaskUiSummaryTypeDef = TypedDict(
    "HumanTaskUiSummaryTypeDef",
    {
        "HumanTaskUiName": str,
        "HumanTaskUiArn": str,
        "CreationTime": datetime,
    },
)
HyperParameterTuningJobObjectiveTypeDef = TypedDict(
    "HyperParameterTuningJobObjectiveTypeDef",
    {
        "Type": HyperParameterTuningJobObjectiveTypeType,
        "MetricName": str,
    },
)
VpcConfigExtraOutputTypeDef = TypedDict(
    "VpcConfigExtraOutputTypeDef",
    {
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
    },
)
HyperParameterTuningInstanceConfigTypeDef = TypedDict(
    "HyperParameterTuningInstanceConfigTypeDef",
    {
        "InstanceType": TrainingInstanceTypeType,
        "InstanceCount": int,
        "VolumeSizeInGB": int,
    },
)
ResourceLimitsTypeDef = TypedDict(
    "ResourceLimitsTypeDef",
    {
        "MaxParallelTrainingJobs": int,
        "MaxNumberOfTrainingJobs": NotRequired[int],
        "MaxRuntimeInSeconds": NotRequired[int],
    },
)
HyperbandStrategyConfigTypeDef = TypedDict(
    "HyperbandStrategyConfigTypeDef",
    {
        "MinResource": NotRequired[int],
        "MaxResource": NotRequired[int],
    },
)
ParentHyperParameterTuningJobTypeDef = TypedDict(
    "ParentHyperParameterTuningJobTypeDef",
    {
        "HyperParameterTuningJobName": NotRequired[str],
    },
)
IamIdentityTypeDef = TypedDict(
    "IamIdentityTypeDef",
    {
        "Arn": NotRequired[str],
        "PrincipalId": NotRequired[str],
        "SourceIdentity": NotRequired[str],
    },
)
IamPolicyConstraintsTypeDef = TypedDict(
    "IamPolicyConstraintsTypeDef",
    {
        "SourceIp": NotRequired[EnabledOrDisabledType],
        "VpcSourceIp": NotRequired[EnabledOrDisabledType],
    },
)
RepositoryAuthConfigTypeDef = TypedDict(
    "RepositoryAuthConfigTypeDef",
    {
        "RepositoryCredentialsProviderArn": str,
    },
)
ImageTypeDef = TypedDict(
    "ImageTypeDef",
    {
        "CreationTime": datetime,
        "ImageArn": str,
        "ImageName": str,
        "ImageStatus": ImageStatusType,
        "LastModifiedTime": datetime,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "FailureReason": NotRequired[str],
    },
)
ImageVersionTypeDef = TypedDict(
    "ImageVersionTypeDef",
    {
        "CreationTime": datetime,
        "ImageArn": str,
        "ImageVersionArn": str,
        "ImageVersionStatus": ImageVersionStatusType,
        "LastModifiedTime": datetime,
        "Version": int,
        "FailureReason": NotRequired[str],
    },
)
InferenceComponentComputeResourceRequirementsTypeDef = TypedDict(
    "InferenceComponentComputeResourceRequirementsTypeDef",
    {
        "MinMemoryRequiredInMb": int,
        "NumberOfCpuCoresRequired": NotRequired[float],
        "NumberOfAcceleratorDevicesRequired": NotRequired[float],
        "MaxMemoryRequiredInMb": NotRequired[int],
    },
)
InferenceComponentContainerSpecificationTypeDef = TypedDict(
    "InferenceComponentContainerSpecificationTypeDef",
    {
        "Image": NotRequired[str],
        "ArtifactUrl": NotRequired[str],
        "Environment": NotRequired[Mapping[str, str]],
    },
)
InferenceComponentStartupParametersTypeDef = TypedDict(
    "InferenceComponentStartupParametersTypeDef",
    {
        "ModelDataDownloadTimeoutInSeconds": NotRequired[int],
        "ContainerStartupHealthCheckTimeoutInSeconds": NotRequired[int],
    },
)
InferenceComponentSummaryTypeDef = TypedDict(
    "InferenceComponentSummaryTypeDef",
    {
        "CreationTime": datetime,
        "InferenceComponentArn": str,
        "InferenceComponentName": str,
        "EndpointArn": str,
        "EndpointName": str,
        "VariantName": str,
        "LastModifiedTime": datetime,
        "InferenceComponentStatus": NotRequired[InferenceComponentStatusType],
    },
)
InferenceExperimentScheduleExtraOutputTypeDef = TypedDict(
    "InferenceExperimentScheduleExtraOutputTypeDef",
    {
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
    },
)
InferenceHubAccessConfigTypeDef = TypedDict(
    "InferenceHubAccessConfigTypeDef",
    {
        "HubContentArn": str,
    },
)
RecommendationMetricsTypeDef = TypedDict(
    "RecommendationMetricsTypeDef",
    {
        "CostPerHour": NotRequired[float],
        "CostPerInference": NotRequired[float],
        "MaxInvocations": NotRequired[int],
        "ModelLatency": NotRequired[int],
        "CpuUtilization": NotRequired[float],
        "MemoryUtilization": NotRequired[float],
        "ModelSetupTime": NotRequired[int],
    },
)
InferenceRecommendationsJobTypeDef = TypedDict(
    "InferenceRecommendationsJobTypeDef",
    {
        "JobName": str,
        "JobDescription": str,
        "JobType": RecommendationJobTypeType,
        "JobArn": str,
        "Status": RecommendationJobStatusType,
        "CreationTime": datetime,
        "RoleArn": str,
        "LastModifiedTime": datetime,
        "CompletionTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "ModelName": NotRequired[str],
        "SamplePayloadUrl": NotRequired[str],
        "ModelPackageVersionArn": NotRequired[str],
    },
)
InstanceGroupTypeDef = TypedDict(
    "InstanceGroupTypeDef",
    {
        "InstanceType": TrainingInstanceTypeType,
        "InstanceCount": int,
        "InstanceGroupName": str,
    },
)
IntegerParameterRangeSpecificationTypeDef = TypedDict(
    "IntegerParameterRangeSpecificationTypeDef",
    {
        "MinValue": str,
        "MaxValue": str,
    },
)
IntegerParameterRangeTypeDef = TypedDict(
    "IntegerParameterRangeTypeDef",
    {
        "Name": str,
        "MinValue": str,
        "MaxValue": str,
        "ScalingType": NotRequired[HyperParameterScalingTypeType],
    },
)
KernelSpecTypeDef = TypedDict(
    "KernelSpecTypeDef",
    {
        "Name": str,
        "DisplayName": NotRequired[str],
    },
)
LabelCountersForWorkteamTypeDef = TypedDict(
    "LabelCountersForWorkteamTypeDef",
    {
        "HumanLabeled": NotRequired[int],
        "PendingHuman": NotRequired[int],
        "Total": NotRequired[int],
    },
)
LabelingJobDataAttributesExtraOutputTypeDef = TypedDict(
    "LabelingJobDataAttributesExtraOutputTypeDef",
    {
        "ContentClassifiers": NotRequired[List[ContentClassifierType]],
    },
)
LabelingJobDataAttributesOutputTypeDef = TypedDict(
    "LabelingJobDataAttributesOutputTypeDef",
    {
        "ContentClassifiers": NotRequired[List[ContentClassifierType]],
    },
)
LabelingJobDataAttributesTypeDef = TypedDict(
    "LabelingJobDataAttributesTypeDef",
    {
        "ContentClassifiers": NotRequired[Sequence[ContentClassifierType]],
    },
)
LabelingJobS3DataSourceTypeDef = TypedDict(
    "LabelingJobS3DataSourceTypeDef",
    {
        "ManifestS3Uri": str,
    },
)
LabelingJobSnsDataSourceTypeDef = TypedDict(
    "LabelingJobSnsDataSourceTypeDef",
    {
        "SnsTopicArn": str,
    },
)
LineageGroupSummaryTypeDef = TypedDict(
    "LineageGroupSummaryTypeDef",
    {
        "LineageGroupArn": NotRequired[str],
        "LineageGroupName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
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
ListAliasesRequestRequestTypeDef = TypedDict(
    "ListAliasesRequestRequestTypeDef",
    {
        "ImageName": str,
        "Alias": NotRequired[str],
        "Version": NotRequired[int],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListAppsRequestRequestTypeDef = TypedDict(
    "ListAppsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameEquals": NotRequired[str],
        "SpaceNameEquals": NotRequired[str],
    },
)
ListCandidatesForAutoMLJobRequestRequestTypeDef = TypedDict(
    "ListCandidatesForAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
        "StatusEquals": NotRequired[CandidateStatusType],
        "CandidateNameEquals": NotRequired[str],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[CandidateSortByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
MonitoringJobDefinitionSummaryTypeDef = TypedDict(
    "MonitoringJobDefinitionSummaryTypeDef",
    {
        "MonitoringJobDefinitionName": str,
        "MonitoringJobDefinitionArn": str,
        "CreationTime": datetime,
        "EndpointName": str,
    },
)
ListDomainsRequestRequestTypeDef = TypedDict(
    "ListDomainsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListInferenceRecommendationsJobStepsRequestRequestTypeDef = TypedDict(
    "ListInferenceRecommendationsJobStepsRequestRequestTypeDef",
    {
        "JobName": str,
        "Status": NotRequired[RecommendationJobStatusType],
        "StepType": NotRequired[Literal["BENCHMARK"]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
TrackingServerSummaryTypeDef = TypedDict(
    "TrackingServerSummaryTypeDef",
    {
        "TrackingServerArn": NotRequired[str],
        "TrackingServerName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "TrackingServerStatus": NotRequired[TrackingServerStatusType],
        "IsActive": NotRequired[IsTrackingServerActiveType],
        "MlflowVersion": NotRequired[str],
    },
)
ModelCardExportJobSummaryTypeDef = TypedDict(
    "ModelCardExportJobSummaryTypeDef",
    {
        "ModelCardExportJobName": str,
        "ModelCardExportJobArn": str,
        "Status": ModelCardExportJobStatusType,
        "ModelCardName": str,
        "ModelCardVersion": int,
        "CreatedAt": datetime,
        "LastModifiedAt": datetime,
    },
)
ModelCardVersionSummaryTypeDef = TypedDict(
    "ModelCardVersionSummaryTypeDef",
    {
        "ModelCardName": str,
        "ModelCardArn": str,
        "ModelCardStatus": ModelCardStatusType,
        "ModelCardVersion": int,
        "CreationTime": datetime,
        "LastModifiedTime": NotRequired[datetime],
    },
)
ModelCardSummaryTypeDef = TypedDict(
    "ModelCardSummaryTypeDef",
    {
        "ModelCardName": str,
        "ModelCardArn": str,
        "ModelCardStatus": ModelCardStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": NotRequired[datetime],
    },
)
ModelMetadataSummaryTypeDef = TypedDict(
    "ModelMetadataSummaryTypeDef",
    {
        "Domain": str,
        "Framework": str,
        "Task": str,
        "Model": str,
        "FrameworkVersion": str,
    },
)
ModelPackageGroupSummaryTypeDef = TypedDict(
    "ModelPackageGroupSummaryTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageGroupArn": str,
        "CreationTime": datetime,
        "ModelPackageGroupStatus": ModelPackageGroupStatusType,
        "ModelPackageGroupDescription": NotRequired[str],
    },
)
ModelPackageSummaryTypeDef = TypedDict(
    "ModelPackageSummaryTypeDef",
    {
        "ModelPackageArn": str,
        "CreationTime": datetime,
        "ModelPackageStatus": ModelPackageStatusType,
        "ModelPackageName": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageVersion": NotRequired[int],
        "ModelPackageDescription": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
    },
)
ModelSummaryTypeDef = TypedDict(
    "ModelSummaryTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "CreationTime": datetime,
    },
)
MonitoringAlertHistorySummaryTypeDef = TypedDict(
    "MonitoringAlertHistorySummaryTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringAlertName": str,
        "CreationTime": datetime,
        "AlertStatus": MonitoringAlertStatusType,
    },
)
ListMonitoringAlertsRequestRequestTypeDef = TypedDict(
    "ListMonitoringAlertsRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
MonitoringScheduleSummaryTypeDef = TypedDict(
    "MonitoringScheduleSummaryTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringScheduleArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "MonitoringScheduleStatus": ScheduleStatusType,
        "EndpointName": NotRequired[str],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)
NotebookInstanceLifecycleConfigSummaryTypeDef = TypedDict(
    "NotebookInstanceLifecycleConfigSummaryTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
        "NotebookInstanceLifecycleConfigArn": str,
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
NotebookInstanceSummaryTypeDef = TypedDict(
    "NotebookInstanceSummaryTypeDef",
    {
        "NotebookInstanceName": str,
        "NotebookInstanceArn": str,
        "NotebookInstanceStatus": NotRequired[NotebookInstanceStatusType],
        "Url": NotRequired[str],
        "InstanceType": NotRequired[InstanceTypeType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "NotebookInstanceLifecycleConfigName": NotRequired[str],
        "DefaultCodeRepository": NotRequired[str],
        "AdditionalCodeRepositories": NotRequired[List[str]],
    },
)
OptimizationJobSummaryTypeDef = TypedDict(
    "OptimizationJobSummaryTypeDef",
    {
        "OptimizationJobName": str,
        "OptimizationJobArn": str,
        "CreationTime": datetime,
        "OptimizationJobStatus": OptimizationJobStatusType,
        "DeploymentInstanceType": OptimizationJobDeploymentInstanceTypeType,
        "OptimizationTypes": List[str],
        "OptimizationStartTime": NotRequired[datetime],
        "OptimizationEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
ListPipelineExecutionStepsRequestRequestTypeDef = TypedDict(
    "ListPipelineExecutionStepsRequestRequestTypeDef",
    {
        "PipelineExecutionArn": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
    },
)
PipelineExecutionSummaryTypeDef = TypedDict(
    "PipelineExecutionSummaryTypeDef",
    {
        "PipelineExecutionArn": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "PipelineExecutionStatus": NotRequired[PipelineExecutionStatusType],
        "PipelineExecutionDescription": NotRequired[str],
        "PipelineExecutionDisplayName": NotRequired[str],
        "PipelineExecutionFailureReason": NotRequired[str],
    },
)
ListPipelineParametersForExecutionRequestRequestTypeDef = TypedDict(
    "ListPipelineParametersForExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ParameterTypeDef = TypedDict(
    "ParameterTypeDef",
    {
        "Name": str,
        "Value": str,
    },
)
PipelineSummaryTypeDef = TypedDict(
    "PipelineSummaryTypeDef",
    {
        "PipelineArn": NotRequired[str],
        "PipelineName": NotRequired[str],
        "PipelineDisplayName": NotRequired[str],
        "PipelineDescription": NotRequired[str],
        "RoleArn": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "LastExecutionTime": NotRequired[datetime],
    },
)
ProcessingJobSummaryTypeDef = TypedDict(
    "ProcessingJobSummaryTypeDef",
    {
        "ProcessingJobName": str,
        "ProcessingJobArn": str,
        "CreationTime": datetime,
        "ProcessingJobStatus": ProcessingJobStatusType,
        "ProcessingEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "ExitMessage": NotRequired[str],
    },
)
ProjectSummaryTypeDef = TypedDict(
    "ProjectSummaryTypeDef",
    {
        "ProjectName": str,
        "ProjectArn": str,
        "ProjectId": str,
        "CreationTime": datetime,
        "ProjectStatus": ProjectStatusType,
        "ProjectDescription": NotRequired[str],
    },
)
ResourceCatalogTypeDef = TypedDict(
    "ResourceCatalogTypeDef",
    {
        "ResourceCatalogArn": str,
        "ResourceCatalogName": str,
        "Description": str,
        "CreationTime": datetime,
    },
)
ListSpacesRequestRequestTypeDef = TypedDict(
    "ListSpacesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[SpaceSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "SpaceNameContains": NotRequired[str],
    },
)
ListStageDevicesRequestRequestTypeDef = TypedDict(
    "ListStageDevicesRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ExcludeDevicesDeployedInOtherStage": NotRequired[bool],
    },
)
StudioLifecycleConfigDetailsTypeDef = TypedDict(
    "StudioLifecycleConfigDetailsTypeDef",
    {
        "StudioLifecycleConfigArn": NotRequired[str],
        "StudioLifecycleConfigName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "StudioLifecycleConfigAppType": NotRequired[StudioLifecycleConfigAppTypeType],
    },
)
ListSubscribedWorkteamsRequestRequestTypeDef = TypedDict(
    "ListSubscribedWorkteamsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListTagsInputRequestTypeDef = TypedDict(
    "ListTagsInputRequestTypeDef",
    {
        "ResourceArn": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListTrainingJobsForHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "ListTrainingJobsForHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[TrainingJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
TransformJobSummaryTypeDef = TypedDict(
    "TransformJobSummaryTypeDef",
    {
        "TransformJobName": str,
        "TransformJobArn": str,
        "CreationTime": datetime,
        "TransformJobStatus": TransformJobStatusType,
        "TransformEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
    },
)
ListUserProfilesRequestRequestTypeDef = TypedDict(
    "ListUserProfilesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[UserProfileSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameContains": NotRequired[str],
    },
)
UserProfileDetailsTypeDef = TypedDict(
    "UserProfileDetailsTypeDef",
    {
        "DomainId": NotRequired[str],
        "UserProfileName": NotRequired[str],
        "Status": NotRequired[UserProfileStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
ListWorkforcesRequestRequestTypeDef = TypedDict(
    "ListWorkforcesRequestRequestTypeDef",
    {
        "SortBy": NotRequired[ListWorkforcesSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListWorkteamsRequestRequestTypeDef = TypedDict(
    "ListWorkteamsRequestRequestTypeDef",
    {
        "SortBy": NotRequired[ListWorkteamsSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
OidcMemberDefinitionExtraOutputTypeDef = TypedDict(
    "OidcMemberDefinitionExtraOutputTypeDef",
    {
        "Groups": NotRequired[List[str]],
    },
)
OidcMemberDefinitionOutputTypeDef = TypedDict(
    "OidcMemberDefinitionOutputTypeDef",
    {
        "Groups": NotRequired[List[str]],
    },
)
OidcMemberDefinitionTypeDef = TypedDict(
    "OidcMemberDefinitionTypeDef",
    {
        "Groups": NotRequired[Sequence[str]],
    },
)
PredefinedMetricSpecificationTypeDef = TypedDict(
    "PredefinedMetricSpecificationTypeDef",
    {
        "PredefinedMetricType": NotRequired[str],
    },
)
ModelAccessConfigTypeDef = TypedDict(
    "ModelAccessConfigTypeDef",
    {
        "AcceptEula": bool,
    },
)
MonitoringGroundTruthS3InputTypeDef = TypedDict(
    "MonitoringGroundTruthS3InputTypeDef",
    {
        "S3Uri": NotRequired[str],
    },
)
ModelCompilationConfigOutputTypeDef = TypedDict(
    "ModelCompilationConfigOutputTypeDef",
    {
        "Image": NotRequired[str],
        "OverrideEnvironment": NotRequired[Dict[str, str]],
    },
)
ModelCompilationConfigTypeDef = TypedDict(
    "ModelCompilationConfigTypeDef",
    {
        "Image": NotRequired[str],
        "OverrideEnvironment": NotRequired[Mapping[str, str]],
    },
)
ModelDashboardEndpointTypeDef = TypedDict(
    "ModelDashboardEndpointTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "EndpointStatus": EndpointStatusType,
    },
)
ModelDashboardIndicatorActionTypeDef = TypedDict(
    "ModelDashboardIndicatorActionTypeDef",
    {
        "Enabled": NotRequired[bool],
    },
)
RealTimeInferenceConfigTypeDef = TypedDict(
    "RealTimeInferenceConfigTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "InstanceCount": int,
    },
)
ModelInputTypeDef = TypedDict(
    "ModelInputTypeDef",
    {
        "DataInputConfig": str,
    },
)
ModelLatencyThresholdTypeDef = TypedDict(
    "ModelLatencyThresholdTypeDef",
    {
        "Percentile": NotRequired[str],
        "ValueInMilliseconds": NotRequired[int],
    },
)
ModelMetadataFilterTypeDef = TypedDict(
    "ModelMetadataFilterTypeDef",
    {
        "Name": ModelMetadataFilterTypeType,
        "Value": str,
    },
)
ModelPackageStatusItemTypeDef = TypedDict(
    "ModelPackageStatusItemTypeDef",
    {
        "Name": str,
        "Status": DetailedModelPackageStatusType,
        "FailureReason": NotRequired[str],
    },
)
ModelQuantizationConfigOutputTypeDef = TypedDict(
    "ModelQuantizationConfigOutputTypeDef",
    {
        "Image": NotRequired[str],
        "OverrideEnvironment": NotRequired[Dict[str, str]],
    },
)
ModelQuantizationConfigTypeDef = TypedDict(
    "ModelQuantizationConfigTypeDef",
    {
        "Image": NotRequired[str],
        "OverrideEnvironment": NotRequired[Mapping[str, str]],
    },
)
ModelStepMetadataTypeDef = TypedDict(
    "ModelStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
MonitoringAppSpecificationExtraOutputTypeDef = TypedDict(
    "MonitoringAppSpecificationExtraOutputTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
    },
)
MonitoringAppSpecificationOutputTypeDef = TypedDict(
    "MonitoringAppSpecificationOutputTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
    },
)
MonitoringAppSpecificationTypeDef = TypedDict(
    "MonitoringAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
    },
)
MonitoringClusterConfigTypeDef = TypedDict(
    "MonitoringClusterConfigTypeDef",
    {
        "InstanceCount": int,
        "InstanceType": ProcessingInstanceTypeType,
        "VolumeSizeInGB": int,
        "VolumeKmsKeyId": NotRequired[str],
    },
)
MonitoringCsvDatasetFormatTypeDef = TypedDict(
    "MonitoringCsvDatasetFormatTypeDef",
    {
        "Header": NotRequired[bool],
    },
)
MonitoringJsonDatasetFormatTypeDef = TypedDict(
    "MonitoringJsonDatasetFormatTypeDef",
    {
        "Line": NotRequired[bool],
    },
)
MonitoringS3OutputTypeDef = TypedDict(
    "MonitoringS3OutputTypeDef",
    {
        "S3Uri": str,
        "LocalPath": str,
        "S3UploadMode": NotRequired[ProcessingS3UploadModeType],
    },
)
ScheduleConfigTypeDef = TypedDict(
    "ScheduleConfigTypeDef",
    {
        "ScheduleExpression": str,
        "DataAnalysisStartTime": NotRequired[str],
        "DataAnalysisEndTime": NotRequired[str],
    },
)
S3StorageConfigTypeDef = TypedDict(
    "S3StorageConfigTypeDef",
    {
        "S3Uri": str,
        "KmsKeyId": NotRequired[str],
        "ResolvedOutputS3Uri": NotRequired[str],
    },
)
OidcConfigForResponseTypeDef = TypedDict(
    "OidcConfigForResponseTypeDef",
    {
        "ClientId": NotRequired[str],
        "Issuer": NotRequired[str],
        "AuthorizationEndpoint": NotRequired[str],
        "TokenEndpoint": NotRequired[str],
        "UserInfoEndpoint": NotRequired[str],
        "LogoutEndpoint": NotRequired[str],
        "JwksUri": NotRequired[str],
        "Scope": NotRequired[str],
        "AuthenticationRequestExtraParams": NotRequired[Dict[str, str]],
    },
)
OnlineStoreSecurityConfigTypeDef = TypedDict(
    "OnlineStoreSecurityConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
    },
)
TtlDurationTypeDef = TypedDict(
    "TtlDurationTypeDef",
    {
        "Unit": NotRequired[TtlDurationUnitType],
        "Value": NotRequired[int],
    },
)
OptimizationModelAccessConfigTypeDef = TypedDict(
    "OptimizationModelAccessConfigTypeDef",
    {
        "AcceptEula": bool,
    },
)
TargetPlatformTypeDef = TypedDict(
    "TargetPlatformTypeDef",
    {
        "Os": TargetPlatformOsType,
        "Arch": TargetPlatformArchType,
        "Accelerator": NotRequired[TargetPlatformAcceleratorType],
    },
)
OwnershipSettingsSummaryTypeDef = TypedDict(
    "OwnershipSettingsSummaryTypeDef",
    {
        "OwnerUserProfileName": NotRequired[str],
    },
)
ParentTypeDef = TypedDict(
    "ParentTypeDef",
    {
        "TrialName": NotRequired[str],
        "ExperimentName": NotRequired[str],
    },
)
ProductionVariantManagedInstanceScalingTypeDef = TypedDict(
    "ProductionVariantManagedInstanceScalingTypeDef",
    {
        "Status": NotRequired[ManagedInstanceScalingStatusType],
        "MinInstanceCount": NotRequired[int],
        "MaxInstanceCount": NotRequired[int],
    },
)
ProductionVariantRoutingConfigTypeDef = TypedDict(
    "ProductionVariantRoutingConfigTypeDef",
    {
        "RoutingStrategy": RoutingStrategyType,
    },
)
ProductionVariantStatusTypeDef = TypedDict(
    "ProductionVariantStatusTypeDef",
    {
        "Status": VariantStatusType,
        "StatusMessage": NotRequired[str],
        "StartTime": NotRequired[datetime],
    },
)
PhaseTypeDef = TypedDict(
    "PhaseTypeDef",
    {
        "InitialNumberOfUsers": NotRequired[int],
        "SpawnRate": NotRequired[int],
        "DurationInSeconds": NotRequired[int],
    },
)
ProcessingJobStepMetadataTypeDef = TypedDict(
    "ProcessingJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
QualityCheckStepMetadataTypeDef = TypedDict(
    "QualityCheckStepMetadataTypeDef",
    {
        "CheckType": NotRequired[str],
        "BaselineUsedForDriftCheckStatistics": NotRequired[str],
        "BaselineUsedForDriftCheckConstraints": NotRequired[str],
        "CalculatedBaselineStatistics": NotRequired[str],
        "CalculatedBaselineConstraints": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ViolationReport": NotRequired[str],
        "CheckJobArn": NotRequired[str],
        "SkipCheck": NotRequired[bool],
        "RegisterNewBaseline": NotRequired[bool],
    },
)
RegisterModelStepMetadataTypeDef = TypedDict(
    "RegisterModelStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
TrainingJobStepMetadataTypeDef = TypedDict(
    "TrainingJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
TransformJobStepMetadataTypeDef = TypedDict(
    "TransformJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
TuningJobStepMetaDataTypeDef = TypedDict(
    "TuningJobStepMetaDataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)
SelectiveExecutionResultTypeDef = TypedDict(
    "SelectiveExecutionResultTypeDef",
    {
        "SourcePipelineExecutionArn": NotRequired[str],
    },
)
ProcessingClusterConfigTypeDef = TypedDict(
    "ProcessingClusterConfigTypeDef",
    {
        "InstanceCount": int,
        "InstanceType": ProcessingInstanceTypeType,
        "VolumeSizeInGB": int,
        "VolumeKmsKeyId": NotRequired[str],
    },
)
ProcessingFeatureStoreOutputTypeDef = TypedDict(
    "ProcessingFeatureStoreOutputTypeDef",
    {
        "FeatureGroupName": str,
    },
)
ProcessingS3InputTypeDef = TypedDict(
    "ProcessingS3InputTypeDef",
    {
        "S3Uri": str,
        "S3DataType": ProcessingS3DataTypeType,
        "LocalPath": NotRequired[str],
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "S3CompressionType": NotRequired[ProcessingS3CompressionTypeType],
    },
)
ProcessingS3OutputTypeDef = TypedDict(
    "ProcessingS3OutputTypeDef",
    {
        "S3Uri": str,
        "LocalPath": str,
        "S3UploadMode": ProcessingS3UploadModeType,
    },
)
ProductionVariantCoreDumpConfigTypeDef = TypedDict(
    "ProductionVariantCoreDumpConfigTypeDef",
    {
        "DestinationS3Uri": str,
        "KmsKeyId": NotRequired[str],
    },
)
ProfilerConfigExtraOutputTypeDef = TypedDict(
    "ProfilerConfigExtraOutputTypeDef",
    {
        "S3OutputPath": NotRequired[str],
        "ProfilingIntervalInMilliseconds": NotRequired[int],
        "ProfilingParameters": NotRequired[Dict[str, str]],
        "DisableProfiler": NotRequired[bool],
    },
)
ProfilerConfigForUpdateTypeDef = TypedDict(
    "ProfilerConfigForUpdateTypeDef",
    {
        "S3OutputPath": NotRequired[str],
        "ProfilingIntervalInMilliseconds": NotRequired[int],
        "ProfilingParameters": NotRequired[Mapping[str, str]],
        "DisableProfiler": NotRequired[bool],
    },
)
ProfilerRuleConfigurationTypeDef = TypedDict(
    "ProfilerRuleConfigurationTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Mapping[str, str]],
    },
)
PropertyNameQueryTypeDef = TypedDict(
    "PropertyNameQueryTypeDef",
    {
        "PropertyNameHint": str,
    },
)
ProvisioningParameterTypeDef = TypedDict(
    "ProvisioningParameterTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
    },
)
USDTypeDef = TypedDict(
    "USDTypeDef",
    {
        "Dollars": NotRequired[int],
        "Cents": NotRequired[int],
        "TenthFractionsOfACent": NotRequired[int],
    },
)
PutModelPackageGroupPolicyInputRequestTypeDef = TypedDict(
    "PutModelPackageGroupPolicyInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
        "ResourcePolicy": str,
    },
)
VertexTypeDef = TypedDict(
    "VertexTypeDef",
    {
        "Arn": NotRequired[str],
        "Type": NotRequired[str],
        "LineageType": NotRequired[LineageTypeType],
    },
)
RStudioServerProAppSettingsTypeDef = TypedDict(
    "RStudioServerProAppSettingsTypeDef",
    {
        "AccessStatus": NotRequired[RStudioServerProAccessStatusType],
        "UserGroup": NotRequired[RStudioServerProUserGroupType],
    },
)
RecommendationJobCompiledOutputConfigTypeDef = TypedDict(
    "RecommendationJobCompiledOutputConfigTypeDef",
    {
        "S3OutputUri": NotRequired[str],
    },
)
RecommendationJobPayloadConfigOutputTypeDef = TypedDict(
    "RecommendationJobPayloadConfigOutputTypeDef",
    {
        "SamplePayloadUrl": NotRequired[str],
        "SupportedContentTypes": NotRequired[List[str]],
    },
)
RecommendationJobPayloadConfigTypeDef = TypedDict(
    "RecommendationJobPayloadConfigTypeDef",
    {
        "SamplePayloadUrl": NotRequired[str],
        "SupportedContentTypes": NotRequired[Sequence[str]],
    },
)
RecommendationJobResourceLimitTypeDef = TypedDict(
    "RecommendationJobResourceLimitTypeDef",
    {
        "MaxNumberOfTests": NotRequired[int],
        "MaxParallelOfTests": NotRequired[int],
    },
)
RecommendationJobVpcConfigOutputTypeDef = TypedDict(
    "RecommendationJobVpcConfigOutputTypeDef",
    {
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
    },
)
RecommendationJobVpcConfigTypeDef = TypedDict(
    "RecommendationJobVpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)
RemoteDebugConfigForUpdateTypeDef = TypedDict(
    "RemoteDebugConfigForUpdateTypeDef",
    {
        "EnableRemoteDebug": NotRequired[bool],
    },
)
RenderableTaskTypeDef = TypedDict(
    "RenderableTaskTypeDef",
    {
        "Input": str,
    },
)
RenderingErrorTypeDef = TypedDict(
    "RenderingErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
)
ResourceConfigForUpdateTypeDef = TypedDict(
    "ResourceConfigForUpdateTypeDef",
    {
        "KeepAlivePeriodInSeconds": int,
    },
)
VisibilityConditionsTypeDef = TypedDict(
    "VisibilityConditionsTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
    },
)
SelectedStepTypeDef = TypedDict(
    "SelectedStepTypeDef",
    {
        "StepName": str,
    },
)
SendPipelineExecutionStepFailureRequestRequestTypeDef = TypedDict(
    "SendPipelineExecutionStepFailureRequestRequestTypeDef",
    {
        "CallbackToken": str,
        "FailureReason": NotRequired[str],
        "ClientRequestToken": NotRequired[str],
    },
)
ShadowModelVariantConfigTypeDef = TypedDict(
    "ShadowModelVariantConfigTypeDef",
    {
        "ShadowModelVariantName": str,
        "SamplingPercentage": int,
    },
)
SharingSettingsTypeDef = TypedDict(
    "SharingSettingsTypeDef",
    {
        "NotebookOutputOption": NotRequired[NotebookOutputOptionType],
        "S3OutputPath": NotRequired[str],
        "S3KmsKeyId": NotRequired[str],
    },
)
SourceIpConfigExtraOutputTypeDef = TypedDict(
    "SourceIpConfigExtraOutputTypeDef",
    {
        "Cidrs": List[str],
    },
)
SourceIpConfigOutputTypeDef = TypedDict(
    "SourceIpConfigOutputTypeDef",
    {
        "Cidrs": List[str],
    },
)
SpaceSharingSettingsSummaryTypeDef = TypedDict(
    "SpaceSharingSettingsSummaryTypeDef",
    {
        "SharingType": NotRequired[SharingTypeType],
    },
)
StairsTypeDef = TypedDict(
    "StairsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
        "NumberOfSteps": NotRequired[int],
        "UsersPerStep": NotRequired[int],
    },
)
StartEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "StartEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
    },
)
StartInferenceExperimentRequestRequestTypeDef = TypedDict(
    "StartInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
    },
)
StartMlflowTrackingServerRequestRequestTypeDef = TypedDict(
    "StartMlflowTrackingServerRequestRequestTypeDef",
    {
        "TrackingServerName": str,
    },
)
StartMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "StartMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)
StartNotebookInstanceInputRequestTypeDef = TypedDict(
    "StartNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)
StopAutoMLJobRequestRequestTypeDef = TypedDict(
    "StopAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
    },
)
StopCompilationJobRequestRequestTypeDef = TypedDict(
    "StopCompilationJobRequestRequestTypeDef",
    {
        "CompilationJobName": str,
    },
)
StopEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "StopEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
    },
)
StopEdgePackagingJobRequestRequestTypeDef = TypedDict(
    "StopEdgePackagingJobRequestRequestTypeDef",
    {
        "EdgePackagingJobName": str,
    },
)
StopHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "StopHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
    },
)
StopInferenceRecommendationsJobRequestRequestTypeDef = TypedDict(
    "StopInferenceRecommendationsJobRequestRequestTypeDef",
    {
        "JobName": str,
    },
)
StopLabelingJobRequestRequestTypeDef = TypedDict(
    "StopLabelingJobRequestRequestTypeDef",
    {
        "LabelingJobName": str,
    },
)
StopMlflowTrackingServerRequestRequestTypeDef = TypedDict(
    "StopMlflowTrackingServerRequestRequestTypeDef",
    {
        "TrackingServerName": str,
    },
)
StopMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "StopMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)
StopNotebookInstanceInputRequestTypeDef = TypedDict(
    "StopNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)
StopOptimizationJobRequestRequestTypeDef = TypedDict(
    "StopOptimizationJobRequestRequestTypeDef",
    {
        "OptimizationJobName": str,
    },
)
StopPipelineExecutionRequestRequestTypeDef = TypedDict(
    "StopPipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "ClientRequestToken": str,
    },
)
StopProcessingJobRequestRequestTypeDef = TypedDict(
    "StopProcessingJobRequestRequestTypeDef",
    {
        "ProcessingJobName": str,
    },
)
StopTrainingJobRequestRequestTypeDef = TypedDict(
    "StopTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
    },
)
StopTransformJobRequestRequestTypeDef = TypedDict(
    "StopTransformJobRequestRequestTypeDef",
    {
        "TransformJobName": str,
    },
)
StudioWebPortalSettingsOutputTypeDef = TypedDict(
    "StudioWebPortalSettingsOutputTypeDef",
    {
        "HiddenMlTools": NotRequired[List[MlToolsType]],
        "HiddenAppTypes": NotRequired[List[AppTypeType]],
    },
)
StudioWebPortalSettingsTypeDef = TypedDict(
    "StudioWebPortalSettingsTypeDef",
    {
        "HiddenMlTools": NotRequired[Sequence[MlToolsType]],
        "HiddenAppTypes": NotRequired[Sequence[AppTypeType]],
    },
)
ThroughputConfigUpdateTypeDef = TypedDict(
    "ThroughputConfigUpdateTypeDef",
    {
        "ThroughputMode": NotRequired[ThroughputModeType],
        "ProvisionedReadCapacityUnits": NotRequired[int],
        "ProvisionedWriteCapacityUnits": NotRequired[int],
    },
)
TimeSeriesConfigOutputTypeDef = TypedDict(
    "TimeSeriesConfigOutputTypeDef",
    {
        "TargetAttributeName": str,
        "TimestampAttributeName": str,
        "ItemIdentifierAttributeName": str,
        "GroupingAttributeNames": NotRequired[List[str]],
    },
)
TimeSeriesConfigTypeDef = TypedDict(
    "TimeSeriesConfigTypeDef",
    {
        "TargetAttributeName": str,
        "TimestampAttributeName": str,
        "ItemIdentifierAttributeName": str,
        "GroupingAttributeNames": NotRequired[Sequence[str]],
    },
)
TimeSeriesTransformationsOutputTypeDef = TypedDict(
    "TimeSeriesTransformationsOutputTypeDef",
    {
        "Filling": NotRequired[Dict[str, Dict[FillingTypeType, str]]],
        "Aggregation": NotRequired[Dict[str, AggregationTransformationValueType]],
    },
)
TimeSeriesTransformationsTypeDef = TypedDict(
    "TimeSeriesTransformationsTypeDef",
    {
        "Filling": NotRequired[Mapping[str, Mapping[FillingTypeType, str]]],
        "Aggregation": NotRequired[Mapping[str, AggregationTransformationValueType]],
    },
)
TrainingRepositoryAuthConfigTypeDef = TypedDict(
    "TrainingRepositoryAuthConfigTypeDef",
    {
        "TrainingRepositoryCredentialsProviderArn": str,
    },
)
TransformS3DataSourceTypeDef = TypedDict(
    "TransformS3DataSourceTypeDef",
    {
        "S3DataType": S3DataTypeType,
        "S3Uri": str,
    },
)
UpdateActionRequestRequestTypeDef = TypedDict(
    "UpdateActionRequestRequestTypeDef",
    {
        "ActionName": str,
        "Description": NotRequired[str],
        "Status": NotRequired[ActionStatusType],
        "Properties": NotRequired[Mapping[str, str]],
        "PropertiesToRemove": NotRequired[Sequence[str]],
    },
)
UpdateArtifactRequestRequestTypeDef = TypedDict(
    "UpdateArtifactRequestRequestTypeDef",
    {
        "ArtifactArn": str,
        "ArtifactName": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "PropertiesToRemove": NotRequired[Sequence[str]],
    },
)
UpdateClusterSoftwareRequestRequestTypeDef = TypedDict(
    "UpdateClusterSoftwareRequestRequestTypeDef",
    {
        "ClusterName": str,
    },
)
UpdateContextRequestRequestTypeDef = TypedDict(
    "UpdateContextRequestRequestTypeDef",
    {
        "ContextName": str,
        "Description": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "PropertiesToRemove": NotRequired[Sequence[str]],
    },
)
VariantPropertyTypeDef = TypedDict(
    "VariantPropertyTypeDef",
    {
        "VariantPropertyType": VariantPropertyTypeType,
    },
)
UpdateExperimentRequestRequestTypeDef = TypedDict(
    "UpdateExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
    },
)
UpdateHubRequestRequestTypeDef = TypedDict(
    "UpdateHubRequestRequestTypeDef",
    {
        "HubName": str,
        "HubDescription": NotRequired[str],
        "HubDisplayName": NotRequired[str],
        "HubSearchKeywords": NotRequired[Sequence[str]],
    },
)
UpdateImageRequestRequestTypeDef = TypedDict(
    "UpdateImageRequestRequestTypeDef",
    {
        "ImageName": str,
        "DeleteProperties": NotRequired[Sequence[str]],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "RoleArn": NotRequired[str],
    },
)
UpdateImageVersionRequestRequestTypeDef = TypedDict(
    "UpdateImageVersionRequestRequestTypeDef",
    {
        "ImageName": str,
        "Alias": NotRequired[str],
        "Version": NotRequired[int],
        "AliasesToAdd": NotRequired[Sequence[str]],
        "AliasesToDelete": NotRequired[Sequence[str]],
        "VendorGuidance": NotRequired[VendorGuidanceType],
        "JobType": NotRequired[JobTypeType],
        "MLFramework": NotRequired[str],
        "ProgrammingLang": NotRequired[str],
        "Processor": NotRequired[ProcessorType],
        "Horovod": NotRequired[bool],
        "ReleaseNotes": NotRequired[str],
    },
)
UpdateMlflowTrackingServerRequestRequestTypeDef = TypedDict(
    "UpdateMlflowTrackingServerRequestRequestTypeDef",
    {
        "TrackingServerName": str,
        "ArtifactStoreUri": NotRequired[str],
        "TrackingServerSize": NotRequired[TrackingServerSizeType],
        "AutomaticModelRegistration": NotRequired[bool],
        "WeeklyMaintenanceWindowStart": NotRequired[str],
    },
)
UpdateModelCardRequestRequestTypeDef = TypedDict(
    "UpdateModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "Content": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
    },
)
UpdateMonitoringAlertRequestRequestTypeDef = TypedDict(
    "UpdateMonitoringAlertRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringAlertName": str,
        "DatapointsToAlert": int,
        "EvaluationPeriod": int,
    },
)
UpdateTrialRequestRequestTypeDef = TypedDict(
    "UpdateTrialRequestRequestTypeDef",
    {
        "TrialName": str,
        "DisplayName": NotRequired[str],
    },
)
WorkforceVpcConfigResponseTypeDef = TypedDict(
    "WorkforceVpcConfigResponseTypeDef",
    {
        "VpcId": str,
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
        "VpcEndpointId": NotRequired[str],
    },
)
ActionSummaryTypeDef = TypedDict(
    "ActionSummaryTypeDef",
    {
        "ActionArn": NotRequired[str],
        "ActionName": NotRequired[str],
        "Source": NotRequired[ActionSourceTypeDef],
        "ActionType": NotRequired[str],
        "Status": NotRequired[ActionStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
AddAssociationResponseTypeDef = TypedDict(
    "AddAssociationResponseTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AssociateTrialComponentResponseTypeDef = TypedDict(
    "AssociateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateActionResponseTypeDef = TypedDict(
    "CreateActionResponseTypeDef",
    {
        "ActionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAlgorithmOutputTypeDef = TypedDict(
    "CreateAlgorithmOutputTypeDef",
    {
        "AlgorithmArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAppImageConfigResponseTypeDef = TypedDict(
    "CreateAppImageConfigResponseTypeDef",
    {
        "AppImageConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAppResponseTypeDef = TypedDict(
    "CreateAppResponseTypeDef",
    {
        "AppArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateArtifactResponseTypeDef = TypedDict(
    "CreateArtifactResponseTypeDef",
    {
        "ArtifactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAutoMLJobResponseTypeDef = TypedDict(
    "CreateAutoMLJobResponseTypeDef",
    {
        "AutoMLJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAutoMLJobV2ResponseTypeDef = TypedDict(
    "CreateAutoMLJobV2ResponseTypeDef",
    {
        "AutoMLJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterResponseTypeDef = TypedDict(
    "CreateClusterResponseTypeDef",
    {
        "ClusterArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCodeRepositoryOutputTypeDef = TypedDict(
    "CreateCodeRepositoryOutputTypeDef",
    {
        "CodeRepositoryArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCompilationJobResponseTypeDef = TypedDict(
    "CreateCompilationJobResponseTypeDef",
    {
        "CompilationJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateContextResponseTypeDef = TypedDict(
    "CreateContextResponseTypeDef",
    {
        "ContextArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDataQualityJobDefinitionResponseTypeDef = TypedDict(
    "CreateDataQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDomainResponseTypeDef = TypedDict(
    "CreateDomainResponseTypeDef",
    {
        "DomainArn": str,
        "Url": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateEdgeDeploymentPlanResponseTypeDef = TypedDict(
    "CreateEdgeDeploymentPlanResponseTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateEndpointConfigOutputTypeDef = TypedDict(
    "CreateEndpointConfigOutputTypeDef",
    {
        "EndpointConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateEndpointOutputTypeDef = TypedDict(
    "CreateEndpointOutputTypeDef",
    {
        "EndpointArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateExperimentResponseTypeDef = TypedDict(
    "CreateExperimentResponseTypeDef",
    {
        "ExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateFeatureGroupResponseTypeDef = TypedDict(
    "CreateFeatureGroupResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateFlowDefinitionResponseTypeDef = TypedDict(
    "CreateFlowDefinitionResponseTypeDef",
    {
        "FlowDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHubContentReferenceResponseTypeDef = TypedDict(
    "CreateHubContentReferenceResponseTypeDef",
    {
        "HubArn": str,
        "HubContentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHubResponseTypeDef = TypedDict(
    "CreateHubResponseTypeDef",
    {
        "HubArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHumanTaskUiResponseTypeDef = TypedDict(
    "CreateHumanTaskUiResponseTypeDef",
    {
        "HumanTaskUiArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHyperParameterTuningJobResponseTypeDef = TypedDict(
    "CreateHyperParameterTuningJobResponseTypeDef",
    {
        "HyperParameterTuningJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateImageResponseTypeDef = TypedDict(
    "CreateImageResponseTypeDef",
    {
        "ImageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateImageVersionResponseTypeDef = TypedDict(
    "CreateImageVersionResponseTypeDef",
    {
        "ImageVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInferenceComponentOutputTypeDef = TypedDict(
    "CreateInferenceComponentOutputTypeDef",
    {
        "InferenceComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInferenceExperimentResponseTypeDef = TypedDict(
    "CreateInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInferenceRecommendationsJobResponseTypeDef = TypedDict(
    "CreateInferenceRecommendationsJobResponseTypeDef",
    {
        "JobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLabelingJobResponseTypeDef = TypedDict(
    "CreateLabelingJobResponseTypeDef",
    {
        "LabelingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateMlflowTrackingServerResponseTypeDef = TypedDict(
    "CreateMlflowTrackingServerResponseTypeDef",
    {
        "TrackingServerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelBiasJobDefinitionResponseTypeDef = TypedDict(
    "CreateModelBiasJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelCardExportJobResponseTypeDef = TypedDict(
    "CreateModelCardExportJobResponseTypeDef",
    {
        "ModelCardExportJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelCardResponseTypeDef = TypedDict(
    "CreateModelCardResponseTypeDef",
    {
        "ModelCardArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelExplainabilityJobDefinitionResponseTypeDef = TypedDict(
    "CreateModelExplainabilityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelOutputTypeDef = TypedDict(
    "CreateModelOutputTypeDef",
    {
        "ModelArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelPackageGroupOutputTypeDef = TypedDict(
    "CreateModelPackageGroupOutputTypeDef",
    {
        "ModelPackageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelPackageOutputTypeDef = TypedDict(
    "CreateModelPackageOutputTypeDef",
    {
        "ModelPackageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelQualityJobDefinitionResponseTypeDef = TypedDict(
    "CreateModelQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateMonitoringScheduleResponseTypeDef = TypedDict(
    "CreateMonitoringScheduleResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateNotebookInstanceLifecycleConfigOutputTypeDef = TypedDict(
    "CreateNotebookInstanceLifecycleConfigOutputTypeDef",
    {
        "NotebookInstanceLifecycleConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateNotebookInstanceOutputTypeDef = TypedDict(
    "CreateNotebookInstanceOutputTypeDef",
    {
        "NotebookInstanceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateOptimizationJobResponseTypeDef = TypedDict(
    "CreateOptimizationJobResponseTypeDef",
    {
        "OptimizationJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePipelineResponseTypeDef = TypedDict(
    "CreatePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePresignedDomainUrlResponseTypeDef = TypedDict(
    "CreatePresignedDomainUrlResponseTypeDef",
    {
        "AuthorizedUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePresignedMlflowTrackingServerUrlResponseTypeDef = TypedDict(
    "CreatePresignedMlflowTrackingServerUrlResponseTypeDef",
    {
        "AuthorizedUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePresignedNotebookInstanceUrlOutputTypeDef = TypedDict(
    "CreatePresignedNotebookInstanceUrlOutputTypeDef",
    {
        "AuthorizedUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProcessingJobResponseTypeDef = TypedDict(
    "CreateProcessingJobResponseTypeDef",
    {
        "ProcessingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProjectOutputTypeDef = TypedDict(
    "CreateProjectOutputTypeDef",
    {
        "ProjectArn": str,
        "ProjectId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateSpaceResponseTypeDef = TypedDict(
    "CreateSpaceResponseTypeDef",
    {
        "SpaceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateStudioLifecycleConfigResponseTypeDef = TypedDict(
    "CreateStudioLifecycleConfigResponseTypeDef",
    {
        "StudioLifecycleConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTrainingJobResponseTypeDef = TypedDict(
    "CreateTrainingJobResponseTypeDef",
    {
        "TrainingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTransformJobResponseTypeDef = TypedDict(
    "CreateTransformJobResponseTypeDef",
    {
        "TransformJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTrialComponentResponseTypeDef = TypedDict(
    "CreateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTrialResponseTypeDef = TypedDict(
    "CreateTrialResponseTypeDef",
    {
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateUserProfileResponseTypeDef = TypedDict(
    "CreateUserProfileResponseTypeDef",
    {
        "UserProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateWorkforceResponseTypeDef = TypedDict(
    "CreateWorkforceResponseTypeDef",
    {
        "WorkforceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateWorkteamResponseTypeDef = TypedDict(
    "CreateWorkteamResponseTypeDef",
    {
        "WorkteamArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteActionResponseTypeDef = TypedDict(
    "DeleteActionResponseTypeDef",
    {
        "ActionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteArtifactResponseTypeDef = TypedDict(
    "DeleteArtifactResponseTypeDef",
    {
        "ArtifactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteAssociationResponseTypeDef = TypedDict(
    "DeleteAssociationResponseTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteClusterResponseTypeDef = TypedDict(
    "DeleteClusterResponseTypeDef",
    {
        "ClusterArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteContextResponseTypeDef = TypedDict(
    "DeleteContextResponseTypeDef",
    {
        "ContextArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteExperimentResponseTypeDef = TypedDict(
    "DeleteExperimentResponseTypeDef",
    {
        "ExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteInferenceExperimentResponseTypeDef = TypedDict(
    "DeleteInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteMlflowTrackingServerResponseTypeDef = TypedDict(
    "DeleteMlflowTrackingServerResponseTypeDef",
    {
        "TrackingServerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeletePipelineResponseTypeDef = TypedDict(
    "DeletePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteTrialComponentResponseTypeDef = TypedDict(
    "DeleteTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteTrialResponseTypeDef = TypedDict(
    "DeleteTrialResponseTypeDef",
    {
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteWorkteamResponseTypeDef = TypedDict(
    "DeleteWorkteamResponseTypeDef",
    {
        "Success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeImageResponseTypeDef = TypedDict(
    "DescribeImageResponseTypeDef",
    {
        "CreationTime": datetime,
        "Description": str,
        "DisplayName": str,
        "FailureReason": str,
        "ImageArn": str,
        "ImageName": str,
        "ImageStatus": ImageStatusType,
        "LastModifiedTime": datetime,
        "RoleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeImageVersionResponseTypeDef = TypedDict(
    "DescribeImageVersionResponseTypeDef",
    {
        "BaseImage": str,
        "ContainerImage": str,
        "CreationTime": datetime,
        "FailureReason": str,
        "ImageArn": str,
        "ImageVersionArn": str,
        "ImageVersionStatus": ImageVersionStatusType,
        "LastModifiedTime": datetime,
        "Version": int,
        "VendorGuidance": VendorGuidanceType,
        "JobType": JobTypeType,
        "MLFramework": str,
        "ProgrammingLang": str,
        "Processor": ProcessorType,
        "Horovod": bool,
        "ReleaseNotes": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribePipelineDefinitionForExecutionResponseTypeDef = TypedDict(
    "DescribePipelineDefinitionForExecutionResponseTypeDef",
    {
        "PipelineDefinition": str,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeStudioLifecycleConfigResponseTypeDef = TypedDict(
    "DescribeStudioLifecycleConfigResponseTypeDef",
    {
        "StudioLifecycleConfigArn": str,
        "StudioLifecycleConfigName": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "StudioLifecycleConfigContent": str,
        "StudioLifecycleConfigAppType": StudioLifecycleConfigAppTypeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DisassociateTrialComponentResponseTypeDef = TypedDict(
    "DisassociateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetLineageGroupPolicyResponseTypeDef = TypedDict(
    "GetLineageGroupPolicyResponseTypeDef",
    {
        "LineageGroupArn": str,
        "ResourcePolicy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetModelPackageGroupPolicyOutputTypeDef = TypedDict(
    "GetModelPackageGroupPolicyOutputTypeDef",
    {
        "ResourcePolicy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSagemakerServicecatalogPortfolioStatusOutputTypeDef = TypedDict(
    "GetSagemakerServicecatalogPortfolioStatusOutputTypeDef",
    {
        "Status": SagemakerServicecatalogStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportHubContentResponseTypeDef = TypedDict(
    "ImportHubContentResponseTypeDef",
    {
        "HubArn": str,
        "HubContentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAliasesResponseTypeDef = TypedDict(
    "ListAliasesResponseTypeDef",
    {
        "SageMakerImageVersionAliases": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
PutModelPackageGroupPolicyOutputTypeDef = TypedDict(
    "PutModelPackageGroupPolicyOutputTypeDef",
    {
        "ModelPackageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RetryPipelineExecutionResponseTypeDef = TypedDict(
    "RetryPipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SendPipelineExecutionStepFailureResponseTypeDef = TypedDict(
    "SendPipelineExecutionStepFailureResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SendPipelineExecutionStepSuccessResponseTypeDef = TypedDict(
    "SendPipelineExecutionStepSuccessResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartInferenceExperimentResponseTypeDef = TypedDict(
    "StartInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartMlflowTrackingServerResponseTypeDef = TypedDict(
    "StartMlflowTrackingServerResponseTypeDef",
    {
        "TrackingServerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartPipelineExecutionResponseTypeDef = TypedDict(
    "StartPipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopInferenceExperimentResponseTypeDef = TypedDict(
    "StopInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopMlflowTrackingServerResponseTypeDef = TypedDict(
    "StopMlflowTrackingServerResponseTypeDef",
    {
        "TrackingServerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopPipelineExecutionResponseTypeDef = TypedDict(
    "StopPipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateActionResponseTypeDef = TypedDict(
    "UpdateActionResponseTypeDef",
    {
        "ActionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateAppImageConfigResponseTypeDef = TypedDict(
    "UpdateAppImageConfigResponseTypeDef",
    {
        "AppImageConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateArtifactResponseTypeDef = TypedDict(
    "UpdateArtifactResponseTypeDef",
    {
        "ArtifactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateClusterResponseTypeDef = TypedDict(
    "UpdateClusterResponseTypeDef",
    {
        "ClusterArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateClusterSoftwareResponseTypeDef = TypedDict(
    "UpdateClusterSoftwareResponseTypeDef",
    {
        "ClusterArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCodeRepositoryOutputTypeDef = TypedDict(
    "UpdateCodeRepositoryOutputTypeDef",
    {
        "CodeRepositoryArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateContextResponseTypeDef = TypedDict(
    "UpdateContextResponseTypeDef",
    {
        "ContextArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDomainResponseTypeDef = TypedDict(
    "UpdateDomainResponseTypeDef",
    {
        "DomainArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEndpointOutputTypeDef = TypedDict(
    "UpdateEndpointOutputTypeDef",
    {
        "EndpointArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEndpointWeightsAndCapacitiesOutputTypeDef = TypedDict(
    "UpdateEndpointWeightsAndCapacitiesOutputTypeDef",
    {
        "EndpointArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateExperimentResponseTypeDef = TypedDict(
    "UpdateExperimentResponseTypeDef",
    {
        "ExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateFeatureGroupResponseTypeDef = TypedDict(
    "UpdateFeatureGroupResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateHubResponseTypeDef = TypedDict(
    "UpdateHubResponseTypeDef",
    {
        "HubArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateImageResponseTypeDef = TypedDict(
    "UpdateImageResponseTypeDef",
    {
        "ImageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateImageVersionResponseTypeDef = TypedDict(
    "UpdateImageVersionResponseTypeDef",
    {
        "ImageVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateInferenceComponentOutputTypeDef = TypedDict(
    "UpdateInferenceComponentOutputTypeDef",
    {
        "InferenceComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateInferenceComponentRuntimeConfigOutputTypeDef = TypedDict(
    "UpdateInferenceComponentRuntimeConfigOutputTypeDef",
    {
        "InferenceComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateInferenceExperimentResponseTypeDef = TypedDict(
    "UpdateInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateMlflowTrackingServerResponseTypeDef = TypedDict(
    "UpdateMlflowTrackingServerResponseTypeDef",
    {
        "TrackingServerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateModelCardResponseTypeDef = TypedDict(
    "UpdateModelCardResponseTypeDef",
    {
        "ModelCardArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateModelPackageOutputTypeDef = TypedDict(
    "UpdateModelPackageOutputTypeDef",
    {
        "ModelPackageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateMonitoringAlertResponseTypeDef = TypedDict(
    "UpdateMonitoringAlertResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "MonitoringAlertName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateMonitoringScheduleResponseTypeDef = TypedDict(
    "UpdateMonitoringScheduleResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePipelineExecutionResponseTypeDef = TypedDict(
    "UpdatePipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePipelineResponseTypeDef = TypedDict(
    "UpdatePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateProjectOutputTypeDef = TypedDict(
    "UpdateProjectOutputTypeDef",
    {
        "ProjectArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateSpaceResponseTypeDef = TypedDict(
    "UpdateSpaceResponseTypeDef",
    {
        "SpaceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTrainingJobResponseTypeDef = TypedDict(
    "UpdateTrainingJobResponseTypeDef",
    {
        "TrainingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTrialComponentResponseTypeDef = TypedDict(
    "UpdateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateTrialResponseTypeDef = TypedDict(
    "UpdateTrialResponseTypeDef",
    {
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateUserProfileResponseTypeDef = TypedDict(
    "UpdateUserProfileResponseTypeDef",
    {
        "UserProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AddTagsInputRequestTypeDef = TypedDict(
    "AddTagsInputRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagTypeDef],
    },
)
AddTagsOutputTypeDef = TypedDict(
    "AddTagsOutputTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateExperimentRequestRequestTypeDef = TypedDict(
    "CreateExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateHubContentReferenceRequestRequestTypeDef = TypedDict(
    "CreateHubContentReferenceRequestRequestTypeDef",
    {
        "HubName": str,
        "SageMakerPublicHubContentArn": str,
        "HubContentName": NotRequired[str],
        "MinVersion": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateImageRequestRequestTypeDef = TypedDict(
    "CreateImageRequestRequestTypeDef",
    {
        "ImageName": str,
        "RoleArn": str,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateMlflowTrackingServerRequestRequestTypeDef = TypedDict(
    "CreateMlflowTrackingServerRequestRequestTypeDef",
    {
        "TrackingServerName": str,
        "ArtifactStoreUri": str,
        "RoleArn": str,
        "TrackingServerSize": NotRequired[TrackingServerSizeType],
        "MlflowVersion": NotRequired[str],
        "AutomaticModelRegistration": NotRequired[bool],
        "WeeklyMaintenanceWindowStart": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateModelPackageGroupInputRequestTypeDef = TypedDict(
    "CreateModelPackageGroupInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageGroupDescription": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateStudioLifecycleConfigRequestRequestTypeDef = TypedDict(
    "CreateStudioLifecycleConfigRequestRequestTypeDef",
    {
        "StudioLifecycleConfigName": str,
        "StudioLifecycleConfigContent": str,
        "StudioLifecycleConfigAppType": StudioLifecycleConfigAppTypeType,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ImportHubContentRequestRequestTypeDef = TypedDict(
    "ImportHubContentRequestRequestTypeDef",
    {
        "HubContentName": str,
        "HubContentType": HubContentTypeType,
        "DocumentSchemaVersion": str,
        "HubName": str,
        "HubContentDocument": str,
        "HubContentVersion": NotRequired[str],
        "HubContentDisplayName": NotRequired[str],
        "HubContentDescription": NotRequired[str],
        "HubContentMarkdown": NotRequired[str],
        "HubContentSearchKeywords": NotRequired[Sequence[str]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ListTagsOutputTypeDef = TypedDict(
    "ListTagsOutputTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
AutoRollbackConfigOutputTypeDef = TypedDict(
    "AutoRollbackConfigOutputTypeDef",
    {
        "Alarms": NotRequired[List[AlarmTypeDef]],
    },
)
AutoRollbackConfigTypeDef = TypedDict(
    "AutoRollbackConfigTypeDef",
    {
        "Alarms": NotRequired[Sequence[AlarmTypeDef]],
    },
)
HyperParameterAlgorithmSpecificationExtraOutputTypeDef = TypedDict(
    "HyperParameterAlgorithmSpecificationExtraOutputTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[List[MetricDefinitionTypeDef]],
    },
)
HyperParameterAlgorithmSpecificationOutputTypeDef = TypedDict(
    "HyperParameterAlgorithmSpecificationOutputTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[List[MetricDefinitionTypeDef]],
    },
)
HyperParameterAlgorithmSpecificationTypeDef = TypedDict(
    "HyperParameterAlgorithmSpecificationTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[Sequence[MetricDefinitionTypeDef]],
    },
)
AlgorithmStatusDetailsTypeDef = TypedDict(
    "AlgorithmStatusDetailsTypeDef",
    {
        "ValidationStatuses": NotRequired[List[AlgorithmStatusItemTypeDef]],
        "ImageScanStatuses": NotRequired[List[AlgorithmStatusItemTypeDef]],
    },
)
ListAlgorithmsOutputTypeDef = TypedDict(
    "ListAlgorithmsOutputTypeDef",
    {
        "AlgorithmSummaryList": List[AlgorithmSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
AppDetailsTypeDef = TypedDict(
    "AppDetailsTypeDef",
    {
        "DomainId": NotRequired[str],
        "UserProfileName": NotRequired[str],
        "SpaceName": NotRequired[str],
        "AppType": NotRequired[AppTypeType],
        "AppName": NotRequired[str],
        "Status": NotRequired[AppStatusType],
        "CreationTime": NotRequired[datetime],
        "ResourceSpec": NotRequired[ResourceSpecTypeDef],
    },
)
CreateAppRequestRequestTypeDef = TypedDict(
    "CreateAppRequestRequestTypeDef",
    {
        "DomainId": str,
        "AppType": AppTypeType,
        "AppName": str,
        "UserProfileName": NotRequired[str],
        "SpaceName": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ResourceSpec": NotRequired[ResourceSpecTypeDef],
    },
)
DescribeAppResponseTypeDef = TypedDict(
    "DescribeAppResponseTypeDef",
    {
        "AppArn": str,
        "AppType": AppTypeType,
        "AppName": str,
        "DomainId": str,
        "UserProfileName": str,
        "SpaceName": str,
        "Status": AppStatusType,
        "LastHealthCheckTimestamp": datetime,
        "LastUserActivityTimestamp": datetime,
        "CreationTime": datetime,
        "FailureReason": str,
        "ResourceSpec": ResourceSpecTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RStudioServerProDomainSettingsForUpdateTypeDef = TypedDict(
    "RStudioServerProDomainSettingsForUpdateTypeDef",
    {
        "DomainExecutionRoleArn": str,
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "RStudioConnectUrl": NotRequired[str],
        "RStudioPackageManagerUrl": NotRequired[str],
    },
)
RStudioServerProDomainSettingsTypeDef = TypedDict(
    "RStudioServerProDomainSettingsTypeDef",
    {
        "DomainExecutionRoleArn": str,
        "RStudioConnectUrl": NotRequired[str],
        "RStudioPackageManagerUrl": NotRequired[str],
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
    },
)
SpaceCodeEditorAppSettingsTypeDef = TypedDict(
    "SpaceCodeEditorAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
    },
)
TensorBoardAppSettingsTypeDef = TypedDict(
    "TensorBoardAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
    },
)
AppSpecificationUnionTypeDef = Union[AppSpecificationTypeDef, AppSpecificationExtraOutputTypeDef]
ArtifactSourceExtraOutputTypeDef = TypedDict(
    "ArtifactSourceExtraOutputTypeDef",
    {
        "SourceUri": str,
        "SourceTypes": NotRequired[List[ArtifactSourceTypeTypeDef]],
    },
)
ArtifactSourceOutputTypeDef = TypedDict(
    "ArtifactSourceOutputTypeDef",
    {
        "SourceUri": str,
        "SourceTypes": NotRequired[List[ArtifactSourceTypeTypeDef]],
    },
)
ArtifactSourceTypeDef = TypedDict(
    "ArtifactSourceTypeDef",
    {
        "SourceUri": str,
        "SourceTypes": NotRequired[Sequence[ArtifactSourceTypeTypeDef]],
    },
)
AsyncInferenceOutputConfigOutputTypeDef = TypedDict(
    "AsyncInferenceOutputConfigOutputTypeDef",
    {
        "KmsKeyId": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "NotificationConfig": NotRequired[AsyncInferenceNotificationConfigOutputTypeDef],
        "S3FailurePath": NotRequired[str],
    },
)
AsyncInferenceOutputConfigTypeDef = TypedDict(
    "AsyncInferenceOutputConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "NotificationConfig": NotRequired[AsyncInferenceNotificationConfigTypeDef],
        "S3FailurePath": NotRequired[str],
    },
)
AutoMLCandidateGenerationConfigOutputTypeDef = TypedDict(
    "AutoMLCandidateGenerationConfigOutputTypeDef",
    {
        "FeatureSpecificationS3Uri": NotRequired[str],
        "AlgorithmsConfig": NotRequired[List[AutoMLAlgorithmConfigOutputTypeDef]],
    },
)
CandidateGenerationConfigOutputTypeDef = TypedDict(
    "CandidateGenerationConfigOutputTypeDef",
    {
        "AlgorithmsConfig": NotRequired[List[AutoMLAlgorithmConfigOutputTypeDef]],
    },
)
AutoMLCandidateGenerationConfigTypeDef = TypedDict(
    "AutoMLCandidateGenerationConfigTypeDef",
    {
        "FeatureSpecificationS3Uri": NotRequired[str],
        "AlgorithmsConfig": NotRequired[Sequence[AutoMLAlgorithmConfigTypeDef]],
    },
)
CandidateGenerationConfigTypeDef = TypedDict(
    "CandidateGenerationConfigTypeDef",
    {
        "AlgorithmsConfig": NotRequired[Sequence[AutoMLAlgorithmConfigTypeDef]],
    },
)
AutoMLDataSourceTypeDef = TypedDict(
    "AutoMLDataSourceTypeDef",
    {
        "S3DataSource": AutoMLS3DataSourceTypeDef,
    },
)
ImageClassificationJobConfigTypeDef = TypedDict(
    "ImageClassificationJobConfigTypeDef",
    {
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
    },
)
TextClassificationJobConfigTypeDef = TypedDict(
    "TextClassificationJobConfigTypeDef",
    {
        "ContentColumn": str,
        "TargetLabelColumn": str,
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
    },
)
ResolvedAttributesTypeDef = TypedDict(
    "ResolvedAttributesTypeDef",
    {
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "ProblemType": NotRequired[ProblemTypeType],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
    },
)
AutoMLJobSummaryTypeDef = TypedDict(
    "AutoMLJobSummaryTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobArn": str,
        "AutoMLJobStatus": AutoMLJobStatusType,
        "AutoMLJobSecondaryStatus": AutoMLJobSecondaryStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "EndTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "PartialFailureReasons": NotRequired[List[AutoMLPartialFailureReasonTypeDef]],
    },
)
AutoMLProblemTypeResolvedAttributesTypeDef = TypedDict(
    "AutoMLProblemTypeResolvedAttributesTypeDef",
    {
        "TabularResolvedAttributes": NotRequired[TabularResolvedAttributesTypeDef],
        "TextGenerationResolvedAttributes": NotRequired[TextGenerationResolvedAttributesTypeDef],
    },
)
AutoMLSecurityConfigOutputTypeDef = TypedDict(
    "AutoMLSecurityConfigOutputTypeDef",
    {
        "VolumeKmsKeyId": NotRequired[str],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigOutputTypeDef],
    },
)
LabelingJobResourceConfigOutputTypeDef = TypedDict(
    "LabelingJobResourceConfigOutputTypeDef",
    {
        "VolumeKmsKeyId": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigOutputTypeDef],
    },
)
MonitoringNetworkConfigOutputTypeDef = TypedDict(
    "MonitoringNetworkConfigOutputTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigOutputTypeDef],
    },
)
NetworkConfigOutputTypeDef = TypedDict(
    "NetworkConfigOutputTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigOutputTypeDef],
    },
)
AutoMLSecurityConfigTypeDef = TypedDict(
    "AutoMLSecurityConfigTypeDef",
    {
        "VolumeKmsKeyId": NotRequired[str],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)
LabelingJobResourceConfigTypeDef = TypedDict(
    "LabelingJobResourceConfigTypeDef",
    {
        "VolumeKmsKeyId": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)
MonitoringNetworkConfigTypeDef = TypedDict(
    "MonitoringNetworkConfigTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)
NetworkConfigTypeDef = TypedDict(
    "NetworkConfigTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)
BiasTypeDef = TypedDict(
    "BiasTypeDef",
    {
        "Report": NotRequired[MetricsSourceTypeDef],
        "PreTrainingReport": NotRequired[MetricsSourceTypeDef],
        "PostTrainingReport": NotRequired[MetricsSourceTypeDef],
    },
)
DriftCheckModelDataQualityTypeDef = TypedDict(
    "DriftCheckModelDataQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)
DriftCheckModelQualityTypeDef = TypedDict(
    "DriftCheckModelQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)
ExplainabilityTypeDef = TypedDict(
    "ExplainabilityTypeDef",
    {
        "Report": NotRequired[MetricsSourceTypeDef],
    },
)
ModelDataQualityTypeDef = TypedDict(
    "ModelDataQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)
ModelQualityTypeDef = TypedDict(
    "ModelQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)
CallbackStepMetadataTypeDef = TypedDict(
    "CallbackStepMetadataTypeDef",
    {
        "CallbackToken": NotRequired[str],
        "SqsQueueUrl": NotRequired[str],
        "OutputParameters": NotRequired[List[OutputParameterTypeDef]],
    },
)
LambdaStepMetadataTypeDef = TypedDict(
    "LambdaStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
        "OutputParameters": NotRequired[List[OutputParameterTypeDef]],
    },
)
SendPipelineExecutionStepSuccessRequestRequestTypeDef = TypedDict(
    "SendPipelineExecutionStepSuccessRequestRequestTypeDef",
    {
        "CallbackToken": str,
        "OutputParameters": NotRequired[Sequence[OutputParameterTypeDef]],
        "ClientRequestToken": NotRequired[str],
    },
)
CandidatePropertiesTypeDef = TypedDict(
    "CandidatePropertiesTypeDef",
    {
        "CandidateArtifactLocations": NotRequired[CandidateArtifactLocationsTypeDef],
        "CandidateMetrics": NotRequired[List[MetricDatumTypeDef]],
    },
)
CanvasAppSettingsOutputTypeDef = TypedDict(
    "CanvasAppSettingsOutputTypeDef",
    {
        "TimeSeriesForecastingSettings": NotRequired[TimeSeriesForecastingSettingsTypeDef],
        "ModelRegisterSettings": NotRequired[ModelRegisterSettingsTypeDef],
        "WorkspaceSettings": NotRequired[WorkspaceSettingsTypeDef],
        "IdentityProviderOAuthSettings": NotRequired[List[IdentityProviderOAuthSettingTypeDef]],
        "DirectDeploySettings": NotRequired[DirectDeploySettingsTypeDef],
        "KendraSettings": NotRequired[KendraSettingsTypeDef],
        "GenerativeAiSettings": NotRequired[GenerativeAiSettingsTypeDef],
    },
)
CanvasAppSettingsTypeDef = TypedDict(
    "CanvasAppSettingsTypeDef",
    {
        "TimeSeriesForecastingSettings": NotRequired[TimeSeriesForecastingSettingsTypeDef],
        "ModelRegisterSettings": NotRequired[ModelRegisterSettingsTypeDef],
        "WorkspaceSettings": NotRequired[WorkspaceSettingsTypeDef],
        "IdentityProviderOAuthSettings": NotRequired[Sequence[IdentityProviderOAuthSettingTypeDef]],
        "DirectDeploySettings": NotRequired[DirectDeploySettingsTypeDef],
        "KendraSettings": NotRequired[KendraSettingsTypeDef],
        "GenerativeAiSettings": NotRequired[GenerativeAiSettingsTypeDef],
    },
)
RollingUpdatePolicyTypeDef = TypedDict(
    "RollingUpdatePolicyTypeDef",
    {
        "MaximumBatchSize": CapacitySizeTypeDef,
        "WaitIntervalInSeconds": int,
        "MaximumExecutionTimeoutInSeconds": NotRequired[int],
        "RollbackMaximumBatchSize": NotRequired[CapacitySizeTypeDef],
    },
)
TrafficRoutingConfigTypeDef = TypedDict(
    "TrafficRoutingConfigTypeDef",
    {
        "Type": TrafficRoutingConfigTypeType,
        "WaitIntervalInSeconds": int,
        "CanarySize": NotRequired[CapacitySizeTypeDef],
        "LinearStepSize": NotRequired[CapacitySizeTypeDef],
    },
)
InferenceExperimentDataStorageConfigOutputTypeDef = TypedDict(
    "InferenceExperimentDataStorageConfigOutputTypeDef",
    {
        "Destination": str,
        "KmsKey": NotRequired[str],
        "ContentType": NotRequired[CaptureContentTypeHeaderOutputTypeDef],
    },
)
InferenceExperimentDataStorageConfigTypeDef = TypedDict(
    "InferenceExperimentDataStorageConfigTypeDef",
    {
        "Destination": str,
        "KmsKey": NotRequired[str],
        "ContentType": NotRequired[CaptureContentTypeHeaderTypeDef],
    },
)
DataCaptureConfigOutputTypeDef = TypedDict(
    "DataCaptureConfigOutputTypeDef",
    {
        "InitialSamplingPercentage": int,
        "DestinationS3Uri": str,
        "CaptureOptions": List[CaptureOptionTypeDef],
        "EnableCapture": NotRequired[bool],
        "KmsKeyId": NotRequired[str],
        "CaptureContentTypeHeader": NotRequired[CaptureContentTypeHeaderOutputTypeDef],
    },
)
DataCaptureConfigTypeDef = TypedDict(
    "DataCaptureConfigTypeDef",
    {
        "InitialSamplingPercentage": int,
        "DestinationS3Uri": str,
        "CaptureOptions": Sequence[CaptureOptionTypeDef],
        "EnableCapture": NotRequired[bool],
        "KmsKeyId": NotRequired[str],
        "CaptureContentTypeHeader": NotRequired[CaptureContentTypeHeaderTypeDef],
    },
)
EnvironmentParameterRangesOutputTypeDef = TypedDict(
    "EnvironmentParameterRangesOutputTypeDef",
    {
        "CategoricalParameterRanges": NotRequired[List[CategoricalParameterOutputTypeDef]],
    },
)
EnvironmentParameterRangesTypeDef = TypedDict(
    "EnvironmentParameterRangesTypeDef",
    {
        "CategoricalParameterRanges": NotRequired[Sequence[CategoricalParameterTypeDef]],
    },
)
ClarifyShapConfigTypeDef = TypedDict(
    "ClarifyShapConfigTypeDef",
    {
        "ShapBaselineConfig": ClarifyShapBaselineConfigTypeDef,
        "NumberOfSamples": NotRequired[int],
        "UseLogit": NotRequired[bool],
        "Seed": NotRequired[int],
        "TextConfig": NotRequired[ClarifyTextConfigTypeDef],
    },
)
ClusterInstanceStorageConfigTypeDef = TypedDict(
    "ClusterInstanceStorageConfigTypeDef",
    {
        "EbsVolumeConfig": NotRequired[ClusterEbsVolumeConfigTypeDef],
    },
)
ClusterNodeSummaryTypeDef = TypedDict(
    "ClusterNodeSummaryTypeDef",
    {
        "InstanceGroupName": str,
        "InstanceId": str,
        "InstanceType": ClusterInstanceTypeType,
        "LaunchTime": datetime,
        "InstanceStatus": ClusterInstanceStatusDetailsTypeDef,
    },
)
ListClustersResponseTypeDef = TypedDict(
    "ListClustersResponseTypeDef",
    {
        "NextToken": str,
        "ClusterSummaries": List[ClusterSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CodeEditorAppImageConfigExtraOutputTypeDef = TypedDict(
    "CodeEditorAppImageConfigExtraOutputTypeDef",
    {
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
        "ContainerConfig": NotRequired[ContainerConfigExtraOutputTypeDef],
    },
)
JupyterLabAppImageConfigExtraOutputTypeDef = TypedDict(
    "JupyterLabAppImageConfigExtraOutputTypeDef",
    {
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
        "ContainerConfig": NotRequired[ContainerConfigExtraOutputTypeDef],
    },
)
CodeEditorAppImageConfigOutputTypeDef = TypedDict(
    "CodeEditorAppImageConfigOutputTypeDef",
    {
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
        "ContainerConfig": NotRequired[ContainerConfigOutputTypeDef],
    },
)
JupyterLabAppImageConfigOutputTypeDef = TypedDict(
    "JupyterLabAppImageConfigOutputTypeDef",
    {
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
        "ContainerConfig": NotRequired[ContainerConfigOutputTypeDef],
    },
)
CodeEditorAppImageConfigTypeDef = TypedDict(
    "CodeEditorAppImageConfigTypeDef",
    {
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
        "ContainerConfig": NotRequired[ContainerConfigTypeDef],
    },
)
JupyterLabAppImageConfigTypeDef = TypedDict(
    "JupyterLabAppImageConfigTypeDef",
    {
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
        "ContainerConfig": NotRequired[ContainerConfigTypeDef],
    },
)
CodeEditorAppSettingsOutputTypeDef = TypedDict(
    "CodeEditorAppSettingsOutputTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[List[CustomImageTypeDef]],
        "LifecycleConfigArns": NotRequired[List[str]],
    },
)
CodeEditorAppSettingsTypeDef = TypedDict(
    "CodeEditorAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[Sequence[CustomImageTypeDef]],
        "LifecycleConfigArns": NotRequired[Sequence[str]],
    },
)
KernelGatewayAppSettingsOutputTypeDef = TypedDict(
    "KernelGatewayAppSettingsOutputTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[List[CustomImageTypeDef]],
        "LifecycleConfigArns": NotRequired[List[str]],
    },
)
KernelGatewayAppSettingsTypeDef = TypedDict(
    "KernelGatewayAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[Sequence[CustomImageTypeDef]],
        "LifecycleConfigArns": NotRequired[Sequence[str]],
    },
)
RSessionAppSettingsOutputTypeDef = TypedDict(
    "RSessionAppSettingsOutputTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[List[CustomImageTypeDef]],
    },
)
RSessionAppSettingsTypeDef = TypedDict(
    "RSessionAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[Sequence[CustomImageTypeDef]],
    },
)
CodeRepositorySummaryTypeDef = TypedDict(
    "CodeRepositorySummaryTypeDef",
    {
        "CodeRepositoryName": str,
        "CodeRepositoryArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "GitConfig": NotRequired[GitConfigTypeDef],
    },
)
CreateCodeRepositoryInputRequestTypeDef = TypedDict(
    "CreateCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
        "GitConfig": GitConfigTypeDef,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeCodeRepositoryOutputTypeDef = TypedDict(
    "DescribeCodeRepositoryOutputTypeDef",
    {
        "CodeRepositoryName": str,
        "CodeRepositoryArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "GitConfig": GitConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
JupyterLabAppSettingsOutputTypeDef = TypedDict(
    "JupyterLabAppSettingsOutputTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[List[CustomImageTypeDef]],
        "LifecycleConfigArns": NotRequired[List[str]],
        "CodeRepositories": NotRequired[List[CodeRepositoryTypeDef]],
    },
)
JupyterLabAppSettingsTypeDef = TypedDict(
    "JupyterLabAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[Sequence[CustomImageTypeDef]],
        "LifecycleConfigArns": NotRequired[Sequence[str]],
        "CodeRepositories": NotRequired[Sequence[CodeRepositoryTypeDef]],
    },
)
JupyterServerAppSettingsOutputTypeDef = TypedDict(
    "JupyterServerAppSettingsOutputTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "LifecycleConfigArns": NotRequired[List[str]],
        "CodeRepositories": NotRequired[List[CodeRepositoryTypeDef]],
    },
)
JupyterServerAppSettingsTypeDef = TypedDict(
    "JupyterServerAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "LifecycleConfigArns": NotRequired[Sequence[str]],
        "CodeRepositories": NotRequired[Sequence[CodeRepositoryTypeDef]],
    },
)
SpaceJupyterLabAppSettingsOutputTypeDef = TypedDict(
    "SpaceJupyterLabAppSettingsOutputTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CodeRepositories": NotRequired[List[CodeRepositoryTypeDef]],
    },
)
SpaceJupyterLabAppSettingsTypeDef = TypedDict(
    "SpaceJupyterLabAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CodeRepositories": NotRequired[Sequence[CodeRepositoryTypeDef]],
    },
)
CollectionConfigTypeDef = TypedDict(
    "CollectionConfigTypeDef",
    {
        "VectorConfig": NotRequired[VectorConfigTypeDef],
    },
)
DebugHookConfigExtraOutputTypeDef = TypedDict(
    "DebugHookConfigExtraOutputTypeDef",
    {
        "S3OutputPath": str,
        "LocalPath": NotRequired[str],
        "HookParameters": NotRequired[Dict[str, str]],
        "CollectionConfigurations": NotRequired[List[CollectionConfigurationExtraOutputTypeDef]],
    },
)
DebugHookConfigOutputTypeDef = TypedDict(
    "DebugHookConfigOutputTypeDef",
    {
        "S3OutputPath": str,
        "LocalPath": NotRequired[str],
        "HookParameters": NotRequired[Dict[str, str]],
        "CollectionConfigurations": NotRequired[List[CollectionConfigurationOutputTypeDef]],
    },
)
DebugHookConfigTypeDef = TypedDict(
    "DebugHookConfigTypeDef",
    {
        "S3OutputPath": str,
        "LocalPath": NotRequired[str],
        "HookParameters": NotRequired[Mapping[str, str]],
        "CollectionConfigurations": NotRequired[Sequence[CollectionConfigurationTypeDef]],
    },
)
ListCompilationJobsResponseTypeDef = TypedDict(
    "ListCompilationJobsResponseTypeDef",
    {
        "CompilationJobSummaries": List[CompilationJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ContextSummaryTypeDef = TypedDict(
    "ContextSummaryTypeDef",
    {
        "ContextArn": NotRequired[str],
        "ContextName": NotRequired[str],
        "Source": NotRequired[ContextSourceTypeDef],
        "ContextType": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
CreateContextRequestRequestTypeDef = TypedDict(
    "CreateContextRequestRequestTypeDef",
    {
        "ContextName": str,
        "Source": ContextSourceTypeDef,
        "ContextType": str,
        "Description": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
TuningJobCompletionCriteriaTypeDef = TypedDict(
    "TuningJobCompletionCriteriaTypeDef",
    {
        "TargetObjectiveMetricValue": NotRequired[float],
        "BestObjectiveNotImproving": NotRequired[BestObjectiveNotImprovingTypeDef],
        "ConvergenceDetected": NotRequired[ConvergenceDetectedTypeDef],
    },
)
CreateActionRequestRequestTypeDef = TypedDict(
    "CreateActionRequestRequestTypeDef",
    {
        "ActionName": str,
        "Source": ActionSourceTypeDef,
        "ActionType": str,
        "Description": NotRequired[str],
        "Status": NotRequired[ActionStatusType],
        "Properties": NotRequired[Mapping[str, str]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateTrialRequestRequestTypeDef = TypedDict(
    "CreateTrialRequestRequestTypeDef",
    {
        "TrialName": str,
        "ExperimentName": str,
        "DisplayName": NotRequired[str],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateDeviceFleetRequestRequestTypeDef = TypedDict(
    "CreateDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "RoleArn": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "EnableIotRoleAlias": NotRequired[bool],
    },
)
CreateEdgePackagingJobRequestRequestTypeDef = TypedDict(
    "CreateEdgePackagingJobRequestRequestTypeDef",
    {
        "EdgePackagingJobName": str,
        "CompilationJobName": str,
        "ModelName": str,
        "ModelVersion": str,
        "RoleArn": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "ResourceKey": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeDeviceFleetResponseTypeDef = TypedDict(
    "DescribeDeviceFleetResponseTypeDef",
    {
        "DeviceFleetName": str,
        "DeviceFleetArn": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "Description": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "RoleArn": str,
        "IotRoleAlias": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDeviceFleetRequestRequestTypeDef = TypedDict(
    "UpdateDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "RoleArn": NotRequired[str],
        "Description": NotRequired[str],
        "EnableIotRoleAlias": NotRequired[bool],
    },
)
CreateHubRequestRequestTypeDef = TypedDict(
    "CreateHubRequestRequestTypeDef",
    {
        "HubName": str,
        "HubDescription": str,
        "HubDisplayName": NotRequired[str],
        "HubSearchKeywords": NotRequired[Sequence[str]],
        "S3StorageConfig": NotRequired[HubS3StorageConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeHubResponseTypeDef = TypedDict(
    "DescribeHubResponseTypeDef",
    {
        "HubName": str,
        "HubArn": str,
        "HubDisplayName": str,
        "HubDescription": str,
        "HubSearchKeywords": List[str],
        "S3StorageConfig": HubS3StorageConfigTypeDef,
        "HubStatus": HubStatusType,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateHumanTaskUiRequestRequestTypeDef = TypedDict(
    "CreateHumanTaskUiRequestRequestTypeDef",
    {
        "HumanTaskUiName": str,
        "UiTemplate": UiTemplateTypeDef,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateInferenceComponentRuntimeConfigInputRequestTypeDef = TypedDict(
    "UpdateInferenceComponentRuntimeConfigInputRequestTypeDef",
    {
        "InferenceComponentName": str,
        "DesiredRuntimeConfig": InferenceComponentRuntimeConfigTypeDef,
    },
)
CreateModelCardExportJobRequestRequestTypeDef = TypedDict(
    "CreateModelCardExportJobRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "ModelCardExportJobName": str,
        "OutputConfig": ModelCardExportOutputConfigTypeDef,
        "ModelCardVersion": NotRequired[int],
    },
)
CreateModelCardRequestRequestTypeDef = TypedDict(
    "CreateModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "Content": str,
        "ModelCardStatus": ModelCardStatusType,
        "SecurityConfig": NotRequired[ModelCardSecurityConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateNotebookInstanceInputRequestTypeDef = TypedDict(
    "CreateNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
        "InstanceType": InstanceTypeType,
        "RoleArn": str,
        "SubnetId": NotRequired[str],
        "SecurityGroupIds": NotRequired[Sequence[str]],
        "KmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "LifecycleConfigName": NotRequired[str],
        "DirectInternetAccess": NotRequired[DirectInternetAccessType],
        "VolumeSizeInGB": NotRequired[int],
        "AcceleratorTypes": NotRequired[Sequence[NotebookInstanceAcceleratorTypeType]],
        "DefaultCodeRepository": NotRequired[str],
        "AdditionalCodeRepositories": NotRequired[Sequence[str]],
        "RootAccess": NotRequired[RootAccessType],
        "PlatformIdentifier": NotRequired[str],
        "InstanceMetadataServiceConfiguration": NotRequired[
            InstanceMetadataServiceConfigurationTypeDef
        ],
    },
)
DescribeNotebookInstanceOutputTypeDef = TypedDict(
    "DescribeNotebookInstanceOutputTypeDef",
    {
        "NotebookInstanceArn": str,
        "NotebookInstanceName": str,
        "NotebookInstanceStatus": NotebookInstanceStatusType,
        "FailureReason": str,
        "Url": str,
        "InstanceType": InstanceTypeType,
        "SubnetId": str,
        "SecurityGroups": List[str],
        "RoleArn": str,
        "KmsKeyId": str,
        "NetworkInterfaceId": str,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "NotebookInstanceLifecycleConfigName": str,
        "DirectInternetAccess": DirectInternetAccessType,
        "VolumeSizeInGB": int,
        "AcceleratorTypes": List[NotebookInstanceAcceleratorTypeType],
        "DefaultCodeRepository": str,
        "AdditionalCodeRepositories": List[str],
        "RootAccess": RootAccessType,
        "PlatformIdentifier": str,
        "InstanceMetadataServiceConfiguration": InstanceMetadataServiceConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateNotebookInstanceInputRequestTypeDef = TypedDict(
    "UpdateNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
        "InstanceType": NotRequired[InstanceTypeType],
        "RoleArn": NotRequired[str],
        "LifecycleConfigName": NotRequired[str],
        "DisassociateLifecycleConfig": NotRequired[bool],
        "VolumeSizeInGB": NotRequired[int],
        "DefaultCodeRepository": NotRequired[str],
        "AdditionalCodeRepositories": NotRequired[Sequence[str]],
        "AcceleratorTypes": NotRequired[Sequence[NotebookInstanceAcceleratorTypeType]],
        "DisassociateAcceleratorTypes": NotRequired[bool],
        "DisassociateDefaultCodeRepository": NotRequired[bool],
        "DisassociateAdditionalCodeRepositories": NotRequired[bool],
        "RootAccess": NotRequired[RootAccessType],
        "InstanceMetadataServiceConfiguration": NotRequired[
            InstanceMetadataServiceConfigurationTypeDef
        ],
    },
)
CreateNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "CreateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
        "OnCreate": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
        "OnStart": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
    },
)
DescribeNotebookInstanceLifecycleConfigOutputTypeDef = TypedDict(
    "DescribeNotebookInstanceLifecycleConfigOutputTypeDef",
    {
        "NotebookInstanceLifecycleConfigArn": str,
        "NotebookInstanceLifecycleConfigName": str,
        "OnCreate": List[NotebookInstanceLifecycleHookTypeDef],
        "OnStart": List[NotebookInstanceLifecycleHookTypeDef],
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "UpdateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
        "OnCreate": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
        "OnStart": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
    },
)
RetryPipelineExecutionRequestRequestTypeDef = TypedDict(
    "RetryPipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "ClientRequestToken": str,
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)
UpdatePipelineExecutionRequestRequestTypeDef = TypedDict(
    "UpdatePipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "PipelineExecutionDescription": NotRequired[str],
        "PipelineExecutionDisplayName": NotRequired[str],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)
CreatePipelineRequestRequestTypeDef = TypedDict(
    "CreatePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
        "ClientRequestToken": str,
        "RoleArn": str,
        "PipelineDisplayName": NotRequired[str],
        "PipelineDefinition": NotRequired[str],
        "PipelineDefinitionS3Location": NotRequired[PipelineDefinitionS3LocationTypeDef],
        "PipelineDescription": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)
UpdatePipelineRequestRequestTypeDef = TypedDict(
    "UpdatePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
        "PipelineDisplayName": NotRequired[str],
        "PipelineDefinition": NotRequired[str],
        "PipelineDefinitionS3Location": NotRequired[PipelineDefinitionS3LocationTypeDef],
        "PipelineDescription": NotRequired[str],
        "RoleArn": NotRequired[str],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)
InferenceExperimentScheduleTypeDef = TypedDict(
    "InferenceExperimentScheduleTypeDef",
    {
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
    },
)
ListActionsRequestRequestTypeDef = TypedDict(
    "ListActionsRequestRequestTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ActionType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortActionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListAlgorithmsInputRequestTypeDef = TypedDict(
    "ListAlgorithmsInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[AlgorithmSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListAppImageConfigsRequestRequestTypeDef = TypedDict(
    "ListAppImageConfigsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[AppImageConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListArtifactsRequestRequestTypeDef = TypedDict(
    "ListArtifactsRequestRequestTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ArtifactType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListAssociationsRequestRequestTypeDef = TypedDict(
    "ListAssociationsRequestRequestTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "SourceType": NotRequired[str],
        "DestinationType": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortAssociationsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListAutoMLJobsRequestRequestTypeDef = TypedDict(
    "ListAutoMLJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[AutoMLJobStatusType],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[AutoMLSortByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListClusterNodesRequestRequestTypeDef = TypedDict(
    "ListClusterNodesRequestRequestTypeDef",
    {
        "ClusterName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "InstanceGroupNameContains": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ClusterSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListClustersRequestRequestTypeDef = TypedDict(
    "ListClustersRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ClusterSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListCodeRepositoriesInputRequestTypeDef = TypedDict(
    "ListCodeRepositoriesInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[CodeRepositorySortByType],
        "SortOrder": NotRequired[CodeRepositorySortOrderType],
    },
)
ListCompilationJobsRequestRequestTypeDef = TypedDict(
    "ListCompilationJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[CompilationJobStatusType],
        "SortBy": NotRequired[ListCompilationJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListContextsRequestRequestTypeDef = TypedDict(
    "ListContextsRequestRequestTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ContextType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortContextsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListDataQualityJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListDataQualityJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)
ListDeviceFleetsRequestRequestTypeDef = TypedDict(
    "ListDeviceFleetsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ListDeviceFleetsSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListDevicesRequestRequestTypeDef = TypedDict(
    "ListDevicesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "LatestHeartbeatAfter": NotRequired[TimestampTypeDef],
        "ModelName": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
    },
)
ListEdgeDeploymentPlansRequestRequestTypeDef = TypedDict(
    "ListEdgeDeploymentPlansRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "DeviceFleetNameContains": NotRequired[str],
        "SortBy": NotRequired[ListEdgeDeploymentPlansSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListEdgePackagingJobsRequestRequestTypeDef = TypedDict(
    "ListEdgePackagingJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelNameContains": NotRequired[str],
        "StatusEquals": NotRequired[EdgePackagingJobStatusType],
        "SortBy": NotRequired[ListEdgePackagingJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListEndpointConfigsInputRequestTypeDef = TypedDict(
    "ListEndpointConfigsInputRequestTypeDef",
    {
        "SortBy": NotRequired[EndpointConfigSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)
ListEndpointsInputRequestTypeDef = TypedDict(
    "ListEndpointsInputRequestTypeDef",
    {
        "SortBy": NotRequired[EndpointSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[EndpointStatusType],
    },
)
ListExperimentsRequestRequestTypeDef = TypedDict(
    "ListExperimentsRequestRequestTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListFeatureGroupsRequestRequestTypeDef = TypedDict(
    "ListFeatureGroupsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "FeatureGroupStatusEquals": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatusEquals": NotRequired[OfflineStoreStatusValueType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[FeatureGroupSortOrderType],
        "SortBy": NotRequired[FeatureGroupSortByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListFlowDefinitionsRequestRequestTypeDef = TypedDict(
    "ListFlowDefinitionsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListHubContentVersionsRequestRequestTypeDef = TypedDict(
    "ListHubContentVersionsRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "HubContentName": str,
        "MinVersion": NotRequired[str],
        "MaxSchemaVersion": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[HubContentSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListHubContentsRequestRequestTypeDef = TypedDict(
    "ListHubContentsRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "NameContains": NotRequired[str],
        "MaxSchemaVersion": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[HubContentSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListHubsRequestRequestTypeDef = TypedDict(
    "ListHubsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[HubSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListHumanTaskUisRequestRequestTypeDef = TypedDict(
    "ListHumanTaskUisRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListHyperParameterTuningJobsRequestRequestTypeDef = TypedDict(
    "ListHyperParameterTuningJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortBy": NotRequired[HyperParameterTuningJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[HyperParameterTuningJobStatusType],
    },
)
ListImageVersionsRequestRequestTypeDef = TypedDict(
    "ListImageVersionsRequestRequestTypeDef",
    {
        "ImageName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ImageVersionSortByType],
        "SortOrder": NotRequired[ImageVersionSortOrderType],
    },
)
ListImagesRequestRequestTypeDef = TypedDict(
    "ListImagesRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ImageSortByType],
        "SortOrder": NotRequired[ImageSortOrderType],
    },
)
ListInferenceComponentsInputRequestTypeDef = TypedDict(
    "ListInferenceComponentsInputRequestTypeDef",
    {
        "SortBy": NotRequired[InferenceComponentSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[InferenceComponentStatusType],
        "EndpointNameEquals": NotRequired[str],
        "VariantNameEquals": NotRequired[str],
    },
)
ListInferenceExperimentsRequestRequestTypeDef = TypedDict(
    "ListInferenceExperimentsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "Type": NotRequired[Literal["ShadowMode"]],
        "StatusEquals": NotRequired[InferenceExperimentStatusType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortInferenceExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListInferenceRecommendationsJobsRequestRequestTypeDef = TypedDict(
    "ListInferenceRecommendationsJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[RecommendationJobStatusType],
        "SortBy": NotRequired[ListInferenceRecommendationsJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ModelNameEquals": NotRequired[str],
        "ModelPackageVersionArnEquals": NotRequired[str],
    },
)
ListLabelingJobsForWorkteamRequestRequestTypeDef = TypedDict(
    "ListLabelingJobsForWorkteamRequestRequestTypeDef",
    {
        "WorkteamArn": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "JobReferenceCodeContains": NotRequired[str],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListLabelingJobsRequestRequestTypeDef = TypedDict(
    "ListLabelingJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "StatusEquals": NotRequired[LabelingJobStatusType],
    },
)
ListLineageGroupsRequestRequestTypeDef = TypedDict(
    "ListLineageGroupsRequestRequestTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortLineageGroupsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListMlflowTrackingServersRequestRequestTypeDef = TypedDict(
    "ListMlflowTrackingServersRequestRequestTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "TrackingServerStatus": NotRequired[TrackingServerStatusType],
        "MlflowVersion": NotRequired[str],
        "SortBy": NotRequired[SortTrackingServerByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListModelBiasJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListModelBiasJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)
ListModelCardExportJobsRequestRequestTypeDef = TypedDict(
    "ListModelCardExportJobsRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "ModelCardVersion": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "ModelCardExportJobNameContains": NotRequired[str],
        "StatusEquals": NotRequired[ModelCardExportJobStatusType],
        "SortBy": NotRequired[ModelCardExportJobSortByType],
        "SortOrder": NotRequired[ModelCardExportJobSortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListModelCardVersionsRequestRequestTypeDef = TypedDict(
    "ListModelCardVersionsRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[Literal["Version"]],
        "SortOrder": NotRequired[ModelCardSortOrderType],
    },
)
ListModelCardsRequestRequestTypeDef = TypedDict(
    "ListModelCardsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ModelCardSortByType],
        "SortOrder": NotRequired[ModelCardSortOrderType],
    },
)
ListModelExplainabilityJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListModelExplainabilityJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)
ListModelPackageGroupsInputRequestTypeDef = TypedDict(
    "ListModelPackageGroupsInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ModelPackageGroupSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "CrossAccountFilterOption": NotRequired[CrossAccountFilterOptionType],
    },
)
ListModelPackagesInputRequestTypeDef = TypedDict(
    "ListModelPackagesInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageType": NotRequired[ModelPackageTypeType],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ModelPackageSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListModelQualityJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListModelQualityJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)
ListModelsInputRequestTypeDef = TypedDict(
    "ListModelsInputRequestTypeDef",
    {
        "SortBy": NotRequired[ModelSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)
ListMonitoringAlertHistoryRequestRequestTypeDef = TypedDict(
    "ListMonitoringAlertHistoryRequestRequestTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringAlertName": NotRequired[str],
        "SortBy": NotRequired[MonitoringAlertHistorySortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[MonitoringAlertStatusType],
    },
)
ListMonitoringExecutionsRequestRequestTypeDef = TypedDict(
    "ListMonitoringExecutionsRequestRequestTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringExecutionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ScheduledTimeBefore": NotRequired[TimestampTypeDef],
        "ScheduledTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ExecutionStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
    },
)
ListMonitoringSchedulesRequestRequestTypeDef = TypedDict(
    "ListMonitoringSchedulesRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringScheduleSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ScheduleStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
    },
)
ListNotebookInstanceLifecycleConfigsInputRequestTypeDef = TypedDict(
    "ListNotebookInstanceLifecycleConfigsInputRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortBy": NotRequired[NotebookInstanceLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceLifecycleConfigSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
    },
)
ListNotebookInstancesInputRequestTypeDef = TypedDict(
    "ListNotebookInstancesInputRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortBy": NotRequired[NotebookInstanceSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[NotebookInstanceStatusType],
        "NotebookInstanceLifecycleConfigNameContains": NotRequired[str],
        "DefaultCodeRepositoryContains": NotRequired[str],
        "AdditionalCodeRepositoryEquals": NotRequired[str],
    },
)
ListOptimizationJobsRequestRequestTypeDef = TypedDict(
    "ListOptimizationJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "OptimizationContains": NotRequired[str],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[OptimizationJobStatusType],
        "SortBy": NotRequired[ListOptimizationJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListPipelineExecutionsRequestRequestTypeDef = TypedDict(
    "ListPipelineExecutionsRequestRequestTypeDef",
    {
        "PipelineName": str,
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelineExecutionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListPipelinesRequestRequestTypeDef = TypedDict(
    "ListPipelinesRequestRequestTypeDef",
    {
        "PipelineNamePrefix": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelinesByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListProcessingJobsRequestRequestTypeDef = TypedDict(
    "ListProcessingJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[ProcessingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListProjectsInputRequestTypeDef = TypedDict(
    "ListProjectsInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ProjectSortByType],
        "SortOrder": NotRequired[ProjectSortOrderType],
    },
)
ListResourceCatalogsRequestRequestTypeDef = TypedDict(
    "ListResourceCatalogsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[ResourceCatalogSortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListStudioLifecycleConfigsRequestRequestTypeDef = TypedDict(
    "ListStudioLifecycleConfigsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "NameContains": NotRequired[str],
        "AppTypeEquals": NotRequired[StudioLifecycleConfigAppTypeType],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[StudioLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
    },
)
ListTrainingJobsRequestRequestTypeDef = TypedDict(
    "ListTrainingJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "WarmPoolStatusEquals": NotRequired[WarmPoolResourceStatusType],
    },
)
ListTransformJobsRequestRequestTypeDef = TypedDict(
    "ListTransformJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TransformJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListTrialComponentsRequestRequestTypeDef = TypedDict(
    "ListTrialComponentsRequestRequestTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
        "SourceArn": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialComponentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListTrialsRequestRequestTypeDef = TypedDict(
    "ListTrialsRequestRequestTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialComponentName": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialsByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
QueryFiltersTypeDef = TypedDict(
    "QueryFiltersTypeDef",
    {
        "Types": NotRequired[Sequence[str]],
        "LineageTypes": NotRequired[Sequence[LineageTypeType]],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "ModifiedBefore": NotRequired[TimestampTypeDef],
        "ModifiedAfter": NotRequired[TimestampTypeDef],
        "Properties": NotRequired[Mapping[str, str]],
    },
)
CreateTrialComponentRequestRequestTypeDef = TypedDict(
    "CreateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "DisplayName": NotRequired[str],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Parameters": NotRequired[Mapping[str, TrialComponentParameterValueTypeDef]],
        "InputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "OutputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateTrialComponentRequestRequestTypeDef = TypedDict(
    "UpdateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "DisplayName": NotRequired[str],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Parameters": NotRequired[Mapping[str, TrialComponentParameterValueTypeDef]],
        "ParametersToRemove": NotRequired[Sequence[str]],
        "InputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "InputArtifactsToRemove": NotRequired[Sequence[str]],
        "OutputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "OutputArtifactsToRemove": NotRequired[Sequence[str]],
    },
)
CreateWorkforceRequestRequestTypeDef = TypedDict(
    "CreateWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
        "CognitoConfig": NotRequired[CognitoConfigTypeDef],
        "OidcConfig": NotRequired[OidcConfigTypeDef],
        "SourceIpConfig": NotRequired[SourceIpConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "WorkforceVpcConfig": NotRequired[WorkforceVpcConfigRequestTypeDef],
    },
)
UpdateWorkforceRequestRequestTypeDef = TypedDict(
    "UpdateWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
        "SourceIpConfig": NotRequired[SourceIpConfigTypeDef],
        "OidcConfig": NotRequired[OidcConfigTypeDef],
        "WorkforceVpcConfig": NotRequired[WorkforceVpcConfigRequestTypeDef],
    },
)
CustomFileSystemConfigTypeDef = TypedDict(
    "CustomFileSystemConfigTypeDef",
    {
        "EFSFileSystemConfig": NotRequired[EFSFileSystemConfigTypeDef],
    },
)
CustomFileSystemTypeDef = TypedDict(
    "CustomFileSystemTypeDef",
    {
        "EFSFileSystem": NotRequired[EFSFileSystemTypeDef],
    },
)
DataQualityAppSpecificationUnionTypeDef = Union[
    DataQualityAppSpecificationTypeDef, DataQualityAppSpecificationOutputTypeDef
]
ModelBiasBaselineConfigTypeDef = TypedDict(
    "ModelBiasBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
    },
)
ModelExplainabilityBaselineConfigTypeDef = TypedDict(
    "ModelExplainabilityBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
    },
)
ModelQualityBaselineConfigTypeDef = TypedDict(
    "ModelQualityBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
    },
)
DataQualityBaselineConfigTypeDef = TypedDict(
    "DataQualityBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
        "StatisticsResource": NotRequired[MonitoringStatisticsResourceTypeDef],
    },
)
MonitoringBaselineConfigTypeDef = TypedDict(
    "MonitoringBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
        "StatisticsResource": NotRequired[MonitoringStatisticsResourceTypeDef],
    },
)
DataSourceExtraOutputTypeDef = TypedDict(
    "DataSourceExtraOutputTypeDef",
    {
        "S3DataSource": NotRequired[S3DataSourceExtraOutputTypeDef],
        "FileSystemDataSource": NotRequired[FileSystemDataSourceTypeDef],
    },
)
DataSourceOutputTypeDef = TypedDict(
    "DataSourceOutputTypeDef",
    {
        "S3DataSource": NotRequired[S3DataSourceOutputTypeDef],
        "FileSystemDataSource": NotRequired[FileSystemDataSourceTypeDef],
    },
)
DataSourceTypeDef = TypedDict(
    "DataSourceTypeDef",
    {
        "S3DataSource": NotRequired[S3DataSourceTypeDef],
        "FileSystemDataSource": NotRequired[FileSystemDataSourceTypeDef],
    },
)
DatasetDefinitionTypeDef = TypedDict(
    "DatasetDefinitionTypeDef",
    {
        "AthenaDatasetDefinition": NotRequired[AthenaDatasetDefinitionTypeDef],
        "RedshiftDatasetDefinition": NotRequired[RedshiftDatasetDefinitionTypeDef],
        "LocalPath": NotRequired[str],
        "DataDistributionType": NotRequired[DataDistributionTypeType],
        "InputMode": NotRequired[InputModeType],
    },
)
DebugRuleConfigurationUnionTypeDef = Union[
    DebugRuleConfigurationTypeDef, DebugRuleConfigurationExtraOutputTypeDef
]
DefaultSpaceStorageSettingsTypeDef = TypedDict(
    "DefaultSpaceStorageSettingsTypeDef",
    {
        "DefaultEbsStorageSettings": NotRequired[DefaultEbsStorageSettingsTypeDef],
    },
)
DeleteDomainRequestRequestTypeDef = TypedDict(
    "DeleteDomainRequestRequestTypeDef",
    {
        "DomainId": str,
        "RetentionPolicy": NotRequired[RetentionPolicyTypeDef],
    },
)
InferenceComponentContainerSpecificationSummaryTypeDef = TypedDict(
    "InferenceComponentContainerSpecificationSummaryTypeDef",
    {
        "DeployedImage": NotRequired[DeployedImageTypeDef],
        "ArtifactUrl": NotRequired[str],
        "Environment": NotRequired[Dict[str, str]],
    },
)
DeploymentRecommendationTypeDef = TypedDict(
    "DeploymentRecommendationTypeDef",
    {
        "RecommendationStatus": RecommendationStatusType,
        "RealTimeInferenceRecommendations": NotRequired[
            List[RealTimeInferenceRecommendationTypeDef]
        ],
    },
)
DeploymentStageStatusSummaryTypeDef = TypedDict(
    "DeploymentStageStatusSummaryTypeDef",
    {
        "StageName": str,
        "DeviceSelectionConfig": DeviceSelectionConfigOutputTypeDef,
        "DeploymentConfig": EdgeDeploymentConfigTypeDef,
        "DeploymentStatus": EdgeDeploymentStatusTypeDef,
    },
)
DeploymentStageTypeDef = TypedDict(
    "DeploymentStageTypeDef",
    {
        "StageName": str,
        "DeviceSelectionConfig": DeviceSelectionConfigTypeDef,
        "DeploymentConfig": NotRequired[EdgeDeploymentConfigTypeDef],
    },
)
NeoVpcConfigUnionTypeDef = Union[NeoVpcConfigTypeDef, NeoVpcConfigOutputTypeDef]
DescribeDeviceResponseTypeDef = TypedDict(
    "DescribeDeviceResponseTypeDef",
    {
        "DeviceArn": str,
        "DeviceName": str,
        "Description": str,
        "DeviceFleetName": str,
        "IotThingName": str,
        "RegistrationTime": datetime,
        "LatestHeartbeat": datetime,
        "Models": List[EdgeModelTypeDef],
        "MaxModels": int,
        "AgentVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeEdgePackagingJobResponseTypeDef = TypedDict(
    "DescribeEdgePackagingJobResponseTypeDef",
    {
        "EdgePackagingJobArn": str,
        "EdgePackagingJobName": str,
        "CompilationJobName": str,
        "ModelName": str,
        "ModelVersion": str,
        "RoleArn": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "ResourceKey": str,
        "EdgePackagingJobStatus": EdgePackagingJobStatusType,
        "EdgePackagingJobStatusMessage": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ModelArtifact": str,
        "ModelSignature": str,
        "PresetDeploymentOutput": EdgePresetDeploymentOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeEndpointInputEndpointDeletedWaitTypeDef = TypedDict(
    "DescribeEndpointInputEndpointDeletedWaitTypeDef",
    {
        "EndpointName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeEndpointInputEndpointInServiceWaitTypeDef = TypedDict(
    "DescribeEndpointInputEndpointInServiceWaitTypeDef",
    {
        "EndpointName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeImageRequestImageCreatedWaitTypeDef = TypedDict(
    "DescribeImageRequestImageCreatedWaitTypeDef",
    {
        "ImageName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeImageRequestImageDeletedWaitTypeDef = TypedDict(
    "DescribeImageRequestImageDeletedWaitTypeDef",
    {
        "ImageName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeImageRequestImageUpdatedWaitTypeDef = TypedDict(
    "DescribeImageRequestImageUpdatedWaitTypeDef",
    {
        "ImageName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeImageVersionRequestImageVersionCreatedWaitTypeDef = TypedDict(
    "DescribeImageVersionRequestImageVersionCreatedWaitTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeImageVersionRequestImageVersionDeletedWaitTypeDef = TypedDict(
    "DescribeImageVersionRequestImageVersionDeletedWaitTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeNotebookInstanceInputNotebookInstanceDeletedWaitTypeDef = TypedDict(
    "DescribeNotebookInstanceInputNotebookInstanceDeletedWaitTypeDef",
    {
        "NotebookInstanceName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeNotebookInstanceInputNotebookInstanceInServiceWaitTypeDef = TypedDict(
    "DescribeNotebookInstanceInputNotebookInstanceInServiceWaitTypeDef",
    {
        "NotebookInstanceName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeNotebookInstanceInputNotebookInstanceStoppedWaitTypeDef = TypedDict(
    "DescribeNotebookInstanceInputNotebookInstanceStoppedWaitTypeDef",
    {
        "NotebookInstanceName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeProcessingJobRequestProcessingJobCompletedOrStoppedWaitTypeDef = TypedDict(
    "DescribeProcessingJobRequestProcessingJobCompletedOrStoppedWaitTypeDef",
    {
        "ProcessingJobName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeTrainingJobRequestTrainingJobCompletedOrStoppedWaitTypeDef = TypedDict(
    "DescribeTrainingJobRequestTrainingJobCompletedOrStoppedWaitTypeDef",
    {
        "TrainingJobName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeTransformJobRequestTransformJobCompletedOrStoppedWaitTypeDef = TypedDict(
    "DescribeTransformJobRequestTransformJobCompletedOrStoppedWaitTypeDef",
    {
        "TransformJobName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
ExperimentSummaryTypeDef = TypedDict(
    "ExperimentSummaryTypeDef",
    {
        "ExperimentArn": NotRequired[str],
        "ExperimentName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "ExperimentSource": NotRequired[ExperimentSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
FeatureGroupSummaryTypeDef = TypedDict(
    "FeatureGroupSummaryTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureGroupArn": str,
        "CreationTime": datetime,
        "FeatureGroupStatus": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatus": NotRequired[OfflineStoreStatusTypeDef],
    },
)
DescribeFeatureMetadataResponseTypeDef = TypedDict(
    "DescribeFeatureMetadataResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "FeatureGroupName": str,
        "FeatureName": str,
        "FeatureType": FeatureTypeType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "Description": str,
        "Parameters": List[FeatureParameterTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FeatureMetadataTypeDef = TypedDict(
    "FeatureMetadataTypeDef",
    {
        "FeatureGroupArn": NotRequired[str],
        "FeatureGroupName": NotRequired[str],
        "FeatureName": NotRequired[str],
        "FeatureType": NotRequired[FeatureTypeType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "Description": NotRequired[str],
        "Parameters": NotRequired[List[FeatureParameterTypeDef]],
    },
)
UpdateFeatureMetadataRequestRequestTypeDef = TypedDict(
    "UpdateFeatureMetadataRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureName": str,
        "Description": NotRequired[str],
        "ParameterAdditions": NotRequired[Sequence[FeatureParameterTypeDef]],
        "ParameterRemovals": NotRequired[Sequence[str]],
    },
)
DescribeHubContentResponseTypeDef = TypedDict(
    "DescribeHubContentResponseTypeDef",
    {
        "HubContentName": str,
        "HubContentArn": str,
        "HubContentVersion": str,
        "HubContentType": HubContentTypeType,
        "DocumentSchemaVersion": str,
        "HubName": str,
        "HubArn": str,
        "HubContentDisplayName": str,
        "HubContentDescription": str,
        "HubContentMarkdown": str,
        "HubContentDocument": str,
        "SageMakerPublicHubContentArn": str,
        "ReferenceMinVersion": str,
        "SupportStatus": HubContentSupportStatusType,
        "HubContentSearchKeywords": List[str],
        "HubContentDependencies": List[HubContentDependencyTypeDef],
        "HubContentStatus": HubContentStatusType,
        "FailureReason": str,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeHumanTaskUiResponseTypeDef = TypedDict(
    "DescribeHumanTaskUiResponseTypeDef",
    {
        "HumanTaskUiArn": str,
        "HumanTaskUiName": str,
        "HumanTaskUiStatus": HumanTaskUiStatusType,
        "CreationTime": datetime,
        "UiTemplate": UiTemplateInfoTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InferenceExperimentSummaryTypeDef = TypedDict(
    "InferenceExperimentSummaryTypeDef",
    {
        "Name": str,
        "Type": Literal["ShadowMode"],
        "Status": InferenceExperimentStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "Schedule": NotRequired[InferenceExperimentScheduleOutputTypeDef],
        "StatusReason": NotRequired[str],
        "Description": NotRequired[str],
        "CompletionTime": NotRequired[datetime],
        "RoleArn": NotRequired[str],
    },
)
ModelBiasAppSpecificationUnionTypeDef = Union[
    ModelBiasAppSpecificationTypeDef, ModelBiasAppSpecificationOutputTypeDef
]
DescribeModelCardExportJobResponseTypeDef = TypedDict(
    "DescribeModelCardExportJobResponseTypeDef",
    {
        "ModelCardExportJobName": str,
        "ModelCardExportJobArn": str,
        "Status": ModelCardExportJobStatusType,
        "ModelCardName": str,
        "ModelCardVersion": int,
        "OutputConfig": ModelCardExportOutputConfigTypeDef,
        "CreatedAt": datetime,
        "LastModifiedAt": datetime,
        "FailureReason": str,
        "ExportArtifacts": ModelCardExportArtifactsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModelExplainabilityAppSpecificationUnionTypeDef = Union[
    ModelExplainabilityAppSpecificationTypeDef, ModelExplainabilityAppSpecificationOutputTypeDef
]
ModelQualityAppSpecificationUnionTypeDef = Union[
    ModelQualityAppSpecificationTypeDef, ModelQualityAppSpecificationOutputTypeDef
]
ListMonitoringExecutionsResponseTypeDef = TypedDict(
    "ListMonitoringExecutionsResponseTypeDef",
    {
        "MonitoringExecutionSummaries": List[MonitoringExecutionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
OptimizationVpcConfigUnionTypeDef = Union[
    OptimizationVpcConfigTypeDef, OptimizationVpcConfigOutputTypeDef
]
DescribeSubscribedWorkteamResponseTypeDef = TypedDict(
    "DescribeSubscribedWorkteamResponseTypeDef",
    {
        "SubscribedWorkteam": SubscribedWorkteamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSubscribedWorkteamsResponseTypeDef = TypedDict(
    "ListSubscribedWorkteamsResponseTypeDef",
    {
        "SubscribedWorkteams": List[SubscribedWorkteamTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
TrainingJobSummaryTypeDef = TypedDict(
    "TrainingJobSummaryTypeDef",
    {
        "TrainingJobName": str,
        "TrainingJobArn": str,
        "CreationTime": datetime,
        "TrainingJobStatus": TrainingJobStatusType,
        "TrainingEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "WarmPoolStatus": NotRequired[WarmPoolStatusTypeDef],
    },
)
TrialSummaryTypeDef = TypedDict(
    "TrialSummaryTypeDef",
    {
        "TrialArn": NotRequired[str],
        "TrialName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "TrialSource": NotRequired[TrialSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
DesiredWeightAndCapacityTypeDef = TypedDict(
    "DesiredWeightAndCapacityTypeDef",
    {
        "VariantName": str,
        "DesiredWeight": NotRequired[float],
        "DesiredInstanceCount": NotRequired[int],
        "ServerlessUpdateConfig": NotRequired[ProductionVariantServerlessUpdateConfigTypeDef],
    },
)
ListStageDevicesResponseTypeDef = TypedDict(
    "ListStageDevicesResponseTypeDef",
    {
        "DeviceDeploymentSummaries": List[DeviceDeploymentSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListDeviceFleetsResponseTypeDef = TypedDict(
    "ListDeviceFleetsResponseTypeDef",
    {
        "DeviceFleetSummaries": List[DeviceFleetSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DeviceSummaryTypeDef = TypedDict(
    "DeviceSummaryTypeDef",
    {
        "DeviceName": str,
        "DeviceArn": str,
        "Description": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
        "IotThingName": NotRequired[str],
        "RegistrationTime": NotRequired[datetime],
        "LatestHeartbeat": NotRequired[datetime],
        "Models": NotRequired[List[EdgeModelSummaryTypeDef]],
        "AgentVersion": NotRequired[str],
    },
)
RegisterDevicesRequestRequestTypeDef = TypedDict(
    "RegisterDevicesRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "Devices": Sequence[DeviceTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateDevicesRequestRequestTypeDef = TypedDict(
    "UpdateDevicesRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "Devices": Sequence[DeviceTypeDef],
    },
)
ListDomainsResponseTypeDef = TypedDict(
    "ListDomainsResponseTypeDef",
    {
        "Domains": List[DomainDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DriftCheckBiasTypeDef = TypedDict(
    "DriftCheckBiasTypeDef",
    {
        "ConfigFile": NotRequired[FileSourceTypeDef],
        "PreTrainingConstraints": NotRequired[MetricsSourceTypeDef],
        "PostTrainingConstraints": NotRequired[MetricsSourceTypeDef],
    },
)
DriftCheckExplainabilityTypeDef = TypedDict(
    "DriftCheckExplainabilityTypeDef",
    {
        "Constraints": NotRequired[MetricsSourceTypeDef],
        "ConfigFile": NotRequired[FileSourceTypeDef],
    },
)
SpaceStorageSettingsTypeDef = TypedDict(
    "SpaceStorageSettingsTypeDef",
    {
        "EbsStorageSettings": NotRequired[EbsStorageSettingsTypeDef],
    },
)
ListEdgeDeploymentPlansResponseTypeDef = TypedDict(
    "ListEdgeDeploymentPlansResponseTypeDef",
    {
        "EdgeDeploymentPlanSummaries": List[EdgeDeploymentPlanSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
GetDeviceFleetReportResponseTypeDef = TypedDict(
    "GetDeviceFleetReportResponseTypeDef",
    {
        "DeviceFleetArn": str,
        "DeviceFleetName": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "Description": str,
        "ReportGenerated": datetime,
        "DeviceStats": DeviceStatsTypeDef,
        "AgentVersions": List[AgentVersionTypeDef],
        "ModelStats": List[EdgeModelStatTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListEdgePackagingJobsResponseTypeDef = TypedDict(
    "ListEdgePackagingJobsResponseTypeDef",
    {
        "EdgePackagingJobSummaries": List[EdgePackagingJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListEndpointConfigsOutputTypeDef = TypedDict(
    "ListEndpointConfigsOutputTypeDef",
    {
        "EndpointConfigs": List[EndpointConfigSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
EndpointOutputConfigurationTypeDef = TypedDict(
    "EndpointOutputConfigurationTypeDef",
    {
        "EndpointName": str,
        "VariantName": str,
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "InitialInstanceCount": NotRequired[int],
        "ServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
    },
)
EndpointPerformanceTypeDef = TypedDict(
    "EndpointPerformanceTypeDef",
    {
        "Metrics": InferenceMetricsTypeDef,
        "EndpointInfo": EndpointInfoTypeDef,
    },
)
ListEndpointsOutputTypeDef = TypedDict(
    "ListEndpointsOutputTypeDef",
    {
        "Endpoints": List[EndpointSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ModelConfigurationTypeDef = TypedDict(
    "ModelConfigurationTypeDef",
    {
        "InferenceSpecificationName": NotRequired[str],
        "EnvironmentParameters": NotRequired[List[EnvironmentParameterTypeDef]],
        "CompilationJobName": NotRequired[str],
    },
)
NestedFiltersTypeDef = TypedDict(
    "NestedFiltersTypeDef",
    {
        "NestedPropertyName": str,
        "Filters": Sequence[FilterTypeDef],
    },
)
HyperParameterTrainingJobSummaryTypeDef = TypedDict(
    "HyperParameterTrainingJobSummaryTypeDef",
    {
        "TrainingJobName": str,
        "TrainingJobArn": str,
        "CreationTime": datetime,
        "TrainingJobStatus": TrainingJobStatusType,
        "TunedHyperParameters": Dict[str, str],
        "TrainingJobDefinitionName": NotRequired[str],
        "TuningJobName": NotRequired[str],
        "TrainingStartTime": NotRequired[datetime],
        "TrainingEndTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "FinalHyperParameterTuningJobObjectiveMetric": NotRequired[
            FinalHyperParameterTuningJobObjectiveMetricTypeDef
        ],
        "ObjectiveStatus": NotRequired[ObjectiveStatusType],
    },
)
ListFlowDefinitionsResponseTypeDef = TypedDict(
    "ListFlowDefinitionsResponseTypeDef",
    {
        "FlowDefinitionSummaries": List[FlowDefinitionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
GetScalingConfigurationRecommendationRequestRequestTypeDef = TypedDict(
    "GetScalingConfigurationRecommendationRequestRequestTypeDef",
    {
        "InferenceRecommendationsJobName": str,
        "RecommendationId": NotRequired[str],
        "EndpointName": NotRequired[str],
        "TargetCpuUtilizationPerCore": NotRequired[int],
        "ScalingPolicyObjective": NotRequired[ScalingPolicyObjectiveTypeDef],
    },
)
GetSearchSuggestionsResponseTypeDef = TypedDict(
    "GetSearchSuggestionsResponseTypeDef",
    {
        "PropertyNameSuggestions": List[PropertyNameSuggestionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCodeRepositoryInputRequestTypeDef = TypedDict(
    "UpdateCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
        "GitConfig": NotRequired[GitConfigForUpdateTypeDef],
    },
)
ListHubContentVersionsResponseTypeDef = TypedDict(
    "ListHubContentVersionsResponseTypeDef",
    {
        "HubContentSummaries": List[HubContentInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListHubContentsResponseTypeDef = TypedDict(
    "ListHubContentsResponseTypeDef",
    {
        "HubContentSummaries": List[HubContentInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListHubsResponseTypeDef = TypedDict(
    "ListHubsResponseTypeDef",
    {
        "HubSummaries": List[HubInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
HumanLoopActivationConfigTypeDef = TypedDict(
    "HumanLoopActivationConfigTypeDef",
    {
        "HumanLoopActivationConditionsConfig": HumanLoopActivationConditionsConfigTypeDef,
    },
)
ListHumanTaskUisResponseTypeDef = TypedDict(
    "ListHumanTaskUisResponseTypeDef",
    {
        "HumanTaskUiSummaries": List[HumanTaskUiSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
NetworkConfigExtraOutputTypeDef = TypedDict(
    "NetworkConfigExtraOutputTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigExtraOutputTypeDef],
    },
)
VpcConfigUnionTypeDef = Union[VpcConfigTypeDef, VpcConfigExtraOutputTypeDef]
HyperParameterTuningResourceConfigExtraOutputTypeDef = TypedDict(
    "HyperParameterTuningResourceConfigExtraOutputTypeDef",
    {
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeSizeInGB": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "AllocationStrategy": NotRequired[Literal["Prioritized"]],
        "InstanceConfigs": NotRequired[List[HyperParameterTuningInstanceConfigTypeDef]],
    },
)
HyperParameterTuningResourceConfigOutputTypeDef = TypedDict(
    "HyperParameterTuningResourceConfigOutputTypeDef",
    {
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeSizeInGB": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "AllocationStrategy": NotRequired[Literal["Prioritized"]],
        "InstanceConfigs": NotRequired[List[HyperParameterTuningInstanceConfigTypeDef]],
    },
)
HyperParameterTuningResourceConfigTypeDef = TypedDict(
    "HyperParameterTuningResourceConfigTypeDef",
    {
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeSizeInGB": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "AllocationStrategy": NotRequired[Literal["Prioritized"]],
        "InstanceConfigs": NotRequired[Sequence[HyperParameterTuningInstanceConfigTypeDef]],
    },
)
HyperParameterTuningJobSummaryTypeDef = TypedDict(
    "HyperParameterTuningJobSummaryTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "HyperParameterTuningJobArn": str,
        "HyperParameterTuningJobStatus": HyperParameterTuningJobStatusType,
        "Strategy": HyperParameterTuningJobStrategyTypeType,
        "CreationTime": datetime,
        "TrainingJobStatusCounters": TrainingJobStatusCountersTypeDef,
        "ObjectiveStatusCounters": ObjectiveStatusCountersTypeDef,
        "HyperParameterTuningEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "ResourceLimits": NotRequired[ResourceLimitsTypeDef],
    },
)
HyperParameterTuningJobStrategyConfigTypeDef = TypedDict(
    "HyperParameterTuningJobStrategyConfigTypeDef",
    {
        "HyperbandStrategyConfig": NotRequired[HyperbandStrategyConfigTypeDef],
    },
)
HyperParameterTuningJobWarmStartConfigExtraOutputTypeDef = TypedDict(
    "HyperParameterTuningJobWarmStartConfigExtraOutputTypeDef",
    {
        "ParentHyperParameterTuningJobs": List[ParentHyperParameterTuningJobTypeDef],
        "WarmStartType": HyperParameterTuningJobWarmStartTypeType,
    },
)
HyperParameterTuningJobWarmStartConfigOutputTypeDef = TypedDict(
    "HyperParameterTuningJobWarmStartConfigOutputTypeDef",
    {
        "ParentHyperParameterTuningJobs": List[ParentHyperParameterTuningJobTypeDef],
        "WarmStartType": HyperParameterTuningJobWarmStartTypeType,
    },
)
HyperParameterTuningJobWarmStartConfigTypeDef = TypedDict(
    "HyperParameterTuningJobWarmStartConfigTypeDef",
    {
        "ParentHyperParameterTuningJobs": Sequence[ParentHyperParameterTuningJobTypeDef],
        "WarmStartType": HyperParameterTuningJobWarmStartTypeType,
    },
)
UserContextTypeDef = TypedDict(
    "UserContextTypeDef",
    {
        "UserProfileArn": NotRequired[str],
        "UserProfileName": NotRequired[str],
        "DomainId": NotRequired[str],
        "IamIdentity": NotRequired[IamIdentityTypeDef],
    },
)
S3PresignTypeDef = TypedDict(
    "S3PresignTypeDef",
    {
        "IamPolicyConstraints": NotRequired[IamPolicyConstraintsTypeDef],
    },
)
ImageConfigTypeDef = TypedDict(
    "ImageConfigTypeDef",
    {
        "RepositoryAccessMode": RepositoryAccessModeType,
        "RepositoryAuthConfig": NotRequired[RepositoryAuthConfigTypeDef],
    },
)
ListImagesResponseTypeDef = TypedDict(
    "ListImagesResponseTypeDef",
    {
        "Images": List[ImageTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListImageVersionsResponseTypeDef = TypedDict(
    "ListImageVersionsResponseTypeDef",
    {
        "ImageVersions": List[ImageVersionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
InferenceComponentSpecificationTypeDef = TypedDict(
    "InferenceComponentSpecificationTypeDef",
    {
        "ComputeResourceRequirements": InferenceComponentComputeResourceRequirementsTypeDef,
        "ModelName": NotRequired[str],
        "Container": NotRequired[InferenceComponentContainerSpecificationTypeDef],
        "StartupParameters": NotRequired[InferenceComponentStartupParametersTypeDef],
    },
)
ListInferenceComponentsOutputTypeDef = TypedDict(
    "ListInferenceComponentsOutputTypeDef",
    {
        "InferenceComponents": List[InferenceComponentSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListInferenceRecommendationsJobsResponseTypeDef = TypedDict(
    "ListInferenceRecommendationsJobsResponseTypeDef",
    {
        "InferenceRecommendationsJobs": List[InferenceRecommendationsJobTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ResourceConfigExtraOutputTypeDef = TypedDict(
    "ResourceConfigExtraOutputTypeDef",
    {
        "VolumeSizeInGB": int,
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "KeepAlivePeriodInSeconds": NotRequired[int],
        "InstanceGroups": NotRequired[List[InstanceGroupTypeDef]],
    },
)
ResourceConfigOutputTypeDef = TypedDict(
    "ResourceConfigOutputTypeDef",
    {
        "VolumeSizeInGB": int,
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "KeepAlivePeriodInSeconds": NotRequired[int],
        "InstanceGroups": NotRequired[List[InstanceGroupTypeDef]],
    },
)
ResourceConfigTypeDef = TypedDict(
    "ResourceConfigTypeDef",
    {
        "VolumeSizeInGB": int,
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "KeepAlivePeriodInSeconds": NotRequired[int],
        "InstanceGroups": NotRequired[Sequence[InstanceGroupTypeDef]],
    },
)
ParameterRangeOutputTypeDef = TypedDict(
    "ParameterRangeOutputTypeDef",
    {
        "IntegerParameterRangeSpecification": NotRequired[
            IntegerParameterRangeSpecificationTypeDef
        ],
        "ContinuousParameterRangeSpecification": NotRequired[
            ContinuousParameterRangeSpecificationTypeDef
        ],
        "CategoricalParameterRangeSpecification": NotRequired[
            CategoricalParameterRangeSpecificationOutputTypeDef
        ],
    },
)
ParameterRangeTypeDef = TypedDict(
    "ParameterRangeTypeDef",
    {
        "IntegerParameterRangeSpecification": NotRequired[
            IntegerParameterRangeSpecificationTypeDef
        ],
        "ContinuousParameterRangeSpecification": NotRequired[
            ContinuousParameterRangeSpecificationTypeDef
        ],
        "CategoricalParameterRangeSpecification": NotRequired[
            CategoricalParameterRangeSpecificationTypeDef
        ],
    },
)
ParameterRangesExtraOutputTypeDef = TypedDict(
    "ParameterRangesExtraOutputTypeDef",
    {
        "IntegerParameterRanges": NotRequired[List[IntegerParameterRangeTypeDef]],
        "ContinuousParameterRanges": NotRequired[List[ContinuousParameterRangeTypeDef]],
        "CategoricalParameterRanges": NotRequired[
            List[CategoricalParameterRangeExtraOutputTypeDef]
        ],
        "AutoParameters": NotRequired[List[AutoParameterTypeDef]],
    },
)
ParameterRangesOutputTypeDef = TypedDict(
    "ParameterRangesOutputTypeDef",
    {
        "IntegerParameterRanges": NotRequired[List[IntegerParameterRangeTypeDef]],
        "ContinuousParameterRanges": NotRequired[List[ContinuousParameterRangeTypeDef]],
        "CategoricalParameterRanges": NotRequired[List[CategoricalParameterRangeOutputTypeDef]],
        "AutoParameters": NotRequired[List[AutoParameterTypeDef]],
    },
)
ParameterRangesTypeDef = TypedDict(
    "ParameterRangesTypeDef",
    {
        "IntegerParameterRanges": NotRequired[Sequence[IntegerParameterRangeTypeDef]],
        "ContinuousParameterRanges": NotRequired[Sequence[ContinuousParameterRangeTypeDef]],
        "CategoricalParameterRanges": NotRequired[Sequence[CategoricalParameterRangeTypeDef]],
        "AutoParameters": NotRequired[Sequence[AutoParameterTypeDef]],
    },
)
KernelGatewayImageConfigExtraOutputTypeDef = TypedDict(
    "KernelGatewayImageConfigExtraOutputTypeDef",
    {
        "KernelSpecs": List[KernelSpecTypeDef],
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
    },
)
KernelGatewayImageConfigOutputTypeDef = TypedDict(
    "KernelGatewayImageConfigOutputTypeDef",
    {
        "KernelSpecs": List[KernelSpecTypeDef],
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
    },
)
KernelGatewayImageConfigTypeDef = TypedDict(
    "KernelGatewayImageConfigTypeDef",
    {
        "KernelSpecs": Sequence[KernelSpecTypeDef],
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
    },
)
LabelingJobForWorkteamSummaryTypeDef = TypedDict(
    "LabelingJobForWorkteamSummaryTypeDef",
    {
        "JobReferenceCode": str,
        "WorkRequesterAccountId": str,
        "CreationTime": datetime,
        "LabelingJobName": NotRequired[str],
        "LabelCounters": NotRequired[LabelCountersForWorkteamTypeDef],
        "NumberOfHumanWorkersPerDataObject": NotRequired[int],
    },
)
LabelingJobDataSourceTypeDef = TypedDict(
    "LabelingJobDataSourceTypeDef",
    {
        "S3DataSource": NotRequired[LabelingJobS3DataSourceTypeDef],
        "SnsDataSource": NotRequired[LabelingJobSnsDataSourceTypeDef],
    },
)
ListLineageGroupsResponseTypeDef = TypedDict(
    "ListLineageGroupsResponseTypeDef",
    {
        "LineageGroupSummaries": List[LineageGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListActionsRequestListActionsPaginateTypeDef = TypedDict(
    "ListActionsRequestListActionsPaginateTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ActionType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortActionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAlgorithmsInputListAlgorithmsPaginateTypeDef = TypedDict(
    "ListAlgorithmsInputListAlgorithmsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[AlgorithmSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAliasesRequestListAliasesPaginateTypeDef = TypedDict(
    "ListAliasesRequestListAliasesPaginateTypeDef",
    {
        "ImageName": str,
        "Alias": NotRequired[str],
        "Version": NotRequired[int],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAppImageConfigsRequestListAppImageConfigsPaginateTypeDef = TypedDict(
    "ListAppImageConfigsRequestListAppImageConfigsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[AppImageConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAppsRequestListAppsPaginateTypeDef = TypedDict(
    "ListAppsRequestListAppsPaginateTypeDef",
    {
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameEquals": NotRequired[str],
        "SpaceNameEquals": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListArtifactsRequestListArtifactsPaginateTypeDef = TypedDict(
    "ListArtifactsRequestListArtifactsPaginateTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ArtifactType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAssociationsRequestListAssociationsPaginateTypeDef = TypedDict(
    "ListAssociationsRequestListAssociationsPaginateTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "SourceType": NotRequired[str],
        "DestinationType": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortAssociationsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAutoMLJobsRequestListAutoMLJobsPaginateTypeDef = TypedDict(
    "ListAutoMLJobsRequestListAutoMLJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[AutoMLJobStatusType],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[AutoMLSortByType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCandidatesForAutoMLJobRequestListCandidatesForAutoMLJobPaginateTypeDef = TypedDict(
    "ListCandidatesForAutoMLJobRequestListCandidatesForAutoMLJobPaginateTypeDef",
    {
        "AutoMLJobName": str,
        "StatusEquals": NotRequired[CandidateStatusType],
        "CandidateNameEquals": NotRequired[str],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[CandidateSortByType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListClusterNodesRequestListClusterNodesPaginateTypeDef = TypedDict(
    "ListClusterNodesRequestListClusterNodesPaginateTypeDef",
    {
        "ClusterName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "InstanceGroupNameContains": NotRequired[str],
        "SortBy": NotRequired[ClusterSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListClustersRequestListClustersPaginateTypeDef = TypedDict(
    "ListClustersRequestListClustersPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ClusterSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCodeRepositoriesInputListCodeRepositoriesPaginateTypeDef = TypedDict(
    "ListCodeRepositoriesInputListCodeRepositoriesPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[CodeRepositorySortByType],
        "SortOrder": NotRequired[CodeRepositorySortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCompilationJobsRequestListCompilationJobsPaginateTypeDef = TypedDict(
    "ListCompilationJobsRequestListCompilationJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[CompilationJobStatusType],
        "SortBy": NotRequired[ListCompilationJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListContextsRequestListContextsPaginateTypeDef = TypedDict(
    "ListContextsRequestListContextsPaginateTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ContextType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortContextsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDataQualityJobDefinitionsRequestListDataQualityJobDefinitionsPaginateTypeDef = TypedDict(
    "ListDataQualityJobDefinitionsRequestListDataQualityJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDeviceFleetsRequestListDeviceFleetsPaginateTypeDef = TypedDict(
    "ListDeviceFleetsRequestListDeviceFleetsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ListDeviceFleetsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDevicesRequestListDevicesPaginateTypeDef = TypedDict(
    "ListDevicesRequestListDevicesPaginateTypeDef",
    {
        "LatestHeartbeatAfter": NotRequired[TimestampTypeDef],
        "ModelName": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDomainsRequestListDomainsPaginateTypeDef = TypedDict(
    "ListDomainsRequestListDomainsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEdgeDeploymentPlansRequestListEdgeDeploymentPlansPaginateTypeDef = TypedDict(
    "ListEdgeDeploymentPlansRequestListEdgeDeploymentPlansPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "DeviceFleetNameContains": NotRequired[str],
        "SortBy": NotRequired[ListEdgeDeploymentPlansSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEdgePackagingJobsRequestListEdgePackagingJobsPaginateTypeDef = TypedDict(
    "ListEdgePackagingJobsRequestListEdgePackagingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelNameContains": NotRequired[str],
        "StatusEquals": NotRequired[EdgePackagingJobStatusType],
        "SortBy": NotRequired[ListEdgePackagingJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEndpointConfigsInputListEndpointConfigsPaginateTypeDef = TypedDict(
    "ListEndpointConfigsInputListEndpointConfigsPaginateTypeDef",
    {
        "SortBy": NotRequired[EndpointConfigSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEndpointsInputListEndpointsPaginateTypeDef = TypedDict(
    "ListEndpointsInputListEndpointsPaginateTypeDef",
    {
        "SortBy": NotRequired[EndpointSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[EndpointStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListExperimentsRequestListExperimentsPaginateTypeDef = TypedDict(
    "ListExperimentsRequestListExperimentsPaginateTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListFeatureGroupsRequestListFeatureGroupsPaginateTypeDef = TypedDict(
    "ListFeatureGroupsRequestListFeatureGroupsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "FeatureGroupStatusEquals": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatusEquals": NotRequired[OfflineStoreStatusValueType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[FeatureGroupSortOrderType],
        "SortBy": NotRequired[FeatureGroupSortByType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListFlowDefinitionsRequestListFlowDefinitionsPaginateTypeDef = TypedDict(
    "ListFlowDefinitionsRequestListFlowDefinitionsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListHumanTaskUisRequestListHumanTaskUisPaginateTypeDef = TypedDict(
    "ListHumanTaskUisRequestListHumanTaskUisPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListHyperParameterTuningJobsRequestListHyperParameterTuningJobsPaginateTypeDef = TypedDict(
    "ListHyperParameterTuningJobsRequestListHyperParameterTuningJobsPaginateTypeDef",
    {
        "SortBy": NotRequired[HyperParameterTuningJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[HyperParameterTuningJobStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListImageVersionsRequestListImageVersionsPaginateTypeDef = TypedDict(
    "ListImageVersionsRequestListImageVersionsPaginateTypeDef",
    {
        "ImageName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[ImageVersionSortByType],
        "SortOrder": NotRequired[ImageVersionSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListImagesRequestListImagesPaginateTypeDef = TypedDict(
    "ListImagesRequestListImagesPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ImageSortByType],
        "SortOrder": NotRequired[ImageSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInferenceComponentsInputListInferenceComponentsPaginateTypeDef = TypedDict(
    "ListInferenceComponentsInputListInferenceComponentsPaginateTypeDef",
    {
        "SortBy": NotRequired[InferenceComponentSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[InferenceComponentStatusType],
        "EndpointNameEquals": NotRequired[str],
        "VariantNameEquals": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInferenceExperimentsRequestListInferenceExperimentsPaginateTypeDef = TypedDict(
    "ListInferenceExperimentsRequestListInferenceExperimentsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "Type": NotRequired[Literal["ShadowMode"]],
        "StatusEquals": NotRequired[InferenceExperimentStatusType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortInferenceExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInferenceRecommendationsJobStepsRequestListInferenceRecommendationsJobStepsPaginateTypeDef = TypedDict(
    "ListInferenceRecommendationsJobStepsRequestListInferenceRecommendationsJobStepsPaginateTypeDef",
    {
        "JobName": str,
        "Status": NotRequired[RecommendationJobStatusType],
        "StepType": NotRequired[Literal["BENCHMARK"]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInferenceRecommendationsJobsRequestListInferenceRecommendationsJobsPaginateTypeDef = TypedDict(
    "ListInferenceRecommendationsJobsRequestListInferenceRecommendationsJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[RecommendationJobStatusType],
        "SortBy": NotRequired[ListInferenceRecommendationsJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "ModelNameEquals": NotRequired[str],
        "ModelPackageVersionArnEquals": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListLabelingJobsForWorkteamRequestListLabelingJobsForWorkteamPaginateTypeDef = TypedDict(
    "ListLabelingJobsForWorkteamRequestListLabelingJobsForWorkteamPaginateTypeDef",
    {
        "WorkteamArn": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "JobReferenceCodeContains": NotRequired[str],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListLabelingJobsRequestListLabelingJobsPaginateTypeDef = TypedDict(
    "ListLabelingJobsRequestListLabelingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "StatusEquals": NotRequired[LabelingJobStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListLineageGroupsRequestListLineageGroupsPaginateTypeDef = TypedDict(
    "ListLineageGroupsRequestListLineageGroupsPaginateTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortLineageGroupsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMlflowTrackingServersRequestListMlflowTrackingServersPaginateTypeDef = TypedDict(
    "ListMlflowTrackingServersRequestListMlflowTrackingServersPaginateTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "TrackingServerStatus": NotRequired[TrackingServerStatusType],
        "MlflowVersion": NotRequired[str],
        "SortBy": NotRequired[SortTrackingServerByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelBiasJobDefinitionsRequestListModelBiasJobDefinitionsPaginateTypeDef = TypedDict(
    "ListModelBiasJobDefinitionsRequestListModelBiasJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelCardExportJobsRequestListModelCardExportJobsPaginateTypeDef = TypedDict(
    "ListModelCardExportJobsRequestListModelCardExportJobsPaginateTypeDef",
    {
        "ModelCardName": str,
        "ModelCardVersion": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "ModelCardExportJobNameContains": NotRequired[str],
        "StatusEquals": NotRequired[ModelCardExportJobStatusType],
        "SortBy": NotRequired[ModelCardExportJobSortByType],
        "SortOrder": NotRequired[ModelCardExportJobSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelCardVersionsRequestListModelCardVersionsPaginateTypeDef = TypedDict(
    "ListModelCardVersionsRequestListModelCardVersionsPaginateTypeDef",
    {
        "ModelCardName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SortBy": NotRequired[Literal["Version"]],
        "SortOrder": NotRequired[ModelCardSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelCardsRequestListModelCardsPaginateTypeDef = TypedDict(
    "ListModelCardsRequestListModelCardsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SortBy": NotRequired[ModelCardSortByType],
        "SortOrder": NotRequired[ModelCardSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelExplainabilityJobDefinitionsRequestListModelExplainabilityJobDefinitionsPaginateTypeDef = TypedDict(
    "ListModelExplainabilityJobDefinitionsRequestListModelExplainabilityJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelPackageGroupsInputListModelPackageGroupsPaginateTypeDef = TypedDict(
    "ListModelPackageGroupsInputListModelPackageGroupsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ModelPackageGroupSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "CrossAccountFilterOption": NotRequired[CrossAccountFilterOptionType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelPackagesInputListModelPackagesPaginateTypeDef = TypedDict(
    "ListModelPackagesInputListModelPackagesPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageType": NotRequired[ModelPackageTypeType],
        "SortBy": NotRequired[ModelPackageSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelQualityJobDefinitionsRequestListModelQualityJobDefinitionsPaginateTypeDef = TypedDict(
    "ListModelQualityJobDefinitionsRequestListModelQualityJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelsInputListModelsPaginateTypeDef = TypedDict(
    "ListModelsInputListModelsPaginateTypeDef",
    {
        "SortBy": NotRequired[ModelSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMonitoringAlertHistoryRequestListMonitoringAlertHistoryPaginateTypeDef = TypedDict(
    "ListMonitoringAlertHistoryRequestListMonitoringAlertHistoryPaginateTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringAlertName": NotRequired[str],
        "SortBy": NotRequired[MonitoringAlertHistorySortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[MonitoringAlertStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMonitoringAlertsRequestListMonitoringAlertsPaginateTypeDef = TypedDict(
    "ListMonitoringAlertsRequestListMonitoringAlertsPaginateTypeDef",
    {
        "MonitoringScheduleName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMonitoringExecutionsRequestListMonitoringExecutionsPaginateTypeDef = TypedDict(
    "ListMonitoringExecutionsRequestListMonitoringExecutionsPaginateTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringExecutionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "ScheduledTimeBefore": NotRequired[TimestampTypeDef],
        "ScheduledTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ExecutionStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMonitoringSchedulesRequestListMonitoringSchedulesPaginateTypeDef = TypedDict(
    "ListMonitoringSchedulesRequestListMonitoringSchedulesPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringScheduleSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ScheduleStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListNotebookInstanceLifecycleConfigsInputListNotebookInstanceLifecycleConfigsPaginateTypeDef = TypedDict(
    "ListNotebookInstanceLifecycleConfigsInputListNotebookInstanceLifecycleConfigsPaginateTypeDef",
    {
        "SortBy": NotRequired[NotebookInstanceLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceLifecycleConfigSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListNotebookInstancesInputListNotebookInstancesPaginateTypeDef = TypedDict(
    "ListNotebookInstancesInputListNotebookInstancesPaginateTypeDef",
    {
        "SortBy": NotRequired[NotebookInstanceSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[NotebookInstanceStatusType],
        "NotebookInstanceLifecycleConfigNameContains": NotRequired[str],
        "DefaultCodeRepositoryContains": NotRequired[str],
        "AdditionalCodeRepositoryEquals": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListOptimizationJobsRequestListOptimizationJobsPaginateTypeDef = TypedDict(
    "ListOptimizationJobsRequestListOptimizationJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "OptimizationContains": NotRequired[str],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[OptimizationJobStatusType],
        "SortBy": NotRequired[ListOptimizationJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPipelineExecutionStepsRequestListPipelineExecutionStepsPaginateTypeDef = TypedDict(
    "ListPipelineExecutionStepsRequestListPipelineExecutionStepsPaginateTypeDef",
    {
        "PipelineExecutionArn": NotRequired[str],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPipelineExecutionsRequestListPipelineExecutionsPaginateTypeDef = TypedDict(
    "ListPipelineExecutionsRequestListPipelineExecutionsPaginateTypeDef",
    {
        "PipelineName": str,
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelineExecutionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPipelineParametersForExecutionRequestListPipelineParametersForExecutionPaginateTypeDef = TypedDict(
    "ListPipelineParametersForExecutionRequestListPipelineParametersForExecutionPaginateTypeDef",
    {
        "PipelineExecutionArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPipelinesRequestListPipelinesPaginateTypeDef = TypedDict(
    "ListPipelinesRequestListPipelinesPaginateTypeDef",
    {
        "PipelineNamePrefix": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelinesByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListProcessingJobsRequestListProcessingJobsPaginateTypeDef = TypedDict(
    "ListProcessingJobsRequestListProcessingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[ProcessingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListResourceCatalogsRequestListResourceCatalogsPaginateTypeDef = TypedDict(
    "ListResourceCatalogsRequestListResourceCatalogsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[ResourceCatalogSortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSpacesRequestListSpacesPaginateTypeDef = TypedDict(
    "ListSpacesRequestListSpacesPaginateTypeDef",
    {
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[SpaceSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "SpaceNameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListStageDevicesRequestListStageDevicesPaginateTypeDef = TypedDict(
    "ListStageDevicesRequestListStageDevicesPaginateTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
        "ExcludeDevicesDeployedInOtherStage": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListStudioLifecycleConfigsRequestListStudioLifecycleConfigsPaginateTypeDef = TypedDict(
    "ListStudioLifecycleConfigsRequestListStudioLifecycleConfigsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "AppTypeEquals": NotRequired[StudioLifecycleConfigAppTypeType],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[StudioLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSubscribedWorkteamsRequestListSubscribedWorkteamsPaginateTypeDef = TypedDict(
    "ListSubscribedWorkteamsRequestListSubscribedWorkteamsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTagsInputListTagsPaginateTypeDef = TypedDict(
    "ListTagsInputListTagsPaginateTypeDef",
    {
        "ResourceArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTrainingJobsForHyperParameterTuningJobRequestListTrainingJobsForHyperParameterTuningJobPaginateTypeDef = TypedDict(
    "ListTrainingJobsForHyperParameterTuningJobRequestListTrainingJobsForHyperParameterTuningJobPaginateTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[TrainingJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTrainingJobsRequestListTrainingJobsPaginateTypeDef = TypedDict(
    "ListTrainingJobsRequestListTrainingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "WarmPoolStatusEquals": NotRequired[WarmPoolResourceStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTransformJobsRequestListTransformJobsPaginateTypeDef = TypedDict(
    "ListTransformJobsRequestListTransformJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TransformJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTrialComponentsRequestListTrialComponentsPaginateTypeDef = TypedDict(
    "ListTrialComponentsRequestListTrialComponentsPaginateTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
        "SourceArn": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialComponentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTrialsRequestListTrialsPaginateTypeDef = TypedDict(
    "ListTrialsRequestListTrialsPaginateTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialComponentName": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListUserProfilesRequestListUserProfilesPaginateTypeDef = TypedDict(
    "ListUserProfilesRequestListUserProfilesPaginateTypeDef",
    {
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[UserProfileSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListWorkforcesRequestListWorkforcesPaginateTypeDef = TypedDict(
    "ListWorkforcesRequestListWorkforcesPaginateTypeDef",
    {
        "SortBy": NotRequired[ListWorkforcesSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListWorkteamsRequestListWorkteamsPaginateTypeDef = TypedDict(
    "ListWorkteamsRequestListWorkteamsPaginateTypeDef",
    {
        "SortBy": NotRequired[ListWorkteamsSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDataQualityJobDefinitionsResponseTypeDef = TypedDict(
    "ListDataQualityJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelBiasJobDefinitionsResponseTypeDef = TypedDict(
    "ListModelBiasJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelExplainabilityJobDefinitionsResponseTypeDef = TypedDict(
    "ListModelExplainabilityJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelQualityJobDefinitionsResponseTypeDef = TypedDict(
    "ListModelQualityJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListMlflowTrackingServersResponseTypeDef = TypedDict(
    "ListMlflowTrackingServersResponseTypeDef",
    {
        "TrackingServerSummaries": List[TrackingServerSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelCardExportJobsResponseTypeDef = TypedDict(
    "ListModelCardExportJobsResponseTypeDef",
    {
        "ModelCardExportJobSummaries": List[ModelCardExportJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelCardVersionsResponseTypeDef = TypedDict(
    "ListModelCardVersionsResponseTypeDef",
    {
        "ModelCardVersionSummaryList": List[ModelCardVersionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelCardsResponseTypeDef = TypedDict(
    "ListModelCardsResponseTypeDef",
    {
        "ModelCardSummaries": List[ModelCardSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelMetadataResponseTypeDef = TypedDict(
    "ListModelMetadataResponseTypeDef",
    {
        "ModelMetadataSummaries": List[ModelMetadataSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelPackageGroupsOutputTypeDef = TypedDict(
    "ListModelPackageGroupsOutputTypeDef",
    {
        "ModelPackageGroupSummaryList": List[ModelPackageGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelPackagesOutputTypeDef = TypedDict(
    "ListModelPackagesOutputTypeDef",
    {
        "ModelPackageSummaryList": List[ModelPackageSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListModelsOutputTypeDef = TypedDict(
    "ListModelsOutputTypeDef",
    {
        "Models": List[ModelSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListMonitoringAlertHistoryResponseTypeDef = TypedDict(
    "ListMonitoringAlertHistoryResponseTypeDef",
    {
        "MonitoringAlertHistory": List[MonitoringAlertHistorySummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListMonitoringSchedulesResponseTypeDef = TypedDict(
    "ListMonitoringSchedulesResponseTypeDef",
    {
        "MonitoringScheduleSummaries": List[MonitoringScheduleSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListNotebookInstanceLifecycleConfigsOutputTypeDef = TypedDict(
    "ListNotebookInstanceLifecycleConfigsOutputTypeDef",
    {
        "NotebookInstanceLifecycleConfigs": List[NotebookInstanceLifecycleConfigSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListNotebookInstancesOutputTypeDef = TypedDict(
    "ListNotebookInstancesOutputTypeDef",
    {
        "NotebookInstances": List[NotebookInstanceSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListOptimizationJobsResponseTypeDef = TypedDict(
    "ListOptimizationJobsResponseTypeDef",
    {
        "OptimizationJobSummaries": List[OptimizationJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListPipelineExecutionsResponseTypeDef = TypedDict(
    "ListPipelineExecutionsResponseTypeDef",
    {
        "PipelineExecutionSummaries": List[PipelineExecutionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListPipelineParametersForExecutionResponseTypeDef = TypedDict(
    "ListPipelineParametersForExecutionResponseTypeDef",
    {
        "PipelineParameters": List[ParameterTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListPipelinesResponseTypeDef = TypedDict(
    "ListPipelinesResponseTypeDef",
    {
        "PipelineSummaries": List[PipelineSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListProcessingJobsResponseTypeDef = TypedDict(
    "ListProcessingJobsResponseTypeDef",
    {
        "ProcessingJobSummaries": List[ProcessingJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListProjectsOutputTypeDef = TypedDict(
    "ListProjectsOutputTypeDef",
    {
        "ProjectSummaryList": List[ProjectSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListResourceCatalogsResponseTypeDef = TypedDict(
    "ListResourceCatalogsResponseTypeDef",
    {
        "ResourceCatalogs": List[ResourceCatalogTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListStudioLifecycleConfigsResponseTypeDef = TypedDict(
    "ListStudioLifecycleConfigsResponseTypeDef",
    {
        "StudioLifecycleConfigs": List[StudioLifecycleConfigDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListTransformJobsResponseTypeDef = TypedDict(
    "ListTransformJobsResponseTypeDef",
    {
        "TransformJobSummaries": List[TransformJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListUserProfilesResponseTypeDef = TypedDict(
    "ListUserProfilesResponseTypeDef",
    {
        "UserProfiles": List[UserProfileDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
MemberDefinitionExtraOutputTypeDef = TypedDict(
    "MemberDefinitionExtraOutputTypeDef",
    {
        "CognitoMemberDefinition": NotRequired[CognitoMemberDefinitionTypeDef],
        "OidcMemberDefinition": NotRequired[OidcMemberDefinitionExtraOutputTypeDef],
    },
)
MemberDefinitionOutputTypeDef = TypedDict(
    "MemberDefinitionOutputTypeDef",
    {
        "CognitoMemberDefinition": NotRequired[CognitoMemberDefinitionTypeDef],
        "OidcMemberDefinition": NotRequired[OidcMemberDefinitionOutputTypeDef],
    },
)
MemberDefinitionTypeDef = TypedDict(
    "MemberDefinitionTypeDef",
    {
        "CognitoMemberDefinition": NotRequired[CognitoMemberDefinitionTypeDef],
        "OidcMemberDefinition": NotRequired[OidcMemberDefinitionTypeDef],
    },
)
MetricSpecificationTypeDef = TypedDict(
    "MetricSpecificationTypeDef",
    {
        "Predefined": NotRequired[PredefinedMetricSpecificationTypeDef],
        "Customized": NotRequired[CustomizedMetricSpecificationTypeDef],
    },
)
S3ModelDataSourceTypeDef = TypedDict(
    "S3ModelDataSourceTypeDef",
    {
        "S3Uri": str,
        "S3DataType": S3ModelDataTypeType,
        "CompressionType": ModelCompressionTypeType,
        "ModelAccessConfig": NotRequired[ModelAccessConfigTypeDef],
        "HubAccessConfig": NotRequired[InferenceHubAccessConfigTypeDef],
    },
)
TextGenerationJobConfigOutputTypeDef = TypedDict(
    "TextGenerationJobConfigOutputTypeDef",
    {
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "BaseModelName": NotRequired[str],
        "TextGenerationHyperParameters": NotRequired[Dict[str, str]],
        "ModelAccessConfig": NotRequired[ModelAccessConfigTypeDef],
    },
)
TextGenerationJobConfigTypeDef = TypedDict(
    "TextGenerationJobConfigTypeDef",
    {
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "BaseModelName": NotRequired[str],
        "TextGenerationHyperParameters": NotRequired[Mapping[str, str]],
        "ModelAccessConfig": NotRequired[ModelAccessConfigTypeDef],
    },
)
MonitoringAlertActionsTypeDef = TypedDict(
    "MonitoringAlertActionsTypeDef",
    {
        "ModelDashboardIndicator": NotRequired[ModelDashboardIndicatorActionTypeDef],
    },
)
ModelInfrastructureConfigTypeDef = TypedDict(
    "ModelInfrastructureConfigTypeDef",
    {
        "InfrastructureType": Literal["RealTimeInference"],
        "RealTimeInferenceConfig": RealTimeInferenceConfigTypeDef,
    },
)
RecommendationJobStoppingConditionsOutputTypeDef = TypedDict(
    "RecommendationJobStoppingConditionsOutputTypeDef",
    {
        "MaxInvocations": NotRequired[int],
        "ModelLatencyThresholds": NotRequired[List[ModelLatencyThresholdTypeDef]],
        "FlatInvocations": NotRequired[FlatInvocationsType],
    },
)
RecommendationJobStoppingConditionsTypeDef = TypedDict(
    "RecommendationJobStoppingConditionsTypeDef",
    {
        "MaxInvocations": NotRequired[int],
        "ModelLatencyThresholds": NotRequired[Sequence[ModelLatencyThresholdTypeDef]],
        "FlatInvocations": NotRequired[FlatInvocationsType],
    },
)
ModelMetadataSearchExpressionTypeDef = TypedDict(
    "ModelMetadataSearchExpressionTypeDef",
    {
        "Filters": NotRequired[Sequence[ModelMetadataFilterTypeDef]],
    },
)
ModelPackageStatusDetailsTypeDef = TypedDict(
    "ModelPackageStatusDetailsTypeDef",
    {
        "ValidationStatuses": List[ModelPackageStatusItemTypeDef],
        "ImageScanStatuses": NotRequired[List[ModelPackageStatusItemTypeDef]],
    },
)
OptimizationConfigOutputTypeDef = TypedDict(
    "OptimizationConfigOutputTypeDef",
    {
        "ModelQuantizationConfig": NotRequired[ModelQuantizationConfigOutputTypeDef],
        "ModelCompilationConfig": NotRequired[ModelCompilationConfigOutputTypeDef],
    },
)
OptimizationConfigTypeDef = TypedDict(
    "OptimizationConfigTypeDef",
    {
        "ModelQuantizationConfig": NotRequired[ModelQuantizationConfigTypeDef],
        "ModelCompilationConfig": NotRequired[ModelCompilationConfigTypeDef],
    },
)
MonitoringResourcesTypeDef = TypedDict(
    "MonitoringResourcesTypeDef",
    {
        "ClusterConfig": MonitoringClusterConfigTypeDef,
    },
)
MonitoringDatasetFormatExtraOutputTypeDef = TypedDict(
    "MonitoringDatasetFormatExtraOutputTypeDef",
    {
        "Csv": NotRequired[MonitoringCsvDatasetFormatTypeDef],
        "Json": NotRequired[MonitoringJsonDatasetFormatTypeDef],
        "Parquet": NotRequired[Dict[str, Any]],
    },
)
MonitoringDatasetFormatOutputTypeDef = TypedDict(
    "MonitoringDatasetFormatOutputTypeDef",
    {
        "Csv": NotRequired[MonitoringCsvDatasetFormatTypeDef],
        "Json": NotRequired[MonitoringJsonDatasetFormatTypeDef],
        "Parquet": NotRequired[Dict[str, Any]],
    },
)
MonitoringDatasetFormatTypeDef = TypedDict(
    "MonitoringDatasetFormatTypeDef",
    {
        "Csv": NotRequired[MonitoringCsvDatasetFormatTypeDef],
        "Json": NotRequired[MonitoringJsonDatasetFormatTypeDef],
        "Parquet": NotRequired[Mapping[str, Any]],
    },
)
MonitoringOutputTypeDef = TypedDict(
    "MonitoringOutputTypeDef",
    {
        "S3Output": MonitoringS3OutputTypeDef,
    },
)
OfflineStoreConfigTypeDef = TypedDict(
    "OfflineStoreConfigTypeDef",
    {
        "S3StorageConfig": S3StorageConfigTypeDef,
        "DisableGlueTableCreation": NotRequired[bool],
        "DataCatalogConfig": NotRequired[DataCatalogConfigTypeDef],
        "TableFormat": NotRequired[TableFormatType],
    },
)
OnlineStoreConfigTypeDef = TypedDict(
    "OnlineStoreConfigTypeDef",
    {
        "SecurityConfig": NotRequired[OnlineStoreSecurityConfigTypeDef],
        "EnableOnlineStore": NotRequired[bool],
        "TtlDuration": NotRequired[TtlDurationTypeDef],
        "StorageType": NotRequired[StorageTypeType],
    },
)
OnlineStoreConfigUpdateTypeDef = TypedDict(
    "OnlineStoreConfigUpdateTypeDef",
    {
        "TtlDuration": NotRequired[TtlDurationTypeDef],
    },
)
OptimizationJobModelSourceS3TypeDef = TypedDict(
    "OptimizationJobModelSourceS3TypeDef",
    {
        "S3Uri": NotRequired[str],
        "ModelAccessConfig": NotRequired[OptimizationModelAccessConfigTypeDef],
    },
)
OutputConfigTypeDef = TypedDict(
    "OutputConfigTypeDef",
    {
        "S3OutputLocation": str,
        "TargetDevice": NotRequired[TargetDeviceType],
        "TargetPlatform": NotRequired[TargetPlatformTypeDef],
        "CompilerOptions": NotRequired[str],
        "KmsKeyId": NotRequired[str],
    },
)
PendingProductionVariantSummaryTypeDef = TypedDict(
    "PendingProductionVariantSummaryTypeDef",
    {
        "VariantName": str,
        "DeployedImages": NotRequired[List[DeployedImageTypeDef]],
        "CurrentWeight": NotRequired[float],
        "DesiredWeight": NotRequired[float],
        "CurrentInstanceCount": NotRequired[int],
        "DesiredInstanceCount": NotRequired[int],
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "AcceleratorType": NotRequired[ProductionVariantAcceleratorTypeType],
        "VariantStatus": NotRequired[List[ProductionVariantStatusTypeDef]],
        "CurrentServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "DesiredServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "ManagedInstanceScaling": NotRequired[ProductionVariantManagedInstanceScalingTypeDef],
        "RoutingConfig": NotRequired[ProductionVariantRoutingConfigTypeDef],
    },
)
ProductionVariantSummaryTypeDef = TypedDict(
    "ProductionVariantSummaryTypeDef",
    {
        "VariantName": str,
        "DeployedImages": NotRequired[List[DeployedImageTypeDef]],
        "CurrentWeight": NotRequired[float],
        "DesiredWeight": NotRequired[float],
        "CurrentInstanceCount": NotRequired[int],
        "DesiredInstanceCount": NotRequired[int],
        "VariantStatus": NotRequired[List[ProductionVariantStatusTypeDef]],
        "CurrentServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "DesiredServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "ManagedInstanceScaling": NotRequired[ProductionVariantManagedInstanceScalingTypeDef],
        "RoutingConfig": NotRequired[ProductionVariantRoutingConfigTypeDef],
    },
)
ProcessingResourcesTypeDef = TypedDict(
    "ProcessingResourcesTypeDef",
    {
        "ClusterConfig": ProcessingClusterConfigTypeDef,
    },
)
ProcessingOutputTypeDef = TypedDict(
    "ProcessingOutputTypeDef",
    {
        "OutputName": str,
        "S3Output": NotRequired[ProcessingS3OutputTypeDef],
        "FeatureStoreOutput": NotRequired[ProcessingFeatureStoreOutputTypeDef],
        "AppManaged": NotRequired[bool],
    },
)
ProductionVariantTypeDef = TypedDict(
    "ProductionVariantTypeDef",
    {
        "VariantName": str,
        "ModelName": NotRequired[str],
        "InitialInstanceCount": NotRequired[int],
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "InitialVariantWeight": NotRequired[float],
        "AcceleratorType": NotRequired[ProductionVariantAcceleratorTypeType],
        "CoreDumpConfig": NotRequired[ProductionVariantCoreDumpConfigTypeDef],
        "ServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "VolumeSizeInGB": NotRequired[int],
        "ModelDataDownloadTimeoutInSeconds": NotRequired[int],
        "ContainerStartupHealthCheckTimeoutInSeconds": NotRequired[int],
        "EnableSSMAccess": NotRequired[bool],
        "ManagedInstanceScaling": NotRequired[ProductionVariantManagedInstanceScalingTypeDef],
        "RoutingConfig": NotRequired[ProductionVariantRoutingConfigTypeDef],
        "InferenceAmiVersion": NotRequired[Literal["al2-ami-sagemaker-inference-gpu-2"]],
    },
)
ProfilerConfigUnionTypeDef = Union[ProfilerConfigTypeDef, ProfilerConfigExtraOutputTypeDef]
ProfilerRuleConfigurationUnionTypeDef = Union[
    ProfilerRuleConfigurationTypeDef, ProfilerRuleConfigurationOutputTypeDef
]
SuggestionQueryTypeDef = TypedDict(
    "SuggestionQueryTypeDef",
    {
        "PropertyNameQuery": NotRequired[PropertyNameQueryTypeDef],
    },
)
ServiceCatalogProvisioningDetailsExtraOutputTypeDef = TypedDict(
    "ServiceCatalogProvisioningDetailsExtraOutputTypeDef",
    {
        "ProductId": str,
        "ProvisioningArtifactId": NotRequired[str],
        "PathId": NotRequired[str],
        "ProvisioningParameters": NotRequired[List[ProvisioningParameterTypeDef]],
    },
)
ServiceCatalogProvisioningDetailsOutputTypeDef = TypedDict(
    "ServiceCatalogProvisioningDetailsOutputTypeDef",
    {
        "ProductId": str,
        "ProvisioningArtifactId": NotRequired[str],
        "PathId": NotRequired[str],
        "ProvisioningParameters": NotRequired[List[ProvisioningParameterTypeDef]],
    },
)
ServiceCatalogProvisioningDetailsTypeDef = TypedDict(
    "ServiceCatalogProvisioningDetailsTypeDef",
    {
        "ProductId": str,
        "ProvisioningArtifactId": NotRequired[str],
        "PathId": NotRequired[str],
        "ProvisioningParameters": NotRequired[Sequence[ProvisioningParameterTypeDef]],
    },
)
ServiceCatalogProvisioningUpdateDetailsTypeDef = TypedDict(
    "ServiceCatalogProvisioningUpdateDetailsTypeDef",
    {
        "ProvisioningArtifactId": NotRequired[str],
        "ProvisioningParameters": NotRequired[Sequence[ProvisioningParameterTypeDef]],
    },
)
PublicWorkforceTaskPriceTypeDef = TypedDict(
    "PublicWorkforceTaskPriceTypeDef",
    {
        "AmountInUsd": NotRequired[USDTypeDef],
    },
)
QueryLineageResponseTypeDef = TypedDict(
    "QueryLineageResponseTypeDef",
    {
        "Vertices": List[VertexTypeDef],
        "Edges": List[EdgeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
RecommendationJobOutputConfigTypeDef = TypedDict(
    "RecommendationJobOutputConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
        "CompiledOutputConfig": NotRequired[RecommendationJobCompiledOutputConfigTypeDef],
    },
)
RecommendationJobContainerConfigOutputTypeDef = TypedDict(
    "RecommendationJobContainerConfigOutputTypeDef",
    {
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "Framework": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
        "PayloadConfig": NotRequired[RecommendationJobPayloadConfigOutputTypeDef],
        "NearestModelName": NotRequired[str],
        "SupportedInstanceTypes": NotRequired[List[str]],
        "SupportedEndpointType": NotRequired[RecommendationJobSupportedEndpointTypeType],
        "DataInputConfig": NotRequired[str],
        "SupportedResponseMIMETypes": NotRequired[List[str]],
    },
)
RecommendationJobContainerConfigTypeDef = TypedDict(
    "RecommendationJobContainerConfigTypeDef",
    {
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "Framework": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
        "PayloadConfig": NotRequired[RecommendationJobPayloadConfigTypeDef],
        "NearestModelName": NotRequired[str],
        "SupportedInstanceTypes": NotRequired[Sequence[str]],
        "SupportedEndpointType": NotRequired[RecommendationJobSupportedEndpointTypeType],
        "DataInputConfig": NotRequired[str],
        "SupportedResponseMIMETypes": NotRequired[Sequence[str]],
    },
)
RenderUiTemplateRequestRequestTypeDef = TypedDict(
    "RenderUiTemplateRequestRequestTypeDef",
    {
        "Task": RenderableTaskTypeDef,
        "RoleArn": str,
        "UiTemplate": NotRequired[UiTemplateTypeDef],
        "HumanTaskUiArn": NotRequired[str],
    },
)
RenderUiTemplateResponseTypeDef = TypedDict(
    "RenderUiTemplateResponseTypeDef",
    {
        "RenderedContent": str,
        "Errors": List[RenderingErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchRequestRequestTypeDef = TypedDict(
    "SearchRequestRequestTypeDef",
    {
        "Resource": ResourceTypeType,
        "SearchExpression": NotRequired["SearchExpressionTypeDef"],
        "SortBy": NotRequired[str],
        "SortOrder": NotRequired[SearchSortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CrossAccountFilterOption": NotRequired[CrossAccountFilterOptionType],
        "VisibilityConditions": NotRequired[Sequence[VisibilityConditionsTypeDef]],
    },
)
SelectiveExecutionConfigExtraOutputTypeDef = TypedDict(
    "SelectiveExecutionConfigExtraOutputTypeDef",
    {
        "SelectedSteps": List[SelectedStepTypeDef],
        "SourcePipelineExecutionArn": NotRequired[str],
    },
)
SelectiveExecutionConfigOutputTypeDef = TypedDict(
    "SelectiveExecutionConfigOutputTypeDef",
    {
        "SelectedSteps": List[SelectedStepTypeDef],
        "SourcePipelineExecutionArn": NotRequired[str],
    },
)
SelectiveExecutionConfigTypeDef = TypedDict(
    "SelectiveExecutionConfigTypeDef",
    {
        "SelectedSteps": Sequence[SelectedStepTypeDef],
        "SourcePipelineExecutionArn": NotRequired[str],
    },
)
ShadowModeConfigOutputTypeDef = TypedDict(
    "ShadowModeConfigOutputTypeDef",
    {
        "SourceModelVariantName": str,
        "ShadowModelVariants": List[ShadowModelVariantConfigTypeDef],
    },
)
ShadowModeConfigTypeDef = TypedDict(
    "ShadowModeConfigTypeDef",
    {
        "SourceModelVariantName": str,
        "ShadowModelVariants": Sequence[ShadowModelVariantConfigTypeDef],
    },
)
SourceIpConfigUnionTypeDef = Union[SourceIpConfigTypeDef, SourceIpConfigExtraOutputTypeDef]
TrafficPatternOutputTypeDef = TypedDict(
    "TrafficPatternOutputTypeDef",
    {
        "TrafficType": NotRequired[TrafficTypeType],
        "Phases": NotRequired[List[PhaseTypeDef]],
        "Stairs": NotRequired[StairsTypeDef],
    },
)
TrafficPatternTypeDef = TypedDict(
    "TrafficPatternTypeDef",
    {
        "TrafficType": NotRequired[TrafficTypeType],
        "Phases": NotRequired[Sequence[PhaseTypeDef]],
        "Stairs": NotRequired[StairsTypeDef],
    },
)
TrainingImageConfigTypeDef = TypedDict(
    "TrainingImageConfigTypeDef",
    {
        "TrainingRepositoryAccessMode": TrainingRepositoryAccessModeType,
        "TrainingRepositoryAuthConfig": NotRequired[TrainingRepositoryAuthConfigTypeDef],
    },
)
TransformDataSourceTypeDef = TypedDict(
    "TransformDataSourceTypeDef",
    {
        "S3DataSource": TransformS3DataSourceTypeDef,
    },
)
WorkforceTypeDef = TypedDict(
    "WorkforceTypeDef",
    {
        "WorkforceName": str,
        "WorkforceArn": str,
        "LastUpdatedDate": NotRequired[datetime],
        "SourceIpConfig": NotRequired[SourceIpConfigOutputTypeDef],
        "SubDomain": NotRequired[str],
        "CognitoConfig": NotRequired[CognitoConfigTypeDef],
        "OidcConfig": NotRequired[OidcConfigForResponseTypeDef],
        "CreateDate": NotRequired[datetime],
        "WorkforceVpcConfig": NotRequired[WorkforceVpcConfigResponseTypeDef],
        "Status": NotRequired[WorkforceStatusType],
        "FailureReason": NotRequired[str],
    },
)
ListActionsResponseTypeDef = TypedDict(
    "ListActionsResponseTypeDef",
    {
        "ActionSummaries": List[ActionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListAppsResponseTypeDef = TypedDict(
    "ListAppsResponseTypeDef",
    {
        "Apps": List[AppDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DomainSettingsForUpdateTypeDef = TypedDict(
    "DomainSettingsForUpdateTypeDef",
    {
        "RStudioServerProDomainSettingsForUpdate": NotRequired[
            RStudioServerProDomainSettingsForUpdateTypeDef
        ],
        "ExecutionRoleIdentityConfig": NotRequired[ExecutionRoleIdentityConfigType],
        "SecurityGroupIds": NotRequired[Sequence[str]],
        "DockerSettings": NotRequired[DockerSettingsTypeDef],
        "AmazonQSettings": NotRequired[AmazonQSettingsTypeDef],
    },
)
DomainSettingsOutputTypeDef = TypedDict(
    "DomainSettingsOutputTypeDef",
    {
        "SecurityGroupIds": NotRequired[List[str]],
        "RStudioServerProDomainSettings": NotRequired[RStudioServerProDomainSettingsTypeDef],
        "ExecutionRoleIdentityConfig": NotRequired[ExecutionRoleIdentityConfigType],
        "DockerSettings": NotRequired[DockerSettingsOutputTypeDef],
        "AmazonQSettings": NotRequired[AmazonQSettingsTypeDef],
    },
)
DomainSettingsTypeDef = TypedDict(
    "DomainSettingsTypeDef",
    {
        "SecurityGroupIds": NotRequired[Sequence[str]],
        "RStudioServerProDomainSettings": NotRequired[RStudioServerProDomainSettingsTypeDef],
        "ExecutionRoleIdentityConfig": NotRequired[ExecutionRoleIdentityConfigType],
        "DockerSettings": NotRequired[DockerSettingsTypeDef],
        "AmazonQSettings": NotRequired[AmazonQSettingsTypeDef],
    },
)
ArtifactSummaryTypeDef = TypedDict(
    "ArtifactSummaryTypeDef",
    {
        "ArtifactArn": NotRequired[str],
        "ArtifactName": NotRequired[str],
        "Source": NotRequired[ArtifactSourceOutputTypeDef],
        "ArtifactType": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)
ArtifactSourceUnionTypeDef = Union[ArtifactSourceTypeDef, ArtifactSourceExtraOutputTypeDef]
CreateArtifactRequestRequestTypeDef = TypedDict(
    "CreateArtifactRequestRequestTypeDef",
    {
        "Source": ArtifactSourceTypeDef,
        "ArtifactType": str,
        "ArtifactName": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DeleteArtifactRequestRequestTypeDef = TypedDict(
    "DeleteArtifactRequestRequestTypeDef",
    {
        "ArtifactArn": NotRequired[str],
        "Source": NotRequired[ArtifactSourceTypeDef],
    },
)
AsyncInferenceConfigOutputTypeDef = TypedDict(
    "AsyncInferenceConfigOutputTypeDef",
    {
        "OutputConfig": AsyncInferenceOutputConfigOutputTypeDef,
        "ClientConfig": NotRequired[AsyncInferenceClientConfigTypeDef],
    },
)
AsyncInferenceConfigTypeDef = TypedDict(
    "AsyncInferenceConfigTypeDef",
    {
        "OutputConfig": AsyncInferenceOutputConfigTypeDef,
        "ClientConfig": NotRequired[AsyncInferenceClientConfigTypeDef],
    },
)
TabularJobConfigOutputTypeDef = TypedDict(
    "TabularJobConfigOutputTypeDef",
    {
        "TargetAttributeName": str,
        "CandidateGenerationConfig": NotRequired[CandidateGenerationConfigOutputTypeDef],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "FeatureSpecificationS3Uri": NotRequired[str],
        "Mode": NotRequired[AutoMLModeType],
        "GenerateCandidateDefinitionsOnly": NotRequired[bool],
        "ProblemType": NotRequired[ProblemTypeType],
        "SampleWeightAttributeName": NotRequired[str],
    },
)
TimeSeriesForecastingJobConfigOutputTypeDef = TypedDict(
    "TimeSeriesForecastingJobConfigOutputTypeDef",
    {
        "ForecastFrequency": str,
        "ForecastHorizon": int,
        "TimeSeriesConfig": TimeSeriesConfigOutputTypeDef,
        "FeatureSpecificationS3Uri": NotRequired[str],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "ForecastQuantiles": NotRequired[List[str]],
        "Transformations": NotRequired[TimeSeriesTransformationsOutputTypeDef],
        "HolidayConfig": NotRequired[List[HolidayConfigAttributesTypeDef]],
        "CandidateGenerationConfig": NotRequired[CandidateGenerationConfigOutputTypeDef],
    },
)
TabularJobConfigTypeDef = TypedDict(
    "TabularJobConfigTypeDef",
    {
        "TargetAttributeName": str,
        "CandidateGenerationConfig": NotRequired[CandidateGenerationConfigTypeDef],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "FeatureSpecificationS3Uri": NotRequired[str],
        "Mode": NotRequired[AutoMLModeType],
        "GenerateCandidateDefinitionsOnly": NotRequired[bool],
        "ProblemType": NotRequired[ProblemTypeType],
        "SampleWeightAttributeName": NotRequired[str],
    },
)
TimeSeriesForecastingJobConfigTypeDef = TypedDict(
    "TimeSeriesForecastingJobConfigTypeDef",
    {
        "ForecastFrequency": str,
        "ForecastHorizon": int,
        "TimeSeriesConfig": TimeSeriesConfigTypeDef,
        "FeatureSpecificationS3Uri": NotRequired[str],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "ForecastQuantiles": NotRequired[Sequence[str]],
        "Transformations": NotRequired[TimeSeriesTransformationsTypeDef],
        "HolidayConfig": NotRequired[Sequence[HolidayConfigAttributesTypeDef]],
        "CandidateGenerationConfig": NotRequired[CandidateGenerationConfigTypeDef],
    },
)
AutoMLChannelTypeDef = TypedDict(
    "AutoMLChannelTypeDef",
    {
        "TargetAttributeName": str,
        "DataSource": NotRequired[AutoMLDataSourceTypeDef],
        "CompressionType": NotRequired[CompressionTypeType],
        "ContentType": NotRequired[str],
        "ChannelType": NotRequired[AutoMLChannelTypeType],
        "SampleWeightAttributeName": NotRequired[str],
    },
)
AutoMLJobChannelTypeDef = TypedDict(
    "AutoMLJobChannelTypeDef",
    {
        "ChannelType": NotRequired[AutoMLChannelTypeType],
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "DataSource": NotRequired[AutoMLDataSourceTypeDef],
    },
)
ListAutoMLJobsResponseTypeDef = TypedDict(
    "ListAutoMLJobsResponseTypeDef",
    {
        "AutoMLJobSummaries": List[AutoMLJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
AutoMLResolvedAttributesTypeDef = TypedDict(
    "AutoMLResolvedAttributesTypeDef",
    {
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "AutoMLProblemTypeResolvedAttributes": NotRequired[
            AutoMLProblemTypeResolvedAttributesTypeDef
        ],
    },
)
AutoMLJobConfigOutputTypeDef = TypedDict(
    "AutoMLJobConfigOutputTypeDef",
    {
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "SecurityConfig": NotRequired[AutoMLSecurityConfigOutputTypeDef],
        "CandidateGenerationConfig": NotRequired[AutoMLCandidateGenerationConfigOutputTypeDef],
        "DataSplitConfig": NotRequired[AutoMLDataSplitConfigTypeDef],
        "Mode": NotRequired[AutoMLModeType],
    },
)
LabelingJobAlgorithmsConfigOutputTypeDef = TypedDict(
    "LabelingJobAlgorithmsConfigOutputTypeDef",
    {
        "LabelingJobAlgorithmSpecificationArn": str,
        "InitialActiveLearningModelArn": NotRequired[str],
        "LabelingJobResourceConfig": NotRequired[LabelingJobResourceConfigOutputTypeDef],
    },
)
AutoMLJobConfigTypeDef = TypedDict(
    "AutoMLJobConfigTypeDef",
    {
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "SecurityConfig": NotRequired[AutoMLSecurityConfigTypeDef],
        "CandidateGenerationConfig": NotRequired[AutoMLCandidateGenerationConfigTypeDef],
        "DataSplitConfig": NotRequired[AutoMLDataSplitConfigTypeDef],
        "Mode": NotRequired[AutoMLModeType],
    },
)
AutoMLSecurityConfigUnionTypeDef = Union[
    AutoMLSecurityConfigTypeDef, AutoMLSecurityConfigOutputTypeDef
]
LabelingJobAlgorithmsConfigTypeDef = TypedDict(
    "LabelingJobAlgorithmsConfigTypeDef",
    {
        "LabelingJobAlgorithmSpecificationArn": str,
        "InitialActiveLearningModelArn": NotRequired[str],
        "LabelingJobResourceConfig": NotRequired[LabelingJobResourceConfigTypeDef],
    },
)
MonitoringNetworkConfigUnionTypeDef = Union[
    MonitoringNetworkConfigTypeDef, MonitoringNetworkConfigOutputTypeDef
]
ModelMetricsTypeDef = TypedDict(
    "ModelMetricsTypeDef",
    {
        "ModelQuality": NotRequired[ModelQualityTypeDef],
        "ModelDataQuality": NotRequired[ModelDataQualityTypeDef],
        "Bias": NotRequired[BiasTypeDef],
        "Explainability": NotRequired[ExplainabilityTypeDef],
    },
)
PipelineExecutionStepMetadataTypeDef = TypedDict(
    "PipelineExecutionStepMetadataTypeDef",
    {
        "TrainingJob": NotRequired[TrainingJobStepMetadataTypeDef],
        "ProcessingJob": NotRequired[ProcessingJobStepMetadataTypeDef],
        "TransformJob": NotRequired[TransformJobStepMetadataTypeDef],
        "TuningJob": NotRequired[TuningJobStepMetaDataTypeDef],
        "Model": NotRequired[ModelStepMetadataTypeDef],
        "RegisterModel": NotRequired[RegisterModelStepMetadataTypeDef],
        "Condition": NotRequired[ConditionStepMetadataTypeDef],
        "Callback": NotRequired[CallbackStepMetadataTypeDef],
        "Lambda": NotRequired[LambdaStepMetadataTypeDef],
        "EMR": NotRequired[EMRStepMetadataTypeDef],
        "QualityCheck": NotRequired[QualityCheckStepMetadataTypeDef],
        "ClarifyCheck": NotRequired[ClarifyCheckStepMetadataTypeDef],
        "Fail": NotRequired[FailStepMetadataTypeDef],
        "AutoMLJob": NotRequired[AutoMLJobStepMetadataTypeDef],
    },
)
AutoMLCandidateTypeDef = TypedDict(
    "AutoMLCandidateTypeDef",
    {
        "CandidateName": str,
        "ObjectiveStatus": ObjectiveStatusType,
        "CandidateSteps": List[AutoMLCandidateStepTypeDef],
        "CandidateStatus": CandidateStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "FinalAutoMLJobObjectiveMetric": NotRequired[FinalAutoMLJobObjectiveMetricTypeDef],
        "InferenceContainers": NotRequired[List[AutoMLContainerDefinitionTypeDef]],
        "EndTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "CandidateProperties": NotRequired[CandidatePropertiesTypeDef],
        "InferenceContainerDefinitions": NotRequired[
            Dict[AutoMLProcessingUnitType, List[AutoMLContainerDefinitionTypeDef]]
        ],
    },
)
BlueGreenUpdatePolicyTypeDef = TypedDict(
    "BlueGreenUpdatePolicyTypeDef",
    {
        "TrafficRoutingConfiguration": TrafficRoutingConfigTypeDef,
        "TerminationWaitInSeconds": NotRequired[int],
        "MaximumExecutionTimeoutInSeconds": NotRequired[int],
    },
)
InferenceExperimentDataStorageConfigUnionTypeDef = Union[
    InferenceExperimentDataStorageConfigTypeDef, InferenceExperimentDataStorageConfigOutputTypeDef
]
DataCaptureConfigUnionTypeDef = Union[DataCaptureConfigTypeDef, DataCaptureConfigOutputTypeDef]
EndpointInputConfigurationOutputTypeDef = TypedDict(
    "EndpointInputConfigurationOutputTypeDef",
    {
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "ServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "InferenceSpecificationName": NotRequired[str],
        "EnvironmentParameterRanges": NotRequired[EnvironmentParameterRangesOutputTypeDef],
    },
)
EndpointInputConfigurationTypeDef = TypedDict(
    "EndpointInputConfigurationTypeDef",
    {
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "ServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "InferenceSpecificationName": NotRequired[str],
        "EnvironmentParameterRanges": NotRequired[EnvironmentParameterRangesTypeDef],
    },
)
ClarifyExplainerConfigOutputTypeDef = TypedDict(
    "ClarifyExplainerConfigOutputTypeDef",
    {
        "ShapConfig": ClarifyShapConfigTypeDef,
        "EnableExplanations": NotRequired[str],
        "InferenceConfig": NotRequired[ClarifyInferenceConfigOutputTypeDef],
    },
)
ClarifyExplainerConfigTypeDef = TypedDict(
    "ClarifyExplainerConfigTypeDef",
    {
        "ShapConfig": ClarifyShapConfigTypeDef,
        "EnableExplanations": NotRequired[str],
        "InferenceConfig": NotRequired[ClarifyInferenceConfigTypeDef],
    },
)
ClusterInstanceGroupDetailsTypeDef = TypedDict(
    "ClusterInstanceGroupDetailsTypeDef",
    {
        "CurrentCount": NotRequired[int],
        "TargetCount": NotRequired[int],
        "InstanceGroupName": NotRequired[str],
        "InstanceType": NotRequired[ClusterInstanceTypeType],
        "LifeCycleConfig": NotRequired[ClusterLifeCycleConfigTypeDef],
        "ExecutionRole": NotRequired[str],
        "ThreadsPerCore": NotRequired[int],
        "InstanceStorageConfigs": NotRequired[List[ClusterInstanceStorageConfigTypeDef]],
    },
)
ClusterInstanceGroupSpecificationTypeDef = TypedDict(
    "ClusterInstanceGroupSpecificationTypeDef",
    {
        "InstanceCount": int,
        "InstanceGroupName": str,
        "InstanceType": ClusterInstanceTypeType,
        "LifeCycleConfig": ClusterLifeCycleConfigTypeDef,
        "ExecutionRole": str,
        "ThreadsPerCore": NotRequired[int],
        "InstanceStorageConfigs": NotRequired[Sequence[ClusterInstanceStorageConfigTypeDef]],
    },
)
ClusterNodeDetailsTypeDef = TypedDict(
    "ClusterNodeDetailsTypeDef",
    {
        "InstanceGroupName": NotRequired[str],
        "InstanceId": NotRequired[str],
        "InstanceStatus": NotRequired[ClusterInstanceStatusDetailsTypeDef],
        "InstanceType": NotRequired[ClusterInstanceTypeType],
        "LaunchTime": NotRequired[datetime],
        "LifeCycleConfig": NotRequired[ClusterLifeCycleConfigTypeDef],
        "ThreadsPerCore": NotRequired[int],
        "InstanceStorageConfigs": NotRequired[List[ClusterInstanceStorageConfigTypeDef]],
        "PrivatePrimaryIp": NotRequired[str],
        "PrivateDnsHostname": NotRequired[str],
        "Placement": NotRequired[ClusterInstancePlacementTypeDef],
    },
)
ListClusterNodesResponseTypeDef = TypedDict(
    "ListClusterNodesResponseTypeDef",
    {
        "NextToken": str,
        "ClusterNodeSummaries": List[ClusterNodeSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CodeEditorAppImageConfigUnionTypeDef = Union[
    CodeEditorAppImageConfigTypeDef, CodeEditorAppImageConfigExtraOutputTypeDef
]
JupyterLabAppImageConfigUnionTypeDef = Union[
    JupyterLabAppImageConfigTypeDef, JupyterLabAppImageConfigExtraOutputTypeDef
]
ListCodeRepositoriesOutputTypeDef = TypedDict(
    "ListCodeRepositoriesOutputTypeDef",
    {
        "CodeRepositorySummaryList": List[CodeRepositorySummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
FeatureDefinitionTypeDef = TypedDict(
    "FeatureDefinitionTypeDef",
    {
        "FeatureName": str,
        "FeatureType": FeatureTypeType,
        "CollectionType": NotRequired[CollectionTypeType],
        "CollectionConfig": NotRequired[CollectionConfigTypeDef],
    },
)
DebugHookConfigUnionTypeDef = Union[DebugHookConfigTypeDef, DebugHookConfigExtraOutputTypeDef]
ListContextsResponseTypeDef = TypedDict(
    "ListContextsResponseTypeDef",
    {
        "ContextSummaries": List[ContextSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
InferenceExperimentScheduleUnionTypeDef = Union[
    InferenceExperimentScheduleTypeDef, InferenceExperimentScheduleExtraOutputTypeDef
]
QueryLineageRequestRequestTypeDef = TypedDict(
    "QueryLineageRequestRequestTypeDef",
    {
        "StartArns": NotRequired[Sequence[str]],
        "Direction": NotRequired[DirectionType],
        "IncludeEdges": NotRequired[bool],
        "Filters": NotRequired[QueryFiltersTypeDef],
        "MaxDepth": NotRequired[int],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ChannelExtraOutputTypeDef = TypedDict(
    "ChannelExtraOutputTypeDef",
    {
        "ChannelName": str,
        "DataSource": DataSourceExtraOutputTypeDef,
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "RecordWrapperType": NotRequired[RecordWrapperType],
        "InputMode": NotRequired[TrainingInputModeType],
        "ShuffleConfig": NotRequired[ShuffleConfigTypeDef],
    },
)
ChannelOutputTypeDef = TypedDict(
    "ChannelOutputTypeDef",
    {
        "ChannelName": str,
        "DataSource": DataSourceOutputTypeDef,
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "RecordWrapperType": NotRequired[RecordWrapperType],
        "InputMode": NotRequired[TrainingInputModeType],
        "ShuffleConfig": NotRequired[ShuffleConfigTypeDef],
    },
)
ChannelTypeDef = TypedDict(
    "ChannelTypeDef",
    {
        "ChannelName": str,
        "DataSource": DataSourceTypeDef,
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "RecordWrapperType": NotRequired[RecordWrapperType],
        "InputMode": NotRequired[TrainingInputModeType],
        "ShuffleConfig": NotRequired[ShuffleConfigTypeDef],
    },
)
ProcessingInputTypeDef = TypedDict(
    "ProcessingInputTypeDef",
    {
        "InputName": str,
        "AppManaged": NotRequired[bool],
        "S3Input": NotRequired[ProcessingS3InputTypeDef],
        "DatasetDefinition": NotRequired[DatasetDefinitionTypeDef],
    },
)
DefaultSpaceSettingsOutputTypeDef = TypedDict(
    "DefaultSpaceSettingsOutputTypeDef",
    {
        "ExecutionRole": NotRequired[str],
        "SecurityGroups": NotRequired[List[str]],
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsOutputTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsOutputTypeDef],
        "JupyterLabAppSettings": NotRequired[JupyterLabAppSettingsOutputTypeDef],
        "SpaceStorageSettings": NotRequired[DefaultSpaceStorageSettingsTypeDef],
        "CustomPosixUserConfig": NotRequired[CustomPosixUserConfigTypeDef],
        "CustomFileSystemConfigs": NotRequired[List[CustomFileSystemConfigTypeDef]],
    },
)
DefaultSpaceSettingsTypeDef = TypedDict(
    "DefaultSpaceSettingsTypeDef",
    {
        "ExecutionRole": NotRequired[str],
        "SecurityGroups": NotRequired[Sequence[str]],
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsTypeDef],
        "JupyterLabAppSettings": NotRequired[JupyterLabAppSettingsTypeDef],
        "SpaceStorageSettings": NotRequired[DefaultSpaceStorageSettingsTypeDef],
        "CustomPosixUserConfig": NotRequired[CustomPosixUserConfigTypeDef],
        "CustomFileSystemConfigs": NotRequired[Sequence[CustomFileSystemConfigTypeDef]],
    },
)
UserSettingsOutputTypeDef = TypedDict(
    "UserSettingsOutputTypeDef",
    {
        "ExecutionRole": NotRequired[str],
        "SecurityGroups": NotRequired[List[str]],
        "SharingSettings": NotRequired[SharingSettingsTypeDef],
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsOutputTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsOutputTypeDef],
        "TensorBoardAppSettings": NotRequired[TensorBoardAppSettingsTypeDef],
        "RStudioServerProAppSettings": NotRequired[RStudioServerProAppSettingsTypeDef],
        "RSessionAppSettings": NotRequired[RSessionAppSettingsOutputTypeDef],
        "CanvasAppSettings": NotRequired[CanvasAppSettingsOutputTypeDef],
        "CodeEditorAppSettings": NotRequired[CodeEditorAppSettingsOutputTypeDef],
        "JupyterLabAppSettings": NotRequired[JupyterLabAppSettingsOutputTypeDef],
        "SpaceStorageSettings": NotRequired[DefaultSpaceStorageSettingsTypeDef],
        "DefaultLandingUri": NotRequired[str],
        "StudioWebPortal": NotRequired[StudioWebPortalType],
        "CustomPosixUserConfig": NotRequired[CustomPosixUserConfigTypeDef],
        "CustomFileSystemConfigs": NotRequired[List[CustomFileSystemConfigTypeDef]],
        "StudioWebPortalSettings": NotRequired[StudioWebPortalSettingsOutputTypeDef],
    },
)
UserSettingsTypeDef = TypedDict(
    "UserSettingsTypeDef",
    {
        "ExecutionRole": NotRequired[str],
        "SecurityGroups": NotRequired[Sequence[str]],
        "SharingSettings": NotRequired[SharingSettingsTypeDef],
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsTypeDef],
        "TensorBoardAppSettings": NotRequired[TensorBoardAppSettingsTypeDef],
        "RStudioServerProAppSettings": NotRequired[RStudioServerProAppSettingsTypeDef],
        "RSessionAppSettings": NotRequired[RSessionAppSettingsTypeDef],
        "CanvasAppSettings": NotRequired[CanvasAppSettingsTypeDef],
        "CodeEditorAppSettings": NotRequired[CodeEditorAppSettingsTypeDef],
        "JupyterLabAppSettings": NotRequired[JupyterLabAppSettingsTypeDef],
        "SpaceStorageSettings": NotRequired[DefaultSpaceStorageSettingsTypeDef],
        "DefaultLandingUri": NotRequired[str],
        "StudioWebPortal": NotRequired[StudioWebPortalType],
        "CustomPosixUserConfig": NotRequired[CustomPosixUserConfigTypeDef],
        "CustomFileSystemConfigs": NotRequired[Sequence[CustomFileSystemConfigTypeDef]],
        "StudioWebPortalSettings": NotRequired[StudioWebPortalSettingsTypeDef],
    },
)
InferenceComponentSpecificationSummaryTypeDef = TypedDict(
    "InferenceComponentSpecificationSummaryTypeDef",
    {
        "ModelName": NotRequired[str],
        "Container": NotRequired[InferenceComponentContainerSpecificationSummaryTypeDef],
        "StartupParameters": NotRequired[InferenceComponentStartupParametersTypeDef],
        "ComputeResourceRequirements": NotRequired[
            InferenceComponentComputeResourceRequirementsTypeDef
        ],
    },
)
DescribeEdgeDeploymentPlanResponseTypeDef = TypedDict(
    "DescribeEdgeDeploymentPlanResponseTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "EdgeDeploymentPlanName": str,
        "ModelConfigs": List[EdgeDeploymentModelConfigTypeDef],
        "DeviceFleetName": str,
        "EdgeDeploymentSuccess": int,
        "EdgeDeploymentPending": int,
        "EdgeDeploymentFailed": int,
        "Stages": List[DeploymentStageStatusSummaryTypeDef],
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
CreateEdgeDeploymentPlanRequestRequestTypeDef = TypedDict(
    "CreateEdgeDeploymentPlanRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "ModelConfigs": Sequence[EdgeDeploymentModelConfigTypeDef],
        "DeviceFleetName": str,
        "Stages": NotRequired[Sequence[DeploymentStageTypeDef]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "CreateEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "Stages": Sequence[DeploymentStageTypeDef],
    },
)
ListExperimentsResponseTypeDef = TypedDict(
    "ListExperimentsResponseTypeDef",
    {
        "ExperimentSummaries": List[ExperimentSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListFeatureGroupsResponseTypeDef = TypedDict(
    "ListFeatureGroupsResponseTypeDef",
    {
        "FeatureGroupSummaries": List[FeatureGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListInferenceExperimentsResponseTypeDef = TypedDict(
    "ListInferenceExperimentsResponseTypeDef",
    {
        "InferenceExperiments": List[InferenceExperimentSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListTrainingJobsResponseTypeDef = TypedDict(
    "ListTrainingJobsResponseTypeDef",
    {
        "TrainingJobSummaries": List[TrainingJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListTrialsResponseTypeDef = TypedDict(
    "ListTrialsResponseTypeDef",
    {
        "TrialSummaries": List[TrialSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateEndpointWeightsAndCapacitiesInputRequestTypeDef = TypedDict(
    "UpdateEndpointWeightsAndCapacitiesInputRequestTypeDef",
    {
        "EndpointName": str,
        "DesiredWeightsAndCapacities": Sequence[DesiredWeightAndCapacityTypeDef],
    },
)
ListDevicesResponseTypeDef = TypedDict(
    "ListDevicesResponseTypeDef",
    {
        "DeviceSummaries": List[DeviceSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DriftCheckBaselinesTypeDef = TypedDict(
    "DriftCheckBaselinesTypeDef",
    {
        "Bias": NotRequired[DriftCheckBiasTypeDef],
        "Explainability": NotRequired[DriftCheckExplainabilityTypeDef],
        "ModelQuality": NotRequired[DriftCheckModelQualityTypeDef],
        "ModelDataQuality": NotRequired[DriftCheckModelDataQualityTypeDef],
    },
)
SpaceSettingsOutputTypeDef = TypedDict(
    "SpaceSettingsOutputTypeDef",
    {
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsOutputTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsOutputTypeDef],
        "CodeEditorAppSettings": NotRequired[SpaceCodeEditorAppSettingsTypeDef],
        "JupyterLabAppSettings": NotRequired[SpaceJupyterLabAppSettingsOutputTypeDef],
        "AppType": NotRequired[AppTypeType],
        "SpaceStorageSettings": NotRequired[SpaceStorageSettingsTypeDef],
        "CustomFileSystems": NotRequired[List[CustomFileSystemTypeDef]],
    },
)
SpaceSettingsSummaryTypeDef = TypedDict(
    "SpaceSettingsSummaryTypeDef",
    {
        "AppType": NotRequired[AppTypeType],
        "SpaceStorageSettings": NotRequired[SpaceStorageSettingsTypeDef],
    },
)
SpaceSettingsTypeDef = TypedDict(
    "SpaceSettingsTypeDef",
    {
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsTypeDef],
        "CodeEditorAppSettings": NotRequired[SpaceCodeEditorAppSettingsTypeDef],
        "JupyterLabAppSettings": NotRequired[SpaceJupyterLabAppSettingsTypeDef],
        "AppType": NotRequired[AppTypeType],
        "SpaceStorageSettings": NotRequired[SpaceStorageSettingsTypeDef],
        "CustomFileSystems": NotRequired[Sequence[CustomFileSystemTypeDef]],
    },
)
InferenceRecommendationTypeDef = TypedDict(
    "InferenceRecommendationTypeDef",
    {
        "EndpointConfiguration": EndpointOutputConfigurationTypeDef,
        "ModelConfiguration": ModelConfigurationTypeDef,
        "RecommendationId": NotRequired[str],
        "Metrics": NotRequired[RecommendationMetricsTypeDef],
        "InvocationEndTime": NotRequired[datetime],
        "InvocationStartTime": NotRequired[datetime],
    },
)
RecommendationJobInferenceBenchmarkTypeDef = TypedDict(
    "RecommendationJobInferenceBenchmarkTypeDef",
    {
        "ModelConfiguration": ModelConfigurationTypeDef,
        "Metrics": NotRequired[RecommendationMetricsTypeDef],
        "EndpointMetrics": NotRequired[InferenceMetricsTypeDef],
        "EndpointConfiguration": NotRequired[EndpointOutputConfigurationTypeDef],
        "FailureReason": NotRequired[str],
        "InvocationEndTime": NotRequired[datetime],
        "InvocationStartTime": NotRequired[datetime],
    },
)
SearchExpressionTypeDef = TypedDict(
    "SearchExpressionTypeDef",
    {
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "NestedFilters": NotRequired[Sequence[NestedFiltersTypeDef]],
        "SubExpressions": NotRequired[Sequence[Dict[str, Any]]],
        "Operator": NotRequired[BooleanOperatorType],
    },
)
ListTrainingJobsForHyperParameterTuningJobResponseTypeDef = TypedDict(
    "ListTrainingJobsForHyperParameterTuningJobResponseTypeDef",
    {
        "TrainingJobSummaries": List[HyperParameterTrainingJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
NetworkConfigUnionTypeDef = Union[NetworkConfigTypeDef, NetworkConfigExtraOutputTypeDef]
ListHyperParameterTuningJobsResponseTypeDef = TypedDict(
    "ListHyperParameterTuningJobsResponseTypeDef",
    {
        "HyperParameterTuningJobSummaries": List[HyperParameterTuningJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
HyperParameterTuningJobWarmStartConfigUnionTypeDef = Union[
    HyperParameterTuningJobWarmStartConfigTypeDef,
    HyperParameterTuningJobWarmStartConfigExtraOutputTypeDef,
]
AssociationSummaryTypeDef = TypedDict(
    "AssociationSummaryTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "SourceType": NotRequired[str],
        "DestinationType": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
        "SourceName": NotRequired[str],
        "DestinationName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
    },
)
DescribeActionResponseTypeDef = TypedDict(
    "DescribeActionResponseTypeDef",
    {
        "ActionName": str,
        "ActionArn": str,
        "Source": ActionSourceTypeDef,
        "ActionType": str,
        "Description": str,
        "Status": ActionStatusType,
        "Properties": Dict[str, str],
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "LineageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeArtifactResponseTypeDef = TypedDict(
    "DescribeArtifactResponseTypeDef",
    {
        "ArtifactName": str,
        "ArtifactArn": str,
        "Source": ArtifactSourceOutputTypeDef,
        "ArtifactType": str,
        "Properties": Dict[str, str],
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "LineageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeContextResponseTypeDef = TypedDict(
    "DescribeContextResponseTypeDef",
    {
        "ContextName": str,
        "ContextArn": str,
        "Source": ContextSourceTypeDef,
        "ContextType": str,
        "Description": str,
        "Properties": Dict[str, str],
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "LineageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeExperimentResponseTypeDef = TypedDict(
    "DescribeExperimentResponseTypeDef",
    {
        "ExperimentName": str,
        "ExperimentArn": str,
        "DisplayName": str,
        "Source": ExperimentSourceTypeDef,
        "Description": str,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLineageGroupResponseTypeDef = TypedDict(
    "DescribeLineageGroupResponseTypeDef",
    {
        "LineageGroupName": str,
        "LineageGroupArn": str,
        "DisplayName": str,
        "Description": str,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeMlflowTrackingServerResponseTypeDef = TypedDict(
    "DescribeMlflowTrackingServerResponseTypeDef",
    {
        "TrackingServerArn": str,
        "TrackingServerName": str,
        "ArtifactStoreUri": str,
        "TrackingServerSize": TrackingServerSizeType,
        "MlflowVersion": str,
        "RoleArn": str,
        "TrackingServerStatus": TrackingServerStatusType,
        "IsActive": IsTrackingServerActiveType,
        "TrackingServerUrl": str,
        "WeeklyMaintenanceWindowStart": str,
        "AutomaticModelRegistration": bool,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeModelCardResponseTypeDef = TypedDict(
    "DescribeModelCardResponseTypeDef",
    {
        "ModelCardArn": str,
        "ModelCardName": str,
        "ModelCardVersion": int,
        "Content": str,
        "ModelCardStatus": ModelCardStatusType,
        "SecurityConfig": ModelCardSecurityConfigTypeDef,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ModelCardProcessingStatus": ModelCardProcessingStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeModelPackageGroupOutputTypeDef = TypedDict(
    "DescribeModelPackageGroupOutputTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageGroupArn": str,
        "ModelPackageGroupDescription": str,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "ModelPackageGroupStatus": ModelPackageGroupStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribePipelineResponseTypeDef = TypedDict(
    "DescribePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "PipelineName": str,
        "PipelineDisplayName": str,
        "PipelineDefinition": str,
        "PipelineDescription": str,
        "RoleArn": str,
        "PipelineStatus": PipelineStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastRunTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedBy": UserContextTypeDef,
        "ParallelismConfiguration": ParallelismConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeTrialComponentResponseTypeDef = TypedDict(
    "DescribeTrialComponentResponseTypeDef",
    {
        "TrialComponentName": str,
        "TrialComponentArn": str,
        "DisplayName": str,
        "Source": TrialComponentSourceTypeDef,
        "Status": TrialComponentStatusTypeDef,
        "StartTime": datetime,
        "EndTime": datetime,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "Parameters": Dict[str, TrialComponentParameterValueTypeDef],
        "InputArtifacts": Dict[str, TrialComponentArtifactTypeDef],
        "OutputArtifacts": Dict[str, TrialComponentArtifactTypeDef],
        "MetadataProperties": MetadataPropertiesTypeDef,
        "Metrics": List[TrialComponentMetricSummaryTypeDef],
        "LineageGroupArn": str,
        "Sources": List[TrialComponentSourceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeTrialResponseTypeDef = TypedDict(
    "DescribeTrialResponseTypeDef",
    {
        "TrialName": str,
        "TrialArn": str,
        "DisplayName": str,
        "ExperimentName": str,
        "Source": TrialSourceTypeDef,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ExperimentTypeDef = TypedDict(
    "ExperimentTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "ExperimentArn": NotRequired[str],
        "DisplayName": NotRequired[str],
        "Source": NotRequired[ExperimentSourceTypeDef],
        "Description": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
ModelCardTypeDef = TypedDict(
    "ModelCardTypeDef",
    {
        "ModelCardArn": NotRequired[str],
        "ModelCardName": NotRequired[str],
        "ModelCardVersion": NotRequired[int],
        "Content": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SecurityConfig": NotRequired[ModelCardSecurityConfigTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "ModelId": NotRequired[str],
        "RiskRating": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
    },
)
ModelDashboardModelCardTypeDef = TypedDict(
    "ModelDashboardModelCardTypeDef",
    {
        "ModelCardArn": NotRequired[str],
        "ModelCardName": NotRequired[str],
        "ModelCardVersion": NotRequired[int],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SecurityConfig": NotRequired[ModelCardSecurityConfigTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "ModelId": NotRequired[str],
        "RiskRating": NotRequired[str],
    },
)
ModelPackageGroupTypeDef = TypedDict(
    "ModelPackageGroupTypeDef",
    {
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageGroupArn": NotRequired[str],
        "ModelPackageGroupDescription": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "ModelPackageGroupStatus": NotRequired[ModelPackageGroupStatusType],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
PipelineTypeDef = TypedDict(
    "PipelineTypeDef",
    {
        "PipelineArn": NotRequired[str],
        "PipelineName": NotRequired[str],
        "PipelineDisplayName": NotRequired[str],
        "PipelineDescription": NotRequired[str],
        "RoleArn": NotRequired[str],
        "PipelineStatus": NotRequired[PipelineStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "LastRunTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
TrialComponentSimpleSummaryTypeDef = TypedDict(
    "TrialComponentSimpleSummaryTypeDef",
    {
        "TrialComponentName": NotRequired[str],
        "TrialComponentArn": NotRequired[str],
        "TrialComponentSource": NotRequired[TrialComponentSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
    },
)
TrialComponentSummaryTypeDef = TypedDict(
    "TrialComponentSummaryTypeDef",
    {
        "TrialComponentName": NotRequired[str],
        "TrialComponentArn": NotRequired[str],
        "DisplayName": NotRequired[str],
        "TrialComponentSource": NotRequired[TrialComponentSourceTypeDef],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
    },
)
WorkerAccessConfigurationTypeDef = TypedDict(
    "WorkerAccessConfigurationTypeDef",
    {
        "S3Presign": NotRequired[S3PresignTypeDef],
    },
)
CreateInferenceComponentInputRequestTypeDef = TypedDict(
    "CreateInferenceComponentInputRequestTypeDef",
    {
        "InferenceComponentName": str,
        "EndpointName": str,
        "VariantName": str,
        "Specification": InferenceComponentSpecificationTypeDef,
        "RuntimeConfig": InferenceComponentRuntimeConfigTypeDef,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateInferenceComponentInputRequestTypeDef = TypedDict(
    "UpdateInferenceComponentInputRequestTypeDef",
    {
        "InferenceComponentName": str,
        "Specification": NotRequired[InferenceComponentSpecificationTypeDef],
        "RuntimeConfig": NotRequired[InferenceComponentRuntimeConfigTypeDef],
    },
)
ResourceConfigUnionTypeDef = Union[ResourceConfigTypeDef, ResourceConfigExtraOutputTypeDef]
HyperParameterSpecificationOutputTypeDef = TypedDict(
    "HyperParameterSpecificationOutputTypeDef",
    {
        "Name": str,
        "Type": ParameterTypeType,
        "Description": NotRequired[str],
        "Range": NotRequired[ParameterRangeOutputTypeDef],
        "IsTunable": NotRequired[bool],
        "IsRequired": NotRequired[bool],
        "DefaultValue": NotRequired[str],
    },
)
HyperParameterSpecificationTypeDef = TypedDict(
    "HyperParameterSpecificationTypeDef",
    {
        "Name": str,
        "Type": ParameterTypeType,
        "Description": NotRequired[str],
        "Range": NotRequired[ParameterRangeTypeDef],
        "IsTunable": NotRequired[bool],
        "IsRequired": NotRequired[bool],
        "DefaultValue": NotRequired[str],
    },
)
HyperParameterTuningJobConfigExtraOutputTypeDef = TypedDict(
    "HyperParameterTuningJobConfigExtraOutputTypeDef",
    {
        "Strategy": HyperParameterTuningJobStrategyTypeType,
        "ResourceLimits": ResourceLimitsTypeDef,
        "StrategyConfig": NotRequired[HyperParameterTuningJobStrategyConfigTypeDef],
        "HyperParameterTuningJobObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "ParameterRanges": NotRequired[ParameterRangesExtraOutputTypeDef],
        "TrainingJobEarlyStoppingType": NotRequired[TrainingJobEarlyStoppingTypeType],
        "TuningJobCompletionCriteria": NotRequired[TuningJobCompletionCriteriaTypeDef],
        "RandomSeed": NotRequired[int],
    },
)
HyperParameterTuningJobConfigOutputTypeDef = TypedDict(
    "HyperParameterTuningJobConfigOutputTypeDef",
    {
        "Strategy": HyperParameterTuningJobStrategyTypeType,
        "ResourceLimits": ResourceLimitsTypeDef,
        "StrategyConfig": NotRequired[HyperParameterTuningJobStrategyConfigTypeDef],
        "HyperParameterTuningJobObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "ParameterRanges": NotRequired[ParameterRangesOutputTypeDef],
        "TrainingJobEarlyStoppingType": NotRequired[TrainingJobEarlyStoppingTypeType],
        "TuningJobCompletionCriteria": NotRequired[TuningJobCompletionCriteriaTypeDef],
        "RandomSeed": NotRequired[int],
    },
)
HyperParameterTuningJobConfigTypeDef = TypedDict(
    "HyperParameterTuningJobConfigTypeDef",
    {
        "Strategy": HyperParameterTuningJobStrategyTypeType,
        "ResourceLimits": ResourceLimitsTypeDef,
        "StrategyConfig": NotRequired[HyperParameterTuningJobStrategyConfigTypeDef],
        "HyperParameterTuningJobObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "ParameterRanges": NotRequired[ParameterRangesTypeDef],
        "TrainingJobEarlyStoppingType": NotRequired[TrainingJobEarlyStoppingTypeType],
        "TuningJobCompletionCriteria": NotRequired[TuningJobCompletionCriteriaTypeDef],
        "RandomSeed": NotRequired[int],
    },
)
AppImageConfigDetailsTypeDef = TypedDict(
    "AppImageConfigDetailsTypeDef",
    {
        "AppImageConfigArn": NotRequired[str],
        "AppImageConfigName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "KernelGatewayImageConfig": NotRequired[KernelGatewayImageConfigOutputTypeDef],
        "JupyterLabAppImageConfig": NotRequired[JupyterLabAppImageConfigOutputTypeDef],
        "CodeEditorAppImageConfig": NotRequired[CodeEditorAppImageConfigOutputTypeDef],
    },
)
DescribeAppImageConfigResponseTypeDef = TypedDict(
    "DescribeAppImageConfigResponseTypeDef",
    {
        "AppImageConfigArn": str,
        "AppImageConfigName": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "KernelGatewayImageConfig": KernelGatewayImageConfigOutputTypeDef,
        "JupyterLabAppImageConfig": JupyterLabAppImageConfigOutputTypeDef,
        "CodeEditorAppImageConfig": CodeEditorAppImageConfigOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAppImageConfigRequestRequestTypeDef = TypedDict(
    "CreateAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "KernelGatewayImageConfig": NotRequired[KernelGatewayImageConfigTypeDef],
        "JupyterLabAppImageConfig": NotRequired[JupyterLabAppImageConfigTypeDef],
        "CodeEditorAppImageConfig": NotRequired[CodeEditorAppImageConfigTypeDef],
    },
)
KernelGatewayImageConfigUnionTypeDef = Union[
    KernelGatewayImageConfigTypeDef, KernelGatewayImageConfigExtraOutputTypeDef
]
UpdateAppImageConfigRequestRequestTypeDef = TypedDict(
    "UpdateAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
        "KernelGatewayImageConfig": NotRequired[KernelGatewayImageConfigTypeDef],
        "JupyterLabAppImageConfig": NotRequired[JupyterLabAppImageConfigTypeDef],
        "CodeEditorAppImageConfig": NotRequired[CodeEditorAppImageConfigTypeDef],
    },
)
ListLabelingJobsForWorkteamResponseTypeDef = TypedDict(
    "ListLabelingJobsForWorkteamResponseTypeDef",
    {
        "LabelingJobSummaryList": List[LabelingJobForWorkteamSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
LabelingJobInputConfigExtraOutputTypeDef = TypedDict(
    "LabelingJobInputConfigExtraOutputTypeDef",
    {
        "DataSource": LabelingJobDataSourceTypeDef,
        "DataAttributes": NotRequired[LabelingJobDataAttributesExtraOutputTypeDef],
    },
)
LabelingJobInputConfigOutputTypeDef = TypedDict(
    "LabelingJobInputConfigOutputTypeDef",
    {
        "DataSource": LabelingJobDataSourceTypeDef,
        "DataAttributes": NotRequired[LabelingJobDataAttributesOutputTypeDef],
    },
)
LabelingJobInputConfigTypeDef = TypedDict(
    "LabelingJobInputConfigTypeDef",
    {
        "DataSource": LabelingJobDataSourceTypeDef,
        "DataAttributes": NotRequired[LabelingJobDataAttributesTypeDef],
    },
)
MemberDefinitionUnionTypeDef = Union[MemberDefinitionTypeDef, MemberDefinitionExtraOutputTypeDef]
TargetTrackingScalingPolicyConfigurationTypeDef = TypedDict(
    "TargetTrackingScalingPolicyConfigurationTypeDef",
    {
        "MetricSpecification": NotRequired[MetricSpecificationTypeDef],
        "TargetValue": NotRequired[float],
    },
)
AdditionalModelDataSourceTypeDef = TypedDict(
    "AdditionalModelDataSourceTypeDef",
    {
        "ChannelName": str,
        "S3DataSource": S3ModelDataSourceTypeDef,
    },
)
ModelDataSourceTypeDef = TypedDict(
    "ModelDataSourceTypeDef",
    {
        "S3DataSource": NotRequired[S3ModelDataSourceTypeDef],
    },
)
MonitoringAlertSummaryTypeDef = TypedDict(
    "MonitoringAlertSummaryTypeDef",
    {
        "MonitoringAlertName": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "AlertStatus": MonitoringAlertStatusType,
        "DatapointsToAlert": int,
        "EvaluationPeriod": int,
        "Actions": MonitoringAlertActionsTypeDef,
    },
)
ModelVariantConfigSummaryTypeDef = TypedDict(
    "ModelVariantConfigSummaryTypeDef",
    {
        "ModelName": str,
        "VariantName": str,
        "InfrastructureConfig": ModelInfrastructureConfigTypeDef,
        "Status": ModelVariantStatusType,
    },
)
ModelVariantConfigTypeDef = TypedDict(
    "ModelVariantConfigTypeDef",
    {
        "ModelName": str,
        "VariantName": str,
        "InfrastructureConfig": ModelInfrastructureConfigTypeDef,
    },
)
RecommendationJobStoppingConditionsUnionTypeDef = Union[
    RecommendationJobStoppingConditionsTypeDef, RecommendationJobStoppingConditionsOutputTypeDef
]
ListModelMetadataRequestListModelMetadataPaginateTypeDef = TypedDict(
    "ListModelMetadataRequestListModelMetadataPaginateTypeDef",
    {
        "SearchExpression": NotRequired[ModelMetadataSearchExpressionTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListModelMetadataRequestRequestTypeDef = TypedDict(
    "ListModelMetadataRequestRequestTypeDef",
    {
        "SearchExpression": NotRequired[ModelMetadataSearchExpressionTypeDef],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
OptimizationConfigUnionTypeDef = Union[OptimizationConfigTypeDef, OptimizationConfigOutputTypeDef]
BatchTransformInputExtraOutputTypeDef = TypedDict(
    "BatchTransformInputExtraOutputTypeDef",
    {
        "DataCapturedDestinationS3Uri": str,
        "DatasetFormat": MonitoringDatasetFormatExtraOutputTypeDef,
        "LocalPath": str,
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "FeaturesAttribute": NotRequired[str],
        "InferenceAttribute": NotRequired[str],
        "ProbabilityAttribute": NotRequired[str],
        "ProbabilityThresholdAttribute": NotRequired[float],
        "StartTimeOffset": NotRequired[str],
        "EndTimeOffset": NotRequired[str],
        "ExcludeFeaturesAttribute": NotRequired[str],
    },
)
BatchTransformInputOutputTypeDef = TypedDict(
    "BatchTransformInputOutputTypeDef",
    {
        "DataCapturedDestinationS3Uri": str,
        "DatasetFormat": MonitoringDatasetFormatOutputTypeDef,
        "LocalPath": str,
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "FeaturesAttribute": NotRequired[str],
        "InferenceAttribute": NotRequired[str],
        "ProbabilityAttribute": NotRequired[str],
        "ProbabilityThresholdAttribute": NotRequired[float],
        "StartTimeOffset": NotRequired[str],
        "EndTimeOffset": NotRequired[str],
        "ExcludeFeaturesAttribute": NotRequired[str],
    },
)
BatchTransformInputTypeDef = TypedDict(
    "BatchTransformInputTypeDef",
    {
        "DataCapturedDestinationS3Uri": str,
        "DatasetFormat": MonitoringDatasetFormatTypeDef,
        "LocalPath": str,
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "FeaturesAttribute": NotRequired[str],
        "InferenceAttribute": NotRequired[str],
        "ProbabilityAttribute": NotRequired[str],
        "ProbabilityThresholdAttribute": NotRequired[float],
        "StartTimeOffset": NotRequired[str],
        "EndTimeOffset": NotRequired[str],
        "ExcludeFeaturesAttribute": NotRequired[str],
    },
)
MonitoringOutputConfigExtraOutputTypeDef = TypedDict(
    "MonitoringOutputConfigExtraOutputTypeDef",
    {
        "MonitoringOutputs": List[MonitoringOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)
MonitoringOutputConfigOutputTypeDef = TypedDict(
    "MonitoringOutputConfigOutputTypeDef",
    {
        "MonitoringOutputs": List[MonitoringOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)
MonitoringOutputConfigTypeDef = TypedDict(
    "MonitoringOutputConfigTypeDef",
    {
        "MonitoringOutputs": Sequence[MonitoringOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)
OptimizationJobModelSourceTypeDef = TypedDict(
    "OptimizationJobModelSourceTypeDef",
    {
        "S3": NotRequired[OptimizationJobModelSourceS3TypeDef],
    },
)
CreateCompilationJobRequestRequestTypeDef = TypedDict(
    "CreateCompilationJobRequestRequestTypeDef",
    {
        "CompilationJobName": str,
        "RoleArn": str,
        "OutputConfig": OutputConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "ModelPackageVersionArn": NotRequired[str],
        "InputConfig": NotRequired[InputConfigTypeDef],
        "VpcConfig": NotRequired[NeoVpcConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeCompilationJobResponseTypeDef = TypedDict(
    "DescribeCompilationJobResponseTypeDef",
    {
        "CompilationJobName": str,
        "CompilationJobArn": str,
        "CompilationJobStatus": CompilationJobStatusType,
        "CompilationStartTime": datetime,
        "CompilationEndTime": datetime,
        "StoppingCondition": StoppingConditionTypeDef,
        "InferenceImage": str,
        "ModelPackageVersionArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "ModelArtifacts": ModelArtifactsTypeDef,
        "ModelDigests": ModelDigestsTypeDef,
        "RoleArn": str,
        "InputConfig": InputConfigTypeDef,
        "OutputConfig": OutputConfigTypeDef,
        "VpcConfig": NeoVpcConfigOutputTypeDef,
        "DerivedInformation": DerivedInformationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PendingDeploymentSummaryTypeDef = TypedDict(
    "PendingDeploymentSummaryTypeDef",
    {
        "EndpointConfigName": str,
        "ProductionVariants": NotRequired[List[PendingProductionVariantSummaryTypeDef]],
        "StartTime": NotRequired[datetime],
        "ShadowProductionVariants": NotRequired[List[PendingProductionVariantSummaryTypeDef]],
    },
)
ProcessingOutputConfigExtraOutputTypeDef = TypedDict(
    "ProcessingOutputConfigExtraOutputTypeDef",
    {
        "Outputs": List[ProcessingOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)
ProcessingOutputConfigOutputTypeDef = TypedDict(
    "ProcessingOutputConfigOutputTypeDef",
    {
        "Outputs": List[ProcessingOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)
ProcessingOutputConfigTypeDef = TypedDict(
    "ProcessingOutputConfigTypeDef",
    {
        "Outputs": Sequence[ProcessingOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)
UpdateTrainingJobRequestRequestTypeDef = TypedDict(
    "UpdateTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
        "ProfilerConfig": NotRequired[ProfilerConfigForUpdateTypeDef],
        "ProfilerRuleConfigurations": NotRequired[Sequence[ProfilerRuleConfigurationUnionTypeDef]],
        "ResourceConfig": NotRequired[ResourceConfigForUpdateTypeDef],
        "RemoteDebugConfig": NotRequired[RemoteDebugConfigForUpdateTypeDef],
    },
)
GetSearchSuggestionsRequestRequestTypeDef = TypedDict(
    "GetSearchSuggestionsRequestRequestTypeDef",
    {
        "Resource": ResourceTypeType,
        "SuggestionQuery": NotRequired[SuggestionQueryTypeDef],
    },
)
DescribeProjectOutputTypeDef = TypedDict(
    "DescribeProjectOutputTypeDef",
    {
        "ProjectArn": str,
        "ProjectName": str,
        "ProjectId": str,
        "ProjectDescription": str,
        "ServiceCatalogProvisioningDetails": ServiceCatalogProvisioningDetailsOutputTypeDef,
        "ServiceCatalogProvisionedProductDetails": ServiceCatalogProvisionedProductDetailsTypeDef,
        "ProjectStatus": ProjectStatusType,
        "CreatedBy": UserContextTypeDef,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ProjectTypeDef = TypedDict(
    "ProjectTypeDef",
    {
        "ProjectArn": NotRequired[str],
        "ProjectName": NotRequired[str],
        "ProjectId": NotRequired[str],
        "ProjectDescription": NotRequired[str],
        "ServiceCatalogProvisioningDetails": NotRequired[
            ServiceCatalogProvisioningDetailsOutputTypeDef
        ],
        "ServiceCatalogProvisionedProductDetails": NotRequired[
            ServiceCatalogProvisionedProductDetailsTypeDef
        ],
        "ProjectStatus": NotRequired[ProjectStatusType],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "CreationTime": NotRequired[datetime],
        "Tags": NotRequired[List[TagTypeDef]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
    },
)
CreateProjectInputRequestTypeDef = TypedDict(
    "CreateProjectInputRequestTypeDef",
    {
        "ProjectName": str,
        "ServiceCatalogProvisioningDetails": ServiceCatalogProvisioningDetailsTypeDef,
        "ProjectDescription": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ServiceCatalogProvisioningDetailsUnionTypeDef = Union[
    ServiceCatalogProvisioningDetailsTypeDef, ServiceCatalogProvisioningDetailsExtraOutputTypeDef
]
UpdateProjectInputRequestTypeDef = TypedDict(
    "UpdateProjectInputRequestTypeDef",
    {
        "ProjectName": str,
        "ProjectDescription": NotRequired[str],
        "ServiceCatalogProvisioningUpdateDetails": NotRequired[
            ServiceCatalogProvisioningUpdateDetailsTypeDef
        ],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
HumanLoopConfigOutputTypeDef = TypedDict(
    "HumanLoopConfigOutputTypeDef",
    {
        "WorkteamArn": str,
        "HumanTaskUiArn": str,
        "TaskTitle": str,
        "TaskDescription": str,
        "TaskCount": int,
        "TaskAvailabilityLifetimeInSeconds": NotRequired[int],
        "TaskTimeLimitInSeconds": NotRequired[int],
        "TaskKeywords": NotRequired[List[str]],
        "PublicWorkforceTaskPrice": NotRequired[PublicWorkforceTaskPriceTypeDef],
    },
)
HumanLoopConfigTypeDef = TypedDict(
    "HumanLoopConfigTypeDef",
    {
        "WorkteamArn": str,
        "HumanTaskUiArn": str,
        "TaskTitle": str,
        "TaskDescription": str,
        "TaskCount": int,
        "TaskAvailabilityLifetimeInSeconds": NotRequired[int],
        "TaskTimeLimitInSeconds": NotRequired[int],
        "TaskKeywords": NotRequired[Sequence[str]],
        "PublicWorkforceTaskPrice": NotRequired[PublicWorkforceTaskPriceTypeDef],
    },
)
HumanTaskConfigOutputTypeDef = TypedDict(
    "HumanTaskConfigOutputTypeDef",
    {
        "WorkteamArn": str,
        "UiConfig": UiConfigTypeDef,
        "PreHumanTaskLambdaArn": str,
        "TaskTitle": str,
        "TaskDescription": str,
        "NumberOfHumanWorkersPerDataObject": int,
        "TaskTimeLimitInSeconds": int,
        "AnnotationConsolidationConfig": AnnotationConsolidationConfigTypeDef,
        "TaskKeywords": NotRequired[List[str]],
        "TaskAvailabilityLifetimeInSeconds": NotRequired[int],
        "MaxConcurrentTaskCount": NotRequired[int],
        "PublicWorkforceTaskPrice": NotRequired[PublicWorkforceTaskPriceTypeDef],
    },
)
HumanTaskConfigTypeDef = TypedDict(
    "HumanTaskConfigTypeDef",
    {
        "WorkteamArn": str,
        "UiConfig": UiConfigTypeDef,
        "PreHumanTaskLambdaArn": str,
        "TaskTitle": str,
        "TaskDescription": str,
        "NumberOfHumanWorkersPerDataObject": int,
        "TaskTimeLimitInSeconds": int,
        "AnnotationConsolidationConfig": AnnotationConsolidationConfigTypeDef,
        "TaskKeywords": NotRequired[Sequence[str]],
        "TaskAvailabilityLifetimeInSeconds": NotRequired[int],
        "MaxConcurrentTaskCount": NotRequired[int],
        "PublicWorkforceTaskPrice": NotRequired[PublicWorkforceTaskPriceTypeDef],
    },
)
DescribePipelineExecutionResponseTypeDef = TypedDict(
    "DescribePipelineExecutionResponseTypeDef",
    {
        "PipelineArn": str,
        "PipelineExecutionArn": str,
        "PipelineExecutionDisplayName": str,
        "PipelineExecutionStatus": PipelineExecutionStatusType,
        "PipelineExecutionDescription": str,
        "PipelineExperimentConfig": PipelineExperimentConfigTypeDef,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedBy": UserContextTypeDef,
        "ParallelismConfiguration": ParallelismConfigurationTypeDef,
        "SelectiveExecutionConfig": SelectiveExecutionConfigOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PipelineExecutionTypeDef = TypedDict(
    "PipelineExecutionTypeDef",
    {
        "PipelineArn": NotRequired[str],
        "PipelineExecutionArn": NotRequired[str],
        "PipelineExecutionDisplayName": NotRequired[str],
        "PipelineExecutionStatus": NotRequired[PipelineExecutionStatusType],
        "PipelineExecutionDescription": NotRequired[str],
        "PipelineExperimentConfig": NotRequired[PipelineExperimentConfigTypeDef],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
        "SelectiveExecutionConfig": NotRequired[SelectiveExecutionConfigOutputTypeDef],
        "PipelineParameters": NotRequired[List[ParameterTypeDef]],
    },
)
SelectiveExecutionConfigUnionTypeDef = Union[
    SelectiveExecutionConfigTypeDef, SelectiveExecutionConfigExtraOutputTypeDef
]
StartPipelineExecutionRequestRequestTypeDef = TypedDict(
    "StartPipelineExecutionRequestRequestTypeDef",
    {
        "PipelineName": str,
        "ClientRequestToken": str,
        "PipelineExecutionDisplayName": NotRequired[str],
        "PipelineParameters": NotRequired[Sequence[ParameterTypeDef]],
        "PipelineExecutionDescription": NotRequired[str],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
        "SelectiveExecutionConfig": NotRequired[SelectiveExecutionConfigTypeDef],
    },
)
ShadowModeConfigUnionTypeDef = Union[ShadowModeConfigTypeDef, ShadowModeConfigOutputTypeDef]
AlgorithmSpecificationExtraOutputTypeDef = TypedDict(
    "AlgorithmSpecificationExtraOutputTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[List[MetricDefinitionTypeDef]],
        "EnableSageMakerMetricsTimeSeries": NotRequired[bool],
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "TrainingImageConfig": NotRequired[TrainingImageConfigTypeDef],
    },
)
AlgorithmSpecificationOutputTypeDef = TypedDict(
    "AlgorithmSpecificationOutputTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[List[MetricDefinitionTypeDef]],
        "EnableSageMakerMetricsTimeSeries": NotRequired[bool],
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "TrainingImageConfig": NotRequired[TrainingImageConfigTypeDef],
    },
)
AlgorithmSpecificationTypeDef = TypedDict(
    "AlgorithmSpecificationTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[Sequence[MetricDefinitionTypeDef]],
        "EnableSageMakerMetricsTimeSeries": NotRequired[bool],
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "TrainingImageConfig": NotRequired[TrainingImageConfigTypeDef],
    },
)
TransformInputTypeDef = TypedDict(
    "TransformInputTypeDef",
    {
        "DataSource": TransformDataSourceTypeDef,
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "SplitType": NotRequired[SplitTypeType],
    },
)
DescribeWorkforceResponseTypeDef = TypedDict(
    "DescribeWorkforceResponseTypeDef",
    {
        "Workforce": WorkforceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListWorkforcesResponseTypeDef = TypedDict(
    "ListWorkforcesResponseTypeDef",
    {
        "Workforces": List[WorkforceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateWorkforceResponseTypeDef = TypedDict(
    "UpdateWorkforceResponseTypeDef",
    {
        "Workforce": WorkforceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DomainSettingsUnionTypeDef = Union[DomainSettingsTypeDef, DomainSettingsOutputTypeDef]
ListArtifactsResponseTypeDef = TypedDict(
    "ListArtifactsResponseTypeDef",
    {
        "ArtifactSummaries": List[ArtifactSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
AsyncInferenceConfigUnionTypeDef = Union[
    AsyncInferenceConfigTypeDef, AsyncInferenceConfigOutputTypeDef
]
AutoMLProblemTypeConfigOutputTypeDef = TypedDict(
    "AutoMLProblemTypeConfigOutputTypeDef",
    {
        "ImageClassificationJobConfig": NotRequired[ImageClassificationJobConfigTypeDef],
        "TextClassificationJobConfig": NotRequired[TextClassificationJobConfigTypeDef],
        "TimeSeriesForecastingJobConfig": NotRequired[TimeSeriesForecastingJobConfigOutputTypeDef],
        "TabularJobConfig": NotRequired[TabularJobConfigOutputTypeDef],
        "TextGenerationJobConfig": NotRequired[TextGenerationJobConfigOutputTypeDef],
    },
)
AutoMLProblemTypeConfigTypeDef = TypedDict(
    "AutoMLProblemTypeConfigTypeDef",
    {
        "ImageClassificationJobConfig": NotRequired[ImageClassificationJobConfigTypeDef],
        "TextClassificationJobConfig": NotRequired[TextClassificationJobConfigTypeDef],
        "TimeSeriesForecastingJobConfig": NotRequired[TimeSeriesForecastingJobConfigTypeDef],
        "TabularJobConfig": NotRequired[TabularJobConfigTypeDef],
        "TextGenerationJobConfig": NotRequired[TextGenerationJobConfigTypeDef],
    },
)
AutoMLJobConfigUnionTypeDef = Union[AutoMLJobConfigTypeDef, AutoMLJobConfigOutputTypeDef]
CreateAutoMLJobRequestRequestTypeDef = TypedDict(
    "CreateAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
        "InputDataConfig": Sequence[AutoMLChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "RoleArn": str,
        "ProblemType": NotRequired[ProblemTypeType],
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "AutoMLJobConfig": NotRequired[AutoMLJobConfigTypeDef],
        "GenerateCandidateDefinitionsOnly": NotRequired[bool],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ModelDeployConfig": NotRequired[ModelDeployConfigTypeDef],
    },
)
LabelingJobAlgorithmsConfigUnionTypeDef = Union[
    LabelingJobAlgorithmsConfigTypeDef, LabelingJobAlgorithmsConfigOutputTypeDef
]
PipelineExecutionStepTypeDef = TypedDict(
    "PipelineExecutionStepTypeDef",
    {
        "StepName": NotRequired[str],
        "StepDisplayName": NotRequired[str],
        "StepDescription": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "StepStatus": NotRequired[StepStatusType],
        "CacheHitResult": NotRequired[CacheHitResultTypeDef],
        "FailureReason": NotRequired[str],
        "Metadata": NotRequired[PipelineExecutionStepMetadataTypeDef],
        "AttemptCount": NotRequired[int],
        "SelectiveExecutionResult": NotRequired[SelectiveExecutionResultTypeDef],
    },
)
DescribeAutoMLJobResponseTypeDef = TypedDict(
    "DescribeAutoMLJobResponseTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobArn": str,
        "InputDataConfig": List[AutoMLChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "RoleArn": str,
        "AutoMLJobObjective": AutoMLJobObjectiveTypeDef,
        "ProblemType": ProblemTypeType,
        "AutoMLJobConfig": AutoMLJobConfigOutputTypeDef,
        "CreationTime": datetime,
        "EndTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "PartialFailureReasons": List[AutoMLPartialFailureReasonTypeDef],
        "BestCandidate": AutoMLCandidateTypeDef,
        "AutoMLJobStatus": AutoMLJobStatusType,
        "AutoMLJobSecondaryStatus": AutoMLJobSecondaryStatusType,
        "GenerateCandidateDefinitionsOnly": bool,
        "AutoMLJobArtifacts": AutoMLJobArtifactsTypeDef,
        "ResolvedAttributes": ResolvedAttributesTypeDef,
        "ModelDeployConfig": ModelDeployConfigTypeDef,
        "ModelDeployResult": ModelDeployResultTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCandidatesForAutoMLJobResponseTypeDef = TypedDict(
    "ListCandidatesForAutoMLJobResponseTypeDef",
    {
        "Candidates": List[AutoMLCandidateTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DeploymentConfigOutputTypeDef = TypedDict(
    "DeploymentConfigOutputTypeDef",
    {
        "BlueGreenUpdatePolicy": NotRequired[BlueGreenUpdatePolicyTypeDef],
        "RollingUpdatePolicy": NotRequired[RollingUpdatePolicyTypeDef],
        "AutoRollbackConfiguration": NotRequired[AutoRollbackConfigOutputTypeDef],
    },
)
DeploymentConfigTypeDef = TypedDict(
    "DeploymentConfigTypeDef",
    {
        "BlueGreenUpdatePolicy": NotRequired[BlueGreenUpdatePolicyTypeDef],
        "RollingUpdatePolicy": NotRequired[RollingUpdatePolicyTypeDef],
        "AutoRollbackConfiguration": NotRequired[AutoRollbackConfigTypeDef],
    },
)
RecommendationJobInputConfigOutputTypeDef = TypedDict(
    "RecommendationJobInputConfigOutputTypeDef",
    {
        "ModelPackageVersionArn": NotRequired[str],
        "ModelName": NotRequired[str],
        "JobDurationInSeconds": NotRequired[int],
        "TrafficPattern": NotRequired[TrafficPatternOutputTypeDef],
        "ResourceLimit": NotRequired[RecommendationJobResourceLimitTypeDef],
        "EndpointConfigurations": NotRequired[List[EndpointInputConfigurationOutputTypeDef]],
        "VolumeKmsKeyId": NotRequired[str],
        "ContainerConfig": NotRequired[RecommendationJobContainerConfigOutputTypeDef],
        "Endpoints": NotRequired[List[EndpointInfoTypeDef]],
        "VpcConfig": NotRequired[RecommendationJobVpcConfigOutputTypeDef],
    },
)
RecommendationJobInputConfigTypeDef = TypedDict(
    "RecommendationJobInputConfigTypeDef",
    {
        "ModelPackageVersionArn": NotRequired[str],
        "ModelName": NotRequired[str],
        "JobDurationInSeconds": NotRequired[int],
        "TrafficPattern": NotRequired[TrafficPatternTypeDef],
        "ResourceLimit": NotRequired[RecommendationJobResourceLimitTypeDef],
        "EndpointConfigurations": NotRequired[Sequence[EndpointInputConfigurationTypeDef]],
        "VolumeKmsKeyId": NotRequired[str],
        "ContainerConfig": NotRequired[RecommendationJobContainerConfigTypeDef],
        "Endpoints": NotRequired[Sequence[EndpointInfoTypeDef]],
        "VpcConfig": NotRequired[RecommendationJobVpcConfigTypeDef],
    },
)
ExplainerConfigOutputTypeDef = TypedDict(
    "ExplainerConfigOutputTypeDef",
    {
        "ClarifyExplainerConfig": NotRequired[ClarifyExplainerConfigOutputTypeDef],
    },
)
ExplainerConfigTypeDef = TypedDict(
    "ExplainerConfigTypeDef",
    {
        "ClarifyExplainerConfig": NotRequired[ClarifyExplainerConfigTypeDef],
    },
)
DescribeClusterResponseTypeDef = TypedDict(
    "DescribeClusterResponseTypeDef",
    {
        "ClusterArn": str,
        "ClusterName": str,
        "ClusterStatus": ClusterStatusType,
        "CreationTime": datetime,
        "FailureMessage": str,
        "InstanceGroups": List[ClusterInstanceGroupDetailsTypeDef],
        "VpcConfig": VpcConfigOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateClusterRequestRequestTypeDef = TypedDict(
    "CreateClusterRequestRequestTypeDef",
    {
        "ClusterName": str,
        "InstanceGroups": Sequence[ClusterInstanceGroupSpecificationTypeDef],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateClusterRequestRequestTypeDef = TypedDict(
    "UpdateClusterRequestRequestTypeDef",
    {
        "ClusterName": str,
        "InstanceGroups": Sequence[ClusterInstanceGroupSpecificationTypeDef],
    },
)
DescribeClusterNodeResponseTypeDef = TypedDict(
    "DescribeClusterNodeResponseTypeDef",
    {
        "NodeDetails": ClusterNodeDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateFeatureGroupRequestRequestTypeDef = TypedDict(
    "CreateFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "RecordIdentifierFeatureName": str,
        "EventTimeFeatureName": str,
        "FeatureDefinitions": Sequence[FeatureDefinitionTypeDef],
        "OnlineStoreConfig": NotRequired[OnlineStoreConfigTypeDef],
        "OfflineStoreConfig": NotRequired[OfflineStoreConfigTypeDef],
        "ThroughputConfig": NotRequired[ThroughputConfigTypeDef],
        "RoleArn": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeFeatureGroupResponseTypeDef = TypedDict(
    "DescribeFeatureGroupResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "FeatureGroupName": str,
        "RecordIdentifierFeatureName": str,
        "EventTimeFeatureName": str,
        "FeatureDefinitions": List[FeatureDefinitionTypeDef],
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "OnlineStoreConfig": OnlineStoreConfigTypeDef,
        "OfflineStoreConfig": OfflineStoreConfigTypeDef,
        "ThroughputConfig": ThroughputConfigDescriptionTypeDef,
        "RoleArn": str,
        "FeatureGroupStatus": FeatureGroupStatusType,
        "OfflineStoreStatus": OfflineStoreStatusTypeDef,
        "LastUpdateStatus": LastUpdateStatusTypeDef,
        "FailureReason": str,
        "Description": str,
        "NextToken": str,
        "OnlineStoreTotalSizeBytes": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FeatureGroupTypeDef = TypedDict(
    "FeatureGroupTypeDef",
    {
        "FeatureGroupArn": NotRequired[str],
        "FeatureGroupName": NotRequired[str],
        "RecordIdentifierFeatureName": NotRequired[str],
        "EventTimeFeatureName": NotRequired[str],
        "FeatureDefinitions": NotRequired[List[FeatureDefinitionTypeDef]],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "OnlineStoreConfig": NotRequired[OnlineStoreConfigTypeDef],
        "OfflineStoreConfig": NotRequired[OfflineStoreConfigTypeDef],
        "RoleArn": NotRequired[str],
        "FeatureGroupStatus": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatus": NotRequired[OfflineStoreStatusTypeDef],
        "LastUpdateStatus": NotRequired[LastUpdateStatusTypeDef],
        "FailureReason": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
UpdateFeatureGroupRequestRequestTypeDef = TypedDict(
    "UpdateFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureAdditions": NotRequired[Sequence[FeatureDefinitionTypeDef]],
        "OnlineStoreConfig": NotRequired[OnlineStoreConfigUpdateTypeDef],
        "ThroughputConfig": NotRequired[ThroughputConfigUpdateTypeDef],
    },
)
HyperParameterTrainingJobDefinitionExtraOutputTypeDef = TypedDict(
    "HyperParameterTrainingJobDefinitionExtraOutputTypeDef",
    {
        "AlgorithmSpecification": HyperParameterAlgorithmSpecificationExtraOutputTypeDef,
        "RoleArn": str,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "DefinitionName": NotRequired[str],
        "TuningObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "HyperParameterRanges": NotRequired[ParameterRangesExtraOutputTypeDef],
        "StaticHyperParameters": NotRequired[Dict[str, str]],
        "InputDataConfig": NotRequired[List[ChannelExtraOutputTypeDef]],
        "VpcConfig": NotRequired[VpcConfigExtraOutputTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigExtraOutputTypeDef],
        "HyperParameterTuningResourceConfig": NotRequired[
            HyperParameterTuningResourceConfigExtraOutputTypeDef
        ],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "Environment": NotRequired[Dict[str, str]],
    },
)
HyperParameterTrainingJobDefinitionOutputTypeDef = TypedDict(
    "HyperParameterTrainingJobDefinitionOutputTypeDef",
    {
        "AlgorithmSpecification": HyperParameterAlgorithmSpecificationOutputTypeDef,
        "RoleArn": str,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "DefinitionName": NotRequired[str],
        "TuningObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "HyperParameterRanges": NotRequired[ParameterRangesOutputTypeDef],
        "StaticHyperParameters": NotRequired[Dict[str, str]],
        "InputDataConfig": NotRequired[List[ChannelOutputTypeDef]],
        "VpcConfig": NotRequired[VpcConfigOutputTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigOutputTypeDef],
        "HyperParameterTuningResourceConfig": NotRequired[
            HyperParameterTuningResourceConfigOutputTypeDef
        ],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "Environment": NotRequired[Dict[str, str]],
    },
)
TrainingJobDefinitionOutputTypeDef = TypedDict(
    "TrainingJobDefinitionOutputTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "InputDataConfig": List[ChannelOutputTypeDef],
        "OutputDataConfig": OutputDataConfigTypeDef,
        "ResourceConfig": ResourceConfigOutputTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "HyperParameters": NotRequired[Dict[str, str]],
    },
)
ChannelUnionTypeDef = Union[ChannelTypeDef, ChannelExtraOutputTypeDef]
HyperParameterTrainingJobDefinitionTypeDef = TypedDict(
    "HyperParameterTrainingJobDefinitionTypeDef",
    {
        "AlgorithmSpecification": HyperParameterAlgorithmSpecificationTypeDef,
        "RoleArn": str,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "DefinitionName": NotRequired[str],
        "TuningObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "HyperParameterRanges": NotRequired[ParameterRangesTypeDef],
        "StaticHyperParameters": NotRequired[Mapping[str, str]],
        "InputDataConfig": NotRequired[Sequence[ChannelTypeDef]],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigTypeDef],
        "HyperParameterTuningResourceConfig": NotRequired[
            HyperParameterTuningResourceConfigTypeDef
        ],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "Environment": NotRequired[Mapping[str, str]],
    },
)
TrainingJobDefinitionTypeDef = TypedDict(
    "TrainingJobDefinitionTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "InputDataConfig": Sequence[ChannelTypeDef],
        "OutputDataConfig": OutputDataConfigTypeDef,
        "ResourceConfig": ResourceConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "HyperParameters": NotRequired[Mapping[str, str]],
    },
)
DefaultSpaceSettingsUnionTypeDef = Union[
    DefaultSpaceSettingsTypeDef, DefaultSpaceSettingsOutputTypeDef
]
DescribeDomainResponseTypeDef = TypedDict(
    "DescribeDomainResponseTypeDef",
    {
        "DomainArn": str,
        "DomainId": str,
        "DomainName": str,
        "HomeEfsFileSystemId": str,
        "SingleSignOnManagedApplicationInstanceId": str,
        "SingleSignOnApplicationArn": str,
        "Status": DomainStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "SecurityGroupIdForDomainBoundary": str,
        "AuthMode": AuthModeType,
        "DefaultUserSettings": UserSettingsOutputTypeDef,
        "DomainSettings": DomainSettingsOutputTypeDef,
        "AppNetworkAccessType": AppNetworkAccessTypeType,
        "HomeEfsFileSystemKmsKeyId": str,
        "SubnetIds": List[str],
        "Url": str,
        "VpcId": str,
        "KmsKeyId": str,
        "AppSecurityGroupManagement": AppSecurityGroupManagementType,
        "DefaultSpaceSettings": DefaultSpaceSettingsOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeUserProfileResponseTypeDef = TypedDict(
    "DescribeUserProfileResponseTypeDef",
    {
        "DomainId": str,
        "UserProfileArn": str,
        "UserProfileName": str,
        "HomeEfsFileSystemUid": str,
        "Status": UserProfileStatusType,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "FailureReason": str,
        "SingleSignOnUserIdentifier": str,
        "SingleSignOnUserValue": str,
        "UserSettings": UserSettingsOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDomainRequestRequestTypeDef = TypedDict(
    "CreateDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "AuthMode": AuthModeType,
        "DefaultUserSettings": UserSettingsTypeDef,
        "SubnetIds": Sequence[str],
        "VpcId": str,
        "DomainSettings": NotRequired[DomainSettingsTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "AppNetworkAccessType": NotRequired[AppNetworkAccessTypeType],
        "HomeEfsFileSystemKmsKeyId": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "AppSecurityGroupManagement": NotRequired[AppSecurityGroupManagementType],
        "DefaultSpaceSettings": NotRequired[DefaultSpaceSettingsTypeDef],
    },
)
CreateUserProfileRequestRequestTypeDef = TypedDict(
    "CreateUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
        "SingleSignOnUserIdentifier": NotRequired[str],
        "SingleSignOnUserValue": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "UserSettings": NotRequired[UserSettingsTypeDef],
    },
)
UpdateDomainRequestRequestTypeDef = TypedDict(
    "UpdateDomainRequestRequestTypeDef",
    {
        "DomainId": str,
        "DefaultUserSettings": NotRequired[UserSettingsTypeDef],
        "DomainSettingsForUpdate": NotRequired[DomainSettingsForUpdateTypeDef],
        "AppSecurityGroupManagement": NotRequired[AppSecurityGroupManagementType],
        "DefaultSpaceSettings": NotRequired[DefaultSpaceSettingsTypeDef],
        "SubnetIds": NotRequired[Sequence[str]],
        "AppNetworkAccessType": NotRequired[AppNetworkAccessTypeType],
    },
)
UpdateUserProfileRequestRequestTypeDef = TypedDict(
    "UpdateUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
        "UserSettings": NotRequired[UserSettingsTypeDef],
    },
)
UserSettingsUnionTypeDef = Union[UserSettingsTypeDef, UserSettingsOutputTypeDef]
DescribeInferenceComponentOutputTypeDef = TypedDict(
    "DescribeInferenceComponentOutputTypeDef",
    {
        "InferenceComponentName": str,
        "InferenceComponentArn": str,
        "EndpointName": str,
        "EndpointArn": str,
        "VariantName": str,
        "FailureReason": str,
        "Specification": InferenceComponentSpecificationSummaryTypeDef,
        "RuntimeConfig": InferenceComponentRuntimeConfigSummaryTypeDef,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "InferenceComponentStatus": InferenceComponentStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeSpaceResponseTypeDef = TypedDict(
    "DescribeSpaceResponseTypeDef",
    {
        "DomainId": str,
        "SpaceArn": str,
        "SpaceName": str,
        "HomeEfsFileSystemUid": str,
        "Status": SpaceStatusType,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "FailureReason": str,
        "SpaceSettings": SpaceSettingsOutputTypeDef,
        "OwnershipSettings": OwnershipSettingsTypeDef,
        "SpaceSharingSettings": SpaceSharingSettingsTypeDef,
        "SpaceDisplayName": str,
        "Url": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SpaceDetailsTypeDef = TypedDict(
    "SpaceDetailsTypeDef",
    {
        "DomainId": NotRequired[str],
        "SpaceName": NotRequired[str],
        "Status": NotRequired[SpaceStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "SpaceSettingsSummary": NotRequired[SpaceSettingsSummaryTypeDef],
        "SpaceSharingSettingsSummary": NotRequired[SpaceSharingSettingsSummaryTypeDef],
        "OwnershipSettingsSummary": NotRequired[OwnershipSettingsSummaryTypeDef],
        "SpaceDisplayName": NotRequired[str],
    },
)
CreateSpaceRequestRequestTypeDef = TypedDict(
    "CreateSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "SpaceSettings": NotRequired[SpaceSettingsTypeDef],
        "OwnershipSettings": NotRequired[OwnershipSettingsTypeDef],
        "SpaceSharingSettings": NotRequired[SpaceSharingSettingsTypeDef],
        "SpaceDisplayName": NotRequired[str],
    },
)
SpaceSettingsUnionTypeDef = Union[SpaceSettingsTypeDef, SpaceSettingsOutputTypeDef]
UpdateSpaceRequestRequestTypeDef = TypedDict(
    "UpdateSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
        "SpaceSettings": NotRequired[SpaceSettingsTypeDef],
        "SpaceDisplayName": NotRequired[str],
    },
)
InferenceRecommendationsJobStepTypeDef = TypedDict(
    "InferenceRecommendationsJobStepTypeDef",
    {
        "StepType": Literal["BENCHMARK"],
        "JobName": str,
        "Status": RecommendationJobStatusType,
        "InferenceBenchmark": NotRequired[RecommendationJobInferenceBenchmarkTypeDef],
    },
)
SearchRequestSearchPaginateTypeDef = TypedDict(
    "SearchRequestSearchPaginateTypeDef",
    {
        "Resource": ResourceTypeType,
        "SearchExpression": NotRequired[SearchExpressionTypeDef],
        "SortBy": NotRequired[str],
        "SortOrder": NotRequired[SearchSortOrderType],
        "CrossAccountFilterOption": NotRequired[CrossAccountFilterOptionType],
        "VisibilityConditions": NotRequired[Sequence[VisibilityConditionsTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAssociationsResponseTypeDef = TypedDict(
    "ListAssociationsResponseTypeDef",
    {
        "AssociationSummaries": List[AssociationSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
TrialTypeDef = TypedDict(
    "TrialTypeDef",
    {
        "TrialName": NotRequired[str],
        "TrialArn": NotRequired[str],
        "DisplayName": NotRequired[str],
        "ExperimentName": NotRequired[str],
        "Source": NotRequired[TrialSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "TrialComponentSummaries": NotRequired[List[TrialComponentSimpleSummaryTypeDef]],
    },
)
ListTrialComponentsResponseTypeDef = TypedDict(
    "ListTrialComponentsResponseTypeDef",
    {
        "TrialComponentSummaries": List[TrialComponentSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
WorkteamTypeDef = TypedDict(
    "WorkteamTypeDef",
    {
        "WorkteamName": str,
        "MemberDefinitions": List[MemberDefinitionOutputTypeDef],
        "WorkteamArn": str,
        "Description": str,
        "WorkforceArn": NotRequired[str],
        "ProductListingIds": NotRequired[List[str]],
        "SubDomain": NotRequired[str],
        "CreateDate": NotRequired[datetime],
        "LastUpdatedDate": NotRequired[datetime],
        "NotificationConfiguration": NotRequired[NotificationConfigurationTypeDef],
        "WorkerAccessConfiguration": NotRequired[WorkerAccessConfigurationTypeDef],
    },
)
TrainingSpecificationOutputTypeDef = TypedDict(
    "TrainingSpecificationOutputTypeDef",
    {
        "TrainingImage": str,
        "SupportedTrainingInstanceTypes": List[TrainingInstanceTypeType],
        "TrainingChannels": List[ChannelSpecificationOutputTypeDef],
        "TrainingImageDigest": NotRequired[str],
        "SupportedHyperParameters": NotRequired[List[HyperParameterSpecificationOutputTypeDef]],
        "SupportsDistributedTraining": NotRequired[bool],
        "MetricDefinitions": NotRequired[List[MetricDefinitionTypeDef]],
        "SupportedTuningJobObjectiveMetrics": NotRequired[
            List[HyperParameterTuningJobObjectiveTypeDef]
        ],
        "AdditionalS3DataSource": NotRequired[AdditionalS3DataSourceTypeDef],
    },
)
TrainingSpecificationTypeDef = TypedDict(
    "TrainingSpecificationTypeDef",
    {
        "TrainingImage": str,
        "SupportedTrainingInstanceTypes": Sequence[TrainingInstanceTypeType],
        "TrainingChannels": Sequence[ChannelSpecificationTypeDef],
        "TrainingImageDigest": NotRequired[str],
        "SupportedHyperParameters": NotRequired[Sequence[HyperParameterSpecificationTypeDef]],
        "SupportsDistributedTraining": NotRequired[bool],
        "MetricDefinitions": NotRequired[Sequence[MetricDefinitionTypeDef]],
        "SupportedTuningJobObjectiveMetrics": NotRequired[
            Sequence[HyperParameterTuningJobObjectiveTypeDef]
        ],
        "AdditionalS3DataSource": NotRequired[AdditionalS3DataSourceTypeDef],
    },
)
HyperParameterTuningJobConfigUnionTypeDef = Union[
    HyperParameterTuningJobConfigTypeDef, HyperParameterTuningJobConfigExtraOutputTypeDef
]
ListAppImageConfigsResponseTypeDef = TypedDict(
    "ListAppImageConfigsResponseTypeDef",
    {
        "AppImageConfigs": List[AppImageConfigDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
LabelingJobSummaryTypeDef = TypedDict(
    "LabelingJobSummaryTypeDef",
    {
        "LabelingJobName": str,
        "LabelingJobArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LabelingJobStatus": LabelingJobStatusType,
        "LabelCounters": LabelCountersTypeDef,
        "WorkteamArn": str,
        "PreHumanTaskLambdaArn": str,
        "AnnotationConsolidationLambdaArn": NotRequired[str],
        "FailureReason": NotRequired[str],
        "LabelingJobOutput": NotRequired[LabelingJobOutputTypeDef],
        "InputConfig": NotRequired[LabelingJobInputConfigOutputTypeDef],
    },
)
LabelingJobInputConfigUnionTypeDef = Union[
    LabelingJobInputConfigTypeDef, LabelingJobInputConfigExtraOutputTypeDef
]
CreateWorkteamRequestRequestTypeDef = TypedDict(
    "CreateWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
        "MemberDefinitions": Sequence[MemberDefinitionUnionTypeDef],
        "Description": str,
        "WorkforceName": NotRequired[str],
        "NotificationConfiguration": NotRequired[NotificationConfigurationTypeDef],
        "WorkerAccessConfiguration": NotRequired[WorkerAccessConfigurationTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateWorkteamRequestRequestTypeDef = TypedDict(
    "UpdateWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
        "MemberDefinitions": NotRequired[Sequence[MemberDefinitionUnionTypeDef]],
        "Description": NotRequired[str],
        "NotificationConfiguration": NotRequired[NotificationConfigurationTypeDef],
        "WorkerAccessConfiguration": NotRequired[WorkerAccessConfigurationTypeDef],
    },
)
ScalingPolicyTypeDef = TypedDict(
    "ScalingPolicyTypeDef",
    {
        "TargetTracking": NotRequired[TargetTrackingScalingPolicyConfigurationTypeDef],
    },
)
ContainerDefinitionExtraOutputTypeDef = TypedDict(
    "ContainerDefinitionExtraOutputTypeDef",
    {
        "ContainerHostname": NotRequired[str],
        "Image": NotRequired[str],
        "ImageConfig": NotRequired[ImageConfigTypeDef],
        "Mode": NotRequired[ContainerModeType],
        "ModelDataUrl": NotRequired[str],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
        "AdditionalModelDataSources": NotRequired[List[AdditionalModelDataSourceTypeDef]],
        "Environment": NotRequired[Dict[str, str]],
        "ModelPackageName": NotRequired[str],
        "InferenceSpecificationName": NotRequired[str],
        "MultiModelConfig": NotRequired[MultiModelConfigTypeDef],
    },
)
ContainerDefinitionOutputTypeDef = TypedDict(
    "ContainerDefinitionOutputTypeDef",
    {
        "ContainerHostname": NotRequired[str],
        "Image": NotRequired[str],
        "ImageConfig": NotRequired[ImageConfigTypeDef],
        "Mode": NotRequired[ContainerModeType],
        "ModelDataUrl": NotRequired[str],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
        "AdditionalModelDataSources": NotRequired[List[AdditionalModelDataSourceTypeDef]],
        "Environment": NotRequired[Dict[str, str]],
        "ModelPackageName": NotRequired[str],
        "InferenceSpecificationName": NotRequired[str],
        "MultiModelConfig": NotRequired[MultiModelConfigTypeDef],
    },
)
ContainerDefinitionTypeDef = TypedDict(
    "ContainerDefinitionTypeDef",
    {
        "ContainerHostname": NotRequired[str],
        "Image": NotRequired[str],
        "ImageConfig": NotRequired[ImageConfigTypeDef],
        "Mode": NotRequired[ContainerModeType],
        "ModelDataUrl": NotRequired[str],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
        "AdditionalModelDataSources": NotRequired[Sequence[AdditionalModelDataSourceTypeDef]],
        "Environment": NotRequired[Mapping[str, str]],
        "ModelPackageName": NotRequired[str],
        "InferenceSpecificationName": NotRequired[str],
        "MultiModelConfig": NotRequired[MultiModelConfigTypeDef],
    },
)
ModelPackageContainerDefinitionExtraOutputTypeDef = TypedDict(
    "ModelPackageContainerDefinitionExtraOutputTypeDef",
    {
        "Image": str,
        "ContainerHostname": NotRequired[str],
        "ImageDigest": NotRequired[str],
        "ModelDataUrl": NotRequired[str],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
        "ProductId": NotRequired[str],
        "Environment": NotRequired[Dict[str, str]],
        "ModelInput": NotRequired[ModelInputTypeDef],
        "Framework": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
        "NearestModelName": NotRequired[str],
        "AdditionalS3DataSource": NotRequired[AdditionalS3DataSourceTypeDef],
    },
)
ModelPackageContainerDefinitionOutputTypeDef = TypedDict(
    "ModelPackageContainerDefinitionOutputTypeDef",
    {
        "Image": str,
        "ContainerHostname": NotRequired[str],
        "ImageDigest": NotRequired[str],
        "ModelDataUrl": NotRequired[str],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
        "ProductId": NotRequired[str],
        "Environment": NotRequired[Dict[str, str]],
        "ModelInput": NotRequired[ModelInputTypeDef],
        "Framework": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
        "NearestModelName": NotRequired[str],
        "AdditionalS3DataSource": NotRequired[AdditionalS3DataSourceTypeDef],
    },
)
ModelPackageContainerDefinitionTypeDef = TypedDict(
    "ModelPackageContainerDefinitionTypeDef",
    {
        "Image": str,
        "ContainerHostname": NotRequired[str],
        "ImageDigest": NotRequired[str],
        "ModelDataUrl": NotRequired[str],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
        "ProductId": NotRequired[str],
        "Environment": NotRequired[Mapping[str, str]],
        "ModelInput": NotRequired[ModelInputTypeDef],
        "Framework": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
        "NearestModelName": NotRequired[str],
        "AdditionalS3DataSource": NotRequired[AdditionalS3DataSourceTypeDef],
    },
)
SourceAlgorithmTypeDef = TypedDict(
    "SourceAlgorithmTypeDef",
    {
        "AlgorithmName": str,
        "ModelDataUrl": NotRequired[str],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
    },
)
ListMonitoringAlertsResponseTypeDef = TypedDict(
    "ListMonitoringAlertsResponseTypeDef",
    {
        "MonitoringAlertSummaries": List[MonitoringAlertSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeInferenceExperimentResponseTypeDef = TypedDict(
    "DescribeInferenceExperimentResponseTypeDef",
    {
        "Arn": str,
        "Name": str,
        "Type": Literal["ShadowMode"],
        "Schedule": InferenceExperimentScheduleOutputTypeDef,
        "Status": InferenceExperimentStatusType,
        "StatusReason": str,
        "Description": str,
        "CreationTime": datetime,
        "CompletionTime": datetime,
        "LastModifiedTime": datetime,
        "RoleArn": str,
        "EndpointMetadata": EndpointMetadataTypeDef,
        "ModelVariants": List[ModelVariantConfigSummaryTypeDef],
        "DataStorageConfig": InferenceExperimentDataStorageConfigOutputTypeDef,
        "ShadowModeConfig": ShadowModeConfigOutputTypeDef,
        "KmsKey": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInferenceExperimentRequestRequestTypeDef = TypedDict(
    "CreateInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
        "Type": Literal["ShadowMode"],
        "RoleArn": str,
        "EndpointName": str,
        "ModelVariants": Sequence[ModelVariantConfigTypeDef],
        "ShadowModeConfig": ShadowModeConfigTypeDef,
        "Schedule": NotRequired[InferenceExperimentScheduleTypeDef],
        "Description": NotRequired[str],
        "DataStorageConfig": NotRequired[InferenceExperimentDataStorageConfigTypeDef],
        "KmsKey": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
StopInferenceExperimentRequestRequestTypeDef = TypedDict(
    "StopInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
        "ModelVariantActions": Mapping[str, ModelVariantActionType],
        "DesiredModelVariants": NotRequired[Sequence[ModelVariantConfigTypeDef]],
        "DesiredState": NotRequired[InferenceExperimentStopDesiredStateType],
        "Reason": NotRequired[str],
    },
)
UpdateInferenceExperimentRequestRequestTypeDef = TypedDict(
    "UpdateInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
        "Schedule": NotRequired[InferenceExperimentScheduleTypeDef],
        "Description": NotRequired[str],
        "ModelVariants": NotRequired[Sequence[ModelVariantConfigTypeDef]],
        "DataStorageConfig": NotRequired[InferenceExperimentDataStorageConfigTypeDef],
        "ShadowModeConfig": NotRequired[ShadowModeConfigTypeDef],
    },
)
MonitoringInputExtraOutputTypeDef = TypedDict(
    "MonitoringInputExtraOutputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputExtraOutputTypeDef],
    },
)
DataQualityJobInputOutputTypeDef = TypedDict(
    "DataQualityJobInputOutputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputOutputTypeDef],
    },
)
ModelBiasJobInputOutputTypeDef = TypedDict(
    "ModelBiasJobInputOutputTypeDef",
    {
        "GroundTruthS3Input": MonitoringGroundTruthS3InputTypeDef,
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputOutputTypeDef],
    },
)
ModelExplainabilityJobInputOutputTypeDef = TypedDict(
    "ModelExplainabilityJobInputOutputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputOutputTypeDef],
    },
)
ModelQualityJobInputOutputTypeDef = TypedDict(
    "ModelQualityJobInputOutputTypeDef",
    {
        "GroundTruthS3Input": MonitoringGroundTruthS3InputTypeDef,
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputOutputTypeDef],
    },
)
MonitoringInputOutputTypeDef = TypedDict(
    "MonitoringInputOutputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputOutputTypeDef],
    },
)
DataQualityJobInputTypeDef = TypedDict(
    "DataQualityJobInputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)
ModelBiasJobInputTypeDef = TypedDict(
    "ModelBiasJobInputTypeDef",
    {
        "GroundTruthS3Input": MonitoringGroundTruthS3InputTypeDef,
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)
ModelExplainabilityJobInputTypeDef = TypedDict(
    "ModelExplainabilityJobInputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)
ModelQualityJobInputTypeDef = TypedDict(
    "ModelQualityJobInputTypeDef",
    {
        "GroundTruthS3Input": MonitoringGroundTruthS3InputTypeDef,
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)
MonitoringInputTypeDef = TypedDict(
    "MonitoringInputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)
MonitoringOutputConfigUnionTypeDef = Union[
    MonitoringOutputConfigTypeDef, MonitoringOutputConfigExtraOutputTypeDef
]
CreateOptimizationJobRequestRequestTypeDef = TypedDict(
    "CreateOptimizationJobRequestRequestTypeDef",
    {
        "OptimizationJobName": str,
        "RoleArn": str,
        "ModelSource": OptimizationJobModelSourceTypeDef,
        "DeploymentInstanceType": OptimizationJobDeploymentInstanceTypeType,
        "OptimizationConfigs": Sequence[OptimizationConfigUnionTypeDef],
        "OutputConfig": OptimizationJobOutputConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "OptimizationEnvironment": NotRequired[Mapping[str, str]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "VpcConfig": NotRequired[OptimizationVpcConfigTypeDef],
    },
)
DescribeOptimizationJobResponseTypeDef = TypedDict(
    "DescribeOptimizationJobResponseTypeDef",
    {
        "OptimizationJobArn": str,
        "OptimizationJobStatus": OptimizationJobStatusType,
        "OptimizationStartTime": datetime,
        "OptimizationEndTime": datetime,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "OptimizationJobName": str,
        "ModelSource": OptimizationJobModelSourceTypeDef,
        "OptimizationEnvironment": Dict[str, str],
        "DeploymentInstanceType": OptimizationJobDeploymentInstanceTypeType,
        "OptimizationConfigs": List[OptimizationConfigOutputTypeDef],
        "OutputConfig": OptimizationJobOutputConfigTypeDef,
        "OptimizationOutput": OptimizationOutputTypeDef,
        "RoleArn": str,
        "StoppingCondition": StoppingConditionTypeDef,
        "VpcConfig": OptimizationVpcConfigOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeProcessingJobResponseTypeDef = TypedDict(
    "DescribeProcessingJobResponseTypeDef",
    {
        "ProcessingInputs": List[ProcessingInputTypeDef],
        "ProcessingOutputConfig": ProcessingOutputConfigOutputTypeDef,
        "ProcessingJobName": str,
        "ProcessingResources": ProcessingResourcesTypeDef,
        "StoppingCondition": ProcessingStoppingConditionTypeDef,
        "AppSpecification": AppSpecificationOutputTypeDef,
        "Environment": Dict[str, str],
        "NetworkConfig": NetworkConfigOutputTypeDef,
        "RoleArn": str,
        "ExperimentConfig": ExperimentConfigTypeDef,
        "ProcessingJobArn": str,
        "ProcessingJobStatus": ProcessingJobStatusType,
        "ExitMessage": str,
        "FailureReason": str,
        "ProcessingEndTime": datetime,
        "ProcessingStartTime": datetime,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "MonitoringScheduleArn": str,
        "AutoMLJobArn": str,
        "TrainingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ProcessingJobTypeDef = TypedDict(
    "ProcessingJobTypeDef",
    {
        "ProcessingInputs": NotRequired[List[ProcessingInputTypeDef]],
        "ProcessingOutputConfig": NotRequired[ProcessingOutputConfigOutputTypeDef],
        "ProcessingJobName": NotRequired[str],
        "ProcessingResources": NotRequired[ProcessingResourcesTypeDef],
        "StoppingCondition": NotRequired[ProcessingStoppingConditionTypeDef],
        "AppSpecification": NotRequired[AppSpecificationOutputTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigOutputTypeDef],
        "RoleArn": NotRequired[str],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "ProcessingJobArn": NotRequired[str],
        "ProcessingJobStatus": NotRequired[ProcessingJobStatusType],
        "ExitMessage": NotRequired[str],
        "FailureReason": NotRequired[str],
        "ProcessingEndTime": NotRequired[datetime],
        "ProcessingStartTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "MonitoringScheduleArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "TrainingJobArn": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
CreateProcessingJobRequestRequestTypeDef = TypedDict(
    "CreateProcessingJobRequestRequestTypeDef",
    {
        "ProcessingJobName": str,
        "ProcessingResources": ProcessingResourcesTypeDef,
        "AppSpecification": AppSpecificationTypeDef,
        "RoleArn": str,
        "ProcessingInputs": NotRequired[Sequence[ProcessingInputTypeDef]],
        "ProcessingOutputConfig": NotRequired[ProcessingOutputConfigTypeDef],
        "StoppingCondition": NotRequired[ProcessingStoppingConditionTypeDef],
        "Environment": NotRequired[Mapping[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
    },
)
ProcessingOutputConfigUnionTypeDef = Union[
    ProcessingOutputConfigTypeDef, ProcessingOutputConfigExtraOutputTypeDef
]
DescribeFlowDefinitionResponseTypeDef = TypedDict(
    "DescribeFlowDefinitionResponseTypeDef",
    {
        "FlowDefinitionArn": str,
        "FlowDefinitionName": str,
        "FlowDefinitionStatus": FlowDefinitionStatusType,
        "CreationTime": datetime,
        "HumanLoopRequestSource": HumanLoopRequestSourceTypeDef,
        "HumanLoopActivationConfig": HumanLoopActivationConfigTypeDef,
        "HumanLoopConfig": HumanLoopConfigOutputTypeDef,
        "OutputConfig": FlowDefinitionOutputConfigTypeDef,
        "RoleArn": str,
        "FailureReason": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateFlowDefinitionRequestRequestTypeDef = TypedDict(
    "CreateFlowDefinitionRequestRequestTypeDef",
    {
        "FlowDefinitionName": str,
        "OutputConfig": FlowDefinitionOutputConfigTypeDef,
        "RoleArn": str,
        "HumanLoopRequestSource": NotRequired[HumanLoopRequestSourceTypeDef],
        "HumanLoopActivationConfig": NotRequired[HumanLoopActivationConfigTypeDef],
        "HumanLoopConfig": NotRequired[HumanLoopConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
HumanLoopConfigUnionTypeDef = Union[HumanLoopConfigTypeDef, HumanLoopConfigOutputTypeDef]
DescribeLabelingJobResponseTypeDef = TypedDict(
    "DescribeLabelingJobResponseTypeDef",
    {
        "LabelingJobStatus": LabelingJobStatusType,
        "LabelCounters": LabelCountersTypeDef,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "JobReferenceCode": str,
        "LabelingJobName": str,
        "LabelingJobArn": str,
        "LabelAttributeName": str,
        "InputConfig": LabelingJobInputConfigOutputTypeDef,
        "OutputConfig": LabelingJobOutputConfigTypeDef,
        "RoleArn": str,
        "LabelCategoryConfigS3Uri": str,
        "StoppingConditions": LabelingJobStoppingConditionsTypeDef,
        "LabelingJobAlgorithmsConfig": LabelingJobAlgorithmsConfigOutputTypeDef,
        "HumanTaskConfig": HumanTaskConfigOutputTypeDef,
        "Tags": List[TagTypeDef],
        "LabelingJobOutput": LabelingJobOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLabelingJobRequestRequestTypeDef = TypedDict(
    "CreateLabelingJobRequestRequestTypeDef",
    {
        "LabelingJobName": str,
        "LabelAttributeName": str,
        "InputConfig": LabelingJobInputConfigTypeDef,
        "OutputConfig": LabelingJobOutputConfigTypeDef,
        "RoleArn": str,
        "HumanTaskConfig": HumanTaskConfigTypeDef,
        "LabelCategoryConfigS3Uri": NotRequired[str],
        "StoppingConditions": NotRequired[LabelingJobStoppingConditionsTypeDef],
        "LabelingJobAlgorithmsConfig": NotRequired[LabelingJobAlgorithmsConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
HumanTaskConfigUnionTypeDef = Union[HumanTaskConfigTypeDef, HumanTaskConfigOutputTypeDef]
DescribeTrainingJobResponseTypeDef = TypedDict(
    "DescribeTrainingJobResponseTypeDef",
    {
        "TrainingJobName": str,
        "TrainingJobArn": str,
        "TuningJobArn": str,
        "LabelingJobArn": str,
        "AutoMLJobArn": str,
        "ModelArtifacts": ModelArtifactsTypeDef,
        "TrainingJobStatus": TrainingJobStatusType,
        "SecondaryStatus": SecondaryStatusType,
        "FailureReason": str,
        "HyperParameters": Dict[str, str],
        "AlgorithmSpecification": AlgorithmSpecificationOutputTypeDef,
        "RoleArn": str,
        "InputDataConfig": List[ChannelOutputTypeDef],
        "OutputDataConfig": OutputDataConfigTypeDef,
        "ResourceConfig": ResourceConfigOutputTypeDef,
        "WarmPoolStatus": WarmPoolStatusTypeDef,
        "VpcConfig": VpcConfigOutputTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "CreationTime": datetime,
        "TrainingStartTime": datetime,
        "TrainingEndTime": datetime,
        "LastModifiedTime": datetime,
        "SecondaryStatusTransitions": List[SecondaryStatusTransitionTypeDef],
        "FinalMetricDataList": List[MetricDataTypeDef],
        "EnableNetworkIsolation": bool,
        "EnableInterContainerTrafficEncryption": bool,
        "EnableManagedSpotTraining": bool,
        "CheckpointConfig": CheckpointConfigTypeDef,
        "TrainingTimeInSeconds": int,
        "BillableTimeInSeconds": int,
        "DebugHookConfig": DebugHookConfigOutputTypeDef,
        "ExperimentConfig": ExperimentConfigTypeDef,
        "DebugRuleConfigurations": List[DebugRuleConfigurationOutputTypeDef],
        "TensorBoardOutputConfig": TensorBoardOutputConfigTypeDef,
        "DebugRuleEvaluationStatuses": List[DebugRuleEvaluationStatusTypeDef],
        "ProfilerConfig": ProfilerConfigOutputTypeDef,
        "ProfilerRuleConfigurations": List[ProfilerRuleConfigurationOutputTypeDef],
        "ProfilerRuleEvaluationStatuses": List[ProfilerRuleEvaluationStatusTypeDef],
        "ProfilingStatus": ProfilingStatusType,
        "Environment": Dict[str, str],
        "RetryStrategy": RetryStrategyTypeDef,
        "RemoteDebugConfig": RemoteDebugConfigTypeDef,
        "InfraCheckConfig": InfraCheckConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TrainingJobTypeDef = TypedDict(
    "TrainingJobTypeDef",
    {
        "TrainingJobName": NotRequired[str],
        "TrainingJobArn": NotRequired[str],
        "TuningJobArn": NotRequired[str],
        "LabelingJobArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "ModelArtifacts": NotRequired[ModelArtifactsTypeDef],
        "TrainingJobStatus": NotRequired[TrainingJobStatusType],
        "SecondaryStatus": NotRequired[SecondaryStatusType],
        "FailureReason": NotRequired[str],
        "HyperParameters": NotRequired[Dict[str, str]],
        "AlgorithmSpecification": NotRequired[AlgorithmSpecificationOutputTypeDef],
        "RoleArn": NotRequired[str],
        "InputDataConfig": NotRequired[List[ChannelOutputTypeDef]],
        "OutputDataConfig": NotRequired[OutputDataConfigTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigOutputTypeDef],
        "VpcConfig": NotRequired[VpcConfigOutputTypeDef],
        "StoppingCondition": NotRequired[StoppingConditionTypeDef],
        "CreationTime": NotRequired[datetime],
        "TrainingStartTime": NotRequired[datetime],
        "TrainingEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "SecondaryStatusTransitions": NotRequired[List[SecondaryStatusTransitionTypeDef]],
        "FinalMetricDataList": NotRequired[List[MetricDataTypeDef]],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "TrainingTimeInSeconds": NotRequired[int],
        "BillableTimeInSeconds": NotRequired[int],
        "DebugHookConfig": NotRequired[DebugHookConfigOutputTypeDef],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "DebugRuleConfigurations": NotRequired[List[DebugRuleConfigurationOutputTypeDef]],
        "TensorBoardOutputConfig": NotRequired[TensorBoardOutputConfigTypeDef],
        "DebugRuleEvaluationStatuses": NotRequired[List[DebugRuleEvaluationStatusTypeDef]],
        "ProfilerConfig": NotRequired[ProfilerConfigOutputTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
AlgorithmSpecificationUnionTypeDef = Union[
    AlgorithmSpecificationTypeDef, AlgorithmSpecificationExtraOutputTypeDef
]
CreateTransformJobRequestRequestTypeDef = TypedDict(
    "CreateTransformJobRequestRequestTypeDef",
    {
        "TransformJobName": str,
        "ModelName": str,
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "MaxConcurrentTransforms": NotRequired[int],
        "ModelClientConfig": NotRequired[ModelClientConfigTypeDef],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Mapping[str, str]],
        "DataCaptureConfig": NotRequired[BatchDataCaptureConfigTypeDef],
        "DataProcessing": NotRequired[DataProcessingTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
    },
)
DescribeTransformJobResponseTypeDef = TypedDict(
    "DescribeTransformJobResponseTypeDef",
    {
        "TransformJobName": str,
        "TransformJobArn": str,
        "TransformJobStatus": TransformJobStatusType,
        "FailureReason": str,
        "ModelName": str,
        "MaxConcurrentTransforms": int,
        "ModelClientConfig": ModelClientConfigTypeDef,
        "MaxPayloadInMB": int,
        "BatchStrategy": BatchStrategyType,
        "Environment": Dict[str, str],
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "DataCaptureConfig": BatchDataCaptureConfigTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "CreationTime": datetime,
        "TransformStartTime": datetime,
        "TransformEndTime": datetime,
        "LabelingJobArn": str,
        "AutoMLJobArn": str,
        "DataProcessing": DataProcessingTypeDef,
        "ExperimentConfig": ExperimentConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TransformJobDefinitionExtraOutputTypeDef = TypedDict(
    "TransformJobDefinitionExtraOutputTypeDef",
    {
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "MaxConcurrentTransforms": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Dict[str, str]],
    },
)
TransformJobDefinitionOutputTypeDef = TypedDict(
    "TransformJobDefinitionOutputTypeDef",
    {
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "MaxConcurrentTransforms": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Dict[str, str]],
    },
)
TransformJobDefinitionTypeDef = TypedDict(
    "TransformJobDefinitionTypeDef",
    {
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "MaxConcurrentTransforms": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Mapping[str, str]],
    },
)
TransformJobTypeDef = TypedDict(
    "TransformJobTypeDef",
    {
        "TransformJobName": NotRequired[str],
        "TransformJobArn": NotRequired[str],
        "TransformJobStatus": NotRequired[TransformJobStatusType],
        "FailureReason": NotRequired[str],
        "ModelName": NotRequired[str],
        "MaxConcurrentTransforms": NotRequired[int],
        "ModelClientConfig": NotRequired[ModelClientConfigTypeDef],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Dict[str, str]],
        "TransformInput": NotRequired[TransformInputTypeDef],
        "TransformOutput": NotRequired[TransformOutputTypeDef],
        "DataCaptureConfig": NotRequired[BatchDataCaptureConfigTypeDef],
        "TransformResources": NotRequired[TransformResourcesTypeDef],
        "CreationTime": NotRequired[datetime],
        "TransformStartTime": NotRequired[datetime],
        "TransformEndTime": NotRequired[datetime],
        "LabelingJobArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "DataProcessing": NotRequired[DataProcessingTypeDef],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
DescribeAutoMLJobV2ResponseTypeDef = TypedDict(
    "DescribeAutoMLJobV2ResponseTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobArn": str,
        "AutoMLJobInputDataConfig": List[AutoMLJobChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "RoleArn": str,
        "AutoMLJobObjective": AutoMLJobObjectiveTypeDef,
        "AutoMLProblemTypeConfig": AutoMLProblemTypeConfigOutputTypeDef,
        "AutoMLProblemTypeConfigName": AutoMLProblemTypeConfigNameType,
        "CreationTime": datetime,
        "EndTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "PartialFailureReasons": List[AutoMLPartialFailureReasonTypeDef],
        "BestCandidate": AutoMLCandidateTypeDef,
        "AutoMLJobStatus": AutoMLJobStatusType,
        "AutoMLJobSecondaryStatus": AutoMLJobSecondaryStatusType,
        "AutoMLJobArtifacts": AutoMLJobArtifactsTypeDef,
        "ResolvedAttributes": AutoMLResolvedAttributesTypeDef,
        "ModelDeployConfig": ModelDeployConfigTypeDef,
        "ModelDeployResult": ModelDeployResultTypeDef,
        "DataSplitConfig": AutoMLDataSplitConfigTypeDef,
        "SecurityConfig": AutoMLSecurityConfigOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AutoMLProblemTypeConfigUnionTypeDef = Union[
    AutoMLProblemTypeConfigTypeDef, AutoMLProblemTypeConfigOutputTypeDef
]
CreateAutoMLJobV2RequestRequestTypeDef = TypedDict(
    "CreateAutoMLJobV2RequestRequestTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobInputDataConfig": Sequence[AutoMLJobChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "AutoMLProblemTypeConfig": AutoMLProblemTypeConfigTypeDef,
        "RoleArn": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "SecurityConfig": NotRequired[AutoMLSecurityConfigTypeDef],
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "ModelDeployConfig": NotRequired[ModelDeployConfigTypeDef],
        "DataSplitConfig": NotRequired[AutoMLDataSplitConfigTypeDef],
    },
)
ListPipelineExecutionStepsResponseTypeDef = TypedDict(
    "ListPipelineExecutionStepsResponseTypeDef",
    {
        "PipelineExecutionSteps": List[PipelineExecutionStepTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
CreateEndpointInputRequestTypeDef = TypedDict(
    "CreateEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
        "EndpointConfigName": str,
        "DeploymentConfig": NotRequired[DeploymentConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DeploymentConfigUnionTypeDef = Union[DeploymentConfigTypeDef, DeploymentConfigOutputTypeDef]
UpdateEndpointInputRequestTypeDef = TypedDict(
    "UpdateEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
        "EndpointConfigName": str,
        "RetainAllVariantProperties": NotRequired[bool],
        "ExcludeRetainedVariantProperties": NotRequired[Sequence[VariantPropertyTypeDef]],
        "DeploymentConfig": NotRequired[DeploymentConfigTypeDef],
        "RetainDeploymentConfig": NotRequired[bool],
    },
)
DescribeInferenceRecommendationsJobResponseTypeDef = TypedDict(
    "DescribeInferenceRecommendationsJobResponseTypeDef",
    {
        "JobName": str,
        "JobDescription": str,
        "JobType": RecommendationJobTypeType,
        "JobArn": str,
        "RoleArn": str,
        "Status": RecommendationJobStatusType,
        "CreationTime": datetime,
        "CompletionTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "InputConfig": RecommendationJobInputConfigOutputTypeDef,
        "StoppingConditions": RecommendationJobStoppingConditionsOutputTypeDef,
        "InferenceRecommendations": List[InferenceRecommendationTypeDef],
        "EndpointPerformances": List[EndpointPerformanceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInferenceRecommendationsJobRequestRequestTypeDef = TypedDict(
    "CreateInferenceRecommendationsJobRequestRequestTypeDef",
    {
        "JobName": str,
        "JobType": RecommendationJobTypeType,
        "RoleArn": str,
        "InputConfig": RecommendationJobInputConfigTypeDef,
        "JobDescription": NotRequired[str],
        "StoppingConditions": NotRequired[RecommendationJobStoppingConditionsTypeDef],
        "OutputConfig": NotRequired[RecommendationJobOutputConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
RecommendationJobInputConfigUnionTypeDef = Union[
    RecommendationJobInputConfigTypeDef, RecommendationJobInputConfigOutputTypeDef
]
DescribeEndpointConfigOutputTypeDef = TypedDict(
    "DescribeEndpointConfigOutputTypeDef",
    {
        "EndpointConfigName": str,
        "EndpointConfigArn": str,
        "ProductionVariants": List[ProductionVariantTypeDef],
        "DataCaptureConfig": DataCaptureConfigOutputTypeDef,
        "KmsKeyId": str,
        "CreationTime": datetime,
        "AsyncInferenceConfig": AsyncInferenceConfigOutputTypeDef,
        "ExplainerConfig": ExplainerConfigOutputTypeDef,
        "ShadowProductionVariants": List[ProductionVariantTypeDef],
        "ExecutionRoleArn": str,
        "VpcConfig": VpcConfigOutputTypeDef,
        "EnableNetworkIsolation": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeEndpointOutputTypeDef = TypedDict(
    "DescribeEndpointOutputTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "EndpointConfigName": str,
        "ProductionVariants": List[ProductionVariantSummaryTypeDef],
        "DataCaptureConfig": DataCaptureConfigSummaryTypeDef,
        "EndpointStatus": EndpointStatusType,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastDeploymentConfig": DeploymentConfigOutputTypeDef,
        "AsyncInferenceConfig": AsyncInferenceConfigOutputTypeDef,
        "PendingDeploymentSummary": PendingDeploymentSummaryTypeDef,
        "ExplainerConfig": ExplainerConfigOutputTypeDef,
        "ShadowProductionVariants": List[ProductionVariantSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateEndpointConfigInputRequestTypeDef = TypedDict(
    "CreateEndpointConfigInputRequestTypeDef",
    {
        "EndpointConfigName": str,
        "ProductionVariants": Sequence[ProductionVariantTypeDef],
        "DataCaptureConfig": NotRequired[DataCaptureConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "KmsKeyId": NotRequired[str],
        "AsyncInferenceConfig": NotRequired[AsyncInferenceConfigTypeDef],
        "ExplainerConfig": NotRequired[ExplainerConfigTypeDef],
        "ShadowProductionVariants": NotRequired[Sequence[ProductionVariantTypeDef]],
        "ExecutionRoleArn": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "EnableNetworkIsolation": NotRequired[bool],
    },
)
ExplainerConfigUnionTypeDef = Union[ExplainerConfigTypeDef, ExplainerConfigOutputTypeDef]
DescribeHyperParameterTuningJobResponseTypeDef = TypedDict(
    "DescribeHyperParameterTuningJobResponseTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "HyperParameterTuningJobArn": str,
        "HyperParameterTuningJobConfig": HyperParameterTuningJobConfigOutputTypeDef,
        "TrainingJobDefinition": HyperParameterTrainingJobDefinitionOutputTypeDef,
        "TrainingJobDefinitions": List[HyperParameterTrainingJobDefinitionOutputTypeDef],
        "HyperParameterTuningJobStatus": HyperParameterTuningJobStatusType,
        "CreationTime": datetime,
        "HyperParameterTuningEndTime": datetime,
        "LastModifiedTime": datetime,
        "TrainingJobStatusCounters": TrainingJobStatusCountersTypeDef,
        "ObjectiveStatusCounters": ObjectiveStatusCountersTypeDef,
        "BestTrainingJob": HyperParameterTrainingJobSummaryTypeDef,
        "OverallBestTrainingJob": HyperParameterTrainingJobSummaryTypeDef,
        "WarmStartConfig": HyperParameterTuningJobWarmStartConfigOutputTypeDef,
        "Autotune": AutotuneTypeDef,
        "FailureReason": str,
        "TuningJobCompletionDetails": HyperParameterTuningJobCompletionDetailsTypeDef,
        "ConsumedResources": HyperParameterTuningJobConsumedResourcesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HyperParameterTuningJobSearchEntityTypeDef = TypedDict(
    "HyperParameterTuningJobSearchEntityTypeDef",
    {
        "HyperParameterTuningJobName": NotRequired[str],
        "HyperParameterTuningJobArn": NotRequired[str],
        "HyperParameterTuningJobConfig": NotRequired[HyperParameterTuningJobConfigOutputTypeDef],
        "TrainingJobDefinition": NotRequired[HyperParameterTrainingJobDefinitionOutputTypeDef],
        "TrainingJobDefinitions": NotRequired[
            List[HyperParameterTrainingJobDefinitionOutputTypeDef]
        ],
        "HyperParameterTuningJobStatus": NotRequired[HyperParameterTuningJobStatusType],
        "CreationTime": NotRequired[datetime],
        "HyperParameterTuningEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "TrainingJobStatusCounters": NotRequired[TrainingJobStatusCountersTypeDef],
        "ObjectiveStatusCounters": NotRequired[ObjectiveStatusCountersTypeDef],
        "BestTrainingJob": NotRequired[HyperParameterTrainingJobSummaryTypeDef],
        "OverallBestTrainingJob": NotRequired[HyperParameterTrainingJobSummaryTypeDef],
        "WarmStartConfig": NotRequired[HyperParameterTuningJobWarmStartConfigOutputTypeDef],
        "FailureReason": NotRequired[str],
        "TuningJobCompletionDetails": NotRequired[HyperParameterTuningJobCompletionDetailsTypeDef],
        "ConsumedResources": NotRequired[HyperParameterTuningJobConsumedResourcesTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
CreateTrainingJobRequestRequestTypeDef = TypedDict(
    "CreateTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
        "AlgorithmSpecification": AlgorithmSpecificationTypeDef,
        "RoleArn": str,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "ResourceConfig": ResourceConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "HyperParameters": NotRequired[Mapping[str, str]],
        "InputDataConfig": NotRequired[Sequence[ChannelUnionTypeDef]],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "DebugHookConfig": NotRequired[DebugHookConfigTypeDef],
        "DebugRuleConfigurations": NotRequired[Sequence[DebugRuleConfigurationUnionTypeDef]],
        "TensorBoardOutputConfig": NotRequired[TensorBoardOutputConfigTypeDef],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "ProfilerConfig": NotRequired[ProfilerConfigTypeDef],
        "ProfilerRuleConfigurations": NotRequired[Sequence[ProfilerRuleConfigurationUnionTypeDef]],
        "Environment": NotRequired[Mapping[str, str]],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "RemoteDebugConfig": NotRequired[RemoteDebugConfigTypeDef],
        "InfraCheckConfig": NotRequired[InfraCheckConfigTypeDef],
        "SessionChainingConfig": NotRequired[SessionChainingConfigTypeDef],
    },
)
HyperParameterTrainingJobDefinitionUnionTypeDef = Union[
    HyperParameterTrainingJobDefinitionTypeDef,
    HyperParameterTrainingJobDefinitionExtraOutputTypeDef,
]
ListSpacesResponseTypeDef = TypedDict(
    "ListSpacesResponseTypeDef",
    {
        "Spaces": List[SpaceDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListInferenceRecommendationsJobStepsResponseTypeDef = TypedDict(
    "ListInferenceRecommendationsJobStepsResponseTypeDef",
    {
        "Steps": List[InferenceRecommendationsJobStepTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DescribeWorkteamResponseTypeDef = TypedDict(
    "DescribeWorkteamResponseTypeDef",
    {
        "Workteam": WorkteamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListWorkteamsResponseTypeDef = TypedDict(
    "ListWorkteamsResponseTypeDef",
    {
        "Workteams": List[WorkteamTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateWorkteamResponseTypeDef = TypedDict(
    "UpdateWorkteamResponseTypeDef",
    {
        "Workteam": WorkteamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TrainingSpecificationUnionTypeDef = Union[
    TrainingSpecificationTypeDef, TrainingSpecificationOutputTypeDef
]
ListLabelingJobsResponseTypeDef = TypedDict(
    "ListLabelingJobsResponseTypeDef",
    {
        "LabelingJobSummaryList": List[LabelingJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
DynamicScalingConfigurationTypeDef = TypedDict(
    "DynamicScalingConfigurationTypeDef",
    {
        "MinCapacity": NotRequired[int],
        "MaxCapacity": NotRequired[int],
        "ScaleInCooldown": NotRequired[int],
        "ScaleOutCooldown": NotRequired[int],
        "ScalingPolicies": NotRequired[List[ScalingPolicyTypeDef]],
    },
)
DescribeModelOutputTypeDef = TypedDict(
    "DescribeModelOutputTypeDef",
    {
        "ModelName": str,
        "PrimaryContainer": ContainerDefinitionOutputTypeDef,
        "Containers": List[ContainerDefinitionOutputTypeDef],
        "InferenceExecutionConfig": InferenceExecutionConfigTypeDef,
        "ExecutionRoleArn": str,
        "VpcConfig": VpcConfigOutputTypeDef,
        "CreationTime": datetime,
        "ModelArn": str,
        "EnableNetworkIsolation": bool,
        "DeploymentRecommendation": DeploymentRecommendationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModelTypeDef = TypedDict(
    "ModelTypeDef",
    {
        "ModelName": NotRequired[str],
        "PrimaryContainer": NotRequired[ContainerDefinitionOutputTypeDef],
        "Containers": NotRequired[List[ContainerDefinitionOutputTypeDef]],
        "InferenceExecutionConfig": NotRequired[InferenceExecutionConfigTypeDef],
        "ExecutionRoleArn": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigOutputTypeDef],
        "CreationTime": NotRequired[datetime],
        "ModelArn": NotRequired[str],
        "EnableNetworkIsolation": NotRequired[bool],
        "Tags": NotRequired[List[TagTypeDef]],
        "DeploymentRecommendation": NotRequired[DeploymentRecommendationTypeDef],
    },
)
ContainerDefinitionUnionTypeDef = Union[
    ContainerDefinitionTypeDef, ContainerDefinitionExtraOutputTypeDef
]
AdditionalInferenceSpecificationDefinitionExtraOutputTypeDef = TypedDict(
    "AdditionalInferenceSpecificationDefinitionExtraOutputTypeDef",
    {
        "Name": str,
        "Containers": List[ModelPackageContainerDefinitionExtraOutputTypeDef],
        "Description": NotRequired[str],
        "SupportedTransformInstanceTypes": NotRequired[List[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            List[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[List[str]],
        "SupportedResponseMIMETypes": NotRequired[List[str]],
    },
)
InferenceSpecificationExtraOutputTypeDef = TypedDict(
    "InferenceSpecificationExtraOutputTypeDef",
    {
        "Containers": List[ModelPackageContainerDefinitionExtraOutputTypeDef],
        "SupportedTransformInstanceTypes": NotRequired[List[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            List[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[List[str]],
        "SupportedResponseMIMETypes": NotRequired[List[str]],
    },
)
AdditionalInferenceSpecificationDefinitionOutputTypeDef = TypedDict(
    "AdditionalInferenceSpecificationDefinitionOutputTypeDef",
    {
        "Name": str,
        "Containers": List[ModelPackageContainerDefinitionOutputTypeDef],
        "Description": NotRequired[str],
        "SupportedTransformInstanceTypes": NotRequired[List[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            List[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[List[str]],
        "SupportedResponseMIMETypes": NotRequired[List[str]],
    },
)
InferenceSpecificationOutputTypeDef = TypedDict(
    "InferenceSpecificationOutputTypeDef",
    {
        "Containers": List[ModelPackageContainerDefinitionOutputTypeDef],
        "SupportedTransformInstanceTypes": NotRequired[List[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            List[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[List[str]],
        "SupportedResponseMIMETypes": NotRequired[List[str]],
    },
)
AdditionalInferenceSpecificationDefinitionTypeDef = TypedDict(
    "AdditionalInferenceSpecificationDefinitionTypeDef",
    {
        "Name": str,
        "Containers": Sequence[ModelPackageContainerDefinitionTypeDef],
        "Description": NotRequired[str],
        "SupportedTransformInstanceTypes": NotRequired[Sequence[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            Sequence[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[Sequence[str]],
        "SupportedResponseMIMETypes": NotRequired[Sequence[str]],
    },
)
InferenceSpecificationTypeDef = TypedDict(
    "InferenceSpecificationTypeDef",
    {
        "Containers": Sequence[ModelPackageContainerDefinitionTypeDef],
        "SupportedTransformInstanceTypes": NotRequired[Sequence[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            Sequence[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[Sequence[str]],
        "SupportedResponseMIMETypes": NotRequired[Sequence[str]],
    },
)
SourceAlgorithmSpecificationExtraOutputTypeDef = TypedDict(
    "SourceAlgorithmSpecificationExtraOutputTypeDef",
    {
        "SourceAlgorithms": List[SourceAlgorithmTypeDef],
    },
)
SourceAlgorithmSpecificationOutputTypeDef = TypedDict(
    "SourceAlgorithmSpecificationOutputTypeDef",
    {
        "SourceAlgorithms": List[SourceAlgorithmTypeDef],
    },
)
SourceAlgorithmSpecificationTypeDef = TypedDict(
    "SourceAlgorithmSpecificationTypeDef",
    {
        "SourceAlgorithms": Sequence[SourceAlgorithmTypeDef],
    },
)
MonitoringJobDefinitionExtraOutputTypeDef = TypedDict(
    "MonitoringJobDefinitionExtraOutputTypeDef",
    {
        "MonitoringInputs": List[MonitoringInputExtraOutputTypeDef],
        "MonitoringOutputConfig": MonitoringOutputConfigExtraOutputTypeDef,
        "MonitoringResources": MonitoringResourcesTypeDef,
        "MonitoringAppSpecification": MonitoringAppSpecificationExtraOutputTypeDef,
        "RoleArn": str,
        "BaselineConfig": NotRequired[MonitoringBaselineConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigExtraOutputTypeDef],
    },
)
DescribeDataQualityJobDefinitionResponseTypeDef = TypedDict(
    "DescribeDataQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "DataQualityBaselineConfig": DataQualityBaselineConfigTypeDef,
        "DataQualityAppSpecification": DataQualityAppSpecificationOutputTypeDef,
        "DataQualityJobInput": DataQualityJobInputOutputTypeDef,
        "DataQualityJobOutputConfig": MonitoringOutputConfigOutputTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigOutputTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeModelBiasJobDefinitionResponseTypeDef = TypedDict(
    "DescribeModelBiasJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "ModelBiasBaselineConfig": ModelBiasBaselineConfigTypeDef,
        "ModelBiasAppSpecification": ModelBiasAppSpecificationOutputTypeDef,
        "ModelBiasJobInput": ModelBiasJobInputOutputTypeDef,
        "ModelBiasJobOutputConfig": MonitoringOutputConfigOutputTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigOutputTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeModelExplainabilityJobDefinitionResponseTypeDef = TypedDict(
    "DescribeModelExplainabilityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "ModelExplainabilityBaselineConfig": ModelExplainabilityBaselineConfigTypeDef,
        "ModelExplainabilityAppSpecification": ModelExplainabilityAppSpecificationOutputTypeDef,
        "ModelExplainabilityJobInput": ModelExplainabilityJobInputOutputTypeDef,
        "ModelExplainabilityJobOutputConfig": MonitoringOutputConfigOutputTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigOutputTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeModelQualityJobDefinitionResponseTypeDef = TypedDict(
    "DescribeModelQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "ModelQualityBaselineConfig": ModelQualityBaselineConfigTypeDef,
        "ModelQualityAppSpecification": ModelQualityAppSpecificationOutputTypeDef,
        "ModelQualityJobInput": ModelQualityJobInputOutputTypeDef,
        "ModelQualityJobOutputConfig": MonitoringOutputConfigOutputTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigOutputTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MonitoringJobDefinitionOutputTypeDef = TypedDict(
    "MonitoringJobDefinitionOutputTypeDef",
    {
        "MonitoringInputs": List[MonitoringInputOutputTypeDef],
        "MonitoringOutputConfig": MonitoringOutputConfigOutputTypeDef,
        "MonitoringResources": MonitoringResourcesTypeDef,
        "MonitoringAppSpecification": MonitoringAppSpecificationOutputTypeDef,
        "RoleArn": str,
        "BaselineConfig": NotRequired[MonitoringBaselineConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigOutputTypeDef],
    },
)
CreateDataQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateDataQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "DataQualityAppSpecification": DataQualityAppSpecificationTypeDef,
        "DataQualityJobInput": DataQualityJobInputTypeDef,
        "DataQualityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "DataQualityBaselineConfig": NotRequired[DataQualityBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DataQualityJobInputUnionTypeDef = Union[
    DataQualityJobInputTypeDef, DataQualityJobInputOutputTypeDef
]
CreateModelBiasJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateModelBiasJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "ModelBiasAppSpecification": ModelBiasAppSpecificationTypeDef,
        "ModelBiasJobInput": ModelBiasJobInputTypeDef,
        "ModelBiasJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "ModelBiasBaselineConfig": NotRequired[ModelBiasBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ModelBiasJobInputUnionTypeDef = Union[ModelBiasJobInputTypeDef, ModelBiasJobInputOutputTypeDef]
CreateModelExplainabilityJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateModelExplainabilityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "ModelExplainabilityAppSpecification": ModelExplainabilityAppSpecificationTypeDef,
        "ModelExplainabilityJobInput": ModelExplainabilityJobInputTypeDef,
        "ModelExplainabilityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "ModelExplainabilityBaselineConfig": NotRequired[ModelExplainabilityBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ModelExplainabilityJobInputUnionTypeDef = Union[
    ModelExplainabilityJobInputTypeDef, ModelExplainabilityJobInputOutputTypeDef
]
CreateModelQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateModelQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "ModelQualityAppSpecification": ModelQualityAppSpecificationTypeDef,
        "ModelQualityJobInput": ModelQualityJobInputTypeDef,
        "ModelQualityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "ModelQualityBaselineConfig": NotRequired[ModelQualityBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ModelQualityJobInputUnionTypeDef = Union[
    ModelQualityJobInputTypeDef, ModelQualityJobInputOutputTypeDef
]
MonitoringJobDefinitionTypeDef = TypedDict(
    "MonitoringJobDefinitionTypeDef",
    {
        "MonitoringInputs": Sequence[MonitoringInputTypeDef],
        "MonitoringOutputConfig": MonitoringOutputConfigTypeDef,
        "MonitoringResources": MonitoringResourcesTypeDef,
        "MonitoringAppSpecification": MonitoringAppSpecificationTypeDef,
        "RoleArn": str,
        "BaselineConfig": NotRequired[MonitoringBaselineConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Environment": NotRequired[Mapping[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigTypeDef],
    },
)
ModelPackageValidationProfileExtraOutputTypeDef = TypedDict(
    "ModelPackageValidationProfileExtraOutputTypeDef",
    {
        "ProfileName": str,
        "TransformJobDefinition": TransformJobDefinitionExtraOutputTypeDef,
    },
)
AlgorithmValidationProfileOutputTypeDef = TypedDict(
    "AlgorithmValidationProfileOutputTypeDef",
    {
        "ProfileName": str,
        "TrainingJobDefinition": TrainingJobDefinitionOutputTypeDef,
        "TransformJobDefinition": NotRequired[TransformJobDefinitionOutputTypeDef],
    },
)
ModelPackageValidationProfileOutputTypeDef = TypedDict(
    "ModelPackageValidationProfileOutputTypeDef",
    {
        "ProfileName": str,
        "TransformJobDefinition": TransformJobDefinitionOutputTypeDef,
    },
)
AlgorithmValidationProfileTypeDef = TypedDict(
    "AlgorithmValidationProfileTypeDef",
    {
        "ProfileName": str,
        "TrainingJobDefinition": TrainingJobDefinitionTypeDef,
        "TransformJobDefinition": NotRequired[TransformJobDefinitionTypeDef],
    },
)
ModelPackageValidationProfileTypeDef = TypedDict(
    "ModelPackageValidationProfileTypeDef",
    {
        "ProfileName": str,
        "TransformJobDefinition": TransformJobDefinitionTypeDef,
    },
)
TrialComponentSourceDetailTypeDef = TypedDict(
    "TrialComponentSourceDetailTypeDef",
    {
        "SourceArn": NotRequired[str],
        "TrainingJob": NotRequired[TrainingJobTypeDef],
        "ProcessingJob": NotRequired[ProcessingJobTypeDef],
        "TransformJob": NotRequired[TransformJobTypeDef],
    },
)
CreateHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "CreateHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "HyperParameterTuningJobConfig": HyperParameterTuningJobConfigTypeDef,
        "TrainingJobDefinition": NotRequired[HyperParameterTrainingJobDefinitionTypeDef],
        "TrainingJobDefinitions": NotRequired[
            Sequence[HyperParameterTrainingJobDefinitionUnionTypeDef]
        ],
        "WarmStartConfig": NotRequired[HyperParameterTuningJobWarmStartConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "Autotune": NotRequired[AutotuneTypeDef],
    },
)
GetScalingConfigurationRecommendationResponseTypeDef = TypedDict(
    "GetScalingConfigurationRecommendationResponseTypeDef",
    {
        "InferenceRecommendationsJobName": str,
        "RecommendationId": str,
        "EndpointName": str,
        "TargetCpuUtilizationPerCore": int,
        "ScalingPolicyObjective": ScalingPolicyObjectiveTypeDef,
        "Metric": ScalingPolicyMetricTypeDef,
        "DynamicScalingConfiguration": DynamicScalingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateModelInputRequestTypeDef = TypedDict(
    "CreateModelInputRequestTypeDef",
    {
        "ModelName": str,
        "PrimaryContainer": NotRequired[ContainerDefinitionTypeDef],
        "Containers": NotRequired[Sequence[ContainerDefinitionUnionTypeDef]],
        "InferenceExecutionConfig": NotRequired[InferenceExecutionConfigTypeDef],
        "ExecutionRoleArn": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "EnableNetworkIsolation": NotRequired[bool],
    },
)
BatchDescribeModelPackageSummaryTypeDef = TypedDict(
    "BatchDescribeModelPackageSummaryTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageArn": str,
        "CreationTime": datetime,
        "InferenceSpecification": InferenceSpecificationOutputTypeDef,
        "ModelPackageStatus": ModelPackageStatusType,
        "ModelPackageVersion": NotRequired[int],
        "ModelPackageDescription": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
    },
)
AdditionalInferenceSpecificationDefinitionUnionTypeDef = Union[
    AdditionalInferenceSpecificationDefinitionTypeDef,
    AdditionalInferenceSpecificationDefinitionExtraOutputTypeDef,
]
InferenceSpecificationUnionTypeDef = Union[
    InferenceSpecificationTypeDef, InferenceSpecificationExtraOutputTypeDef
]
SourceAlgorithmSpecificationUnionTypeDef = Union[
    SourceAlgorithmSpecificationTypeDef, SourceAlgorithmSpecificationExtraOutputTypeDef
]
MonitoringScheduleConfigExtraOutputTypeDef = TypedDict(
    "MonitoringScheduleConfigExtraOutputTypeDef",
    {
        "ScheduleConfig": NotRequired[ScheduleConfigTypeDef],
        "MonitoringJobDefinition": NotRequired[MonitoringJobDefinitionExtraOutputTypeDef],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)
MonitoringScheduleConfigOutputTypeDef = TypedDict(
    "MonitoringScheduleConfigOutputTypeDef",
    {
        "ScheduleConfig": NotRequired[ScheduleConfigTypeDef],
        "MonitoringJobDefinition": NotRequired[MonitoringJobDefinitionOutputTypeDef],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)
MonitoringScheduleConfigTypeDef = TypedDict(
    "MonitoringScheduleConfigTypeDef",
    {
        "ScheduleConfig": NotRequired[ScheduleConfigTypeDef],
        "MonitoringJobDefinition": NotRequired[MonitoringJobDefinitionTypeDef],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)
ModelPackageValidationSpecificationExtraOutputTypeDef = TypedDict(
    "ModelPackageValidationSpecificationExtraOutputTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": List[ModelPackageValidationProfileExtraOutputTypeDef],
    },
)
AlgorithmValidationSpecificationOutputTypeDef = TypedDict(
    "AlgorithmValidationSpecificationOutputTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": List[AlgorithmValidationProfileOutputTypeDef],
    },
)
ModelPackageValidationSpecificationOutputTypeDef = TypedDict(
    "ModelPackageValidationSpecificationOutputTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": List[ModelPackageValidationProfileOutputTypeDef],
    },
)
AlgorithmValidationSpecificationTypeDef = TypedDict(
    "AlgorithmValidationSpecificationTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": Sequence[AlgorithmValidationProfileTypeDef],
    },
)
ModelPackageValidationSpecificationTypeDef = TypedDict(
    "ModelPackageValidationSpecificationTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": Sequence[ModelPackageValidationProfileTypeDef],
    },
)
TrialComponentTypeDef = TypedDict(
    "TrialComponentTypeDef",
    {
        "TrialComponentName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "TrialComponentArn": NotRequired[str],
        "Source": NotRequired[TrialComponentSourceTypeDef],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Parameters": NotRequired[Dict[str, TrialComponentParameterValueTypeDef]],
        "InputArtifacts": NotRequired[Dict[str, TrialComponentArtifactTypeDef]],
        "OutputArtifacts": NotRequired[Dict[str, TrialComponentArtifactTypeDef]],
        "Metrics": NotRequired[List[TrialComponentMetricSummaryTypeDef]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "SourceDetail": NotRequired[TrialComponentSourceDetailTypeDef],
        "LineageGroupArn": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "Parents": NotRequired[List[ParentTypeDef]],
        "RunName": NotRequired[str],
    },
)
BatchDescribeModelPackageOutputTypeDef = TypedDict(
    "BatchDescribeModelPackageOutputTypeDef",
    {
        "ModelPackageSummaries": Dict[str, BatchDescribeModelPackageSummaryTypeDef],
        "BatchDescribeModelPackageErrorMap": Dict[str, BatchDescribeModelPackageErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateModelPackageInputRequestTypeDef = TypedDict(
    "UpdateModelPackageInputRequestTypeDef",
    {
        "ModelPackageArn": str,
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "ApprovalDescription": NotRequired[str],
        "CustomerMetadataProperties": NotRequired[Mapping[str, str]],
        "CustomerMetadataPropertiesToRemove": NotRequired[Sequence[str]],
        "AdditionalInferenceSpecificationsToAdd": NotRequired[
            Sequence[AdditionalInferenceSpecificationDefinitionUnionTypeDef]
        ],
        "InferenceSpecification": NotRequired[InferenceSpecificationTypeDef],
        "SourceUri": NotRequired[str],
        "ModelCard": NotRequired[ModelPackageModelCardTypeDef],
    },
)
DescribeMonitoringScheduleResponseTypeDef = TypedDict(
    "DescribeMonitoringScheduleResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "MonitoringScheduleName": str,
        "MonitoringScheduleStatus": ScheduleStatusType,
        "MonitoringType": MonitoringTypeType,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "MonitoringScheduleConfig": MonitoringScheduleConfigOutputTypeDef,
        "EndpointName": str,
        "LastMonitoringExecutionSummary": MonitoringExecutionSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModelDashboardMonitoringScheduleTypeDef = TypedDict(
    "ModelDashboardMonitoringScheduleTypeDef",
    {
        "MonitoringScheduleArn": NotRequired[str],
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringScheduleStatus": NotRequired[ScheduleStatusType],
        "MonitoringType": NotRequired[MonitoringTypeType],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "MonitoringScheduleConfig": NotRequired[MonitoringScheduleConfigOutputTypeDef],
        "EndpointName": NotRequired[str],
        "MonitoringAlertSummaries": NotRequired[List[MonitoringAlertSummaryTypeDef]],
        "LastMonitoringExecutionSummary": NotRequired[MonitoringExecutionSummaryTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputOutputTypeDef],
    },
)
MonitoringScheduleTypeDef = TypedDict(
    "MonitoringScheduleTypeDef",
    {
        "MonitoringScheduleArn": NotRequired[str],
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringScheduleStatus": NotRequired[ScheduleStatusType],
        "MonitoringType": NotRequired[MonitoringTypeType],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "MonitoringScheduleConfig": NotRequired[MonitoringScheduleConfigOutputTypeDef],
        "EndpointName": NotRequired[str],
        "LastMonitoringExecutionSummary": NotRequired[MonitoringExecutionSummaryTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
CreateMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "CreateMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringScheduleConfig": MonitoringScheduleConfigTypeDef,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
MonitoringScheduleConfigUnionTypeDef = Union[
    MonitoringScheduleConfigTypeDef, MonitoringScheduleConfigExtraOutputTypeDef
]
UpdateMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "UpdateMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringScheduleConfig": MonitoringScheduleConfigTypeDef,
    },
)
DescribeAlgorithmOutputTypeDef = TypedDict(
    "DescribeAlgorithmOutputTypeDef",
    {
        "AlgorithmName": str,
        "AlgorithmArn": str,
        "AlgorithmDescription": str,
        "CreationTime": datetime,
        "TrainingSpecification": TrainingSpecificationOutputTypeDef,
        "InferenceSpecification": InferenceSpecificationOutputTypeDef,
        "ValidationSpecification": AlgorithmValidationSpecificationOutputTypeDef,
        "AlgorithmStatus": AlgorithmStatusType,
        "AlgorithmStatusDetails": AlgorithmStatusDetailsTypeDef,
        "ProductId": str,
        "CertifyForMarketplace": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeModelPackageOutputTypeDef = TypedDict(
    "DescribeModelPackageOutputTypeDef",
    {
        "ModelPackageName": str,
        "ModelPackageGroupName": str,
        "ModelPackageVersion": int,
        "ModelPackageArn": str,
        "ModelPackageDescription": str,
        "CreationTime": datetime,
        "InferenceSpecification": InferenceSpecificationOutputTypeDef,
        "SourceAlgorithmSpecification": SourceAlgorithmSpecificationOutputTypeDef,
        "ValidationSpecification": ModelPackageValidationSpecificationOutputTypeDef,
        "ModelPackageStatus": ModelPackageStatusType,
        "ModelPackageStatusDetails": ModelPackageStatusDetailsTypeDef,
        "CertifyForMarketplace": bool,
        "ModelApprovalStatus": ModelApprovalStatusType,
        "CreatedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "ModelMetrics": ModelMetricsTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ApprovalDescription": str,
        "Domain": str,
        "Task": str,
        "SamplePayloadUrl": str,
        "CustomerMetadataProperties": Dict[str, str],
        "DriftCheckBaselines": DriftCheckBaselinesTypeDef,
        "AdditionalInferenceSpecifications": List[
            AdditionalInferenceSpecificationDefinitionOutputTypeDef
        ],
        "SkipModelValidation": SkipModelValidationType,
        "SourceUri": str,
        "SecurityConfig": ModelPackageSecurityConfigTypeDef,
        "ModelCard": ModelPackageModelCardTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ModelPackageTypeDef = TypedDict(
    "ModelPackageTypeDef",
    {
        "ModelPackageName": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageVersion": NotRequired[int],
        "ModelPackageArn": NotRequired[str],
        "ModelPackageDescription": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "InferenceSpecification": NotRequired[InferenceSpecificationOutputTypeDef],
        "SourceAlgorithmSpecification": NotRequired[SourceAlgorithmSpecificationOutputTypeDef],
        "ValidationSpecification": NotRequired[ModelPackageValidationSpecificationOutputTypeDef],
        "ModelPackageStatus": NotRequired[ModelPackageStatusType],
        "ModelPackageStatusDetails": NotRequired[ModelPackageStatusDetailsTypeDef],
        "CertifyForMarketplace": NotRequired[bool],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "ModelMetrics": NotRequired[ModelMetricsTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "ApprovalDescription": NotRequired[str],
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "SamplePayloadUrl": NotRequired[str],
        "AdditionalInferenceSpecifications": NotRequired[
            List[AdditionalInferenceSpecificationDefinitionOutputTypeDef]
        ],
        "SourceUri": NotRequired[str],
        "SecurityConfig": NotRequired[ModelPackageSecurityConfigTypeDef],
        "ModelCard": NotRequired[ModelPackageModelCardTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "CustomerMetadataProperties": NotRequired[Dict[str, str]],
        "DriftCheckBaselines": NotRequired[DriftCheckBaselinesTypeDef],
        "SkipModelValidation": NotRequired[SkipModelValidationType],
    },
)
AlgorithmValidationSpecificationUnionTypeDef = Union[
    AlgorithmValidationSpecificationTypeDef, AlgorithmValidationSpecificationOutputTypeDef
]
CreateAlgorithmInputRequestTypeDef = TypedDict(
    "CreateAlgorithmInputRequestTypeDef",
    {
        "AlgorithmName": str,
        "TrainingSpecification": TrainingSpecificationTypeDef,
        "AlgorithmDescription": NotRequired[str],
        "InferenceSpecification": NotRequired[InferenceSpecificationTypeDef],
        "ValidationSpecification": NotRequired[AlgorithmValidationSpecificationTypeDef],
        "CertifyForMarketplace": NotRequired[bool],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateModelPackageInputRequestTypeDef = TypedDict(
    "CreateModelPackageInputRequestTypeDef",
    {
        "ModelPackageName": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageDescription": NotRequired[str],
        "InferenceSpecification": NotRequired[InferenceSpecificationTypeDef],
        "ValidationSpecification": NotRequired[ModelPackageValidationSpecificationTypeDef],
        "SourceAlgorithmSpecification": NotRequired[SourceAlgorithmSpecificationTypeDef],
        "CertifyForMarketplace": NotRequired[bool],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "ModelMetrics": NotRequired[ModelMetricsTypeDef],
        "ClientToken": NotRequired[str],
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "SamplePayloadUrl": NotRequired[str],
        "CustomerMetadataProperties": NotRequired[Mapping[str, str]],
        "DriftCheckBaselines": NotRequired[DriftCheckBaselinesTypeDef],
        "AdditionalInferenceSpecifications": NotRequired[
            Sequence[AdditionalInferenceSpecificationDefinitionUnionTypeDef]
        ],
        "SkipModelValidation": NotRequired[SkipModelValidationType],
        "SourceUri": NotRequired[str],
        "SecurityConfig": NotRequired[ModelPackageSecurityConfigTypeDef],
        "ModelCard": NotRequired[ModelPackageModelCardTypeDef],
    },
)
ModelPackageValidationSpecificationUnionTypeDef = Union[
    ModelPackageValidationSpecificationTypeDef,
    ModelPackageValidationSpecificationExtraOutputTypeDef,
]
ModelDashboardModelTypeDef = TypedDict(
    "ModelDashboardModelTypeDef",
    {
        "Model": NotRequired[ModelTypeDef],
        "Endpoints": NotRequired[List[ModelDashboardEndpointTypeDef]],
        "LastBatchTransformJob": NotRequired[TransformJobTypeDef],
        "MonitoringSchedules": NotRequired[List[ModelDashboardMonitoringScheduleTypeDef]],
        "ModelCard": NotRequired[ModelDashboardModelCardTypeDef],
    },
)
EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "EndpointConfigName": str,
        "EndpointStatus": EndpointStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ProductionVariants": NotRequired[List[ProductionVariantSummaryTypeDef]],
        "DataCaptureConfig": NotRequired[DataCaptureConfigSummaryTypeDef],
        "FailureReason": NotRequired[str],
        "MonitoringSchedules": NotRequired[List[MonitoringScheduleTypeDef]],
        "Tags": NotRequired[List[TagTypeDef]],
        "ShadowProductionVariants": NotRequired[List[ProductionVariantSummaryTypeDef]],
    },
)
SearchRecordTypeDef = TypedDict(
    "SearchRecordTypeDef",
    {
        "TrainingJob": NotRequired[TrainingJobTypeDef],
        "Experiment": NotRequired[ExperimentTypeDef],
        "Trial": NotRequired[TrialTypeDef],
        "TrialComponent": NotRequired[TrialComponentTypeDef],
        "Endpoint": NotRequired[EndpointTypeDef],
        "ModelPackage": NotRequired[ModelPackageTypeDef],
        "ModelPackageGroup": NotRequired[ModelPackageGroupTypeDef],
        "Pipeline": NotRequired[PipelineTypeDef],
        "PipelineExecution": NotRequired[PipelineExecutionTypeDef],
        "FeatureGroup": NotRequired[FeatureGroupTypeDef],
        "FeatureMetadata": NotRequired[FeatureMetadataTypeDef],
        "Project": NotRequired[ProjectTypeDef],
        "HyperParameterTuningJob": NotRequired[HyperParameterTuningJobSearchEntityTypeDef],
        "ModelCard": NotRequired[ModelCardTypeDef],
        "Model": NotRequired[ModelDashboardModelTypeDef],
    },
)
SearchResponseTypeDef = TypedDict(
    "SearchResponseTypeDef",
    {
        "Results": List[SearchRecordTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
