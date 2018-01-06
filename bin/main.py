import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# __file__获取的是相对路径
# D:\code\PycharmCode\day4\Atm

sys.path.append(BASE_DIR)

from core import shopping_cart  # 动态添加的，所以会有红线

if __name__ == "__main__":
    shopping_cart.run()
