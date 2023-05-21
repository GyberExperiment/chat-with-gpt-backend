import mindsdb_sdk

from pandas import DataFrame
from mindsdb_sdk.project import Project

from django.conf import settings

server = None


def connect_server() -> mindsdb_sdk.Server:
    global server

    if not server:
        server = mindsdb_sdk.connect(
            'https://cloud.mindsdb.com',
            login=settings.MINDSDB_USERNAME,
            password=settings.MINDSDB_PASSWORD
        )
    return server


def make_query(text: str, ctx: str = ''):
    text = text.replace("'", '"')
    return f""" SELECT * FROM mindsdb.gpt4 WHERE text = '{text}' AND ctx = '{ctx}' """


def send_message(text: str, ctx: str = '') -> DataFrame:
    ctx = 'Привет. Ты - хороший ассистент, к тебе будут приходить сообщения в таком формате: {"role": "user", "content": "вопрос от пользователя"}. Тебе нужно отвечать только на последний вопрос от пользователя в формате: {"role": "assistant", "content": "твой ответ"}\n%s' % ctx
    ctx.replace("'", '"')

    server: mindsdb_sdk.Server = connect_server()
    project: Project = server.get_project('mindsdb')
    result: DataFrame = project.query(make_query(str(text), ctx)).fetch()

    return result
