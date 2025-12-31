import os
import pickle
import open3d as o3d
import numpy as np
from PIL import Image
import random


def projection(pcd, save_name, rotation_angle=(0, 0, 0), img_size=[512, 512]):
    rotation_matirx = o3d.geometry.get_rotation_matrix_from_xyz(rotation_angle)  # （横，竖，里）
    pcd = pcd.rotate(rotation_matirx, pcd.get_center())

    points, colors = np.array(pcd.points), np.array(pcd.colors) * 255
    min_val, max_val = pcd.get_min_bound(), pcd.get_max_bound()

    rows, cols = img_size[0] - 1, img_size[1] - 1
    img = np.ones(([img_size[0], img_size[1], 3]), dtype=np.uint8) * 255
    depth = np.zeros((img_size[0], img_size[1]), np.float32)
    depth[:] = -np.inf
    correspondence = [[[] for _ in range(img_size[1])] for _ in range(img_size[0])]

    dx_dy = (max_val[:2] - min_val[:2]) / np.array([cols, rows])
    dxy = dx_dy.max()
    object_cols_rows = np.floor((max_val[:2] - min_val[:2]) / dxy)
    offset_col, offset_row = np.floor((np.array([cols, rows]) - object_cols_rows) / 2).astype(np.int64)
    coor = np.floor((points - min_val) / dxy).astype(np.int64)

    for index in range(points.shape[0]):
        coor_col, coor_row, coor_depth = coor[index]
        coor_col, coor_row = offset_col + coor_col, rows - offset_row - coor_row

        if coor_depth >= depth[coor_row, coor_col]:
            if coor_depth > depth[coor_row, coor_col]:
                depth[coor_row, coor_col] = coor_depth
                img[coor_row, coor_col] = np.array(colors[index], dtype=np.uint8)
                correspondence[coor_row][coor_col] = []
            correspondence[coor_row][coor_col].append(index)

    # 保存投影图像
    Image.fromarray(img).save(save_name + '_c.png')

    # # 保存映射关系
    # with open(save_name + '.pkl', 'wb') as pkl_file:  # 读取使用'rb'
    #     pickle.dump(correspondence, pkl_file)

    # 保存深度图
    # min_depth, max_depth = depth[depth != -np.inf].min(), depth[depth != -np.inf].max()
    # depth[depth != -np.inf] = (depth[depth != -np.inf] - min_depth) / (max_depth - min_depth) * 250 + 5
    # depth = depth.astype(np.uint8)
    # Image.fromarray(depth).save(save_name + '_d.png')


if __name__ == '__main__':
    # 读取点云
    # --------------------------------------------- 随机视点 ----------------------------------------
    # root = './CPCQA/'
    # ply_dir = root + 'ply/ply10/'
    # img_root = root + 'img/'
    # print(ply_dir)
    # for name in os.listdir(ply_dir):
    #     pcd = o3d.io.read_point_cloud(ply_dir + name)
    #     img_dir = img_root + name[:-4] + '/'
    #     os.makedirs(img_dir, exist_ok=True)
    #     for _ in range(150):
    #         x, y = random.random() - 0.5, random.random()
    #         save_name = img_dir + name[:-4] + '_' + str(_).rjust(3, '0')
    #         projection(pcd, save_name, (x * np.pi, y * 2 * np.pi, 0), img_size=(480, 480))
    # --------------------------------------------- 固定视点 ----------------------------------------
    # root = './WPC2/'
    # ply_dir = root + 'ply/ply4/'
    # img_root = root + 'img_fixed/'
    # ply_dir = 'F:/Project/jnd/jnd/data/'
    # img_root = 'F:/Project/jnd/jnd/pic/'

    ply_dir = 'I:/1-data-180/'
    img_root = 'I:/pic/'

    print(ply_dir)
    for name in os.listdir(ply_dir):
        pcd = o3d.io.read_point_cloud(ply_dir + name)
        img_dir = img_root + name[:-4] + '/'
        os.makedirs(img_dir, exist_ok=True)
        for index in range(4):
            y = 1 / 4 * index
            save_name = img_dir + name[:-4] + '_' + str(index).rjust(3, '0')
            projection(pcd, save_name, (0, y * 2 * np.pi, 0), img_size=(480, 480))
