# Homework #5

1. Create table

```sql
create database hw5;
```

2. Prepare

```shell
./tpcc.lua --pgsql-host=localhost \
--pgsql-user=postgres --pgsql-password=postgres \
--pgsql-db=hw5 --pgsql-port=5432 --db-driver=pgsql \
--time=300 --threads=64 --report-interval=1 --tables=10 \
--scale=100 prepare
```

3. Benchmark

```shell
./tpcc.lua --pgsql-host=localhost \
--pgsql-user=postgres --pgsql-password=postgres \
--pgsql-db=hw5 --pgsql-port=5432 --db-driver=pgsql \
--time=300 --threads=64 --report-interval=1 --tables=10 \
--scale=100 run
```

4. Clean up

```shell
./tpcc.lua --pgsql-host=localhost \
--pgsql-user=postgres --pgsql-password=postgres \
--pgsql-db=hw5 --pgsql-port=5432 --db-driver=pgsql \
--time=300 --threads=64 --report-interval=1 --tables=10 \
--scale=100 cleanup
```
