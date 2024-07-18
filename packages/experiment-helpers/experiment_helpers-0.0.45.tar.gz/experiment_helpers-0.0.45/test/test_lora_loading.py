import os
import sys
sys.path.append('/home/jlb638/Desktop/package')
from src.experiment_helpers.better_ddpo_pipeline import BetterDefaultDDPOStableDiffusionPipeline
from src.experiment_helpers.lora_loading import save_lora_weights, load_lora_weights,save_pipeline_hf,get_pipeline_from_hf

pipeline=BetterDefaultDDPOStableDiffusionPipeline(False,False,True,False,use_lora=True,
    pretrained_model_name="runwayml/stable-diffusion-v1-5")

pipeline("single step",num_inference_steps=1)

hub_model_id="jlbaker361/test-lora-loading"

save_pipeline_hf(pipeline,hub_model_id)
pipeline=get_pipeline_from_hf(hub_model_id,False,False,True,False,use_lora=True,
    pretrained_model_name="runwayml/stable-diffusion-v1-5")

pipeline("single step",num_inference_steps=1)