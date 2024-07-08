FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Upgrade pip and install the required packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "my_django_project.wsgi:application"]
