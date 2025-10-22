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
    pip install -e .[act]  && \
    cd third_party/act/detr && \
    pip install -e .

## add for fix torch version
#    sed -i -e 's@"torch"@"torch<2.9"@' pyproject.toml && \

## SARNN
RUN source /RoboManip/venv/bin/activate && \
    cd /RoboManip/RoboManipBaselines && \
    pip install -e .[sarnn] && \ 
    cd third_party/eipl && \
    pip install -e .

## Diffusion Policy
RUN apt update -q -qq && \
    apt install -q -qq -y libosmesa6-dev libglfw3 patchelf && \
    apt clean && \
    rm -rf /var/lib/apt/lists/
# libgl1-mesa-glx is not required in irsl_system
RUN source /RoboManip/venv/bin/activate && \
    cd /RoboManip/RoboManipBaselines && \
    pip install -e .[diffusion-policy] && \
    cd third_party/diffusion_policy && \
    pip install -e .

## other policies
