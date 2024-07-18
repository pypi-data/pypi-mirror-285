# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Function:
import traceback

import fastdeploy as fd
from pathlib import Path
from zhousflib.image import read


model_file = Path(r"D:\workspace\ZhousfLib\model\PPLCNet_x1_0_infer-v9\inference.pdmodel")
params_file = Path(r"D:\workspace\ZhousfLib\model\PPLCNet_x1_0_infer-v9\inference.pdiparams")
config_file = Path(r"D:\workspace\ZhousfLib\model\PPLCNet_x1_0_infer-v9\inference_cls.yaml")

runtime_option = fd.RuntimeOption()
# runtime_option.set_model_path(str(model_file), str(params_file))
# runtime_option.use_gpu(0)
# runtime_option.use_paddle_backend()
# # model = fd.vision.classification.PaddleClasModel(str(model_file), str(params_file), config_file=str(config_file),
# #                                                  runtime_option=runtime_option)
# model = fd.vision.classification.PaddleClasModel("", "", config_file=str(config_file),
#                                                  runtime_option=runtime_option)

with open(str(model_file), "rb") as model_buffer:
    with open(str(params_file), "rb") as params_buffer:
        runtime_option.set_model_buffer(model_buffer.read(), params_buffer.read())
        runtime_option.use_gpu(0)
        runtime_option.use_paddle_backend()
        model = fd.vision.classification.PaddleClasModel("", "", config_file=str(config_file), runtime_option=runtime_option)


# try:
#     with model_file.open("rb") as model_buffer, params_file.open("rb") as params_buffer:
#         runtime_option.set_model_buffer(model_buffer.read(), params_buffer.read())
#         runtime_option.use_gpu(0)
#         runtime_option.use_paddle_backend()
#         # runtime_option.use_paddle_infer_backend()
#         # Initialize model without model path and params path
#         model = fd.vision.classification.PaddleClasModel("", "", str(config_file), runtime_option=runtime_option)
#         # image_arr = read(Path(r"D:\workspace\ZhousfLib\model\PPLCNet_x1_0_infer-v9\test.png"))
#         # res = model.predict(image_arr)
#         # print(res)
# except Exception as e:
#     print(traceback.print_exc())

import os

# when key is not given, key will be automatically generated.
# otherwise, the file will be encrypted by specific key
# save_model = Path("__model__.encrypted")
# save_params = Path("__params__.encrypted")
# save_key = Path("encryption_key.txt")
# with model_file.open("rb") as model_buffer, params_file.open("rb") as params_buffer:
#     encrypted_model, key = fd.encryption.encrypt(model_buffer.read())
#     encrypted_params, key = fd.encryption.encrypt(params_buffer.read(), key)
#     with save_model.open("r") as f:
#         f.write(encrypted_model)

from fastdeploy import encryption

# import encrypt
#
# encrypted_model_dir = Path(r"D:\workspace\ZhousfLib\zhousflib\infer_framework\fast_infer")
# c = ("python {0} "
#      "--model_file {1}  "
#      "--params_file {2} "
#      "--encrypted_model_dir ResNet50_vd_infer_encrypt").format(encrypt.__file__, model_file, params_file, encrypted_model_dir)
#
# import os
# print(c)
# os.system(c)


