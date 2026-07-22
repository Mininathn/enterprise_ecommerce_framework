FROM mcr.microsoft.com/playwright/python:v1.54.0-noble


WORKDIR /app


COPY requirements.txt .


RUN pip install --upgrade pip


RUN pip install -r requirements.txt


COPY . .


CMD ["pytest", "-v", "--alluredir=reports/allure-results"]