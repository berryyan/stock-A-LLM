# test_gpu.py
"""
测试 GPU 是否可用
"""

import torch

print("PyTorch 版本:", torch.__version__)
print("CUDA 是否可用:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("CUDA 版本:", torch.version.cuda)
    print("GPU 数量:", torch.cuda.device_count())
    print("当前 GPU:", torch.cuda.get_device_name(0))
    print("GPU 显存:", f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # 测试简单运算
    x = torch.rand(1000, 1000).cuda()
    y = torch.rand(1000, 1000).cuda()
    z = torch.mm(x, y)
    print("GPU 运算测试: ✅ 成功")
else:
    print("⚠️ CUDA 不可用，将使用 CPU")