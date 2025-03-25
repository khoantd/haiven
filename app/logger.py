# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import sys
from loguru import logger


class HaivenLogger:
    __instance = None

    def __init__(self, loguru_logger):
        print("instantiating HaivenLogger")
        loguru_logger.remove()

        self.logger = loguru_logger.patch(HaivenLogger.patching)
        self.logger.add(sys.stdout, format="{extra[serialized]}")

        self.logger.level("ANALYTICS", no=60)

        if HaivenLogger.__instance is not None:
            raise Exception(
                "HaivenLogger is a singleton class. Use getInstance() to get the instance."
            )
        HaivenLogger.__instance = self

    def analytics(self, message, extra=None):
        self.logger.log("ANALYTICS", message, extra=extra)

    def error(self, message, extra=None):
        self.logger.error(message, extra=extra)

    def info(self, message, extra=None):
        self.logger.info(message, extra=extra)

    def warn(self, message, extra=None):
        self.logger.warning(message, extra=extra)

    @staticmethod
    def get():
        if HaivenLogger.__instance is None:
            HaivenLogger(logger)
        return HaivenLogger.__instance

    @staticmethod
    def serialize(record):
        try:
            # Ensure message is treated as a plain string without formatting
            message = str(record["message"])
            subset = {
                "time": str(record["time"]),
                "message": message,
                "level": record["level"].name,
                "file": record["file"].path,
                "extra": record.get("extra", None)
            }
            return json.dumps(subset)
        except Exception as e:
            # Fallback for serialization errors
            return json.dumps({
                "time": str(record.get("time", "")),
                "message": f"Error serializing log: {str(e)}",
                "level": "ERROR",
                "file": str(record.get("file", {}).get("path", "unknown")),
                "extra": None
            })

    @staticmethod
    def patching(record):
        try:
            record["extra"] = record.get("extra", {})
            record["extra"]["serialized"] = HaivenLogger.serialize(record)
        except Exception as e:
            # Fallback logging in case of serialization errors
            print(f"Logger error: {str(e)}", file=sys.stderr)
