from stream_framework.verbs import register
from stream_framework.verbs.base import Verb


class PostVerb(Verb):
    id = 10
    infinitive = 'post'
    past_tense = 'posted'

class LikeVerb(Verb):
    id  = 11
    infinitive = 'like'
    past_tense = 'liked'

class ViewVerb(Verb):
    id  = 12
    infinitive = 'view'
    past_tense = 'viewed'

register(PostVerb)
register(LikeVerb)
register(ViewVerb)

