FROM python:3.12-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install --upgrade pip


RUN pip install -r requirements.txt


COPY . .


RUN playwright install --with-deps chromium


CMD ["pytest", "-v", "--alluredir=reports/allure-results"]