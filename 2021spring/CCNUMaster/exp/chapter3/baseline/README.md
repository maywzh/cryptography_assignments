# Knowledge Tracing Models
## Pre-processed Dataset
* Download Link: https://bit.ly/2w7J3On
* Dataset format: log files are seperated by users. Once you download and unzip each tar.gz file, there's a folder `processed`, and there are 5 subdirectories named from `1` to `5` for cross validation. Each subdirectory has its own train/val/test separation, where test dataset is shared by all 5 separations. Separation ratio are given in the following table. 
For each user, `{user_id}.csv` contains two columns (with headers): tag(skill_id, or question_id, which is a single positive integer) and correctness (0 or 1). 

| Dataset          | Train:Val:Test | Link | 
|------------------|----------------|------|
| ASSISTments2009  |       56:14:30       | https://sites.google.com/site/assistmentsdata/home/assistment-2009-2010-data/skill-builder-data-2009-2010 |
| ASSISTments2015  |       56:14:30       | https://sites.google.com/site/assistmentsdata/home/2015-assistments-skill-builder-data |
| STATICS          |       56:14:30       | https://pslcdatashop.web.cmu.edu/Project?id=48 |

## Usage

```
python main.py --num_workers=8 --model=DKT --num_epochs=6 
--eval_steps=5000 --train_batch=2048 --test_batch=2048 --seq_size=200 
--input_dim=100 --hidden_dim=100 --name=ASSISTments2009_DKT_dim_100_100 
--dataset_name=2009 --cross_validation=1
```

Here are descriptions of arguments:

* `name`: name of the run. More precisely, the weight of the best model will be saved in the directory `weight/{ARGS.name}/`. 
* `gpu`: number(s) of gpu. 
* `device`: device. cpu, cuda, or others. 
* `base_path`: the path where datasets are located. 
* `num_workers`: number of workers for gpu training.
* `dataset_name`: the name of the benchmark dataset. Currently, ASSISTments2009, ASSISTments2015, ASSISTmentsChall, STATICS, Junyi, and EdNet-KT1 are available. 

* `model`: name of the model. DKT, DKVMN, or NPA. (SAKT is not available yet)
* `num_layers`: number of LSTM layers, for DKT and NPA. Set to be 1 as a default value. 
* `input_dim`: input embedding dimension of interactions, for DKT and NPA.
* `hidden_dim`: hidden dimension of LSTM models, for DKT and NPA.
* `key_dim`: dimension of key vectors of DKVMN.
* `value_dim`: dimension of value vectors of DKVMN.
* `summary_dim`: dimension of the last FC layer of DKVMN.
* `concept_num`: number of latent concepts, for DKVMN.
* `attention_dim`: dimension of the attention layer of NPA.
* `fc_dim`: largest dimension for the last FC layers of NPA.
* `dropout`: dropout rate of the model.

* `random_seed`: random seed for initialization, for reproducibility. Set to be 1 as default. 
* `num_epochs`: number of training epochs. 
* `eval_steps`: number of steps to evaluate trained model on validation set. The model weight with best performance will be saved. 
* `train_batch`: batch size while training.
* `test_batch`: batch size while testing.
* `lr`: learning rate. 
* `warmup_step`: warmup step for Noam optimizer. 
* `seq_size`: length of interaction sequence to be feeded into models. The sequence whose length is shorter than `seq_size` will be padded. 
* `cross_validation`: if `cross_validation` is 0, then the model is trained & tested only on the first dataset. If `cross_validation` is 1, then the model is trained & tested on all 5 splits, and give average results (with standard deviation). 

## Common features

* All models are trained with Noam optimizer. 
## DKT (Deep Knowledge Tracing)
* Paper: https://web.stanford.edu/~cpiech/bio/papers/deepKnowledgeTracing.pdf
* Model: RNN, LSTM (only LSTM is implemented)
* Performances: 

| Dataset          | ACC (%) | AUC (%) | Hyper Parameters |
|------------------|-----|-----|------------------|
| ASSISTments2009  | 76.99 ± 0.08 | 81.79 ± 0.09 | input_dim=100, hidden_dim=100 |

* All models are trained with batch size 2048 and sequence size 200. 

## DKVMN (Dynamic Key-Value Memory Network)
* Paper: http://papers.www2017.com.au.s3-website-ap-southeast-2.amazonaws.com/proceedings/p765.pdf
* Model: Extension of Memory-Augmented Neural Network (MANN)
* Performances: 

| Dataset          | ACC (%) | AUC (%) | Hyper Parameters |
|------------------|-----|-----|------------------|
| ASSISTments2009  |75.53 ± 0.19 | 79.58 ± 0.27 |key_dim = 50, value_dim = 200, summary_dim = 50, concept_num = 20, batch_size = 1024 |

* Due to memory issues, not all models are trained with batch size 2048.

## NPA (Neural Padagogical Agency)
* Paper: https://arxiv.org/abs/1906.10910
* Model: Bi-LSTM + Attention
* Performances: 

| Dataset          | ACC (%) | AUC (%) | Hyper Parameters |
|------------------|-----|-----|------------------|
| ASSISTments2009  | 77.09 ± 0.08 | 81.81 ± 0.13 |input_dim=100, hidden_dim=100, attention_dim=100, fc_dim=200 |

* All models are trained with batch size 2048 and sequence size 200. 

## SAKT (Self-Attentive Knowledge Tracing)
* Paper: https://files.eric.ed.gov/fulltext/ED599186.pdf
* Model: Transformer (1-layer, only encoder with subsequent mask)
* Performances: 

| Dataset          | ACC (%) | AUC (%) | Hyper Parameters |
|------------------|-----|-----|------------------|
| ASSISTments2009  | 76.37 ± 0.15 | 80.77 ± 0.09 |hidden_dim=100, seq_size=100, batch_size=512 |
