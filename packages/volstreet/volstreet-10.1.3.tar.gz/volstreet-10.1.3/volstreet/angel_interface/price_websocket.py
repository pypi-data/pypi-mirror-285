import json
import struct
import zmq
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import time
from time import sleep
import threading
import uuid
from volstreet.config import token_symbol_dict, logger, token_exchange_dict
from volstreet.utils import current_time
from volstreet.angel_interface.base_websocket import BaseWebsocket


class PriceWebsocket(BaseWebsocket):
    LITTLE_ENDIAN_BYTE_ORDER = "<"

    # Available Actions
    SUBSCRIBE_ACTION = 1
    UNSUBSCRIBE_ACTION = 0

    # Possible Subscription Mode
    LTP_MODE = 1
    QUOTE = 2
    SNAP_QUOTE = 3
    DEPTH = 4

    # Exchange Type
    EXCHANGE_TYPE_MAP = {
        "NSE": 1,
        "NFO": 2,
        "BSE": 3,
        "BFO": 4,
        "MCX": 5,
        "NCDEX": 7,
        "CDS": 13,
    }

    # Subscription Mode Map
    SUBSCRIPTION_MODE_MAP = {1: "LTP", 2: "QUOTE", 3: "SNAP_QUOTE", 4: "DEPTH"}

    def __init__(
        self,
        auth_token,
        api_key,
        client_code,
        feed_token,
        manager,
        correlation_id="default",
        socket: zmq.Socket = None,
    ):
        self.correlation_id = correlation_id
        self.socket = socket
        self.request_dict_lock = None

        super().__init__(
            auth_token,
            api_key,
            client_code,
            feed_token,
            manager,
        )

        self.command_queue = manager.Queue()
        self.input_request_dict = manager.dict()
        self.underlying_options_subscribed = manager.dict()
        self.RESUBSCRIBE_FLAG = False
        self._processing_subscriptions = False

    @staticmethod
    def processing_subscriptions(
        func,
    ):  # This decorator is used to avoid updating strike range while
        # subscription processes are running
        def wrapper(self, *args, **kwargs):
            self._processing_subscriptions = True
            try:
                self.request_dict_lock.acquire()
                result = func(self, *args, **kwargs)
                return result
            finally:
                self.request_dict_lock.release()
                self._processing_subscriptions = False

        return wrapper

    @property
    def root_uri(self):
        return "wss://smartapisocket.angelone.in/smart-stream"

    @property
    def heart_beat_interval(self):
        return 10

    @property
    def websocket_type(self):
        return "Price websocket"

    def on_open(self, wsapp):
        self.request_dict_lock = (
            threading.Lock()
            if self.request_dict_lock is None
            else self.request_dict_lock
        )
        if self.RESUBSCRIBE_FLAG:
            self.resubscribe()
        super().on_open(wsapp)

    def on_data(self, wsapp, message, data_type, continue_flag):
        if data_type == 2:
            self.socket.send(message)

    def on_error(self, wsapp, error):
        super().on_error(wsapp, error)
        self.RESUBSCRIBE_FLAG = True

    def _create_payload(self, tokens: list):
        payload = defaultdict(list)
        for token in tokens:
            exchange = token_exchange_dict.get(token)
            if exchange:
                payload[self.EXCHANGE_TYPE_MAP[exchange]].append(token)
        return [{"exchangeType": key, "tokens": val} for key, val in payload.items()]

    def subscribe(self, tokens: list, mode: int = 3):
        payload = self._create_payload(tokens)
        self._subscribe(self.correlation_id, mode, payload)

    def unsubscribe(self, tokens: list, mode: int = 1):
        payload = self._create_payload(tokens)
        self._unsubscribe(self.correlation_id, mode, payload)

    def get_current_usage(
        self,
    ):  # Our usage should be capped at 1000 tokens.
        with self.request_dict_lock:
            return len(self.data_bank)

    @processing_subscriptions
    def _subscribe(self, correlation_id: str, mode: int, instruction_list: list[dict]):
        """
        This Function subscribe the price data for the given token
        Parameters
        ------
        correlation_id: string
            A 10 character alphanumeric ID client may provide which will be returned by the server in error response
            to indicate which request generated error response.
            Clients can use this optional ID for tracking purposes between request and corresponding error response.
        mode: integer
            It denotes the subscription type
            possible values -> 1, 2 and 3
            1 -> LTP
            2 -> Quote
            3 -> Snap Quote
        instruction_list: list of dict
            Sample Value ->
                [
                    { "exchangeType": 1, "tokens": ["10626", "5290"]},
                    {"exchangeType": 5, "tokens": [ "234230", "234235", "234219"]}
                ]
                exchangeType: integer
                possible values ->
                    1 -> nse_cm
                    2 -> nse_fo
                    3 -> bse_cm
                    4 -> bse_fo
                    5 -> mcx_fo
                    7 -> ncx_fo
                    13 -> cde_fo
                tokens: list of string
        """
        try:
            request_data = {
                "correlationID": correlation_id,
                "action": self.SUBSCRIBE_ACTION,
                "params": {"mode": mode, "tokenList": instruction_list},
            }
            if mode == 4:
                for token in instruction_list:
                    if token.get("exchangeType") != 1:
                        error_message = (
                            f"{self.websocket_type} subscribe error\n"
                            f"Invalid ExchangeType:{token.get('exchangeType')} "
                            f"Please check the exchange type and try again it support only 1 exchange type"
                        )
                        logger.error(error_message)
                        raise ValueError(error_message)

            if mode == self.DEPTH:
                total_tokens = sum(
                    len(instruction["tokens"]) for instruction in instruction_list
                )
                quota_limit = 50
                if total_tokens > quota_limit:
                    error_message = (
                        f"Price websocket quota exceeded: "
                        f"You can subscribe to a maximum of {quota_limit} tokens only."
                    )
                    logger.error(error_message)
                    raise Exception(error_message)
            logger.info(
                f"Before subscribing input_request_dict: {self.input_request_dict}"
            )
            if self.input_request_dict.get(mode) is None:
                self.input_request_dict[mode] = defaultdict(list)

            for instruction in instruction_list:
                logger.info(f"Executing {instruction} to input_request_dict")
                # We need to update it in this way because it is a shared dict (read the docs)
                d = self.input_request_dict[mode]
                d[instruction["exchangeType"]].extend(instruction["tokens"])
                self.input_request_dict[mode] = d
                logger.info(f"Updated input_request_dict: {self.input_request_dict}")

            logger.info(
                f"After subscribing input_request_dict: {self.input_request_dict}"
            )

            self.wsapp.send(json.dumps(request_data))
            self.RESUBSCRIBE_FLAG = True
            sleep(1)

        except Exception as e:
            logger.error(f"Price websocket error occurred during subscribe: {e}")
            raise e

    @processing_subscriptions
    def _unsubscribe(self, correlation_id, mode, token_list):
        """
        This function unsubscribe the data for given token
        Parameters
        ------
        correlation_id: string
            A 10 character alphanumeric ID client may provide which will be returned by the server in error response
            to indicate which request generated error response.
            Clients can use this optional ID for tracking purposes between request and corresponding error response.
        mode: integer
            It denotes the subscription type
            possible values -> 1, 2 and 3
            1 -> LTP
            2 -> Quote
            3 -> Snap Quote
        token_list: list of dict
            Sample Value ->
                [
                    { "exchangeType": 1, "tokens": ["10626", "5290"]},
                    {"exchangeType": 5, "tokens": [ "234230", "234235", "234219"]}
                ]
                exchangeType: integer
                possible values ->
                    1 -> nse_cm
                    2 -> nse_fo
                    3 -> bse_cm
                    4 -> bse_fo
                    5 -> mcx_fo
                    7 -> ncx_fo
                    13 -> cde_fo
                tokens: list of string
        """
        # Remove unsubscribed tokens from input_request_dict
        for token_dict in token_list:
            exchange_type = token_dict["exchangeType"]
            tokens_to_remove = token_dict["tokens"]
            if (
                mode in self.input_request_dict
                and exchange_type in self.input_request_dict[mode]
            ):
                d = self.input_request_dict[mode]
                d[exchange_type] = [
                    token
                    for token in self.input_request_dict[mode][exchange_type]
                    if token not in tokens_to_remove
                ]
                self.input_request_dict[mode] = d
        try:
            request_data = {
                "correlationID": correlation_id,
                "action": self.UNSUBSCRIBE_ACTION,
                "params": {"mode": mode, "tokenList": token_list},
            }
            self.wsapp.send(json.dumps(request_data))
            self.RESUBSCRIBE_FLAG = True
            sleep(1)
        except Exception as e:
            logger.error(f"Price websocket error occurred during unsubscribe: {e}")
            raise e

        # Remove unsubscribed tokens from data_bank
        for token_dict in token_list:
            tokens_to_remove = token_dict["tokens"]
            for token in tokens_to_remove:
                self.data_bank.pop(token, None)

    @processing_subscriptions
    def resubscribe(self):
        try:
            for key, val in self.input_request_dict.items():
                token_list = []
                for key1, val1 in val.items():
                    temp_data = {"exchangeType": key1, "tokens": val1}
                    token_list.append(temp_data)
                request_data = {
                    "action": self.SUBSCRIBE_ACTION,
                    "params": {"mode": key, "tokenList": token_list},
                }
                self.wsapp.send(json.dumps(request_data))
                sleep(1)
        except Exception as e:
            logger.error(f"{self.websocket_type} resubscribe error: {e}")
            raise e

    def subscribe_indices(self):
        self.subscribe(
            ["99926000", "99926009", "99926037", "99926074", "99919000", "99919012"],
            mode=1,
        )


class LocalSocket:

    def __init__(self, manager, subscription_port=5555):
        self.subscription_port = subscription_port
        self.data_bank = manager.dict()
        self.intentionally_closed = manager.Value("b", False)
        self.connection_fresh = manager.Value("b", False)

    def connect(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(f"tcp://localhost:{self.subscription_port}")
        socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # Start the freshness check thread
        threading.Thread(target=self.periodically_check_freshness, daemon=True).start()

        try:
            while True and not self.intentionally_closed.value:
                data = socket.recv()
                # data, delay = decompose_message_with_identity(data)
                data = parse_binary_data(data)
                data = format_message_for_data_bank(data)
                self.data_bank.update(data)
        finally:
            self.connection_fresh.value = False
            socket.close()
            context.term()

    def periodically_check_freshness(self):
        while True and not self.intentionally_closed.value:
            self.connection_fresh.value = check_price_feed_freshness(self.data_bank)
            sleep(1)


def extract_timestamps_for_monitoring(data_bank):
    time_now = current_time()
    timestamps = {key: value["timestamp"] for key, value in data_bank.items()}
    timestamps = {
        key: value
        for key, value in sorted(timestamps.items(), key=lambda item: item[1])
    }
    timestamps = convert_tokens_to_symbols(timestamps)
    return timestamps, time_now


def check_price_feed_freshness(data_bank):
    # This method will update the connection_stale flag. The idea is to check the
    # Freshness based on data in teh databank rather than the connection status.
    if len(data_bank) > 0:
        try:
            time_now = current_time()
            most_recent_timestamp = max(
                [value["timestamp"] for value in data_bank.values()]
            )
            if time_now - most_recent_timestamp > timedelta(seconds=5):
                return False
            else:
                return True
        except Exception as e:
            logger.error(f"Error in checking freshness of data: {e}")
    else:
        return False


def add_identifier_to_message(original_message):
    # Generate a unique identifier and get the current time
    msg_id = uuid.uuid4().int & ((1 << 64) - 1)  # Using only the first 64 bits of UUID
    timestamp_sent = time.time()

    # Pack the ID and timestamp into a binary format (16 bytes for UUID, 8 bytes for timestamp)
    header = struct.pack(
        "!Qd", msg_id, timestamp_sent
    )  # ! for network order, Q for unsigned long long, d for double

    # Combine the header with the original message
    prepared_message = header + original_message
    return prepared_message


def decompose_message_with_identity(received_message):
    # Unpack the first 16 bytes for the UUID and the next 8 bytes for the timestamp
    msg_id, timestamp_sent = struct.unpack("!Qd", received_message[:16])

    # The rest is the original message
    original_message = received_message[16:]

    # Calculate the delay
    delay = time.time() - timestamp_sent
    # print(f"Message ID: {msg_id} - Delay: {delay:.4f} seconds")
    return original_message, delay


def format_message_for_data_bank(message):
    formatted_message = {
        message["token"]: {
            "ltp": message["last_traded_price"] / 100,
            "best_bid": (
                message["best_5_sell_data"][0]["price"] / 100
                if "best_5_sell_data" in message
                else None
            ),
            # 'best_5_sell_data' is not present in 'mode 1' messages
            "best_bid_qty": (
                message["best_5_sell_data"][0]["quantity"]
                if "best_5_sell_data" in message
                else None
            ),
            "best_ask": (
                message["best_5_buy_data"][0]["price"] / 100
                if "best_5_buy_data" in message
                else None
            ),
            "best_ask_qty": (
                message["best_5_buy_data"][0]["quantity"]
                if "best_5_buy_data" in message
                else None
            ),
            "timestamp": datetime.fromtimestamp(
                message["exchange_timestamp"] / 1000,
                tz=timezone(timedelta(hours=5, minutes=30)),
            ).replace(tzinfo=None),
            "last_traded_datetime": (
                datetime.fromtimestamp(
                    message["last_traded_timestamp"],
                    tz=timezone(timedelta(hours=5, minutes=30)),
                ).replace(tzinfo=None)
                if "last_traded_timestamp" in message
                else None
            ),
            **message,
        }
    }
    return formatted_message


def convert_tokens_to_symbols(data_dict):
    new_price_dict = {
        token_symbol_dict[token]: value for token, value in data_dict.items()
    }
    return new_price_dict


def parse_binary_data(binary_data):
    parsed_data = {
        "subscription_mode": _unpack_data(binary_data, 0, 1, byte_format="B")[0],
        "exchange_type": _unpack_data(binary_data, 1, 2, byte_format="B")[0],
        "token": _parse_token_value(binary_data[2:27]),
        "sequence_number": _unpack_data(binary_data, 27, 35, byte_format="q")[0],
        "exchange_timestamp": _unpack_data(binary_data, 35, 43, byte_format="q")[0],
        "last_traded_price": _unpack_data(binary_data, 43, 51, byte_format="q")[0],
    }
    try:
        subscription_mode_map = {1: "LTP", 2: "QUOTE", 3: "SNAP_QUOTE", 4: "DEPTH"}
        parsed_data["subscription_mode_val"] = subscription_mode_map.get(
            parsed_data["subscription_mode"]
        )

        if parsed_data["subscription_mode"] in [2, 3]:
            parsed_data["last_traded_quantity"] = _unpack_data(
                binary_data, 51, 59, byte_format="q"
            )[0]
            parsed_data["average_traded_price"] = _unpack_data(
                binary_data, 59, 67, byte_format="q"
            )[0]
            parsed_data["volume_trade_for_the_day"] = _unpack_data(
                binary_data, 67, 75, byte_format="q"
            )[0]
            parsed_data["total_buy_quantity"] = _unpack_data(
                binary_data, 75, 83, byte_format="d"
            )[0]
            parsed_data["total_sell_quantity"] = _unpack_data(
                binary_data, 83, 91, byte_format="d"
            )[0]
            parsed_data["open_price_of_the_day"] = _unpack_data(
                binary_data, 91, 99, byte_format="q"
            )[0]
            parsed_data["high_price_of_the_day"] = _unpack_data(
                binary_data, 99, 107, byte_format="q"
            )[0]
            parsed_data["low_price_of_the_day"] = _unpack_data(
                binary_data, 107, 115, byte_format="q"
            )[0]
            parsed_data["closed_price"] = _unpack_data(
                binary_data, 115, 123, byte_format="q"
            )[0]

        if parsed_data["subscription_mode"] == 3:
            parsed_data["last_traded_timestamp"] = _unpack_data(
                binary_data, 123, 131, byte_format="q"
            )[0]
            parsed_data["open_interest"] = _unpack_data(
                binary_data, 131, 139, byte_format="q"
            )[0]
            parsed_data["open_interest_change_percentage"] = _unpack_data(
                binary_data, 139, 147, byte_format="q"
            )[0]
            parsed_data["upper_circuit_limit"] = _unpack_data(
                binary_data, 347, 355, byte_format="q"
            )[0]
            parsed_data["lower_circuit_limit"] = _unpack_data(
                binary_data, 355, 363, byte_format="q"
            )[0]
            parsed_data["52_week_high_price"] = _unpack_data(
                binary_data, 363, 371, byte_format="q"
            )[0]
            parsed_data["52_week_low_price"] = _unpack_data(
                binary_data, 371, 379, byte_format="q"
            )[0]
            best_5_buy_and_sell_data = _parse_best_5_buy_and_sell_data(
                binary_data[147:347]
            )
            parsed_data["best_5_buy_data"] = best_5_buy_and_sell_data[
                "best_5_sell_data"
            ]
            parsed_data["best_5_sell_data"] = best_5_buy_and_sell_data[
                "best_5_buy_data"
            ]

        if parsed_data["subscription_mode"] == 4:
            parsed_data.pop("sequence_number", None)
            parsed_data.pop("last_traded_price", None)
            parsed_data.pop("subscription_mode_val", None)
            parsed_data["packet_received_time"] = _unpack_data(
                binary_data, 35, 43, byte_format="q"
            )[0]
            depth_data_start_index = 43
            depth_20_data = _parse_depth_20_buy_and_sell_data(
                binary_data[depth_data_start_index:]
            )
            parsed_data["depth_20_buy_data"] = depth_20_data["depth_20_buy_data"]
            parsed_data["depth_20_sell_data"] = depth_20_data["depth_20_sell_data"]

        return parsed_data
    except Exception as e:
        logger.error(f"Price websocket error occurred during binary data parsing: {e}")
        raise e


def _unpack_data(binary_data, start, end, byte_format="I"):
    """
    Unpack Binary Data to the integer according to the specified byte_format.
    This function returns the tuple
    """
    return struct.unpack("<" + byte_format, binary_data[start:end])


def _parse_token_value(binary_packet):
    token = ""
    for i in range(len(binary_packet)):
        if chr(binary_packet[i]) == "\x00":
            return token
        token += chr(binary_packet[i])
    return token


def _parse_best_5_buy_and_sell_data(binary_data):
    def split_packets(binary_packets):
        packets = []

        i = 0
        while i < len(binary_packets):
            packets.append(binary_packets[i : i + 20])
            i += 20
        return packets

    best_5_buy_sell_packets = split_packets(binary_data)

    best_5_buy_data = []
    best_5_sell_data = []

    for packet in best_5_buy_sell_packets:
        each_data = {
            "flag": _unpack_data(packet, 0, 2, byte_format="H")[0],
            "quantity": _unpack_data(packet, 2, 10, byte_format="q")[0],
            "price": _unpack_data(packet, 10, 18, byte_format="q")[0],
            "no of orders": _unpack_data(packet, 18, 20, byte_format="H")[0],
        }

        if each_data["flag"] == 0:
            best_5_buy_data.append(each_data)
        else:
            best_5_sell_data.append(each_data)

    return {
        "best_5_buy_data": best_5_buy_data,
        "best_5_sell_data": best_5_sell_data,
    }


def _parse_depth_20_buy_and_sell_data(binary_data):
    depth_20_buy_data = []
    depth_20_sell_data = []

    for i in range(20):
        buy_start_idx = i * 10
        sell_start_idx = 200 + i * 10

        # Parse buy data
        buy_packet_data = {
            "quantity": _unpack_data(
                binary_data, buy_start_idx, buy_start_idx + 4, byte_format="i"
            )[0],
            "price": _unpack_data(
                binary_data, buy_start_idx + 4, buy_start_idx + 8, byte_format="i"
            )[0],
            "num_of_orders": _unpack_data(
                binary_data, buy_start_idx + 8, buy_start_idx + 10, byte_format="h"
            )[0],
        }

        # Parse sell data
        sell_packet_data = {
            "quantity": _unpack_data(
                binary_data, sell_start_idx, sell_start_idx + 4, byte_format="i"
            )[0],
            "price": _unpack_data(
                binary_data, sell_start_idx + 4, sell_start_idx + 8, byte_format="i"
            )[0],
            "num_of_orders": _unpack_data(
                binary_data,
                sell_start_idx + 8,
                sell_start_idx + 10,
                byte_format="h",
            )[0],
        }

        depth_20_buy_data.append(buy_packet_data)
        depth_20_sell_data.append(sell_packet_data)

    return {
        "depth_20_buy_data": depth_20_buy_data,
        "depth_20_sell_data": depth_20_sell_data,
    }
