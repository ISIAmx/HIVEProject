# HIVEProject
Built with
* MySQL version 5.7.32-0ubuntu0.18.04.1 (Ubuntu)
* python 3.8.6
* flask 1.1.2
* flask-login 0.5.0
* flask-sqlalchemy 2.4.4

### DB
From the server, creating an user with
 ```
 CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
 ```
```
 GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' IDENTIFIED BY 'password';
```

### Web App
From the directory
 ```
 HIVEPROJECT/ 
 ```

Typing
  ```
 pipenv install
 ```
 ```
 pipenv shell 
 ```

 To create the tables, use
 ```
 $ python
 $ from app import db
 $ db.create_all()
 ```

 Then
```
$ export FLASK_APP=app.py
```

```
$ flask run
```

Finally
Open the link http://127.0.0.1:5000/





