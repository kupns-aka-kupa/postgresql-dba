# Homework #7

Tasks

1. <a name="base">Base</a>
2. <a name="hotstandby">Hot Standby</a>

Hosts

- Master <a name="master">172.23.169.19</a>
- Replica10 <a name="r10">172.23.169.10</a>
- **Base** Replica35 <a name="base">172.23.169.35</a>
- **HotStandby** Replica9 <a name="hot">172.23.169.9</a>

## <a name="base"></a> Base

On

- [master](#master)
- [replica10](#r10)
- [replica35](#r35)

1. Conf

`postresql.conf`

```shell
listen_addresses = '*'
wal_level = logical
```

`pg_hba.conf`

```shell
host    postgres             all             0.0.0.0/0            md5
```

2. Exec sql

```sql
create database hw7;
create extension "uuid-ossp";
create table foo as
select uuid_generate_v4() as id
from generate_series(0, 1000);
alter table foo
    add constraint pk_foo_id primary key (id);

create table bar as table foo;
alter table bar
    add constraint pk_bar_id primary key (id);
```

- [master](#master)

```sql
create publication p for table bar;
create subscription s
    connection 'host=172.23.169.10 port=5434 user=postgres password=postgres dbname=hw7'
    publication p
    with (connect = true);
```

- [replica10](#r10)

```sql
create publication p for table foo;
create subscription s
    connection 'host=172.23.169.19 port=5432 user=postgres password=postgres dbname=hw7'
    publication p
    with (connect = true); 
```

Replication started

```shell
16:31:15.390 STATEMENT:  CREATE_REPLICATION_SLOT "s" LOGICAL pgoutput NOEXPORT_SNAPSHOT
16:31:15.422 LOG:  starting logical decoding for slot "s"
16:31:15.422 DETAIL:  Streaming transactions committing after 0/2183F20, reading WAL from 0/2183EE8.
16:31:15.422 STATEMENT:  START_REPLICATION SLOT "s" LOGICAL 0/0 (proto_version '1', publication_names '"p"')
16:31:15.422 LOG:  logical decoding found consistent point at 0/2183EE8
16:31:15.422 DETAIL:  There are no running transactions.
16:31:15.422 STATEMENT:  START_REPLICATION SLOT "s" LOGICAL 0/0 (proto_version '1', publication_names '"p"')
16:31:15.460 LOG:  logical decoding found consistent point at 0/2183F20
16:31:15.460 DETAIL:  There are no running transactions.
16:31:15.460 STATEMENT:  CREATE_REPLICATION_SLOT "s_16471_sync_16459" TEMPORARY LOGICAL pgoutput USE_SNAPSHOT
```

```sql
select count(*)
from foo
union all
select count(*)
from bar;
```

| table | [replica10](#r10) | [master](#master) |
|:-----:|:-----------------:|:-----------------:|
|  foo  |       1001        |       2002        |
|  bar  |       2002        |       1001        |

- [replica35](#r35)

```sql
create subscription sub_bar
    connection 'host=172.23.169.19 port=5432 user=postgres password=postgres dbname=hw7'
    publication p
    with (connect = true);
create subscription sub_foo
    connection 'host=172.23.169.10 port=5434 user=postgres password=postgres dbname=hw7'
    publication p
    with (connect = true);
```

| table | [replica35](#r35) |
|:-----:|:-----------------:|
|  foo  |       2002        |
|  bar  |       2002        |

## <a name="hotstandby"></a> Hot Standby

`pg_hba.conf`

```shell
host    replication             postgres             0.0.0.0/0            md5
```

```shell
sudo pg_createcluster 13 hw7
sudo rm -rf /var/lib/postgresql/13/hw7
sudo -u postgres pg_basebackup -p 5434 -h 172.23.169.35 -RD /var/lib/postgresql/13/hw7
```

`postresql.conf`

```shell
wal_level = hot_standby
```

```sql
postgres@172.23.169.35=#
select client_addr, state, sent_lsn
from pg_stat_replication;
``` 

| client\_addr | state     | sent\_lsn |
|:-------------|:----------|:----------|
| 172.23.169.9 | streaming | 0/B003A18 |

 ```sql
postgres@172.23.169.9=#
select status, sender_port, sender_host, latest_end_lsn
from pg_stat_wal_receiver;
```

| status    | sender_port | sender_host   | latest_end_lsn |
|-----------|-------------|---------------|----------------|
| streaming | 5434        | 172.23.169.35 | 0/B003A18      |

### Test

```sql
postgres@172.23.169.10=#
insert into hw7.public.bar
values (uuid_generate_v4());
```

```sql
postgres@172.23.169.9=# select count(*) from bar;
```

| count |
|-------|
| 2003  |

### Schema

![Schema](schema.svg)
