import os
import sys
sys.path.append('/home/jlb638/Desktop/package')
from src.experiment_helpers.unsafe_stable_diffusion_pipeline import UnsafeStableDiffusionPipeline

pipeline=UnsafeStableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipeline("genital",num_inference_steps=30).images[0].save("nsfw.png")