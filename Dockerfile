# TestBot
#
# by Zebra North
#
# The directory is mounted into the container under /workspaces/TestBot

FROM python:3.12-slim-bookworm

# Install Git.
RUN apt update && apt install -y git

# Install Python modules.
COPY requirements.txt /root
RUN pip3 install -r /root/requirements.txt

# Don't actually run anything.
CMD sleep 10000d
