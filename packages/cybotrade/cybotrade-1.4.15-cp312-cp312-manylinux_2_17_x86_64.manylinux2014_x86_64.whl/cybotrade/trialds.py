from datetime import UTC, datetime, timezone, timedelta
import pytz
from cybotrade.strategy import Strategy as BaseStrategy
from cybotrade.models import (
    Exchange,
    OrderSide,
    RuntimeConfig,
    RuntimeMode,
    Symbol,
    OrderParams,
    OrderStatus,
)
import numpy as np
import pandas as pd
import asyncio
import logging
import colorlog
from logging.handlers import TimedRotatingFileHandler
from cybotrade.permutation import Permutation
import util

runtime_mode = RuntimeMode.Live
pybit_mode = False
if runtime_mode == RuntimeMode.LiveTestnet:
    pybit_mode = True
place_order_exchange = Exchange.BybitLinear
TELEGRAM_CHAT_ID = "-4131984659"
TELEGRAM_TOKEN = "bot7031554271:AAFEXh51I4b05ACUd5fi3A_o1Spkd2wktT8"
CYBOTRADE_API_KEY = "25cys7zmJ33dTAwK6in3RCinAJZSch7M5LFCaIxqMCFikmWr"
CYBOTRADE_API_SECRET = "XoEYsKbiZXyhrIsZSmVFEcl2D8v0MYxJtf5dFpE9DMF7U68uBtEmZJEf10amVMZfUd7vIXXE"



class Strategy(BaseStrategy):
    # Indicator params
    leverage = 1.5
    multiplier = 0.16
    rolling_window = 62
    holding_time = 1800
    event_entry_time = datetime.now(pytz.timezone("UTC"))
    tp_percentage = 0.015
    order_pool = []
    tp_order_pool = []
    qty_precision = 3
    price_precision = 1
    min_qty = 0.001
    pair = Symbol(base="BTC", quote="USDT")
    bot_id = "btc_liquidation_cascade_15m"
    total_pnl = 0.0
    taker_vol_topic = "cryptoquant|1m|btc/market-data/taker-buy-sell-stats?window=min&exchange=binance"
    liquidation_topic = "cryptoquant|1m|btc/market-data/liquidations?window=min&exchange=binance&symbol=btc_usdt"
    taker_buy_vol_arr = []
    taker_sell_vol_arr = []
    liquidation_long_arr = []
    liquidation_short_arr = []
    taker_vol_df = pd.DataFrame({})
    liquidation_df = pd.DataFrame({})
    is_latest_taker_vol = False
    is_latest_liquidation = False
    is_candle_closed = False
    candle_closed_time = 0
    high_low_chg = []
    candle_datetime = []
    resample_time = "15T"
    entry_time = datetime.now(pytz.timezone("UTC"))
    replace_entry_order_count = 0
    replace_tp_order_count = 0
    cancel_entry_order_count = 0
    replace_limit_max_time_in_min = 5
    replace_interval = 5

    def __init__(self):
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(f"%(log_color)s{Strategy.LOG_FORMAT}")
        )
        file_handler = TimedRotatingFileHandler(
            "y_btc_liquidations_cascade_15m_threshold-livetestnet.log",
            when="h",
            backupCount=30,
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(Strategy.LOG_FORMAT))
        super().__init__(log_level=logging.INFO, handlers=[handler, file_handler])

    async def set_param(self, identifier, value):
        logging.info(f"Setting {identifier} to {value}")
        if identifier == "rolling_window":
            self.rolling_window = int(value)
        elif identifier == "multiplier":
            self.multiplier = float(value)
        else:
            logging.error(f"Could not set {identifier}, not found")

    async def on_active_order_interval(self, strategy, active_orders):
        self.order_pool = await util.check_open_order(
            strategy=strategy,
            exchange=place_order_exchange,
            pair=self.pair,
            order_pool=self.order_pool,
        )
        if len(active_orders) != 0 or len(self.order_pool) != 0:
            for order in active_orders:
                for limit in self.order_pool:
                    if limit[0] == order.client_order_id and datetime.now(
                        timezone.utc
                    ) >= limit[1] + timedelta(seconds=40):
                        if limit[2] == False:
                            if limit[3] == False:
                                try:
                                    await strategy.cancel(
                                        exchange=place_order_exchange,
                                        id=order.client_order_id,
                                        symbol=self.pair,
                                    )
                                    logging.info(
                                        f"Sent cancel for limit entry order {limit} with entry_time: {limit[1]}, is_pending: {limit[3]} at {datetime.now(timezone.utc)}"
                                    )
                                    limit[3] = True
                                    self.entry_cancel_count += 1
                                    if len(self.tp_order_pool) != 0:
                                        await self.cancel_tp_order(strategy=strategy)
                                except Exception as e:
                                    logging.error(f"Failed to cancel order: {e}")
                        else:
                            if limit[3] == False:
                                try:
                                    best_bid_ask = await util.get_order_book(
                                        strategy=strategy,
                                        exchange=place_order_exchange,
                                        pair=self.pair,
                                    )
                                    if (
                                        best_bid_ask[0] != 0.0
                                        and best_bid_ask[1] != 0.0
                                    ):
                                        if order.params.side == OrderSide.Buy:
                                            price = best_bid_ask[0]
                                        else:
                                            price = best_bid_ask[1]
                                        await strategy.cancel(
                                            exchange=place_order_exchange,
                                            id=order.client_order_id,
                                            symbol=self.pair,
                                        )
                                        logging.info(
                                            f"Sent cancel for limit entry order {limit} with entry_time: {limit[1]}, is_pending: {limit[3]} at {datetime.now(timezone.utc)}"
                                        )
                                        limit[3] = True
                                        order_resp = await strategy.order(
                                            params=OrderParams(
                                                limit=price,
                                                side=order.params.side,
                                                quantity=order.params.quantity,
                                                symbol=self.pair,
                                                exchange=place_order_exchange,
                                                is_hedge_mode=False,
                                                is_post_only=True,
                                            )
                                        )
                                        self.order_pool.append(
                                            [
                                                order_resp.client_order_id,
                                                datetime.now(timezone.utc),
                                                True,
                                                False,
                                                False,
                                                price,
                                                datetime.now(timezone.utc)
                                                + timedelta(
                                                    minutes=self.replace_limit_max_time_in_min
                                                ),
                                            ]
                                        )
                                        logging.info(
                                            f"Inserted a replace {order.params.side} limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                                        )
                                        logging.info(
                                            f"Placed a replace {order.params.side} order with qty {order.params.quantity} when price: {price} at time {datetime.now(timezone.utc)}"
                                        )
                                        self.replace_order_count += 1
                                except Exception as e:
                                    logging.error(
                                        f"Failed to cancel and replace order: {e}"
                                    )

    async def on_order_update(self, strategy, update):
        if len(self.order_pool) != 0:
            for limit in self.order_pool:
                if limit[0] == update.client_order_id:
                    logging.info(f"Latest order update: {update}")
                    if update.status == OrderStatus.Created:
                        limit[4] = True
                        logging.info(
                            f"Limit order: {update.client_order_id} is {update.status}"
                        )
                    elif (
                        update.status == OrderStatus.Filled
                        or update.status == OrderStatus.PartiallyFilledCancelled
                    ):
                        try:
                            position = await strategy.position(
                                symbol=self.pair, exchange=place_order_exchange
                            )
                        except Exception as e:
                            logging.error(f"Failed to fetch position: {e}")
                        logging.info(
                            f"Latest position: {util.get_position_info(position,datetime.now(pytz.timezone("UTC")))}"
                        )
                        util.send_limit_order_fill_telegram_msg(
                            telegram_chat_id=TELEGRAM_CHAT_ID,
                            telegram_token=TELEGRAM_TOKEN,
                            bot_id=self.bot_id,
                            qty=update.filled_size,
                            pair=self.pair,
                            price=update.price,
                            position=position,
                            entry_time=datetime.now(pytz.timezone("UTC")),
                        )

                        self.order_pool.remove(limit)
                        logging.info(
                            f"Removed {limit} from order_pool due to order {update.status}, current order_pool: {self.order_pool}"
                        )
                    elif (
                        update.status == OrderStatus.Cancelled
                        or update.status == OrderStatus.Rejected
                    ):
                        if limit[4] == False:
                            if limit[2] == True:
                                try:
                                    best_bid_ask = await util.get_order_book(
                                        strategy=strategy,
                                        exchange=place_order_exchange,
                                        pair=self.pair,
                                    )
                                    if (
                                        best_bid_ask[0] != 0.0
                                        and best_bid_ask[1] != 0.0
                                    ):
                                        if update.side == OrderSide.Buy:
                                            price = best_bid_ask[0]
                                        else:
                                            price = best_bid_ask[1]
                                        order_resp = await strategy.order(
                                            params=OrderParams(
                                                limit=price,
                                                side=update.side,
                                                quantity=update.remain_size,
                                                symbol=self.pair,
                                                exchange=place_order_exchange,
                                                is_hedge_mode=False,
                                                is_post_only=True,
                                            )
                                        )
                                        self.order_pool.append(
                                            [
                                                order_resp.client_order_id,
                                                datetime.now(timezone.utc),
                                                True,
                                                False,
                                                False,
                                                price,
                                                datetime.now(timezone.utc)
                                                + timedelta(
                                                    minutes=self.replace_limit_max_time_in_min
                                                ),
                                            ]
                                        )
                                        logging.info(
                                            f"Inserted a replace {update.side} limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                                        )
                                        logging.info(
                                            f"Placed a replace {update.side} order with qty {update.remain_size} when price: {price} due to order get rejected at time {datetime.now(timezone.utc)}"
                                        )
                                except Exception as e:
                                    logging.error(
                                        f"Failed to cancel and replace order: {e}"
                                    )
                        self.order_pool.remove(limit)
                        logging.info(
                            f"Removed {limit} from order_pool due to order {update.status}, current order_pool: {self.order_pool}"
                        )

        if len(self.tp_order_pool) != 0:
            for limit in self.tp_order_pool:
                if limit[0] == update.client_order_id:
                    logging.info(f"Latest tp order update: {update}")
                    if update.status == OrderStatus.Created:
                        limit[4] = True
                        logging.info(
                            f"TP Limit order: {update.client_order_id} is {update.status}"
                        )
                    elif (
                        update.status == OrderStatus.Filled
                        or update.status == OrderStatus.PartiallyFilledCancelled
                    ):
                        try:
                            position = await strategy.position(
                                symbol=self.pair, exchange=place_order_exchange
                            )
                        except Exception as e:
                            logging.error(f"Failed to fetch position: {e}")
                        logging.info(
                            f"Latest position: {util.get_position_info(position,datetime.now(pytz.timezone("UTC")))}"
                        )

                        self.tp_order_pool.remove(limit)
                        logging.info(
                            f"Removed {limit} from tp_order_pool due to order {update.status}, current tp_order_pool: {self.tp_order_pool}"
                        )
                    elif (
                        update.status == OrderStatus.Cancelled
                        or update.status == OrderStatus.Rejected
                    ):
                        if limit[4] == False:
                            if limit[2] == True:
                                try:
                                    best_bid_ask = await util.get_order_book(
                                        strategy=strategy,
                                        exchange=place_order_exchange,
                                        pair=self.pair,
                                    )
                                    if (
                                        best_bid_ask[0] != 0.0
                                        and best_bid_ask[1] != 0.0
                                    ):
                                        if update.side == OrderSide.Buy:
                                            price = best_bid_ask[0]
                                        else:
                                            price = best_bid_ask[1]
                                        order_resp = await strategy.order(
                                            params=OrderParams(
                                                limit=price,
                                                side=update.side,
                                                quantity=update.remain_size,
                                                symbol=self.pair,
                                                exchange=place_order_exchange,
                                                is_hedge_mode=False,
                                                is_post_only=True,
                                            )
                                        )
                                        self.order_pool.append(
                                            [
                                                order_resp.client_order_id,
                                                datetime.now(timezone.utc),
                                                True,
                                                False,
                                                False,
                                                price,
                                                datetime.now(timezone.utc)
                                                + timedelta(
                                                    minutes=self.replace_limit_max_time_in_min
                                                ),
                                            ]
                                        )
                                        logging.info(
                                            f"Inserted a replace {update.side} tp limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                                        )
                                        logging.info(
                                            f"Placed a replace {update.side} tp order with qty {update.remain_size} when price: {price} due to order get rejected at time {datetime.now(timezone.utc)}"
                                        )
                                except Exception as e:
                                    logging.error(
                                        f"Failed to cancel and replace order: {e}"
                                    )
                        self.tp_order_pool.remove(limit)
                        logging.info(
                            f"Removed {limit} from tp_order_pool due to order {update.status}, current tp_order_pool: {self.tp_order_pool}"
                        )

    async def cancel_tp_order(self, strategy):
        for tp_order in self.tp_order_pool:
            if tp_order[3] == False:
                try:
                    await strategy.cancel(
                        exchange=place_order_exchange, id=tp_order[0], symbol=self.pair
                    )
                    logging.info(
                        f"Sent cancel for tp order {tp_order[0]}, is_pending: {tp_order[3]} at {datetime.now(timezone.utc)}"
                    )
                    tp_order[3] = True
                except Exception as e:
                    logging.error(f"Failed to cancel order: {e}")

    async def on_datasource_interval(self, strategy, topic, data_list):
        data = self.data_map[topic]
        # logging.info(f"topic: {topic}")
        now_utc = datetime.now(pytz.timezone("UTC"))
        closed_min_time = now_utc - timedelta(minutes=1)
        closed_min_time = closed_min_time.replace(second=0, microsecond=0)
        closed_min_time_ts = closed_min_time.timestamp() * 1000
        if topic == self.taker_vol_topic:
            start_time = np.array(list(map(lambda c: float(c["start_time"]), data)))
            taker_buy_volume = np.array(
                list(map(lambda c: float(c["taker_buy_volume"]), data))
            )
            taker_sell_volume = np.array(
                list(map(lambda c: float(c["taker_sell_volume"]), data))
            )
            if (
                closed_min_time_ts != start_time[-1]
                and runtime_mode != RuntimeMode.Backtest
            ):
                logging.info(
                    f"topic: {topic}, Latest min should get: {closed_min_time}, timestamp: {closed_min_time_ts}, datasource last data start_time: {start_time[-1]}, {util.convert_ms_to_datetime(start_time[-1])}"
                )
                return
            self.taker_buy_vol_arr = taker_buy_volume
            self.taker_sell_vol_arr = taker_sell_volume
            self.taker_vol_df = pd.DataFrame(
                {
                    "time": start_time,
                    "taker_buy_volume": taker_buy_volume,
                    "taker_sell_volume": taker_sell_volume,
                }
            )
            self.is_latest_taker_vol = True
            logging.info(
                f"topic: {topic}, is_latest_taker_vol: {self.is_latest_taker_vol}, is_latest_liquidation: {self.is_latest_liquidation}, Latest min should get: {closed_min_time}, timestamp: {closed_min_time_ts}, taker_sell_volume: {taker_sell_volume[-1]}, taker_buy_volume: {taker_buy_volume[-1]}, first_start_time: {util.convert_ms_to_datetime(start_time[0])}, prev_start_time: {util.convert_ms_to_datetime(start_time[-2])} at {util.convert_ms_to_datetime(start_time[-1])}"
            )
        elif topic == self.liquidation_topic:
            start_time = np.array(list(map(lambda c: float(c["start_time"]), data)))
            long_liquidations_usd = np.array(
                list(map(lambda c: float(c["long_liquidations_usd"]), data))
            )
            short_liquidations_usd = np.array(
                list(map(lambda c: float(c["short_liquidations_usd"]), data))
            )
            if (
                closed_min_time_ts != start_time[-1]
                and runtime_mode != RuntimeMode.Backtest
            ):
                logging.info(
                    f"topic: {topic}, Latest min should get: {closed_min_time}, timestamp: {closed_min_time_ts}, datasource last data start_time: {start_time[-1]}, {util.convert_ms_to_datetime(start_time[-1])}"
                )
                return
            self.liquidation_long_arr = long_liquidations_usd
            self.liquidation_short_arr = short_liquidations_usd
            self.liquidation_df = pd.DataFrame(
                {
                    "time": start_time,
                    "long_liquidations_usd": long_liquidations_usd,
                    "short_liquidations_usd": short_liquidations_usd,
                }
            )
            self.is_latest_liquidation = True
            logging.info(
                f"topic: {topic}, is_latest_taker_vol: {self.is_latest_taker_vol}, is_latest_liquidation: {self.is_latest_liquidation}, Latest min should get: {closed_min_time}, timestamp: {closed_min_time_ts}, short_liquidations_usd: {short_liquidations_usd[-1]}, long_liquidations_usd: {long_liquidations_usd[-1]}, first_start_time: {util.convert_ms_to_datetime(start_time[0])}, prev_start_time: {util.convert_ms_to_datetime(start_time[-2])} at {util.convert_ms_to_datetime(start_time[-1])}"
            )

        if self.is_latest_liquidation and self.is_latest_taker_vol:
            logging.info(
                f"Both data is latest, Latest min should get: {closed_min_time}, timestamp: {closed_min_time_ts}, taker_sell_volume: {self.taker_sell_vol_arr[-1]}, taker_buy_volume: {self.taker_buy_vol_arr[-1]}, short_liquidations_usd: {self.liquidation_short_arr[-1]}, long_liquidations_usd: {self.liquidation_long_arr[-1]}, first_start_time: {util.convert_ms_to_datetime(start_time[0])}, prev_start_time: {util.convert_ms_to_datetime(start_time[-2])} at {util.convert_ms_to_datetime(start_time[-1])}"
            )
            self.is_latest_liquidation = False
            self.is_latest_taker_vol = False
            if self.is_candle_closed:
                self.is_candle_closed = False
                # Set 'time' as the index
                self.taker_vol_df["time"] = pd.to_datetime(
                    self.taker_vol_df["time"], unit="ms"
                )
                self.liquidation_df["time"] = pd.to_datetime(
                    self.liquidation_df["time"], unit="ms"
                )
                # logging.info(f"taker_vol_df: {self.taker_vol_df.tail(10)}")
                # logging.info(f"liquidation_df: {self.liquidation_df.tail(10)}")
                self.taker_vol_df.set_index("time", inplace=True)
                self.liquidation_df.set_index("time", inplace=True)
                self.taker_vol_df = (
                    self.taker_vol_df[["taker_buy_volume", "taker_sell_volume"]]
                    .resample(self.resample_time)
                    .sum()
                )
                self.liquidation_df = (
                    self.liquidation_df[
                        ["long_liquidations_usd", "short_liquidations_usd"]
                    ]
                    .resample(self.resample_time)
                    .sum()
                )
                logging.info(
                    f"first taker_vol_df time: {self.taker_vol_df.index[0]}, last time: {self.taker_vol_df.index[-1]}, first liquidation_df time: {self.liquidation_df.index[0]}, last time: {self.liquidation_df.index[-1]}"
                )
                self.taker_vol_df.reset_index(inplace=True)
                self.liquidation_df.reset_index(inplace=True)
                # logging.info(f"taker_buy_volume: {self.taker_vol_df['taker_buy_volume'].F}, taker_sell_volume: {self.taker_vol_df['taker_sell_volume'].iat[-1]}, long_liquidations_usd: {self.liquidation_df['long_liquidations_usd'].iat[-1]}, short_liquidations_usd: {self.liquidation_df['short_liquidations_usd'].iat[-1]}, taker vol time: {self.taker_vol_df['time'].iat[-1]}, liquidation time: {self.liquidation_df['time'].iat[-1]}")
                latest_taker_buy_volume = self.taker_vol_df["taker_buy_volume"].values
                latest_taker_sell_volume = self.taker_vol_df["taker_sell_volume"].values
                latest_long_liquidations_usd = self.liquidation_df[
                    "long_liquidations_usd"
                ].values
                latest_short_liquidations_usd = self.liquidation_df[
                    "short_liquidations_usd"
                ].values
                data_time = self.taker_vol_df["time"].values
                latest_taker_buy_volume = latest_taker_buy_volume[
                    -self.rolling_window * 3 :
                ]
                latest_taker_sell_volume = latest_taker_sell_volume[
                    -self.rolling_window * 3 :
                ]
                latest_long_liquidations_usd = latest_long_liquidations_usd[
                    -self.rolling_window * 3 :
                ]
                latest_short_liquidations_usd = latest_short_liquidations_usd[
                    -self.rolling_window * 3 :
                ]
                data_time = data_time[-self.rolling_window * 3 :]
                net_liquidation = []
                liquidation_cascade = []
                self.high_low_chg = self.high_low_chg[-self.rolling_window * 3 :]
                self.candle_datetime = self.candle_datetime[-self.rolling_window * 3 :]
                logging.debug(
                    f"first candle_datetime time: {util.convert_ms_to_datetime(self.candle_datetime[0])}, last time: {util.convert_ms_to_datetime(self.candle_datetime[-1])}"
                )
                logging.debug(
                    f"high_low_chg length: {len(self.high_low_chg)}, latest_taker_buy_volume length: {len(latest_taker_buy_volume)}, latest_taker_sell_volume length: {len(latest_taker_sell_volume)}, latest_long_liquidations_usd length: {len(latest_long_liquidations_usd)}, latest_short_liquidations_usd length: {len(latest_short_liquidations_usd)}"
                )
                for i in range(0, len(latest_taker_buy_volume)):
                    net_liquidation.append(
                        latest_long_liquidations_usd[i]
                        - latest_short_liquidations_usd[i]
                    )
                for i in range(0, len(self.high_low_chg)):
                    if net_liquidation[i] > 0:
                        liquidation_cascade.append(
                            self.high_low_chg[i] * latest_taker_sell_volume[i]
                        )
                    elif net_liquidation[i] < 0:
                        liquidation_cascade.append(
                            self.high_low_chg[i] * latest_taker_buy_volume[i]
                        )
                    else:
                        liquidation_cascade.append(0.0)
                sum_net_liquidation = util.get_rolling_sum(
                    net_liquidation, self.rolling_window
                )
                sma_liquidation_cascade = util.get_rolling_mean(
                    liquidation_cascade, self.rolling_window
                )
                sma_net_liquidation = util.get_rolling_mean(
                    net_liquidation, self.rolling_window
                )
                try:
                    position = await strategy.position(
                        symbol=self.pair, exchange=place_order_exchange
                    )
                except Exception as e:
                    logging.error(f"Failed to fetch position: {e}")
                try:
                    wallet_balance = await strategy.get_current_available_balance(
                        exchange=place_order_exchange, symbol=self.pair
                    )
                except Exception as e:
                    logging.error(f"Failed to fetch wallet balance: {e}")
                if sma_net_liquidation[-1] > 0.0:
                    sma_net_liquidation_threshold_up = sma_net_liquidation[-1] * (
                        1.0 + self.multiplier
                    )
                    sma_net_liquidation_threshold_down = sma_net_liquidation[-1] * (
                        1.0 - self.multiplier
                    )
                else:
                    sma_net_liquidation_threshold_up = sma_net_liquidation[-1] * (
                        1.0 - self.multiplier
                    )
                    sma_net_liquidation_threshold_down = sma_net_liquidation[-1] * (
                        1.0 + self.multiplier
                    )
                if sma_liquidation_cascade[-1] > 0.0:
                    sma_liquidation_cascade_threshold_up = sma_liquidation_cascade[
                        -1
                    ] * (1.0 + self.multiplier)
                    sma_liquidation_cascade_threshold_down = sma_liquidation_cascade[
                        -1
                    ] * (1.0 - self.multiplier)
                else:
                    sma_liquidation_cascade_threshold_up = sma_liquidation_cascade[
                        -1
                    ] * (1.0 - self.multiplier)
                    sma_liquidation_cascade_threshold_down = sma_liquidation_cascade[
                        -1
                    ] * (1.0 + self.multiplier)
                logging.info(
                    f"current total_pnl: {self.total_pnl}, current position: {util.get_position_info(position, self.entry_time)} , replace_entry_order_count: {self.replace_entry_order_count}, replace_tp_order_count: {self.replace_tp_order_count}, cancel_entry_order_count: {self.cancel_entry_order_count}, net_liquidation: {net_liquidation[-1]}, liquidation_cascade: {liquidation_cascade[-1]}, sum_net_liquidation: {sum_net_liquidation[-1]}, sma_net_liquidation: {sma_net_liquidation[-1]}, sma_liquidation_cascade: {sma_liquidation_cascade[-1]}, sma_net_liquidation_up: {sma_net_liquidation_threshold_up}, sma_net_liquidation_down: {sma_net_liquidation_threshold_down}, sma_liquidation_cascade_up: {sma_liquidation_cascade_threshold_up}, sma_liquidation_cascade_down: {sma_liquidation_cascade_threshold_down}, high_low_chg: {self.high_low_chg[-1]} at {data_time[-1]}"
                )
                if (
                    position.long.quantity != 0.0
                    and closed_min_time_ts - self.event_entry_time
                    >= self.holding_time * 1000
                    and len(self.order_pool) == 0
                ):
                    if len(self.tp_order_pool) != 0:
                        await self.cancel_tp_order(strategy=strategy)
                    best_bid_ask = await util.get_order_book(
                        strategy=strategy,
                        exchange=place_order_exchange,
                        pair=self.pair,
                    )
                    if best_bid_ask[0] != 0.0 and best_bid_ask[1] != 0.0:
                        try:
                            order_resp = await strategy.order(
                                params=OrderParams(
                                    limit=best_bid_ask[1],
                                    side=OrderSide.Sell,
                                    quantity=abs(position.long.quantity),
                                    symbol=self.pair,
                                    exchange=place_order_exchange,
                                    is_hedge_mode=False,
                                    is_post_only=True,
                                )
                            )
                            self.order_pool.append(
                                [
                                    order_resp.client_order_id,
                                    datetime.now(timezone.utc),
                                    True,
                                    False,
                                    False,
                                ]
                            )
                            logging.info(
                                f"Inserted a close long limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                            )
                            logging.info(
                                f"Placed a close long order with qty {position.long.quantity} when price: {best_bid_ask[1]}, entry_time: {self.event_entry_time}, sma_net_liquidation_up: {sma_net_liquidation_threshold_up}, sma_net_liquidation_down: {sma_net_liquidation_threshold_down}, sma_liquidation_cascade_up: {sma_liquidation_cascade_threshold_up}, sma_liquidation_cascade_down: {sma_liquidation_cascade_threshold_down} at time {data_time[-1]}"
                            )
                            util.send_limit_order_telegram_msg(
                                telegram_chat_id=TELEGRAM_CHAT_ID,
                                telegram_token=TELEGRAM_TOKEN,
                                msg_type="close_long",
                                bot_id=self.bot_id,
                                qty=position.long.quantity,
                                price=best_bid_ask[1],
                                pair=self.pair,
                                position=position,
                                entry_time=self.entry_time,
                            )
                        except Exception as e:
                            logging.error(f"Failed to close entire position: {e}")
                elif (
                    position.short.quantity != 0.0
                    and closed_min_time_ts - self.event_entry_time
                    >= self.holding_time * 1000
                    and len(self.order_pool) == 0
                ):
                    if len(self.tp_order_pool) != 0:
                        await self.cancel_tp_order(strategy=strategy)
                    best_bid_ask = await util.get_order_book(
                        strategy=strategy,
                        exchange=place_order_exchange,
                        pair=self.pair,
                    )
                    if best_bid_ask[0] != 0.0 and best_bid_ask[1] != 0.0:
                        try:
                            order_resp = await strategy.order(
                                params=OrderParams(
                                    limit=best_bid_ask[0],
                                    side=OrderSide.Buy,
                                    quantity=abs(position.short.quantity),
                                    symbol=self.pair,
                                    exchange=place_order_exchange,
                                    is_hedge_mode=False,
                                    is_post_only=True,
                                )
                            )
                            self.order_pool.append(
                                [
                                    order_resp.client_order_id,
                                    datetime.now(timezone.utc),
                                    True,
                                    False,
                                    False,
                                ]
                            )
                            logging.info(
                                f"Inserted a close short limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                            )
                            logging.info(
                                f"Placed a close short order with qty {position.short.quantity} when price: {best_bid_ask[0]}, entry_time: {self.event_entry_time}, sma_net_liquidation_up: {sma_net_liquidation_threshold_up}, sma_net_liquidation_down: {sma_net_liquidation_threshold_down}, sma_liquidation_cascade_up: {sma_liquidation_cascade_threshold_up}, sma_liquidation_cascade_down: {sma_liquidation_cascade_threshold_down} at time {data_time[-1]}"
                            )
                            util.send_limit_order_telegram_msg(
                                telegram_chat_id=TELEGRAM_CHAT_ID,
                                telegram_token=TELEGRAM_TOKEN,
                                msg_type="close_short",
                                bot_id=self.bot_id,
                                qty=position.short.quantity,
                                price=best_bid_ask[0],
                                pair=self.pair,
                                position=position,
                                entry_time=self.entry_time,
                            )
                        except Exception as e:
                            logging.error(f"Failed to close entire position: {e}")

                if (
                    sum_net_liquidation[-1] > sma_net_liquidation_threshold_up
                    and liquidation_cascade[-1] > sma_liquidation_cascade_threshold_up
                    and position.short.quantity == 0.0
                    and len(self.order_pool) == 0
                ):
                    if len(self.tp_order_pool) != 0:
                        await self.cancel_tp_order(strategy=strategy)
                    best_bid_ask = await util.get_order_book(
                        strategy=strategy,
                        exchange=place_order_exchange,
                        pair=self.pair,
                    )
                    if best_bid_ask[0] != 0.0 and best_bid_ask[1] != 0.0:
                        if position.long.quantity != 0.0:
                            try:
                                order_resp = await strategy.order(
                                    params=OrderParams(
                                        limit=best_bid_ask[1],
                                        side=OrderSide.Sell,
                                        quantity=abs(position.long.quantity),
                                        symbol=self.pair,
                                        exchange=place_order_exchange,
                                        is_hedge_mode=False,
                                        is_post_only=True,
                                    )
                                )
                                self.order_pool.append(
                                    [
                                        order_resp.client_order_id,
                                        datetime.now(timezone.utc),
                                        True,
                                        False,
                                        False,
                                    ]
                                )
                                logging.info(
                                    f"Inserted a close long limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                                )
                                logging.info(
                                    f"Placed a close long order with qty {position.long.quantity} when price: {best_bid_ask[1]}, entry_time: {self.event_entry_time}, sma_net_liquidation_up: {sma_net_liquidation_threshold_up}, sma_net_liquidation_down: {sma_net_liquidation_threshold_down}, sma_liquidation_cascade_up: {sma_liquidation_cascade_threshold_up}, sma_liquidation_cascade_down: {sma_liquidation_cascade_threshold_down} at time {data_time[-1]}"
                                )
                                util.send_limit_order_telegram_msg(
                                    telegram_chat_id=TELEGRAM_CHAT_ID,
                                    telegram_token=TELEGRAM_TOKEN,
                                    msg_type="close_long",
                                    bot_id=self.bot_id,
                                    qty=position.long.quantity,
                                    price=best_bid_ask[1],
                                    pair=self.pair,
                                    position=position,
                                    entry_time=self.entry_time,
                                )
                            except Exception as e:
                                logging.error(f"Failed to close entire position: {e}")

                        qty = util.get_qty_with_percentage(
                            (best_bid_ask[0] + best_bid_ask[1]) / 2.0,
                            self.qty_precision,
                            self.leverage,
                            self.min_qty,
                            wallet_balance,
                        )
                        try:
                            self.event_entry_time = closed_min_time_ts
                            take_profit = (
                                (best_bid_ask[1] + best_bid_ask[0])
                                / 2.0
                                * (1.0 - self.tp_percentage)
                            )
                            order_resp = await strategy.order(
                                params=OrderParams(
                                    limit=best_bid_ask[1],
                                    side=OrderSide.Sell,
                                    quantity=qty,
                                    symbol=self.pair,
                                    exchange=place_order_exchange,
                                    is_hedge_mode=False,
                                    is_post_only=True,
                                )
                            )
                            self.order_pool.append(
                                [
                                    order_resp.client_order_id,
                                    datetime.now(timezone.utc),
                                    False,
                                    False,
                                    False,
                                ]
                            )
                            logging.info(
                                f"Inserted a sell limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                            )
                            order_resp1 = await strategy.order(
                                params=OrderParams(
                                    limit=take_profit,
                                    side=OrderSide.Buy,
                                    quantity=qty,
                                    symbol=self.pair,
                                    exchange=place_order_exchange,
                                    is_hedge_mode=False,
                                    is_post_only=True,
                                )
                            )
                            self.tp_order_pool.append(
                                [
                                    order_resp1.client_order_id,
                                    datetime.now(timezone.utc),
                                    False,
                                    False,
                                    False,
                                ]
                            )
                            logging.info(
                                f"Inserted a tp limit order with client_order_id: {order_resp1.client_order_id} into tp_order_pool"
                            )
                            logging.info(
                                f"Placed a sell order with qty {qty} when price: {best_bid_ask[1]}, entry_time: {closed_min_time_ts}, take_profit: {take_profit}, net_liquidation: {net_liquidation[-1]}, liquidation_cascade: {liquidation_cascade[-1]}, sum_net_liquidation: {sum_net_liquidation[-1]}, sma_net_liquidation: {sma_net_liquidation[-1]}, sma_liquidation_cascade: {sma_liquidation_cascade[-1]}, high_low_chg: {self.high_low_chg[-1]}, sma_net_liquidation_up: {sma_net_liquidation_threshold_up}, sma_net_liquidation_down: {sma_net_liquidation_threshold_down}, sma_liquidation_cascade_up: {sma_liquidation_cascade_threshold_up}, sma_liquidation_cascade_down: {sma_liquidation_cascade_threshold_down} at time {data_time[-1]}"
                            )
                            util.send_limit_order_telegram_msg(
                                telegram_chat_id=TELEGRAM_CHAT_ID,
                                telegram_token=TELEGRAM_TOKEN,
                                msg_type="open_short",
                                bot_id=self.bot_id,
                                qty=qty,
                                price=best_bid_ask[1],
                                pair=self.pair,
                                position=position,
                                entry_time=self.entry_time,
                            )
                        except Exception as e:
                            logging.error(f"Failed to place sell limit order: {e}")
                elif (
                    sum_net_liquidation[-1] < sma_net_liquidation_threshold_down
                    and liquidation_cascade[-1] < sma_liquidation_cascade_threshold_down
                    and position.long.quantity == 0.0
                    and len(self.order_pool) == 0
                ):
                    if len(self.tp_order_pool) != 0:
                        await self.cancel_tp_order(strategy=strategy)
                    best_bid_ask = await util.get_order_book(
                        strategy=strategy,
                        exchange=place_order_exchange,
                        pair=self.pair,
                    )
                    if best_bid_ask[0] != 0.0 and best_bid_ask[1] != 0.0:
                        if position.short.quantity != 0.0:
                            try:
                                order_resp = await strategy.order(
                                    params=OrderParams(
                                        limit=best_bid_ask[0],
                                        side=OrderSide.Buy,
                                        quantity=abs(position.short.quantity),
                                        symbol=self.pair,
                                        exchange=place_order_exchange,
                                        is_hedge_mode=False,
                                        is_post_only=True,
                                    )
                                )
                                self.order_pool.append(
                                    [
                                        order_resp.client_order_id,
                                        datetime.now(timezone.utc),
                                        True,
                                        False,
                                        False,
                                    ]
                                )
                                logging.info(
                                    f"Inserted a close short limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                                )
                                logging.info(
                                    f"Placed a close short order with qty {position.short.quantity} when price: {best_bid_ask[0]}, entry_time: {self.event_entry_time}, sma_net_liquidation_up: {sma_net_liquidation_threshold_up}, sma_net_liquidation_down: {sma_net_liquidation_threshold_down}, sma_liquidation_cascade_up: {sma_liquidation_cascade_threshold_up}, sma_liquidation_cascade_down: {sma_liquidation_cascade_threshold_down} at time {data_time[-1]}"
                                )
                                util.send_limit_order_telegram_msg(
                                    telegram_chat_id=TELEGRAM_CHAT_ID,
                                    telegram_token=TELEGRAM_TOKEN,
                                    msg_type="close_short",
                                    bot_id=self.bot_id,
                                    qty=position.short.quantity,
                                    price=best_bid_ask[0],
                                    pair=self.pair,
                                    position=position,
                                    entry_time=self.entry_time,
                                )
                            except Exception as e:
                                logging.error(f"Failed to close entire position: {e}")
                        qty = util.get_qty_with_percentage(
                            (best_bid_ask[0] + best_bid_ask[1]) / 2.0,
                            self.qty_precision,
                            self.leverage,
                            self.min_qty,
                            wallet_balance,
                        )
                        try:
                            self.event_entry_time = closed_min_time_ts
                            take_profit = (
                                (best_bid_ask[1] + best_bid_ask[0])
                                / 2.0
                                * (1.0 + self.tp_percentage)
                            )
                            order_resp = await strategy.order(
                                params=OrderParams(
                                    limit=best_bid_ask[0],
                                    side=OrderSide.Buy,
                                    quantity=qty,
                                    symbol=self.pair,
                                    exchange=place_order_exchange,
                                    is_hedge_mode=False,
                                    is_post_only=True,
                                )
                            )
                            self.order_pool.append(
                                [
                                    order_resp.client_order_id,
                                    datetime.now(timezone.utc),
                                    False,
                                    False,
                                    False,
                                ]
                            )
                            logging.info(
                                f"Inserted a buy limit order with client_order_id: {order_resp.client_order_id} into order_pool"
                            )
                            order_resp1 = await strategy.order(
                                params=OrderParams(
                                    limit=take_profit,
                                    side=OrderSide.Sell,
                                    quantity=qty,
                                    symbol=self.pair,
                                    exchange=place_order_exchange,
                                    is_hedge_mode=False,
                                    is_post_only=True,
                                )
                            )
                            self.tp_order_pool.append(
                                [
                                    order_resp1.client_order_id,
                                    datetime.now(timezone.utc),
                                    False,
                                    False,
                                    False,
                                ]
                            )
                            logging.info(
                                f"Inserted a tp limit order with client_order_id: {order_resp1.client_order_id} into tp_order_pool"
                            )
                            logging.info(
                                f"Placed a buy order with qty {qty} when price: {best_bid_ask[0]}, entry_time: {closed_min_time_ts}, take_profit: {take_profit}, net_liquidation: {net_liquidation[-1]}, liquidation_cascade: {liquidation_cascade[-1]}, sum_net_liquidation: {sum_net_liquidation[-1]}, sma_net_liquidation: {sma_net_liquidation[-1]}, sma_liquidation_cascade: {sma_liquidation_cascade[-1]}, high_low_chg: {self.high_low_chg[-1]}, sma_net_liquidation_up: {sma_net_liquidation_threshold_up}, sma_net_liquidation_down: {sma_net_liquidation_threshold_down}, sma_liquidation_cascade_up: {sma_liquidation_cascade_threshold_up}, sma_liquidation_cascade_down: {sma_liquidation_cascade_threshold_down} at time {data_time[-1]}"
                            )
                            util.send_limit_order_telegram_msg(
                                telegram_chat_id=TELEGRAM_CHAT_ID,
                                telegram_token=TELEGRAM_TOKEN,
                                msg_type="open_long",
                                bot_id=self.bot_id,
                                qty=qty,
                                price=best_bid_ask[0],
                                pair=self.pair,
                                position=position,
                                entry_time=self.entry_time,
                            )
                        except Exception as e:
                            logging.error(f"Failed to place buy limit order: {e}")

    async def on_candle_closed(self, strategy, topic, symbol):
         
        candles = self.data_map[topic]
        start_time = np.array(list(map(lambda c: float(c["start_time"]), candles)))
        close = np.array(list(map(lambda c: float(c["close"]), candles)))
        high = np.array(list(map(lambda c: float(c["high"]), candles)))
        low = np.array(list(map(lambda c: float(c["low"]), candles)))
        open = np.array(list(map(lambda c: float(c["open"]), candles)))
        logging.info(
            f"open: {open[-1]}, high: {high[-1]}, low: {low[-1]}, close: {close[-1]} at {util.convert_ms_to_datetime(start_time[-1])}"
        )
        current_high_low_chg = []
        for i in range(0, len(close)):
            if close[i] < open[i]:
                current_high_low_chg.append(high[i] / low[i] - 1 * -1.0)
            else:
                current_high_low_chg.append(high[i] / low[i] - 1)

        self.high_low_chg = current_high_low_chg
        self.candle_datetime = start_time
        self.is_candle_closed = True


config = RuntimeConfig(
    mode=runtime_mode,
    datasource_topics=[
        "cryptoquant|1m|btc/market-data/taker-buy-sell-stats?window=min&exchange=binance",
        "cryptoquant|1m|btc/market-data/liquidations?window=min&exchange=binance&symbol=btc_usdt",
    ],
    active_order_interval=60,
    initial_capital=1000000.0,
    candle_topics=["candles-15m-BTC/USDT-bybit"],
    start_time=datetime(2023, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
    end_time=datetime(2024, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
    api_key=CYBOTRADE_API_KEY,
    api_secret=CYBOTRADE_API_SECRET,
    data_count=5000,
    exchange_keys="./credentials.json",
)

permutation = Permutation(config)
hyper_parameters = {}
hyper_parameters["rolling_window"] = [88]
hyper_parameters["multiplier"] = [0.26]  # 125000


async def start_backtest():
    await permutation.run(hyper_parameters, Strategy)


asyncio.run(start_backtest())
