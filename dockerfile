FROM python
RUN pip install youtube_dl pydub ffprobe pandas
RUN apt-get update -y &&  apt install ffmpeg -y
