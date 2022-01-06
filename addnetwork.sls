/opt/mistnet/etc/addnetwork:
  file.directory:
    - user: root
    - group: root
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True

/opt/mistnet/etc/addnetwork/utils:
  file.directory:
    - user: root
    - group: root
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True

flask_cors:
  pip.installed:
    - require:
      - pkg: python-pip

requests:
  pip.installed:
    - require:
      - pkg: python-pip

python-pip:
  pkg.installed

pymongo:
  pip.installed:
    - require:
      - pkg: python-pip

/opt/mistnet/etc/addnetwork/tmpfile.csv:
  file.managed:
    - source: salt://tmpfile.csv

/opt/mistnet/etc/addnetwork/addnetwork.py:
  file.managed:
    - source: salt://addnetwork.py

/opt/mistnet/etc/addnetwork/addnetwork.json:
  file.managed:
    - source: salt://addnetwork.json

/opt/mistnet/etc/addnetwork/utils/database.py:
  file.managed:
    - source: salt://database.py

/opt/mistnet/etc/addnetwork/utils/__init__.py:
  file.managed:
    - source: salt://__init__.py

/etc/systemd/system/addnetwork.service:
  file.managed:
    - source: salt://addnetwork.service

addnetwork.service:
  service.running:
    - enable: True
