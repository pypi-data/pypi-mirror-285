import os
import sys
sys.path.append('/home/jlb638/Desktop/package')
from src.experiment_helpers.training import train_unet
from PIL import Image
from accelerate import Accelerator
from diffusers import StableDiffusionPipeline
from diffusers.models import AutoencoderKL
import torch
from accelerate import Accelerator
from random import randint
from PIL import Image
from torchvision.transforms import PILToTensor
from transformers import CLIPImageProcessor, CLIPTextModel, CLIPTokenizer, CLIPVisionModelWithProjection
import torch.nn.functional as F
from tqdm.auto import tqdm
from peft import LoraConfig, get_peft_model


def basic_test(use_prior_preservation):
    accelerator=Accelerator(log_with="wandb",gradient_accumulation_steps=4)
    accelerator.init_trackers(project_name="testing_bullshit")
    pipeline=StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    pipeline("do this to instantiate things",num_inference_steps=1)
    pipeline.safety_checker=None
    img=Image.open("ArcaneJinx.jpg").convert("RGB").crop((0,0,64,64)).resize((512,512))
    for model in [pipeline.text_encoder, pipeline.vae,pipeline.unet]:
        model.eval()
        model.requires_grad_(False)
    config = LoraConfig(
            r=4,
            lora_alpha=16,
            target_modules=["to_k", "to_q", "to_v", "to_out.0"],
            lora_dropout=0.0,
            bias="none")
    pipeline.unet = get_peft_model(pipeline.unet, config)
    pipeline.unet.print_trainable_parameters()
    opt=torch.optim.AdamW(
        pipeline.unet.parameters(),
        lr=0.001
    )
    pipeline.unet.to(accelerator.device)
    #pipeline.scheduler.to(accelerator.device)
    opt,pipeline.unet=accelerator.prepare(opt,pipeline.unet)
    pipeline=train_unet(pipeline,5,[img for _ in range(5)],["{}" for _ in range(5)],
                            opt,use_prior_preservation,"girl",1,1.0,"jinx",accelerator,10,0.1)

if __name__=='__main__':
    basic_test(True)
    basic_test(False)