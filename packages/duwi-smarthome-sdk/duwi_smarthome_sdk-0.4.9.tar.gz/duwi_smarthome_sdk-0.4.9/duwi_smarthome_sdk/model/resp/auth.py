from typing import Optional, Dict, Any
import datetime


class AuthToken:
    def __init__(
            self,
            access_token: str,
            access_token_expire_time: str,
            refresh_token: str,
            refresh_token_expire_time: str
    ):
        self.access_token: str = access_token
        self.access_token_expire_time: datetime.datetime = self._parse_datetime(
            access_token_expire_time) if access_token_expire_time else None
        self.refresh_token: str = refresh_token
        self.refresh_token_expire_time: datetime.datetime = self._parse_datetime(
            refresh_token_expire_time) if refresh_token_expire_time else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessToken": self.access_token,
            "accessTokenExpireTime": self.access_token_expire_time.isoformat() if self.access_token_expire_time else None,
            "refreshToken": self.refresh_token,
            "refreshTokenExpireTime": self.refresh_token_expire_time.isoformat() if self.refresh_token_expire_time else None,
        }

    @staticmethod
    def _parse_datetime(datetime_str: str) -> datetime.datetime:
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    def __str__(self) -> str:
        return (f"Access Token: {self.access_token}, "
                f"Access Token Expires On: {self.access_token_expire_time}, "
                f"Refresh Token: {self.refresh_token}, "
                f"Refresh Token Expires On: {self.refresh_token_expire_time}")
