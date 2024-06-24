FROM python:3.12-slim

WORKDIR /app



COPY requirements.txt requirements.txt

# Upgrade pip and install Python packages
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir psycopg2-binary && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=server.py

# Create a script to initialize the database and start the app
RUN echo '#!/bin/sh\n\
python3 -c "from server import create_tables; create_tables()"\n\
python3 -m flask run --host=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]