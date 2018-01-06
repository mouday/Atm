"""购物车升级版V2.0
用户入口：
    1.商品信息存在文件里
    2.已购商品，余额信息记录
商家入口：
    1.可以添加商品，修改商品价格
更新V2.0
添加ATM接口，用于购物支付
添加购物日志
"""
import json
import os
import time
# import sys
# sys.path.append("..")  # 加入系统路径

from core import atm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# D:\code\PycharmCode\day4\Atm

# 日志文件夹
log_path = os.path.join(BASE_DIR + "/logs/shopping.log")

def log(arg):
    f = open(log_path, "a", encoding="utf-8")
    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\t"+arg+"\n")
    f.close()

def get_goods():
    """获取商品信息
    :return: goods{dict}
    """
    with open("../database/goods.json","r", encoding="utf-8") as f:
        goods = json.load(f)
        return goods


def set_goods(goods):
    """保存商品信息
    :param goods: {dict}
    :return: None
    """
    with open("../database/goods.json", "w", encoding="utf-8") as f:
        json.dump(goods, f, ensure_ascii=False, indent="\t")


def get_userinfo():
    """获取用户信息
    :return: user_info{dict}
    """
    with open("../database/userinfo.json", "r",encoding="utf-8") as f:
        user_info = json.load(f)
        return user_info


def set_userinfo(userinfo):
    """保存用户信息
    :param user_info: {dict}
    :return: None
    """
    with open("../database/userinfo.json", "w", encoding="utf-8") as f:
        # 中文字符乱码,dump默认使用的ascii编码
        # 使用 ensure_ascii=False 关掉这个默认选项就可以
        json.dump(userinfo, f, ensure_ascii=False, indent="\t")


def choice_user_type():
    """选择用户类型，1.客户/2.商家/0.错误
    :return:user_type{int}
    """
    user_type = input("请选择登陆模式（1.客户/2.商家）：")
    if user_type == "1":
        print("以客户模式登陆，可以购买商品。")
        return 1
    elif user_type == "2":
        print("以商家模式登陆，可以修改商品。")
        return 2
    else:
        print("选择错误！")
        return 0


def check_balance(user, good_prices):
    """检查余额是否足够
    :param user{User}:用户对象
    :param good_prices{list}:价格列表
    :return balance{int}:余额
    """
    balance =user.get_balance()
    if balance < min(good_prices):
        add = input("当前余额：\033[31;1m%s\033[0m，余额不足，请充值:" % balance)
        if add.isdigit():  # 判断用户输入是否为数字
            user.repayment(int(add))
            balance = user.get_balance()
            print("充值成功，当前余额为：\033[32;1m%s\033[0m" % balance)
        else:
            print("充值失败，当前余额为：\033[32;1m%s\033[0m" % balance)
    return balance


def customer_mode():
    # 获取信息
    goods = get_goods()
    userinfo = get_userinfo()

    # 初始化
    id = userinfo["id"]
    password = userinfo["password"]

    user = atm.User(id, password)
    balance = user.get_balance() # 余额
    shopping_cart = userinfo["shopping_cart"] # 购物车

    good_prices = [good[1] for good in goods]  # 价格列表

    # 打印相关信息
    print("当前用户信息：")
    print("\t当前余额：\033[32;1m%s\033[0m" % balance)
    print("\t购物车：")
    for good in userinfo["shopping_cart"]:
        print("\t-", good)

    balance = check_balance(user, good_prices)

    while True:
        # 打印商品列表
        print("商品列表：")
        for index, value in enumerate(goods):
            print(" ", index, "->", value)

        user_input = input("请选择商品编号(q退出):")

        if user_input.isdigit():  # 用户输入类型校验
            good_number = int(user_input)
            if 0 <= good_number and good_number < len(goods):  # 商品编号校验
                price =  goods[good_number][1]
                res = user.payment(price)  # 支付
                balance = user.get_balance()
                if res == True:  # 余额检验
                    shopping_cart.append(goods[good_number])
                    # \033设置显示颜色
                    log(str(goods[good_number]))
                    print("%s 购买成功！余额：\033[31;1m %s\033[0m" % (goods[good_number], balance))
                else:
                    print("余额不足！余额：\033[41;1m%s\033[0m" % balance)
                    balance = check_balance(user, good_prices)

            else:
                print("请输入正确的商品编号：%s~%s" % (0, len(goods)-1))
        elif user_input == "q":
            print("余额：\033[32;1m%s\033[0m" % balance)
            print("已购商品：")
            for good_number in shopping_cart:
                print(" ", good_number)

            # 保存用户信息
            userinfoupdate = {"id": "000001","password":"123456", "shopping_cart": shopping_cart}
            set_userinfo(userinfoupdate)
            print("谢谢光临")
            exit()  # 退出
        else:
            print("请输入正确的商品编号！")



def manage_mode():
    goods = get_goods()
    while True:
        # 打印商品列表
        for good in goods:
            print(good)

        good_name = input("需要修改的商品(q退出)：")
        good_names=[good[0] for good in goods]  # 获取商品列表
        if good_name in good_names:
            mode = input("选择修改模式(1.修改/2.删除):")
            if mode == "1":
                print("\033[32;1m%s\033[0m 的当前价格为：\033[31;1m%s\033[0m" % (good_name, goods[good_names.index(good_name)][1]))
                price = input("修改价格为：")
                if price.isdigit():
                    price = int(price)
                    goods[good_names.index(good_name)][1] = price
                    print("价格修改成功！")
                else:
                    print("输入价格错误")
            elif mode == "2":
                goods.pop(good_names.index(good_name))
                print("成功删除：",good_names)
        elif good_name == "q":
            set_goods(goods)
            print("退出成功！")
            exit()
        else:
            print("库存中无此商品，将新增：\033[32;1m%s\033[0m" % good_name)
            price = input("设置价格为：")
            if price.isdigit():
                price = int(price)
                goods.append([good_name, price])
                print("新增商品成功！")
            else:
                print("输入价格错误")


def run():
    user_type = choice_user_type()
    if user_type == 1:  # 客户
        customer_mode()
    elif user_type == 2:  # 商家
        manage_mode()
    else:  # 错误
        exit()


if __name__ == "__main__":
    run()
