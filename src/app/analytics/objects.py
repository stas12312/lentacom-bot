from typing import NamedTuple

from aioinflux import lineprotocol, MEASUREMENT, STR, TIMEDT, INT, TAG


@lineprotocol
class BotUpdate(NamedTuple):
    measurement: MEASUREMENT
    timestamp: TIMEDT
    update_type: TAG
    user_id: TAG
    value: TAG
    update: STR
    stub: INT
