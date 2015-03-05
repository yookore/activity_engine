from django.conf import settings
import pika
from pika.credentials import PlainCredentials
import jsonpickle

class PikaConsumer(object):

    def __init__(self):
        self.creds = PlainCredentials(username=settings.RABBIT_MQ_USERNAME, password=settings.RABBIT_MQ_PASSWORD)

    def callback(self, ch, method, properties, body):
        print body #Ideally this class should be external and part of the views module.

    def async_open(self):
        print "The conenction is open"

    def start(self):
        print self.creds
        print settings.RABBIT_MQ_HOST

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBIT_MQ_HOST, credentials=self.creds))
        #connection = pika.AsyncoreConnection(pika.ConnectionParameters(host=settings.RABBIT_MQ_HOST, credentials=self.creds))
        #channel = connection.channel(on_open_callback=self.async_open)
        channel = connection.channel()
        #channel.exchange_declare(exchange='all_subs', type='fanout')
        channel.queue_declare(queue="activities", durable=True)
        #result = channel.queue_declare(exclusive=True)
        #queue_name = result.queue()

        #channel.queue_bind(exchange='all_subs', queue=queue_name)

        channel.basic_consume(consumer_callback=self.callback, queue='activities')
        print "Starting consumer listener"
        channel.start_consuming()

        #pika.asyncore_loop()


