# Homework #5

1. [System conf](#conf)
2. [Setup](#setup)
3. Benchmark settings
    - [Default](#default)
    - [Custom](#custom)
3. [Summary](#summary)

## <a name="conf"></a> System configuration

- DB Version: 13
- OS Type: linux
- DB Type: dw
- Total Memory (RAM): 16 GB
- CPUs num: 8
- Connections num: 128
- Data Storage: hdd

## <a name="setup"></a> Setup

1. Create table

```shell
sudo pg_createcluster 13 hw5 -D /home/hw5
sudo systemctl start postgresql@13-hw5
sudo -u postgres psql -c "create database hw5;"
```

2. Prepare

```shell
./tpcc.lua --pgsql-host=localhost \
--pgsql-user=postgres --pgsql-password=postgres \
--pgsql-db=hw5 --pgsql-port=5434 --db-driver=pgsql \
--time=300 --threads=64 --report-interval=10 --tables=10 \
--scale=100 prepare
```

3. Benchmark

```shell
./tpcc.lua --pgsql-host=localhost \
--pgsql-user=postgres --pgsql-password=postgres \
--pgsql-db=hw5 --pgsql-port=5434 --db-driver=pgsql \
--time=300 --threads=64 --report-interval=10 --tables=10 \
--scale=100 run
```

Conclusion

- `103G` data directory
- `~24h` prepare time 🤦

## <a name="default"></a> Default settings

```shell
SQL statistics:
    queries performed:
        read:                            14019
        write:                           14591
        other:                           2252
        total:                           30862
    transactions:                        1055   (2.88 per sec.)
    queries:                             30862  (84.27 per sec.)
    ignored errors:                      11     (0.03 per sec.)
    reconnects:                          0      (0.00 per sec.)

General statistics:
    total time:                          366.2127s
    total number of events:              1055

Latency (ms):
         min:                                 1015.80
         avg:                                19492.51
         max:                               176956.21
         95th percentile:                    66090.17
         sum:                             20564598.16

Threads fairness:
    events (avg/stddev):           16.4844/4.30
    execution time (avg/stddev):   321.3218/18.83
```

## <a name="custom"></a> Custom settings

`conf.d/00common.conf`

```shell
huge_pages = off
random_page_cost = 4
max_connections = 128
default_statistics_target = 500
synchronous_commit = off
```

Aggressive autovacuum

`conf.d/01autovacuum.conf`

```shell
autovacuum = on 
log_autovacuum_min_duration = 0
autovacuum_max_workers = 10
autovacuum_naptime = 5min
autovacuum_vacuum_scale_factor = 0.01 
autovacuum_analyze_scale_factor = 0.01 
autovacuum_vacuum_cost_delay = 1ms  
```

`conf.d/02checkpoint.conf`

```shell
checkpoint_completion_target = 0.9
checkpoint_timeout = 1h
log_checkpoints = on
```

`conf.d/03buffers.conf`

```shell
shared_buffers = 4GB # RAM / 3
work_mem = 32MB
effective_cache_size = 12GB # RAM * 2 / 3
maintenance_work_mem = 4GB
```

`conf.d/04wal.conf`

```shell
wal_buffers = 128MB 
min_wal_size = 4GB
max_wal_size = 16GB
```

`conf.d/05concurency.conf`

```shell
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
effective_io_concurrency = 2
```

`posgtresql.conf`

```shell
include_dir 'conf.d'
```

```shell
SQL statistics:
    queries performed:
        read:                            18059
        write:                           18777
        other:                           2910
        total:                           39746
    transactions:                        1382   (4.19 per sec.)
    queries:                             39746  (120.50 per sec.)
    ignored errors:                      12     (0.04 per sec.)
    reconnects:                          0      (0.00 per sec.)

General statistics:
    total time:                          329.8341s
    total number of events:              1382

Latency (ms):
         min:                                   10.83
         avg:                                14481.67
         max:                               198744.57
         95th percentile:                    71026.01
         sum:                             20013672.18

Threads fairness:
    events (avg/stddev):           21.5938/7.83
    execution time (avg/stddev):   312.7136/9.09
```

Clean up

```shell
./tpcc.lua --pgsql-host=localhost \
--pgsql-user=postgres --pgsql-password=postgres \
--pgsql-db=hw5 --pgsql-port=5434 --db-driver=pgsql \
--time=300 --threads=64 --report-interval=10 --tables=10 \
--scale=100 cleanup
```

or

```shell
 sudo pg_dropcluster 13 hw5 --stop
```

## <a name="custom"></a> Summary

- tps `45%` efficiency
