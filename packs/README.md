# 放所需要的包
---

## jdk

放入 `tar.gz` 结尾的包(jdk-8u131-linux-x64.tar.gz).<br>

---

## zabbix-agent

放入 `tar.gz` 结尾的包(zabbix-3.4.4.tar.gz).<br>

---

## salt-minion

放入 `minion.tar.gz` 包.<br>
最好是在安装master的时候也把minion的所有依赖包都down到本地，这样可以保持版本一致.<br>
```linux
安装yum源
yum install -y --downloadonly --downloaddir=/root/minion salt-minion
cd /root
tar -zcvf minion.tar.gz minion/
```

