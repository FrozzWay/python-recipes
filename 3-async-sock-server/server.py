import socket
import asyncio
from concurrent import futures


async def callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client = writer.get_extra_info('peername')
    print(f'Открыл соединение для клиента {client}')
    while True:
        await writer.drain()
        accepted_message = (await reader.readline()).decode('utf-8')
        if not accepted_message:
            break
        with futures.ThreadPoolExecutor() as e:
            if accepted_message == 'LIST\n':
                respond_with_message_list(e, writer, client)
            else:
                save_message(e, accepted_message, writer, client)
    writer.close()
    await writer.wait_closed()
    print(f'Закрыл соединение для клиента {client}')


def write_message_to_file(record: str):
    with open('data.txt', "a", encoding='utf-8') as file:
        file.write(record)


def read_messages_from_file() -> list[str]:
    with open('data.txt', "r+", encoding='utf-8') as file:
        return file.read().split('\n')


def respond_with_message_list(thread_executor, writer, client):
    future = thread_executor.submit(read_messages_from_file)
    data = future.result()
    response = ";".join(data)
    writer.write(response.encode('utf-8'))
    print(f'Отправил список сообщений клиенту {client}.')


def save_message(thread_executor, message, writer, client):
    future = thread_executor.submit(write_message_to_file, message)
    future.add_done_callback(
        lambda f: writer.write(f'Message added: "{message.strip()}"'.encode('utf-8'))
    )
    print(f'Сохранил сообщение "{message.strip()}" от клиента {client}')


async def supervisor(hostname, port):
    server = await asyncio.start_server(
        client_connected_cb=callback,
        host=hostname,
        port=port
    )
    addresses = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Обработка подключения к адресам {addresses}')
    await server.serve_forever()


def main():
    hostname = socket.gethostname()
    port = '8088'
    try:
        asyncio.run(supervisor(hostname, port))
    except KeyboardInterrupt:
        print('\nСервер остановлен.')


if __name__ == '__main__':
    main()