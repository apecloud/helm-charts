########################################################
#                                                      #
#                  Configuration                       #
#                                                      #
########################################################

######### 0. Client only configurations #############

# The interval for CLI to send heartbeat to mnode
# shellActivityTimer        3


############### 1. Cluster End point ############################

# The end point of the first dnode in the cluster to be connected to when this dnode or the CLI utility is started
# firstEp                   hostname:6030

# The end point of the second dnode to be connected to if the firstEp is not available
# secondEp


############### 2. Configuration Parameters of current dnode #####

# The FQDN of the host on which this dnode will be started. It can be IP address
# fqdn                      hostname

# The port for external access after this dnode is started
# serverPort                6030

# The maximum number of connections a dnode can accept
# maxShellConns             5000

# The directory for writing log files, if you are using Windows platform please change to Windows path
# logDir                    /var/log/taos

# All data files are stored in this directory, if you are using Windows platform please change to Windows path
# dataDir                   /var/lib/taos

# temporary file's directory, if you are using Windows platform please change to Windows path
# tempDir                   /tmp/

# Switch for allowing to collect and report service usage information
# telemetryReporting        1

# Switch for allowing to collect and report crash information
# crashReporting            1

# The maximum number of vnodes supported by this dnode
# supportVnodes             0

# The interval of this dnode reporting status to mnode, [1..10] seconds
# statusInterval            1

# The minimum sliding window time, milli-second
# minSlidingTime            10

# The minimum time window, milli-second
# minIntervalTime           10

# The maximum allowed query buffer size in MB during query processing for each data node
# -1 no limit (default)
# 0  no query allowed, queries are disabled
# queryBufferSize           -1

# The compressed rpc message, option:
#  -1 (no compression)
#   0 (all message compressed),
# > 0 (rpc message body which larger than this value will be compressed)
# compressMsgSize           -1

# query retrieved column data compression option:
#  -1 (no compression)
#   0 (all retrieved column data compressed),
# > 0 (any retrieved column size greater than this value all data will be compressed.)
# compressColData           -1

# system time zone
# timezone                  UTC-8

# system time zone (for windows 10)
# timezone              Asia/Shanghai (CST, +0800)

# system locale
# locale                    en_US.UTF-8

# system charset
# charset                   UTF-8

# stop writing logs when the disk size of the log folder is less than this value
# minimalLogDirGB           1.0

# stop writing temporary files when the disk size of the tmp folder is less than this value
# minimalTmpDirGB           1.0

# if free disk space is less than this value, this dnode will fail to start
# minimalDataDirGB          2.0

# enable/disable system monitor
monitor                   1
monitorFqdn               localhost

# The following parameter is used to limit the maximum number of lines in log files.
# max number of lines per log filters
# numOfLogLines             10000000

# write log in async way: 1 - async, 0 - sync
# asyncLog                  1

# time period of keeping log files, in days
# logKeepDays               0


############ 3. Debug Flag and levels #############################################

# The following parameters are used for debug purpose only by this dnode.
# debugFlag is a 8 bits mask: FILE-SCREEN-UNUSED-HeartBeat-DUMP-TRACE_WARN-ERROR
# Available debug levels are:
# 131: output warning and error
# 135: output debug, warning and error
# 143: output trace, debug, warning and error to log
# 199: output debug, warning and error to both screen and file
# 207: output trace, debug, warning and error to both screen and file

# debug flag for all log type, take effect when non-zero value
# debugFlag                 0

# debug flag for timer
# tmrDebugFlag              131

# debug flag for util
# uDebugFlag                131

# debug flag for rpc
# rpcDebugFlag              131

# debug flag for jni
# jniDebugFlag              131

# debug flag for query
# qDebugFlag                131

# debug flag for client driver
# cDebugFlag                131

# debug flag for dnode messages
# dDebugFlag                135

# debug flag for vnode
# vDebugFlag                131

# debug flag for meta management messages
# mDebugFlag                135

# debug flag for wal
# wDebugFlag                135

# debug flag for sync module
# sDebugFlag                135

# debug flag for tsdb
# tsdbDebugFlag             131

# debug flag for tq
# tqDebugFlag               131

# debug flag for fs
# fsDebugFlag               131

# debug flag for udf
# udfDebugFlag              131

# debug flag for sma
# smaDebugFlag              131

# debug flag for index
# idxDebugFlag              131

# debug flag for tdb
# tdbDebugFlag              131

# debug flag for meta
# metaDebugFlag             131

# generate core file when service crash
# enableCoreFile            1