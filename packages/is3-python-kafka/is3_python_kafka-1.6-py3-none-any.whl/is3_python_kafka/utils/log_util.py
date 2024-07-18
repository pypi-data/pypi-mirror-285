from is3_python_kafka.domain.data_dto import DataEntity
from ..utils.kafka_component_util import kafkaComponent


def send_plugin_log(message, dataDto: DataEntity):
    pluginLog = {
        'message': message,
        'taskId': dataDto.taskId,
        'logId': dataDto.logId,
        'pluginCode': dataDto.serverName,
        'nodeId': dataDto.nodeId,
        'prjId': dataDto.prjId
    }
    topic = 'plugin-log-context'
    kafka_component = kafkaComponent(topic='plugin-log-context', group_id='DEFAULT_GROUP',
                                     bootstrap_servers=dataDto.bootstrapServers)
    kafka_component.send(topic, pluginLog)


def send_task_log(message, dataDto: DataEntity):
    taskLog = message
    taskLog['nodeId'] = dataDto.nodeId
    taskLog['taskId'] = dataDto.taskId
    taskLog['recordId'] = dataDto.taskInstanceId
    topic = 'task-log-context'
    kafka_component = kafkaComponent(topic=topic, group_id='DEFAULT_GROUP', bootstrap_servers=dataDto.bootstrapServers)
    kafka_component.send(topic, taskLog)
