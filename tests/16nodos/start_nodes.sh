#!/bin/bash

set -e

HOST="${HOST:-0.0.0.0}"
START_PORT="9700"
export NODE_NUM="1 2 3 4 5 6 7 8"

if [ ! -d "/home/indy/ledger/sandbox/keys" ]; then
    echo "Ledger does not exist - Creating..."
    bash ./scripts/init_genesis.sh
fi

cat <<EOF > supervisord.conf
[supervisord]
logfile = /tmp/supervisord.log
logfile_maxbytes = 50MB
logfile_backups=10
loglevel = info
pidfile = /tmp/supervisord.pid
nodaemon = true
minfds = 1024
minprocs = 200
umask = 022
user = indy
identifier = supervisor
directory = /tmp
nocleanup = true
childlogdir = /tmp
strip_ansi = false

[program:node1]
command=start_indy_node Node1 $HOST 9701 $HOST 9702
directory=/home/indy
stdout_logfile=/tmp/node1.log
stderr_logfile=/tmp/node1.log

[program:node2]
command=start_indy_node Node2 $HOST 9703 $HOST 9704
directory=/home/indy
stdout_logfile=/tmp/node2.log
stderr_logfile=/tmp/node2.log

[program:node3]
command=start_indy_node Node3 $HOST 9705 $HOST 9706
directory=/home/indy
stdout_logfile=/tmp/node3.log
stderr_logfile=/tmp/node3.log

[program:node4]
command=start_indy_node Node4 $HOST 9707 $HOST 9708
directory=/home/indy
stdout_logfile=/tmp/node4.log
stderr_logfile=/tmp/node4.log

[program:node5]
command=start_indy_node Node5 $HOST 9709 $HOST 9710
directory=/home/indy
stdout_logfile=/tmp/node5.log
stderr_logfile=/tmp/node5.log

[program:node6]
command=start_indy_node Node5 $HOST 9711 $HOST 9712
directory=/home/indy
stdout_logfile=/tmp/node6.log
stderr_logfile=/tmp/node6.log

[program:node7]
command=start_indy_node Node5 $HOST 9713 $HOST 9714
directory=/home/indy
stdout_logfile=/tmp/node7.log
stderr_logfile=/tmp/node7.log

[program:node8]
command=start_indy_node Node5 $HOST 9715 $HOST 9716
directory=/home/indy
stdout_logfile=/tmp/node8.log
stderr_logfile=/tmp/node8.log

[program:node9]
command=start_indy_node Node9 $HOST 9717 $HOST 9718
directory=/home/indy
stdout_logfile=/tmp/node9.log
stderr_logfile=/tmp/node9.log

[program:node10]
command=start_indy_node Node10 $HOST 9719 $HOST 9720
directory=/home/indy
stdout_logfile=/tmp/node10.log
stderr_logfile=/tmp/node10.log

[program:node11]
command=start_indy_node Node11 $HOST 9721 $HOST 9722
directory=/home/indy
stdout_logfile=/tmp/node11.log
stderr_logfile=/tmp/node11.log

[program:node12]
command=start_indy_node Node12 $HOST 9723 $HOST 9724
directory=/home/indy
stdout_logfile=/tmp/node12.log
stderr_logfile=/tmp/node12.log

[program:node13]
command=start_indy_node Node13 $HOST 9725 $HOST 9726
directory=/home/indy
stdout_logfile=/tmp/node13.log
stderr_logfile=/tmp/node13.log

[program:node14]
command=start_indy_node Node14 $HOST 9727 $HOST 9728
directory=/home/indy
stdout_logfile=/tmp/node14.log
stderr_logfile=/tmp/node14.log

[program:node15]
command=start_indy_node Node15 $HOST 9729 $HOST 9730
directory=/home/indy
stdout_logfile=/tmp/node15.log
stderr_logfile=/tmp/node15.log

[program:node16]
command=start_indy_node Node16 $HOST 9731 $HOST 9732
directory=/home/indy
stdout_logfile=/tmp/node16.log
stderr_logfile=/tmp/node16.log

[program:printlogs]
command=tail -F /tmp/supervisord.log /tmp/node1.log /tmp/node2.log /tmp/node3.log /tmp/node4.log /tmp/node5.log /tmp/node6.log /tmp/node7.log /tmp/node8.log /tmp/node9.log /tmp/node10.log /tmp/node11.log /tmp/node12.log /tmp/node13.log /tmp/node14.log /tmp/node15.log /tmp/node16.log
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0

EOF

echo "Starting indy nodes"
supervisord
