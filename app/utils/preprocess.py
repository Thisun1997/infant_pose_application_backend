import io
import math
import random

import cv2
import numpy as np
import torch
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from torchvision import transforms

from config import Config

out_shp = (64, 64)
sz_pch = (256, 256)
SMaL_configs = {
    "numJoints": 14,
    "connectedJoints": np.array(
        [
            [0, 1],
            [1, 2],
            [3, 4],
            [4, 5],
            [6, 7],
            [7, 8],
            [9, 10],
            [10, 11],
            [8, 12],
            [9, 12],
            [12, 13]
        ]
    ),
    "headIndex": 13,
    "jointNames": (
        "R_Ankle",
        "R_Knee",
        "R_Hip",
        "L_Hip",
        "L_Knee",
        "L_Ankle",
        "R_Wrist",
        "R_Elbow",
        "R_Shoulder",
        "L_Shoulder",
        "L_Elbow",
        "L_Wrist",
        "Thorax",
        "Head"),
    "jointColours": [
        "blue",
        "blue",
        "blue",
        "red",
        "red",
        "red",
        "green",
        "green",
        "green",
        "blue",
        "blue",
        "blue",
        "red",
        "red",
    ],
    "gtjointColours": [
                          "yellow"
                      ] * 14,
    "predjointColours": ["blue"] * 14,
    "dct_clrMap": {  # the name of cv2 color map
        "depth": 'COLORMAP_BONE',
        'RGB': 'COLORMAP_BONE'
    },
    "flip_pairs": (
        ('R_Hip', 'L_Hip'), ('R_Knee', 'L_Knee'), ('R_Ankle', 'L_Ankle'),
        ('R_Shoulder', 'L_Shoulder'), ('R_Elbow', 'L_Elbow'), ('R_Wrist', 'L_Wrist')
    ),
    "skels_name": (
        # ('Pelvis', 'Thorax'),
        ('Thorax', 'Head'),
        ('Thorax', 'R_Shoulder'), ('R_Shoulder', 'R_Elbow'), ('R_Elbow', 'R_Wrist'),
        ('Thorax', 'L_Shoulder'), ('L_Shoulder', 'L_Elbow'), ('L_Elbow', 'L_Wrist'),
        # ('Pelvis', 'R_Hip'),
        ('R_Hip', 'R_Knee'), ('R_Knee', 'R_Ankle'),
        # ('Pelvis', 'L_Hip'),
        ('L_Hip', 'L_Knee'), ('L_Knee', 'L_Ankle'),
    )
}


def generate_patch_image(cvimg, bbox, do_flip, scale, rot, do_occlusion, input_shape=(256, 256)):
    # return skimage RGB,  h,w,c
    # flip first , then trans ( rot, scale,
    img = cvimg.copy()
    img_height, img_width, img_channels = img.shape  # h,w,c        # too many to unpack?

    # synthetic occlusion
    if do_occlusion:
        while True:
            area_min = 0.0
            area_max = 0.7
            synth_area = (random.random() * (area_max - area_min) + area_min) * bbox[2] * bbox[3]

            ratio_min = 0.3
            ratio_max = 1 / 0.3
            synth_ratio = (random.random() * (ratio_max - ratio_min) + ratio_min)

            synth_h = math.sqrt(synth_area * synth_ratio)
            synth_w = math.sqrt(synth_area / synth_ratio)
            synth_xmin = random.random() * (bbox[2] - synth_w - 1) + bbox[0]
            synth_ymin = random.random() * (bbox[3] - synth_h - 1) + bbox[1]

            if synth_xmin >= 0 and synth_ymin >= 0 and synth_xmin + synth_w < img_width and synth_ymin + synth_h < img_height:
                xmin = int(synth_xmin)
                ymin = int(synth_ymin)
                w = int(synth_w)
                h = int(synth_h)
                img[ymin:ymin + h, xmin:xmin + w, :] = np.random.rand(h, w, img_channels) * 255
                break

    bb_c_x = float(bbox[0] + 0.5 * bbox[2])
    bb_c_y = float(bbox[1] + 0.5 * bbox[3])
    bb_width = float(bbox[2])
    bb_height = float(bbox[3])

    if do_flip:
        img = img[:, ::-1, :]
        bb_c_x = img_width - bb_c_x - 1

    trans = gen_trans_from_patch_cv(bb_c_x, bb_c_y, bb_width, bb_height, input_shape[1], input_shape[0], scale, rot,
                                    inv=False)  # is bb aspect needed? yes, otherwise patch distorted
    img_patch = cv2.warpAffine(img, trans, (int(input_shape[1]), int(input_shape[0])),
                               flags=cv2.INTER_LINEAR)  # is there channel requirements
    # if len(img_patch.shape)==3:     #  I don't think it is needed as original is already single channel
    # 	img_patch = img_patch[:, :, ::-1].copy()

    img_patch = img_patch.copy().astype(np.float32)

    return img_patch, trans


def gen_trans_from_patch_cv(c_x, c_y, src_width, src_height, dst_width, dst_height, scale, rot, inv=False):
    # augment size with scale
    src_w = src_width * scale
    src_h = src_height * scale
    src_center = np.array([c_x, c_y], dtype=np.float32)

    # augment rotation
    rot_rad = np.pi * rot / 180
    src_downdir = rotate_2d(np.array([0, src_h * 0.5], dtype=np.float32), rot_rad)
    src_rightdir = rotate_2d(np.array([src_w * 0.5, 0], dtype=np.float32), rot_rad)

    dst_w = dst_width
    dst_h = dst_height
    dst_center = np.array([dst_w * 0.5, dst_h * 0.5], dtype=np.float32)
    dst_downdir = np.array([0, dst_h * 0.5], dtype=np.float32)
    dst_rightdir = np.array([dst_w * 0.5, 0], dtype=np.float32)

    src = np.zeros((3, 2), dtype=np.float32)
    src[0, :] = src_center
    src[1, :] = src_center + src_downdir
    src[2, :] = src_center + src_rightdir

    dst = np.zeros((3, 2), dtype=np.float32)
    dst[0, :] = dst_center
    dst[1, :] = dst_center + dst_downdir
    dst[2, :] = dst_center + dst_rightdir

    if inv:
        trans = cv2.getAffineTransform(np.float32(dst), np.float32(src))
    else:
        trans = cv2.getAffineTransform(np.float32(src), np.float32(dst))

    return trans


def rotate_2d(pt_2d, rot_rad):
    x = pt_2d[0]
    y = pt_2d[1]
    sn, cs = np.sin(rot_rad), np.cos(rot_rad)
    xx = x * cs - y * sn
    yy = x * sn + y * cs
    return np.array([xx, yy], dtype=np.float32)


def adj_bb(bb, rt_xy=1):
    '''
    according to ratio x, y, adjust the bb with respect ration (rt), keep longer dim unchanged.
    :param bb:
    :param rt_xy:
    :return:
    '''
    bb_n = bb.copy()
    w = bb[2]
    h = bb[3]
    c_x = bb[0] + w / 2.
    c_y = bb[1] + h / 2.
    aspect_ratio = rt_xy
    if w > aspect_ratio * h:
        h = w / aspect_ratio
    elif w < aspect_ratio * h:
        w = h * aspect_ratio
    bb_n[2] = w
    bb_n[3] = h
    bb_n[0] = c_x - w / 2.
    bb_n[1] = c_y - h / 2.

    return np.array(bb_n)


def display_input_images(pressure_image, depth_image):
    fig = Figure()
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.imshow(pressure_image)
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.imshow(depth_image)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def preprocess(depth_image, psm_image):
    input_image_stacked = np.stack([depth_image, psm_image], axis=2)
    input_image_exp = np.expand_dims(input_image_stacked, axis=0)
    input_image_exp[:, :, :, 0] = np.clip(input_image_exp[:, :, :, 0], 400, 800)
    mean = np.load(Config.base_path + "config/input_configs/mean.npy")
    std = np.load(Config.base_path + "config/input_configs/std.npy")
    img = input_image_exp[0, :, :, :]
    img_resized = cv2.resize(img, dsize=(256, 256), interpolation=cv2.INTER_CUBIC)
    img_height, img_width, img_channel = img_resized.shape
    bb = [0, 0, img_width, img_height]  # full image bb , make square bb
    bb = adj_bb(bb, rt_xy=1)
    scale, rot, do_flip, color_scale, do_occlusion = 1.0, 0.0, False, [1.0, 1.0, 1.0], False
    img_patch, trans = generate_patch_image(img_resized, bb, do_flip, scale, rot, do_occlusion, input_shape=(256, 256))
    img_channels = img_patch.shape[2]
    for i in range(img_channels):
        img_patch[:, :, i] = img_patch[:, :, i] * color_scale[i]
    trans_tch = transforms.Compose([transforms.ToTensor(),
                                    transforms.Normalize(mean=mean, std=std)]
                                   )
    pch_tch = trans_tch(img_patch)[None, :, :, :]
    return pch_tch, img_patch


def display_output(pred, img_patch):
    outputs = pred["output"]

    if isinstance(outputs, list):
        output = outputs[-1]
    else:
        output = outputs

    pred_hm, _ = get_max_preds(output.cpu().detach().numpy())
    pred2d_patch = np.ones((SMaL_configs["numJoints"], 3))  # 3rd for  vis
    pred2d_patch[:, :2] = pred_hm[0] / out_shp[0] * sz_pch[1]  # only firs

    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    plotImage(ax, img_patch[:, :, 0], 0)
    plot2DJoints(ax, pred2d_patch, SMaL_configs["connectedJoints"], SMaL_configs["gtjointColours"])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return output


def get_max_preds(batch_heatmaps):
    '''
	get predictions from score maps
	heatmaps: numpy.ndarray([batch_size, num_joints, height, width])
	:return preds [N x n_jt x 2]
	'''
    assert isinstance(batch_heatmaps, np.ndarray), \
        'batch_heatmaps should be numpy.ndarray'
    assert batch_heatmaps.ndim == 4, 'batch_images should be 4-ndim'

    batch_size = batch_heatmaps.shape[0]
    num_joints = batch_heatmaps.shape[1]
    width = batch_heatmaps.shape[3]
    heatmaps_reshaped = batch_heatmaps.reshape((batch_size, num_joints, -1))
    idx = np.argmax(heatmaps_reshaped, 2)
    maxvals = np.amax(heatmaps_reshaped, 2)  # amax, array max

    maxvals = maxvals.reshape((batch_size, num_joints, 1))
    idx = idx.reshape((batch_size, num_joints, 1))

    preds = np.tile(idx, (1, 1, 2)).astype(np.float32)

    preds[:, :, 0] = (preds[:, :, 0]) % width
    preds[:, :, 1] = np.floor((preds[:, :, 1]) / width)

    pred_mask = np.tile(np.greater(maxvals, 0.0), (1, 1, 2))
    pred_mask = pred_mask.astype(np.float32)  # clean up if too low confidence (maxvals)

    preds *= pred_mask
    return preds, maxvals


def plotImage(ax, image,c):
    if torch.is_tensor(image):
        image = image.permute(1, 2, 0)[:,:,c].cpu().numpy()
    image = np.array(image)
    ax.imshow(image)

def plot2DJoints(ax, joints2D, connectedJoints, jointColours, visJoints=None):
    # Plot skeleton
    for i in np.arange(len(connectedJoints)):
        joint1 = connectedJoints[i, 0]
        joint2 = connectedJoints[i, 1]
        if visJoints is None or (visJoints[joint1] == 1 and visJoints[joint2] == 1):
            x, y = [
                np.array(
                    [
                        joints2D[connectedJoints[i, 0], j],
                        joints2D[connectedJoints[i, 1], j],
                    ]
                )
                for j in range(2)
            ]
            ax.plot(x, y, lw=2, c=jointColours[i])

    # Plot joint coordiantes
    for i in range(len(joints2D)):
        scatterColour = "black" if visJoints is None or visJoints[i] == 1 else "orange"
        ax.scatter(joints2D[i, 0], joints2D[i, 1], c=scatterColour)
        # ax.text(
        #     joints2D[i, 0], joints2D[i, 1]-5, i)