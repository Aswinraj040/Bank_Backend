You can run this application using two ways 

*Using Docker*

The project was built using python and danjgo , so in order to start the server it requires the following steps to be executed

1.)Start the Postgres Server and have a database called “credit_system” (Port 5432 , if there is change in port kindly change it in credit_system/settings.py)

2.)Start the reddis-server . Kindly install the reddis server as it is a message broker and task queue for Celery. Also it provides a fast and reliable way to manage the distribution of tasks between workers.

3.)If docker is not installed please install docker

4.)Make sure that no other program is using the 8000 port (If so then change the port in the compose.yaml file)

4.)Open the project in vs code or navigate to the project using terminal and type the following command

docker-compose up –build

5.)Then you can test out the api’s here are some examples

1.)Register
http://127.0.0.1:8000/register

Body

{
    "first_name" : "Aswin",
    "last_name" : "R",
    "age" : 20,
    "monthly_income" : 90000,
    "phone_number" : 9042046471
}

2.)check-eligibility
http://127.0.0.1:8000/check-eligibility

Body

{
    "customer_id" : 201,
    "loan_amount" : 300000,
    "interest_rate" : 20,
    "tenure" : 36
}

3.)create-loan

http://127.0.0.1:8000/create-loan

Body

{
    "customer_id" : 201,
    "loan_amount" : 300000,
    "interest_rate" : 20,
    "tenure" : 36
}

4.)view-loan

http://127.0.0.1:8000/view-loan/5930
5.)view-loans
http://127.0.0.1:8000/view-loans/101


*Without Using Docker*

Even without using docker you can run the application. Just open the project in any IDE (I have used pycharm). Follow these steps

1.)Start the Postgres Server and have a database called “credit_system” (Port 5432 , if there is change in port kindly change it in credit_system/settings.py)

2.)Start the reddis-server . Kindly install the reddis server as it is a message broker and task queue for Celery. Also it provides a fast and reliable way to manage the distribution of tasks between workers. You can start the reddis server by running the command in the cmd

reddis-server

3.)Start the Celery for the ingestion process using the below command

celery -A credit_system.celery worker --loglevel=INFO -P solo

4.)Then run the below code for data ingestion

python manage.py start_data_ingestion

5.)Then start the Django server by running the following code

python manage.py runserver











![image](https://github.com/user-attachments/assets/d1a6d809-14bc-486d-9538-2fdaddf7cadf)
