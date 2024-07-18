import io
import asyncio

from requests_toolbelt import MultipartEncoder

import lark_oapi
import lark_oapi as lark


def run_async_function(sync_callback):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(sync_callback)

def upload_all_file(file):
    # print(isinstance(io.BufferedReader, io.IOBase))
    # return
    # 创建client
    client = lark.Client.builder() \
        .app_id("cli_a3aacb5fdf78d00e") \
        .app_secret("2zwKfrqM2xe9kMjoz2OmIgmUFUB7CAeH") \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象

    data = {
        "name": "2305.14283.pdf",
        "type": "attachment",
        # "file_name": "2305.14283.pdf",
        # "parent_type": "explorer",
        # "parent_node": "FHsUf2I0wl8oscdH46dcDsKNn0c",
        # "size": 1212451,
        # "file":  ("2305.14283.pdf", file, "")
        "content": ("2305.14283.pdf", file, "")
    }
    body = MultipartEncoder(lark.Files.parse_form_data(data))

    # request: lark.BaseRequest = (lark.BaseRequest.builder() \
    #     .http_method(lark.HttpMethod.POST) \
    #     .uri("/open-apis/drive/v1/files/upload_all") \
    #     .headers({"Content-Type": body.content_type}) \
    #     .token_types({lark.AccessTokenType.USER}) \
    #     .body(body) \
    #     .build())

    request: lark.BaseRequest = (
        lark.BaseRequest.builder()
        .http_method(lark.HttpMethod.POST)
        .uri("/approval/openapi/v2/file/upload")
        .headers({"Content-Type": body.content_type})
        .token_types({lark.AccessTokenType.TENANT})
        .body(body)
        .build()
    )

    # 发起请求
    response: lark.BaseResponse = client.request(request, option=lark_oapi.RequestOption.builder().user_access_token("u-fTy552b6N2.XXUMGUCED1Nh0iqsBh1f1V0G0ghC821fU").build())

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.request failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return

    # 处理业务结果
    lark.logger.info(str(response.raw.content, lark.UTF_8))

if __name__ == '__main__':
    file = open("/Users/bytedance/Downloads/2305.14283.pdf", "rb")
    # file = open("/Users/bytedance/Downloads/2c60da4397e18c0ae1fdf6bf50b36ad4_gvIc3W7D2z.png", "rb")
    upload_all_file(file)
