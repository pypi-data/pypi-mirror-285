# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import asyncio
import inspect
import aio_pika
import async_timeout

from .publish import RabbitMQProducerForExchangePool
from .consume import RabbitMQConsumerForExchange

from ...extend.error import catch_error
from ...extend.asyncio.base import Utils


STREAM_EOF: bytes = b'\0\0'


class RpcServerError(Exception): pass


def get_routing_key(server_name: typing.Optional[str]) -> str:
    return f'rpc_server.{server_name}' if server_name else r'rpc_server'


class RpcServer:

    def __init__(
            self, pool_size: int, connection: aio_pika.RobustConnection, exchange_name: str,
            *, server_name: typing.Optional[str] = None, message_ttl: float = 60, max_priority: int = 10
    ):

        self._rpc_function: typing.Dict[str, typing.Callable] = {}

        self._queue_name: str = get_routing_key(server_name)
        self._exchange_name: str = exchange_name

        self._queue_config: typing.Dict[str, typing.Any] = {
            r'arguments': {
                r'x-message-ttl': round(message_ttl * 1000),
                r'x-max-priority': max_priority,
            }
        }

        self._producer: RabbitMQProducerForExchangePool = RabbitMQProducerForExchangePool(
            pool_size, connection, self._exchange_name
        )

        self._consumer: RabbitMQConsumerForExchange = RabbitMQConsumerForExchange(
            connection, self._queue_name, self._exchange_name
        )

    async def open(self):

        self._rpc_function[r'ping'] = lambda: r'pong'

        await self._producer.open(
            exchange_type=aio_pika.ExchangeType.TOPIC
        )

        await self._consumer.open(
            consume_func=self._consume_message,
            consume_no_ack=False,
            queue_config=self._queue_config,
            channel_qos_config={r'prefetch_count': self._producer.size}
        )

    async def close(self):

        await self._producer.close()
        await self._consumer.close()

        self._rpc_function.clear()

    async def _reply_message(self, incoming: aio_pika.IncomingMessage, func_name: str, data: typing.Any):

        await self._producer.publish(
            aio_pika.Message(
                body=Utils.msgpack_encode(
                    {
                        r'name': func_name,
                        r'data': data,
                    }
                ),
                correlation_id=incoming.correlation_id
            ),
            routing_key=incoming.reply_to
        )

    async def _reply_error(self, incoming: aio_pika.IncomingMessage, func_name: str, error: str):

        await self._producer.publish(
            aio_pika.Message(
                body=Utils.msgpack_encode(
                    {
                        r'name': func_name,
                        r'error': error,
                    }
                ),
                correlation_id=incoming.correlation_id
            ),
            routing_key=incoming.reply_to
        )

    async def _reply_eof(self, incoming: aio_pika.IncomingMessage):

        await self._producer.publish(
            aio_pika.Message(
                body=STREAM_EOF,
                correlation_id=incoming.correlation_id
            ),
            routing_key=incoming.reply_to
        )

    async def _consume_message(self, message: aio_pika.IncomingMessage):

        with catch_error():

            _message = Utils.msgpack_decode(message.body)

            Utils.log.info(f'rpc client request: {_message}')

            _func_name = _message.get(r'name')
            _func_args = _message.get(r'args')
            _func_kwargs = _message.get(r'kwargs')

            if _func_name not in self._rpc_function:
                raise Exception(f'function {_func_name} not found')

            try:

                result = self._rpc_function[_func_name](*_func_args, **_func_kwargs)

                if inspect.iscoroutine(result):
                    await self._reply_message(message, _func_name, await result)
                elif inspect.isasyncgen(result):
                    async for _item in result:
                        await self._reply_message(message, _func_name, _item)
                    else:
                        await self._reply_eof(message)
                else:
                    raise Exception(f'function {_func_name} not supported')

            except Exception as err:
                await self._reply_error(message, _func_name, str(err))
                raise err

        await message.ack()

    def register(self, name: str, func: typing.Callable):

        self._rpc_function[name] = func

        Utils.log.info(f'rpc server register {name} {func}')


class RpcClient:

    def __init__(
            self, pool_size: int, connection: aio_pika.RobustConnection,
            exchange_name: str, message_ttl: float = 60
    ):

        self._unary_response: typing.Dict[str, asyncio.Future] = {}
        self._stream_response: typing.Dict[str, asyncio.Queue] = {}

        self._queue_name: str = f'rpc_client.{Utils.uuid1()}'
        self._exchange_name: str = exchange_name

        self._queue_config: typing.Dict[str, typing.Any] = {
            r'exclusive': True,
            r'arguments': {r'x-message-ttl': round(message_ttl * 1000)}
        }

        self._producer: RabbitMQProducerForExchangePool = RabbitMQProducerForExchangePool(
            pool_size, connection, self._exchange_name
        )

        self._consumer: RabbitMQConsumerForExchange = RabbitMQConsumerForExchange(
            connection, self._queue_name, self._exchange_name
        )

    async def open(self):

        await self._producer.open(
            exchange_type=aio_pika.ExchangeType.TOPIC
        )

        await self._consumer.open(
            consume_func=self._consume_message,
            consume_no_ack=False,
            queue_config=self._queue_config,
            channel_qos_config={r'prefetch_count': 1}
        )

    async def close(self):

        await self._producer.close()
        await self._consumer.close()

    async def _send_message(self, correlation_id: str, priority: int, server_name: str, message: typing.Any):

        await self._producer.publish(
            aio_pika.Message(
                Utils.msgpack_encode(message),
                priority=priority,
                correlation_id=correlation_id,
                reply_to=self._consumer.queue_name,
            ),
            routing_key=get_routing_key(server_name),
        )

    async def _consume_message(self, message: aio_pika.IncomingMessage):

        with catch_error():

            message_body = message.body
            correlation_id = message.correlation_id

            if correlation_id in self._unary_response:
                self._unary_response[correlation_id].set_result(message_body)
            elif correlation_id in self._stream_response:
                self._stream_response[correlation_id].put_nowait(message_body)
            else:
                raise Exception(f'unexpected correlation_id: {correlation_id}')

        await message.ack()

    async def ping(self, priority: int = 0, server_name: typing.Optional[str] = None):
        return await self.call(r'ping', priority=priority, server_name=server_name)

    async def call(
            self, name: str, *,
            args: typing.Optional[typing.List] = None,
            kwargs: typing.Optional[typing.Dict] = None,
            priority: int = 0,
            server_name: typing.Optional[str] = None,
            request_timeout: float = 60
    ):

        correlation_id = Utils.uuid1()

        unary_response = self._unary_response[correlation_id] = asyncio.Future()

        try:

            async with async_timeout.timeout(request_timeout):

                await self._send_message(
                    correlation_id, priority, server_name,
                    {
                        r'name': name,
                        r'args': args if args is not None else [],
                        r'kwargs': kwargs if kwargs is not None else {},
                    }
                )

                response = Utils.msgpack_decode(await unary_response)

                if r'error' in response:
                    raise RpcServerError(response[r'error'])

                return response[r'data']

        except asyncio.TimeoutError as err:
            Utils.log.error(f'rpc call timeout: {name=} {args=} {kwargs=}')
            raise err

        finally:
            del self._unary_response[correlation_id]

    async def call_stream(
            self, name: str, *,
            args: typing.Optional[typing.List] = None,
            kwargs: typing.Optional[typing.Dict] = None,
            priority: int = 0,
            server_name: typing.Optional[str] = None,
            request_timeout: float = 3600
    ):

        correlation_id = Utils.uuid1()

        stream_response = self._stream_response[correlation_id] = asyncio.Queue()

        try:

            async with async_timeout.timeout(request_timeout):

                await self._send_message(
                    correlation_id, priority, server_name,
                    {
                        r'name': name,
                        r'args': args if args is not None else [],
                        r'kwargs': kwargs if kwargs is not None else {},
                    }
                )

                while (response := await stream_response.get()) != STREAM_EOF:

                    response = Utils.msgpack_decode(response)

                    if r'error' in response:
                        raise RpcServerError(response[r'error'])

                    yield response[r'data']

        except asyncio.TimeoutError as err:
            Utils.log.error(f'rpc call timeout: {name=} {args=} {kwargs=}')
            raise err

        finally:
            del self._stream_response[correlation_id]
