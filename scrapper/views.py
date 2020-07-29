import re
from http import HTTPStatus

from flask import request, Response, current_app
from flask.views import MethodView

from .models import ScrapperTaskDocument
from .task import ScrapperTask


class TasksAPI(MethodView):
    URL_REGEX = regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def get(self, task_id: str):
        document: ScrapperTaskDocument = ScrapperTaskDocument.objects.get_or_404(id=task_id)
        return document.to_json(), HTTPStatus.OK

    def post(self):
        try:
            url: str = self.get_url_from_request()
        except ValueError as e:
            return {"error": str(e)}, HTTPStatus.BAD_REQUEST
        document: ScrapperTaskDocument = self.create_scrap_task(url)
        return document.to_json(), HTTPStatus.CREATED

    def get_url_from_request(self) -> str:
        request_data = request.get_json()
        url = request_data.get('url')
        if url is None:
            raise NotImplementedError
        if not re.match(self.URL_REGEX, url):
            raise ValueError('Invalid URL')
        return url

    @classmethod
    def create_scrap_task(cls, url: str) -> ScrapperTaskDocument:
        task_document = ScrapperTaskDocument(
            url=url
        )
        task_document.save()
        ScrapperTask.scrap_website.delay(str(task_document.id), str(current_app.config['UPLOAD_DIR']))
        return task_document
