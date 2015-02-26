from feed_engine.models import StatusUpdate
from feed_engine.feedmanager import manager
from loremipsum import get_sentence
status = StatusUpdate()
status.text = get_sentence(start_with_lorem=False)
status.author = 'jomski2009'
status.save()
print status

manager.addactivity(status)





