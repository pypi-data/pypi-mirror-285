from dataproc_sdk.dataproc_sdk_datiofilesystem.datiofilesystem import DatioFileSystem
from dataproc_sdk.dataproc_sdk_datiopysparksession.datiopysparksession import DatioPysparkSession
from dataproc_sdk.dataproc_sdk_schema.datioschema import DatioSchema
from dataproc_sdk.dataproc_sdk_utils.logging import get_user_logger
from pyspark.sql import SparkSession


class HDFSDatio:
    def __init__(self):
        self.__logger = get_user_logger("__name__")
        self._dataproc = DatioPysparkSession().get_or_create()
        self._spark = SparkSession.getActiveSession()
        self._sc = self._spark.sparkContext
        self.FileUtil = self._sc._gateway.jvm.org.apache.hadoop.fs.FileUtil
        self.Configuration = self._sc._gateway.jvm.org.apache.hadoop.conf.Configuration
        self.conf = self.Configuration()
        self.conf.setBoolean("hdfs.append.support", True)
        self.conf.setBoolean("dfs.append.support", True)
        self.fs = DatioFileSystem().get()

    def fs_delete(self, path: str) -> None:
        file_system = self.fs.qualify(path).fileSystem()
        path_fs = self.fs.qualify(path).path()
        file_system.delete(path_fs)

    def fs_copy(self, src: str, dst: str) -> None:
        fs = self.fs.qualify(src).fileSystem()
        fs_dst = DatioFileSystem().get().qualify(dst).fileSystem()
        self.FileUtil.copy(
            fs, self.fs.qualify(src).path(), fs_dst, self.fs.qualify(dst).path(),
            False, self.conf
        )

    def fs_rename(self, src: str, dst: str) -> None:
        fs = self.fs.qualify(src).fileSystem()
        fs.rename(self.fs.qualify(src).path(), self.fs.qualify(dst).path())

    def fs_mkdirs(self, src):
        fs = self.fs.qualify(src).fileSystem()
        exists = self.fs_exists(src)
        if not exists:
            fs.mkdirs(self.fs.qualify(src).path())
            return True
        else:
            print(f"folder exists -> {src}")

    def fs_exists(self, src):
        fs = self.fs.qualify(src).fileSystem()
        exists = fs.exists(self.fs.qualify(src).path())
        return exists

    def fs_ls(self, path):
        try:
            fs = self.fs.qualify(path).fileSystem()
            status = fs.listStatus(self.fs.qualify(path).path())
            return [fileStatus.getPath().getName() for fileStatus in status if fileStatus.isDir()]
        except Exception:
            return []

    def fs_get_last_partition(self, path):
        fs = self.fs.qualify(path).fileSystem()
        exists = fs.exists(self.fs.qualify(path).path())
        if not exists:
            return []
        status = fs.listStatus(self.fs.qualify(path).path())
        path_content = [file.getPath().toString().split("/")[-1] for file in status]
        path_content = [file for file in path_content if file not in ('_not_overwritten', '_SUCCESS')]
        if not path_content:
            return None
        path_content.sort(reverse=True)
        output_date = path_content[0].split("=")[1]
        return output_date

    def fs_get_prev_months(self, t: str, i: int):
        t_context = list()
        for _ in range(i):
            prev_month = (lambda x: str(((x - 1) % 12) + 1))(int(t[4:]) - 1)
            if len(prev_month) == 1:
                prev_month = "0" + prev_month
            year = str(int(t[:4]) - 1) if prev_month == "12" else t[:4]
            t = year + prev_month
            t_context.append(t)
        return t_context

    def fs_get_next_months(self, t: str, i: int):
        """
          t -- month (e.g. '202201')
          i -- (int) amount of months to be returned
        """
        t_context = list()
        for _ in range(i):
            next_month = (lambda x: str(((x - 1) % 12) + 1))(int(str(t)[4:]) + 1)
            if len(next_month) == 1:
                next_month = "0" + next_month
            year = str(int(t[:4]) + 1) if next_month == "01" else t[:4]
            t = year + next_month
            t_context.append(t)
        return t_context
