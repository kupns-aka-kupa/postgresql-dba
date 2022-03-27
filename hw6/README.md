# Homework #6

Hosts

- Master <a name="master">172.23.169.19</a>
- Backup <a name="backup">172.23.169.10 | localhost</a>

On [master](#master)

```shell
sudo pg_createcluster 13 hw6
sudo pg_ctlcluster 13 hw6 start
psql -p 5434 -b hw6 -U postgres -c 'create database hw6;'
```

```sql
begin;
create table test
(
    id text
);
insert into test
select i::text
from generate_series(0, 10000000) as t(i);

create role backup with login replication password 'backup';
grant usage on schema pg_catalog to backup;
grant execute on function pg_catalog.current_setting(text) to backup;
grant execute on function pg_catalog.set_config(text, text, boolean) to backup;
grant execute on function pg_catalog.pg_is_in_recovery() to backup;
grant execute on function pg_catalog.pg_start_backup(text, boolean, boolean) to backup;
grant execute on function pg_catalog.pg_stop_backup(boolean, boolean) to backup;
grant execute on function pg_catalog.pg_create_restore_point(text) to backup;
grant execute on function pg_catalog.pg_switch_wal() to backup;
grant execute on function pg_catalog.pg_last_wal_replay_lsn() to backup;
grant execute on function pg_catalog.txid_current() to backup;
grant execute on function pg_catalog.txid_current_snapshot() to backup;
grant execute on function pg_catalog.txid_snapshot_xmax(txid_snapshot) to backup;
grant execute on function pg_catalog.pg_control_checkpoint() to backup;
commit;
```

`pg_hba.conf`

```shell
host    replication     backup              172.23.169.10/0         md5
```

```shell
sudo pg_ctlcluster 13 hw6 restart
```

On [backup](#backup)

```shell
sudo -u postgres pg_probackup-13 init -B /var/lib/postgresql/dumps

sudo pg_probackup-13 add-instance --instance=hw6 --remote-host=172.23.169.19 \ 
--remote-user=postgres -D /var/lib/postgresql/13/hw6 -B /var/lib/postgresql/dumps \
--ssh-options='-i ~/.ssh/id_rsa_postgres'
```

```shell
sudo pg_probackup-13 backup --instance=hw6 -j2 --backup-mode=FULL \
--compress --stream --delete-expired -U backup --pgdatabase=hw6 \
--remote-host=172.23.169.19 --remote-user=postgres -B /var/lib/postgresql/dumps -p 5434 \
--ssh-options='-i ~/.ssh/id_rsa_postgres'

sudo pg_createcluster 13 hw6

sudo rm -rf /var/lib/postgresql/13/hw6

sudo pg_probackup-13 restore --instance=hw6 -B /var/lib/postgresql/dumps \
-D /var/lib/postgresql/13/hw6
```

```shell
INFO: Validating backup R9EOFX
INFO: Backup R9EOFX data files are valid
INFO: Backup R9EOFX WAL segments are valid
INFO: Backup R9EOFX is valid.
INFO: Restoring the database from backup at 2022-03-27 16:35:57+03
INFO: Start restoring backup files. PGDATA size: 393MB
INFO: Backup files are restored. Transfered bytes: 393MB, time elapsed: 0
INFO: Restore incremental ratio (less is better): 100% (393MB/393MB)
INFO: Syncing restored files to disk
INFO: Restored backup files are synced, time elapsed: 13s
INFO: Restore of backup R9EOFX completed.
```

```shell
sudo chown postgres:postgres -R /var/lib/postgresql/13/hw6
sudo pg_ctlcluster 13 hw6 start
```

Check

```shell
sudo -u postgres psql -p 5433 -d hw6 -c 'select count(*) from test;'
```

| count    |
|----------|
| 10001005 |

👏

---

Setup config for future backups

```shell
sudo pg_probackup-13 set-config -B /var/lib/postgresql/dumps --instance=hw6 \
-U backup --pgdatabase=hw6 --remote-host=172.23.169.19 --remote-user=postgres \
-p 5434 --ssh-options='-i ~/.ssh/id_rsa_postgres'
```

```shell
sudo pg_probackup-13 backup --instance=hw6 -j2 --backup-mode=FULL --compress --stream \
--delete-expired -B /var/lib/postgresql/dumps
```
