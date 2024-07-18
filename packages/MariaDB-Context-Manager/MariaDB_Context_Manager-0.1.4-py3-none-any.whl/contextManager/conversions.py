from datetime import date, datetime, time
import json


def mariadb_to_python(value: int):
    if value in [15, 253, 254]:
        return str
    if value in [8, 1, 2, 3, 8, 9]:
        return int
    if value in [246, 0, 4, 5]:
        return float
    if value in [248]:
        return set
    if value in [10, 14, 18]:
        return date
    if value in [7, 11, 17, 19]:
        return time
    if value in [12]:
        return datetime
    if value in [13]:
        return date.year
    if value in [16, 249, 250, 251, 252]:
        return bytes
    if value in [245]:
        return json
    # Catches anything else and returns string
    return str
