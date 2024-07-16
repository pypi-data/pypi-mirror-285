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

class PHQ9Q1(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I had {emotion} in doing things.",
            template="It is {intensifier} correct.",
            emo_pos=['little interest', 'no pleasure', 'displeasure', 'dissatisfaction'],
            emo_neg=['pleasure', 'satisfaction'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":1,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Little interest or pleasure in doing things'
            },
            **kwargs
        )

class PHQ9Q2(_QMNLI):
    def __init__(self, **kwargs ):
        super().__init__(
            context="Over the last 2 weeks, I have been feeling {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['down', 'depressed', 'hopeless'],
            emo_neg=['happy', 'hopeful', 'cheerful'],          
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":2,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling down, depressed or hopeless'
            },
            **kwargs
        )

class PHQ9Q3(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I {intensifier} had trouble falling asleep.",
            template="This sentence is {emotion}.",
            emo_neg=['depressive', 'sad', 'gloom'],
            emo_pos=["benign", 'legitimate',],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":3,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble falling asleep, staying asleep, or sleeping too much'
            },
            **kwargs
        )

class PHQ9Q4(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I have been feeling {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['tired', 'drained', 'fatigued'],
            emo_neg=['energized', 'refreshed', 'lively'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":4,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling tired or having little energy'
            },
            **kwargs
        )

class PHQ9Q5(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I had {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['poor appetite', 'been overeating'],
            emo_neg=['healthy appetite', 'satisfying appetite'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":5,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Poor appetite or overeating'
            },
            **kwargs
        )

class PHQ9Q6(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I feel {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['I am a failure', 'I am a disappointment', 'I am underachieving', 'I let myself down', 'I let my family down'],
            emo_neg=['successful ', 'lucky', 'confident'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":6,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling bad about yourself - or that you’re a failure or have let yourself or your family down'
            },
            **kwargs
        )

class PHQ9Q7(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I {intensifier} had trouble concentrating.",
            template="This sentence is {emotion}.",
            emo_pos=["happy", 'joyful',],
            emo_neg=['depressive', 'sad', 'gloom'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":7,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble concentrating on things, such as reading the newspaper or watching television'
            },
            **kwargs
        )

class PHQ9Q8(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I move or speak {emotion}.",
            template="It is {intensifier} correct.",
            emo_pos=['fidgetly', 'slowly'],
            emo_neg=['normally', 'naturally'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":8,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Moving or speaking so slowly that other people could have noticed. Or, the opposite - being so fidgety or restless that you have been moving around a lot more than usual'
            },
            **kwargs
        )

class PHQ9Q9(_QMNLI):
    def __init__(self, **kwargs):
        super().__init__(
            context="Over the last 2 weeks, I have {emotion} thoughts.",
            template="It is {intensifier} correct.",
            emo_pos=['suicidal', 'self destructive', 'deadly'],
            emo_neg=['happy', 'hopeful', 'positive'],
            intensifiers=frequency_weights,
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ",
              "Ordinal":9,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Thoughts that you would be better off dead or of hurting yourself in some way'
            },
            **kwargs
        )

phq2_qmnli = [PHQ9Q1, PHQ9Q2]
phq9_qmnli = [PHQ9Q1, PHQ9Q2, PHQ9Q3, PHQ9Q4, PHQ9Q5, PHQ9Q6, PHQ9Q7, PHQ9Q8, PHQ9Q9]
phq_qmnli = phq9_qmnli