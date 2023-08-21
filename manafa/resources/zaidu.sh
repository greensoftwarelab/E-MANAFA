# !/bin/bash

config_file=$1
output_file=$2
test -z "$1" && config_file="/storage/emulated/0/zaidu/resources/perfetto.config.bin"
test -z "$2" && output_file="/data/misc/perfetto-traces/trace"

cat $config_file | perfetto --background -o$output_file --config -
