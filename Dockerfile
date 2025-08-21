# This sets up the container with Python 3.10 installed.
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# This tells Docker to listen on port 80 at runtime. Port 80 is the standard port for HTTP.
EXPOSE 80

# This command creates a .streamlit directory in the home directory of the container.
RUN mkdir ~/.streamlit

# This copies your Streamlit configuration file into the .streamlit directory you just created.
RUN cp config.toml ~/.streamlit/config.toml

# This sets the default command for the container to run the app with Streamlit.
ENTRYPOINT ["streamlit", "run"]

# This command tells Streamlit to run your app.py script when the container starts.
CMD ["app.py"]