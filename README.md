# dba

1. Install [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible-with-pip)
2. Create `cred.ini` in project root
```ini
[masters:vars]
ansible_sudo_pass={{SUDO_PASSWORD}}

[workers:vars]
ansible_sudo_pass={{SUDO_PASSWORD}}
```

3. Run
```shell
ansible-playbook -i hosts.ini -i cred.ini deps.yml 
```
