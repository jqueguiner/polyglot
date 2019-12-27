
source /opt/extract.sh

# DATASET_URL = "" will lead to local DATASET definition
if ! [[ -z "$DATASET_URL" ]]; then
	# special url binding for OSCAR dataset
	if [[ "$DATASET_URL" == "https://traces1.inria.fr/oscar/files/Compressed/" ]]; then
		dl_filename=${LANGUAGE}_dedup.txt.gz
		DATASET_URL=${DATASET_URL}${dl_filename}
	else
		dl_filename="${DATASET_URL##*/}"
	fi
	filename=$(echo "$dl_filename" | cut -f 1 -d '.')
    
    if [ ! -f "$filename" ]; then
      echo "$filename does not exist : pre-processing"
      wget -O $dl_filename $DATASET_URL
      extract $dl_filename
    else
      echo "$filename already exist : skipping pre-processing"    
    fi

    for f in $(ls | grep $filename); do
        export DATASET=$f
    done
fi


# GET the first DATASET_SIZE MB of DATASET
head -c $DATASET_SIZE $DATASET > ${DATASET}_preprocessed


available_models=$(gpt_2_simple list_models)


if [[ $available_models == *"$MODEL_NAME"* ]]; then

  if [[ -z "${RUN_NAME}" ]]; then
    export RUN_NAME=${LANGUAGE}_${MODEL_NAME}
  fi

  if [[ -z "${CHECKPOINT_DIR}" ]]; then
    export CHECKPOINT_DIR=$WORKSPACE/checkpoint/$RUN_NAME
  fi

  gpt_2_simple finetune \
            --run_name $RUN_NAME \
            --checkpoint_dir $CHECKPOINT_DIR \
            --model_name $MODEL_NAME \
            --model_dir $MODEL_DIR \
            --dataset ${DATASET}_preprocessed \
            --steps $STEPS \
            --restore_from $RESTORE_FROM \
            --sample_every $SAMPLE_EVERY \
            --print_every $PRINT_EVERY \
            --optimizer $OPTIMIZER \
            --overwrite $OVERWRITE \
            --multi_gpu $MULTI_GPU \
            --reporting_config $REPORTING_CONFIG
else
  echo "[ERROR] $MODEL_NAME is not part of available OpenAI GPT-2 models should be in list:"
  echo $available_models
fi


