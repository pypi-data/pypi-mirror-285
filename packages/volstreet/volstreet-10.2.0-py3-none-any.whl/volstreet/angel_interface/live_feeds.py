from multiprocessing import Process, Manager
from datetime import datetime
import asyncio
import traceback
from threading import Event, Thread
from volstreet.config import logger
from volstreet.decorators import classproperty
from volstreet.utils import current_time, timedelta
from volstreet.angel_interface.login import wait_for_login
from volstreet.angel_interface.order_websocket import OrderWebsocket
from volstreet.angel_interface.price_websocket import LocalSocket
from volstreet.angel_interface.async_interface import get_quotes_async


class LiveFeeds:
    price_feed = None
    order_feed = None
    price_feed_process = None
    order_feed_process = None
    back_up_event = Event()
    back_up_feed = {}
    back_up_time = datetime.now()
    back_up_tokens = set()

    @classmethod
    @wait_for_login
    def start_price_feed(cls, manager: Manager):
        socket = LocalSocket(manager=manager)
        process = Process(target=socket.connect)
        cls.price_feed_process = process
        cls.price_feed = socket
        process.start()
        cls.periodically_back_up()

    @classmethod
    @wait_for_login
    def start_order_feed(cls, manager: Manager, **kwargs):
        of = OrderWebsocket.from_active_session(manager, **kwargs)
        process = Process(target=of.connect)
        cls.order_feed_process = process
        cls.order_feed = of
        process.start()

    @classproperty
    def order_book(self) -> list:
        return list(self.order_feed.data_bank.values())

    @classmethod
    def order_feed_connected(cls):
        return cls.order_feed is not None and cls.order_feed.connected.value

    @classmethod
    def price_feed_connected(cls):
        return cls.price_feed is not None and cls.price_feed.connection_fresh.value

    @classmethod
    def close(cls):
        try:
            if cls.price_feed is not None and cls.price_feed_process is not None:
                cls.price_feed.intentionally_closed.value = True
            if cls.order_feed is not None:
                cls.order_feed.command_queue.put("close_connection")
        except Exception as e:
            logger.error(f"Error while closing live feeds: {e}")

    @classmethod
    def periodically_back_up(cls):
        last_check_time = current_time()

        def _inner():
            nonlocal last_check_time
            try:
                while True:
                    cls.back_up_event.wait(5)
                    if cls.back_up_tokens:
                        cls.back_up_feed = asyncio.run(
                            get_quotes_async(tokens=[*cls.back_up_tokens])
                        )
                        cls.back_up_time = current_time()
                    cls.back_up_event.clear()
                    if current_time() - last_check_time > timedelta(minutes=1):
                        logger.info(
                            f"Local socket connection fresh: {cls.price_feed_connected()}. "
                            f"Back up feed updated: {cls.back_up_time}."
                        )
                        last_check_time = current_time()
            except Exception as e:
                logger.error(
                    f"Error in back up thread. {e}\nTraceback: {traceback.format_exc()}"
                )
            finally:
                cls.back_up_feed = False

        thread = Thread(target=_inner)
        thread.start()
