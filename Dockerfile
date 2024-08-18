FROM python:3.10

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
EXPOSE 3030

ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
COPY run.sh /app/
RUN mkdir -p /app/sessions
CMD ["bash", "/app/run.sh"]