from celery import shared_task

from documents.services.exports import run_export
from documents.services.lifecycle import run_generation


@shared_task(ignore_result=True)
def generate_document_task(document_id):
    run_generation(document_id)


@shared_task(ignore_result=True)
def export_document_task(export_id):
    run_export(export_id)
