import os
import sys
sys.path.append('/home/jlb638/Desktop/package')
from src.experiment_helpers.better_ddpo_pipeline import BetterDefaultDDPOStableDiffusionPipeline
from src.experiment_helpers.better_ddpo_trainer import BetterDDPOTrainer
from trl import DDPOConfig

pipeline=BetterDefaultDDPOStableDiffusionPipeline(
    False,
    False,
    True,
    False,
    use_lora=True,
    pretrained_model_name="runwayml/stable-diffusion-v1-5"
)

def image_samples_hook(prompt_image_data, global_step, tracker):
    return

def prompt_fn():
    return " prompt ",{}

config=DDPOConfig(
    train_learning_rate=0.001,
    num_epochs=1,
    train_gradient_accumulation_steps=2,
    sample_num_steps=2,
    sample_batch_size=2,
    train_batch_size=2,
    sample_num_batches_per_epoch=8,
    mixed_precision="no",
    tracker_project_name="ddpo-test-exp-helpers",
    log_with="wandb",
    accelerator_kwargs={
        #"project_dir":args.output_dir
    },
    #project_kwargs=project_kwargs
)

def reward_fn(images, prompts, epoch,prompt_metadata):
    return [1.0 for _ in images],{}
trainer = BetterDDPOTrainer(
    config,
    reward_fn,
    prompt_fn,
    pipeline,
    image_samples_hook
)

trainer.train()

