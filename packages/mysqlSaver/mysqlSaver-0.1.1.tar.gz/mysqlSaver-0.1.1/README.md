First of all , you must connect to your mysql database with this function :

```
from mysqlSaver.mysqlSaver import check_connection

your_connection = check_connection("your_host" , "your_port" , "your_username" , "your_password" , "your_databasename")
```

When you make connection to your owen database , you can use "your_connection" variable to use other function like this , for example :

```
from mysqlSaver.mysqlSaver import check_connection , sql_saver
import pandas as pd

your_connection = check_connection(host="localhost" , port=3306 , username="root" , password="test_password" , database="students")
df = pd.DataFrame({"name" : ['john'] , "lastname" : ["doe"] , 'age' : [19]})
sql_saver(df , "your_table" , your_connection)
```


In this function, at first, according to the create_table function, the table is created based on the type of each column in the dataframe .
You can use other functions such as partition and primarykey and etc. in the same way.
Good Luck .