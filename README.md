# CREDIT #
Credit goes to https://github.com/minimaxir/gpt-2-simple for the finetuning part
and to : \
https://twitter.com/theshawwn \
https://twitter.com/l4rz \
https://twitter.com/gwern \
for inspiration

# REPORTING #
## PURPOSE ##
Reporting system for finetuning monitoring, you can track multiple GPT-2 experiment at the same time with :
- Quantitative analytics (Loss for instance) and 
- Qualitativ analytics (Generated text for a giving step)

Example : http://www.watch-me-learn-to-talk.com/progress

## PRE-REQUISITES ##
Have a postgresql database
with the appropriate schema
see => monitoring/schema.sql
https://github.com/jqueguiner/polyglot/blob/master/monitoring/schema.sql
## BUILDING DOCKER FOR REPORTING SYSTEM ##
```
docker build -t gpt-2-monitoring -f docker.monitoring  .

```
## ADJUST API WRITE TOKEN ##
https://github.com/jqueguiner/polyglot/blob/master/monitoring/config.yml

## RUNNING THE MONITORING BACKEND ##
```
docker run -d -p 5000 gpt-2-monitoring

```
# FINETUNING ANY LANGUAGE WITH ANY MODEL #

## BUILDING DOCKER FOR FINETUNING GPT-2 ###
```
docker build -t gpt-2-simple -f docker.gpt-2-simple  .

```
## RUNNING FOR FINETUNING ##

```
nvidia-docker run -it -v /mnt/netapp/:/mnt/netapp/ \
-e REPORTING_CONFIG=/mnt/netapp/config.yml \
-e DATASET_SIZE=2M \
-e LANGUAGE=an \
-e MODEL=774M \
-e RUN_NAME=an_774M \
gpt-2-simple
```
This means train gpt-2 774M parameters for language "an" (Aragonese) in [OSCAR](https://traces1.inria.fr/oscar/) default dataset using only its 2 first MB of corpus.

The experiment will be using the config in /mnt/netapp/config.yml to report progress.

## Detailed Variables ##
What it means:

| variable         | default value                                    | settable at runtime | Runtime setting example                                                           | definition                                                                                                                                                                                                                                                    |
|------------------|--------------------------------------------------|---------------------|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| WORKSPACE        | /workspace                                       | Yes                 | nvidia-docker run -d -e WORKSPACE=/my_custom_workspace gpt-2-simple               | The WORKDIR instruction sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions that follow it in the Dockerfile. If the WORKDIR doesn’t exist, it will be created even if it’s not used in any subsequent Dockerfile instruction. |
| DATASET_URL      | https://traces1.inria.fr/oscar/files/Compressed/ | Yes                 | nvidia-docker run -d -e DATASET_URL=https://my_custom_url/corpus.txt gpt-2-simple |  URL of the corpus to train on, if empty the algorithm will train on raw file set by $DATASET When having a non empty DATASET_URL the DATASET will be manipulated and saved to the $DATASET file                                                              |
| LANGUAGE         | en                                               | Yes                 | nvidia-docker run -d -e LANGUAGE=en gpt-2-simple                                  | Language for the training                                                                                                                                                                                                                                     |
| DATASET_SIZE     | 10M                                              | Yes                 | nvidia-docker run -d -e DATASET_SIZE=10M gpt-2-simple                             | First 10M of file to be trained on                                                                                                                                                                                                                            |
| REPORTING_CONFIG | $WORKSPACE/config.yml                            | Yes                 | nvidia-docker run -d -e REPORTING_CONFIG=/workspace/config.yml gpt-2-simple       | Location of the config.yml file used for training reporting dashbaord, if set to null ("") it will disable the reporting                                                                                                                                      |
| RUN_NAME         | $LANGUAGE\_$MODEL_NAME                           | Yes                 | nvidia-docker run -d -e RUN_NAME=custom_run_name gpt-2-simple                     | Name for the run better to be unique for reporting                                                                                                                                                                                                            |
| CHECKPOINT_DIR   | $WORKSPACE/checkpoint                            | Yes                 | nvidia-docker run -d -e CHECKPOINT_DIR=/workspace/checkpoint gpt-2-simple         | Directory to store the checkpoints                                                                                                                                                                                                                            |
| MODEL_NAME       | 124M                                             | Yes                 | nvidia-docker run -d -e MODEL_NAME=345M gpt-2-simple                              | GPT-2 Model name to use can be 1 of the following values ['117M', '124M', '345M', '355M', '774M', '1558M']                                                                                                                                                             |
| MODEL_DIR        | $WORKSPACE/models                                | Yes                 | nvidia-docker run -d -e MODEL_DIR=/custom_model_dir_path gpt-2-simple             | Directory where to save or retreive GPT-2 models                                                                                                                                                                                                              |
| DATASET          | $WORKSPACE/dataset                               | Yes                 | nvidia-docker run -d -e DATASET=/custom_data_dir_file gpt-2-simple                | Path to the file to finetine / learn from                                                                                                                                                                                                                     |
| STEPS            | 5000                                             | Yes                 | nvidia-docker run -d -e STEPS=5000 gpt-2-simple                                   | Number of steps to finetune, -1 for infinite                                                                                                                                                                                                                  |
| RESTORE_FROM     | latest                                           | Yes                 | nvidia-docker run -d -e RESTORE_FROM=fresh gpt-2-simple                           | Will restore previous checkpoint from CHECJPOINT_DIR and finetune if lastest, else (fresh) will start from OpenAI pretrained models                                                                                                                           |
| SAVE_EVERY       | 1000                                             | Yes                 | nvidia-docker run -d -e SAVE_EVERY=2000 gpt-2-simple                              | Checkpoints will be saved every N steps                                                                                                                                                                                                                       |
| SAMPLE_EVERY     | 1000                                             | Yes                 | nvidia-docker run -d -e SAMPLE_EVERY=2000 gpt-2-simple                            | The finetuning will generate samples every N steps                                                                                                                                                                                                            |
| PRINT_EVERY      | 1000                                             | Yes                 | nvidia-docker run -d -e PRINT_EVERY=2000 gpt-2-simple                             | The finetuning will print samples every N steps                                                                                                                                                                                                               |
| OPTIMIZER        | adam                                             | Yes                 | nvidia-docker run -d -e OPTIMIZER=sgd gpt-2-simple                                | Define the Optimizer could be one of the following values [adam, sgd]                                                                                                                                                                                         |
| OVERWRITE        | false                                            | Yes                 | nvidia-docker run -d -e OVERWRITE=true gpt-2-simple                               | ill continue training and remove the previous iteration of the model without creating a duplicate copy                                                                                                                                                        |
| MULTI_GPU        | true                                             | Yes                 | nvidia-docker run -d -e MULTI_GPU=false gpt-2-simple                              | Finetuning on multi-gpu could be [true, false]                                                                                                                                                                                                                |
