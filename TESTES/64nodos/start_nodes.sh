#!/bin/bash

set -e

HOST="${HOST:-0.0.0.0}"
START_PORT="9700"
export NODE_NUM="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64"

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

[program:node17]
command=start_indy_node Node17 $HOST 9733 $HOST 9734
directory=/home/indy
stdout_logfile=/tmp/node17.log
stderr_logfile=/tmp/node17.log

[program:node18]
command=start_indy_node Node18 $HOST 9735 $HOST 9736
directory=/home/indy
stdout_logfile=/tmp/node18.log
stderr_logfile=/tmp/node18.log

[program:node19]
command=start_indy_node Node19 $HOST 9737 $HOST 9738
directory=/home/indy
stdout_logfile=/tmp/node19.log
stderr_logfile=/tmp/node19.log

[program:node20]
command=start_indy_node Node20 $HOST 9739 $HOST 9740
directory=/home/indy
stdout_logfile=/tmp/node20.log
stderr_logfile=/tmp/node20.log

[program:node21]
command=start_indy_node Node21 $HOST 9741 $HOST 9742
directory=/home/indy
stdout_logfile=/tmp/node21.log
stderr_logfile=/tmp/node21.log

[program:node22]
command=start_indy_node Node22 $HOST 9743 $HOST 9744
directory=/home/indy
stdout_logfile=/tmp/node22.log
stderr_logfile=/tmp/node22.log

[program:node23]
command=start_indy_node Node23 $HOST 9745 $HOST 9746
directory=/home/indy
stdout_logfile=/tmp/node23.log
stderr_logfile=/tmp/node23.log

[program:node24]
command=start_indy_node Node24 $HOST 9747 $HOST 9748
directory=/home/indy
stdout_logfile=/tmp/node24.log
stderr_logfile=/tmp/node24.log

[program:node25]
command=start_indy_node Node25 $HOST 9749 $HOST 9750
directory=/home/indy
stdout_logfile=/tmp/node25.log
stderr_logfile=/tmp/node25.log

[program:node26]
command=start_indy_node Node26 $HOST 9751 $HOST 9752
directory=/home/indy
stdout_logfile=/tmp/node26.log
stderr_logfile=/tmp/node26.log

[program:node27]
command=start_indy_node Node27 $HOST 9753 $HOST 9754
directory=/home/indy
stdout_logfile=/tmp/node27.log
stderr_logfile=/tmp/node27.log

[program:node28]
command=start_indy_node Node28 $HOST 9755 $HOST 9756
directory=/home/indy
stdout_logfile=/tmp/node28.log
stderr_logfile=/tmp/node28.log

[program:node29]
command=start_indy_node Node29 $HOST 9757 $HOST 9758
directory=/home/indy
stdout_logfile=/tmp/node29.log
stderr_logfile=/tmp/node29.log

[program:node30]
command=start_indy_node Node30 $HOST 9759 $HOST 9760
directory=/home/indy
stdout_logfile=/tmp/node30.log
stderr_logfile=/tmp/node30.log

[program:node31]
command=start_indy_node Node31 $HOST 9761 $HOST 9762
directory=/home/indy
stdout_logfile=/tmp/node31.log
stderr_logfile=/tmp/node31.log

[program:node32]
command=start_indy_node Node32 $HOST 9763 $HOST 9764
directory=/home/indy
stdout_logfile=/tmp/node32.log
stderr_logfile=/tmp/node32.log

[program:node33]
command=start_indy_node Node33 $HOST 9765 $HOST 9766
directory=/home/indy
stdout_logfile=/tmp/node33.log
stderr_logfile=/tmp/node33.log

[program:node34]
command=start_indy_node Node34 $HOST 9767 $HOST 9768
directory=/home/indy
stdout_logfile=/tmp/node34.log
stderr_logfile=/tmp/node34.log

[program:node35]
command=start_indy_node Node35 $HOST 9769 $HOST 9770
directory=/home/indy
stdout_logfile=/tmp/node35.log
stderr_logfile=/tmp/node35.log

[program:node36]
command=start_indy_node Node36 $HOST 9771 $HOST 9772
directory=/home/indy
stdout_logfile=/tmp/node36.log
stderr_logfile=/tmp/node36.log

[program:node37]
command=start_indy_node Node37 $HOST 9773 $HOST 9774
directory=/home/indy
stdout_logfile=/tmp/node37.log
stderr_logfile=/tmp/node37.log

[program:node38]
command=start_indy_node Node38 $HOST 9775 $HOST 9776
directory=/home/indy
stdout_logfile=/tmp/node38.log
stderr_logfile=/tmp/node38.log

[program:node39]
command=start_indy_node Node39 $HOST 9777 $HOST 9778
directory=/home/indy
stdout_logfile=/tmp/node39.log
stderr_logfile=/tmp/node39.log

[program:node40]
command=start_indy_node Node40 $HOST 9779 $HOST 9780
directory=/home/indy
stdout_logfile=/tmp/node40.log
stderr_logfile=/tmp/node40.log

[program:node41]
command=start_indy_node Node41 $HOST 9781 $HOST 9782
directory=/home/indy
stdout_logfile=/tmp/node41.log
stderr_logfile=/tmp/node41.log

[program:node42]
command=start_indy_node Node42 $HOST 9783 $HOST 9784
directory=/home/indy
stdout_logfile=/tmp/node42.log
stderr_logfile=/tmp/node42.log

[program:node43]
command=start_indy_node Node43 $HOST 9785 $HOST 9786
directory=/home/indy
stdout_logfile=/tmp/node43.log
stderr_logfile=/tmp/node43.log

[program:node44]
command=start_indy_node Node44 $HOST 9787 $HOST 9788
directory=/home/indy
stdout_logfile=/tmp/node44.log
stderr_logfile=/tmp/node44.log

[program:node45]
command=start_indy_node Node45 $HOST 9789 $HOST 9790
directory=/home/indy
stdout_logfile=/tmp/node45.log
stderr_logfile=/tmp/node45.log

[program:node46]
command=start_indy_node Node46 $HOST 9791 $HOST 9792
directory=/home/indy
stdout_logfile=/tmp/node46.log
stderr_logfile=/tmp/node46.log

[program:node47]
command=start_indy_node Node47 $HOST 9793 $HOST 9794
directory=/home/indy
stdout_logfile=/tmp/node47.log
stderr_logfile=/tmp/node47.log

[program:node48]
command=start_indy_node Node48 $HOST 9795 $HOST 9796
directory=/home/indy
stdout_logfile=/tmp/node48.log
stderr_logfile=/tmp/node48.log

[program:node49]
command=start_indy_node Node49 $HOST 9797 $HOST 9798
directory=/home/indy
stdout_logfile=/tmp/node49.log
stderr_logfile=/tmp/node49.log

[program:node50]
command=start_indy_node Node50 $HOST 9799 $HOST 9800
directory=/home/indy
stdout_logfile=/tmp/node50.log
stderr_logfile=/tmp/node50.log

[program:node51]
command=start_indy_node Node51 $HOST 9801 $HOST 9802
directory=/home/indy
stdout_logfile=/tmp/node51.log
stderr_logfile=/tmp/node51.log

[program:node52]
command=start_indy_node Node52 $HOST 9803 $HOST 9804
directory=/home/indy
stdout_logfile=/tmp/node52.log
stderr_logfile=/tmp/node52.log

[program:node53]
command=start_indy_node Node53 $HOST 9805 $HOST 9806
directory=/home/indy
stdout_logfile=/tmp/node53.log
stderr_logfile=/tmp/node53.log

[program:node54]
command=start_indy_node Node54 $HOST 9807 $HOST 9808
directory=/home/indy
stdout_logfile=/tmp/node54.log
stderr_logfile=/tmp/node54.log

[program:node55]
command=start_indy_node Node55 $HOST 9809 $HOST 9810
directory=/home/indy
stdout_logfile=/tmp/node55.log
stderr_logfile=/tmp/node55.log

[program:node56]
command=start_indy_node Node56 $HOST 9811 $HOST 9812
directory=/home/indy
stdout_logfile=/tmp/node56.log
stderr_logfile=/tmp/node56.log

[program:node57]
command=start_indy_node Node57 $HOST 9813 $HOST 9814
directory=/home/indy
stdout_logfile=/tmp/node57.log
stderr_logfile=/tmp/node57.log

[program:node58]
command=start_indy_node Node58 $HOST 9815 $HOST 9816
directory=/home/indy
stdout_logfile=/tmp/node58.log
stderr_logfile=/tmp/node58.log

[program:node59]
command=start_indy_node Node59 $HOST 9817 $HOST 9818
directory=/home/indy
stdout_logfile=/tmp/node59.log
stderr_logfile=/tmp/node59.log

[program:node60]
command=start_indy_node Node60 $HOST 9819 $HOST 9820
directory=/home/indy
stdout_logfile=/tmp/node60.log
stderr_logfile=/tmp/node60.log

[program:node61]
command=start_indy_node Node61 $HOST 9821 $HOST 9822
directory=/home/indy
stdout_logfile=/tmp/node61.log
stderr_logfile=/tmp/node61.log

[program:node62]
command=start_indy_node Node62 $HOST 9823 $HOST 9824
directory=/home/indy
stdout_logfile=/tmp/node62.log
stderr_logfile=/tmp/node62.log

[program:node63]
command=start_indy_node Node63 $HOST 9825 $HOST 9826
directory=/home/indy
stdout_logfile=/tmp/node63.log
stderr_logfile=/tmp/node63.log

[program:node64]
command=start_indy_node Node64 $HOST 9827 $HOST 9828
directory=/home/indy
stdout_logfile=/tmp/node64.log
stderr_logfile=/tmp/node64.log

[program:printlogs]
command=tail -F /tmp/supervisord.log /tmp/node1.log /tmp/node2.log /tmp/node3.log /tmp/node4.log /tmp/node5.log /tmp/node6.log /tmp/node7.log /tmp/node8.log /tmp/node9.log /tmp/node10.log /tmp/node11.log /tmp/node12.log /tmp/node13.log /tmp/node14.log /tmp/node15.log /tmp/node16.log /tmp/node17.log /tmp/node18.log /tmp/node19.log /tmp/node20.log /tmp/node21.log /tmp/node22.log /tmp/node23.log /tmp/node24.log /tmp/node25.log /tmp/node26.log /tmp/node27.log /tmp/node28.log /tmp/node29.log /tmp/node30.log /tmp/node31.log /tmp/node32.log /tmp/node33.log /tmp/node34.log /tmp/node35.log /tmp/node36.log /tmp/node37.log /tmp/node38.log /tmp/node39.log /tmp/node40.log /tmp/node41.log /tmp/node42.log /tmp/node43.log /tmp/node44.log /tmp/node45.log /tmp/node46.log /tmp/node47.log /tmp/node48.log /tmp/node49.log /tmp/node50.log /tmp/node51.log /tmp/node52.log /tmp/node53.log /tmp/node54.log /tmp/node55.log /tmp/node56.log /tmp/node57.log /tmp/node58.log /tmp/node59.log /tmp/node60.log /tmp/node61.log /tmp/node62.log /tmp/node63.log /tmp/node64.log
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0

EOF

echo "Starting indy nodes"
supervisord
