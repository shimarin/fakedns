# fakedns
Fake DNS that resolves A record using gethostbyname

```
cp fakedns.py /usr/sbin/
cp fakedns.service /etc/systemd/system/
systemctl start fakedns
```
