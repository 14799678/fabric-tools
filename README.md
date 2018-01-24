# fabric-tools
使用fabric提供一些日常的运维操作，会持续更新<br>

* [fabric 学习文档推荐](http://fabric-chs.readthedocs.io/zh_CN/chs/tutorial.html "fabric 文档推荐") 

* [packs路径 包存放说明](https://github.com/s57445560/fabric-tools/tree/master/packs/README.md)

## fabric 安装与基础配置
```linux
安装epel源
rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
yum安装fabric
yum install fabric -y
```
##### `settings.py` 是配置文件

		# jdk安装的位置
		JDK_INSTALL_PATH = '/opt/'
		
		# zabbix_server 地址
		ZABBIX_SERVER_IP = '192.168.6.199'
		
		# salt_master 地址
		SALT_MASTER_IP = '192.168.6.199'

##### `ip.conf` 是需要登录的服务器文件

		ip地址        密码   主机名(如果需要修改主机名可以配置此列)
		192.168.6.125 123456 test002

		使用空格分开

##### 任务运行

		fab -f running.py host_init
		-f 是指定那个是主文件
##### 并发执行
		fab -f running.py -P sun
		-P 是并发

---

## 目前已有任务查看

```linux
[root@localhost fabric-tools]# fab -f running.py --list
Available commands:

    host_init
    hostname
    jdk
    salt
    ssh_trust
    zabbix
[root@localhost fabric-tools]# 
```

### host_init
服务器的 `初始化` 初始化脚本在`script/init.sh`,有需要调整的项目可以更改次脚本。<br>


### hostname
修改服务器主机名，需要ip.conf最后一列内有主机名。修改时会在/etc/hosts内写上本次设置的所有ip与hostname对应。<br>

### jdk
jdk安装 需要在 packs 目录内有 jdk 的 tar.gz压缩包<br>

### salt
批量安装salt minion 前提需要把所有依赖包下载到本地并且命名为 minion.tar.gz 放到 packs目录内。<br>

### ssh_trust
批量添加 ssh主机信任，需要在ip.conf内设置好做信任的所有主机，执行任务时会提示与那一台做信任。<br>

### zabbix
zabbix的agent安装，需要在 packs目录内放入 tar.gz的 zabbix安装包。<br>
