FROM tensorflow/tensorflow

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

CMD python -u ./bot.py
