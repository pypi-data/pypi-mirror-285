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

class GAD7Q1(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I feel {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['nervous', 'anxious', 'on edge'],
            emo_neg=['calm', 'peaceful', 'relaxed'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD",
                      "Ordinal":1,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling nervous, anxious or on edge'
            },
            **kwargs
        )

class GAD7Q2(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I was {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['nervous', 'bothered', 'disturbed'],
            emo_neg=['peaceful','calm', 'relaxed'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"GAD7",
              "Factor":"GAD",
              "Ordinal":2,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Not being able to stop or control worrying'
            },
            **kwargs
        )

class GAD7Q3(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I felt {emotion} about different things.",
            template="It is {intensifier} correct.",
            emo_pos=['worryied', 'stressed', 'nervous'],
            emo_neg=['confident', 'tranquil'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD",
                      "Ordinal":3,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Worrying too much about different things'
            },
            **kwargs
        )

class GAD7Q4(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I've been having {emotion} relaxing.",
            template="It is {intensifier} correct.",
            emo_pos=['trouble', 'difficulty', ],
            emo_neg=['no problem', 'an easy time'],

            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD",
                      "Ordinal":4,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble relaxing'
            },
            **kwargs
        )

class GAD7Q5(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I felt {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['restless', 'agitated', 'nervous'],
            emo_neg=['calm', 'tranquil', 'relaxed'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD",
                      "Ordinal":5,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Being so restless that it is hard to sit still'
            },
            **kwargs
        )

class GAD7Q6(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I became {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['annoyed', 'irritated', 'frustrated', 'bothered'],
            emo_neg=['calm', 'tranquil', 'peaceful', 'relaxed'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD",
                      "Ordinal":6,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Becoming easily annoyed or irritable'
            },
            **kwargs
        )

class GAD7Q7(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I felt {emotion} about upcoming events.",
            template="It is {intensifier} correct.",
            emo_pos=['afraid', 'scared'],
            emo_neg=['calm', 'tranquil', 'relaxed'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD",
                      "Ordinal":7,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling afraid as if something awful might happen'
            },
            **kwargs
        )

gad2_qmnli = [GAD7Q1, GAD7Q2]
gad7_qmnli = [GAD7Q1, GAD7Q2, GAD7Q3, GAD7Q4, GAD7Q5, GAD7Q6, GAD7Q7]
gad_qmnli = gad7_qmnli