import logging
import subprocess
from pathlib import Path
from shutil import rmtree

from .extensions import celery
from .models import ScrapperTaskDocument, ScrapperTaskStatus
from .scrapper import Scrapper


logger = logging.getLogger()


class ScrapperTask:

    @staticmethod
    @celery.task
    def scrap_website(task_document_id: str, upload_dir: str):
        task_document = ScrapperTaskDocument.objects.get(id=task_document_id)
        task_document.status = ScrapperTaskStatus.IN_PROGRESS.value
        task_document.save()

        temp_dir = Path(upload_dir) / str(task_document.id)

        try:
            scrapper = Scrapper(task_document.url, temp_dir)
            scrapper.run()
            subprocess.run(
                ['zip', '-r', '-D', f'{task_document_id}.zip', task_document_id],
                check=True,
                cwd=Path(upload_dir)
            )
        except Exception as e:
            logger.log(logging.ERROR, e)
            task_document.status = ScrapperTaskStatus.FAILED.value
        else:
            task_document.download_link = f'/upload/{task_document_id}.zip'
            task_document.status = ScrapperTaskStatus.COMPLETE.value
        finally:
            rmtree(temp_dir, ignore_errors=True)

        task_document.save()
