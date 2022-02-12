# Homework #2

Hosts

- Master <a name="master">172.23.169.19</a>
- Slave <a name="slave">172.23.169.20</a>

Content

1. [Base exercise](#base)
2. [Exercise*](#extended)

## <a name="base"></a> Ex

1. Check cluster

```shell
sudo -u postgres pg_lsclusters
--------------------------------------

Ver Cluster Port Status Owner    Data directory              Log file
12  main    5432 online postgres /var/lib/postgresql/12/main /var/log/postgresql/postgresql-12-main.log
```

2. Copy database schema from [Homework #1](https://gitlab.rd.aorti.ru/nkupreenkov/dba/-/blob/master/hw1/README.md)

```shell
postgres=# create database hw2 template hw1;
postgres=# \c hw2
hw2=# insert into authors(name, masterpiece)
hw2-# values ('Smash Mouth', 'All Star');
```

3. Stop cluster

```shell
sudo systemctl stop postgresql@12-main
sudo systemctl is-active postgresql@12-main 
--------------------------------------
failed
```

4. Mount data dir

- Current partitions status

```shell
lsblk
--------------------------------------
sda           8:0    0 931,5G  0 disk 
└─sda1        8:1    0 931,5G  0 part 
```

- Setup partitions

```shell
sudo parted /dev/sda rm 1

sudo parted -a opt /dev/sda mkpart primary ext4 0% 90%
sudo parted -a opt /dev/sda mkpart ext4 90% 100%
sudo mkfs.ext4 -L postgresdata /dev/sda2

lsblk
--------------------------------------
sda           8:0    0 931,5G  0 disk 
├─sda1        8:1    0 838,4G  0 part 
└─sda2        8:2    0  93,2G  0 part 
```

- Mount data directory

```shell
sudo mkdir -p /mnt/data
sudo mount -o defaults /dev/sda2 /mnt/data
```

5. Corrupt postgres data

```shell
sudo mv /var/lib/postgresql/12/ /mnt/data
sudo systemctl start postgresql@12-main 
sudo systemctl status postgresql@12-main
--------------------------------------
Error: /var/lib/postgresql/12/main is not accessible or does not exist
Can't open PID file /run/postgresql/12-main.pid (yet?) after start: Operation not permitted
```

#### Possible solutions

- Set the actual **data_directory** in `postgresql.conf`

```shell
data_directory = '/mnt/data/12/main'  
```

Before restart postgres service, we can see sure that the *CLI* argument **-D** is set correctly

```shell
     CGroup: /system.slice/system-postgresql.slice/postgresql@12-main.service
             ├─11643 /usr/lib/postgresql/12/bin/postgres -D /mnt/data/12/main 
```

- Rollback moving 😎

6. Check early created database

```shell
sudo -u postgres psql -c "select * from authors" -d hw2
```

| id  | name        | masterpiece             |
|-----|-------------|-------------------------|
| 1   | Rick Astley | Never Gonna Give You Up |
| 2   | Smash Mouth | All Star                |

---

## <a name="extended"></a> Ex*

1. Install [nfs](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nfs-mount-on-ubuntu-20-04-ru) on
   hosts

```shell
ansible-playbook -i hosts.ini -i cred.ini nfs.yml
```

2. Check postgres data on [slave](#slave)

```shell
sudo -u postgres psql -c 'select datname from pg_database;'
  datname  
-----------
 postgres
 template1
 template0
```

seems default

3. Setup nfs `/etc/exports` on [master](#master)

```shell
/mnt/data 172.23.169.20(rw,sync,no_subtree_check)
```

- run

```shell
sudo ufw allow 111
sudo ufw allow 2049
sudo exportfs -a
```

- mount exported dir on [slave](#slave)

```shell
sudo mount 172.23.169.19:/mnt/data /mnt/
```

`postgresql.conf`

```shell
data_directory = '/mnt/12/main' 
```

- finally restart postgres service

```shell
sudo systemctl restart postgresql
```

4. Check this out

```shell
sudo -u postgres psql -c 'select datname from pg_database;'
  datname  
-----------
 postgres
 hw1
 template1
 template0
 hw2
 ```

Insert something on [master](#master)

```shell
psql -h 172.23.169.19 -b hw1 -U postgres << EOF
insert into authors(name, masterpiece)
values ('Bag Raiders', 'Shooting Stars');
EOF
```

and check data on [slave](#slave)

```shell
psql -c 'select * from authors ;' -d hw2 -h 172.23.169.20 -U postgres 
```

| id  | name        | masterpiece             |
|-----|-------------|-------------------------|
| 1   | Rick Astley | Never Gonna Give You Up |
| 2   | Smash Mouth | All Star                |
| 3   | Bag Raiders | Shooting Stars          |

\\( ﾟヮﾟ)/

### But 🙃

If we insert anything on the [slave](#slave), we may corrupt some data and we have to
- **restart** both clusters
- or mark exported nfs `/mnt/data` on [master](#master) as *ro*

```shell
hw2=# insert into authors(name, masterpiece)
values ('Undertale', 'Megalovania');
WARNING:  terminating connection because of crash of another server process
DETAIL:  The postmaster has commanded this server process to roll back the current transaction and exit, because another server process exited abnormally and possibly corrupted shared memory.
HINT:  In a moment you should be able to reconnect to the database and repeat your command.
server closed the connection unexpectedly
        This probably means the server terminated abnormally
        before or while processing the request.
The connection to the server was lost. Attempting reset: Failed.
```

| id     | name        | masterpiece             |
|--------|-------------|-------------------------|
| 1      | Rick Astley | Never Gonna Give You Up |
| 2      | Smash Mouth | All Star                |
| 3      | Bag Raiders | Shooting Stars          |
| **37** | Undertale   | Megalomania             |

---
