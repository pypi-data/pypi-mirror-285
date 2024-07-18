import os
from typing import Dict, List, Optional, Union

from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType

from ng_data_pipelines_sdk.custom_logger import logger
from ng_data_pipelines_sdk.interfaces import (
    AWSCredentials,
    Env,
    FileType,
    SparkConfigParams,
)


class SuppressOutput:
    def __enter__(self):
        self._original_stdout_fd = os.dup(1)
        self._original_stderr_fd = os.dup(2)
        self._null_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self._null_fd, 1)
        os.dup2(self._null_fd, 2)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.dup2(self._original_stdout_fd, 1)
        os.dup2(self._original_stderr_fd, 2)
        os.close(self._null_fd)


class SparkManager:
    """
    A class that manages the SparkSession and provides methods for reading and writing data.

    Args:
        app_name (str): The name of the Spark application.
        aws_credentials_dict (Optional[Dict[Env, AWSCredentials]], optional): A dictionary of AWS credentials for different environments. Defaults to None.
    """

    def __init__(
        self,
        app_name: str,
        aws_credentials_dict: Optional[Dict[Env, AWSCredentials]] = None,
        spark_config_params: SparkConfigParams = SparkConfigParams(),
        suppress_initial_output: bool = False,
    ):
        self.aws_credentials_dict = aws_credentials_dict
        spark_config = self.create_spark_config(app_name, spark_config_params)

        self.spark = self.create_spark_session(
            spark_config=spark_config, suppress_output=suppress_initial_output
        )
        self.spark.sparkContext.setLogLevel("ERROR")

    def _set_aws_credentials(self, env: Env):
        """
        Sets the AWS credentials for the specified environment.

        Args:
            env (Env): The environment for which to set the AWS credentials.
        """
        if not self.aws_credentials_dict:
            return

        aws_credentials = self.aws_credentials_dict[env]

        jsc = getattr(self.spark.sparkContext, "_jsc")
        hadoopConfiguration = jsc.hadoopConfiguration()

        hadoopConfiguration.set("fs.s3a.access.key", aws_credentials.aws_access_key_id)
        hadoopConfiguration.set(
            "fs.s3a.secret.key", aws_credentials.aws_secret_access_key
        )

    def create_spark_session(self, spark_config, suppress_output: bool = False):
        if suppress_output:
            with SuppressOutput():
                spark = SparkSession.builder.config(conf=spark_config).getOrCreate()  # type: ignore
        else:
            spark = SparkSession.builder.config(conf=spark_config).getOrCreate()  # type: ignore
        return spark

    def create_spark_config(
        self,
        app_name: str,
        spark_config_params: SparkConfigParams,
    ):
        """
        Creates the Spark configuration.

        Args:
            app_name (str): The name of the Spark application.

        Returns:
            SparkConf: The Spark configuration.
        """
        config: SparkConf = SparkConf().setAppName(app_name)

        config.set("spark.executor.memory", spark_config_params.executor_memory)
        config.set("spark.driver.memory", spark_config_params.driver_memory)
        config.set(
            "spark.executor.memoryOverhead",
            spark_config_params.executor_memory_overhead,
        )
        config.set(
            "spark.driver.memoryOverhead", spark_config_params.driver_memory_overhead
        )
        config.set("spark.task.maxFailures", spark_config_params.task_max_failures)
        config.set(
            "spark.stage.maxConsecutiveAttempts",
            spark_config_params.stage_max_consecutive_attempts,
        )
        config.set(
            "spark.sql.eagerEval.enabled", spark_config_params.sql_eager_eval_enabled
        )

        config.set("spark.sql.parquet.datetimeRebaseModeInRead", "LEGACY")
        config.set("spark.sql.parquet.datetimeRebaseModeInWrite", "LEGACY")
        config.set("spark.sql.parquet.int96RebaseModeInWrite", "LEGACY")
        config.set(
            "spark.hadoop.fs.s3a.impl", " org.apache.hadoop.fs.s3a.S3AFileSystem"
        )

        # Set the packages to be used by Spark for Hadoop AWS integration
        config.set("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.2.2")

        if self.aws_credentials_dict:
            config.set(
                "spark.hadoop.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
            )

        return config

    def read(
        self,
        env: Env,
        paths: Union[str, List[str]],
        file_type: FileType,
        base_path: Optional[str] = None,
        schema: Optional[StructType] = None,
        persist: bool = False,
    ) -> Optional[DataFrame]:
        def get_existing_paths(paths: List[str]) -> List[str]:
            sc = self.spark.sparkContext
            hadoop_conf = sc._jsc.hadoopConfiguration()
            existing_paths = []
            for path in paths:
                fs_path = self.spark._jvm.org.apache.hadoop.fs.Path(path)
                fs = fs_path.getFileSystem(hadoop_conf)
                if fs.exists(fs_path):
                    existing_paths.append(path)
                else:
                    logger.warning(f"Path does not exist (ignoring): {path}")

            return existing_paths

        self._set_aws_credentials(env)

        if isinstance(paths, str):
            paths = [paths]

        existing_paths = get_existing_paths(paths)

        if existing_paths == []:
            logger.warning("No existing paths found.")
            return None

        logger.info(f"Reading data from existing paths: {existing_paths}")

        reader = self.spark.read.format(file_type)
        if schema:
            reader = reader.schema(schema)
        if base_path:
            reader = reader.option("basePath", base_path)

        df = reader.load(existing_paths)

        if persist:
            logger.info("Caching DataFrame...")
            df.persist()
            df.count()  # Trigger persistence

        return df

    def write(
        self,
        env: Env,
        df: DataFrame,
        path: str,
        file_type: FileType,
        partitions: Optional[List[str]] = None,
    ):
        """
        Writes the DataFrame to the specified path using the specified file type.

        Args:
            env (Env): The environment to use for setting AWS credentials.
            df (DataFrame): The DataFrame to write.
            path (str): The path where the DataFrame should be written.
            file_type (FileType): The file type to use for writing the DataFrame.
            partitions (Optional[List[str]], optional): A list of partition columns to use for writing the DataFrame. Defaults to None.
        """
        self._set_aws_credentials(env)

        if partitions:
            df.write.partitionBy(partitions).format(file_type).mode("append").save(path)
        else:
            df.write.format(file_type).mode("append").save(path)
