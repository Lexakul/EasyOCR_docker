FROM pytorch/pytorch:2.7.0-cuda12.6-cudnn9-runtime

# путь
WORKDIR /app
#Скопирую весь проект по пути app
ADD . /app/

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./run.py"]
