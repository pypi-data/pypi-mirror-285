from dataclasses import dataclass
from time import time
from typing import Optional, Tuple
from datetime import datetime, timedelta, tzinfo

from .types import MAX_TS, MAX_NODE_ID, MAX_SEQUENCE, TimestampResolution


class SnowflakeIdGenerator:
    """Snowflake Id generator"""

    def __init__(
        self,
        *,
        node_id: int = 0,
        sequence: int = 0,
        epoch: int = 0,
        timestamp: Optional[int] = None,
        timestamp_resolution: TimestampResolution = TimestampResolution.MILLISECOND,
    ):
        """Creates a new Snowflake ID generator
        If timestamp resolution is set to MICROSECOND, the extra microseconds will be added to sequence number

        Args:
            node_id (int, optional): _description_. Defaults to 0.
            sequence (int, optional): _description_. Defaults to 0.
            epoch (int, optional): _description_. Defaults to 0.
            timestamp (Optional[int], optional): _description_. Defaults to None.
            timestamp_resolution (TimestampResolution, optional): _description_. Defaults to TimestampResolution.MILLISECOND.

        Raises:
            OverflowError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """

        current_timestamp = self.__get_current_timestamp()

        self.__validate_fields(current_timestamp, node_id, sequence, epoch, timestamp)

        timestamp = timestamp or current_timestamp[0]

        self._epoch = epoch
        self._ts = timestamp - self._epoch
        self._node_id = node_id << 12
        self._sequence = sequence
        self._timestamp_resolution = timestamp_resolution

    def __get_current_timestamp(self) -> Tuple[int, int]:
        """Returns the current timestamp in milliseconds and microseconds

        Raises:
            OverflowError: _description_

        Returns:
            Tuple[int, int]: _description_
        """

        return (
            int(time() * 1000.0),
            int(time() * 1000000.0),
        )

    def __validate_timestamp(self, timestamp: int, epoch: int):

        if timestamp - epoch >= MAX_TS:
            raise OverflowError(
                "The maximum current timestamp has been reached in selected epoch. Snowflake cannot generate more IDs."
            )

    def __validate_fields(
        self,
        current_timestamp: Tuple[int, int],
        node_id: int,
        sequence: int,
        epoch: int,
        timestamp: int,
    ):

        if node_id < 0 or node_id > MAX_NODE_ID:
            raise ValueError(f"node_id must be between 0 and {MAX_NODE_ID}")

        if sequence < 0 or sequence > MAX_SEQUENCE:
            raise ValueError(f"sequence must be between 0 and {MAX_SEQUENCE}")

        self.__validate_timestamp(current_timestamp[0], epoch)

        timestamp = timestamp or current_timestamp[0]

        if timestamp < 0 or timestamp > current_timestamp[0]:
            raise ValueError(f"timestamp must be between 0 and {current_timestamp[0]}")

        if epoch < 0 or epoch > current_timestamp[0]:
            raise ValueError(f"epoch must be between 0 and {current_timestamp[0]}")

    @property
    def epoch(self) -> int:
        return self._epoch

    def __iter__(self):
        return self

    def __next__(self) -> Optional[int]:

        current_timestamp = self.__get_current_timestamp()

        self.__validate_timestamp(current_timestamp[0], self._epoch)

        current = current_timestamp[0] - self._epoch
        current_microseconds = current_timestamp[1] - (self._epoch * 1000)
        extra_microseconds = current_microseconds % 1000

        if self._ts == current:
            if self._sequence == MAX_SEQUENCE:
                return None
            self._sequence += 1
        elif self._ts > current:
            return None
        else:
            self._sequence = 0

        self._ts = current
        sequence = (
            self._sequence
            if self._timestamp_resolution == TimestampResolution.MILLISECOND
            else self._sequence + extra_microseconds
        )
        timestamp = int(current_microseconds / self._timestamp_resolution.value) << 22

        # Calculate id
        return timestamp | self._node_id | sequence
