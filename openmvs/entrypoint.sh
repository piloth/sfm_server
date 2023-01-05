#!/bin/bash
set -xe
if ! [ -e /root/.ssh/id_rsa ] ; then
	ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa
fi
chmod 700 /root/.ssh
cat /root/.ssh/id_rsa.pub > /root/.ssh/authorized_keys
mkdir -p /run/sshd
/usr/sbin/sshd -D
