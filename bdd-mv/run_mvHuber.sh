#!/bin/bash

## Settings specific to "mvHuber".
ALPHA_STRAT=("0")
BETA="0.9"
RISK_NAME="mvHuber"
STEP_SIZE=("0.1" "0.5" "1.0" "1.5" "2.0")

## Dataset name is passed to this script.
DATA="$1"

## Run the driver script for the prescribed settings.
for idx_s in "${!STEP_SIZE[@]}"
do
    for idx_r in "${!ALPHA_STRAT[@]}"
    do
	TASK="s${idx_s}r${idx_r}"
	python "learn_driver.py" --algo-ancillary="$ALGO_ANCILLARY" --algo-main="$ALGO_MAIN" --alpha="$BETA" --alpha-strat="${ALPHA_STRAT[idx_r]}" --batch-size="$BATCH_SIZE" --beta="$BETA" --data="$DATA" --entropy="$ENTROPY" --loss-base="$LOSS_BASE" --model="$MODEL" --noise-rate="$NOISE_RATE" --num-epochs="$NUM_EPOCHS" --num-trials="$NUM_TRIALS" --risk-name="$RISK_NAME" --save-dist="$SAVE_DIST" --step-size="${STEP_SIZE[idx_s]}" --task-name="$TASK"
    done
done
