# Django Project with PostgreSQL

Project to control the notifications sent to clients. 

## Project Structure

The project is divided into three main applications:

1. **rates**: It contains service to check if rates for a certain type and user are ok.
2. **notifications**: Manages the creation, edition and sending of notifications.
3. **clients**: Handles client management.

## Environment Variables Setup

Before starting the application, make sure to configure the environment variables listed in the `.env.example` file at the root of the project, into a new `.env` file

## Running the app with Docker Compose
1. **Build the Docker images**
 `docker compose build`
2. **Start the containers**
 `docker compose up -d`
3. **Apply migrations inside container**
 `docker compose exec backend python3 manage.py migrate`
4. **Access app: in your browser, browse to `http://localhost:8000`**
5. **Run tests inside container**
 `docker compose exec backend python3 manage.py test`

## Testing in a Python shell
1. **Open a Python shell inside the container**
    `docker compose exec backend python3 manage.py shell`
2. **Create example Users**
    ```
    from clients.service import ClientsService
    clients_service = ClientsService()
    client_1 = clients_service.create_client(email='client_1@test.com')
    client_2 = clients_service.create_client(email='client_2@test.com')
    ```
3. **Create notification types with rates**
    ```
    from rates.service import RateLimitsService
    rates_service = RateLimitsService()
    type_1 = rates_service.create_notification_type_with_rate(name='type_1', max_times=1, minutes=1)
    type_2 = rates_service.create_notification_type_with_rate(name='type_2', max_times=2, minutes=1)
    ```
4. **Send notifications to users**
    ```
    from notifications.service import NotificationsService
    notif_service = NotificationsService()
    notif_service.send_notification(notif_type='type_1', client_uuid=client_1.uuid, message='Hello world')
    notif_service.send_notification(notif_type='type_1', client_uuid=client_2.uuid, message='Hello world')

    # This one should raise the RateLimitError
    notif_service.send_notification(notif_type='type_1', client_uuid=client_1.uuid, message='Hello world')

    notif_service.send_notification(notif_type='type_2', client_uuid=client_1.uuid, message='Hello world')
    notif_service.send_notification(notif_type='type_2', client_uuid=client_2.uuid, message='Hello world')
    notif_service.send_notification(notif_type='type_2', client_uuid=client_2.uuid, message='Hello world')
    
    # This one should raise the RateLimitError
    notif_service.send_notification(notif_type='type_2', client_uuid=client_2.uuid, message='Hello world')
    ```