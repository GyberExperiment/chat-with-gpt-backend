import ujson

from rest_framework.request import Request
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import AssistantSerializer
from .services.connector import send_message
from .services.redis_client import RedisClient


class AssistantView(CreateAPIView):
    redis_client = RedisClient()

    serializer_class = AssistantSerializer

    @extend_schema(
        request=AssistantSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'role': {
                        'type': 'string',
                        'description': 'Role of the sender'
                    },
                    'content': {
                        'type': 'string',
                        'description': 'Message describing the result'
                    },
                }
            }
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        This endpoint is responsible for sending message it to MindsDB
        """
        message_data: dict = request.query_params

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data.get('user_id', False)
        chat_id = serializer.validated_data.get('chat_id', False)
        prompt = serializer.validated_data.get('content').replace("'", '"')
        text = {
            "role": "user",
            "content": f"{prompt}"
        }

        ctx = "\n".join(self.redis_client.get_context(user_id, chat_id)) \
            if not all((isinstance(user_id, bool), isinstance(chat_id, bool))) else ""
        
        print(ctx)

        # Send a message with context to the chatbot.
        # It will return the response in the format pd.DataFrame.
        content = send_message(str(text), ctx)['response'].values[0]
        self.redis_client.set_context(user_id, chat_id, str(text))
        self.redis_client.set_context(user_id, chat_id, content)

        return Response(ujson.loads(content))
  