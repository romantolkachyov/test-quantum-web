from django.core.management.base import BaseCommand

from quantum_web.worker.listener import QuantumListener


class Command(BaseCommand):
    help = 'Process quantum job queue'

    def handle(self, *args, **options):
        QuantumListener().run()
