from enum import Enum


class Port(Enum):
    ftp = 21
    sftp = 22
    ssh = 22  # noqa: PIE796
    telnet = 23
    dns = 53
    gopher = 70
    http = 80
    ws = 80  # noqa: PIE796
    https = 443
    wss = 443  # noqa: PIE796
    ipp = 631
    ipps = 631  # noqa: PIE796
    mariadb = 3306
    mysql = 3306  # noqa: PIE796
    postgres = 5432
    postgresql = 5432  # noqa: PIE796
    redshift = 5439
    redis = 6379
    git = 9418
    mongodb = 27017
