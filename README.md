# HIVEProject
Built with
* MySQL version 5.7.32-0ubuntu0.18.04.1 (Ubuntu)
* Python 3.8.6
* Flask 1.1.2
* Flask-mysql 1.5.1

### DB
From the server, creating an user with
 ```
 CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
 ```
```
 GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' IDENTIFIED BY 'password';
```

To create the tables, use the **database.txt** file from HIVEPROJECT folder

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

 Then
```
$ export FLASK_APP=app.py
```

```
$ flask run
```

Finally
Open the link http://127.0.0.1:5000/





