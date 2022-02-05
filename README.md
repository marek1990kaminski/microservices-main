commands to build flask app:
`docker-compose exec backend /bin/bash`

inside run:  
`python manager.py db init` - this will cause migrations folder to appear  
`python manager.py db migrate` - this will trigger 'alembic_version' table to appear  
`python manager.py db upgrade` - this will trigger actual migration
