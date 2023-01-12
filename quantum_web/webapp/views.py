import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


async def start(request):
    """Schedule a new job."""
    job_id = str(uuid.uuid4())
    redis_client = await cache.client.get_client()
    await redis_client.rpush(settings.JOB_QUEUE, job_id)
    return JsonResponse({"job_id": job_id})
