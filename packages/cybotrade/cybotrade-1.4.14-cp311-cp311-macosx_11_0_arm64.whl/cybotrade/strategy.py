import logging
import collections

from typing import Any, List, Dict
from signal import SIGINT, signal
import time
import math

from .models import FloatWithTime, OpenedTrade, OrderUpdate

class Strategy:
    """
    This class is a handler that will be used by the Runtime to handle events such as
    `on_candle_closed`, `on_execution_update`, etc. The is a base class and every new strategy
    should be inheriting this class and override the methods.
    """

    logger = logging
    LOG_FORMAT = (
        "%(levelname)s %(name)s %(asctime)-15s %(filename)s:%(lineno)d %(message)s"
    )
    data_map: Dict[str, collections.deque] = {}
    split_data_map: Dict[str, Dict[str, collections.deque]] = {}
    handlers: List[logging.Handler] = []
    max_deque_length = 0

    def __init__(
            self,
            log_level: int = logging.INFO,
            handlers: List[logging.Handler] = [],
    ):
        """
        Set up the logger
        """
        if len(self.handlers) == 0:
            default_handler = logging.StreamHandler()
            default_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
            self.handlers.append(default_handler)

        logging.root.setLevel(log_level)
        if not logging.root.hasHandlers():
            for handler in handlers:
                logging.root.addHandler(handler)

    def on_shutdown(self):
        return 

    def get_data_map(self):
        return self.data_map

    async def initialize_split_ringbuffer(self, topics, deque_length, data: Dict[str, List[Dict[str, str]]]):
        self.max_deque_length = deque_length 
        for topic in topics:
            self.split_data_map[topic] = {}
            if topic in data:
                for values in data[topic]:
                    for key in values.keys():
                        self.split_data_map[topic][key] = collections.deque(maxlen=deque_length)

                for values in data[topic]:
                    for key in values.keys():
                        self.split_data_map[topic][key].append(values[key])


    async def update_split_ringbuffer(self, topic, data_list: List[Dict[str, str]]):
        data_map = self.split_data_map[topic]
        for kv_data in data_list:
            try:
                if topic in self.split_data_map:
                    if len(data_map) < 1:
                        for key in kv_data.keys():
                            self.split_data_map[topic][key] = collections.deque(maxlen=self.max_deque_length) 
                            self.split_data_map[topic][key].append(kv_data[key]) 

                topic_end_time = self.split_data_map[topic]['end_time'][-1]
                if kv_data['end_time'] == topic_end_time:
                    for key in kv_data.keys():
                        if key == "confirm":
                            continue;
                        data_map[key].pop()
                        data_map[key].append(kv_data[key])
                else:
                    for key in kv_data.keys():
                        if key == "confirm":
                            continue;
                        data_map[key].append(kv_data[key])
            except Exception as e:
                logging.error(f"Missing end_time parameter in data: {kv_data}: {e}\nInform the Cybotrade team in regards to this issue\n");
                raise e


    async def initialize_ringbuffer(self, topics, deque_length, data):
        for topic in topics:
            self.data_map[topic] = collections.deque(maxlen=deque_length)
            if topic in data:
                self.data_map[topic].extend(data[topic])

        logging.info("Successfully initialized ringbuffer for data")

    async def update_ringbuffer(self, topic, data_list):
        for data in data_list:
            if topic in self.data_map:
                if len(self.data_map[topic]) < 1:
                    self.data_map[topic].append(data) 

                topic_list = self.data_map[topic][-1]
                try:
                    if data["end_time"] == topic_list["end_time"]:
                        self.data_map[topic].pop()
                        self.data_map[topic].append(data)
                    elif data["end_time"] < topic_list["end_time"]:
                        continue
                    else:
                        self.data_map[topic].append(data)
                except Exception as e:
                    logging.error(f"Missing end_time parameter in data: {data}\nInform the Cybotrade team in regards to this issue\n");
                    raise e

    async def resync_split_ringbuffer(self, topics: List[str], data: Dict[str, List[Dict[str,str]]]) -> List[bool]:
        """
        resync
        """
        updated = []
        for topic in topics:
            keys = self.split_data_map[topic].keys();
            values = data[topic]
            current_end_time = self.split_data_map[topic]['end_time'][-1]
            time_now = math.floor(time.time() * 1000)
            x = list(filter(lambda x: (x.get('end_time') > current_end_time), data[topic]))

            if len(x) == 0:
                updated.append(False)
            else:
                updatable = False
                for item in x:
                    if int(item.get('end_time')) > time_now:
                        continue
                    updatable = True
                        
                updated.append(updatable)

            for key in keys:
                new_values = []

                for value in values:
                    new_values.append(value[key])

                self.split_data_map[topic][key] = collections.deque(new_values, maxlen=len(new_values))

        return updated


    async def resync_ringbuffer(self, topics: List[str], data: Dict[str, List[Dict[str, str]]]) -> List[bool]:
        """
        Do something
        """
        updated = []
        
        
        for topic in topics:
            x = list(filter(lambda x: x.get('end_time') > self.data_map[topic][-1].get('end_time'), data[topic]))

            if len(x) == 0:
                updated.append(False)
            else:
                updated.append(True)

            self.data_map[topic] = collections.deque(data[topic],maxlen=len(data[topic]))

        return updated

    async def set_param(self, identifier, value):
        """
        Used to set up params for the strategy
        """
        # logging.info(f"Setting {identifier} to {value}")
    
    async def on_init(self, strategy):
        """
        on init
        """
        # logging.info("[on_init] Strategy successfully started.")

    async def on_trade(self, strategy, trade: OpenedTrade):
        """
        on trade 
        """
        # logging.info(f"[on_trade] Received opened trade: {trade.__repr__()}")

    async def on_market_update(self, strategy, equity, available_balance):
        """
        on market_update 
        """
        # logging.info(
        #     f"[on_market_update] Received market update: equity({equity.__repr__()}), available_balance({available_balance.__repr__()})")

    async def on_order_update(self, strategy, update):
        """
        on order_update 
        """
        # logging.info(f"[on_order_update] Received order update: {update.__repr__()}")

    async def on_active_order_interval(self, strategy, active_orders):
        """
        on active_order 
        """
        # logging.debug(f"[on_active_order_interval] Received active orders: {active_orders.__repr__()}")

    async def on_backtest_complete(self, strategy):
        """
        on active_order 
        """
        # logging.info("[on_backtest_complete] Backtest completed.")
