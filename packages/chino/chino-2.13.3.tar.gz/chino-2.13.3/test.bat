@rem NOTE: you have to add customer_id, customer_key & url in the env variables
cd test
nosetests tests_chino.py --with-coverage --cover-html --cover-package=chino
cd ..
cscript PopupNotification.vbs
