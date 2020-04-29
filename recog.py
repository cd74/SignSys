# coding: utf-8
import mxnet as mx
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
from detection.mxnet_mtcnn_face_detection.mtcnn_detector import MtcnnDetector
from recognition.sphereface_pytorch.matlab_cp2tform import get_similarity_transform_for_cv2
from recognition.sphereface_pytorch.dataset import ImageDataset
from recognition.sphereface_pytorch import net_sphere
from recognition.sphereface_pytorch.lfw_eval import alignment
import argparse
import cv2
import os
import time

torch.backends.cudnn.benchmark = True

user_path = './dataset/face/user/'
cache_path = './cache/'

detector = MtcnnDetector(model_folder='./detection/mxnet_mtcnn_face_detection/model', ctx=mx.cpu(
    0), num_worker=4, accurate_landmark=True)  # initialize face detector

net = net_sphere.sphere20a()
net.load_state_dict(torch.load(
    './recognition/sphereface_pytorch/sphere20a.pth'))
net#.cuda()
net.eval()
net.feature = True


def del_file(path):
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            del_file(path_file)


def crop_info(img, create_cache=False):
    # crop image (from cv2.imread, etc.) into cropped images of faces, colored pictures only
    result = detector.detect_face(img)
    if result is None:
        return None
    points = result[1]
    chips = detector.extract_image_chips(img, points, 144, 0.37)
    if create_cache:
        del_file(cache_path)
        for i, chip in enumerate(chips):
            cv2.imwrite(cache_path + 'chip_'+str(i)+'.png', chip)
    return chips


def get_landmarks(img):
    # get landmarks of cropped image
    result = detector.detect_face(img)
    if result is None:
        return None
    return result[1][0]


def get_landmarks(img):
    # get boxes of cropped image
    result = detector.detect_face(img)
    if result is None:
        return None
    return result[1][0]


def save_img(img, landmarks, name):
    # save image and info to ./dataset/face/user/
    dirname = user_path + name + '/'
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = dirname + name + '_' + str(time.time())+'.jpg'
    cv2.imwrite(filename, img)
    with open(user_path+name+'/' + name+'.txt', 'a') as file:
        file.write(filename + '\t' +
                   str(landmarks))#.strip('[').strip(']') + '\n')


def compare(img1, landmarks1, img2, landmarks2):
    img1 = alignment(img1, landmarks1)
    img2 = alignment(img2, landmarks2)
    cv2.imwrite('11.png',img1)
    cv2.imwrite('22.png',img2)
    imglist = [img1, cv2.flip(img1, 1), img2, cv2.flip(img2, 1)]
    for i in range(len(imglist)):
        imglist[i] = imglist[i].transpose(2, 0, 1).reshape((1, 3, 112, 96))
        imglist[i] = (imglist[i]-127.5)/128.0
    img = np.vstack(imglist)
    img = Variable(torch.from_numpy(img).float(), volatile=True)#.cuda()
    output = net(img)
    f = output.data
    f1, f2 = f[0], f[2]
    cosdistance = f1.dot(f2)/(f1.norm()*f2.norm()+1e-5)
    return cosdistance.item()
