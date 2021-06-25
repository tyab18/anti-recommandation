FROM python:3.9

RUN pip install flask
RUN pip install natto-py pandas sklearn emoji
RUN apt update && apt install -y mecab libmecab-dev mecab-ipadic-utf8 git make curl xz-utils file swig

RUN apt install -y sudo
RUN git clone https://github.com/neologd/mecab-ipadic-neologd.git
RUN cd mecab-ipadic-neologd && ./bin/install-mecab-ipadic-neologd -n -y
RUN ln -s /usr/lib/x86_64-linux-gnu/mecab/ /usr/local/lib/mecab
