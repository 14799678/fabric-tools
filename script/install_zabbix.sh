#!/bin/bash
yum install gcc -y

cd zabbix*
./configure --sysconfdir=/etc/zabbix --enable-agent
make && make install
cp misc/init.d/tru64/zabbix_agentd /etc/init.d/
chmod +x /etc/init.d/zabbix_agentd
groupadd zabbix
useradd zabbix -g zabbix
sed -i 's/\(PIDFILE=\).*/\1\/var\/log\/zabbix\/zabbix_agentd.pid/g' /etc/init.d/zabbix_agentd
mkdir /var/log/zabbix
chown -R zabbix: /var/log/zabbix/
>/etc/zabbix/zabbix_agentd.conf
ip=`ifconfig|grep -Po '(?<=inet addr:)[\d.]+'|head -1`
cat >>/etc/zabbix/zabbix_agentd.conf<<EOF
LogFile=/var/log/zabbix/zabbix_agent.log
PidFile=/var/log/zabbix/zabbix_agentd.pid
Server=ZABBIX_SERVER_IP
ServerActive=ZABBIX_SERVER_IP
Hostname=gj_$ip
Timeout=30
UnsafeUserParameters=1
Include=/etc/zabbix/zabbix_agentd.conf.d/
HostMetadataItem=system.uname
UserParameter=hardware,bash /etc/zabbix/script/hardware.sh
EOF

mkdir /etc/zabbix/script/
chmod 755 -R /etc/zabbix/script/
chown zabbix.zabbix -R /etc/zabbix/script
/etc/init.d/zabbix_agentd start
echo "/etc/init.d/zabbix_agentd start" >>/etc/rc.local

ps -ef|grep zabbix
