# app/Dockerfile

# Using a specific version of Python
FROM python:3.10

# Setting a working directory
WORKDIR /app/

# Copy requirements.txt to the working directory
COPY ./requirements.txt ./

# Update system packages, install build-essential and python dependencies
RUN apt-get update && \
    apt-get install -y build-essential && \
    pip install --no-cache-dir -r requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Flask runs on port 5000 by default, expose it
# EXPOSE 80

# This is the command that will run when container starts
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
ENV PYTHONPATH="/app"
HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health
# use cmd instead of ENTRYPOINT so that you can use docker-compose run and override the command
CMD ["/bin/bash", "-c", "streamlit run streamlit_app.py --server.port=80 --server.address=0.0.0.0 –browser.serverAddress 0.0.0.0 –server.enableCORS False"]

EXPOSE 80