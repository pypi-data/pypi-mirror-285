# qpsychometric

## Contains the following finalized questionnaires: ASI, BIG5, GAD, PHQ, SOC.

### Which questionnaires are available to run in each questionnaire's file?

* ASI:
  * asi_all_qmnli (all questions of ASI)
  * asi_bg_qmnli (questions from the B(G) category of ASI)
  * asi_bi_qmnli (questions from the B(I) category of ASI)
  * asi_bp_qmnli (questions from the B(P) category of ASI)
  * asi_h_qmnli (questions from the H category of ASI)
* BIG5:
  * big5_qmnli (all questions of BIG5)
* GAD:
  * gad2_qmnli (first 2 questions of GAD)
  * gad7_qmnli (all questions of GAD)
* PHQ:
  * phq2_qmnli (first 2 questions of PHQ)
  * phq7_qmnli (all questions of PHQ)
* SOC:
  * soc_qmnli (all questions of SOC)

### Structure of the qpsychometric library:
qpsychometric  
|-mental_health  
| |-generalized_anxiety_disorder (GAD)  
| |-patient_health_questionnaire (PHQ)  
| |-sense_of_coherence (SOC)  
|-personality_traits  
| |-big5 (BIG5)  
|-social_biases  
| |-ambivalent_sex_inventory (ASI)  

### Commands and steps for running a questionnaire:

* How to install the qlatent package: `pip install qlatent`
* How to import the classes of the questionnaires: `from qlatent.qmnli.qmnli import *`
* How to load an MNLI model from huggingface.com into a pipeline in 5 steps:
  * Import pytorch : `import torch` (Please ensure that you've downloaded it through the python terminal using this command : pip install torch)
  * Load your device for running the model: `device = 0 if torch.cuda.is_available() else -1` (0 is CUDA, -1 is CPU)
  * Choose an MNLI model path from huggingface.com: `p = "<huggingface_model_path>"` (replace <huggingface_model_path> with your actual path)
  * Load the MNLI model into a pipeline: `mnli = pipeline("zero-shot-classification",device=device, model=p)`
  * Set the model's identifier for the pipeline: `mnli.model_identifier = p`
* How to load a questionnaire: ?
* How to run a question from a questionnaire through an MNLI pipeline: ?
* How to run a report for a question's performance: ?
* How to run a full questionnaire: ?

### Run examples:
Load MNLI pipeline
```
p = "typeform/distilbert-base-uncased-mnli"
mnli = pipeline("zero-shot-classification",device=device, model=p)
mnli.model_identifier = p
```

Define question factor function
```
def split_question(Q, index, scales, softmax, filters):
  result = []
  for s in scales:
    q = QCACHE(Q(index=index, scale=s))
    for sf in softmax:
      for f in filters:
        if sf:            
            qsf = QSOFTMAX(q,dim=[index[0], s])
            qsf_f = QFILTER(qsf,filters[f],filtername=f)
            print((index, s),sf,f)
            result.append(qsf_f)
        else:
            qsf = QPASS(q,descupdate={'softmax':''})
            qsf_f = QFILTER(qsf,filters[f],filtername=f)
            print(s,sf,f)
            result.append(qsf_f)
  return result

```

Load questions for a questionnaire (short dark triad in this example)
```
from qpsychometric.personality_traits.short_dark_triad.sd3_qmnli import sd3_qmnli

for Q in tqdm(sd3_qmnli):
    Qs = split_question(Q,
                        index=Q.q_index,
                        scales=[Q.q_scale],
                        softmax=[True],
                        filters={'unfiltered':{},
                                "positiveonly":Q().get_filter_for_postive_keywords()
                                },
                        )
    print(Qs[0]._descriptor['Ordinal'])
    Qs[0].run(mnli).mean_score()
```

You can also load all available questions and run them. Here we load questions from files that ends with "_qmnli.py".
```
from qpsychometric.utils import load_questions

all_questions = load_questions(pattern='_qmnli.py')

for Q in tqdm(all_questions):
    Qs = split_question(Q,
                        index=Q.q_index,
                        scales=[Q.q_scale],
                        softmax=[True],
                        filters={'unfiltered':{},
                                "positiveonly":Q().get_filter_for_postive_keywords()
                                },
                        )
    print(Qs[0]._descriptor)
    Qs[0].run(mnli).mean_score()
```
?
