from is3_python_kafka.domain.data_dto import DataEntity
from is3_python_kafka.utils.is3_request_util import RequestUtil


def get_meta_table_list(json, dataDto: DataEntity):
    url = 'http://118.195.242.175:31900/data-main/operation/getDataByCondition'
    json['prjId'] = dataDto.prjId
    return RequestUtil.post(url, json, dataDto.headers)
