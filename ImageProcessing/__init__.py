import logging
import os
import config
import importlib
from PIL import Image
import shutil
from ADC_function import file_not_exist_or_empty

def face_crop_width(filename, width, height):
    # 新宽度是高度的2/3
    cropWidthHalf = int(height/3)
    try:
        locations_model = config.getInstance().face_locations_model().lower().split(',')
        locations_model = filter(lambda x: x, locations_model)
        for model in locations_model:
            center, top = face_center(filename, model)
            # 如果找到就跳出循环
            if center:
                cropLeft = center-cropWidthHalf
                cropRight = center+cropWidthHalf
                # 越界处理
                if cropLeft < 0:
                    cropLeft = 0
                    cropRight = cropWidthHalf*2
                elif cropRight > width:
                    cropLeft = width-cropWidthHalf*2
                    cropRight = width
                return (cropLeft, 0, cropRight, height)
    except:
        print('[-]Not found face!   ' + filename)
    # 默认靠右切
    return (width-cropWidthHalf*2, 0, width, height)


def face_crop_height(filename, width, height):
    cropHeight = int(width*3/2)
    try:
        locations_model = config.getInstance().face_locations_model().lower().split(',')
        locations_model = filter(lambda x: x, locations_model)
        for model in locations_model:
            center, top = face_center(filename, model)
            # 如果找到就跳出循环
            if top:
                # 头部靠上
                cropTop = top
                cropBottom = cropHeight + top
                if cropBottom > height:
                    cropTop = 0
                    cropBottom = cropHeight
                return (0, cropTop, width, cropBottom)
    except:
        print('[-]Not found face!   ' + filename)
    # 默认从顶部向下切割
    return (0, 0, width, cropHeight)


def cutImage(imagecut, path, fanart_path, poster_path):
    fullpath_fanart = os.path.join(path, fanart_path)
    fullpath_poster = os.path.join(path, poster_path)
    if config.getInstance().download_only_missing_images() and not file_not_exist_or_empty(fullpath_poster):
        return
    if imagecut == 1:  # 剪裁大封面
        try:
            img = Image.open(fullpath_fanart)
            width, height = img.size
            if width/height > 2/3:  # 如果宽度大于2
                # 以人像为中心切取
                img2 = img.crop(face_crop_width(fullpath_fanart, width, height))
            elif width/height < 2/3:  # 如果高度大于3
                # 从底部向上切割
                img2 = img.crop(face_crop_height(fullpath_fanart, width, height))
            else:  # 如果等于2/3
                img2 = img
            img2.save(fullpath_poster)
            print('[+]Image Cutted!     ' + fullpath_poster)
        except Exception as e:
            print(e)
            print('[-]Cover cut failed!')
    elif imagecut == 0:  # 复制封面
        shutil.copyfile(fullpath_fanart, fullpath_poster)
        print('[+]Image Copyed!     ' + fullpath_poster)


def face_center(filename, model):
    print('[+]Use model         ' + model)
    try:
        mod = importlib.import_module('.' + model, 'ImageProcessing')
        return mod.face_center(filename, model)
    except Exception as e:
        print('[-]Model found face  ' + filename)
        if config.getInstance().debug() == 1:
            logging.error(e)
        return (0, 0)

if __name__ == '__main__':
    cutImage(1,'H:\\test\\','12.jpg','test.jpg')
