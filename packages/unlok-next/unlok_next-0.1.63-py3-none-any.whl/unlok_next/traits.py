import random
import uuid
from typing import Callable

import yaml


class RoomListener:

    def connected_nodes(diagram):
        pass

    def to_input(self):
        from unlok_next.api.schema import NodeInput

        return NodeInput(**self.dict())
