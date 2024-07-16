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

import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.abstract_client import AbstractClient
from tencentcloud.aa.v20200224 import models


class AaClient(AbstractClient):
    _apiVersion = '2020-02-24'
    _endpoint = 'aa.tencentcloudapi.com'
    _service = 'aa'


    def QueryActivityAntiRush(self, request):
        """腾讯云活动防刷（ActivityAntiRush，AA）是针对电商、O2O、P2P、游戏、支付等行业在促销活动中遇到“羊毛党”恶意刷取优惠福利的行为时，通过防刷引擎，精准识别出“薅羊毛”恶意行为的活动防刷服务，避免了企业被刷带来的巨大经济损失。

        :param request: Request instance for QueryActivityAntiRush.
        :type request: :class:`tencentcloud.aa.v20200224.models.QueryActivityAntiRushRequest`
        :rtype: :class:`tencentcloud.aa.v20200224.models.QueryActivityAntiRushResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("QueryActivityAntiRush", params, headers=headers)
            response = json.loads(body)
            model = models.QueryActivityAntiRushResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))