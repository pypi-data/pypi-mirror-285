import json
import os
import subprocess
from odps import ODPS
from odps.inter import setup, enter, teardown, list_rooms


class _MaxcomputeSetup:
    def __init__(self):
        # way 1: read aliyun config by command line *=(default profile only)
        script = ["aliyun", "configure", "get", "--profile", "default"]
        try:
            result = subprocess.run(
                script,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                check=True,
            )
        except:
            raise ValueError(
                "fail to get aliyun account, please install aliyun cli to setup account and restart your computer(for windows) refer to https://help.aliyun.com/zh/cli/installation-guide!"
            )
        self.default_project = "dteam_dw_dev"

        config = json.loads(result.stdout)
        self.access_key_id = config["access_key_id"]  # type: ignore
        self.access_key_secret = config["access_key_secret"]  # type: ignore
        self.region_id = config["region_id"]
        self.endpoint = f"http://service.{self.region_id}.maxcompute.aliyun.com/api"

    def _setup(self):
        if self._inited:
            return

        teardown()
        setup(
            self.access_key_id,
            self.access_key_secret,
            self.default_project,
            endpoint=self.endpoint,
        )

    @property
    def _inited(self):
        rooms = list_rooms()
        if len(rooms) == 0:
            return False
        return True

    @property
    def default_odps(self) -> ODPS:
        self._setup()
        return enter().odps

    def get_project_odps(self, project: str) -> ODPS:
        return ODPS(self.access_key_id, self.access_key_secret, project, self.endpoint)
