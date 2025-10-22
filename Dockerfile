FROM repo.irsl.eiiris.tut.ac.jp/irsl_system:one

WORKDIR /RoboManip

RUN git clone https://github.com/isri-aist/RoboManipBaselines.git --recursive

RUN apt update -q -qq && \
    apt install -q -qq -y ffmpeg python3-venv && \
    apt clean && \
    rm -rf /var/lib/apt/lists/

RUN python3 -m venv venv --copies

RUN source /RoboManip/venv/bin/activate && \
    cd /RoboManip/RoboManipBaselines && \
    sed -i -e 's@"torch"@"torch<2.9"@' pyproject.toml && \
    pip install -e .[act]  && \
    cd third_party/act/detr && \
    pip install -e .
