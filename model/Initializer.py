import os
import torch
from model.HRposeFuseNetNewUnweighted_v2 import get_pose_net


# exec('from model.{} import get_pose_net'.format(opts.model))

def initialize_model():
    mod_src = ["depth", "psm"]
    fuse_model_path = "D:\IIT\/academic\Final_project\code\infant_pose_application_backend\model"



    model = get_pose_net(in_ch=2, out_ch=14, fuse_stage=2, fuse_type="iAFF", mod_src=mod_src)

    checkpoint_file = os.path.join(fuse_model_path, 'model_best.pth')

    checkpoint = torch.load(checkpoint_file, map_location=torch.device('cpu'))

    model.load_state_dict(checkpoint['state_dict'])
    # model.cuda()

    model.eval()
    return model
