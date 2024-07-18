from typing import List


class DataEntity:
    def __init__(self, preData: List[int], pluginDataConfig: str, taskInstanceId: int, taskId: int, nodeId: int,
                 logId: int, headers: str, serverName: str, prjId: int, tenantId: int, bootstrapServers: str, minioEndpoint: str, minioAccessKey: str, minioSecretKey: str,):
        self.preData = preData
        self.pluginDataConfig = pluginDataConfig
        self.taskInstanceId = taskInstanceId
        self.taskId = taskId
        self.nodeId = nodeId
        self.logId = logId
        self.headers = headers
        self.serverName = serverName
        self.prjId = prjId
        self.tenantId = tenantId
        self.bootstrapServers = bootstrapServers
        self.minioEndpoint = minioEndpoint
        self.minioAccessKey = minioAccessKey
        self.minioSecretKey = minioSecretKey

    def __str__(self):
        return (f"DataEntity("
                f"preData={self.preData}, "
                f"pluginDataConfig='{self.pluginDataConfig}', "
                f"taskInstanceId={self.taskInstanceId}, "
                f"taskId={self.taskId}, "
                f"nodeId={self.nodeId}, "
                f"logId={self.logId}, "
                f"headers='{self.headers}', "
                f"serverName='{self.serverName}', "
                f"prjId={self.prjId}, "
                f"tenantId={self.tenantId}, "
                f"bootstrapServers='{self.bootstrapServers}')",
                f"minioEndpoint='{self.minioEndpoint}')",
                f"minioAccessKey='{self.minioAccessKey}')",
                f"minioAccessKey='{self.minioAccessKey}')"
                )
