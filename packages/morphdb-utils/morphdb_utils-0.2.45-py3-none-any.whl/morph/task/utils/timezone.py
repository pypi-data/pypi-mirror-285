import os
import time


class TimezoneManager:
    def __init__(self):
        self.zone_dir = self._get_zone_dir()

    @staticmethod
    def _get_zone_dir():
        localtime_link = os.readlink("/etc/localtime")
        zone_dir = os.path.dirname(localtime_link)
        if "zoneinfo" in zone_dir:
            return zone_dir.split("zoneinfo")[0] + "zoneinfo"
        else:
            return "/usr/share/zoneinfo"

    @staticmethod
    def get_current_timezone():
        localtime_link = os.readlink("/etc/localtime")
        return localtime_link.split("zoneinfo/")[-1]

    def list_timezones(self):
        timezones = []
        for root, dirs, files in os.walk(self.zone_dir):
            for name in files:
                filepath = os.path.join(root, name)
                if not os.path.islink(filepath) and name not in [
                    "posixrules",
                    "localtime",
                ]:
                    timezone = os.path.relpath(filepath, self.zone_dir)
                    timezones.append(timezone)
        return sorted(timezones)

    def is_valid_timezone(self, timezone):
        return timezone in self.list_timezones()

    def change_timezone(self, timezone):
        if not self.is_valid_timezone(timezone):
            print(f"Invalid timezone: {timezone}")
            return

        # 方針1: pytzライブラリの利用
        # import pytz
        # from datetime import datetime
        # utc = pytz.utc
        # now_utc = datetime.now(utc)
        # print("Current time in UTC:", now_utc)

        # TODO: この方針でちゃんと稼働しているか疎通後に検証する
        # 方針2: 環境変数でタイムゾーンを設定
        os.environ["TZ"] = "UTC"
        time.tzset()

        # 方針3: OSのタイムゾーン変更 (VMでsudo権限は利用できないので不可)
        # if os.geteuid() == 0:
        #     try:
        #         subprocess.run(
        #             ["ln", "-sf", f"{self.zone_dir}/{timezone}", "/etc/localtime"],
        #             check=True,
        #         )
        #         self.zone_dir = self._get_zone_dir()
        #         print(f"Timezone successfully changed to {timezone}")
        #     except subprocess.CalledProcessError as e:
        #         print(f"Error changing timezone: {e}")
        # else:
        #     try:
        #         subprocess.run(
        #             [
        #                 "sudo",
        #                 "ln",
        #                 "-sf",
        #                 f"{self.zone_dir}/{timezone}",
        #                 "/etc/localtime",
        #             ],
        #             check=True,
        #         )
        #         self.zone_dir = self._get_zone_dir()
        #         print(f"Timezone successfully changed to {timezone} using sudo")
        #     except subprocess.CalledProcessError as e:
        #         print(f"Error changing timezone with sudo: {e}")
