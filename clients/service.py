import logging
from clients.models import Client
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)

class ClientDoesNotExistError(Exception):
    pass

class ClientsService:
    def create_client(self, email):
        try:
            Client.objects.create(email=email)
        except IntegrityError:
            logger.error(f'Client with email {email} already exists')
            raise
    
        logger.info(f'Client {email} created successfully')
        return

    def get_client_by_uuid(self, uuid):
        try:
            return Client.objects.get(uuid=uuid)
        except Client.DoesNotExist:
            logger.error(f'Client with uuid {uuid} does not exist')
            raise ClientDoesNotExistError
