#!/usr/bin/python
# -*- coding: utf-8 -*-

from fabric.api import *
import os
import sys
import re
import settings



JDK_INSTALL_PATH = getattr(settings,"JDK_INSTALL_PATH","/opt/")
ZABBIX_SERVER_IP = getattr(settings,"ZABBIX_SERVER_IP","default")
SALT_MASTER_IP = getattr(settings,"SALT_MASTER_IP","default")

list_user_ip = []
list_ip = []
ip_dict = {}
host_dict = {}


fabric_path = os.getcwd()

env.warn_only = True

# 读取ip.conf 文件 来设置env.hosts 和env.passwords
with open('ip.conf') as f:
    for line in f.readlines():
        if line.rstrip() == '':
            continue
        list_line = line.rstrip().split()
        ip = list_line[0]
        if len(list_line) == 3:
            host = list_line[2]
            host_dict[ip] = host
        passwd = list_line[1]
        ip_dict['root@' + ip + ':22'] = passwd
        ssh_ip = 'root@' + ip
        list_user_ip.append(ssh_ip)
        list_ip.append(ip)

env.hosts = list_user_ip
env.user = 'root'
env.passwords = ip_dict


# 测试链接使用
@task
def test():
    run("ifconfig")


# 修改服务器hostname，并且把ip.conf列表内的ip与主机名对应关系写到 /etc/hosts。
@task
def hostname():
    if len(list_user_ip) != len(host_dict):
       abort("edit ip.conf add hostname") 
    run("sed -i 's/\(HOSTNAME=\).*/\\1%s/g' /etc/sysconfig/network"
        % host_dict[env.host])
    for (ip, hostname) in host_dict.items():
        run("egrep '\\b{ip}\\b' /etc/hosts >/dev/null&&sed -i 's/\({ip}\\b\).*/\\1 {hostname}/g' /etc/hosts||echo '{ip} {hostname}' >>/etc/hosts".format(ip=ip,
            hostname=hostname))
    run('hostname {name}'.format(name=host_dict[env.host]))



# jdk安装，在packs目录下放tar.gz结尾的安装包,(jdk-7u67-linux-x64.tar.gz, jdk-8u131-linux-x64.tar.gz),如果packs目录下有多个jdk包，则安装第一个
@task
def jdk():
    re_status = False
    jdk_re = re.compile(r"^jdk.*\.tar.gz")
    jdk_num_re = re.compile("(?<=u)[0-9]+")
    dir_list = os.listdir("./packs/")
    for pack in dir_list:
        jdk_result = jdk_re.search(pack)
        if jdk_result:
            jdk_name = jdk_result.group()
            jdk_num = jdk_num_re.search(jdk_name).group()
            re_status = True
            break
    if not re_status:
        abort("The JDK(jdk-?u?.?.tar.gz) package was not found in the packs directory")
    result = run("if [ -d {path} ];then echo '{path} dir exists!';fi".format(path=os.path.join(JDK_INSTALL_PATH,"jdk")))
    if result:
        return "jdk exists"
    run("mkdir -p {path}".format(path=JDK_INSTALL_PATH))
    put('packs/{jdk_pack}'.format(jdk_pack=jdk_name), '/tmp/')
    run("tar -zxf /tmp/{jdk_pack} -C {path}||echo 'tar jdk fail!'".format(jdk_pack=jdk_name, path=JDK_INSTALL_PATH))
    run('mv {old_path} {new_path}'.format(old_path=os.path.join(JDK_INSTALL_PATH,"jdk*%s"%jdk_num),new_path=os.path.join(JDK_INSTALL_PATH,"jdk")))
    run('echo "export JAVA_HOME={path}" >> /etc/profile'.format(path=os.path.join(JDK_INSTALL_PATH,"jdk")))
    run('echo "export CLASSPATH=$CLASSPATH:$JAVA_HOME/lib/*.jar" >> /etc/profile')
    run('echo "export PATH=$JAVA_HOME/bin:$PATH" >> /etc/profile')
    run('mkdir -p /usr/java')
    run('ln -s /opt/jdk/ /usr/java/default')



# 主机的初始化操作，如果觉得初始化不够完善请修改 script/init.sh 脚本
@task
@parallel(pool_size=3)
def host_init():
    put("script/init.sh","/tmp")
    run("bash /tmp/init.sh") 



# 安装 zabbix_agent 端，需要在packs目录下放入zabbix.?.?.tar.gz的安装包
@task
def zabbix():
    if ZABBIX_SERVER_IP == "default":
        abort("Please edit the ZABBIX_SERVER_IP variable of settings")
    re_status = False
    zabbix_re = re.compile(r"^zabbix.*\.tar.gz")
    dir_list = os.listdir("./packs/")
    for pack in dir_list:
        zabbix_result = zabbix_re.search(pack)
        if zabbix_result:
            zabbix_name = zabbix_result.group()
            re_status = True
            break
    if not re_status:
        abort("The ZABBIX(zabbix.?.?.tar.gz) package was not found in the packs directory")
    run('mkdir -p /tmp/zabbix_tmp_5560/')
    put('./packs/{zabbix}'.format(zabbix=zabbix_name),'/tmp/zabbix_tmp_5560/{zabbix}'.format(zabbix=zabbix_name))
    put('./script/install_zabbix.sh','/tmp/zabbix_tmp_5560/install_zabbix.sh')
    run('tar -zxf /tmp/zabbix_tmp_5560/{zabbix} -C /tmp/zabbix_tmp_5560'.format(zabbix=zabbix_name))
    run('sed -i "s/ZABBIX_SERVER_IP/{server_ip}/g" /tmp/zabbix_tmp_5560/install_zabbix.sh'.format(server_ip=ZABBIX_SERVER_IP))
    with cd('/tmp/zabbix_tmp_5560'):
        run('bash install_zabbix.sh')


# 安装salt_minion，此功能属于我个人使用，如果有需要的话请看 packs/README.md 里有用法
@task
def salt():
    if SALT_MASTER_IP == "default":
        abort("Please edit the SALT_MASTER_IP variable of settings")
    put('./packs/minion.tar.gz','/tmp/minion.tar.gz')
    with cd('/tmp'):
        run('tar -zxvf minion.tar.gz')
    with cd('/tmp/minion'):
        run('rpm -ivh * --force --nodeps')
    run('a=`cat /etc/sysconfig/network|grep -Po "(?<=HOSTNAME=).*"`;echo "id: $a">>/etc/salt/minion;echo "master: {salt_ip}">>/etc/salt/minion;chkconfig salt-minion on;service salt-minion start'.format(salt_ip=SALT_MASTER_IP))



# ssh信任，运行时需要指定与那个服务器做ssh信任。
@runs_once
def user_ssh_input():
    ssh_ip = prompt("Input and trust with that server [ip]: ",default=False)
    if not ssh_ip:
        abort("Need to fill in IP")
    if ssh_ip not in list_ip:
        abort("Fill in IP is not within ip.conf")
    return ssh_ip

@runs_once
def build_key():
    run("echo |ssh-keygen  -t rsa -P '' -f /root/.ssh/identity")
    return run('cat /root/.ssh/identity.pub')

@task
def ssh_trust():
    ssh_ip = user_ssh_input()
    result = execute(build_key,hosts="root@"+ssh_ip)
    run('echo "{data}" >> /root/.ssh/authorized_keys'.format(data=''.join(result.values())))



