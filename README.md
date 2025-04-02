# Starting the Environment
```bash
docker-compose up
```

# Accessing the Application
- Django admin: http://localhost:8000/admin/ (login with admin/admin)
- Your app: http://localhost:8000/
- RQ dashboard: http://localhost:8000/django-rq/

# Scheduling Monitors
After starting the environment, run:
```bash
docker-compose exec web python manage.py schedule_monitors --clear
```

# Debugging
You can connect to any container:
```bash

docker-compose exec web python manage.py shell
docker-compose exec db psql -U upagent upagent_db
docker-compose exec redis redis-cli
```

