import torch
from PIL import Image
from torchvision import transforms
from matplotlib import pyplot as plt
import cv2
import numpy as np 
import os
import pydicom

def segment(imagename, save_name, model, equalize=False, out_dicom=False):
    dicom = True
    try:
        pydicom.dcmread(imagename)
    except:
        dicom = False
    lungs_list, percentage_list = [],[]
    for i in range(2):
        if dicom:
            if os.path.isdir(imagename):ds = pydicom.dcmread(os.path.join(imagename, get_PA_image(imagename)))
            else:ds = pydicom.dcmread(imagename)
            pixel_spacings = ds.ImagerPixelSpacing # 0.16mm
            image_uint8 = ((ds.pixel_array/ds.pixel_array.max())*255).astype(np.uint8)
            # bg = np.mean([image_uint8[0,0] , image_uint8[-1,-1], image_uint8[-1,0], image_uint8[0,-1]])
            if i == 1: image_uint8 = 255 - image_uint8
            img = Image.fromarray(image_uint8).convert("L")
        else:
            img = Image.open(imagename).convert("L")
        # Code 
        Transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        orig_img = np.array(img)
        original_size = img.size
        if equalize:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            img = Image.fromarray(clahe.apply(np.array(img)))
        # img = cv2.resize(img, (256, 256), interpolation=cv2.INTER_CUBIC)
        img = Transform(img)
        img = img.unsqueeze(0)
        img = img.to(device)
        model.to(device)
        outputs = model(img).squeeze()
        pred = torch.sigmoid(outputs).detach().cpu().numpy()
        pred[pred < 0.5] = 0
        pred[pred > 0.5] = 1
        # print('before',lungs.shape)
        lungs = cv2.resize(pred, original_size, interpolation=cv2.INTER_NEAREST)
        lungs_list.append(lungs)
        # Check how much percentage is the lungs 
        percent = len(lungs[lungs == True])/len(lungs.ravel()) * 100
        percentage_list.append(percent)
        img.to('cpu') ; del img
        model.to('cpu'); 
    lungs = lungs_list[np.argmax(percentage_list)]
    if out_dicom:
        im = (lungs * 65535).astype(np.uint16)
        ds.PixelData = im.tobytes()
        ds.save_as(save_name)
    elif dicom:
        cv2.imwrite(save_name+'.jpg', (lungs * 255))
    else:
        cv2.imwrite(save_name, (lungs * 255))
    return 0