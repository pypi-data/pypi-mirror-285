import os
import sys
sys.path.append('/home/jlb638/Desktop/package')
from src.experiment_helpers.measuring import print_tables


run_id_dict={
        "Vanilla":["173w2r1q","mwhnxtpb"],
        #"Vanilla_Negative":["co78j4ak","ykumm85l"],
        "Vanilla_Spare":["peyzw3oa","07n5xoqb"],
        "T5_Transformer":["3zl9cz3a","g1trkmly","bza128pk","osadows9","3d9go23s","93f0ngw2"],
        #"T5_Transformer_Negative":["y42whkb3","njww0sxj"],
        "T5_Transformer_Spare":["8x7mwl5r","jfeq3nq6","3x2xbzuc","bq1224jb","8ba3jea3","letuoqqs"],
        "T5_Unet": ["yob4st69","qfm2nxy7"],
        #"T5_UNet_Negative":["4yegkplc","1571dfbf"],
        "T5_UNet_Spare":["7a3eacrp","0qetqpq0"],
        "Vanilla_Short":["gd0jkf6f","0j5a8ixd"], #this is the shit in the normal script
        "Vanilla_Short_Spare":["fjlumnap","rmebldhu"],
        "Llama_Unet":["vd003zab","pwugepr3","ru7wudup","bxr7owkj","wba5xtkj","ecgcazyt"],
        #"Llama_UNet_Negative":[],
        "Llama_Unet_Spare":["d4t21b4k","wmerq6if","bjqwvq40","enru9x0c","bmdlnj49","adeyybau"]
    }
key_list=["content_target_similarity", "content_consistency", "image_reward", "prompt_similarity"]

print_tables(run_id_dict,key_list,"personalization")