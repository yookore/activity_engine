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


register(PostVerb)
register(LikeVerb)

