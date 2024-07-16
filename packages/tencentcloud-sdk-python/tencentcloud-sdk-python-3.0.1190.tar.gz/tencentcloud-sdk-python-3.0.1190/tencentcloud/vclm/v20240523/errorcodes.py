# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# CAM签名/鉴权错误。
AUTHFAILURE = 'AuthFailure'

# 音频解码失败。
FAILEDOPERATION_AUDIODECODEFAILED = 'FailedOperation.AudioDecodeFailed'

# 音频处理失败。
FAILEDOPERATION_AUDIOPROCESSFAILED = 'FailedOperation.AudioProcessFailed'

# 音频处理任务未完成，不能执行翻译结果确认
FAILEDOPERATION_AUDIOPROCESSNOTFINISHED = 'FailedOperation.AudioProcessNotFinished'

# 翻译结果确认任务异常。
FAILEDOPERATION_CONFIRMTASKEXCEPTION = 'FailedOperation.ConfirmTaskException'

# 下载视频出错。
FAILEDOPERATION_DOWNLOADERROR = 'FailedOperation.DownloadError'

# 人脸框太小，无法识别使用。
FAILEDOPERATION_FACESIZETOOSMALL = 'FailedOperation.FaceSizeTooSmall'

# 图片解码失败。
FAILEDOPERATION_IMAGEDECODEFAILED = 'FailedOperation.ImageDecodeFailed'

# 不支持的图片文件。
FAILEDOPERATION_IMAGENOTSUPPORTED = 'FailedOperation.ImageNotSupported'

# 图片分辨率过大。
FAILEDOPERATION_IMAGERESOLUTIONEXCEED = 'FailedOperation.ImageResolutionExceed'

# base64编码后的图片数据过大。
FAILEDOPERATION_IMAGESIZEEXCEED = 'FailedOperation.ImageSizeExceed'

# 服务内部错误，请重试。
FAILEDOPERATION_INNERERROR = 'FailedOperation.InnerError'

# 任务不存在。
FAILEDOPERATION_JOBNOTEXIST = 'FailedOperation.JobNotExist'

# 任务不存在。
FAILEDOPERATION_JOBNOTFOUND = 'FailedOperation.JobNotFound'

# 任务队列已满，请稍后重试。
FAILEDOPERATION_JOBQUEUEFULL = 'FailedOperation.JobQueueFull'

# 内容审核不通过。
FAILEDOPERATION_MODERATIONFAILED = 'FailedOperation.ModerationFailed'

# 后端服务超时。
FAILEDOPERATION_REQUESTTIMEOUT = 'FailedOperation.RequestTimeout'

# 系统内部错误。
FAILEDOPERATION_SERVERERROR = 'FailedOperation.ServerError'

# 任务不存在。
FAILEDOPERATION_TASKNOTEXIST = 'FailedOperation.TaskNotExist'

# 任务状态异常。
FAILEDOPERATION_TASKSTATUSERROR = 'FailedOperation.TaskStatusError'

# 文本未通过审核，请修改后重新尝试。
FAILEDOPERATION_TEXTMODERATIONNOTPASS = 'FailedOperation.TextModerationNotPass'

# 音频翻译结果已确认
FAILEDOPERATION_TRANSLATIONCONFIRMHASFINISHED = 'FailedOperation.TranslationConfirmHasFinished'

# 用户未选择确认音频翻译结果
FAILEDOPERATION_TRANSLATIONNOTNEEDCONFIRM = 'FailedOperation.TranslationNotNeedConfirm'

# 内部错误。
FAILEDOPERATION_UNKNOWERROR = 'FailedOperation.UnKnowError'

# 视频解码失败。
FAILEDOPERATION_VIDEODECODEFAILED = 'FailedOperation.VideoDecodeFailed'

# 视频时长超限制。
FAILEDOPERATION_VIDEODURATIONEXCEED = 'FailedOperation.VideoDurationExceed'

# 视频Fps超限制。
FAILEDOPERATION_VIDEOFPSEXCEED = 'FailedOperation.VideoFpsExceed'

# 视频分辨率超限制。
FAILEDOPERATION_VIDEORESOLUTIONEXCEED = 'FailedOperation.VideoResolutionExceed'

# 视频分辨率超限制。
FAILEDOPERATION_VIDEOSIZEEXCEED = 'FailedOperation.VideoSizeExceed'

# 内部错误。
INTERNALERROR = 'InternalError'

# 参数错误。
INVALIDPARAMETER = 'InvalidParameter'

# 参数不合法。
INVALIDPARAMETER_INVALIDPARAMETER = 'InvalidParameter.InvalidParameter'

# 参数取值错误。
INVALIDPARAMETERVALUE = 'InvalidParameterValue'

# 不支持的视频宽高比。
INVALIDPARAMETERVALUE_INVALIDVIDEOASPECTRATIO = 'InvalidParameterValue.InvalidVideoAspectRatio'

# 视频时长超过限制。
INVALIDPARAMETERVALUE_INVALIDVIDEODURATION = 'InvalidParameterValue.InvalidVideoDuration'

# 不支持的视频FPS。
INVALIDPARAMETERVALUE_INVALIDVIDEOFPS = 'InvalidParameterValue.InvalidVideoFPS'

# 不支持的视频格式。
INVALIDPARAMETERVALUE_INVALIDVIDEOFORMAT = 'InvalidParameterValue.InvalidVideoFormat'

# 不支持的分辨率。
INVALIDPARAMETERVALUE_INVALIDVIDEORESOLUTION = 'InvalidParameterValue.InvalidVideoResolution'

# 图片中没有人脸。
INVALIDPARAMETERVALUE_NOFACEINPHOTO = 'InvalidParameterValue.NoFaceInPhoto'

# 参数字段或者值有误。
INVALIDPARAMETERVALUE_PARAMETERVALUEERROR = 'InvalidParameterValue.ParameterValueError'

# 风格不存在。
INVALIDPARAMETERVALUE_STYLENOTEXIST = 'InvalidParameterValue.StyleNotExist'

# URL格式不合法。
INVALIDPARAMETERVALUE_URLILLEGAL = 'InvalidParameterValue.UrlIllegal'

# 视频大小超过限制。
INVALIDPARAMETERVALUE_VIDEOSIZEEXCEED = 'InvalidParameterValue.VideoSizeExceed'

# 超过配额限制。
LIMITEXCEEDED = 'LimitExceeded'

# 操作被拒绝。
OPERATIONDENIED = 'OperationDenied'

# 请求的次数超过了频率限制。
REQUESTLIMITEXCEEDED = 'RequestLimitExceeded'

# 提交任务数超过最大并发。
REQUESTLIMITEXCEEDED_JOBNUMEXCEED = 'RequestLimitExceeded.JobNumExceed'

# 用户账号超出了限制。
REQUESTLIMITEXCEEDED_UINLIMITEXCEEDED = 'RequestLimitExceeded.UinLimitExceeded'

# 资源不足。
RESOURCEINSUFFICIENT = 'ResourceInsufficient'

# 资源不存在。
RESOURCENOTFOUND = 'ResourceNotFound'

# 资源正在发货中。
RESOURCEUNAVAILABLE_DELIVERING = 'ResourceUnavailable.Delivering'

# 账号已被冻结。
RESOURCEUNAVAILABLE_FREEZE = 'ResourceUnavailable.Freeze'

# ResourceUnavailable.InArrears
RESOURCEUNAVAILABLE_INARREARS = 'ResourceUnavailable.InArrears'

# 服务正在开通中，请稍等。
RESOURCEUNAVAILABLE_ISOPENING = 'ResourceUnavailable.IsOpening'

# ResourceUnavailable.LowBalance
RESOURCEUNAVAILABLE_LOWBALANCE = 'ResourceUnavailable.LowBalance'

# 计费状态未知。
RESOURCEUNAVAILABLE_NOTEXIST = 'ResourceUnavailable.NotExist'

# 服务未开通。
RESOURCEUNAVAILABLE_NOTREADY = 'ResourceUnavailable.NotReady'

# 资源已被回收。
RESOURCEUNAVAILABLE_RECOVER = 'ResourceUnavailable.Recover'

# 计费状态未知。
RESOURCEUNAVAILABLE_UNKNOWNSTATUS = 'ResourceUnavailable.UnknownStatus'

# 账号已欠费。
RESOURCESSOLDOUT_CHARGESTATUSEXCEPTION = 'ResourcesSoldOut.ChargeStatusException'

# 未授权操作。
UNAUTHORIZEDOPERATION = 'UnauthorizedOperation'

# 操作不支持。
UNSUPPORTEDOPERATION = 'UnsupportedOperation'
