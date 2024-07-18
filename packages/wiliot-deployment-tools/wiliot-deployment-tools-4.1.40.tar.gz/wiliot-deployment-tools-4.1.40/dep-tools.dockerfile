FROM python:3.8 

RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan bitbucket.org >> ~/.ssh/known_hosts

RUN --mount=type=ssh ssh git@bitbucket.org

WORKDIR /wlt

RUN pip install wiliot-core && \
cp /usr/local/lib/python3.8/site-packages/wiliot_core/utils/update_wiliot_packages.py update_wiliot_packages.py && \
pip uninstall -y wiliot-core

RUN --mount=type=ssh python update_wiliot_packages.py -p wiliot-api -n && \
python update_wiliot_packages.py -p wiliot-core -n

COPY "config" /root/.local/share/wiliot/common/configs/