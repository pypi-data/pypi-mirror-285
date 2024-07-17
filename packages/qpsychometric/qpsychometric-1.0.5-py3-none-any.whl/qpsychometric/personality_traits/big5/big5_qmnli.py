from qlatent.qmnli.qmnli import _QMNLI, SCALE

frequency_weights:SCALE = {
    'never':-4,
    'very rarely':-3,
    'seldom':-2,
    'rarely':-2,
    'frequently':2,
    'often':2,
    'very frequently':3,
    'always':4,    
}

class BIG5Q1(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I {intensifier} {emotion} new experiences and trying new things.",
            template="It is correct.",
            emo_pos=['am open to', 'enjoy', 'like'],
            emo_neg=['avoid', 'reject', 'dislike'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":1,
              "Original":'I am open to new experiences and enjoy trying new things.'
            },
            **kwargs
        )

class BIG5Q2(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} {emotion}.",
            template="It is correct.",
            emo_pos=['inventive', 'imaginative', 'creative'],
            emo_neg=['lacking imagination', 'boring'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":2,
              "Original":'I am imaginative and have a rich inner life.'
            },
            **kwargs
        )

class BIG5Q3(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I {intensifier} {emotion} new experiences.",
            template="It is correct.", 
            emo_pos=['seek out', 'look for', 'want to have'],
            emo_neg=['decline', 'dislike', 'give up on'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":3,
              "Original":'I am adventurous and seek out new experiences.'
            },
            **kwargs
        )

class BIG5Q4(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I {intensifier} {emotion} the details.",
            template="It is correct.",
            emo_pos=['closely inspect', 'pay attention to', 'am thorough in'],
            emo_neg=['overlook', 'miss out on', 'tend to neglect'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":4,
            "Original":'I am thorough and pay attention to detail.'
            },
            **kwargs
        )

class BIG5Q5(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} {emotion}.",
            template="It is correct.",
            emo_pos=['responsible', 'dependable', 'trustworthy'],
            emo_neg=['unreliable', 'reckless', 'unaccountable'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":5,
            "Original":'I am responsible and dependable.'
            },
            **kwargs
        )

class BIG5Q6(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I {intensifier} like to be {emotion}.",
            template="It is correct.",
            emo_pos=['organized', 'arranged'],
            emo_neg=['messy', 'disordered'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":6,
            "Original":'I am organized and like to keep things tidy.'
            },
            **kwargs
        )

class BIG5Q7(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} {emotion} around other people.",
            template="It is correct.",
            emo_pos=['talkative', 'chatty', 'amiable'],
            emo_neg=['quiet', 'silent', 'withdrawn', 'shy'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":7,
            "Original":'I am talkative and enjoy being around others.'
            },
            **kwargs
        )

class BIG5Q8(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} {emotion}.",
            template="It is correct.",
            emo_pos=['sociable', 'in the center of attention'],
            emo_neg=['quiet', 'reserved', 'shy'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":8,
            "Original":'I am outgoing and enjoy being the center of attention.'
            },
            **kwargs
        )

class BIG5Q9(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} {emotion}.",
            template="It is correct.",
            emo_pos=['sociable', 'friendly', 'approachable'],
            emo_neg=['distant','unfriendly', 'unsociable'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":9,
            "Original":'I am sociable and make friends easily.'
            },
            **kwargs
        )

class BIG5Q10(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} {emotion} other people's feelings.",
            template="It is correct.",
            emo_pos=['considerate towards', 'respectful towards', 'care about'],
            emo_neg=['indifferent towards', 'emotionally distant towards', 'insensitive towards'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":10,
            "Original":"I am considerate and care about other people's feelings."
            },
            **kwargs
        )

class BIG5Q11(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} {emotion} towards others.",
            template="It is correct.",
            emo_pos=['compassionate', 'empathetic', 'sympathetic'],
            emo_neg=['indifferent', 'careless', 'apathetic'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":11,
            "Original":"I am compassionate and empathetic towards others."
            },
            **kwargs
        )

class BIG5Q12(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I {intensifier} {emotion} with others.",
            template="It is correct.",
            emo_pos=['cooperate', 'work well', 'helpful'],
            emo_neg=['disobliging', 'unsupportive'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":12,
            "Original":"I am cooperative and work well with others."
            },
            **kwargs
        )

class BIG5Q13(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} easily {emotion} about things.",
            template="It is correct.",
            emo_pos=['stressed', 'worry', 'concern'],
            emo_neg=['calmed', 'collected', 'composed'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Neuroticism",
              "Ordinal":13,
            "Original":"I am easily stressed and worry about things."
            },
            **kwargs
        )

class BIG5Q14(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="I am {intensifier} easily {emotion}.",
            template="It is correct.",
            emo_pos=['upset', 'prone to mood swings', 'agitated'],
            emo_neg=['calmed', 'relaxed'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Neuroticism",
              "Ordinal":14,
            "Original":"I am easily upset and prone to mood swings."
            },
            **kwargs
        )

big5_qmnli = [BIG5Q1, BIG5Q2, BIG5Q3, BIG5Q4, BIG5Q5, BIG5Q6, BIG5Q7, BIG5Q8, BIG5Q9, BIG5Q10, BIG5Q11, BIG5Q12, BIG5Q13, BIG5Q14]