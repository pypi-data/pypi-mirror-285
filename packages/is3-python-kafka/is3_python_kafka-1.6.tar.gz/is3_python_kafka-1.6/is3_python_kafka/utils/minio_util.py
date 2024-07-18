from is3_python_kafka.domain.data_dto import DataEntity
from is3_python_kafka.minio.MinioComponent import MinioComponent


def upload_file_with_expire(dataDto: DataEntity, bucketName, fileName):
    minioClient = MinioComponent(dataDto.minioEndpoint, dataDto.minioAccessKey, dataDto.minioSecretKey)
    return minioClient.upload_file_with_expire(bucketName, fileName)


def upload_file(dataDto: DataEntity, bucketName, fileName):
    minioClient = MinioComponent(dataDto.minioEndpoint, dataDto.minioAccessKey, dataDto.minioSecretKey)
    return minioClient.upload_file(bucketName, fileName)
