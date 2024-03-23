import requests
import logging
from django.shortcuts import render
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HelloView(APIView):
    def get(self, request):
        logger.info("Calling httpbin")
        try:
            response = requests.get("https://httpbin.org/delay/2")
            logger.info("Received the response")
            data = response.json()
        except requests.ConnectionError:
            logger.critical("Couldn't reach httpbin")
        return render(request, "hello.html", {"name": "amir"})
