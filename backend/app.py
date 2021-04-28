import pika
import mysql.connector
import hashlib
import logging
import os
import time

import mysql.connector
import pika
import pika.exceptions

logging.basicConfig(level=logging.INFO)

def process_request(ch, method, properties, body): 
    logging.info(str(body))
    str_body = str(body)
    email_start = str_body.find("email")+9
    email_end = str_body.find("hash")-4
    email = str_body[email_start:email_end]
    hash_start = str_body.find("hash")+8
    hash_end = str_body.find("}")-1
    user_hash = str_body[hash_start:hash_end] 
    logging.info(user_hash)
    action_start = str_body.find(":")+3
    action_end = str_body.find(",")-1
    action = str_body[action_start:action_end]
    channel.basic_ack(delivery_tag=method.delivery_tag)

    if action == "REGISTER":
        #store in db
        register_user(email, user_hash, mycursor)
        return_msg(action, channel)
    elif action == "GETHASH":
        #lookup in db
        login_user(email, user_hash, mycursor)
        return_msg(action, channel)
    else:
        logging.info(action)
        return_msg(action,channel)
    #logging.info(type(body["data"]))

def register_user(user_email, user_pass, cursor):
    #TODO: 1 Connect to DB 2 Create a new entry in the appropriate table 3 verify successful add
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",(user_email,user_pass))
    logging.info(cursor)

def login_user(user_email, user_pass, cursor):
    #TODO: 1 Connect to DB 2 Pull the hash based on username 3 compare the hashes, 4 return t/f
    cursor.execute("SELECT password FROM users WHERE username = %s")
    #need to copy the username from the stdout

def return_msg(action_string, msg_ch):
    if action_string == "REGISTER" and msg_ch.is_open:
        msg_body = 'REGISTER',{'success': True}
        try:
            msg_ch.basic_publish(exchange='request', body=msg_body, properties=pika.BasicProperties(delivery_mode=2, #messages are now persistant
            ))
        except pika.exceptions.UnroutableError as err :
            logging.info("UnroutableError error: {0}".format(err))
        except pika.exceptions.NackError as err :
            logging.info("NackError error: {0}".format(err))


# repeatedly try to connect to db and messaging, waiting up to 60s, doubling
# backoff

time.sleep(30)

cnx = mysql.connector.connect(user='test', password='test', host='db', database='Jhin')
logging.info(cnx.is_connected())

mycursor = cnx.cursor()
mycursor.execute("SHOW TABLES")
count = 0
for table in mycursor:
	if(table[0] == "users"):
		count += 1
if(count == 0):
    mycursor.execute("CREATE TABLE users (username VARCHAR(255), password VARCHAR(255))")
    mycursor.execute("INSERT INTO users (username, password) VALUES ('test', 'password')")
else:
	logging.info(print("Users table already created!"))

cnx.commit()
logging.info("Connecting to messaging service...")

credentials = pika.PlainCredentials(
    os.environ['RABBITMQ_DEFAULT_USER'],
    os.environ['RABBITMQ_DEFAULT_PASS']
)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
            host='messaging',
            credentials=credentials
        )
    )
     
channel = connection.channel()

# create the request queue if it doesn't exist
channel.queue_declare(queue='request', durable=True)
channel.exchange_declare(exchange="login_sys", exchange_type="direct")
channel.queue_bind(exchange="login_sys", queue="request")

channel.basic_consume(
    queue='request', auto_ack=True, on_message_callback=process_request, consumer_tag='backend hw')


# loops forever consuming from 'request' queue
logging.info("Starting consumption...")
channel.start_consuming()

#salt = os.random(32) Can be used to add a salt to the hashed password
#password = 'something'
#key = hashlib.pbkdf2_hmac(
#   'sha256', the algorithm you choose for hashing
#   password.encode('utf-8'), Convert the password to bytes
#   salt, provide the salt
#   100000 Recommended to use at least 100000 iterations of sha-256           
#)

cnx.close()
cnx.close()