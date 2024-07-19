"""
Type annotations for medialive service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_medialive/type_defs/)

Usage::

    ```python
    from mypy_boto3_medialive.type_defs import AacSettingsTypeDef

    data: AacSettingsTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AacCodingModeType,
    AacInputTypeType,
    AacProfileType,
    AacRateControlModeType,
    AacRawFormatType,
    AacSpecType,
    AacVbrQualityType,
    Ac3AttenuationControlType,
    Ac3BitstreamModeType,
    Ac3CodingModeType,
    Ac3DrcProfileType,
    Ac3LfeFilterType,
    Ac3MetadataControlType,
    AccessibilityTypeType,
    AfdSignalingType,
    AlgorithmType,
    AudioDescriptionAudioTypeControlType,
    AudioDescriptionLanguageCodeControlType,
    AudioLanguageSelectionPolicyType,
    AudioNormalizationAlgorithmType,
    AudioOnlyHlsSegmentTypeType,
    AudioOnlyHlsTrackTypeType,
    AudioTypeType,
    AuthenticationSchemeType,
    AvailBlankingStateType,
    BlackoutSlateNetworkEndBlackoutType,
    BlackoutSlateStateType,
    BurnInAlignmentType,
    BurnInBackgroundColorType,
    BurnInFontColorType,
    BurnInOutlineColorType,
    BurnInShadowColorType,
    BurnInTeletextGridControlType,
    CdiInputResolutionType,
    ChannelClassType,
    ChannelPipelineIdToRestartType,
    ChannelStateType,
    CloudWatchAlarmTemplateComparisonOperatorType,
    CloudWatchAlarmTemplateStatisticType,
    CloudWatchAlarmTemplateTargetResourceTypeType,
    CloudWatchAlarmTemplateTreatMissingDataType,
    CmafIngestSegmentLengthUnitsType,
    CmafNielsenId3BehaviorType,
    ColorSpaceType,
    DashRoleAudioType,
    DashRoleCaptionType,
    DeviceSettingsSyncStateType,
    DeviceUpdateStatusType,
    DolbyEProgramSelectionType,
    DvbDashAccessibilityType,
    DvbSdtOutputSdtType,
    DvbSubDestinationAlignmentType,
    DvbSubDestinationBackgroundColorType,
    DvbSubDestinationFontColorType,
    DvbSubDestinationOutlineColorType,
    DvbSubDestinationShadowColorType,
    DvbSubDestinationTeletextGridControlType,
    DvbSubOcrLanguageType,
    Eac3AtmosCodingModeType,
    Eac3AtmosDrcLineType,
    Eac3AtmosDrcRfType,
    Eac3AttenuationControlType,
    Eac3BitstreamModeType,
    Eac3CodingModeType,
    Eac3DcFilterType,
    Eac3DrcLineType,
    Eac3DrcRfType,
    Eac3LfeControlType,
    Eac3LfeFilterType,
    Eac3MetadataControlType,
    Eac3PassthroughControlType,
    Eac3PhaseControlType,
    Eac3StereoDownmixType,
    Eac3SurroundExModeType,
    Eac3SurroundModeType,
    EbuTtDDestinationStyleControlType,
    EbuTtDFillLineGapControlType,
    EmbeddedConvert608To708Type,
    EmbeddedScte20DetectionType,
    EventBridgeRuleTemplateEventTypeType,
    FeatureActivationsInputPrepareScheduleActionsType,
    FeatureActivationsOutputStaticImageOverlayScheduleActionsType,
    FecOutputIncludeFecType,
    FixedAfdType,
    Fmp4NielsenId3BehaviorType,
    Fmp4TimedMetadataBehaviorType,
    FollowPointType,
    FrameCaptureIntervalUnitType,
    GlobalConfigurationInputEndActionType,
    GlobalConfigurationLowFramerateInputsType,
    GlobalConfigurationOutputLockingModeType,
    GlobalConfigurationOutputTimingSourceType,
    H264AdaptiveQuantizationType,
    H264ColorMetadataType,
    H264EntropyEncodingType,
    H264FlickerAqType,
    H264ForceFieldPicturesType,
    H264FramerateControlType,
    H264GopBReferenceType,
    H264GopSizeUnitsType,
    H264LevelType,
    H264LookAheadRateControlType,
    H264ParControlType,
    H264ProfileType,
    H264QualityLevelType,
    H264RateControlModeType,
    H264ScanTypeType,
    H264SceneChangeDetectType,
    H264SpatialAqType,
    H264SubGopLengthType,
    H264SyntaxType,
    H264TemporalAqType,
    H264TimecodeInsertionBehaviorType,
    H265AdaptiveQuantizationType,
    H265AlternativeTransferFunctionType,
    H265ColorMetadataType,
    H265FlickerAqType,
    H265GopSizeUnitsType,
    H265LevelType,
    H265LookAheadRateControlType,
    H265MvOverPictureBoundariesType,
    H265MvTemporalPredictorType,
    H265ProfileType,
    H265RateControlModeType,
    H265ScanTypeType,
    H265SceneChangeDetectType,
    H265TierType,
    H265TilePaddingType,
    H265TimecodeInsertionBehaviorType,
    H265TreeblockSizeType,
    HlsAdMarkersType,
    HlsAkamaiHttpTransferModeType,
    HlsCaptionLanguageSettingType,
    HlsClientCacheType,
    HlsCodecSpecificationType,
    HlsDirectoryStructureType,
    HlsDiscontinuityTagsType,
    HlsEncryptionTypeType,
    HlsH265PackagingTypeType,
    HlsId3SegmentTaggingStateType,
    HlsIncompleteSegmentBehaviorType,
    HlsIvInManifestType,
    HlsIvSourceType,
    HlsManifestCompressionType,
    HlsManifestDurationFormatType,
    HlsModeType,
    HlsOutputSelectionType,
    HlsProgramDateTimeClockType,
    HlsProgramDateTimeType,
    HlsRedundantManifestType,
    HlsScte35SourceTypeType,
    HlsSegmentationModeType,
    HlsStreamInfResolutionType,
    HlsTimedMetadataId3FrameType,
    HlsTsFileModeType,
    HlsWebdavHttpTransferModeType,
    IFrameOnlyPlaylistTypeType,
    IncludeFillerNalUnitsType,
    InputClassType,
    InputCodecType,
    InputDeblockFilterType,
    InputDenoiseFilterType,
    InputDeviceActiveInputType,
    InputDeviceCodecType,
    InputDeviceConfigurableAudioChannelPairProfileType,
    InputDeviceConfiguredInputType,
    InputDeviceConnectionStateType,
    InputDeviceIpSchemeType,
    InputDeviceOutputTypeType,
    InputDeviceScanTypeType,
    InputDeviceStateType,
    InputDeviceTransferTypeType,
    InputDeviceTypeType,
    InputDeviceUhdAudioChannelPairProfileType,
    InputFilterType,
    InputLossActionForHlsOutType,
    InputLossActionForMsSmoothOutType,
    InputLossActionForRtmpOutType,
    InputLossActionForUdpOutType,
    InputLossImageTypeType,
    InputMaximumBitrateType,
    InputPreferenceType,
    InputResolutionType,
    InputSecurityGroupStateType,
    InputSourceEndBehaviorType,
    InputSourceTypeType,
    InputStateType,
    InputTimecodeSourceType,
    InputTypeType,
    LastFrameClippingBehaviorType,
    LogLevelType,
    M2tsAbsentInputAudioBehaviorType,
    M2tsAribCaptionsPidControlType,
    M2tsAribType,
    M2tsAudioBufferModelType,
    M2tsAudioIntervalType,
    M2tsAudioStreamTypeType,
    M2tsBufferModelType,
    M2tsCcDescriptorType,
    M2tsEbifControlType,
    M2tsEbpPlacementType,
    M2tsEsRateInPesType,
    M2tsKlvType,
    M2tsNielsenId3BehaviorType,
    M2tsPcrControlType,
    M2tsRateModeType,
    M2tsScte35ControlType,
    M2tsSegmentationMarkersType,
    M2tsSegmentationStyleType,
    M2tsTimedMetadataBehaviorType,
    M3u8KlvBehaviorType,
    M3u8NielsenId3BehaviorType,
    M3u8PcrControlType,
    M3u8Scte35BehaviorType,
    M3u8TimedMetadataBehaviorType,
    MaintenanceDayType,
    MotionGraphicsInsertionType,
    Mp2CodingModeType,
    Mpeg2AdaptiveQuantizationType,
    Mpeg2ColorMetadataType,
    Mpeg2ColorSpaceType,
    Mpeg2DisplayRatioType,
    Mpeg2GopSizeUnitsType,
    Mpeg2ScanTypeType,
    Mpeg2SubGopLengthType,
    Mpeg2TimecodeInsertionBehaviorType,
    MsSmoothH265PackagingTypeType,
    MultiplexStateType,
    NetworkInputServerValidationType,
    NielsenPcmToId3TaggingStateType,
    NielsenWatermarksCbetStepasideType,
    NielsenWatermarksDistributionTypesType,
    NielsenWatermarkTimezonesType,
    PipelineIdType,
    PreferredChannelPipelineType,
    RebootInputDeviceForceType,
    ReservationAutomaticRenewalType,
    ReservationCodecType,
    ReservationMaximumBitrateType,
    ReservationMaximumFramerateType,
    ReservationResolutionType,
    ReservationResourceTypeType,
    ReservationSpecialFeatureType,
    ReservationStateType,
    ReservationVideoQualityType,
    RtmpCacheFullBehaviorType,
    RtmpCaptionDataType,
    RtmpOutputCertificateModeType,
    S3CannedAclType,
    Scte20Convert608To708Type,
    Scte27OcrLanguageType,
    Scte35AposNoRegionalBlackoutBehaviorType,
    Scte35AposWebDeliveryAllowedBehaviorType,
    Scte35ArchiveAllowedFlagType,
    Scte35DeviceRestrictionsType,
    Scte35InputModeType,
    Scte35NoRegionalBlackoutFlagType,
    Scte35SegmentationCancelIndicatorType,
    Scte35SegmentationScopeType,
    Scte35SpliceInsertNoRegionalBlackoutBehaviorType,
    Scte35SpliceInsertWebDeliveryAllowedBehaviorType,
    Scte35TypeType,
    Scte35WebDeliveryAllowedFlagType,
    SignalMapMonitorDeploymentStatusType,
    SignalMapStatusType,
    SmoothGroupAudioOnlyTimecodeControlType,
    SmoothGroupCertificateModeType,
    SmoothGroupEventIdModeType,
    SmoothGroupEventStopBehaviorType,
    SmoothGroupSegmentationModeType,
    SmoothGroupSparseTrackTypeType,
    SmoothGroupStreamManifestBehaviorType,
    SmoothGroupTimestampOffsetModeType,
    Smpte2038DataPreferenceType,
    TemporalFilterPostFilterSharpeningType,
    TemporalFilterStrengthType,
    ThumbnailStateType,
    ThumbnailTypeType,
    TimecodeBurninFontSizeType,
    TimecodeBurninPositionType,
    TimecodeConfigSourceType,
    TtmlDestinationStyleControlType,
    UdpTimedMetadataId3FrameType,
    VideoDescriptionRespondToAfdType,
    VideoDescriptionScalingBehaviorType,
    VideoSelectorColorSpaceType,
    VideoSelectorColorSpaceUsageType,
    WavCodingModeType,
    WebvttDestinationStyleControlType,
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
    "AacSettingsTypeDef",
    "Ac3SettingsTypeDef",
    "AcceptInputDeviceTransferRequestRequestTypeDef",
    "AccountConfigurationTypeDef",
    "AncillarySourceSettingsTypeDef",
    "ArchiveS3SettingsTypeDef",
    "OutputLocationRefTypeDef",
    "InputChannelLevelTypeDef",
    "Eac3AtmosSettingsTypeDef",
    "Eac3SettingsTypeDef",
    "Mp2SettingsTypeDef",
    "WavSettingsTypeDef",
    "AudioNormalizationSettingsTypeDef",
    "AudioDolbyEDecodeTypeDef",
    "AudioHlsRenditionSelectionTypeDef",
    "AudioLanguageSelectionTypeDef",
    "InputLocationTypeDef",
    "AudioPidSelectionTypeDef",
    "AudioSilenceFailoverSettingsTypeDef",
    "AudioTrackTypeDef",
    "EsamTypeDef",
    "Scte35SpliceInsertTypeDef",
    "Scte35TimeSignalAposTypeDef",
    "BatchDeleteRequestRequestTypeDef",
    "BatchFailedResultModelTypeDef",
    "BatchSuccessfulResultModelTypeDef",
    "ResponseMetadataTypeDef",
    "BatchScheduleActionDeleteRequestTypeDef",
    "BatchStartRequestRequestTypeDef",
    "BatchStopRequestRequestTypeDef",
    "CancelInputDeviceTransferRequestRequestTypeDef",
    "EbuTtDDestinationSettingsTypeDef",
    "TtmlDestinationSettingsTypeDef",
    "WebvttDestinationSettingsTypeDef",
    "CaptionLanguageMappingTypeDef",
    "CaptionRectangleTypeDef",
    "DvbSubSourceSettingsTypeDef",
    "EmbeddedSourceSettingsTypeDef",
    "Scte20SourceSettingsTypeDef",
    "Scte27SourceSettingsTypeDef",
    "CdiInputSpecificationTypeDef",
    "ChannelEgressEndpointTypeDef",
    "InputSpecificationTypeDef",
    "MaintenanceStatusTypeDef",
    "VpcOutputSettingsDescriptionTypeDef",
    "PipelineDetailTypeDef",
    "ClaimDeviceRequestRequestTypeDef",
    "CloudWatchAlarmTemplateGroupSummaryTypeDef",
    "CloudWatchAlarmTemplateSummaryTypeDef",
    "CmafIngestOutputSettingsTypeDef",
    "ColorCorrectionTypeDef",
    "MaintenanceCreateSettingsTypeDef",
    "VpcOutputSettingsTypeDef",
    "CreateCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    "CreateCloudWatchAlarmTemplateRequestRequestTypeDef",
    "CreateEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    "EventBridgeRuleTemplateTargetTypeDef",
    "InputDestinationRequestTypeDef",
    "InputDeviceSettingsTypeDef",
    "InputSourceRequestTypeDef",
    "InputVpcRequestTypeDef",
    "MediaConnectFlowRequestTypeDef",
    "InputWhitelistRuleCidrTypeDef",
    "MultiplexSettingsTypeDef",
    "CreatePartnerInputRequestRequestTypeDef",
    "CreateSignalMapRequestRequestTypeDef",
    "MonitorDeploymentTypeDef",
    "SuccessfulMonitorDeploymentTypeDef",
    "CreateTagsRequestRequestTypeDef",
    "DeleteChannelRequestRequestTypeDef",
    "DeleteCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    "DeleteCloudWatchAlarmTemplateRequestRequestTypeDef",
    "DeleteEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    "DeleteEventBridgeRuleTemplateRequestRequestTypeDef",
    "DeleteInputRequestRequestTypeDef",
    "DeleteInputSecurityGroupRequestRequestTypeDef",
    "DeleteMultiplexProgramRequestRequestTypeDef",
    "MultiplexProgramPacketIdentifiersMapTypeDef",
    "MultiplexProgramPipelineDetailTypeDef",
    "DeleteMultiplexRequestRequestTypeDef",
    "DeleteReservationRequestRequestTypeDef",
    "RenewalSettingsTypeDef",
    "ReservationResourceSpecificationTypeDef",
    "DeleteScheduleRequestRequestTypeDef",
    "DeleteSignalMapRequestRequestTypeDef",
    "DeleteTagsRequestRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeChannelRequestRequestTypeDef",
    "DescribeInputDeviceRequestRequestTypeDef",
    "InputDeviceHdSettingsTypeDef",
    "InputDeviceNetworkSettingsTypeDef",
    "DescribeInputDeviceThumbnailRequestRequestTypeDef",
    "DescribeInputRequestRequestTypeDef",
    "InputSourceTypeDef",
    "MediaConnectFlowTypeDef",
    "DescribeInputSecurityGroupRequestRequestTypeDef",
    "InputWhitelistRuleTypeDef",
    "DescribeMultiplexProgramRequestRequestTypeDef",
    "DescribeMultiplexRequestRequestTypeDef",
    "DescribeOfferingRequestRequestTypeDef",
    "DescribeReservationRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeScheduleRequestRequestTypeDef",
    "DescribeThumbnailsRequestRequestTypeDef",
    "DvbNitSettingsTypeDef",
    "DvbSdtSettingsTypeDef",
    "DvbTdtSettingsTypeDef",
    "FeatureActivationsTypeDef",
    "NielsenConfigurationTypeDef",
    "ThumbnailConfigurationTypeDef",
    "TimecodeConfigTypeDef",
    "EpochLockingSettingsTypeDef",
    "EventBridgeRuleTemplateGroupSummaryTypeDef",
    "EventBridgeRuleTemplateSummaryTypeDef",
    "InputLossFailoverSettingsTypeDef",
    "VideoBlackFailoverSettingsTypeDef",
    "FecOutputSettingsTypeDef",
    "FixedModeScheduleActionStartSettingsTypeDef",
    "Fmp4HlsSettingsTypeDef",
    "FollowModeScheduleActionStartSettingsTypeDef",
    "FrameCaptureS3SettingsTypeDef",
    "FrameCaptureOutputSettingsTypeDef",
    "TimecodeBurninSettingsTypeDef",
    "GetCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    "GetCloudWatchAlarmTemplateRequestRequestTypeDef",
    "GetEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    "GetEventBridgeRuleTemplateRequestRequestTypeDef",
    "GetSignalMapRequestRequestTypeDef",
    "H264ColorSpaceSettingsOutputTypeDef",
    "H264ColorSpaceSettingsTypeDef",
    "TemporalFilterSettingsTypeDef",
    "Hdr10SettingsTypeDef",
    "HlsAkamaiSettingsTypeDef",
    "HlsBasicPutSettingsTypeDef",
    "HlsMediaStoreSettingsTypeDef",
    "HlsS3SettingsTypeDef",
    "HlsWebdavSettingsTypeDef",
    "HlsId3SegmentTaggingScheduleActionSettingsTypeDef",
    "HlsInputSettingsTypeDef",
    "HlsTimedMetadataScheduleActionSettingsTypeDef",
    "StartTimecodeTypeDef",
    "StopTimecodeTypeDef",
    "InputDestinationVpcTypeDef",
    "InputDeviceConfigurableAudioChannelPairConfigTypeDef",
    "InputDeviceMediaConnectConfigurableSettingsTypeDef",
    "InputDeviceMediaConnectSettingsTypeDef",
    "InputDeviceRequestTypeDef",
    "InputDeviceUhdAudioChannelPairConfigTypeDef",
    "ListChannelsRequestRequestTypeDef",
    "ListCloudWatchAlarmTemplateGroupsRequestRequestTypeDef",
    "ListCloudWatchAlarmTemplatesRequestRequestTypeDef",
    "ListEventBridgeRuleTemplateGroupsRequestRequestTypeDef",
    "ListEventBridgeRuleTemplatesRequestRequestTypeDef",
    "ListInputDeviceTransfersRequestRequestTypeDef",
    "TransferringInputDeviceSummaryTypeDef",
    "ListInputDevicesRequestRequestTypeDef",
    "ListInputSecurityGroupsRequestRequestTypeDef",
    "ListInputsRequestRequestTypeDef",
    "ListMultiplexProgramsRequestRequestTypeDef",
    "MultiplexProgramSummaryTypeDef",
    "ListMultiplexesRequestRequestTypeDef",
    "ListOfferingsRequestRequestTypeDef",
    "ListReservationsRequestRequestTypeDef",
    "ListSignalMapsRequestRequestTypeDef",
    "SignalMapSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "M3u8SettingsTypeDef",
    "MaintenanceUpdateSettingsTypeDef",
    "MediaPackageOutputDestinationSettingsTypeDef",
    "MediaResourceNeighborTypeDef",
    "MotionGraphicsActivateScheduleActionSettingsTypeDef",
    "MotionGraphicsSettingsOutputTypeDef",
    "MotionGraphicsSettingsTypeDef",
    "MsSmoothOutputSettingsTypeDef",
    "MultiplexMediaConnectOutputDestinationSettingsTypeDef",
    "MultiplexProgramChannelDestinationSettingsTypeDef",
    "MultiplexProgramServiceDescriptorTypeDef",
    "MultiplexSettingsSummaryTypeDef",
    "MultiplexStatmuxVideoSettingsTypeDef",
    "NielsenCBETTypeDef",
    "NielsenNaesIiNwTypeDef",
    "OutputDestinationSettingsTypeDef",
    "RtmpGroupSettingsOutputTypeDef",
    "UdpGroupSettingsTypeDef",
    "RtmpGroupSettingsTypeDef",
    "PipelinePauseStateSettingsTypeDef",
    "RebootInputDeviceRequestRequestTypeDef",
    "RejectInputDeviceTransferRequestRequestTypeDef",
    "RestartChannelPipelinesRequestRequestTypeDef",
    "Scte35InputScheduleActionSettingsTypeDef",
    "Scte35ReturnToNetworkScheduleActionSettingsTypeDef",
    "Scte35SpliceInsertScheduleActionSettingsTypeDef",
    "StaticImageDeactivateScheduleActionSettingsTypeDef",
    "StaticImageOutputDeactivateScheduleActionSettingsExtraOutputTypeDef",
    "StaticImageOutputDeactivateScheduleActionSettingsOutputTypeDef",
    "StaticImageOutputDeactivateScheduleActionSettingsTypeDef",
    "Scte35DeliveryRestrictionsTypeDef",
    "SrtCallerDecryptionRequestTypeDef",
    "SrtCallerDecryptionTypeDef",
    "StartChannelRequestRequestTypeDef",
    "StartDeleteMonitorDeploymentRequestRequestTypeDef",
    "StartInputDeviceMaintenanceWindowRequestRequestTypeDef",
    "StartInputDeviceRequestRequestTypeDef",
    "StartMonitorDeploymentRequestRequestTypeDef",
    "StartMultiplexRequestRequestTypeDef",
    "StartUpdateSignalMapRequestRequestTypeDef",
    "StopChannelRequestRequestTypeDef",
    "StopInputDeviceRequestRequestTypeDef",
    "StopMultiplexRequestRequestTypeDef",
    "ThumbnailTypeDef",
    "TransferInputDeviceRequestRequestTypeDef",
    "UpdateCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    "UpdateCloudWatchAlarmTemplateRequestRequestTypeDef",
    "UpdateEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    "VideoSelectorPidTypeDef",
    "VideoSelectorProgramIdTypeDef",
    "UpdateAccountConfigurationRequestRequestTypeDef",
    "ArchiveCdnSettingsTypeDef",
    "CmafIngestGroupSettingsTypeDef",
    "MediaPackageGroupSettingsTypeDef",
    "MsSmoothGroupSettingsTypeDef",
    "MultiplexOutputSettingsTypeDef",
    "RtmpOutputSettingsTypeDef",
    "AudioChannelMappingOutputTypeDef",
    "AudioChannelMappingTypeDef",
    "AudioCodecSettingsOutputTypeDef",
    "AudioCodecSettingsTypeDef",
    "AudioOnlyHlsSettingsTypeDef",
    "AvailBlankingTypeDef",
    "BlackoutSlateTypeDef",
    "BurnInDestinationSettingsTypeDef",
    "DvbSubDestinationSettingsTypeDef",
    "InputLossBehaviorTypeDef",
    "StaticImageActivateScheduleActionSettingsTypeDef",
    "StaticImageOutputActivateScheduleActionSettingsExtraOutputTypeDef",
    "StaticImageOutputActivateScheduleActionSettingsOutputTypeDef",
    "StaticImageOutputActivateScheduleActionSettingsTypeDef",
    "StaticKeySettingsTypeDef",
    "AudioTrackSelectionExtraOutputTypeDef",
    "AudioTrackSelectionOutputTypeDef",
    "AudioTrackSelectionTypeDef",
    "AvailSettingsTypeDef",
    "BatchDeleteResponseTypeDef",
    "BatchStartResponseTypeDef",
    "BatchStopResponseTypeDef",
    "CreateCloudWatchAlarmTemplateGroupResponseTypeDef",
    "CreateCloudWatchAlarmTemplateResponseTypeDef",
    "CreateEventBridgeRuleTemplateGroupResponseTypeDef",
    "DescribeAccountConfigurationResponseTypeDef",
    "DescribeInputDeviceThumbnailResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetCloudWatchAlarmTemplateGroupResponseTypeDef",
    "GetCloudWatchAlarmTemplateResponseTypeDef",
    "GetEventBridgeRuleTemplateGroupResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "UpdateAccountConfigurationResponseTypeDef",
    "UpdateCloudWatchAlarmTemplateGroupResponseTypeDef",
    "UpdateCloudWatchAlarmTemplateResponseTypeDef",
    "UpdateEventBridgeRuleTemplateGroupResponseTypeDef",
    "TeletextSourceSettingsTypeDef",
    "ListCloudWatchAlarmTemplateGroupsResponseTypeDef",
    "ListCloudWatchAlarmTemplatesResponseTypeDef",
    "ColorCorrectionSettingsOutputTypeDef",
    "ColorCorrectionSettingsTypeDef",
    "CreateEventBridgeRuleTemplateRequestRequestTypeDef",
    "CreateEventBridgeRuleTemplateResponseTypeDef",
    "GetEventBridgeRuleTemplateResponseTypeDef",
    "UpdateEventBridgeRuleTemplateRequestRequestTypeDef",
    "UpdateEventBridgeRuleTemplateResponseTypeDef",
    "CreateInputSecurityGroupRequestRequestTypeDef",
    "UpdateInputSecurityGroupRequestRequestTypeDef",
    "CreateMultiplexRequestRequestTypeDef",
    "UpdateMultiplexRequestRequestTypeDef",
    "PurchaseOfferingRequestRequestTypeDef",
    "UpdateReservationRequestRequestTypeDef",
    "DeleteReservationResponseTypeDef",
    "DescribeOfferingResponseTypeDef",
    "DescribeReservationResponseTypeDef",
    "OfferingTypeDef",
    "ReservationTypeDef",
    "DescribeChannelRequestChannelCreatedWaitTypeDef",
    "DescribeChannelRequestChannelDeletedWaitTypeDef",
    "DescribeChannelRequestChannelRunningWaitTypeDef",
    "DescribeChannelRequestChannelStoppedWaitTypeDef",
    "DescribeInputRequestInputAttachedWaitTypeDef",
    "DescribeInputRequestInputDeletedWaitTypeDef",
    "DescribeInputRequestInputDetachedWaitTypeDef",
    "DescribeMultiplexRequestMultiplexCreatedWaitTypeDef",
    "DescribeMultiplexRequestMultiplexDeletedWaitTypeDef",
    "DescribeMultiplexRequestMultiplexRunningWaitTypeDef",
    "DescribeMultiplexRequestMultiplexStoppedWaitTypeDef",
    "GetSignalMapRequestSignalMapCreatedWaitTypeDef",
    "GetSignalMapRequestSignalMapMonitorDeletedWaitTypeDef",
    "GetSignalMapRequestSignalMapMonitorDeployedWaitTypeDef",
    "GetSignalMapRequestSignalMapUpdatedWaitTypeDef",
    "DescribeInputSecurityGroupResponseTypeDef",
    "InputSecurityGroupTypeDef",
    "DescribeScheduleRequestDescribeSchedulePaginateTypeDef",
    "ListChannelsRequestListChannelsPaginateTypeDef",
    "ListCloudWatchAlarmTemplateGroupsRequestListCloudWatchAlarmTemplateGroupsPaginateTypeDef",
    "ListCloudWatchAlarmTemplatesRequestListCloudWatchAlarmTemplatesPaginateTypeDef",
    "ListEventBridgeRuleTemplateGroupsRequestListEventBridgeRuleTemplateGroupsPaginateTypeDef",
    "ListEventBridgeRuleTemplatesRequestListEventBridgeRuleTemplatesPaginateTypeDef",
    "ListInputDeviceTransfersRequestListInputDeviceTransfersPaginateTypeDef",
    "ListInputDevicesRequestListInputDevicesPaginateTypeDef",
    "ListInputSecurityGroupsRequestListInputSecurityGroupsPaginateTypeDef",
    "ListInputsRequestListInputsPaginateTypeDef",
    "ListMultiplexProgramsRequestListMultiplexProgramsPaginateTypeDef",
    "ListMultiplexesRequestListMultiplexesPaginateTypeDef",
    "ListOfferingsRequestListOfferingsPaginateTypeDef",
    "ListReservationsRequestListReservationsPaginateTypeDef",
    "ListSignalMapsRequestListSignalMapsPaginateTypeDef",
    "M2tsSettingsTypeDef",
    "OutputLockingSettingsOutputTypeDef",
    "OutputLockingSettingsTypeDef",
    "ListEventBridgeRuleTemplateGroupsResponseTypeDef",
    "ListEventBridgeRuleTemplatesResponseTypeDef",
    "FailoverConditionSettingsTypeDef",
    "ScheduleActionStartSettingsExtraOutputTypeDef",
    "ScheduleActionStartSettingsOutputTypeDef",
    "ScheduleActionStartSettingsTypeDef",
    "FrameCaptureCdnSettingsTypeDef",
    "FrameCaptureSettingsTypeDef",
    "H264FilterSettingsTypeDef",
    "H265FilterSettingsTypeDef",
    "Mpeg2FilterSettingsTypeDef",
    "H265ColorSpaceSettingsOutputTypeDef",
    "H265ColorSpaceSettingsTypeDef",
    "VideoSelectorColorSpaceSettingsTypeDef",
    "HlsCdnSettingsTypeDef",
    "NetworkInputSettingsTypeDef",
    "InputClippingSettingsTypeDef",
    "InputDestinationTypeDef",
    "InputDeviceConfigurableSettingsTypeDef",
    "InputDeviceUhdSettingsTypeDef",
    "ListInputDeviceTransfersResponseTypeDef",
    "ListMultiplexProgramsResponseTypeDef",
    "ListSignalMapsResponseTypeDef",
    "StandardHlsSettingsTypeDef",
    "MediaResourceTypeDef",
    "MotionGraphicsConfigurationOutputTypeDef",
    "MotionGraphicsConfigurationTypeDef",
    "MultiplexOutputDestinationTypeDef",
    "MultiplexSummaryTypeDef",
    "MultiplexVideoSettingsTypeDef",
    "NielsenWatermarksSettingsTypeDef",
    "OutputDestinationExtraOutputTypeDef",
    "OutputDestinationOutputTypeDef",
    "OutputDestinationTypeDef",
    "PauseStateScheduleActionSettingsExtraOutputTypeDef",
    "PauseStateScheduleActionSettingsOutputTypeDef",
    "PauseStateScheduleActionSettingsTypeDef",
    "Scte35SegmentationDescriptorTypeDef",
    "SrtCallerSourceRequestTypeDef",
    "SrtCallerSourceTypeDef",
    "ThumbnailDetailTypeDef",
    "VideoSelectorSettingsTypeDef",
    "ArchiveGroupSettingsTypeDef",
    "RemixSettingsOutputTypeDef",
    "RemixSettingsTypeDef",
    "CaptionDestinationSettingsOutputTypeDef",
    "CaptionDestinationSettingsTypeDef",
    "KeyProviderSettingsTypeDef",
    "AudioSelectorSettingsExtraOutputTypeDef",
    "AudioSelectorSettingsOutputTypeDef",
    "AudioSelectorSettingsTypeDef",
    "AvailConfigurationTypeDef",
    "CaptionSelectorSettingsExtraOutputTypeDef",
    "CaptionSelectorSettingsOutputTypeDef",
    "CaptionSelectorSettingsTypeDef",
    "ListOfferingsResponseTypeDef",
    "ListReservationsResponseTypeDef",
    "PurchaseOfferingResponseTypeDef",
    "UpdateReservationResponseTypeDef",
    "CreateInputSecurityGroupResponseTypeDef",
    "ListInputSecurityGroupsResponseTypeDef",
    "UpdateInputSecurityGroupResponseTypeDef",
    "ArchiveContainerSettingsTypeDef",
    "UdpContainerSettingsTypeDef",
    "GlobalConfigurationOutputTypeDef",
    "GlobalConfigurationTypeDef",
    "FailoverConditionTypeDef",
    "FrameCaptureGroupSettingsTypeDef",
    "H264SettingsOutputTypeDef",
    "H264SettingsTypeDef",
    "Mpeg2SettingsTypeDef",
    "H265SettingsOutputTypeDef",
    "H265SettingsTypeDef",
    "InputPrepareScheduleActionSettingsExtraOutputTypeDef",
    "InputPrepareScheduleActionSettingsOutputTypeDef",
    "InputPrepareScheduleActionSettingsTypeDef",
    "InputSwitchScheduleActionSettingsExtraOutputTypeDef",
    "InputSwitchScheduleActionSettingsOutputTypeDef",
    "InputSwitchScheduleActionSettingsTypeDef",
    "UpdateInputDeviceRequestRequestTypeDef",
    "DescribeInputDeviceResponseTypeDef",
    "InputDeviceSummaryTypeDef",
    "UpdateInputDeviceResponseTypeDef",
    "HlsSettingsTypeDef",
    "CreateSignalMapResponseTypeDef",
    "GetSignalMapResponseTypeDef",
    "StartDeleteMonitorDeploymentResponseTypeDef",
    "StartMonitorDeploymentResponseTypeDef",
    "StartUpdateSignalMapResponseTypeDef",
    "DeleteMultiplexResponseTypeDef",
    "DescribeMultiplexResponseTypeDef",
    "MultiplexTypeDef",
    "StartMultiplexResponseTypeDef",
    "StopMultiplexResponseTypeDef",
    "ListMultiplexesResponseTypeDef",
    "MultiplexProgramSettingsTypeDef",
    "AudioWatermarkSettingsTypeDef",
    "OutputDestinationUnionTypeDef",
    "Scte35DescriptorSettingsTypeDef",
    "SrtSettingsRequestTypeDef",
    "SrtSettingsTypeDef",
    "DescribeThumbnailsResponseTypeDef",
    "VideoSelectorTypeDef",
    "CaptionDescriptionOutputTypeDef",
    "CaptionDescriptionTypeDef",
    "HlsGroupSettingsOutputTypeDef",
    "HlsGroupSettingsTypeDef",
    "AudioSelectorExtraOutputTypeDef",
    "AudioSelectorOutputTypeDef",
    "AudioSelectorTypeDef",
    "CaptionSelectorExtraOutputTypeDef",
    "CaptionSelectorOutputTypeDef",
    "CaptionSelectorTypeDef",
    "ArchiveOutputSettingsTypeDef",
    "UdpOutputSettingsTypeDef",
    "AutomaticInputFailoverSettingsExtraOutputTypeDef",
    "AutomaticInputFailoverSettingsOutputTypeDef",
    "AutomaticInputFailoverSettingsTypeDef",
    "VideoCodecSettingsOutputTypeDef",
    "VideoCodecSettingsTypeDef",
    "ListInputDevicesResponseTypeDef",
    "HlsOutputSettingsTypeDef",
    "CreateMultiplexResponseTypeDef",
    "UpdateMultiplexResponseTypeDef",
    "CreateMultiplexProgramRequestRequestTypeDef",
    "DeleteMultiplexProgramResponseTypeDef",
    "DescribeMultiplexProgramResponseTypeDef",
    "MultiplexProgramTypeDef",
    "UpdateMultiplexProgramRequestRequestTypeDef",
    "AudioDescriptionOutputTypeDef",
    "AudioDescriptionTypeDef",
    "UpdateChannelClassRequestRequestTypeDef",
    "Scte35DescriptorTypeDef",
    "CreateInputRequestRequestTypeDef",
    "UpdateInputRequestRequestTypeDef",
    "DescribeInputResponseTypeDef",
    "InputTypeDef",
    "OutputGroupSettingsOutputTypeDef",
    "OutputGroupSettingsTypeDef",
    "InputSettingsExtraOutputTypeDef",
    "InputSettingsOutputTypeDef",
    "InputSettingsTypeDef",
    "VideoDescriptionOutputTypeDef",
    "VideoDescriptionTypeDef",
    "OutputSettingsTypeDef",
    "CreateMultiplexProgramResponseTypeDef",
    "UpdateMultiplexProgramResponseTypeDef",
    "Scte35TimeSignalScheduleActionSettingsExtraOutputTypeDef",
    "Scte35TimeSignalScheduleActionSettingsOutputTypeDef",
    "Scte35TimeSignalScheduleActionSettingsTypeDef",
    "CreateInputResponseTypeDef",
    "CreatePartnerInputResponseTypeDef",
    "ListInputsResponseTypeDef",
    "UpdateInputResponseTypeDef",
    "InputAttachmentExtraOutputTypeDef",
    "InputAttachmentOutputTypeDef",
    "InputAttachmentTypeDef",
    "OutputTypeDef",
    "ScheduleActionSettingsExtraOutputTypeDef",
    "ScheduleActionSettingsOutputTypeDef",
    "ScheduleActionSettingsTypeDef",
    "ChannelSummaryTypeDef",
    "InputAttachmentUnionTypeDef",
    "OutputGroupOutputTypeDef",
    "OutputGroupTypeDef",
    "ScheduleActionExtraOutputTypeDef",
    "ScheduleActionOutputTypeDef",
    "ScheduleActionTypeDef",
    "ListChannelsResponseTypeDef",
    "EncoderSettingsOutputTypeDef",
    "EncoderSettingsTypeDef",
    "BatchScheduleActionCreateResultTypeDef",
    "BatchScheduleActionDeleteResultTypeDef",
    "DescribeScheduleResponseTypeDef",
    "BatchScheduleActionCreateRequestTypeDef",
    "ChannelTypeDef",
    "DeleteChannelResponseTypeDef",
    "DescribeChannelResponseTypeDef",
    "RestartChannelPipelinesResponseTypeDef",
    "StartChannelResponseTypeDef",
    "StopChannelResponseTypeDef",
    "CreateChannelRequestRequestTypeDef",
    "EncoderSettingsUnionTypeDef",
    "UpdateChannelRequestRequestTypeDef",
    "BatchUpdateScheduleResponseTypeDef",
    "BatchUpdateScheduleRequestRequestTypeDef",
    "CreateChannelResponseTypeDef",
    "UpdateChannelClassResponseTypeDef",
    "UpdateChannelResponseTypeDef",
)

AacSettingsTypeDef = TypedDict(
    "AacSettingsTypeDef",
    {
        "Bitrate": NotRequired[float],
        "CodingMode": NotRequired[AacCodingModeType],
        "InputType": NotRequired[AacInputTypeType],
        "Profile": NotRequired[AacProfileType],
        "RateControlMode": NotRequired[AacRateControlModeType],
        "RawFormat": NotRequired[AacRawFormatType],
        "SampleRate": NotRequired[float],
        "Spec": NotRequired[AacSpecType],
        "VbrQuality": NotRequired[AacVbrQualityType],
    },
)
Ac3SettingsTypeDef = TypedDict(
    "Ac3SettingsTypeDef",
    {
        "Bitrate": NotRequired[float],
        "BitstreamMode": NotRequired[Ac3BitstreamModeType],
        "CodingMode": NotRequired[Ac3CodingModeType],
        "Dialnorm": NotRequired[int],
        "DrcProfile": NotRequired[Ac3DrcProfileType],
        "LfeFilter": NotRequired[Ac3LfeFilterType],
        "MetadataControl": NotRequired[Ac3MetadataControlType],
        "AttenuationControl": NotRequired[Ac3AttenuationControlType],
    },
)
AcceptInputDeviceTransferRequestRequestTypeDef = TypedDict(
    "AcceptInputDeviceTransferRequestRequestTypeDef",
    {
        "InputDeviceId": str,
    },
)
AccountConfigurationTypeDef = TypedDict(
    "AccountConfigurationTypeDef",
    {
        "KmsKeyId": NotRequired[str],
    },
)
AncillarySourceSettingsTypeDef = TypedDict(
    "AncillarySourceSettingsTypeDef",
    {
        "SourceAncillaryChannelNumber": NotRequired[int],
    },
)
ArchiveS3SettingsTypeDef = TypedDict(
    "ArchiveS3SettingsTypeDef",
    {
        "CannedAcl": NotRequired[S3CannedAclType],
    },
)
OutputLocationRefTypeDef = TypedDict(
    "OutputLocationRefTypeDef",
    {
        "DestinationRefId": NotRequired[str],
    },
)
InputChannelLevelTypeDef = TypedDict(
    "InputChannelLevelTypeDef",
    {
        "Gain": int,
        "InputChannel": int,
    },
)
Eac3AtmosSettingsTypeDef = TypedDict(
    "Eac3AtmosSettingsTypeDef",
    {
        "Bitrate": NotRequired[float],
        "CodingMode": NotRequired[Eac3AtmosCodingModeType],
        "Dialnorm": NotRequired[int],
        "DrcLine": NotRequired[Eac3AtmosDrcLineType],
        "DrcRf": NotRequired[Eac3AtmosDrcRfType],
        "HeightTrim": NotRequired[float],
        "SurroundTrim": NotRequired[float],
    },
)
Eac3SettingsTypeDef = TypedDict(
    "Eac3SettingsTypeDef",
    {
        "AttenuationControl": NotRequired[Eac3AttenuationControlType],
        "Bitrate": NotRequired[float],
        "BitstreamMode": NotRequired[Eac3BitstreamModeType],
        "CodingMode": NotRequired[Eac3CodingModeType],
        "DcFilter": NotRequired[Eac3DcFilterType],
        "Dialnorm": NotRequired[int],
        "DrcLine": NotRequired[Eac3DrcLineType],
        "DrcRf": NotRequired[Eac3DrcRfType],
        "LfeControl": NotRequired[Eac3LfeControlType],
        "LfeFilter": NotRequired[Eac3LfeFilterType],
        "LoRoCenterMixLevel": NotRequired[float],
        "LoRoSurroundMixLevel": NotRequired[float],
        "LtRtCenterMixLevel": NotRequired[float],
        "LtRtSurroundMixLevel": NotRequired[float],
        "MetadataControl": NotRequired[Eac3MetadataControlType],
        "PassthroughControl": NotRequired[Eac3PassthroughControlType],
        "PhaseControl": NotRequired[Eac3PhaseControlType],
        "StereoDownmix": NotRequired[Eac3StereoDownmixType],
        "SurroundExMode": NotRequired[Eac3SurroundExModeType],
        "SurroundMode": NotRequired[Eac3SurroundModeType],
    },
)
Mp2SettingsTypeDef = TypedDict(
    "Mp2SettingsTypeDef",
    {
        "Bitrate": NotRequired[float],
        "CodingMode": NotRequired[Mp2CodingModeType],
        "SampleRate": NotRequired[float],
    },
)
WavSettingsTypeDef = TypedDict(
    "WavSettingsTypeDef",
    {
        "BitDepth": NotRequired[float],
        "CodingMode": NotRequired[WavCodingModeType],
        "SampleRate": NotRequired[float],
    },
)
AudioNormalizationSettingsTypeDef = TypedDict(
    "AudioNormalizationSettingsTypeDef",
    {
        "Algorithm": NotRequired[AudioNormalizationAlgorithmType],
        "AlgorithmControl": NotRequired[Literal["CORRECT_AUDIO"]],
        "TargetLkfs": NotRequired[float],
    },
)
AudioDolbyEDecodeTypeDef = TypedDict(
    "AudioDolbyEDecodeTypeDef",
    {
        "ProgramSelection": DolbyEProgramSelectionType,
    },
)
AudioHlsRenditionSelectionTypeDef = TypedDict(
    "AudioHlsRenditionSelectionTypeDef",
    {
        "GroupId": str,
        "Name": str,
    },
)
AudioLanguageSelectionTypeDef = TypedDict(
    "AudioLanguageSelectionTypeDef",
    {
        "LanguageCode": str,
        "LanguageSelectionPolicy": NotRequired[AudioLanguageSelectionPolicyType],
    },
)
InputLocationTypeDef = TypedDict(
    "InputLocationTypeDef",
    {
        "Uri": str,
        "PasswordParam": NotRequired[str],
        "Username": NotRequired[str],
    },
)
AudioPidSelectionTypeDef = TypedDict(
    "AudioPidSelectionTypeDef",
    {
        "Pid": int,
    },
)
AudioSilenceFailoverSettingsTypeDef = TypedDict(
    "AudioSilenceFailoverSettingsTypeDef",
    {
        "AudioSelectorName": str,
        "AudioSilenceThresholdMsec": NotRequired[int],
    },
)
AudioTrackTypeDef = TypedDict(
    "AudioTrackTypeDef",
    {
        "Track": int,
    },
)
EsamTypeDef = TypedDict(
    "EsamTypeDef",
    {
        "AcquisitionPointId": str,
        "PoisEndpoint": str,
        "AdAvailOffset": NotRequired[int],
        "PasswordParam": NotRequired[str],
        "Username": NotRequired[str],
        "ZoneIdentity": NotRequired[str],
    },
)
Scte35SpliceInsertTypeDef = TypedDict(
    "Scte35SpliceInsertTypeDef",
    {
        "AdAvailOffset": NotRequired[int],
        "NoRegionalBlackoutFlag": NotRequired[Scte35SpliceInsertNoRegionalBlackoutBehaviorType],
        "WebDeliveryAllowedFlag": NotRequired[Scte35SpliceInsertWebDeliveryAllowedBehaviorType],
    },
)
Scte35TimeSignalAposTypeDef = TypedDict(
    "Scte35TimeSignalAposTypeDef",
    {
        "AdAvailOffset": NotRequired[int],
        "NoRegionalBlackoutFlag": NotRequired[Scte35AposNoRegionalBlackoutBehaviorType],
        "WebDeliveryAllowedFlag": NotRequired[Scte35AposWebDeliveryAllowedBehaviorType],
    },
)
BatchDeleteRequestRequestTypeDef = TypedDict(
    "BatchDeleteRequestRequestTypeDef",
    {
        "ChannelIds": NotRequired[Sequence[str]],
        "InputIds": NotRequired[Sequence[str]],
        "InputSecurityGroupIds": NotRequired[Sequence[str]],
        "MultiplexIds": NotRequired[Sequence[str]],
    },
)
BatchFailedResultModelTypeDef = TypedDict(
    "BatchFailedResultModelTypeDef",
    {
        "Arn": NotRequired[str],
        "Code": NotRequired[str],
        "Id": NotRequired[str],
        "Message": NotRequired[str],
    },
)
BatchSuccessfulResultModelTypeDef = TypedDict(
    "BatchSuccessfulResultModelTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "State": NotRequired[str],
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
BatchScheduleActionDeleteRequestTypeDef = TypedDict(
    "BatchScheduleActionDeleteRequestTypeDef",
    {
        "ActionNames": Sequence[str],
    },
)
BatchStartRequestRequestTypeDef = TypedDict(
    "BatchStartRequestRequestTypeDef",
    {
        "ChannelIds": NotRequired[Sequence[str]],
        "MultiplexIds": NotRequired[Sequence[str]],
    },
)
BatchStopRequestRequestTypeDef = TypedDict(
    "BatchStopRequestRequestTypeDef",
    {
        "ChannelIds": NotRequired[Sequence[str]],
        "MultiplexIds": NotRequired[Sequence[str]],
    },
)
CancelInputDeviceTransferRequestRequestTypeDef = TypedDict(
    "CancelInputDeviceTransferRequestRequestTypeDef",
    {
        "InputDeviceId": str,
    },
)
EbuTtDDestinationSettingsTypeDef = TypedDict(
    "EbuTtDDestinationSettingsTypeDef",
    {
        "CopyrightHolder": NotRequired[str],
        "FillLineGap": NotRequired[EbuTtDFillLineGapControlType],
        "FontFamily": NotRequired[str],
        "StyleControl": NotRequired[EbuTtDDestinationStyleControlType],
    },
)
TtmlDestinationSettingsTypeDef = TypedDict(
    "TtmlDestinationSettingsTypeDef",
    {
        "StyleControl": NotRequired[TtmlDestinationStyleControlType],
    },
)
WebvttDestinationSettingsTypeDef = TypedDict(
    "WebvttDestinationSettingsTypeDef",
    {
        "StyleControl": NotRequired[WebvttDestinationStyleControlType],
    },
)
CaptionLanguageMappingTypeDef = TypedDict(
    "CaptionLanguageMappingTypeDef",
    {
        "CaptionChannel": int,
        "LanguageCode": str,
        "LanguageDescription": str,
    },
)
CaptionRectangleTypeDef = TypedDict(
    "CaptionRectangleTypeDef",
    {
        "Height": float,
        "LeftOffset": float,
        "TopOffset": float,
        "Width": float,
    },
)
DvbSubSourceSettingsTypeDef = TypedDict(
    "DvbSubSourceSettingsTypeDef",
    {
        "OcrLanguage": NotRequired[DvbSubOcrLanguageType],
        "Pid": NotRequired[int],
    },
)
EmbeddedSourceSettingsTypeDef = TypedDict(
    "EmbeddedSourceSettingsTypeDef",
    {
        "Convert608To708": NotRequired[EmbeddedConvert608To708Type],
        "Scte20Detection": NotRequired[EmbeddedScte20DetectionType],
        "Source608ChannelNumber": NotRequired[int],
        "Source608TrackNumber": NotRequired[int],
    },
)
Scte20SourceSettingsTypeDef = TypedDict(
    "Scte20SourceSettingsTypeDef",
    {
        "Convert608To708": NotRequired[Scte20Convert608To708Type],
        "Source608ChannelNumber": NotRequired[int],
    },
)
Scte27SourceSettingsTypeDef = TypedDict(
    "Scte27SourceSettingsTypeDef",
    {
        "OcrLanguage": NotRequired[Scte27OcrLanguageType],
        "Pid": NotRequired[int],
    },
)
CdiInputSpecificationTypeDef = TypedDict(
    "CdiInputSpecificationTypeDef",
    {
        "Resolution": NotRequired[CdiInputResolutionType],
    },
)
ChannelEgressEndpointTypeDef = TypedDict(
    "ChannelEgressEndpointTypeDef",
    {
        "SourceIp": NotRequired[str],
    },
)
InputSpecificationTypeDef = TypedDict(
    "InputSpecificationTypeDef",
    {
        "Codec": NotRequired[InputCodecType],
        "MaximumBitrate": NotRequired[InputMaximumBitrateType],
        "Resolution": NotRequired[InputResolutionType],
    },
)
MaintenanceStatusTypeDef = TypedDict(
    "MaintenanceStatusTypeDef",
    {
        "MaintenanceDay": NotRequired[MaintenanceDayType],
        "MaintenanceDeadline": NotRequired[str],
        "MaintenanceScheduledDate": NotRequired[str],
        "MaintenanceStartTime": NotRequired[str],
    },
)
VpcOutputSettingsDescriptionTypeDef = TypedDict(
    "VpcOutputSettingsDescriptionTypeDef",
    {
        "AvailabilityZones": NotRequired[List[str]],
        "NetworkInterfaceIds": NotRequired[List[str]],
        "SecurityGroupIds": NotRequired[List[str]],
        "SubnetIds": NotRequired[List[str]],
    },
)
PipelineDetailTypeDef = TypedDict(
    "PipelineDetailTypeDef",
    {
        "ActiveInputAttachmentName": NotRequired[str],
        "ActiveInputSwitchActionName": NotRequired[str],
        "ActiveMotionGraphicsActionName": NotRequired[str],
        "ActiveMotionGraphicsUri": NotRequired[str],
        "PipelineId": NotRequired[str],
    },
)
ClaimDeviceRequestRequestTypeDef = TypedDict(
    "ClaimDeviceRequestRequestTypeDef",
    {
        "Id": NotRequired[str],
    },
)
CloudWatchAlarmTemplateGroupSummaryTypeDef = TypedDict(
    "CloudWatchAlarmTemplateGroupSummaryTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Id": str,
        "Name": str,
        "TemplateCount": int,
        "Description": NotRequired[str],
        "ModifiedAt": NotRequired[datetime],
        "Tags": NotRequired[Dict[str, str]],
    },
)
CloudWatchAlarmTemplateSummaryTypeDef = TypedDict(
    "CloudWatchAlarmTemplateSummaryTypeDef",
    {
        "Arn": str,
        "ComparisonOperator": CloudWatchAlarmTemplateComparisonOperatorType,
        "CreatedAt": datetime,
        "EvaluationPeriods": int,
        "GroupId": str,
        "Id": str,
        "MetricName": str,
        "Name": str,
        "Period": int,
        "Statistic": CloudWatchAlarmTemplateStatisticType,
        "TargetResourceType": CloudWatchAlarmTemplateTargetResourceTypeType,
        "Threshold": float,
        "TreatMissingData": CloudWatchAlarmTemplateTreatMissingDataType,
        "DatapointsToAlarm": NotRequired[int],
        "Description": NotRequired[str],
        "ModifiedAt": NotRequired[datetime],
        "Tags": NotRequired[Dict[str, str]],
    },
)
CmafIngestOutputSettingsTypeDef = TypedDict(
    "CmafIngestOutputSettingsTypeDef",
    {
        "NameModifier": NotRequired[str],
    },
)
ColorCorrectionTypeDef = TypedDict(
    "ColorCorrectionTypeDef",
    {
        "InputColorSpace": ColorSpaceType,
        "OutputColorSpace": ColorSpaceType,
        "Uri": str,
    },
)
MaintenanceCreateSettingsTypeDef = TypedDict(
    "MaintenanceCreateSettingsTypeDef",
    {
        "MaintenanceDay": NotRequired[MaintenanceDayType],
        "MaintenanceStartTime": NotRequired[str],
    },
)
VpcOutputSettingsTypeDef = TypedDict(
    "VpcOutputSettingsTypeDef",
    {
        "SubnetIds": Sequence[str],
        "PublicAddressAllocationIds": NotRequired[Sequence[str]],
        "SecurityGroupIds": NotRequired[Sequence[str]],
    },
)
CreateCloudWatchAlarmTemplateGroupRequestRequestTypeDef = TypedDict(
    "CreateCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateCloudWatchAlarmTemplateRequestRequestTypeDef = TypedDict(
    "CreateCloudWatchAlarmTemplateRequestRequestTypeDef",
    {
        "ComparisonOperator": CloudWatchAlarmTemplateComparisonOperatorType,
        "EvaluationPeriods": int,
        "GroupIdentifier": str,
        "MetricName": str,
        "Name": str,
        "Period": int,
        "Statistic": CloudWatchAlarmTemplateStatisticType,
        "TargetResourceType": CloudWatchAlarmTemplateTargetResourceTypeType,
        "Threshold": float,
        "TreatMissingData": CloudWatchAlarmTemplateTreatMissingDataType,
        "DatapointsToAlarm": NotRequired[int],
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateEventBridgeRuleTemplateGroupRequestRequestTypeDef = TypedDict(
    "CreateEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    {
        "Name": str,
        "Description": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
EventBridgeRuleTemplateTargetTypeDef = TypedDict(
    "EventBridgeRuleTemplateTargetTypeDef",
    {
        "Arn": str,
    },
)
InputDestinationRequestTypeDef = TypedDict(
    "InputDestinationRequestTypeDef",
    {
        "StreamName": NotRequired[str],
    },
)
InputDeviceSettingsTypeDef = TypedDict(
    "InputDeviceSettingsTypeDef",
    {
        "Id": NotRequired[str],
    },
)
InputSourceRequestTypeDef = TypedDict(
    "InputSourceRequestTypeDef",
    {
        "PasswordParam": NotRequired[str],
        "Url": NotRequired[str],
        "Username": NotRequired[str],
    },
)
InputVpcRequestTypeDef = TypedDict(
    "InputVpcRequestTypeDef",
    {
        "SubnetIds": Sequence[str],
        "SecurityGroupIds": NotRequired[Sequence[str]],
    },
)
MediaConnectFlowRequestTypeDef = TypedDict(
    "MediaConnectFlowRequestTypeDef",
    {
        "FlowArn": NotRequired[str],
    },
)
InputWhitelistRuleCidrTypeDef = TypedDict(
    "InputWhitelistRuleCidrTypeDef",
    {
        "Cidr": NotRequired[str],
    },
)
MultiplexSettingsTypeDef = TypedDict(
    "MultiplexSettingsTypeDef",
    {
        "TransportStreamBitrate": int,
        "TransportStreamId": int,
        "MaximumVideoBufferDelayMilliseconds": NotRequired[int],
        "TransportStreamReservedBitrate": NotRequired[int],
    },
)
CreatePartnerInputRequestRequestTypeDef = TypedDict(
    "CreatePartnerInputRequestRequestTypeDef",
    {
        "InputId": str,
        "RequestId": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateSignalMapRequestRequestTypeDef = TypedDict(
    "CreateSignalMapRequestRequestTypeDef",
    {
        "DiscoveryEntryPointArn": str,
        "Name": str,
        "CloudWatchAlarmTemplateGroupIdentifiers": NotRequired[Sequence[str]],
        "Description": NotRequired[str],
        "EventBridgeRuleTemplateGroupIdentifiers": NotRequired[Sequence[str]],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
MonitorDeploymentTypeDef = TypedDict(
    "MonitorDeploymentTypeDef",
    {
        "Status": SignalMapMonitorDeploymentStatusType,
        "DetailsUri": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
SuccessfulMonitorDeploymentTypeDef = TypedDict(
    "SuccessfulMonitorDeploymentTypeDef",
    {
        "DetailsUri": str,
        "Status": SignalMapMonitorDeploymentStatusType,
    },
)
CreateTagsRequestRequestTypeDef = TypedDict(
    "CreateTagsRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": NotRequired[Mapping[str, str]],
    },
)
DeleteChannelRequestRequestTypeDef = TypedDict(
    "DeleteChannelRequestRequestTypeDef",
    {
        "ChannelId": str,
    },
)
DeleteCloudWatchAlarmTemplateGroupRequestRequestTypeDef = TypedDict(
    "DeleteCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
DeleteCloudWatchAlarmTemplateRequestRequestTypeDef = TypedDict(
    "DeleteCloudWatchAlarmTemplateRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
DeleteEventBridgeRuleTemplateGroupRequestRequestTypeDef = TypedDict(
    "DeleteEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
DeleteEventBridgeRuleTemplateRequestRequestTypeDef = TypedDict(
    "DeleteEventBridgeRuleTemplateRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
DeleteInputRequestRequestTypeDef = TypedDict(
    "DeleteInputRequestRequestTypeDef",
    {
        "InputId": str,
    },
)
DeleteInputSecurityGroupRequestRequestTypeDef = TypedDict(
    "DeleteInputSecurityGroupRequestRequestTypeDef",
    {
        "InputSecurityGroupId": str,
    },
)
DeleteMultiplexProgramRequestRequestTypeDef = TypedDict(
    "DeleteMultiplexProgramRequestRequestTypeDef",
    {
        "MultiplexId": str,
        "ProgramName": str,
    },
)
MultiplexProgramPacketIdentifiersMapTypeDef = TypedDict(
    "MultiplexProgramPacketIdentifiersMapTypeDef",
    {
        "AudioPids": NotRequired[List[int]],
        "DvbSubPids": NotRequired[List[int]],
        "DvbTeletextPid": NotRequired[int],
        "EtvPlatformPid": NotRequired[int],
        "EtvSignalPid": NotRequired[int],
        "KlvDataPids": NotRequired[List[int]],
        "PcrPid": NotRequired[int],
        "PmtPid": NotRequired[int],
        "PrivateMetadataPid": NotRequired[int],
        "Scte27Pids": NotRequired[List[int]],
        "Scte35Pid": NotRequired[int],
        "TimedMetadataPid": NotRequired[int],
        "VideoPid": NotRequired[int],
    },
)
MultiplexProgramPipelineDetailTypeDef = TypedDict(
    "MultiplexProgramPipelineDetailTypeDef",
    {
        "ActiveChannelPipeline": NotRequired[str],
        "PipelineId": NotRequired[str],
    },
)
DeleteMultiplexRequestRequestTypeDef = TypedDict(
    "DeleteMultiplexRequestRequestTypeDef",
    {
        "MultiplexId": str,
    },
)
DeleteReservationRequestRequestTypeDef = TypedDict(
    "DeleteReservationRequestRequestTypeDef",
    {
        "ReservationId": str,
    },
)
RenewalSettingsTypeDef = TypedDict(
    "RenewalSettingsTypeDef",
    {
        "AutomaticRenewal": NotRequired[ReservationAutomaticRenewalType],
        "RenewalCount": NotRequired[int],
    },
)
ReservationResourceSpecificationTypeDef = TypedDict(
    "ReservationResourceSpecificationTypeDef",
    {
        "ChannelClass": NotRequired[ChannelClassType],
        "Codec": NotRequired[ReservationCodecType],
        "MaximumBitrate": NotRequired[ReservationMaximumBitrateType],
        "MaximumFramerate": NotRequired[ReservationMaximumFramerateType],
        "Resolution": NotRequired[ReservationResolutionType],
        "ResourceType": NotRequired[ReservationResourceTypeType],
        "SpecialFeature": NotRequired[ReservationSpecialFeatureType],
        "VideoQuality": NotRequired[ReservationVideoQualityType],
    },
)
DeleteScheduleRequestRequestTypeDef = TypedDict(
    "DeleteScheduleRequestRequestTypeDef",
    {
        "ChannelId": str,
    },
)
DeleteSignalMapRequestRequestTypeDef = TypedDict(
    "DeleteSignalMapRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
DeleteTagsRequestRequestTypeDef = TypedDict(
    "DeleteTagsRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)
WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)
DescribeChannelRequestRequestTypeDef = TypedDict(
    "DescribeChannelRequestRequestTypeDef",
    {
        "ChannelId": str,
    },
)
DescribeInputDeviceRequestRequestTypeDef = TypedDict(
    "DescribeInputDeviceRequestRequestTypeDef",
    {
        "InputDeviceId": str,
    },
)
InputDeviceHdSettingsTypeDef = TypedDict(
    "InputDeviceHdSettingsTypeDef",
    {
        "ActiveInput": NotRequired[InputDeviceActiveInputType],
        "ConfiguredInput": NotRequired[InputDeviceConfiguredInputType],
        "DeviceState": NotRequired[InputDeviceStateType],
        "Framerate": NotRequired[float],
        "Height": NotRequired[int],
        "MaxBitrate": NotRequired[int],
        "ScanType": NotRequired[InputDeviceScanTypeType],
        "Width": NotRequired[int],
        "LatencyMs": NotRequired[int],
    },
)
InputDeviceNetworkSettingsTypeDef = TypedDict(
    "InputDeviceNetworkSettingsTypeDef",
    {
        "DnsAddresses": NotRequired[List[str]],
        "Gateway": NotRequired[str],
        "IpAddress": NotRequired[str],
        "IpScheme": NotRequired[InputDeviceIpSchemeType],
        "SubnetMask": NotRequired[str],
    },
)
DescribeInputDeviceThumbnailRequestRequestTypeDef = TypedDict(
    "DescribeInputDeviceThumbnailRequestRequestTypeDef",
    {
        "InputDeviceId": str,
        "Accept": Literal["image/jpeg"],
    },
)
DescribeInputRequestRequestTypeDef = TypedDict(
    "DescribeInputRequestRequestTypeDef",
    {
        "InputId": str,
    },
)
InputSourceTypeDef = TypedDict(
    "InputSourceTypeDef",
    {
        "PasswordParam": NotRequired[str],
        "Url": NotRequired[str],
        "Username": NotRequired[str],
    },
)
MediaConnectFlowTypeDef = TypedDict(
    "MediaConnectFlowTypeDef",
    {
        "FlowArn": NotRequired[str],
    },
)
DescribeInputSecurityGroupRequestRequestTypeDef = TypedDict(
    "DescribeInputSecurityGroupRequestRequestTypeDef",
    {
        "InputSecurityGroupId": str,
    },
)
InputWhitelistRuleTypeDef = TypedDict(
    "InputWhitelistRuleTypeDef",
    {
        "Cidr": NotRequired[str],
    },
)
DescribeMultiplexProgramRequestRequestTypeDef = TypedDict(
    "DescribeMultiplexProgramRequestRequestTypeDef",
    {
        "MultiplexId": str,
        "ProgramName": str,
    },
)
DescribeMultiplexRequestRequestTypeDef = TypedDict(
    "DescribeMultiplexRequestRequestTypeDef",
    {
        "MultiplexId": str,
    },
)
DescribeOfferingRequestRequestTypeDef = TypedDict(
    "DescribeOfferingRequestRequestTypeDef",
    {
        "OfferingId": str,
    },
)
DescribeReservationRequestRequestTypeDef = TypedDict(
    "DescribeReservationRequestRequestTypeDef",
    {
        "ReservationId": str,
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
DescribeScheduleRequestRequestTypeDef = TypedDict(
    "DescribeScheduleRequestRequestTypeDef",
    {
        "ChannelId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeThumbnailsRequestRequestTypeDef = TypedDict(
    "DescribeThumbnailsRequestRequestTypeDef",
    {
        "ChannelId": str,
        "PipelineId": str,
        "ThumbnailType": str,
    },
)
DvbNitSettingsTypeDef = TypedDict(
    "DvbNitSettingsTypeDef",
    {
        "NetworkId": int,
        "NetworkName": str,
        "RepInterval": NotRequired[int],
    },
)
DvbSdtSettingsTypeDef = TypedDict(
    "DvbSdtSettingsTypeDef",
    {
        "OutputSdt": NotRequired[DvbSdtOutputSdtType],
        "RepInterval": NotRequired[int],
        "ServiceName": NotRequired[str],
        "ServiceProviderName": NotRequired[str],
    },
)
DvbTdtSettingsTypeDef = TypedDict(
    "DvbTdtSettingsTypeDef",
    {
        "RepInterval": NotRequired[int],
    },
)
FeatureActivationsTypeDef = TypedDict(
    "FeatureActivationsTypeDef",
    {
        "InputPrepareScheduleActions": NotRequired[
            FeatureActivationsInputPrepareScheduleActionsType
        ],
        "OutputStaticImageOverlayScheduleActions": NotRequired[
            FeatureActivationsOutputStaticImageOverlayScheduleActionsType
        ],
    },
)
NielsenConfigurationTypeDef = TypedDict(
    "NielsenConfigurationTypeDef",
    {
        "DistributorId": NotRequired[str],
        "NielsenPcmToId3Tagging": NotRequired[NielsenPcmToId3TaggingStateType],
    },
)
ThumbnailConfigurationTypeDef = TypedDict(
    "ThumbnailConfigurationTypeDef",
    {
        "State": ThumbnailStateType,
    },
)
TimecodeConfigTypeDef = TypedDict(
    "TimecodeConfigTypeDef",
    {
        "Source": TimecodeConfigSourceType,
        "SyncThreshold": NotRequired[int],
    },
)
EpochLockingSettingsTypeDef = TypedDict(
    "EpochLockingSettingsTypeDef",
    {
        "CustomEpoch": NotRequired[str],
        "JamSyncTime": NotRequired[str],
    },
)
EventBridgeRuleTemplateGroupSummaryTypeDef = TypedDict(
    "EventBridgeRuleTemplateGroupSummaryTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Id": str,
        "Name": str,
        "TemplateCount": int,
        "Description": NotRequired[str],
        "ModifiedAt": NotRequired[datetime],
        "Tags": NotRequired[Dict[str, str]],
    },
)
EventBridgeRuleTemplateSummaryTypeDef = TypedDict(
    "EventBridgeRuleTemplateSummaryTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "EventTargetCount": int,
        "EventType": EventBridgeRuleTemplateEventTypeType,
        "GroupId": str,
        "Id": str,
        "Name": str,
        "Description": NotRequired[str],
        "ModifiedAt": NotRequired[datetime],
        "Tags": NotRequired[Dict[str, str]],
    },
)
InputLossFailoverSettingsTypeDef = TypedDict(
    "InputLossFailoverSettingsTypeDef",
    {
        "InputLossThresholdMsec": NotRequired[int],
    },
)
VideoBlackFailoverSettingsTypeDef = TypedDict(
    "VideoBlackFailoverSettingsTypeDef",
    {
        "BlackDetectThreshold": NotRequired[float],
        "VideoBlackThresholdMsec": NotRequired[int],
    },
)
FecOutputSettingsTypeDef = TypedDict(
    "FecOutputSettingsTypeDef",
    {
        "ColumnDepth": NotRequired[int],
        "IncludeFec": NotRequired[FecOutputIncludeFecType],
        "RowLength": NotRequired[int],
    },
)
FixedModeScheduleActionStartSettingsTypeDef = TypedDict(
    "FixedModeScheduleActionStartSettingsTypeDef",
    {
        "Time": str,
    },
)
Fmp4HlsSettingsTypeDef = TypedDict(
    "Fmp4HlsSettingsTypeDef",
    {
        "AudioRenditionSets": NotRequired[str],
        "NielsenId3Behavior": NotRequired[Fmp4NielsenId3BehaviorType],
        "TimedMetadataBehavior": NotRequired[Fmp4TimedMetadataBehaviorType],
    },
)
FollowModeScheduleActionStartSettingsTypeDef = TypedDict(
    "FollowModeScheduleActionStartSettingsTypeDef",
    {
        "FollowPoint": FollowPointType,
        "ReferenceActionName": str,
    },
)
FrameCaptureS3SettingsTypeDef = TypedDict(
    "FrameCaptureS3SettingsTypeDef",
    {
        "CannedAcl": NotRequired[S3CannedAclType],
    },
)
FrameCaptureOutputSettingsTypeDef = TypedDict(
    "FrameCaptureOutputSettingsTypeDef",
    {
        "NameModifier": NotRequired[str],
    },
)
TimecodeBurninSettingsTypeDef = TypedDict(
    "TimecodeBurninSettingsTypeDef",
    {
        "FontSize": TimecodeBurninFontSizeType,
        "Position": TimecodeBurninPositionType,
        "Prefix": NotRequired[str],
    },
)
GetCloudWatchAlarmTemplateGroupRequestRequestTypeDef = TypedDict(
    "GetCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
GetCloudWatchAlarmTemplateRequestRequestTypeDef = TypedDict(
    "GetCloudWatchAlarmTemplateRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
GetEventBridgeRuleTemplateGroupRequestRequestTypeDef = TypedDict(
    "GetEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
GetEventBridgeRuleTemplateRequestRequestTypeDef = TypedDict(
    "GetEventBridgeRuleTemplateRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
GetSignalMapRequestRequestTypeDef = TypedDict(
    "GetSignalMapRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
H264ColorSpaceSettingsOutputTypeDef = TypedDict(
    "H264ColorSpaceSettingsOutputTypeDef",
    {
        "ColorSpacePassthroughSettings": NotRequired[Dict[str, Any]],
        "Rec601Settings": NotRequired[Dict[str, Any]],
        "Rec709Settings": NotRequired[Dict[str, Any]],
    },
)
H264ColorSpaceSettingsTypeDef = TypedDict(
    "H264ColorSpaceSettingsTypeDef",
    {
        "ColorSpacePassthroughSettings": NotRequired[Mapping[str, Any]],
        "Rec601Settings": NotRequired[Mapping[str, Any]],
        "Rec709Settings": NotRequired[Mapping[str, Any]],
    },
)
TemporalFilterSettingsTypeDef = TypedDict(
    "TemporalFilterSettingsTypeDef",
    {
        "PostFilterSharpening": NotRequired[TemporalFilterPostFilterSharpeningType],
        "Strength": NotRequired[TemporalFilterStrengthType],
    },
)
Hdr10SettingsTypeDef = TypedDict(
    "Hdr10SettingsTypeDef",
    {
        "MaxCll": NotRequired[int],
        "MaxFall": NotRequired[int],
    },
)
HlsAkamaiSettingsTypeDef = TypedDict(
    "HlsAkamaiSettingsTypeDef",
    {
        "ConnectionRetryInterval": NotRequired[int],
        "FilecacheDuration": NotRequired[int],
        "HttpTransferMode": NotRequired[HlsAkamaiHttpTransferModeType],
        "NumRetries": NotRequired[int],
        "RestartDelay": NotRequired[int],
        "Salt": NotRequired[str],
        "Token": NotRequired[str],
    },
)
HlsBasicPutSettingsTypeDef = TypedDict(
    "HlsBasicPutSettingsTypeDef",
    {
        "ConnectionRetryInterval": NotRequired[int],
        "FilecacheDuration": NotRequired[int],
        "NumRetries": NotRequired[int],
        "RestartDelay": NotRequired[int],
    },
)
HlsMediaStoreSettingsTypeDef = TypedDict(
    "HlsMediaStoreSettingsTypeDef",
    {
        "ConnectionRetryInterval": NotRequired[int],
        "FilecacheDuration": NotRequired[int],
        "MediaStoreStorageClass": NotRequired[Literal["TEMPORAL"]],
        "NumRetries": NotRequired[int],
        "RestartDelay": NotRequired[int],
    },
)
HlsS3SettingsTypeDef = TypedDict(
    "HlsS3SettingsTypeDef",
    {
        "CannedAcl": NotRequired[S3CannedAclType],
    },
)
HlsWebdavSettingsTypeDef = TypedDict(
    "HlsWebdavSettingsTypeDef",
    {
        "ConnectionRetryInterval": NotRequired[int],
        "FilecacheDuration": NotRequired[int],
        "HttpTransferMode": NotRequired[HlsWebdavHttpTransferModeType],
        "NumRetries": NotRequired[int],
        "RestartDelay": NotRequired[int],
    },
)
HlsId3SegmentTaggingScheduleActionSettingsTypeDef = TypedDict(
    "HlsId3SegmentTaggingScheduleActionSettingsTypeDef",
    {
        "Tag": NotRequired[str],
        "Id3": NotRequired[str],
    },
)
HlsInputSettingsTypeDef = TypedDict(
    "HlsInputSettingsTypeDef",
    {
        "Bandwidth": NotRequired[int],
        "BufferSegments": NotRequired[int],
        "Retries": NotRequired[int],
        "RetryInterval": NotRequired[int],
        "Scte35Source": NotRequired[HlsScte35SourceTypeType],
    },
)
HlsTimedMetadataScheduleActionSettingsTypeDef = TypedDict(
    "HlsTimedMetadataScheduleActionSettingsTypeDef",
    {
        "Id3": str,
    },
)
StartTimecodeTypeDef = TypedDict(
    "StartTimecodeTypeDef",
    {
        "Timecode": NotRequired[str],
    },
)
StopTimecodeTypeDef = TypedDict(
    "StopTimecodeTypeDef",
    {
        "LastFrameClippingBehavior": NotRequired[LastFrameClippingBehaviorType],
        "Timecode": NotRequired[str],
    },
)
InputDestinationVpcTypeDef = TypedDict(
    "InputDestinationVpcTypeDef",
    {
        "AvailabilityZone": NotRequired[str],
        "NetworkInterfaceId": NotRequired[str],
    },
)
InputDeviceConfigurableAudioChannelPairConfigTypeDef = TypedDict(
    "InputDeviceConfigurableAudioChannelPairConfigTypeDef",
    {
        "Id": NotRequired[int],
        "Profile": NotRequired[InputDeviceConfigurableAudioChannelPairProfileType],
    },
)
InputDeviceMediaConnectConfigurableSettingsTypeDef = TypedDict(
    "InputDeviceMediaConnectConfigurableSettingsTypeDef",
    {
        "FlowArn": NotRequired[str],
        "RoleArn": NotRequired[str],
        "SecretArn": NotRequired[str],
        "SourceName": NotRequired[str],
    },
)
InputDeviceMediaConnectSettingsTypeDef = TypedDict(
    "InputDeviceMediaConnectSettingsTypeDef",
    {
        "FlowArn": NotRequired[str],
        "RoleArn": NotRequired[str],
        "SecretArn": NotRequired[str],
        "SourceName": NotRequired[str],
    },
)
InputDeviceRequestTypeDef = TypedDict(
    "InputDeviceRequestTypeDef",
    {
        "Id": NotRequired[str],
    },
)
InputDeviceUhdAudioChannelPairConfigTypeDef = TypedDict(
    "InputDeviceUhdAudioChannelPairConfigTypeDef",
    {
        "Id": NotRequired[int],
        "Profile": NotRequired[InputDeviceUhdAudioChannelPairProfileType],
    },
)
ListChannelsRequestRequestTypeDef = TypedDict(
    "ListChannelsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListCloudWatchAlarmTemplateGroupsRequestRequestTypeDef = TypedDict(
    "ListCloudWatchAlarmTemplateGroupsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Scope": NotRequired[str],
        "SignalMapIdentifier": NotRequired[str],
    },
)
ListCloudWatchAlarmTemplatesRequestRequestTypeDef = TypedDict(
    "ListCloudWatchAlarmTemplatesRequestRequestTypeDef",
    {
        "GroupIdentifier": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Scope": NotRequired[str],
        "SignalMapIdentifier": NotRequired[str],
    },
)
ListEventBridgeRuleTemplateGroupsRequestRequestTypeDef = TypedDict(
    "ListEventBridgeRuleTemplateGroupsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "SignalMapIdentifier": NotRequired[str],
    },
)
ListEventBridgeRuleTemplatesRequestRequestTypeDef = TypedDict(
    "ListEventBridgeRuleTemplatesRequestRequestTypeDef",
    {
        "GroupIdentifier": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "SignalMapIdentifier": NotRequired[str],
    },
)
ListInputDeviceTransfersRequestRequestTypeDef = TypedDict(
    "ListInputDeviceTransfersRequestRequestTypeDef",
    {
        "TransferType": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
TransferringInputDeviceSummaryTypeDef = TypedDict(
    "TransferringInputDeviceSummaryTypeDef",
    {
        "Id": NotRequired[str],
        "Message": NotRequired[str],
        "TargetCustomerId": NotRequired[str],
        "TransferType": NotRequired[InputDeviceTransferTypeType],
    },
)
ListInputDevicesRequestRequestTypeDef = TypedDict(
    "ListInputDevicesRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListInputSecurityGroupsRequestRequestTypeDef = TypedDict(
    "ListInputSecurityGroupsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListInputsRequestRequestTypeDef = TypedDict(
    "ListInputsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListMultiplexProgramsRequestRequestTypeDef = TypedDict(
    "ListMultiplexProgramsRequestRequestTypeDef",
    {
        "MultiplexId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
MultiplexProgramSummaryTypeDef = TypedDict(
    "MultiplexProgramSummaryTypeDef",
    {
        "ChannelId": NotRequired[str],
        "ProgramName": NotRequired[str],
    },
)
ListMultiplexesRequestRequestTypeDef = TypedDict(
    "ListMultiplexesRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListOfferingsRequestRequestTypeDef = TypedDict(
    "ListOfferingsRequestRequestTypeDef",
    {
        "ChannelClass": NotRequired[str],
        "ChannelConfiguration": NotRequired[str],
        "Codec": NotRequired[str],
        "Duration": NotRequired[str],
        "MaxResults": NotRequired[int],
        "MaximumBitrate": NotRequired[str],
        "MaximumFramerate": NotRequired[str],
        "NextToken": NotRequired[str],
        "Resolution": NotRequired[str],
        "ResourceType": NotRequired[str],
        "SpecialFeature": NotRequired[str],
        "VideoQuality": NotRequired[str],
    },
)
ListReservationsRequestRequestTypeDef = TypedDict(
    "ListReservationsRequestRequestTypeDef",
    {
        "ChannelClass": NotRequired[str],
        "Codec": NotRequired[str],
        "MaxResults": NotRequired[int],
        "MaximumBitrate": NotRequired[str],
        "MaximumFramerate": NotRequired[str],
        "NextToken": NotRequired[str],
        "Resolution": NotRequired[str],
        "ResourceType": NotRequired[str],
        "SpecialFeature": NotRequired[str],
        "VideoQuality": NotRequired[str],
    },
)
ListSignalMapsRequestRequestTypeDef = TypedDict(
    "ListSignalMapsRequestRequestTypeDef",
    {
        "CloudWatchAlarmTemplateGroupIdentifier": NotRequired[str],
        "EventBridgeRuleTemplateGroupIdentifier": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
SignalMapSummaryTypeDef = TypedDict(
    "SignalMapSummaryTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Id": str,
        "MonitorDeploymentStatus": SignalMapMonitorDeploymentStatusType,
        "Name": str,
        "Status": SignalMapStatusType,
        "Description": NotRequired[str],
        "ModifiedAt": NotRequired[datetime],
        "Tags": NotRequired[Dict[str, str]],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
M3u8SettingsTypeDef = TypedDict(
    "M3u8SettingsTypeDef",
    {
        "AudioFramesPerPes": NotRequired[int],
        "AudioPids": NotRequired[str],
        "EcmPid": NotRequired[str],
        "NielsenId3Behavior": NotRequired[M3u8NielsenId3BehaviorType],
        "PatInterval": NotRequired[int],
        "PcrControl": NotRequired[M3u8PcrControlType],
        "PcrPeriod": NotRequired[int],
        "PcrPid": NotRequired[str],
        "PmtInterval": NotRequired[int],
        "PmtPid": NotRequired[str],
        "ProgramNum": NotRequired[int],
        "Scte35Behavior": NotRequired[M3u8Scte35BehaviorType],
        "Scte35Pid": NotRequired[str],
        "TimedMetadataBehavior": NotRequired[M3u8TimedMetadataBehaviorType],
        "TimedMetadataPid": NotRequired[str],
        "TransportStreamId": NotRequired[int],
        "VideoPid": NotRequired[str],
        "KlvBehavior": NotRequired[M3u8KlvBehaviorType],
        "KlvDataPids": NotRequired[str],
    },
)
MaintenanceUpdateSettingsTypeDef = TypedDict(
    "MaintenanceUpdateSettingsTypeDef",
    {
        "MaintenanceDay": NotRequired[MaintenanceDayType],
        "MaintenanceScheduledDate": NotRequired[str],
        "MaintenanceStartTime": NotRequired[str],
    },
)
MediaPackageOutputDestinationSettingsTypeDef = TypedDict(
    "MediaPackageOutputDestinationSettingsTypeDef",
    {
        "ChannelId": NotRequired[str],
    },
)
MediaResourceNeighborTypeDef = TypedDict(
    "MediaResourceNeighborTypeDef",
    {
        "Arn": str,
        "Name": NotRequired[str],
    },
)
MotionGraphicsActivateScheduleActionSettingsTypeDef = TypedDict(
    "MotionGraphicsActivateScheduleActionSettingsTypeDef",
    {
        "Duration": NotRequired[int],
        "PasswordParam": NotRequired[str],
        "Url": NotRequired[str],
        "Username": NotRequired[str],
    },
)
MotionGraphicsSettingsOutputTypeDef = TypedDict(
    "MotionGraphicsSettingsOutputTypeDef",
    {
        "HtmlMotionGraphicsSettings": NotRequired[Dict[str, Any]],
    },
)
MotionGraphicsSettingsTypeDef = TypedDict(
    "MotionGraphicsSettingsTypeDef",
    {
        "HtmlMotionGraphicsSettings": NotRequired[Mapping[str, Any]],
    },
)
MsSmoothOutputSettingsTypeDef = TypedDict(
    "MsSmoothOutputSettingsTypeDef",
    {
        "H265PackagingType": NotRequired[MsSmoothH265PackagingTypeType],
        "NameModifier": NotRequired[str],
    },
)
MultiplexMediaConnectOutputDestinationSettingsTypeDef = TypedDict(
    "MultiplexMediaConnectOutputDestinationSettingsTypeDef",
    {
        "EntitlementArn": NotRequired[str],
    },
)
MultiplexProgramChannelDestinationSettingsTypeDef = TypedDict(
    "MultiplexProgramChannelDestinationSettingsTypeDef",
    {
        "MultiplexId": NotRequired[str],
        "ProgramName": NotRequired[str],
    },
)
MultiplexProgramServiceDescriptorTypeDef = TypedDict(
    "MultiplexProgramServiceDescriptorTypeDef",
    {
        "ProviderName": str,
        "ServiceName": str,
    },
)
MultiplexSettingsSummaryTypeDef = TypedDict(
    "MultiplexSettingsSummaryTypeDef",
    {
        "TransportStreamBitrate": NotRequired[int],
    },
)
MultiplexStatmuxVideoSettingsTypeDef = TypedDict(
    "MultiplexStatmuxVideoSettingsTypeDef",
    {
        "MaximumBitrate": NotRequired[int],
        "MinimumBitrate": NotRequired[int],
        "Priority": NotRequired[int],
    },
)
NielsenCBETTypeDef = TypedDict(
    "NielsenCBETTypeDef",
    {
        "CbetCheckDigitString": str,
        "CbetStepaside": NielsenWatermarksCbetStepasideType,
        "Csid": str,
    },
)
NielsenNaesIiNwTypeDef = TypedDict(
    "NielsenNaesIiNwTypeDef",
    {
        "CheckDigitString": str,
        "Sid": float,
        "Timezone": NotRequired[NielsenWatermarkTimezonesType],
    },
)
OutputDestinationSettingsTypeDef = TypedDict(
    "OutputDestinationSettingsTypeDef",
    {
        "PasswordParam": NotRequired[str],
        "StreamName": NotRequired[str],
        "Url": NotRequired[str],
        "Username": NotRequired[str],
    },
)
RtmpGroupSettingsOutputTypeDef = TypedDict(
    "RtmpGroupSettingsOutputTypeDef",
    {
        "AdMarkers": NotRequired[List[Literal["ON_CUE_POINT_SCTE35"]]],
        "AuthenticationScheme": NotRequired[AuthenticationSchemeType],
        "CacheFullBehavior": NotRequired[RtmpCacheFullBehaviorType],
        "CacheLength": NotRequired[int],
        "CaptionData": NotRequired[RtmpCaptionDataType],
        "InputLossAction": NotRequired[InputLossActionForRtmpOutType],
        "RestartDelay": NotRequired[int],
        "IncludeFillerNalUnits": NotRequired[IncludeFillerNalUnitsType],
    },
)
UdpGroupSettingsTypeDef = TypedDict(
    "UdpGroupSettingsTypeDef",
    {
        "InputLossAction": NotRequired[InputLossActionForUdpOutType],
        "TimedMetadataId3Frame": NotRequired[UdpTimedMetadataId3FrameType],
        "TimedMetadataId3Period": NotRequired[int],
    },
)
RtmpGroupSettingsTypeDef = TypedDict(
    "RtmpGroupSettingsTypeDef",
    {
        "AdMarkers": NotRequired[Sequence[Literal["ON_CUE_POINT_SCTE35"]]],
        "AuthenticationScheme": NotRequired[AuthenticationSchemeType],
        "CacheFullBehavior": NotRequired[RtmpCacheFullBehaviorType],
        "CacheLength": NotRequired[int],
        "CaptionData": NotRequired[RtmpCaptionDataType],
        "InputLossAction": NotRequired[InputLossActionForRtmpOutType],
        "RestartDelay": NotRequired[int],
        "IncludeFillerNalUnits": NotRequired[IncludeFillerNalUnitsType],
    },
)
PipelinePauseStateSettingsTypeDef = TypedDict(
    "PipelinePauseStateSettingsTypeDef",
    {
        "PipelineId": PipelineIdType,
    },
)
RebootInputDeviceRequestRequestTypeDef = TypedDict(
    "RebootInputDeviceRequestRequestTypeDef",
    {
        "InputDeviceId": str,
        "Force": NotRequired[RebootInputDeviceForceType],
    },
)
RejectInputDeviceTransferRequestRequestTypeDef = TypedDict(
    "RejectInputDeviceTransferRequestRequestTypeDef",
    {
        "InputDeviceId": str,
    },
)
RestartChannelPipelinesRequestRequestTypeDef = TypedDict(
    "RestartChannelPipelinesRequestRequestTypeDef",
    {
        "ChannelId": str,
        "PipelineIds": NotRequired[Sequence[ChannelPipelineIdToRestartType]],
    },
)
Scte35InputScheduleActionSettingsTypeDef = TypedDict(
    "Scte35InputScheduleActionSettingsTypeDef",
    {
        "Mode": Scte35InputModeType,
        "InputAttachmentNameReference": NotRequired[str],
    },
)
Scte35ReturnToNetworkScheduleActionSettingsTypeDef = TypedDict(
    "Scte35ReturnToNetworkScheduleActionSettingsTypeDef",
    {
        "SpliceEventId": int,
    },
)
Scte35SpliceInsertScheduleActionSettingsTypeDef = TypedDict(
    "Scte35SpliceInsertScheduleActionSettingsTypeDef",
    {
        "SpliceEventId": int,
        "Duration": NotRequired[int],
    },
)
StaticImageDeactivateScheduleActionSettingsTypeDef = TypedDict(
    "StaticImageDeactivateScheduleActionSettingsTypeDef",
    {
        "FadeOut": NotRequired[int],
        "Layer": NotRequired[int],
    },
)
StaticImageOutputDeactivateScheduleActionSettingsExtraOutputTypeDef = TypedDict(
    "StaticImageOutputDeactivateScheduleActionSettingsExtraOutputTypeDef",
    {
        "OutputNames": List[str],
        "FadeOut": NotRequired[int],
        "Layer": NotRequired[int],
    },
)
StaticImageOutputDeactivateScheduleActionSettingsOutputTypeDef = TypedDict(
    "StaticImageOutputDeactivateScheduleActionSettingsOutputTypeDef",
    {
        "OutputNames": List[str],
        "FadeOut": NotRequired[int],
        "Layer": NotRequired[int],
    },
)
StaticImageOutputDeactivateScheduleActionSettingsTypeDef = TypedDict(
    "StaticImageOutputDeactivateScheduleActionSettingsTypeDef",
    {
        "OutputNames": Sequence[str],
        "FadeOut": NotRequired[int],
        "Layer": NotRequired[int],
    },
)
Scte35DeliveryRestrictionsTypeDef = TypedDict(
    "Scte35DeliveryRestrictionsTypeDef",
    {
        "ArchiveAllowedFlag": Scte35ArchiveAllowedFlagType,
        "DeviceRestrictions": Scte35DeviceRestrictionsType,
        "NoRegionalBlackoutFlag": Scte35NoRegionalBlackoutFlagType,
        "WebDeliveryAllowedFlag": Scte35WebDeliveryAllowedFlagType,
    },
)
SrtCallerDecryptionRequestTypeDef = TypedDict(
    "SrtCallerDecryptionRequestTypeDef",
    {
        "Algorithm": NotRequired[AlgorithmType],
        "PassphraseSecretArn": NotRequired[str],
    },
)
SrtCallerDecryptionTypeDef = TypedDict(
    "SrtCallerDecryptionTypeDef",
    {
        "Algorithm": NotRequired[AlgorithmType],
        "PassphraseSecretArn": NotRequired[str],
    },
)
StartChannelRequestRequestTypeDef = TypedDict(
    "StartChannelRequestRequestTypeDef",
    {
        "ChannelId": str,
    },
)
StartDeleteMonitorDeploymentRequestRequestTypeDef = TypedDict(
    "StartDeleteMonitorDeploymentRequestRequestTypeDef",
    {
        "Identifier": str,
    },
)
StartInputDeviceMaintenanceWindowRequestRequestTypeDef = TypedDict(
    "StartInputDeviceMaintenanceWindowRequestRequestTypeDef",
    {
        "InputDeviceId": str,
    },
)
StartInputDeviceRequestRequestTypeDef = TypedDict(
    "StartInputDeviceRequestRequestTypeDef",
    {
        "InputDeviceId": str,
    },
)
StartMonitorDeploymentRequestRequestTypeDef = TypedDict(
    "StartMonitorDeploymentRequestRequestTypeDef",
    {
        "Identifier": str,
        "DryRun": NotRequired[bool],
    },
)
StartMultiplexRequestRequestTypeDef = TypedDict(
    "StartMultiplexRequestRequestTypeDef",
    {
        "MultiplexId": str,
    },
)
StartUpdateSignalMapRequestRequestTypeDef = TypedDict(
    "StartUpdateSignalMapRequestRequestTypeDef",
    {
        "Identifier": str,
        "CloudWatchAlarmTemplateGroupIdentifiers": NotRequired[Sequence[str]],
        "Description": NotRequired[str],
        "DiscoveryEntryPointArn": NotRequired[str],
        "EventBridgeRuleTemplateGroupIdentifiers": NotRequired[Sequence[str]],
        "ForceRediscovery": NotRequired[bool],
        "Name": NotRequired[str],
    },
)
StopChannelRequestRequestTypeDef = TypedDict(
    "StopChannelRequestRequestTypeDef",
    {
        "ChannelId": str,
    },
)
StopInputDeviceRequestRequestTypeDef = TypedDict(
    "StopInputDeviceRequestRequestTypeDef",
    {
        "InputDeviceId": str,
    },
)
StopMultiplexRequestRequestTypeDef = TypedDict(
    "StopMultiplexRequestRequestTypeDef",
    {
        "MultiplexId": str,
    },
)
ThumbnailTypeDef = TypedDict(
    "ThumbnailTypeDef",
    {
        "Body": NotRequired[str],
        "ContentType": NotRequired[str],
        "ThumbnailType": NotRequired[ThumbnailTypeType],
        "TimeStamp": NotRequired[datetime],
    },
)
TransferInputDeviceRequestRequestTypeDef = TypedDict(
    "TransferInputDeviceRequestRequestTypeDef",
    {
        "InputDeviceId": str,
        "TargetCustomerId": NotRequired[str],
        "TargetRegion": NotRequired[str],
        "TransferMessage": NotRequired[str],
    },
)
UpdateCloudWatchAlarmTemplateGroupRequestRequestTypeDef = TypedDict(
    "UpdateCloudWatchAlarmTemplateGroupRequestRequestTypeDef",
    {
        "Identifier": str,
        "Description": NotRequired[str],
    },
)
UpdateCloudWatchAlarmTemplateRequestRequestTypeDef = TypedDict(
    "UpdateCloudWatchAlarmTemplateRequestRequestTypeDef",
    {
        "Identifier": str,
        "ComparisonOperator": NotRequired[CloudWatchAlarmTemplateComparisonOperatorType],
        "DatapointsToAlarm": NotRequired[int],
        "Description": NotRequired[str],
        "EvaluationPeriods": NotRequired[int],
        "GroupIdentifier": NotRequired[str],
        "MetricName": NotRequired[str],
        "Name": NotRequired[str],
        "Period": NotRequired[int],
        "Statistic": NotRequired[CloudWatchAlarmTemplateStatisticType],
        "TargetResourceType": NotRequired[CloudWatchAlarmTemplateTargetResourceTypeType],
        "Threshold": NotRequired[float],
        "TreatMissingData": NotRequired[CloudWatchAlarmTemplateTreatMissingDataType],
    },
)
UpdateEventBridgeRuleTemplateGroupRequestRequestTypeDef = TypedDict(
    "UpdateEventBridgeRuleTemplateGroupRequestRequestTypeDef",
    {
        "Identifier": str,
        "Description": NotRequired[str],
    },
)
VideoSelectorPidTypeDef = TypedDict(
    "VideoSelectorPidTypeDef",
    {
        "Pid": NotRequired[int],
    },
)
VideoSelectorProgramIdTypeDef = TypedDict(
    "VideoSelectorProgramIdTypeDef",
    {
        "ProgramId": NotRequired[int],
    },
)
UpdateAccountConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateAccountConfigurationRequestRequestTypeDef",
    {
        "AccountConfiguration": NotRequired[AccountConfigurationTypeDef],
    },
)
ArchiveCdnSettingsTypeDef = TypedDict(
    "ArchiveCdnSettingsTypeDef",
    {
        "ArchiveS3Settings": NotRequired[ArchiveS3SettingsTypeDef],
    },
)
CmafIngestGroupSettingsTypeDef = TypedDict(
    "CmafIngestGroupSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
        "NielsenId3Behavior": NotRequired[CmafNielsenId3BehaviorType],
        "Scte35Type": NotRequired[Scte35TypeType],
        "SegmentLength": NotRequired[int],
        "SegmentLengthUnits": NotRequired[CmafIngestSegmentLengthUnitsType],
        "SendDelayMs": NotRequired[int],
    },
)
MediaPackageGroupSettingsTypeDef = TypedDict(
    "MediaPackageGroupSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
    },
)
MsSmoothGroupSettingsTypeDef = TypedDict(
    "MsSmoothGroupSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
        "AcquisitionPointId": NotRequired[str],
        "AudioOnlyTimecodeControl": NotRequired[SmoothGroupAudioOnlyTimecodeControlType],
        "CertificateMode": NotRequired[SmoothGroupCertificateModeType],
        "ConnectionRetryInterval": NotRequired[int],
        "EventId": NotRequired[str],
        "EventIdMode": NotRequired[SmoothGroupEventIdModeType],
        "EventStopBehavior": NotRequired[SmoothGroupEventStopBehaviorType],
        "FilecacheDuration": NotRequired[int],
        "FragmentLength": NotRequired[int],
        "InputLossAction": NotRequired[InputLossActionForMsSmoothOutType],
        "NumRetries": NotRequired[int],
        "RestartDelay": NotRequired[int],
        "SegmentationMode": NotRequired[SmoothGroupSegmentationModeType],
        "SendDelayMs": NotRequired[int],
        "SparseTrackType": NotRequired[SmoothGroupSparseTrackTypeType],
        "StreamManifestBehavior": NotRequired[SmoothGroupStreamManifestBehaviorType],
        "TimestampOffset": NotRequired[str],
        "TimestampOffsetMode": NotRequired[SmoothGroupTimestampOffsetModeType],
    },
)
MultiplexOutputSettingsTypeDef = TypedDict(
    "MultiplexOutputSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
    },
)
RtmpOutputSettingsTypeDef = TypedDict(
    "RtmpOutputSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
        "CertificateMode": NotRequired[RtmpOutputCertificateModeType],
        "ConnectionRetryInterval": NotRequired[int],
        "NumRetries": NotRequired[int],
    },
)
AudioChannelMappingOutputTypeDef = TypedDict(
    "AudioChannelMappingOutputTypeDef",
    {
        "InputChannelLevels": List[InputChannelLevelTypeDef],
        "OutputChannel": int,
    },
)
AudioChannelMappingTypeDef = TypedDict(
    "AudioChannelMappingTypeDef",
    {
        "InputChannelLevels": Sequence[InputChannelLevelTypeDef],
        "OutputChannel": int,
    },
)
AudioCodecSettingsOutputTypeDef = TypedDict(
    "AudioCodecSettingsOutputTypeDef",
    {
        "AacSettings": NotRequired[AacSettingsTypeDef],
        "Ac3Settings": NotRequired[Ac3SettingsTypeDef],
        "Eac3AtmosSettings": NotRequired[Eac3AtmosSettingsTypeDef],
        "Eac3Settings": NotRequired[Eac3SettingsTypeDef],
        "Mp2Settings": NotRequired[Mp2SettingsTypeDef],
        "PassThroughSettings": NotRequired[Dict[str, Any]],
        "WavSettings": NotRequired[WavSettingsTypeDef],
    },
)
AudioCodecSettingsTypeDef = TypedDict(
    "AudioCodecSettingsTypeDef",
    {
        "AacSettings": NotRequired[AacSettingsTypeDef],
        "Ac3Settings": NotRequired[Ac3SettingsTypeDef],
        "Eac3AtmosSettings": NotRequired[Eac3AtmosSettingsTypeDef],
        "Eac3Settings": NotRequired[Eac3SettingsTypeDef],
        "Mp2Settings": NotRequired[Mp2SettingsTypeDef],
        "PassThroughSettings": NotRequired[Mapping[str, Any]],
        "WavSettings": NotRequired[WavSettingsTypeDef],
    },
)
AudioOnlyHlsSettingsTypeDef = TypedDict(
    "AudioOnlyHlsSettingsTypeDef",
    {
        "AudioGroupId": NotRequired[str],
        "AudioOnlyImage": NotRequired[InputLocationTypeDef],
        "AudioTrackType": NotRequired[AudioOnlyHlsTrackTypeType],
        "SegmentType": NotRequired[AudioOnlyHlsSegmentTypeType],
    },
)
AvailBlankingTypeDef = TypedDict(
    "AvailBlankingTypeDef",
    {
        "AvailBlankingImage": NotRequired[InputLocationTypeDef],
        "State": NotRequired[AvailBlankingStateType],
    },
)
BlackoutSlateTypeDef = TypedDict(
    "BlackoutSlateTypeDef",
    {
        "BlackoutSlateImage": NotRequired[InputLocationTypeDef],
        "NetworkEndBlackout": NotRequired[BlackoutSlateNetworkEndBlackoutType],
        "NetworkEndBlackoutImage": NotRequired[InputLocationTypeDef],
        "NetworkId": NotRequired[str],
        "State": NotRequired[BlackoutSlateStateType],
    },
)
BurnInDestinationSettingsTypeDef = TypedDict(
    "BurnInDestinationSettingsTypeDef",
    {
        "Alignment": NotRequired[BurnInAlignmentType],
        "BackgroundColor": NotRequired[BurnInBackgroundColorType],
        "BackgroundOpacity": NotRequired[int],
        "Font": NotRequired[InputLocationTypeDef],
        "FontColor": NotRequired[BurnInFontColorType],
        "FontOpacity": NotRequired[int],
        "FontResolution": NotRequired[int],
        "FontSize": NotRequired[str],
        "OutlineColor": NotRequired[BurnInOutlineColorType],
        "OutlineSize": NotRequired[int],
        "ShadowColor": NotRequired[BurnInShadowColorType],
        "ShadowOpacity": NotRequired[int],
        "ShadowXOffset": NotRequired[int],
        "ShadowYOffset": NotRequired[int],
        "TeletextGridControl": NotRequired[BurnInTeletextGridControlType],
        "XPosition": NotRequired[int],
        "YPosition": NotRequired[int],
    },
)
DvbSubDestinationSettingsTypeDef = TypedDict(
    "DvbSubDestinationSettingsTypeDef",
    {
        "Alignment": NotRequired[DvbSubDestinationAlignmentType],
        "BackgroundColor": NotRequired[DvbSubDestinationBackgroundColorType],
        "BackgroundOpacity": NotRequired[int],
        "Font": NotRequired[InputLocationTypeDef],
        "FontColor": NotRequired[DvbSubDestinationFontColorType],
        "FontOpacity": NotRequired[int],
        "FontResolution": NotRequired[int],
        "FontSize": NotRequired[str],
        "OutlineColor": NotRequired[DvbSubDestinationOutlineColorType],
        "OutlineSize": NotRequired[int],
        "ShadowColor": NotRequired[DvbSubDestinationShadowColorType],
        "ShadowOpacity": NotRequired[int],
        "ShadowXOffset": NotRequired[int],
        "ShadowYOffset": NotRequired[int],
        "TeletextGridControl": NotRequired[DvbSubDestinationTeletextGridControlType],
        "XPosition": NotRequired[int],
        "YPosition": NotRequired[int],
    },
)
InputLossBehaviorTypeDef = TypedDict(
    "InputLossBehaviorTypeDef",
    {
        "BlackFrameMsec": NotRequired[int],
        "InputLossImageColor": NotRequired[str],
        "InputLossImageSlate": NotRequired[InputLocationTypeDef],
        "InputLossImageType": NotRequired[InputLossImageTypeType],
        "RepeatFrameMsec": NotRequired[int],
    },
)
StaticImageActivateScheduleActionSettingsTypeDef = TypedDict(
    "StaticImageActivateScheduleActionSettingsTypeDef",
    {
        "Image": InputLocationTypeDef,
        "Duration": NotRequired[int],
        "FadeIn": NotRequired[int],
        "FadeOut": NotRequired[int],
        "Height": NotRequired[int],
        "ImageX": NotRequired[int],
        "ImageY": NotRequired[int],
        "Layer": NotRequired[int],
        "Opacity": NotRequired[int],
        "Width": NotRequired[int],
    },
)
StaticImageOutputActivateScheduleActionSettingsExtraOutputTypeDef = TypedDict(
    "StaticImageOutputActivateScheduleActionSettingsExtraOutputTypeDef",
    {
        "Image": InputLocationTypeDef,
        "OutputNames": List[str],
        "Duration": NotRequired[int],
        "FadeIn": NotRequired[int],
        "FadeOut": NotRequired[int],
        "Height": NotRequired[int],
        "ImageX": NotRequired[int],
        "ImageY": NotRequired[int],
        "Layer": NotRequired[int],
        "Opacity": NotRequired[int],
        "Width": NotRequired[int],
    },
)
StaticImageOutputActivateScheduleActionSettingsOutputTypeDef = TypedDict(
    "StaticImageOutputActivateScheduleActionSettingsOutputTypeDef",
    {
        "Image": InputLocationTypeDef,
        "OutputNames": List[str],
        "Duration": NotRequired[int],
        "FadeIn": NotRequired[int],
        "FadeOut": NotRequired[int],
        "Height": NotRequired[int],
        "ImageX": NotRequired[int],
        "ImageY": NotRequired[int],
        "Layer": NotRequired[int],
        "Opacity": NotRequired[int],
        "Width": NotRequired[int],
    },
)
StaticImageOutputActivateScheduleActionSettingsTypeDef = TypedDict(
    "StaticImageOutputActivateScheduleActionSettingsTypeDef",
    {
        "Image": InputLocationTypeDef,
        "OutputNames": Sequence[str],
        "Duration": NotRequired[int],
        "FadeIn": NotRequired[int],
        "FadeOut": NotRequired[int],
        "Height": NotRequired[int],
        "ImageX": NotRequired[int],
        "ImageY": NotRequired[int],
        "Layer": NotRequired[int],
        "Opacity": NotRequired[int],
        "Width": NotRequired[int],
    },
)
StaticKeySettingsTypeDef = TypedDict(
    "StaticKeySettingsTypeDef",
    {
        "StaticKeyValue": str,
        "KeyProviderServer": NotRequired[InputLocationTypeDef],
    },
)
AudioTrackSelectionExtraOutputTypeDef = TypedDict(
    "AudioTrackSelectionExtraOutputTypeDef",
    {
        "Tracks": List[AudioTrackTypeDef],
        "DolbyEDecode": NotRequired[AudioDolbyEDecodeTypeDef],
    },
)
AudioTrackSelectionOutputTypeDef = TypedDict(
    "AudioTrackSelectionOutputTypeDef",
    {
        "Tracks": List[AudioTrackTypeDef],
        "DolbyEDecode": NotRequired[AudioDolbyEDecodeTypeDef],
    },
)
AudioTrackSelectionTypeDef = TypedDict(
    "AudioTrackSelectionTypeDef",
    {
        "Tracks": Sequence[AudioTrackTypeDef],
        "DolbyEDecode": NotRequired[AudioDolbyEDecodeTypeDef],
    },
)
AvailSettingsTypeDef = TypedDict(
    "AvailSettingsTypeDef",
    {
        "Esam": NotRequired[EsamTypeDef],
        "Scte35SpliceInsert": NotRequired[Scte35SpliceInsertTypeDef],
        "Scte35TimeSignalApos": NotRequired[Scte35TimeSignalAposTypeDef],
    },
)
BatchDeleteResponseTypeDef = TypedDict(
    "BatchDeleteResponseTypeDef",
    {
        "Failed": List[BatchFailedResultModelTypeDef],
        "Successful": List[BatchSuccessfulResultModelTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchStartResponseTypeDef = TypedDict(
    "BatchStartResponseTypeDef",
    {
        "Failed": List[BatchFailedResultModelTypeDef],
        "Successful": List[BatchSuccessfulResultModelTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchStopResponseTypeDef = TypedDict(
    "BatchStopResponseTypeDef",
    {
        "Failed": List[BatchFailedResultModelTypeDef],
        "Successful": List[BatchSuccessfulResultModelTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCloudWatchAlarmTemplateGroupResponseTypeDef = TypedDict(
    "CreateCloudWatchAlarmTemplateGroupResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCloudWatchAlarmTemplateResponseTypeDef = TypedDict(
    "CreateCloudWatchAlarmTemplateResponseTypeDef",
    {
        "Arn": str,
        "ComparisonOperator": CloudWatchAlarmTemplateComparisonOperatorType,
        "CreatedAt": datetime,
        "DatapointsToAlarm": int,
        "Description": str,
        "EvaluationPeriods": int,
        "GroupId": str,
        "Id": str,
        "MetricName": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Period": int,
        "Statistic": CloudWatchAlarmTemplateStatisticType,
        "Tags": Dict[str, str],
        "TargetResourceType": CloudWatchAlarmTemplateTargetResourceTypeType,
        "Threshold": float,
        "TreatMissingData": CloudWatchAlarmTemplateTreatMissingDataType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateEventBridgeRuleTemplateGroupResponseTypeDef = TypedDict(
    "CreateEventBridgeRuleTemplateGroupResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeAccountConfigurationResponseTypeDef = TypedDict(
    "DescribeAccountConfigurationResponseTypeDef",
    {
        "AccountConfiguration": AccountConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeInputDeviceThumbnailResponseTypeDef = TypedDict(
    "DescribeInputDeviceThumbnailResponseTypeDef",
    {
        "Body": StreamingBody,
        "ContentType": Literal["image/jpeg"],
        "ContentLength": int,
        "ETag": str,
        "LastModified": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetCloudWatchAlarmTemplateGroupResponseTypeDef = TypedDict(
    "GetCloudWatchAlarmTemplateGroupResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetCloudWatchAlarmTemplateResponseTypeDef = TypedDict(
    "GetCloudWatchAlarmTemplateResponseTypeDef",
    {
        "Arn": str,
        "ComparisonOperator": CloudWatchAlarmTemplateComparisonOperatorType,
        "CreatedAt": datetime,
        "DatapointsToAlarm": int,
        "Description": str,
        "EvaluationPeriods": int,
        "GroupId": str,
        "Id": str,
        "MetricName": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Period": int,
        "Statistic": CloudWatchAlarmTemplateStatisticType,
        "Tags": Dict[str, str],
        "TargetResourceType": CloudWatchAlarmTemplateTargetResourceTypeType,
        "Threshold": float,
        "TreatMissingData": CloudWatchAlarmTemplateTreatMissingDataType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetEventBridgeRuleTemplateGroupResponseTypeDef = TypedDict(
    "GetEventBridgeRuleTemplateGroupResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateAccountConfigurationResponseTypeDef = TypedDict(
    "UpdateAccountConfigurationResponseTypeDef",
    {
        "AccountConfiguration": AccountConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCloudWatchAlarmTemplateGroupResponseTypeDef = TypedDict(
    "UpdateCloudWatchAlarmTemplateGroupResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCloudWatchAlarmTemplateResponseTypeDef = TypedDict(
    "UpdateCloudWatchAlarmTemplateResponseTypeDef",
    {
        "Arn": str,
        "ComparisonOperator": CloudWatchAlarmTemplateComparisonOperatorType,
        "CreatedAt": datetime,
        "DatapointsToAlarm": int,
        "Description": str,
        "EvaluationPeriods": int,
        "GroupId": str,
        "Id": str,
        "MetricName": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Period": int,
        "Statistic": CloudWatchAlarmTemplateStatisticType,
        "Tags": Dict[str, str],
        "TargetResourceType": CloudWatchAlarmTemplateTargetResourceTypeType,
        "Threshold": float,
        "TreatMissingData": CloudWatchAlarmTemplateTreatMissingDataType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEventBridgeRuleTemplateGroupResponseTypeDef = TypedDict(
    "UpdateEventBridgeRuleTemplateGroupResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TeletextSourceSettingsTypeDef = TypedDict(
    "TeletextSourceSettingsTypeDef",
    {
        "OutputRectangle": NotRequired[CaptionRectangleTypeDef],
        "PageNumber": NotRequired[str],
    },
)
ListCloudWatchAlarmTemplateGroupsResponseTypeDef = TypedDict(
    "ListCloudWatchAlarmTemplateGroupsResponseTypeDef",
    {
        "CloudWatchAlarmTemplateGroups": List[CloudWatchAlarmTemplateGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListCloudWatchAlarmTemplatesResponseTypeDef = TypedDict(
    "ListCloudWatchAlarmTemplatesResponseTypeDef",
    {
        "CloudWatchAlarmTemplates": List[CloudWatchAlarmTemplateSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ColorCorrectionSettingsOutputTypeDef = TypedDict(
    "ColorCorrectionSettingsOutputTypeDef",
    {
        "GlobalColorCorrections": List[ColorCorrectionTypeDef],
    },
)
ColorCorrectionSettingsTypeDef = TypedDict(
    "ColorCorrectionSettingsTypeDef",
    {
        "GlobalColorCorrections": Sequence[ColorCorrectionTypeDef],
    },
)
CreateEventBridgeRuleTemplateRequestRequestTypeDef = TypedDict(
    "CreateEventBridgeRuleTemplateRequestRequestTypeDef",
    {
        "EventType": EventBridgeRuleTemplateEventTypeType,
        "GroupIdentifier": str,
        "Name": str,
        "Description": NotRequired[str],
        "EventTargets": NotRequired[Sequence[EventBridgeRuleTemplateTargetTypeDef]],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
CreateEventBridgeRuleTemplateResponseTypeDef = TypedDict(
    "CreateEventBridgeRuleTemplateResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "EventTargets": List[EventBridgeRuleTemplateTargetTypeDef],
        "EventType": EventBridgeRuleTemplateEventTypeType,
        "GroupId": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetEventBridgeRuleTemplateResponseTypeDef = TypedDict(
    "GetEventBridgeRuleTemplateResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "EventTargets": List[EventBridgeRuleTemplateTargetTypeDef],
        "EventType": EventBridgeRuleTemplateEventTypeType,
        "GroupId": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEventBridgeRuleTemplateRequestRequestTypeDef = TypedDict(
    "UpdateEventBridgeRuleTemplateRequestRequestTypeDef",
    {
        "Identifier": str,
        "Description": NotRequired[str],
        "EventTargets": NotRequired[Sequence[EventBridgeRuleTemplateTargetTypeDef]],
        "EventType": NotRequired[EventBridgeRuleTemplateEventTypeType],
        "GroupIdentifier": NotRequired[str],
        "Name": NotRequired[str],
    },
)
UpdateEventBridgeRuleTemplateResponseTypeDef = TypedDict(
    "UpdateEventBridgeRuleTemplateResponseTypeDef",
    {
        "Arn": str,
        "CreatedAt": datetime,
        "Description": str,
        "EventTargets": List[EventBridgeRuleTemplateTargetTypeDef],
        "EventType": EventBridgeRuleTemplateEventTypeType,
        "GroupId": str,
        "Id": str,
        "ModifiedAt": datetime,
        "Name": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInputSecurityGroupRequestRequestTypeDef = TypedDict(
    "CreateInputSecurityGroupRequestRequestTypeDef",
    {
        "Tags": NotRequired[Mapping[str, str]],
        "WhitelistRules": NotRequired[Sequence[InputWhitelistRuleCidrTypeDef]],
    },
)
UpdateInputSecurityGroupRequestRequestTypeDef = TypedDict(
    "UpdateInputSecurityGroupRequestRequestTypeDef",
    {
        "InputSecurityGroupId": str,
        "Tags": NotRequired[Mapping[str, str]],
        "WhitelistRules": NotRequired[Sequence[InputWhitelistRuleCidrTypeDef]],
    },
)
CreateMultiplexRequestRequestTypeDef = TypedDict(
    "CreateMultiplexRequestRequestTypeDef",
    {
        "AvailabilityZones": Sequence[str],
        "MultiplexSettings": MultiplexSettingsTypeDef,
        "Name": str,
        "RequestId": str,
        "Tags": NotRequired[Mapping[str, str]],
    },
)
UpdateMultiplexRequestRequestTypeDef = TypedDict(
    "UpdateMultiplexRequestRequestTypeDef",
    {
        "MultiplexId": str,
        "MultiplexSettings": NotRequired[MultiplexSettingsTypeDef],
        "Name": NotRequired[str],
    },
)
PurchaseOfferingRequestRequestTypeDef = TypedDict(
    "PurchaseOfferingRequestRequestTypeDef",
    {
        "Count": int,
        "OfferingId": str,
        "Name": NotRequired[str],
        "RenewalSettings": NotRequired[RenewalSettingsTypeDef],
        "RequestId": NotRequired[str],
        "Start": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
    },
)
UpdateReservationRequestRequestTypeDef = TypedDict(
    "UpdateReservationRequestRequestTypeDef",
    {
        "ReservationId": str,
        "Name": NotRequired[str],
        "RenewalSettings": NotRequired[RenewalSettingsTypeDef],
    },
)
DeleteReservationResponseTypeDef = TypedDict(
    "DeleteReservationResponseTypeDef",
    {
        "Arn": str,
        "Count": int,
        "CurrencyCode": str,
        "Duration": int,
        "DurationUnits": Literal["MONTHS"],
        "End": str,
        "FixedPrice": float,
        "Name": str,
        "OfferingDescription": str,
        "OfferingId": str,
        "OfferingType": Literal["NO_UPFRONT"],
        "Region": str,
        "RenewalSettings": RenewalSettingsTypeDef,
        "ReservationId": str,
        "ResourceSpecification": ReservationResourceSpecificationTypeDef,
        "Start": str,
        "State": ReservationStateType,
        "Tags": Dict[str, str],
        "UsagePrice": float,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeOfferingResponseTypeDef = TypedDict(
    "DescribeOfferingResponseTypeDef",
    {
        "Arn": str,
        "CurrencyCode": str,
        "Duration": int,
        "DurationUnits": Literal["MONTHS"],
        "FixedPrice": float,
        "OfferingDescription": str,
        "OfferingId": str,
        "OfferingType": Literal["NO_UPFRONT"],
        "Region": str,
        "ResourceSpecification": ReservationResourceSpecificationTypeDef,
        "UsagePrice": float,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeReservationResponseTypeDef = TypedDict(
    "DescribeReservationResponseTypeDef",
    {
        "Arn": str,
        "Count": int,
        "CurrencyCode": str,
        "Duration": int,
        "DurationUnits": Literal["MONTHS"],
        "End": str,
        "FixedPrice": float,
        "Name": str,
        "OfferingDescription": str,
        "OfferingId": str,
        "OfferingType": Literal["NO_UPFRONT"],
        "Region": str,
        "RenewalSettings": RenewalSettingsTypeDef,
        "ReservationId": str,
        "ResourceSpecification": ReservationResourceSpecificationTypeDef,
        "Start": str,
        "State": ReservationStateType,
        "Tags": Dict[str, str],
        "UsagePrice": float,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OfferingTypeDef = TypedDict(
    "OfferingTypeDef",
    {
        "Arn": NotRequired[str],
        "CurrencyCode": NotRequired[str],
        "Duration": NotRequired[int],
        "DurationUnits": NotRequired[Literal["MONTHS"]],
        "FixedPrice": NotRequired[float],
        "OfferingDescription": NotRequired[str],
        "OfferingId": NotRequired[str],
        "OfferingType": NotRequired[Literal["NO_UPFRONT"]],
        "Region": NotRequired[str],
        "ResourceSpecification": NotRequired[ReservationResourceSpecificationTypeDef],
        "UsagePrice": NotRequired[float],
    },
)
ReservationTypeDef = TypedDict(
    "ReservationTypeDef",
    {
        "Arn": NotRequired[str],
        "Count": NotRequired[int],
        "CurrencyCode": NotRequired[str],
        "Duration": NotRequired[int],
        "DurationUnits": NotRequired[Literal["MONTHS"]],
        "End": NotRequired[str],
        "FixedPrice": NotRequired[float],
        "Name": NotRequired[str],
        "OfferingDescription": NotRequired[str],
        "OfferingId": NotRequired[str],
        "OfferingType": NotRequired[Literal["NO_UPFRONT"]],
        "Region": NotRequired[str],
        "RenewalSettings": NotRequired[RenewalSettingsTypeDef],
        "ReservationId": NotRequired[str],
        "ResourceSpecification": NotRequired[ReservationResourceSpecificationTypeDef],
        "Start": NotRequired[str],
        "State": NotRequired[ReservationStateType],
        "Tags": NotRequired[Dict[str, str]],
        "UsagePrice": NotRequired[float],
    },
)
DescribeChannelRequestChannelCreatedWaitTypeDef = TypedDict(
    "DescribeChannelRequestChannelCreatedWaitTypeDef",
    {
        "ChannelId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeChannelRequestChannelDeletedWaitTypeDef = TypedDict(
    "DescribeChannelRequestChannelDeletedWaitTypeDef",
    {
        "ChannelId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeChannelRequestChannelRunningWaitTypeDef = TypedDict(
    "DescribeChannelRequestChannelRunningWaitTypeDef",
    {
        "ChannelId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeChannelRequestChannelStoppedWaitTypeDef = TypedDict(
    "DescribeChannelRequestChannelStoppedWaitTypeDef",
    {
        "ChannelId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeInputRequestInputAttachedWaitTypeDef = TypedDict(
    "DescribeInputRequestInputAttachedWaitTypeDef",
    {
        "InputId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeInputRequestInputDeletedWaitTypeDef = TypedDict(
    "DescribeInputRequestInputDeletedWaitTypeDef",
    {
        "InputId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeInputRequestInputDetachedWaitTypeDef = TypedDict(
    "DescribeInputRequestInputDetachedWaitTypeDef",
    {
        "InputId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeMultiplexRequestMultiplexCreatedWaitTypeDef = TypedDict(
    "DescribeMultiplexRequestMultiplexCreatedWaitTypeDef",
    {
        "MultiplexId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeMultiplexRequestMultiplexDeletedWaitTypeDef = TypedDict(
    "DescribeMultiplexRequestMultiplexDeletedWaitTypeDef",
    {
        "MultiplexId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeMultiplexRequestMultiplexRunningWaitTypeDef = TypedDict(
    "DescribeMultiplexRequestMultiplexRunningWaitTypeDef",
    {
        "MultiplexId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeMultiplexRequestMultiplexStoppedWaitTypeDef = TypedDict(
    "DescribeMultiplexRequestMultiplexStoppedWaitTypeDef",
    {
        "MultiplexId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
GetSignalMapRequestSignalMapCreatedWaitTypeDef = TypedDict(
    "GetSignalMapRequestSignalMapCreatedWaitTypeDef",
    {
        "Identifier": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
GetSignalMapRequestSignalMapMonitorDeletedWaitTypeDef = TypedDict(
    "GetSignalMapRequestSignalMapMonitorDeletedWaitTypeDef",
    {
        "Identifier": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
GetSignalMapRequestSignalMapMonitorDeployedWaitTypeDef = TypedDict(
    "GetSignalMapRequestSignalMapMonitorDeployedWaitTypeDef",
    {
        "Identifier": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
GetSignalMapRequestSignalMapUpdatedWaitTypeDef = TypedDict(
    "GetSignalMapRequestSignalMapUpdatedWaitTypeDef",
    {
        "Identifier": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeInputSecurityGroupResponseTypeDef = TypedDict(
    "DescribeInputSecurityGroupResponseTypeDef",
    {
        "Arn": str,
        "Id": str,
        "Inputs": List[str],
        "State": InputSecurityGroupStateType,
        "Tags": Dict[str, str],
        "WhitelistRules": List[InputWhitelistRuleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InputSecurityGroupTypeDef = TypedDict(
    "InputSecurityGroupTypeDef",
    {
        "Arn": NotRequired[str],
        "Id": NotRequired[str],
        "Inputs": NotRequired[List[str]],
        "State": NotRequired[InputSecurityGroupStateType],
        "Tags": NotRequired[Dict[str, str]],
        "WhitelistRules": NotRequired[List[InputWhitelistRuleTypeDef]],
    },
)
DescribeScheduleRequestDescribeSchedulePaginateTypeDef = TypedDict(
    "DescribeScheduleRequestDescribeSchedulePaginateTypeDef",
    {
        "ChannelId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListChannelsRequestListChannelsPaginateTypeDef = TypedDict(
    "ListChannelsRequestListChannelsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCloudWatchAlarmTemplateGroupsRequestListCloudWatchAlarmTemplateGroupsPaginateTypeDef = (
    TypedDict(
        "ListCloudWatchAlarmTemplateGroupsRequestListCloudWatchAlarmTemplateGroupsPaginateTypeDef",
        {
            "Scope": NotRequired[str],
            "SignalMapIdentifier": NotRequired[str],
            "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
        },
    )
)
ListCloudWatchAlarmTemplatesRequestListCloudWatchAlarmTemplatesPaginateTypeDef = TypedDict(
    "ListCloudWatchAlarmTemplatesRequestListCloudWatchAlarmTemplatesPaginateTypeDef",
    {
        "GroupIdentifier": NotRequired[str],
        "Scope": NotRequired[str],
        "SignalMapIdentifier": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListEventBridgeRuleTemplateGroupsRequestListEventBridgeRuleTemplateGroupsPaginateTypeDef = (
    TypedDict(
        "ListEventBridgeRuleTemplateGroupsRequestListEventBridgeRuleTemplateGroupsPaginateTypeDef",
        {
            "SignalMapIdentifier": NotRequired[str],
            "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
        },
    )
)
ListEventBridgeRuleTemplatesRequestListEventBridgeRuleTemplatesPaginateTypeDef = TypedDict(
    "ListEventBridgeRuleTemplatesRequestListEventBridgeRuleTemplatesPaginateTypeDef",
    {
        "GroupIdentifier": NotRequired[str],
        "SignalMapIdentifier": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInputDeviceTransfersRequestListInputDeviceTransfersPaginateTypeDef = TypedDict(
    "ListInputDeviceTransfersRequestListInputDeviceTransfersPaginateTypeDef",
    {
        "TransferType": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInputDevicesRequestListInputDevicesPaginateTypeDef = TypedDict(
    "ListInputDevicesRequestListInputDevicesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInputSecurityGroupsRequestListInputSecurityGroupsPaginateTypeDef = TypedDict(
    "ListInputSecurityGroupsRequestListInputSecurityGroupsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListInputsRequestListInputsPaginateTypeDef = TypedDict(
    "ListInputsRequestListInputsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMultiplexProgramsRequestListMultiplexProgramsPaginateTypeDef = TypedDict(
    "ListMultiplexProgramsRequestListMultiplexProgramsPaginateTypeDef",
    {
        "MultiplexId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMultiplexesRequestListMultiplexesPaginateTypeDef = TypedDict(
    "ListMultiplexesRequestListMultiplexesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListOfferingsRequestListOfferingsPaginateTypeDef = TypedDict(
    "ListOfferingsRequestListOfferingsPaginateTypeDef",
    {
        "ChannelClass": NotRequired[str],
        "ChannelConfiguration": NotRequired[str],
        "Codec": NotRequired[str],
        "Duration": NotRequired[str],
        "MaximumBitrate": NotRequired[str],
        "MaximumFramerate": NotRequired[str],
        "Resolution": NotRequired[str],
        "ResourceType": NotRequired[str],
        "SpecialFeature": NotRequired[str],
        "VideoQuality": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListReservationsRequestListReservationsPaginateTypeDef = TypedDict(
    "ListReservationsRequestListReservationsPaginateTypeDef",
    {
        "ChannelClass": NotRequired[str],
        "Codec": NotRequired[str],
        "MaximumBitrate": NotRequired[str],
        "MaximumFramerate": NotRequired[str],
        "Resolution": NotRequired[str],
        "ResourceType": NotRequired[str],
        "SpecialFeature": NotRequired[str],
        "VideoQuality": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSignalMapsRequestListSignalMapsPaginateTypeDef = TypedDict(
    "ListSignalMapsRequestListSignalMapsPaginateTypeDef",
    {
        "CloudWatchAlarmTemplateGroupIdentifier": NotRequired[str],
        "EventBridgeRuleTemplateGroupIdentifier": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
M2tsSettingsTypeDef = TypedDict(
    "M2tsSettingsTypeDef",
    {
        "AbsentInputAudioBehavior": NotRequired[M2tsAbsentInputAudioBehaviorType],
        "Arib": NotRequired[M2tsAribType],
        "AribCaptionsPid": NotRequired[str],
        "AribCaptionsPidControl": NotRequired[M2tsAribCaptionsPidControlType],
        "AudioBufferModel": NotRequired[M2tsAudioBufferModelType],
        "AudioFramesPerPes": NotRequired[int],
        "AudioPids": NotRequired[str],
        "AudioStreamType": NotRequired[M2tsAudioStreamTypeType],
        "Bitrate": NotRequired[int],
        "BufferModel": NotRequired[M2tsBufferModelType],
        "CcDescriptor": NotRequired[M2tsCcDescriptorType],
        "DvbNitSettings": NotRequired[DvbNitSettingsTypeDef],
        "DvbSdtSettings": NotRequired[DvbSdtSettingsTypeDef],
        "DvbSubPids": NotRequired[str],
        "DvbTdtSettings": NotRequired[DvbTdtSettingsTypeDef],
        "DvbTeletextPid": NotRequired[str],
        "Ebif": NotRequired[M2tsEbifControlType],
        "EbpAudioInterval": NotRequired[M2tsAudioIntervalType],
        "EbpLookaheadMs": NotRequired[int],
        "EbpPlacement": NotRequired[M2tsEbpPlacementType],
        "EcmPid": NotRequired[str],
        "EsRateInPes": NotRequired[M2tsEsRateInPesType],
        "EtvPlatformPid": NotRequired[str],
        "EtvSignalPid": NotRequired[str],
        "FragmentTime": NotRequired[float],
        "Klv": NotRequired[M2tsKlvType],
        "KlvDataPids": NotRequired[str],
        "NielsenId3Behavior": NotRequired[M2tsNielsenId3BehaviorType],
        "NullPacketBitrate": NotRequired[float],
        "PatInterval": NotRequired[int],
        "PcrControl": NotRequired[M2tsPcrControlType],
        "PcrPeriod": NotRequired[int],
        "PcrPid": NotRequired[str],
        "PmtInterval": NotRequired[int],
        "PmtPid": NotRequired[str],
        "ProgramNum": NotRequired[int],
        "RateMode": NotRequired[M2tsRateModeType],
        "Scte27Pids": NotRequired[str],
        "Scte35Control": NotRequired[M2tsScte35ControlType],
        "Scte35Pid": NotRequired[str],
        "SegmentationMarkers": NotRequired[M2tsSegmentationMarkersType],
        "SegmentationStyle": NotRequired[M2tsSegmentationStyleType],
        "SegmentationTime": NotRequired[float],
        "TimedMetadataBehavior": NotRequired[M2tsTimedMetadataBehaviorType],
        "TimedMetadataPid": NotRequired[str],
        "TransportStreamId": NotRequired[int],
        "VideoPid": NotRequired[str],
        "Scte35PrerollPullupMilliseconds": NotRequired[float],
    },
)
OutputLockingSettingsOutputTypeDef = TypedDict(
    "OutputLockingSettingsOutputTypeDef",
    {
        "EpochLockingSettings": NotRequired[EpochLockingSettingsTypeDef],
        "PipelineLockingSettings": NotRequired[Dict[str, Any]],
    },
)
OutputLockingSettingsTypeDef = TypedDict(
    "OutputLockingSettingsTypeDef",
    {
        "EpochLockingSettings": NotRequired[EpochLockingSettingsTypeDef],
        "PipelineLockingSettings": NotRequired[Mapping[str, Any]],
    },
)
ListEventBridgeRuleTemplateGroupsResponseTypeDef = TypedDict(
    "ListEventBridgeRuleTemplateGroupsResponseTypeDef",
    {
        "EventBridgeRuleTemplateGroups": List[EventBridgeRuleTemplateGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListEventBridgeRuleTemplatesResponseTypeDef = TypedDict(
    "ListEventBridgeRuleTemplatesResponseTypeDef",
    {
        "EventBridgeRuleTemplates": List[EventBridgeRuleTemplateSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
FailoverConditionSettingsTypeDef = TypedDict(
    "FailoverConditionSettingsTypeDef",
    {
        "AudioSilenceSettings": NotRequired[AudioSilenceFailoverSettingsTypeDef],
        "InputLossSettings": NotRequired[InputLossFailoverSettingsTypeDef],
        "VideoBlackSettings": NotRequired[VideoBlackFailoverSettingsTypeDef],
    },
)
ScheduleActionStartSettingsExtraOutputTypeDef = TypedDict(
    "ScheduleActionStartSettingsExtraOutputTypeDef",
    {
        "FixedModeScheduleActionStartSettings": NotRequired[
            FixedModeScheduleActionStartSettingsTypeDef
        ],
        "FollowModeScheduleActionStartSettings": NotRequired[
            FollowModeScheduleActionStartSettingsTypeDef
        ],
        "ImmediateModeScheduleActionStartSettings": NotRequired[Dict[str, Any]],
    },
)
ScheduleActionStartSettingsOutputTypeDef = TypedDict(
    "ScheduleActionStartSettingsOutputTypeDef",
    {
        "FixedModeScheduleActionStartSettings": NotRequired[
            FixedModeScheduleActionStartSettingsTypeDef
        ],
        "FollowModeScheduleActionStartSettings": NotRequired[
            FollowModeScheduleActionStartSettingsTypeDef
        ],
        "ImmediateModeScheduleActionStartSettings": NotRequired[Dict[str, Any]],
    },
)
ScheduleActionStartSettingsTypeDef = TypedDict(
    "ScheduleActionStartSettingsTypeDef",
    {
        "FixedModeScheduleActionStartSettings": NotRequired[
            FixedModeScheduleActionStartSettingsTypeDef
        ],
        "FollowModeScheduleActionStartSettings": NotRequired[
            FollowModeScheduleActionStartSettingsTypeDef
        ],
        "ImmediateModeScheduleActionStartSettings": NotRequired[Mapping[str, Any]],
    },
)
FrameCaptureCdnSettingsTypeDef = TypedDict(
    "FrameCaptureCdnSettingsTypeDef",
    {
        "FrameCaptureS3Settings": NotRequired[FrameCaptureS3SettingsTypeDef],
    },
)
FrameCaptureSettingsTypeDef = TypedDict(
    "FrameCaptureSettingsTypeDef",
    {
        "CaptureInterval": NotRequired[int],
        "CaptureIntervalUnits": NotRequired[FrameCaptureIntervalUnitType],
        "TimecodeBurninSettings": NotRequired[TimecodeBurninSettingsTypeDef],
    },
)
H264FilterSettingsTypeDef = TypedDict(
    "H264FilterSettingsTypeDef",
    {
        "TemporalFilterSettings": NotRequired[TemporalFilterSettingsTypeDef],
    },
)
H265FilterSettingsTypeDef = TypedDict(
    "H265FilterSettingsTypeDef",
    {
        "TemporalFilterSettings": NotRequired[TemporalFilterSettingsTypeDef],
    },
)
Mpeg2FilterSettingsTypeDef = TypedDict(
    "Mpeg2FilterSettingsTypeDef",
    {
        "TemporalFilterSettings": NotRequired[TemporalFilterSettingsTypeDef],
    },
)
H265ColorSpaceSettingsOutputTypeDef = TypedDict(
    "H265ColorSpaceSettingsOutputTypeDef",
    {
        "ColorSpacePassthroughSettings": NotRequired[Dict[str, Any]],
        "DolbyVision81Settings": NotRequired[Dict[str, Any]],
        "Hdr10Settings": NotRequired[Hdr10SettingsTypeDef],
        "Rec601Settings": NotRequired[Dict[str, Any]],
        "Rec709Settings": NotRequired[Dict[str, Any]],
    },
)
H265ColorSpaceSettingsTypeDef = TypedDict(
    "H265ColorSpaceSettingsTypeDef",
    {
        "ColorSpacePassthroughSettings": NotRequired[Mapping[str, Any]],
        "DolbyVision81Settings": NotRequired[Mapping[str, Any]],
        "Hdr10Settings": NotRequired[Hdr10SettingsTypeDef],
        "Rec601Settings": NotRequired[Mapping[str, Any]],
        "Rec709Settings": NotRequired[Mapping[str, Any]],
    },
)
VideoSelectorColorSpaceSettingsTypeDef = TypedDict(
    "VideoSelectorColorSpaceSettingsTypeDef",
    {
        "Hdr10Settings": NotRequired[Hdr10SettingsTypeDef],
    },
)
HlsCdnSettingsTypeDef = TypedDict(
    "HlsCdnSettingsTypeDef",
    {
        "HlsAkamaiSettings": NotRequired[HlsAkamaiSettingsTypeDef],
        "HlsBasicPutSettings": NotRequired[HlsBasicPutSettingsTypeDef],
        "HlsMediaStoreSettings": NotRequired[HlsMediaStoreSettingsTypeDef],
        "HlsS3Settings": NotRequired[HlsS3SettingsTypeDef],
        "HlsWebdavSettings": NotRequired[HlsWebdavSettingsTypeDef],
    },
)
NetworkInputSettingsTypeDef = TypedDict(
    "NetworkInputSettingsTypeDef",
    {
        "HlsInputSettings": NotRequired[HlsInputSettingsTypeDef],
        "ServerValidation": NotRequired[NetworkInputServerValidationType],
    },
)
InputClippingSettingsTypeDef = TypedDict(
    "InputClippingSettingsTypeDef",
    {
        "InputTimecodeSource": InputTimecodeSourceType,
        "StartTimecode": NotRequired[StartTimecodeTypeDef],
        "StopTimecode": NotRequired[StopTimecodeTypeDef],
    },
)
InputDestinationTypeDef = TypedDict(
    "InputDestinationTypeDef",
    {
        "Ip": NotRequired[str],
        "Port": NotRequired[str],
        "Url": NotRequired[str],
        "Vpc": NotRequired[InputDestinationVpcTypeDef],
    },
)
InputDeviceConfigurableSettingsTypeDef = TypedDict(
    "InputDeviceConfigurableSettingsTypeDef",
    {
        "ConfiguredInput": NotRequired[InputDeviceConfiguredInputType],
        "MaxBitrate": NotRequired[int],
        "LatencyMs": NotRequired[int],
        "Codec": NotRequired[InputDeviceCodecType],
        "MediaconnectSettings": NotRequired[InputDeviceMediaConnectConfigurableSettingsTypeDef],
        "AudioChannelPairs": NotRequired[
            Sequence[InputDeviceConfigurableAudioChannelPairConfigTypeDef]
        ],
    },
)
InputDeviceUhdSettingsTypeDef = TypedDict(
    "InputDeviceUhdSettingsTypeDef",
    {
        "ActiveInput": NotRequired[InputDeviceActiveInputType],
        "ConfiguredInput": NotRequired[InputDeviceConfiguredInputType],
        "DeviceState": NotRequired[InputDeviceStateType],
        "Framerate": NotRequired[float],
        "Height": NotRequired[int],
        "MaxBitrate": NotRequired[int],
        "ScanType": NotRequired[InputDeviceScanTypeType],
        "Width": NotRequired[int],
        "LatencyMs": NotRequired[int],
        "Codec": NotRequired[InputDeviceCodecType],
        "MediaconnectSettings": NotRequired[InputDeviceMediaConnectSettingsTypeDef],
        "AudioChannelPairs": NotRequired[List[InputDeviceUhdAudioChannelPairConfigTypeDef]],
    },
)
ListInputDeviceTransfersResponseTypeDef = TypedDict(
    "ListInputDeviceTransfersResponseTypeDef",
    {
        "InputDeviceTransfers": List[TransferringInputDeviceSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListMultiplexProgramsResponseTypeDef = TypedDict(
    "ListMultiplexProgramsResponseTypeDef",
    {
        "MultiplexPrograms": List[MultiplexProgramSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListSignalMapsResponseTypeDef = TypedDict(
    "ListSignalMapsResponseTypeDef",
    {
        "SignalMaps": List[SignalMapSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
StandardHlsSettingsTypeDef = TypedDict(
    "StandardHlsSettingsTypeDef",
    {
        "M3u8Settings": M3u8SettingsTypeDef,
        "AudioRenditionSets": NotRequired[str],
    },
)
MediaResourceTypeDef = TypedDict(
    "MediaResourceTypeDef",
    {
        "Destinations": NotRequired[List[MediaResourceNeighborTypeDef]],
        "Name": NotRequired[str],
        "Sources": NotRequired[List[MediaResourceNeighborTypeDef]],
    },
)
MotionGraphicsConfigurationOutputTypeDef = TypedDict(
    "MotionGraphicsConfigurationOutputTypeDef",
    {
        "MotionGraphicsSettings": MotionGraphicsSettingsOutputTypeDef,
        "MotionGraphicsInsertion": NotRequired[MotionGraphicsInsertionType],
    },
)
MotionGraphicsConfigurationTypeDef = TypedDict(
    "MotionGraphicsConfigurationTypeDef",
    {
        "MotionGraphicsSettings": MotionGraphicsSettingsTypeDef,
        "MotionGraphicsInsertion": NotRequired[MotionGraphicsInsertionType],
    },
)
MultiplexOutputDestinationTypeDef = TypedDict(
    "MultiplexOutputDestinationTypeDef",
    {
        "MediaConnectSettings": NotRequired[MultiplexMediaConnectOutputDestinationSettingsTypeDef],
    },
)
MultiplexSummaryTypeDef = TypedDict(
    "MultiplexSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "AvailabilityZones": NotRequired[List[str]],
        "Id": NotRequired[str],
        "MultiplexSettings": NotRequired[MultiplexSettingsSummaryTypeDef],
        "Name": NotRequired[str],
        "PipelinesRunningCount": NotRequired[int],
        "ProgramCount": NotRequired[int],
        "State": NotRequired[MultiplexStateType],
        "Tags": NotRequired[Dict[str, str]],
    },
)
MultiplexVideoSettingsTypeDef = TypedDict(
    "MultiplexVideoSettingsTypeDef",
    {
        "ConstantBitrate": NotRequired[int],
        "StatmuxSettings": NotRequired[MultiplexStatmuxVideoSettingsTypeDef],
    },
)
NielsenWatermarksSettingsTypeDef = TypedDict(
    "NielsenWatermarksSettingsTypeDef",
    {
        "NielsenCbetSettings": NotRequired[NielsenCBETTypeDef],
        "NielsenDistributionType": NotRequired[NielsenWatermarksDistributionTypesType],
        "NielsenNaesIiNwSettings": NotRequired[NielsenNaesIiNwTypeDef],
    },
)
OutputDestinationExtraOutputTypeDef = TypedDict(
    "OutputDestinationExtraOutputTypeDef",
    {
        "Id": NotRequired[str],
        "MediaPackageSettings": NotRequired[List[MediaPackageOutputDestinationSettingsTypeDef]],
        "MultiplexSettings": NotRequired[MultiplexProgramChannelDestinationSettingsTypeDef],
        "Settings": NotRequired[List[OutputDestinationSettingsTypeDef]],
    },
)
OutputDestinationOutputTypeDef = TypedDict(
    "OutputDestinationOutputTypeDef",
    {
        "Id": NotRequired[str],
        "MediaPackageSettings": NotRequired[List[MediaPackageOutputDestinationSettingsTypeDef]],
        "MultiplexSettings": NotRequired[MultiplexProgramChannelDestinationSettingsTypeDef],
        "Settings": NotRequired[List[OutputDestinationSettingsTypeDef]],
    },
)
OutputDestinationTypeDef = TypedDict(
    "OutputDestinationTypeDef",
    {
        "Id": NotRequired[str],
        "MediaPackageSettings": NotRequired[Sequence[MediaPackageOutputDestinationSettingsTypeDef]],
        "MultiplexSettings": NotRequired[MultiplexProgramChannelDestinationSettingsTypeDef],
        "Settings": NotRequired[Sequence[OutputDestinationSettingsTypeDef]],
    },
)
PauseStateScheduleActionSettingsExtraOutputTypeDef = TypedDict(
    "PauseStateScheduleActionSettingsExtraOutputTypeDef",
    {
        "Pipelines": NotRequired[List[PipelinePauseStateSettingsTypeDef]],
    },
)
PauseStateScheduleActionSettingsOutputTypeDef = TypedDict(
    "PauseStateScheduleActionSettingsOutputTypeDef",
    {
        "Pipelines": NotRequired[List[PipelinePauseStateSettingsTypeDef]],
    },
)
PauseStateScheduleActionSettingsTypeDef = TypedDict(
    "PauseStateScheduleActionSettingsTypeDef",
    {
        "Pipelines": NotRequired[Sequence[PipelinePauseStateSettingsTypeDef]],
    },
)
Scte35SegmentationDescriptorTypeDef = TypedDict(
    "Scte35SegmentationDescriptorTypeDef",
    {
        "SegmentationCancelIndicator": Scte35SegmentationCancelIndicatorType,
        "SegmentationEventId": int,
        "DeliveryRestrictions": NotRequired[Scte35DeliveryRestrictionsTypeDef],
        "SegmentNum": NotRequired[int],
        "SegmentationDuration": NotRequired[int],
        "SegmentationTypeId": NotRequired[int],
        "SegmentationUpid": NotRequired[str],
        "SegmentationUpidType": NotRequired[int],
        "SegmentsExpected": NotRequired[int],
        "SubSegmentNum": NotRequired[int],
        "SubSegmentsExpected": NotRequired[int],
    },
)
SrtCallerSourceRequestTypeDef = TypedDict(
    "SrtCallerSourceRequestTypeDef",
    {
        "Decryption": NotRequired[SrtCallerDecryptionRequestTypeDef],
        "MinimumLatency": NotRequired[int],
        "SrtListenerAddress": NotRequired[str],
        "SrtListenerPort": NotRequired[str],
        "StreamId": NotRequired[str],
    },
)
SrtCallerSourceTypeDef = TypedDict(
    "SrtCallerSourceTypeDef",
    {
        "Decryption": NotRequired[SrtCallerDecryptionTypeDef],
        "MinimumLatency": NotRequired[int],
        "SrtListenerAddress": NotRequired[str],
        "SrtListenerPort": NotRequired[str],
        "StreamId": NotRequired[str],
    },
)
ThumbnailDetailTypeDef = TypedDict(
    "ThumbnailDetailTypeDef",
    {
        "PipelineId": NotRequired[str],
        "Thumbnails": NotRequired[List[ThumbnailTypeDef]],
    },
)
VideoSelectorSettingsTypeDef = TypedDict(
    "VideoSelectorSettingsTypeDef",
    {
        "VideoSelectorPid": NotRequired[VideoSelectorPidTypeDef],
        "VideoSelectorProgramId": NotRequired[VideoSelectorProgramIdTypeDef],
    },
)
ArchiveGroupSettingsTypeDef = TypedDict(
    "ArchiveGroupSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
        "ArchiveCdnSettings": NotRequired[ArchiveCdnSettingsTypeDef],
        "RolloverInterval": NotRequired[int],
    },
)
RemixSettingsOutputTypeDef = TypedDict(
    "RemixSettingsOutputTypeDef",
    {
        "ChannelMappings": List[AudioChannelMappingOutputTypeDef],
        "ChannelsIn": NotRequired[int],
        "ChannelsOut": NotRequired[int],
    },
)
RemixSettingsTypeDef = TypedDict(
    "RemixSettingsTypeDef",
    {
        "ChannelMappings": Sequence[AudioChannelMappingTypeDef],
        "ChannelsIn": NotRequired[int],
        "ChannelsOut": NotRequired[int],
    },
)
CaptionDestinationSettingsOutputTypeDef = TypedDict(
    "CaptionDestinationSettingsOutputTypeDef",
    {
        "AribDestinationSettings": NotRequired[Dict[str, Any]],
        "BurnInDestinationSettings": NotRequired[BurnInDestinationSettingsTypeDef],
        "DvbSubDestinationSettings": NotRequired[DvbSubDestinationSettingsTypeDef],
        "EbuTtDDestinationSettings": NotRequired[EbuTtDDestinationSettingsTypeDef],
        "EmbeddedDestinationSettings": NotRequired[Dict[str, Any]],
        "EmbeddedPlusScte20DestinationSettings": NotRequired[Dict[str, Any]],
        "RtmpCaptionInfoDestinationSettings": NotRequired[Dict[str, Any]],
        "Scte20PlusEmbeddedDestinationSettings": NotRequired[Dict[str, Any]],
        "Scte27DestinationSettings": NotRequired[Dict[str, Any]],
        "SmpteTtDestinationSettings": NotRequired[Dict[str, Any]],
        "TeletextDestinationSettings": NotRequired[Dict[str, Any]],
        "TtmlDestinationSettings": NotRequired[TtmlDestinationSettingsTypeDef],
        "WebvttDestinationSettings": NotRequired[WebvttDestinationSettingsTypeDef],
    },
)
CaptionDestinationSettingsTypeDef = TypedDict(
    "CaptionDestinationSettingsTypeDef",
    {
        "AribDestinationSettings": NotRequired[Mapping[str, Any]],
        "BurnInDestinationSettings": NotRequired[BurnInDestinationSettingsTypeDef],
        "DvbSubDestinationSettings": NotRequired[DvbSubDestinationSettingsTypeDef],
        "EbuTtDDestinationSettings": NotRequired[EbuTtDDestinationSettingsTypeDef],
        "EmbeddedDestinationSettings": NotRequired[Mapping[str, Any]],
        "EmbeddedPlusScte20DestinationSettings": NotRequired[Mapping[str, Any]],
        "RtmpCaptionInfoDestinationSettings": NotRequired[Mapping[str, Any]],
        "Scte20PlusEmbeddedDestinationSettings": NotRequired[Mapping[str, Any]],
        "Scte27DestinationSettings": NotRequired[Mapping[str, Any]],
        "SmpteTtDestinationSettings": NotRequired[Mapping[str, Any]],
        "TeletextDestinationSettings": NotRequired[Mapping[str, Any]],
        "TtmlDestinationSettings": NotRequired[TtmlDestinationSettingsTypeDef],
        "WebvttDestinationSettings": NotRequired[WebvttDestinationSettingsTypeDef],
    },
)
KeyProviderSettingsTypeDef = TypedDict(
    "KeyProviderSettingsTypeDef",
    {
        "StaticKeySettings": NotRequired[StaticKeySettingsTypeDef],
    },
)
AudioSelectorSettingsExtraOutputTypeDef = TypedDict(
    "AudioSelectorSettingsExtraOutputTypeDef",
    {
        "AudioHlsRenditionSelection": NotRequired[AudioHlsRenditionSelectionTypeDef],
        "AudioLanguageSelection": NotRequired[AudioLanguageSelectionTypeDef],
        "AudioPidSelection": NotRequired[AudioPidSelectionTypeDef],
        "AudioTrackSelection": NotRequired[AudioTrackSelectionExtraOutputTypeDef],
    },
)
AudioSelectorSettingsOutputTypeDef = TypedDict(
    "AudioSelectorSettingsOutputTypeDef",
    {
        "AudioHlsRenditionSelection": NotRequired[AudioHlsRenditionSelectionTypeDef],
        "AudioLanguageSelection": NotRequired[AudioLanguageSelectionTypeDef],
        "AudioPidSelection": NotRequired[AudioPidSelectionTypeDef],
        "AudioTrackSelection": NotRequired[AudioTrackSelectionOutputTypeDef],
    },
)
AudioSelectorSettingsTypeDef = TypedDict(
    "AudioSelectorSettingsTypeDef",
    {
        "AudioHlsRenditionSelection": NotRequired[AudioHlsRenditionSelectionTypeDef],
        "AudioLanguageSelection": NotRequired[AudioLanguageSelectionTypeDef],
        "AudioPidSelection": NotRequired[AudioPidSelectionTypeDef],
        "AudioTrackSelection": NotRequired[AudioTrackSelectionTypeDef],
    },
)
AvailConfigurationTypeDef = TypedDict(
    "AvailConfigurationTypeDef",
    {
        "AvailSettings": NotRequired[AvailSettingsTypeDef],
        "Scte35SegmentationScope": NotRequired[Scte35SegmentationScopeType],
    },
)
CaptionSelectorSettingsExtraOutputTypeDef = TypedDict(
    "CaptionSelectorSettingsExtraOutputTypeDef",
    {
        "AncillarySourceSettings": NotRequired[AncillarySourceSettingsTypeDef],
        "AribSourceSettings": NotRequired[Dict[str, Any]],
        "DvbSubSourceSettings": NotRequired[DvbSubSourceSettingsTypeDef],
        "EmbeddedSourceSettings": NotRequired[EmbeddedSourceSettingsTypeDef],
        "Scte20SourceSettings": NotRequired[Scte20SourceSettingsTypeDef],
        "Scte27SourceSettings": NotRequired[Scte27SourceSettingsTypeDef],
        "TeletextSourceSettings": NotRequired[TeletextSourceSettingsTypeDef],
    },
)
CaptionSelectorSettingsOutputTypeDef = TypedDict(
    "CaptionSelectorSettingsOutputTypeDef",
    {
        "AncillarySourceSettings": NotRequired[AncillarySourceSettingsTypeDef],
        "AribSourceSettings": NotRequired[Dict[str, Any]],
        "DvbSubSourceSettings": NotRequired[DvbSubSourceSettingsTypeDef],
        "EmbeddedSourceSettings": NotRequired[EmbeddedSourceSettingsTypeDef],
        "Scte20SourceSettings": NotRequired[Scte20SourceSettingsTypeDef],
        "Scte27SourceSettings": NotRequired[Scte27SourceSettingsTypeDef],
        "TeletextSourceSettings": NotRequired[TeletextSourceSettingsTypeDef],
    },
)
CaptionSelectorSettingsTypeDef = TypedDict(
    "CaptionSelectorSettingsTypeDef",
    {
        "AncillarySourceSettings": NotRequired[AncillarySourceSettingsTypeDef],
        "AribSourceSettings": NotRequired[Mapping[str, Any]],
        "DvbSubSourceSettings": NotRequired[DvbSubSourceSettingsTypeDef],
        "EmbeddedSourceSettings": NotRequired[EmbeddedSourceSettingsTypeDef],
        "Scte20SourceSettings": NotRequired[Scte20SourceSettingsTypeDef],
        "Scte27SourceSettings": NotRequired[Scte27SourceSettingsTypeDef],
        "TeletextSourceSettings": NotRequired[TeletextSourceSettingsTypeDef],
    },
)
ListOfferingsResponseTypeDef = TypedDict(
    "ListOfferingsResponseTypeDef",
    {
        "Offerings": List[OfferingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListReservationsResponseTypeDef = TypedDict(
    "ListReservationsResponseTypeDef",
    {
        "Reservations": List[ReservationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
PurchaseOfferingResponseTypeDef = TypedDict(
    "PurchaseOfferingResponseTypeDef",
    {
        "Reservation": ReservationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateReservationResponseTypeDef = TypedDict(
    "UpdateReservationResponseTypeDef",
    {
        "Reservation": ReservationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateInputSecurityGroupResponseTypeDef = TypedDict(
    "CreateInputSecurityGroupResponseTypeDef",
    {
        "SecurityGroup": InputSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListInputSecurityGroupsResponseTypeDef = TypedDict(
    "ListInputSecurityGroupsResponseTypeDef",
    {
        "InputSecurityGroups": List[InputSecurityGroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateInputSecurityGroupResponseTypeDef = TypedDict(
    "UpdateInputSecurityGroupResponseTypeDef",
    {
        "SecurityGroup": InputSecurityGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ArchiveContainerSettingsTypeDef = TypedDict(
    "ArchiveContainerSettingsTypeDef",
    {
        "M2tsSettings": NotRequired[M2tsSettingsTypeDef],
        "RawSettings": NotRequired[Mapping[str, Any]],
    },
)
UdpContainerSettingsTypeDef = TypedDict(
    "UdpContainerSettingsTypeDef",
    {
        "M2tsSettings": NotRequired[M2tsSettingsTypeDef],
    },
)
GlobalConfigurationOutputTypeDef = TypedDict(
    "GlobalConfigurationOutputTypeDef",
    {
        "InitialAudioGain": NotRequired[int],
        "InputEndAction": NotRequired[GlobalConfigurationInputEndActionType],
        "InputLossBehavior": NotRequired[InputLossBehaviorTypeDef],
        "OutputLockingMode": NotRequired[GlobalConfigurationOutputLockingModeType],
        "OutputTimingSource": NotRequired[GlobalConfigurationOutputTimingSourceType],
        "SupportLowFramerateInputs": NotRequired[GlobalConfigurationLowFramerateInputsType],
        "OutputLockingSettings": NotRequired[OutputLockingSettingsOutputTypeDef],
    },
)
GlobalConfigurationTypeDef = TypedDict(
    "GlobalConfigurationTypeDef",
    {
        "InitialAudioGain": NotRequired[int],
        "InputEndAction": NotRequired[GlobalConfigurationInputEndActionType],
        "InputLossBehavior": NotRequired[InputLossBehaviorTypeDef],
        "OutputLockingMode": NotRequired[GlobalConfigurationOutputLockingModeType],
        "OutputTimingSource": NotRequired[GlobalConfigurationOutputTimingSourceType],
        "SupportLowFramerateInputs": NotRequired[GlobalConfigurationLowFramerateInputsType],
        "OutputLockingSettings": NotRequired[OutputLockingSettingsTypeDef],
    },
)
FailoverConditionTypeDef = TypedDict(
    "FailoverConditionTypeDef",
    {
        "FailoverConditionSettings": NotRequired[FailoverConditionSettingsTypeDef],
    },
)
FrameCaptureGroupSettingsTypeDef = TypedDict(
    "FrameCaptureGroupSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
        "FrameCaptureCdnSettings": NotRequired[FrameCaptureCdnSettingsTypeDef],
    },
)
H264SettingsOutputTypeDef = TypedDict(
    "H264SettingsOutputTypeDef",
    {
        "AdaptiveQuantization": NotRequired[H264AdaptiveQuantizationType],
        "AfdSignaling": NotRequired[AfdSignalingType],
        "Bitrate": NotRequired[int],
        "BufFillPct": NotRequired[int],
        "BufSize": NotRequired[int],
        "ColorMetadata": NotRequired[H264ColorMetadataType],
        "ColorSpaceSettings": NotRequired[H264ColorSpaceSettingsOutputTypeDef],
        "EntropyEncoding": NotRequired[H264EntropyEncodingType],
        "FilterSettings": NotRequired[H264FilterSettingsTypeDef],
        "FixedAfd": NotRequired[FixedAfdType],
        "FlickerAq": NotRequired[H264FlickerAqType],
        "ForceFieldPictures": NotRequired[H264ForceFieldPicturesType],
        "FramerateControl": NotRequired[H264FramerateControlType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopBReference": NotRequired[H264GopBReferenceType],
        "GopClosedCadence": NotRequired[int],
        "GopNumBFrames": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[H264GopSizeUnitsType],
        "Level": NotRequired[H264LevelType],
        "LookAheadRateControl": NotRequired[H264LookAheadRateControlType],
        "MaxBitrate": NotRequired[int],
        "MinIInterval": NotRequired[int],
        "NumRefFrames": NotRequired[int],
        "ParControl": NotRequired[H264ParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "Profile": NotRequired[H264ProfileType],
        "QualityLevel": NotRequired[H264QualityLevelType],
        "QvbrQualityLevel": NotRequired[int],
        "RateControlMode": NotRequired[H264RateControlModeType],
        "ScanType": NotRequired[H264ScanTypeType],
        "SceneChangeDetect": NotRequired[H264SceneChangeDetectType],
        "Slices": NotRequired[int],
        "Softness": NotRequired[int],
        "SpatialAq": NotRequired[H264SpatialAqType],
        "SubgopLength": NotRequired[H264SubGopLengthType],
        "Syntax": NotRequired[H264SyntaxType],
        "TemporalAq": NotRequired[H264TemporalAqType],
        "TimecodeInsertion": NotRequired[H264TimecodeInsertionBehaviorType],
        "TimecodeBurninSettings": NotRequired[TimecodeBurninSettingsTypeDef],
    },
)
H264SettingsTypeDef = TypedDict(
    "H264SettingsTypeDef",
    {
        "AdaptiveQuantization": NotRequired[H264AdaptiveQuantizationType],
        "AfdSignaling": NotRequired[AfdSignalingType],
        "Bitrate": NotRequired[int],
        "BufFillPct": NotRequired[int],
        "BufSize": NotRequired[int],
        "ColorMetadata": NotRequired[H264ColorMetadataType],
        "ColorSpaceSettings": NotRequired[H264ColorSpaceSettingsTypeDef],
        "EntropyEncoding": NotRequired[H264EntropyEncodingType],
        "FilterSettings": NotRequired[H264FilterSettingsTypeDef],
        "FixedAfd": NotRequired[FixedAfdType],
        "FlickerAq": NotRequired[H264FlickerAqType],
        "ForceFieldPictures": NotRequired[H264ForceFieldPicturesType],
        "FramerateControl": NotRequired[H264FramerateControlType],
        "FramerateDenominator": NotRequired[int],
        "FramerateNumerator": NotRequired[int],
        "GopBReference": NotRequired[H264GopBReferenceType],
        "GopClosedCadence": NotRequired[int],
        "GopNumBFrames": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[H264GopSizeUnitsType],
        "Level": NotRequired[H264LevelType],
        "LookAheadRateControl": NotRequired[H264LookAheadRateControlType],
        "MaxBitrate": NotRequired[int],
        "MinIInterval": NotRequired[int],
        "NumRefFrames": NotRequired[int],
        "ParControl": NotRequired[H264ParControlType],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "Profile": NotRequired[H264ProfileType],
        "QualityLevel": NotRequired[H264QualityLevelType],
        "QvbrQualityLevel": NotRequired[int],
        "RateControlMode": NotRequired[H264RateControlModeType],
        "ScanType": NotRequired[H264ScanTypeType],
        "SceneChangeDetect": NotRequired[H264SceneChangeDetectType],
        "Slices": NotRequired[int],
        "Softness": NotRequired[int],
        "SpatialAq": NotRequired[H264SpatialAqType],
        "SubgopLength": NotRequired[H264SubGopLengthType],
        "Syntax": NotRequired[H264SyntaxType],
        "TemporalAq": NotRequired[H264TemporalAqType],
        "TimecodeInsertion": NotRequired[H264TimecodeInsertionBehaviorType],
        "TimecodeBurninSettings": NotRequired[TimecodeBurninSettingsTypeDef],
    },
)
Mpeg2SettingsTypeDef = TypedDict(
    "Mpeg2SettingsTypeDef",
    {
        "FramerateDenominator": int,
        "FramerateNumerator": int,
        "AdaptiveQuantization": NotRequired[Mpeg2AdaptiveQuantizationType],
        "AfdSignaling": NotRequired[AfdSignalingType],
        "ColorMetadata": NotRequired[Mpeg2ColorMetadataType],
        "ColorSpace": NotRequired[Mpeg2ColorSpaceType],
        "DisplayAspectRatio": NotRequired[Mpeg2DisplayRatioType],
        "FilterSettings": NotRequired[Mpeg2FilterSettingsTypeDef],
        "FixedAfd": NotRequired[FixedAfdType],
        "GopClosedCadence": NotRequired[int],
        "GopNumBFrames": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[Mpeg2GopSizeUnitsType],
        "ScanType": NotRequired[Mpeg2ScanTypeType],
        "SubgopLength": NotRequired[Mpeg2SubGopLengthType],
        "TimecodeInsertion": NotRequired[Mpeg2TimecodeInsertionBehaviorType],
        "TimecodeBurninSettings": NotRequired[TimecodeBurninSettingsTypeDef],
    },
)
H265SettingsOutputTypeDef = TypedDict(
    "H265SettingsOutputTypeDef",
    {
        "FramerateDenominator": int,
        "FramerateNumerator": int,
        "AdaptiveQuantization": NotRequired[H265AdaptiveQuantizationType],
        "AfdSignaling": NotRequired[AfdSignalingType],
        "AlternativeTransferFunction": NotRequired[H265AlternativeTransferFunctionType],
        "Bitrate": NotRequired[int],
        "BufSize": NotRequired[int],
        "ColorMetadata": NotRequired[H265ColorMetadataType],
        "ColorSpaceSettings": NotRequired[H265ColorSpaceSettingsOutputTypeDef],
        "FilterSettings": NotRequired[H265FilterSettingsTypeDef],
        "FixedAfd": NotRequired[FixedAfdType],
        "FlickerAq": NotRequired[H265FlickerAqType],
        "GopClosedCadence": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[H265GopSizeUnitsType],
        "Level": NotRequired[H265LevelType],
        "LookAheadRateControl": NotRequired[H265LookAheadRateControlType],
        "MaxBitrate": NotRequired[int],
        "MinIInterval": NotRequired[int],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "Profile": NotRequired[H265ProfileType],
        "QvbrQualityLevel": NotRequired[int],
        "RateControlMode": NotRequired[H265RateControlModeType],
        "ScanType": NotRequired[H265ScanTypeType],
        "SceneChangeDetect": NotRequired[H265SceneChangeDetectType],
        "Slices": NotRequired[int],
        "Tier": NotRequired[H265TierType],
        "TimecodeInsertion": NotRequired[H265TimecodeInsertionBehaviorType],
        "TimecodeBurninSettings": NotRequired[TimecodeBurninSettingsTypeDef],
        "MvOverPictureBoundaries": NotRequired[H265MvOverPictureBoundariesType],
        "MvTemporalPredictor": NotRequired[H265MvTemporalPredictorType],
        "TileHeight": NotRequired[int],
        "TilePadding": NotRequired[H265TilePaddingType],
        "TileWidth": NotRequired[int],
        "TreeblockSize": NotRequired[H265TreeblockSizeType],
    },
)
H265SettingsTypeDef = TypedDict(
    "H265SettingsTypeDef",
    {
        "FramerateDenominator": int,
        "FramerateNumerator": int,
        "AdaptiveQuantization": NotRequired[H265AdaptiveQuantizationType],
        "AfdSignaling": NotRequired[AfdSignalingType],
        "AlternativeTransferFunction": NotRequired[H265AlternativeTransferFunctionType],
        "Bitrate": NotRequired[int],
        "BufSize": NotRequired[int],
        "ColorMetadata": NotRequired[H265ColorMetadataType],
        "ColorSpaceSettings": NotRequired[H265ColorSpaceSettingsTypeDef],
        "FilterSettings": NotRequired[H265FilterSettingsTypeDef],
        "FixedAfd": NotRequired[FixedAfdType],
        "FlickerAq": NotRequired[H265FlickerAqType],
        "GopClosedCadence": NotRequired[int],
        "GopSize": NotRequired[float],
        "GopSizeUnits": NotRequired[H265GopSizeUnitsType],
        "Level": NotRequired[H265LevelType],
        "LookAheadRateControl": NotRequired[H265LookAheadRateControlType],
        "MaxBitrate": NotRequired[int],
        "MinIInterval": NotRequired[int],
        "ParDenominator": NotRequired[int],
        "ParNumerator": NotRequired[int],
        "Profile": NotRequired[H265ProfileType],
        "QvbrQualityLevel": NotRequired[int],
        "RateControlMode": NotRequired[H265RateControlModeType],
        "ScanType": NotRequired[H265ScanTypeType],
        "SceneChangeDetect": NotRequired[H265SceneChangeDetectType],
        "Slices": NotRequired[int],
        "Tier": NotRequired[H265TierType],
        "TimecodeInsertion": NotRequired[H265TimecodeInsertionBehaviorType],
        "TimecodeBurninSettings": NotRequired[TimecodeBurninSettingsTypeDef],
        "MvOverPictureBoundaries": NotRequired[H265MvOverPictureBoundariesType],
        "MvTemporalPredictor": NotRequired[H265MvTemporalPredictorType],
        "TileHeight": NotRequired[int],
        "TilePadding": NotRequired[H265TilePaddingType],
        "TileWidth": NotRequired[int],
        "TreeblockSize": NotRequired[H265TreeblockSizeType],
    },
)
InputPrepareScheduleActionSettingsExtraOutputTypeDef = TypedDict(
    "InputPrepareScheduleActionSettingsExtraOutputTypeDef",
    {
        "InputAttachmentNameReference": NotRequired[str],
        "InputClippingSettings": NotRequired[InputClippingSettingsTypeDef],
        "UrlPath": NotRequired[List[str]],
    },
)
InputPrepareScheduleActionSettingsOutputTypeDef = TypedDict(
    "InputPrepareScheduleActionSettingsOutputTypeDef",
    {
        "InputAttachmentNameReference": NotRequired[str],
        "InputClippingSettings": NotRequired[InputClippingSettingsTypeDef],
        "UrlPath": NotRequired[List[str]],
    },
)
InputPrepareScheduleActionSettingsTypeDef = TypedDict(
    "InputPrepareScheduleActionSettingsTypeDef",
    {
        "InputAttachmentNameReference": NotRequired[str],
        "InputClippingSettings": NotRequired[InputClippingSettingsTypeDef],
        "UrlPath": NotRequired[Sequence[str]],
    },
)
InputSwitchScheduleActionSettingsExtraOutputTypeDef = TypedDict(
    "InputSwitchScheduleActionSettingsExtraOutputTypeDef",
    {
        "InputAttachmentNameReference": str,
        "InputClippingSettings": NotRequired[InputClippingSettingsTypeDef],
        "UrlPath": NotRequired[List[str]],
    },
)
InputSwitchScheduleActionSettingsOutputTypeDef = TypedDict(
    "InputSwitchScheduleActionSettingsOutputTypeDef",
    {
        "InputAttachmentNameReference": str,
        "InputClippingSettings": NotRequired[InputClippingSettingsTypeDef],
        "UrlPath": NotRequired[List[str]],
    },
)
InputSwitchScheduleActionSettingsTypeDef = TypedDict(
    "InputSwitchScheduleActionSettingsTypeDef",
    {
        "InputAttachmentNameReference": str,
        "InputClippingSettings": NotRequired[InputClippingSettingsTypeDef],
        "UrlPath": NotRequired[Sequence[str]],
    },
)
UpdateInputDeviceRequestRequestTypeDef = TypedDict(
    "UpdateInputDeviceRequestRequestTypeDef",
    {
        "InputDeviceId": str,
        "HdDeviceSettings": NotRequired[InputDeviceConfigurableSettingsTypeDef],
        "Name": NotRequired[str],
        "UhdDeviceSettings": NotRequired[InputDeviceConfigurableSettingsTypeDef],
        "AvailabilityZone": NotRequired[str],
    },
)
DescribeInputDeviceResponseTypeDef = TypedDict(
    "DescribeInputDeviceResponseTypeDef",
    {
        "Arn": str,
        "ConnectionState": InputDeviceConnectionStateType,
        "DeviceSettingsSyncState": DeviceSettingsSyncStateType,
        "DeviceUpdateStatus": DeviceUpdateStatusType,
        "HdDeviceSettings": InputDeviceHdSettingsTypeDef,
        "Id": str,
        "MacAddress": str,
        "Name": str,
        "NetworkSettings": InputDeviceNetworkSettingsTypeDef,
        "SerialNumber": str,
        "Type": InputDeviceTypeType,
        "UhdDeviceSettings": InputDeviceUhdSettingsTypeDef,
        "Tags": Dict[str, str],
        "AvailabilityZone": str,
        "MedialiveInputArns": List[str],
        "OutputType": InputDeviceOutputTypeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InputDeviceSummaryTypeDef = TypedDict(
    "InputDeviceSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "ConnectionState": NotRequired[InputDeviceConnectionStateType],
        "DeviceSettingsSyncState": NotRequired[DeviceSettingsSyncStateType],
        "DeviceUpdateStatus": NotRequired[DeviceUpdateStatusType],
        "HdDeviceSettings": NotRequired[InputDeviceHdSettingsTypeDef],
        "Id": NotRequired[str],
        "MacAddress": NotRequired[str],
        "Name": NotRequired[str],
        "NetworkSettings": NotRequired[InputDeviceNetworkSettingsTypeDef],
        "SerialNumber": NotRequired[str],
        "Type": NotRequired[InputDeviceTypeType],
        "UhdDeviceSettings": NotRequired[InputDeviceUhdSettingsTypeDef],
        "Tags": NotRequired[Dict[str, str]],
        "AvailabilityZone": NotRequired[str],
        "MedialiveInputArns": NotRequired[List[str]],
        "OutputType": NotRequired[InputDeviceOutputTypeType],
    },
)
UpdateInputDeviceResponseTypeDef = TypedDict(
    "UpdateInputDeviceResponseTypeDef",
    {
        "Arn": str,
        "ConnectionState": InputDeviceConnectionStateType,
        "DeviceSettingsSyncState": DeviceSettingsSyncStateType,
        "DeviceUpdateStatus": DeviceUpdateStatusType,
        "HdDeviceSettings": InputDeviceHdSettingsTypeDef,
        "Id": str,
        "MacAddress": str,
        "Name": str,
        "NetworkSettings": InputDeviceNetworkSettingsTypeDef,
        "SerialNumber": str,
        "Type": InputDeviceTypeType,
        "UhdDeviceSettings": InputDeviceUhdSettingsTypeDef,
        "Tags": Dict[str, str],
        "AvailabilityZone": str,
        "MedialiveInputArns": List[str],
        "OutputType": InputDeviceOutputTypeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HlsSettingsTypeDef = TypedDict(
    "HlsSettingsTypeDef",
    {
        "AudioOnlyHlsSettings": NotRequired[AudioOnlyHlsSettingsTypeDef],
        "Fmp4HlsSettings": NotRequired[Fmp4HlsSettingsTypeDef],
        "FrameCaptureHlsSettings": NotRequired[Mapping[str, Any]],
        "StandardHlsSettings": NotRequired[StandardHlsSettingsTypeDef],
    },
)
CreateSignalMapResponseTypeDef = TypedDict(
    "CreateSignalMapResponseTypeDef",
    {
        "Arn": str,
        "CloudWatchAlarmTemplateGroupIds": List[str],
        "CreatedAt": datetime,
        "Description": str,
        "DiscoveryEntryPointArn": str,
        "ErrorMessage": str,
        "EventBridgeRuleTemplateGroupIds": List[str],
        "FailedMediaResourceMap": Dict[str, MediaResourceTypeDef],
        "Id": str,
        "LastDiscoveredAt": datetime,
        "LastSuccessfulMonitorDeployment": SuccessfulMonitorDeploymentTypeDef,
        "MediaResourceMap": Dict[str, MediaResourceTypeDef],
        "ModifiedAt": datetime,
        "MonitorChangesPendingDeployment": bool,
        "MonitorDeployment": MonitorDeploymentTypeDef,
        "Name": str,
        "Status": SignalMapStatusType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSignalMapResponseTypeDef = TypedDict(
    "GetSignalMapResponseTypeDef",
    {
        "Arn": str,
        "CloudWatchAlarmTemplateGroupIds": List[str],
        "CreatedAt": datetime,
        "Description": str,
        "DiscoveryEntryPointArn": str,
        "ErrorMessage": str,
        "EventBridgeRuleTemplateGroupIds": List[str],
        "FailedMediaResourceMap": Dict[str, MediaResourceTypeDef],
        "Id": str,
        "LastDiscoveredAt": datetime,
        "LastSuccessfulMonitorDeployment": SuccessfulMonitorDeploymentTypeDef,
        "MediaResourceMap": Dict[str, MediaResourceTypeDef],
        "ModifiedAt": datetime,
        "MonitorChangesPendingDeployment": bool,
        "MonitorDeployment": MonitorDeploymentTypeDef,
        "Name": str,
        "Status": SignalMapStatusType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartDeleteMonitorDeploymentResponseTypeDef = TypedDict(
    "StartDeleteMonitorDeploymentResponseTypeDef",
    {
        "Arn": str,
        "CloudWatchAlarmTemplateGroupIds": List[str],
        "CreatedAt": datetime,
        "Description": str,
        "DiscoveryEntryPointArn": str,
        "ErrorMessage": str,
        "EventBridgeRuleTemplateGroupIds": List[str],
        "FailedMediaResourceMap": Dict[str, MediaResourceTypeDef],
        "Id": str,
        "LastDiscoveredAt": datetime,
        "LastSuccessfulMonitorDeployment": SuccessfulMonitorDeploymentTypeDef,
        "MediaResourceMap": Dict[str, MediaResourceTypeDef],
        "ModifiedAt": datetime,
        "MonitorChangesPendingDeployment": bool,
        "MonitorDeployment": MonitorDeploymentTypeDef,
        "Name": str,
        "Status": SignalMapStatusType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartMonitorDeploymentResponseTypeDef = TypedDict(
    "StartMonitorDeploymentResponseTypeDef",
    {
        "Arn": str,
        "CloudWatchAlarmTemplateGroupIds": List[str],
        "CreatedAt": datetime,
        "Description": str,
        "DiscoveryEntryPointArn": str,
        "ErrorMessage": str,
        "EventBridgeRuleTemplateGroupIds": List[str],
        "FailedMediaResourceMap": Dict[str, MediaResourceTypeDef],
        "Id": str,
        "LastDiscoveredAt": datetime,
        "LastSuccessfulMonitorDeployment": SuccessfulMonitorDeploymentTypeDef,
        "MediaResourceMap": Dict[str, MediaResourceTypeDef],
        "ModifiedAt": datetime,
        "MonitorChangesPendingDeployment": bool,
        "MonitorDeployment": MonitorDeploymentTypeDef,
        "Name": str,
        "Status": SignalMapStatusType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartUpdateSignalMapResponseTypeDef = TypedDict(
    "StartUpdateSignalMapResponseTypeDef",
    {
        "Arn": str,
        "CloudWatchAlarmTemplateGroupIds": List[str],
        "CreatedAt": datetime,
        "Description": str,
        "DiscoveryEntryPointArn": str,
        "ErrorMessage": str,
        "EventBridgeRuleTemplateGroupIds": List[str],
        "FailedMediaResourceMap": Dict[str, MediaResourceTypeDef],
        "Id": str,
        "LastDiscoveredAt": datetime,
        "LastSuccessfulMonitorDeployment": SuccessfulMonitorDeploymentTypeDef,
        "MediaResourceMap": Dict[str, MediaResourceTypeDef],
        "ModifiedAt": datetime,
        "MonitorChangesPendingDeployment": bool,
        "MonitorDeployment": MonitorDeploymentTypeDef,
        "Name": str,
        "Status": SignalMapStatusType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteMultiplexResponseTypeDef = TypedDict(
    "DeleteMultiplexResponseTypeDef",
    {
        "Arn": str,
        "AvailabilityZones": List[str],
        "Destinations": List[MultiplexOutputDestinationTypeDef],
        "Id": str,
        "MultiplexSettings": MultiplexSettingsTypeDef,
        "Name": str,
        "PipelinesRunningCount": int,
        "ProgramCount": int,
        "State": MultiplexStateType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeMultiplexResponseTypeDef = TypedDict(
    "DescribeMultiplexResponseTypeDef",
    {
        "Arn": str,
        "AvailabilityZones": List[str],
        "Destinations": List[MultiplexOutputDestinationTypeDef],
        "Id": str,
        "MultiplexSettings": MultiplexSettingsTypeDef,
        "Name": str,
        "PipelinesRunningCount": int,
        "ProgramCount": int,
        "State": MultiplexStateType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MultiplexTypeDef = TypedDict(
    "MultiplexTypeDef",
    {
        "Arn": NotRequired[str],
        "AvailabilityZones": NotRequired[List[str]],
        "Destinations": NotRequired[List[MultiplexOutputDestinationTypeDef]],
        "Id": NotRequired[str],
        "MultiplexSettings": NotRequired[MultiplexSettingsTypeDef],
        "Name": NotRequired[str],
        "PipelinesRunningCount": NotRequired[int],
        "ProgramCount": NotRequired[int],
        "State": NotRequired[MultiplexStateType],
        "Tags": NotRequired[Dict[str, str]],
    },
)
StartMultiplexResponseTypeDef = TypedDict(
    "StartMultiplexResponseTypeDef",
    {
        "Arn": str,
        "AvailabilityZones": List[str],
        "Destinations": List[MultiplexOutputDestinationTypeDef],
        "Id": str,
        "MultiplexSettings": MultiplexSettingsTypeDef,
        "Name": str,
        "PipelinesRunningCount": int,
        "ProgramCount": int,
        "State": MultiplexStateType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopMultiplexResponseTypeDef = TypedDict(
    "StopMultiplexResponseTypeDef",
    {
        "Arn": str,
        "AvailabilityZones": List[str],
        "Destinations": List[MultiplexOutputDestinationTypeDef],
        "Id": str,
        "MultiplexSettings": MultiplexSettingsTypeDef,
        "Name": str,
        "PipelinesRunningCount": int,
        "ProgramCount": int,
        "State": MultiplexStateType,
        "Tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListMultiplexesResponseTypeDef = TypedDict(
    "ListMultiplexesResponseTypeDef",
    {
        "Multiplexes": List[MultiplexSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
MultiplexProgramSettingsTypeDef = TypedDict(
    "MultiplexProgramSettingsTypeDef",
    {
        "ProgramNumber": int,
        "PreferredChannelPipeline": NotRequired[PreferredChannelPipelineType],
        "ServiceDescriptor": NotRequired[MultiplexProgramServiceDescriptorTypeDef],
        "VideoSettings": NotRequired[MultiplexVideoSettingsTypeDef],
    },
)
AudioWatermarkSettingsTypeDef = TypedDict(
    "AudioWatermarkSettingsTypeDef",
    {
        "NielsenWatermarksSettings": NotRequired[NielsenWatermarksSettingsTypeDef],
    },
)
OutputDestinationUnionTypeDef = Union[OutputDestinationTypeDef, OutputDestinationExtraOutputTypeDef]
Scte35DescriptorSettingsTypeDef = TypedDict(
    "Scte35DescriptorSettingsTypeDef",
    {
        "SegmentationDescriptorScte35DescriptorSettings": Scte35SegmentationDescriptorTypeDef,
    },
)
SrtSettingsRequestTypeDef = TypedDict(
    "SrtSettingsRequestTypeDef",
    {
        "SrtCallerSources": NotRequired[Sequence[SrtCallerSourceRequestTypeDef]],
    },
)
SrtSettingsTypeDef = TypedDict(
    "SrtSettingsTypeDef",
    {
        "SrtCallerSources": NotRequired[List[SrtCallerSourceTypeDef]],
    },
)
DescribeThumbnailsResponseTypeDef = TypedDict(
    "DescribeThumbnailsResponseTypeDef",
    {
        "ThumbnailDetails": List[ThumbnailDetailTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
VideoSelectorTypeDef = TypedDict(
    "VideoSelectorTypeDef",
    {
        "ColorSpace": NotRequired[VideoSelectorColorSpaceType],
        "ColorSpaceSettings": NotRequired[VideoSelectorColorSpaceSettingsTypeDef],
        "ColorSpaceUsage": NotRequired[VideoSelectorColorSpaceUsageType],
        "SelectorSettings": NotRequired[VideoSelectorSettingsTypeDef],
    },
)
CaptionDescriptionOutputTypeDef = TypedDict(
    "CaptionDescriptionOutputTypeDef",
    {
        "CaptionSelectorName": str,
        "Name": str,
        "Accessibility": NotRequired[AccessibilityTypeType],
        "DestinationSettings": NotRequired[CaptionDestinationSettingsOutputTypeDef],
        "LanguageCode": NotRequired[str],
        "LanguageDescription": NotRequired[str],
        "CaptionDashRoles": NotRequired[List[DashRoleCaptionType]],
        "DvbDashAccessibility": NotRequired[DvbDashAccessibilityType],
    },
)
CaptionDescriptionTypeDef = TypedDict(
    "CaptionDescriptionTypeDef",
    {
        "CaptionSelectorName": str,
        "Name": str,
        "Accessibility": NotRequired[AccessibilityTypeType],
        "DestinationSettings": NotRequired[CaptionDestinationSettingsTypeDef],
        "LanguageCode": NotRequired[str],
        "LanguageDescription": NotRequired[str],
        "CaptionDashRoles": NotRequired[Sequence[DashRoleCaptionType]],
        "DvbDashAccessibility": NotRequired[DvbDashAccessibilityType],
    },
)
HlsGroupSettingsOutputTypeDef = TypedDict(
    "HlsGroupSettingsOutputTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
        "AdMarkers": NotRequired[List[HlsAdMarkersType]],
        "BaseUrlContent": NotRequired[str],
        "BaseUrlContent1": NotRequired[str],
        "BaseUrlManifest": NotRequired[str],
        "BaseUrlManifest1": NotRequired[str],
        "CaptionLanguageMappings": NotRequired[List[CaptionLanguageMappingTypeDef]],
        "CaptionLanguageSetting": NotRequired[HlsCaptionLanguageSettingType],
        "ClientCache": NotRequired[HlsClientCacheType],
        "CodecSpecification": NotRequired[HlsCodecSpecificationType],
        "ConstantIv": NotRequired[str],
        "DirectoryStructure": NotRequired[HlsDirectoryStructureType],
        "DiscontinuityTags": NotRequired[HlsDiscontinuityTagsType],
        "EncryptionType": NotRequired[HlsEncryptionTypeType],
        "HlsCdnSettings": NotRequired[HlsCdnSettingsTypeDef],
        "HlsId3SegmentTagging": NotRequired[HlsId3SegmentTaggingStateType],
        "IFrameOnlyPlaylists": NotRequired[IFrameOnlyPlaylistTypeType],
        "IncompleteSegmentBehavior": NotRequired[HlsIncompleteSegmentBehaviorType],
        "IndexNSegments": NotRequired[int],
        "InputLossAction": NotRequired[InputLossActionForHlsOutType],
        "IvInManifest": NotRequired[HlsIvInManifestType],
        "IvSource": NotRequired[HlsIvSourceType],
        "KeepSegments": NotRequired[int],
        "KeyFormat": NotRequired[str],
        "KeyFormatVersions": NotRequired[str],
        "KeyProviderSettings": NotRequired[KeyProviderSettingsTypeDef],
        "ManifestCompression": NotRequired[HlsManifestCompressionType],
        "ManifestDurationFormat": NotRequired[HlsManifestDurationFormatType],
        "MinSegmentLength": NotRequired[int],
        "Mode": NotRequired[HlsModeType],
        "OutputSelection": NotRequired[HlsOutputSelectionType],
        "ProgramDateTime": NotRequired[HlsProgramDateTimeType],
        "ProgramDateTimeClock": NotRequired[HlsProgramDateTimeClockType],
        "ProgramDateTimePeriod": NotRequired[int],
        "RedundantManifest": NotRequired[HlsRedundantManifestType],
        "SegmentLength": NotRequired[int],
        "SegmentationMode": NotRequired[HlsSegmentationModeType],
        "SegmentsPerSubdirectory": NotRequired[int],
        "StreamInfResolution": NotRequired[HlsStreamInfResolutionType],
        "TimedMetadataId3Frame": NotRequired[HlsTimedMetadataId3FrameType],
        "TimedMetadataId3Period": NotRequired[int],
        "TimestampDeltaMilliseconds": NotRequired[int],
        "TsFileMode": NotRequired[HlsTsFileModeType],
    },
)
HlsGroupSettingsTypeDef = TypedDict(
    "HlsGroupSettingsTypeDef",
    {
        "Destination": OutputLocationRefTypeDef,
        "AdMarkers": NotRequired[Sequence[HlsAdMarkersType]],
        "BaseUrlContent": NotRequired[str],
        "BaseUrlContent1": NotRequired[str],
        "BaseUrlManifest": NotRequired[str],
        "BaseUrlManifest1": NotRequired[str],
        "CaptionLanguageMappings": NotRequired[Sequence[CaptionLanguageMappingTypeDef]],
        "CaptionLanguageSetting": NotRequired[HlsCaptionLanguageSettingType],
        "ClientCache": NotRequired[HlsClientCacheType],
        "CodecSpecification": NotRequired[HlsCodecSpecificationType],
        "ConstantIv": NotRequired[str],
        "DirectoryStructure": NotRequired[HlsDirectoryStructureType],
        "DiscontinuityTags": NotRequired[HlsDiscontinuityTagsType],
        "EncryptionType": NotRequired[HlsEncryptionTypeType],
        "HlsCdnSettings": NotRequired[HlsCdnSettingsTypeDef],
        "HlsId3SegmentTagging": NotRequired[HlsId3SegmentTaggingStateType],
        "IFrameOnlyPlaylists": NotRequired[IFrameOnlyPlaylistTypeType],
        "IncompleteSegmentBehavior": NotRequired[HlsIncompleteSegmentBehaviorType],
        "IndexNSegments": NotRequired[int],
        "InputLossAction": NotRequired[InputLossActionForHlsOutType],
        "IvInManifest": NotRequired[HlsIvInManifestType],
        "IvSource": NotRequired[HlsIvSourceType],
        "KeepSegments": NotRequired[int],
        "KeyFormat": NotRequired[str],
        "KeyFormatVersions": NotRequired[str],
        "KeyProviderSettings": NotRequired[KeyProviderSettingsTypeDef],
        "ManifestCompression": NotRequired[HlsManifestCompressionType],
        "ManifestDurationFormat": NotRequired[HlsManifestDurationFormatType],
        "MinSegmentLength": NotRequired[int],
        "Mode": NotRequired[HlsModeType],
        "OutputSelection": NotRequired[HlsOutputSelectionType],
        "ProgramDateTime": NotRequired[HlsProgramDateTimeType],
        "ProgramDateTimeClock": NotRequired[HlsProgramDateTimeClockType],
        "ProgramDateTimePeriod": NotRequired[int],
        "RedundantManifest": NotRequired[HlsRedundantManifestType],
        "SegmentLength": NotRequired[int],
        "SegmentationMode": NotRequired[HlsSegmentationModeType],
        "SegmentsPerSubdirectory": NotRequired[int],
        "StreamInfResolution": NotRequired[HlsStreamInfResolutionType],
        "TimedMetadataId3Frame": NotRequired[HlsTimedMetadataId3FrameType],
        "TimedMetadataId3Period": NotRequired[int],
        "TimestampDeltaMilliseconds": NotRequired[int],
        "TsFileMode": NotRequired[HlsTsFileModeType],
    },
)
AudioSelectorExtraOutputTypeDef = TypedDict(
    "AudioSelectorExtraOutputTypeDef",
    {
        "Name": str,
        "SelectorSettings": NotRequired[AudioSelectorSettingsExtraOutputTypeDef],
    },
)
AudioSelectorOutputTypeDef = TypedDict(
    "AudioSelectorOutputTypeDef",
    {
        "Name": str,
        "SelectorSettings": NotRequired[AudioSelectorSettingsOutputTypeDef],
    },
)
AudioSelectorTypeDef = TypedDict(
    "AudioSelectorTypeDef",
    {
        "Name": str,
        "SelectorSettings": NotRequired[AudioSelectorSettingsTypeDef],
    },
)
CaptionSelectorExtraOutputTypeDef = TypedDict(
    "CaptionSelectorExtraOutputTypeDef",
    {
        "Name": str,
        "LanguageCode": NotRequired[str],
        "SelectorSettings": NotRequired[CaptionSelectorSettingsExtraOutputTypeDef],
    },
)
CaptionSelectorOutputTypeDef = TypedDict(
    "CaptionSelectorOutputTypeDef",
    {
        "Name": str,
        "LanguageCode": NotRequired[str],
        "SelectorSettings": NotRequired[CaptionSelectorSettingsOutputTypeDef],
    },
)
CaptionSelectorTypeDef = TypedDict(
    "CaptionSelectorTypeDef",
    {
        "Name": str,
        "LanguageCode": NotRequired[str],
        "SelectorSettings": NotRequired[CaptionSelectorSettingsTypeDef],
    },
)
ArchiveOutputSettingsTypeDef = TypedDict(
    "ArchiveOutputSettingsTypeDef",
    {
        "ContainerSettings": ArchiveContainerSettingsTypeDef,
        "Extension": NotRequired[str],
        "NameModifier": NotRequired[str],
    },
)
UdpOutputSettingsTypeDef = TypedDict(
    "UdpOutputSettingsTypeDef",
    {
        "ContainerSettings": UdpContainerSettingsTypeDef,
        "Destination": OutputLocationRefTypeDef,
        "BufferMsec": NotRequired[int],
        "FecOutputSettings": NotRequired[FecOutputSettingsTypeDef],
    },
)
AutomaticInputFailoverSettingsExtraOutputTypeDef = TypedDict(
    "AutomaticInputFailoverSettingsExtraOutputTypeDef",
    {
        "SecondaryInputId": str,
        "ErrorClearTimeMsec": NotRequired[int],
        "FailoverConditions": NotRequired[List[FailoverConditionTypeDef]],
        "InputPreference": NotRequired[InputPreferenceType],
    },
)
AutomaticInputFailoverSettingsOutputTypeDef = TypedDict(
    "AutomaticInputFailoverSettingsOutputTypeDef",
    {
        "SecondaryInputId": str,
        "ErrorClearTimeMsec": NotRequired[int],
        "FailoverConditions": NotRequired[List[FailoverConditionTypeDef]],
        "InputPreference": NotRequired[InputPreferenceType],
    },
)
AutomaticInputFailoverSettingsTypeDef = TypedDict(
    "AutomaticInputFailoverSettingsTypeDef",
    {
        "SecondaryInputId": str,
        "ErrorClearTimeMsec": NotRequired[int],
        "FailoverConditions": NotRequired[Sequence[FailoverConditionTypeDef]],
        "InputPreference": NotRequired[InputPreferenceType],
    },
)
VideoCodecSettingsOutputTypeDef = TypedDict(
    "VideoCodecSettingsOutputTypeDef",
    {
        "FrameCaptureSettings": NotRequired[FrameCaptureSettingsTypeDef],
        "H264Settings": NotRequired[H264SettingsOutputTypeDef],
        "H265Settings": NotRequired[H265SettingsOutputTypeDef],
        "Mpeg2Settings": NotRequired[Mpeg2SettingsTypeDef],
    },
)
VideoCodecSettingsTypeDef = TypedDict(
    "VideoCodecSettingsTypeDef",
    {
        "FrameCaptureSettings": NotRequired[FrameCaptureSettingsTypeDef],
        "H264Settings": NotRequired[H264SettingsTypeDef],
        "H265Settings": NotRequired[H265SettingsTypeDef],
        "Mpeg2Settings": NotRequired[Mpeg2SettingsTypeDef],
    },
)
ListInputDevicesResponseTypeDef = TypedDict(
    "ListInputDevicesResponseTypeDef",
    {
        "InputDevices": List[InputDeviceSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
HlsOutputSettingsTypeDef = TypedDict(
    "HlsOutputSettingsTypeDef",
    {
        "HlsSettings": HlsSettingsTypeDef,
        "H265PackagingType": NotRequired[HlsH265PackagingTypeType],
        "NameModifier": NotRequired[str],
        "SegmentModifier": NotRequired[str],
    },
)
CreateMultiplexResponseTypeDef = TypedDict(
    "CreateMultiplexResponseTypeDef",
    {
        "Multiplex": MultiplexTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateMultiplexResponseTypeDef = TypedDict(
    "UpdateMultiplexResponseTypeDef",
    {
        "Multiplex": MultiplexTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateMultiplexProgramRequestRequestTypeDef = TypedDict(
    "CreateMultiplexProgramRequestRequestTypeDef",
    {
        "MultiplexId": str,
        "MultiplexProgramSettings": MultiplexProgramSettingsTypeDef,
        "ProgramName": str,
        "RequestId": str,
    },
)
DeleteMultiplexProgramResponseTypeDef = TypedDict(
    "DeleteMultiplexProgramResponseTypeDef",
    {
        "ChannelId": str,
        "MultiplexProgramSettings": MultiplexProgramSettingsTypeDef,
        "PacketIdentifiersMap": MultiplexProgramPacketIdentifiersMapTypeDef,
        "PipelineDetails": List[MultiplexProgramPipelineDetailTypeDef],
        "ProgramName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeMultiplexProgramResponseTypeDef = TypedDict(
    "DescribeMultiplexProgramResponseTypeDef",
    {
        "ChannelId": str,
        "MultiplexProgramSettings": MultiplexProgramSettingsTypeDef,
        "PacketIdentifiersMap": MultiplexProgramPacketIdentifiersMapTypeDef,
        "PipelineDetails": List[MultiplexProgramPipelineDetailTypeDef],
        "ProgramName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MultiplexProgramTypeDef = TypedDict(
    "MultiplexProgramTypeDef",
    {
        "ChannelId": NotRequired[str],
        "MultiplexProgramSettings": NotRequired[MultiplexProgramSettingsTypeDef],
        "PacketIdentifiersMap": NotRequired[MultiplexProgramPacketIdentifiersMapTypeDef],
        "PipelineDetails": NotRequired[List[MultiplexProgramPipelineDetailTypeDef]],
        "ProgramName": NotRequired[str],
    },
)
UpdateMultiplexProgramRequestRequestTypeDef = TypedDict(
    "UpdateMultiplexProgramRequestRequestTypeDef",
    {
        "MultiplexId": str,
        "ProgramName": str,
        "MultiplexProgramSettings": NotRequired[MultiplexProgramSettingsTypeDef],
    },
)
AudioDescriptionOutputTypeDef = TypedDict(
    "AudioDescriptionOutputTypeDef",
    {
        "AudioSelectorName": str,
        "Name": str,
        "AudioNormalizationSettings": NotRequired[AudioNormalizationSettingsTypeDef],
        "AudioType": NotRequired[AudioTypeType],
        "AudioTypeControl": NotRequired[AudioDescriptionAudioTypeControlType],
        "AudioWatermarkingSettings": NotRequired[AudioWatermarkSettingsTypeDef],
        "CodecSettings": NotRequired[AudioCodecSettingsOutputTypeDef],
        "LanguageCode": NotRequired[str],
        "LanguageCodeControl": NotRequired[AudioDescriptionLanguageCodeControlType],
        "RemixSettings": NotRequired[RemixSettingsOutputTypeDef],
        "StreamName": NotRequired[str],
        "AudioDashRoles": NotRequired[List[DashRoleAudioType]],
        "DvbDashAccessibility": NotRequired[DvbDashAccessibilityType],
    },
)
AudioDescriptionTypeDef = TypedDict(
    "AudioDescriptionTypeDef",
    {
        "AudioSelectorName": str,
        "Name": str,
        "AudioNormalizationSettings": NotRequired[AudioNormalizationSettingsTypeDef],
        "AudioType": NotRequired[AudioTypeType],
        "AudioTypeControl": NotRequired[AudioDescriptionAudioTypeControlType],
        "AudioWatermarkingSettings": NotRequired[AudioWatermarkSettingsTypeDef],
        "CodecSettings": NotRequired[AudioCodecSettingsTypeDef],
        "LanguageCode": NotRequired[str],
        "LanguageCodeControl": NotRequired[AudioDescriptionLanguageCodeControlType],
        "RemixSettings": NotRequired[RemixSettingsTypeDef],
        "StreamName": NotRequired[str],
        "AudioDashRoles": NotRequired[Sequence[DashRoleAudioType]],
        "DvbDashAccessibility": NotRequired[DvbDashAccessibilityType],
    },
)
UpdateChannelClassRequestRequestTypeDef = TypedDict(
    "UpdateChannelClassRequestRequestTypeDef",
    {
        "ChannelClass": ChannelClassType,
        "ChannelId": str,
        "Destinations": NotRequired[Sequence[OutputDestinationUnionTypeDef]],
    },
)
Scte35DescriptorTypeDef = TypedDict(
    "Scte35DescriptorTypeDef",
    {
        "Scte35DescriptorSettings": Scte35DescriptorSettingsTypeDef,
    },
)
CreateInputRequestRequestTypeDef = TypedDict(
    "CreateInputRequestRequestTypeDef",
    {
        "Destinations": NotRequired[Sequence[InputDestinationRequestTypeDef]],
        "InputDevices": NotRequired[Sequence[InputDeviceSettingsTypeDef]],
        "InputSecurityGroups": NotRequired[Sequence[str]],
        "MediaConnectFlows": NotRequired[Sequence[MediaConnectFlowRequestTypeDef]],
        "Name": NotRequired[str],
        "RequestId": NotRequired[str],
        "RoleArn": NotRequired[str],
        "Sources": NotRequired[Sequence[InputSourceRequestTypeDef]],
        "Tags": NotRequired[Mapping[str, str]],
        "Type": NotRequired[InputTypeType],
        "Vpc": NotRequired[InputVpcRequestTypeDef],
        "SrtSettings": NotRequired[SrtSettingsRequestTypeDef],
    },
)
UpdateInputRequestRequestTypeDef = TypedDict(
    "UpdateInputRequestRequestTypeDef",
    {
        "InputId": str,
        "Destinations": NotRequired[Sequence[InputDestinationRequestTypeDef]],
        "InputDevices": NotRequired[Sequence[InputDeviceRequestTypeDef]],
        "InputSecurityGroups": NotRequired[Sequence[str]],
        "MediaConnectFlows": NotRequired[Sequence[MediaConnectFlowRequestTypeDef]],
        "Name": NotRequired[str],
        "RoleArn": NotRequired[str],
        "Sources": NotRequired[Sequence[InputSourceRequestTypeDef]],
        "SrtSettings": NotRequired[SrtSettingsRequestTypeDef],
    },
)
DescribeInputResponseTypeDef = TypedDict(
    "DescribeInputResponseTypeDef",
    {
        "Arn": str,
        "AttachedChannels": List[str],
        "Destinations": List[InputDestinationTypeDef],
        "Id": str,
        "InputClass": InputClassType,
        "InputDevices": List[InputDeviceSettingsTypeDef],
        "InputPartnerIds": List[str],
        "InputSourceType": InputSourceTypeType,
        "MediaConnectFlows": List[MediaConnectFlowTypeDef],
        "Name": str,
        "RoleArn": str,
        "SecurityGroups": List[str],
        "Sources": List[InputSourceTypeDef],
        "State": InputStateType,
        "Tags": Dict[str, str],
        "Type": InputTypeType,
        "SrtSettings": SrtSettingsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InputTypeDef = TypedDict(
    "InputTypeDef",
    {
        "Arn": NotRequired[str],
        "AttachedChannels": NotRequired[List[str]],
        "Destinations": NotRequired[List[InputDestinationTypeDef]],
        "Id": NotRequired[str],
        "InputClass": NotRequired[InputClassType],
        "InputDevices": NotRequired[List[InputDeviceSettingsTypeDef]],
        "InputPartnerIds": NotRequired[List[str]],
        "InputSourceType": NotRequired[InputSourceTypeType],
        "MediaConnectFlows": NotRequired[List[MediaConnectFlowTypeDef]],
        "Name": NotRequired[str],
        "RoleArn": NotRequired[str],
        "SecurityGroups": NotRequired[List[str]],
        "Sources": NotRequired[List[InputSourceTypeDef]],
        "State": NotRequired[InputStateType],
        "Tags": NotRequired[Dict[str, str]],
        "Type": NotRequired[InputTypeType],
        "SrtSettings": NotRequired[SrtSettingsTypeDef],
    },
)
OutputGroupSettingsOutputTypeDef = TypedDict(
    "OutputGroupSettingsOutputTypeDef",
    {
        "ArchiveGroupSettings": NotRequired[ArchiveGroupSettingsTypeDef],
        "FrameCaptureGroupSettings": NotRequired[FrameCaptureGroupSettingsTypeDef],
        "HlsGroupSettings": NotRequired[HlsGroupSettingsOutputTypeDef],
        "MediaPackageGroupSettings": NotRequired[MediaPackageGroupSettingsTypeDef],
        "MsSmoothGroupSettings": NotRequired[MsSmoothGroupSettingsTypeDef],
        "MultiplexGroupSettings": NotRequired[Dict[str, Any]],
        "RtmpGroupSettings": NotRequired[RtmpGroupSettingsOutputTypeDef],
        "UdpGroupSettings": NotRequired[UdpGroupSettingsTypeDef],
        "CmafIngestGroupSettings": NotRequired[CmafIngestGroupSettingsTypeDef],
    },
)
OutputGroupSettingsTypeDef = TypedDict(
    "OutputGroupSettingsTypeDef",
    {
        "ArchiveGroupSettings": NotRequired[ArchiveGroupSettingsTypeDef],
        "FrameCaptureGroupSettings": NotRequired[FrameCaptureGroupSettingsTypeDef],
        "HlsGroupSettings": NotRequired[HlsGroupSettingsTypeDef],
        "MediaPackageGroupSettings": NotRequired[MediaPackageGroupSettingsTypeDef],
        "MsSmoothGroupSettings": NotRequired[MsSmoothGroupSettingsTypeDef],
        "MultiplexGroupSettings": NotRequired[Mapping[str, Any]],
        "RtmpGroupSettings": NotRequired[RtmpGroupSettingsTypeDef],
        "UdpGroupSettings": NotRequired[UdpGroupSettingsTypeDef],
        "CmafIngestGroupSettings": NotRequired[CmafIngestGroupSettingsTypeDef],
    },
)
InputSettingsExtraOutputTypeDef = TypedDict(
    "InputSettingsExtraOutputTypeDef",
    {
        "AudioSelectors": NotRequired[List[AudioSelectorExtraOutputTypeDef]],
        "CaptionSelectors": NotRequired[List[CaptionSelectorExtraOutputTypeDef]],
        "DeblockFilter": NotRequired[InputDeblockFilterType],
        "DenoiseFilter": NotRequired[InputDenoiseFilterType],
        "FilterStrength": NotRequired[int],
        "InputFilter": NotRequired[InputFilterType],
        "NetworkInputSettings": NotRequired[NetworkInputSettingsTypeDef],
        "Scte35Pid": NotRequired[int],
        "Smpte2038DataPreference": NotRequired[Smpte2038DataPreferenceType],
        "SourceEndBehavior": NotRequired[InputSourceEndBehaviorType],
        "VideoSelector": NotRequired[VideoSelectorTypeDef],
    },
)
InputSettingsOutputTypeDef = TypedDict(
    "InputSettingsOutputTypeDef",
    {
        "AudioSelectors": NotRequired[List[AudioSelectorOutputTypeDef]],
        "CaptionSelectors": NotRequired[List[CaptionSelectorOutputTypeDef]],
        "DeblockFilter": NotRequired[InputDeblockFilterType],
        "DenoiseFilter": NotRequired[InputDenoiseFilterType],
        "FilterStrength": NotRequired[int],
        "InputFilter": NotRequired[InputFilterType],
        "NetworkInputSettings": NotRequired[NetworkInputSettingsTypeDef],
        "Scte35Pid": NotRequired[int],
        "Smpte2038DataPreference": NotRequired[Smpte2038DataPreferenceType],
        "SourceEndBehavior": NotRequired[InputSourceEndBehaviorType],
        "VideoSelector": NotRequired[VideoSelectorTypeDef],
    },
)
InputSettingsTypeDef = TypedDict(
    "InputSettingsTypeDef",
    {
        "AudioSelectors": NotRequired[Sequence[AudioSelectorTypeDef]],
        "CaptionSelectors": NotRequired[Sequence[CaptionSelectorTypeDef]],
        "DeblockFilter": NotRequired[InputDeblockFilterType],
        "DenoiseFilter": NotRequired[InputDenoiseFilterType],
        "FilterStrength": NotRequired[int],
        "InputFilter": NotRequired[InputFilterType],
        "NetworkInputSettings": NotRequired[NetworkInputSettingsTypeDef],
        "Scte35Pid": NotRequired[int],
        "Smpte2038DataPreference": NotRequired[Smpte2038DataPreferenceType],
        "SourceEndBehavior": NotRequired[InputSourceEndBehaviorType],
        "VideoSelector": NotRequired[VideoSelectorTypeDef],
    },
)
VideoDescriptionOutputTypeDef = TypedDict(
    "VideoDescriptionOutputTypeDef",
    {
        "Name": str,
        "CodecSettings": NotRequired[VideoCodecSettingsOutputTypeDef],
        "Height": NotRequired[int],
        "RespondToAfd": NotRequired[VideoDescriptionRespondToAfdType],
        "ScalingBehavior": NotRequired[VideoDescriptionScalingBehaviorType],
        "Sharpness": NotRequired[int],
        "Width": NotRequired[int],
    },
)
VideoDescriptionTypeDef = TypedDict(
    "VideoDescriptionTypeDef",
    {
        "Name": str,
        "CodecSettings": NotRequired[VideoCodecSettingsTypeDef],
        "Height": NotRequired[int],
        "RespondToAfd": NotRequired[VideoDescriptionRespondToAfdType],
        "ScalingBehavior": NotRequired[VideoDescriptionScalingBehaviorType],
        "Sharpness": NotRequired[int],
        "Width": NotRequired[int],
    },
)
OutputSettingsTypeDef = TypedDict(
    "OutputSettingsTypeDef",
    {
        "ArchiveOutputSettings": NotRequired[ArchiveOutputSettingsTypeDef],
        "FrameCaptureOutputSettings": NotRequired[FrameCaptureOutputSettingsTypeDef],
        "HlsOutputSettings": NotRequired[HlsOutputSettingsTypeDef],
        "MediaPackageOutputSettings": NotRequired[Mapping[str, Any]],
        "MsSmoothOutputSettings": NotRequired[MsSmoothOutputSettingsTypeDef],
        "MultiplexOutputSettings": NotRequired[MultiplexOutputSettingsTypeDef],
        "RtmpOutputSettings": NotRequired[RtmpOutputSettingsTypeDef],
        "UdpOutputSettings": NotRequired[UdpOutputSettingsTypeDef],
        "CmafIngestOutputSettings": NotRequired[CmafIngestOutputSettingsTypeDef],
    },
)
CreateMultiplexProgramResponseTypeDef = TypedDict(
    "CreateMultiplexProgramResponseTypeDef",
    {
        "MultiplexProgram": MultiplexProgramTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateMultiplexProgramResponseTypeDef = TypedDict(
    "UpdateMultiplexProgramResponseTypeDef",
    {
        "MultiplexProgram": MultiplexProgramTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
Scte35TimeSignalScheduleActionSettingsExtraOutputTypeDef = TypedDict(
    "Scte35TimeSignalScheduleActionSettingsExtraOutputTypeDef",
    {
        "Scte35Descriptors": List[Scte35DescriptorTypeDef],
    },
)
Scte35TimeSignalScheduleActionSettingsOutputTypeDef = TypedDict(
    "Scte35TimeSignalScheduleActionSettingsOutputTypeDef",
    {
        "Scte35Descriptors": List[Scte35DescriptorTypeDef],
    },
)
Scte35TimeSignalScheduleActionSettingsTypeDef = TypedDict(
    "Scte35TimeSignalScheduleActionSettingsTypeDef",
    {
        "Scte35Descriptors": Sequence[Scte35DescriptorTypeDef],
    },
)
CreateInputResponseTypeDef = TypedDict(
    "CreateInputResponseTypeDef",
    {
        "Input": InputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePartnerInputResponseTypeDef = TypedDict(
    "CreatePartnerInputResponseTypeDef",
    {
        "Input": InputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListInputsResponseTypeDef = TypedDict(
    "ListInputsResponseTypeDef",
    {
        "Inputs": List[InputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
UpdateInputResponseTypeDef = TypedDict(
    "UpdateInputResponseTypeDef",
    {
        "Input": InputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InputAttachmentExtraOutputTypeDef = TypedDict(
    "InputAttachmentExtraOutputTypeDef",
    {
        "AutomaticInputFailoverSettings": NotRequired[
            AutomaticInputFailoverSettingsExtraOutputTypeDef
        ],
        "InputAttachmentName": NotRequired[str],
        "InputId": NotRequired[str],
        "InputSettings": NotRequired[InputSettingsExtraOutputTypeDef],
    },
)
InputAttachmentOutputTypeDef = TypedDict(
    "InputAttachmentOutputTypeDef",
    {
        "AutomaticInputFailoverSettings": NotRequired[AutomaticInputFailoverSettingsOutputTypeDef],
        "InputAttachmentName": NotRequired[str],
        "InputId": NotRequired[str],
        "InputSettings": NotRequired[InputSettingsOutputTypeDef],
    },
)
InputAttachmentTypeDef = TypedDict(
    "InputAttachmentTypeDef",
    {
        "AutomaticInputFailoverSettings": NotRequired[AutomaticInputFailoverSettingsTypeDef],
        "InputAttachmentName": NotRequired[str],
        "InputId": NotRequired[str],
        "InputSettings": NotRequired[InputSettingsTypeDef],
    },
)
OutputTypeDef = TypedDict(
    "OutputTypeDef",
    {
        "OutputSettings": OutputSettingsTypeDef,
        "AudioDescriptionNames": NotRequired[Sequence[str]],
        "CaptionDescriptionNames": NotRequired[Sequence[str]],
        "OutputName": NotRequired[str],
        "VideoDescriptionName": NotRequired[str],
    },
)
ScheduleActionSettingsExtraOutputTypeDef = TypedDict(
    "ScheduleActionSettingsExtraOutputTypeDef",
    {
        "HlsId3SegmentTaggingSettings": NotRequired[
            HlsId3SegmentTaggingScheduleActionSettingsTypeDef
        ],
        "HlsTimedMetadataSettings": NotRequired[HlsTimedMetadataScheduleActionSettingsTypeDef],
        "InputPrepareSettings": NotRequired[InputPrepareScheduleActionSettingsExtraOutputTypeDef],
        "InputSwitchSettings": NotRequired[InputSwitchScheduleActionSettingsExtraOutputTypeDef],
        "MotionGraphicsImageActivateSettings": NotRequired[
            MotionGraphicsActivateScheduleActionSettingsTypeDef
        ],
        "MotionGraphicsImageDeactivateSettings": NotRequired[Dict[str, Any]],
        "PauseStateSettings": NotRequired[PauseStateScheduleActionSettingsExtraOutputTypeDef],
        "Scte35InputSettings": NotRequired[Scte35InputScheduleActionSettingsTypeDef],
        "Scte35ReturnToNetworkSettings": NotRequired[
            Scte35ReturnToNetworkScheduleActionSettingsTypeDef
        ],
        "Scte35SpliceInsertSettings": NotRequired[Scte35SpliceInsertScheduleActionSettingsTypeDef],
        "Scte35TimeSignalSettings": NotRequired[
            Scte35TimeSignalScheduleActionSettingsExtraOutputTypeDef
        ],
        "StaticImageActivateSettings": NotRequired[
            StaticImageActivateScheduleActionSettingsTypeDef
        ],
        "StaticImageDeactivateSettings": NotRequired[
            StaticImageDeactivateScheduleActionSettingsTypeDef
        ],
        "StaticImageOutputActivateSettings": NotRequired[
            StaticImageOutputActivateScheduleActionSettingsExtraOutputTypeDef
        ],
        "StaticImageOutputDeactivateSettings": NotRequired[
            StaticImageOutputDeactivateScheduleActionSettingsExtraOutputTypeDef
        ],
    },
)
ScheduleActionSettingsOutputTypeDef = TypedDict(
    "ScheduleActionSettingsOutputTypeDef",
    {
        "HlsId3SegmentTaggingSettings": NotRequired[
            HlsId3SegmentTaggingScheduleActionSettingsTypeDef
        ],
        "HlsTimedMetadataSettings": NotRequired[HlsTimedMetadataScheduleActionSettingsTypeDef],
        "InputPrepareSettings": NotRequired[InputPrepareScheduleActionSettingsOutputTypeDef],
        "InputSwitchSettings": NotRequired[InputSwitchScheduleActionSettingsOutputTypeDef],
        "MotionGraphicsImageActivateSettings": NotRequired[
            MotionGraphicsActivateScheduleActionSettingsTypeDef
        ],
        "MotionGraphicsImageDeactivateSettings": NotRequired[Dict[str, Any]],
        "PauseStateSettings": NotRequired[PauseStateScheduleActionSettingsOutputTypeDef],
        "Scte35InputSettings": NotRequired[Scte35InputScheduleActionSettingsTypeDef],
        "Scte35ReturnToNetworkSettings": NotRequired[
            Scte35ReturnToNetworkScheduleActionSettingsTypeDef
        ],
        "Scte35SpliceInsertSettings": NotRequired[Scte35SpliceInsertScheduleActionSettingsTypeDef],
        "Scte35TimeSignalSettings": NotRequired[
            Scte35TimeSignalScheduleActionSettingsOutputTypeDef
        ],
        "StaticImageActivateSettings": NotRequired[
            StaticImageActivateScheduleActionSettingsTypeDef
        ],
        "StaticImageDeactivateSettings": NotRequired[
            StaticImageDeactivateScheduleActionSettingsTypeDef
        ],
        "StaticImageOutputActivateSettings": NotRequired[
            StaticImageOutputActivateScheduleActionSettingsOutputTypeDef
        ],
        "StaticImageOutputDeactivateSettings": NotRequired[
            StaticImageOutputDeactivateScheduleActionSettingsOutputTypeDef
        ],
    },
)
ScheduleActionSettingsTypeDef = TypedDict(
    "ScheduleActionSettingsTypeDef",
    {
        "HlsId3SegmentTaggingSettings": NotRequired[
            HlsId3SegmentTaggingScheduleActionSettingsTypeDef
        ],
        "HlsTimedMetadataSettings": NotRequired[HlsTimedMetadataScheduleActionSettingsTypeDef],
        "InputPrepareSettings": NotRequired[InputPrepareScheduleActionSettingsTypeDef],
        "InputSwitchSettings": NotRequired[InputSwitchScheduleActionSettingsTypeDef],
        "MotionGraphicsImageActivateSettings": NotRequired[
            MotionGraphicsActivateScheduleActionSettingsTypeDef
        ],
        "MotionGraphicsImageDeactivateSettings": NotRequired[Mapping[str, Any]],
        "PauseStateSettings": NotRequired[PauseStateScheduleActionSettingsTypeDef],
        "Scte35InputSettings": NotRequired[Scte35InputScheduleActionSettingsTypeDef],
        "Scte35ReturnToNetworkSettings": NotRequired[
            Scte35ReturnToNetworkScheduleActionSettingsTypeDef
        ],
        "Scte35SpliceInsertSettings": NotRequired[Scte35SpliceInsertScheduleActionSettingsTypeDef],
        "Scte35TimeSignalSettings": NotRequired[Scte35TimeSignalScheduleActionSettingsTypeDef],
        "StaticImageActivateSettings": NotRequired[
            StaticImageActivateScheduleActionSettingsTypeDef
        ],
        "StaticImageDeactivateSettings": NotRequired[
            StaticImageDeactivateScheduleActionSettingsTypeDef
        ],
        "StaticImageOutputActivateSettings": NotRequired[
            StaticImageOutputActivateScheduleActionSettingsTypeDef
        ],
        "StaticImageOutputDeactivateSettings": NotRequired[
            StaticImageOutputDeactivateScheduleActionSettingsTypeDef
        ],
    },
)
ChannelSummaryTypeDef = TypedDict(
    "ChannelSummaryTypeDef",
    {
        "Arn": NotRequired[str],
        "CdiInputSpecification": NotRequired[CdiInputSpecificationTypeDef],
        "ChannelClass": NotRequired[ChannelClassType],
        "Destinations": NotRequired[List[OutputDestinationOutputTypeDef]],
        "EgressEndpoints": NotRequired[List[ChannelEgressEndpointTypeDef]],
        "Id": NotRequired[str],
        "InputAttachments": NotRequired[List[InputAttachmentOutputTypeDef]],
        "InputSpecification": NotRequired[InputSpecificationTypeDef],
        "LogLevel": NotRequired[LogLevelType],
        "Maintenance": NotRequired[MaintenanceStatusTypeDef],
        "Name": NotRequired[str],
        "PipelinesRunningCount": NotRequired[int],
        "RoleArn": NotRequired[str],
        "State": NotRequired[ChannelStateType],
        "Tags": NotRequired[Dict[str, str]],
        "Vpc": NotRequired[VpcOutputSettingsDescriptionTypeDef],
    },
)
InputAttachmentUnionTypeDef = Union[InputAttachmentTypeDef, InputAttachmentExtraOutputTypeDef]
OutputGroupOutputTypeDef = TypedDict(
    "OutputGroupOutputTypeDef",
    {
        "OutputGroupSettings": OutputGroupSettingsOutputTypeDef,
        "Outputs": List[OutputTypeDef],
        "Name": NotRequired[str],
    },
)
OutputGroupTypeDef = TypedDict(
    "OutputGroupTypeDef",
    {
        "OutputGroupSettings": OutputGroupSettingsTypeDef,
        "Outputs": Sequence[OutputTypeDef],
        "Name": NotRequired[str],
    },
)
ScheduleActionExtraOutputTypeDef = TypedDict(
    "ScheduleActionExtraOutputTypeDef",
    {
        "ActionName": str,
        "ScheduleActionSettings": ScheduleActionSettingsExtraOutputTypeDef,
        "ScheduleActionStartSettings": ScheduleActionStartSettingsExtraOutputTypeDef,
    },
)
ScheduleActionOutputTypeDef = TypedDict(
    "ScheduleActionOutputTypeDef",
    {
        "ActionName": str,
        "ScheduleActionSettings": ScheduleActionSettingsOutputTypeDef,
        "ScheduleActionStartSettings": ScheduleActionStartSettingsOutputTypeDef,
    },
)
ScheduleActionTypeDef = TypedDict(
    "ScheduleActionTypeDef",
    {
        "ActionName": str,
        "ScheduleActionSettings": ScheduleActionSettingsTypeDef,
        "ScheduleActionStartSettings": ScheduleActionStartSettingsTypeDef,
    },
)
ListChannelsResponseTypeDef = TypedDict(
    "ListChannelsResponseTypeDef",
    {
        "Channels": List[ChannelSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
EncoderSettingsOutputTypeDef = TypedDict(
    "EncoderSettingsOutputTypeDef",
    {
        "AudioDescriptions": List[AudioDescriptionOutputTypeDef],
        "OutputGroups": List[OutputGroupOutputTypeDef],
        "TimecodeConfig": TimecodeConfigTypeDef,
        "VideoDescriptions": List[VideoDescriptionOutputTypeDef],
        "AvailBlanking": NotRequired[AvailBlankingTypeDef],
        "AvailConfiguration": NotRequired[AvailConfigurationTypeDef],
        "BlackoutSlate": NotRequired[BlackoutSlateTypeDef],
        "CaptionDescriptions": NotRequired[List[CaptionDescriptionOutputTypeDef]],
        "FeatureActivations": NotRequired[FeatureActivationsTypeDef],
        "GlobalConfiguration": NotRequired[GlobalConfigurationOutputTypeDef],
        "MotionGraphicsConfiguration": NotRequired[MotionGraphicsConfigurationOutputTypeDef],
        "NielsenConfiguration": NotRequired[NielsenConfigurationTypeDef],
        "ThumbnailConfiguration": NotRequired[ThumbnailConfigurationTypeDef],
        "ColorCorrectionSettings": NotRequired[ColorCorrectionSettingsOutputTypeDef],
    },
)
EncoderSettingsTypeDef = TypedDict(
    "EncoderSettingsTypeDef",
    {
        "AudioDescriptions": Sequence[AudioDescriptionTypeDef],
        "OutputGroups": Sequence[OutputGroupTypeDef],
        "TimecodeConfig": TimecodeConfigTypeDef,
        "VideoDescriptions": Sequence[VideoDescriptionTypeDef],
        "AvailBlanking": NotRequired[AvailBlankingTypeDef],
        "AvailConfiguration": NotRequired[AvailConfigurationTypeDef],
        "BlackoutSlate": NotRequired[BlackoutSlateTypeDef],
        "CaptionDescriptions": NotRequired[Sequence[CaptionDescriptionTypeDef]],
        "FeatureActivations": NotRequired[FeatureActivationsTypeDef],
        "GlobalConfiguration": NotRequired[GlobalConfigurationTypeDef],
        "MotionGraphicsConfiguration": NotRequired[MotionGraphicsConfigurationTypeDef],
        "NielsenConfiguration": NotRequired[NielsenConfigurationTypeDef],
        "ThumbnailConfiguration": NotRequired[ThumbnailConfigurationTypeDef],
        "ColorCorrectionSettings": NotRequired[ColorCorrectionSettingsTypeDef],
    },
)
BatchScheduleActionCreateResultTypeDef = TypedDict(
    "BatchScheduleActionCreateResultTypeDef",
    {
        "ScheduleActions": List[ScheduleActionOutputTypeDef],
    },
)
BatchScheduleActionDeleteResultTypeDef = TypedDict(
    "BatchScheduleActionDeleteResultTypeDef",
    {
        "ScheduleActions": List[ScheduleActionOutputTypeDef],
    },
)
DescribeScheduleResponseTypeDef = TypedDict(
    "DescribeScheduleResponseTypeDef",
    {
        "ScheduleActions": List[ScheduleActionOutputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
BatchScheduleActionCreateRequestTypeDef = TypedDict(
    "BatchScheduleActionCreateRequestTypeDef",
    {
        "ScheduleActions": Sequence[ScheduleActionTypeDef],
    },
)
ChannelTypeDef = TypedDict(
    "ChannelTypeDef",
    {
        "Arn": NotRequired[str],
        "CdiInputSpecification": NotRequired[CdiInputSpecificationTypeDef],
        "ChannelClass": NotRequired[ChannelClassType],
        "Destinations": NotRequired[List[OutputDestinationOutputTypeDef]],
        "EgressEndpoints": NotRequired[List[ChannelEgressEndpointTypeDef]],
        "EncoderSettings": NotRequired[EncoderSettingsOutputTypeDef],
        "Id": NotRequired[str],
        "InputAttachments": NotRequired[List[InputAttachmentOutputTypeDef]],
        "InputSpecification": NotRequired[InputSpecificationTypeDef],
        "LogLevel": NotRequired[LogLevelType],
        "Maintenance": NotRequired[MaintenanceStatusTypeDef],
        "Name": NotRequired[str],
        "PipelineDetails": NotRequired[List[PipelineDetailTypeDef]],
        "PipelinesRunningCount": NotRequired[int],
        "RoleArn": NotRequired[str],
        "State": NotRequired[ChannelStateType],
        "Tags": NotRequired[Dict[str, str]],
        "Vpc": NotRequired[VpcOutputSettingsDescriptionTypeDef],
    },
)
DeleteChannelResponseTypeDef = TypedDict(
    "DeleteChannelResponseTypeDef",
    {
        "Arn": str,
        "CdiInputSpecification": CdiInputSpecificationTypeDef,
        "ChannelClass": ChannelClassType,
        "Destinations": List[OutputDestinationOutputTypeDef],
        "EgressEndpoints": List[ChannelEgressEndpointTypeDef],
        "EncoderSettings": EncoderSettingsOutputTypeDef,
        "Id": str,
        "InputAttachments": List[InputAttachmentOutputTypeDef],
        "InputSpecification": InputSpecificationTypeDef,
        "LogLevel": LogLevelType,
        "Maintenance": MaintenanceStatusTypeDef,
        "Name": str,
        "PipelineDetails": List[PipelineDetailTypeDef],
        "PipelinesRunningCount": int,
        "RoleArn": str,
        "State": ChannelStateType,
        "Tags": Dict[str, str],
        "Vpc": VpcOutputSettingsDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeChannelResponseTypeDef = TypedDict(
    "DescribeChannelResponseTypeDef",
    {
        "Arn": str,
        "CdiInputSpecification": CdiInputSpecificationTypeDef,
        "ChannelClass": ChannelClassType,
        "Destinations": List[OutputDestinationOutputTypeDef],
        "EgressEndpoints": List[ChannelEgressEndpointTypeDef],
        "EncoderSettings": EncoderSettingsOutputTypeDef,
        "Id": str,
        "InputAttachments": List[InputAttachmentOutputTypeDef],
        "InputSpecification": InputSpecificationTypeDef,
        "LogLevel": LogLevelType,
        "Maintenance": MaintenanceStatusTypeDef,
        "Name": str,
        "PipelineDetails": List[PipelineDetailTypeDef],
        "PipelinesRunningCount": int,
        "RoleArn": str,
        "State": ChannelStateType,
        "Tags": Dict[str, str],
        "Vpc": VpcOutputSettingsDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RestartChannelPipelinesResponseTypeDef = TypedDict(
    "RestartChannelPipelinesResponseTypeDef",
    {
        "Arn": str,
        "CdiInputSpecification": CdiInputSpecificationTypeDef,
        "ChannelClass": ChannelClassType,
        "Destinations": List[OutputDestinationOutputTypeDef],
        "EgressEndpoints": List[ChannelEgressEndpointTypeDef],
        "EncoderSettings": EncoderSettingsOutputTypeDef,
        "Id": str,
        "InputAttachments": List[InputAttachmentOutputTypeDef],
        "InputSpecification": InputSpecificationTypeDef,
        "LogLevel": LogLevelType,
        "Maintenance": MaintenanceStatusTypeDef,
        "MaintenanceStatus": str,
        "Name": str,
        "PipelineDetails": List[PipelineDetailTypeDef],
        "PipelinesRunningCount": int,
        "RoleArn": str,
        "State": ChannelStateType,
        "Tags": Dict[str, str],
        "Vpc": VpcOutputSettingsDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartChannelResponseTypeDef = TypedDict(
    "StartChannelResponseTypeDef",
    {
        "Arn": str,
        "CdiInputSpecification": CdiInputSpecificationTypeDef,
        "ChannelClass": ChannelClassType,
        "Destinations": List[OutputDestinationOutputTypeDef],
        "EgressEndpoints": List[ChannelEgressEndpointTypeDef],
        "EncoderSettings": EncoderSettingsOutputTypeDef,
        "Id": str,
        "InputAttachments": List[InputAttachmentOutputTypeDef],
        "InputSpecification": InputSpecificationTypeDef,
        "LogLevel": LogLevelType,
        "Maintenance": MaintenanceStatusTypeDef,
        "Name": str,
        "PipelineDetails": List[PipelineDetailTypeDef],
        "PipelinesRunningCount": int,
        "RoleArn": str,
        "State": ChannelStateType,
        "Tags": Dict[str, str],
        "Vpc": VpcOutputSettingsDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopChannelResponseTypeDef = TypedDict(
    "StopChannelResponseTypeDef",
    {
        "Arn": str,
        "CdiInputSpecification": CdiInputSpecificationTypeDef,
        "ChannelClass": ChannelClassType,
        "Destinations": List[OutputDestinationOutputTypeDef],
        "EgressEndpoints": List[ChannelEgressEndpointTypeDef],
        "EncoderSettings": EncoderSettingsOutputTypeDef,
        "Id": str,
        "InputAttachments": List[InputAttachmentOutputTypeDef],
        "InputSpecification": InputSpecificationTypeDef,
        "LogLevel": LogLevelType,
        "Maintenance": MaintenanceStatusTypeDef,
        "Name": str,
        "PipelineDetails": List[PipelineDetailTypeDef],
        "PipelinesRunningCount": int,
        "RoleArn": str,
        "State": ChannelStateType,
        "Tags": Dict[str, str],
        "Vpc": VpcOutputSettingsDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateChannelRequestRequestTypeDef = TypedDict(
    "CreateChannelRequestRequestTypeDef",
    {
        "CdiInputSpecification": NotRequired[CdiInputSpecificationTypeDef],
        "ChannelClass": NotRequired[ChannelClassType],
        "Destinations": NotRequired[Sequence[OutputDestinationUnionTypeDef]],
        "EncoderSettings": NotRequired[EncoderSettingsTypeDef],
        "InputAttachments": NotRequired[Sequence[InputAttachmentUnionTypeDef]],
        "InputSpecification": NotRequired[InputSpecificationTypeDef],
        "LogLevel": NotRequired[LogLevelType],
        "Maintenance": NotRequired[MaintenanceCreateSettingsTypeDef],
        "Name": NotRequired[str],
        "RequestId": NotRequired[str],
        "Reserved": NotRequired[str],
        "RoleArn": NotRequired[str],
        "Tags": NotRequired[Mapping[str, str]],
        "Vpc": NotRequired[VpcOutputSettingsTypeDef],
    },
)
EncoderSettingsUnionTypeDef = Union[EncoderSettingsTypeDef, EncoderSettingsOutputTypeDef]
UpdateChannelRequestRequestTypeDef = TypedDict(
    "UpdateChannelRequestRequestTypeDef",
    {
        "ChannelId": str,
        "CdiInputSpecification": NotRequired[CdiInputSpecificationTypeDef],
        "Destinations": NotRequired[Sequence[OutputDestinationUnionTypeDef]],
        "EncoderSettings": NotRequired[EncoderSettingsTypeDef],
        "InputAttachments": NotRequired[Sequence[InputAttachmentUnionTypeDef]],
        "InputSpecification": NotRequired[InputSpecificationTypeDef],
        "LogLevel": NotRequired[LogLevelType],
        "Maintenance": NotRequired[MaintenanceUpdateSettingsTypeDef],
        "Name": NotRequired[str],
        "RoleArn": NotRequired[str],
    },
)
BatchUpdateScheduleResponseTypeDef = TypedDict(
    "BatchUpdateScheduleResponseTypeDef",
    {
        "Creates": BatchScheduleActionCreateResultTypeDef,
        "Deletes": BatchScheduleActionDeleteResultTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchUpdateScheduleRequestRequestTypeDef = TypedDict(
    "BatchUpdateScheduleRequestRequestTypeDef",
    {
        "ChannelId": str,
        "Creates": NotRequired[BatchScheduleActionCreateRequestTypeDef],
        "Deletes": NotRequired[BatchScheduleActionDeleteRequestTypeDef],
    },
)
CreateChannelResponseTypeDef = TypedDict(
    "CreateChannelResponseTypeDef",
    {
        "Channel": ChannelTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateChannelClassResponseTypeDef = TypedDict(
    "UpdateChannelClassResponseTypeDef",
    {
        "Channel": ChannelTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateChannelResponseTypeDef = TypedDict(
    "UpdateChannelResponseTypeDef",
    {
        "Channel": ChannelTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
