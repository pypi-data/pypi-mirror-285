# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import sys

from typing import List

from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
from alibabacloud_tea_util.client import Client as UtilClient
import json
from ks_utility import datetimes
from ks_utility.constants import RET_OK, RET_ERROR

from enum import Enum

class SmsStatus(Enum):
    SENDING = '发送中'
    OK = '发送成功'
    ERROR = '发送失败'


class SmsClient():
    def __init__(self, access_key_id: str, access_key_secret: str):
        self.client = self.create_client(access_key_id, access_key_secret)

    def create_client(
        self,
        access_key_id: str,
        access_key_secret: str,
    ) -> DysmsapiClient:
        """
        使用AK&SK初始化账号Client
        """
        config = open_api_models.Config()
        config.access_key_id = access_key_id
        config.access_key_secret = access_key_secret
        return DysmsapiClient(config)

    def send_sms(
        self,
        phone_numbers: str,
        sign_name: str,
        template_code: str,
        template_param: str
    ) -> None:
        client = self.client
        # 1.发送短信
        send_req = dysmsapi_models.SendSmsRequest(
            phone_numbers=phone_numbers,
            sign_name=sign_name,
            template_code=template_code,
            template_param=template_param
        )
        send_resp = client.send_sms(send_req)
        code = send_resp.body.code
        if not UtilClient.equal_string(code, 'OK'):
            return RET_ERROR, f'msg:{send_resp.body.message};request_id:{send_resp.body.request_id}'

        biz_id = send_resp.body.biz_id
        return RET_OK, biz_id
        

    def query_sms(self, biz_id: str, phone_numbers: str):
        if not biz_id:
            return
        
        client = self.client
        statuses: list[dict] = []

        # 3.查询结果
        phone_nums = phone_numbers.split(',')
        for phone_num in phone_nums:
            query_req = dysmsapi_models.QuerySendDetailsRequest(
                phone_number=UtilClient.assert_as_string(phone_num),
                biz_id=biz_id,
                send_date=datetimes.now().strftime('%Y%m%d'),
                page_size=10,
                current_page=1   
            )
            query_resp = client.query_send_details(query_req)
            dtos = query_resp.body.sms_send_detail_dtos.sms_send_detail_dto
            # 打印结果
            for dto in dtos:
                if UtilClient.equal_string(f'{dto.send_status}', '3'):
                    status = SmsStatus.OK
                elif UtilClient.equal_string(f'{dto.send_status}', '2'):
                    status = SmsStatus.ERROR
                else:
                    status = SmsStatus.SENDING
        
            statuses.append({
                'phone_number': dto.phone_num,
                'status': status,
                'datetime': dto.receive_date
            })

        return statuses

