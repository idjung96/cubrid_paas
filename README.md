# cubrid_paas

pip3 install virtualenv
virtualenv venv
pip install -r requirements.txt

$ wget https://kojipkgs.fedoraproject.org//packages/sqlite/3.8.11/1.fc21/x86_64/sqlite-devel-3.8.11-1.fc21.x86_64.rpm
$ wget https://kojipkgs.fedoraproject.org//packages/sqlite/3.8.11/1.fc21/x86_64/sqlite-3.8.11-1.fc21.x86_64.rpm
$ yum install sqlite-3.8.11-1.fc21.x86_64.rpm sqlite-devel-3.8.11-1.fc21.x86_64.rpm
$ sqlite3 –version 
3.8.11 2015-07-27 13:49:41 b8e92227a469de677a66da62e4361f099c0b79d0
$ python manage.py runserver 0.0.0.0:8000
