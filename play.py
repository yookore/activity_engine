# import time_uuid
#
# csv = open('/Users/jome/Desktop/statusupdates.csv', mode='r')
#
# for line in csv.readlines():
#     count = len(line.split(';'))
#     if count > 5:
#         print count


from cqlengine import connection, Model
from cqlengine import columns
import uuid
from cqlengine.management import sync_table
from loremipsum import get_sentence

conn = connection.setup(['192.168.10.200', '192.168.10.201'], 'yookore')

class Funny(Model):
    id = columns.Integer(primary_key=True)
    tt = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    reading = columns.Text()

sync_table(Funny)

# key = 10
#
# for i in range(100):
#     reading = "reading number {0}".format(i)
#     Funny.create(id=key, tt=uuid.uuid1(), reading=reading)

nextkey = None

moreItems = True
while moreItems:

    if nextkey is not None: #Meaning this is not the first iteration
        items = Funny.objects.filter(id=10).filter(tt__lt=nextkey).limit(10)
    else:
        items = Funny.objects.filter(id=10).limit(10)

    if items:
        nextkey = items[len(items) -1].tt
        print ('next key: ', nextkey)
        for item in items:
            print item.reading
    else:
        moreItems = False


