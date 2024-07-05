import os
import torch
from model.HRposeFuseNetNewUnweighted_v2 import get_pose_net


# exec('from model.{} import get_pose_net'.format(opts.model))

def initialize_model(model_configs):
    mod_src = ["depth", "psm"]
    fuse_model_path = 'D:\IIT\/academic\Final_project\code\infant_pose_application_backend\model'

    model_type = model_configs["model_type"]

    if model_type == "HRNet_fusion":
        fuse_stage = int(model_configs["fuse_stage"])
        fuse_type = model_configs["fuse_type"]
        best_model_name = model_configs["best_model_path"]
        model = get_pose_net(in_ch=2, out_ch=14, fuse_stage=fuse_stage, fuse_type=fuse_type, mod_src=mod_src)

        checkpoint_file = os.path.join(fuse_model_path, best_model_name)

        checkpoint = torch.load(checkpoint_file, map_location=torch.device('cpu'))

        model.load_state_dict(checkpoint['state_dict'])
        # model.cuda()

        model.eval()
        return model
