export URL=$DATASET_URL$LANGUAGE\_dedup.txt.gz
wget -O $LANGUAGE.txt.gz $URL
unpigz $LANGUAGE.txt.gz
head -c $DATASET_SIZE $LANGUAGE.txt > $DATASET

gpt_2_simple finetune \
			--run_name $RUN_NAME \
			--checkpoint_dir $CHECKPOINT_DIR \
			--model_name $MODEL_NAME \
			--model_dir $MODEL_DIR \
			--dataset $DATASET \
			--steps $STEPS \
			--restore_from $RESTORE_FROM \
			--sample_every $SAMPLE_EVERY \
			--print_every $PRINT_EVERY \
			--optimizer $OPTIMIZER \
			--overwrite $OVERWRITE \
			--multi_gpu $MULTI_GPU \
			--reporting_config $REPORTING_CONFIG