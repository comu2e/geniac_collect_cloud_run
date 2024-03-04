FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
RUN pip install poetry

# Set work directory
WORKDIR /geniac-collect-jp

# Copy project
COPY . /geniac-collect-jp/

# Install dependencies
RUN poetry config virtualenvs.create false
RUN poetry install
