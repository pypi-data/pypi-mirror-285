import os
import sys
sys.path.append('/home/jlb638/Desktop/package')
from src.experiment_helpers.wandb_utils import get_grouping_dict, make_tables

key_value_dict={
    "method":["t5_unet","vanilla","t5_transformer"],
    "lr":["0.08"],
    "scheduler":["DDPMScheduler"],
    "start":["2","5","10"],
    "epoch":["250"],
    "suffix":["_dumb","_multi","_negative"]
}

grouping_keys=["method","suffix"]

#/home/jlb638/Desktop/text/slurm/personalization_20_250_0.08_DDPMScheduler/vanilla_multi

format_string="/home/jlb638/Desktop/text/slurm/personalization_{start}_{epoch}_{lr}_{scheduler}/{method}{suffix}.err"

gd=get_grouping_dict("personalization",format_string,key_value_dict, grouping_keys)
for k,v in gd.items():
    print(k,v)

make_tables(gd, ["prompt_similarity","identity_consistency"],"personalization")

#slurm/oneshot_0_5_5_0.001_per_prompt/content_style_constant

format_string="/home/jlb638/Desktop/prompt/slurm/oneshot_{start}_{pretrain}_{train}_{lr}{suffix}/{method}.err"

key_value_dict={
    "method":["content","content_image"],
    "start":["4","0"],
    "pretrain":["5"],
    "train":["10"],
    "lr":["0.0001"],
    "suffix":[""]

}

grouping_keys=["method","suffix"]

gd=get_grouping_dict("one_shot",format_string,key_value_dict, grouping_keys)
for k,v in gd.items():
    print(k,v)

make_tables(gd, ["prompt_similarity","identity_consistency"],"one_shot")