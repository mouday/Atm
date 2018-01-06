import json
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# D:\code\PycharmCode\day4\Atm

# 日志文件夹
log_path = os.path.join(BASE_DIR + "/logs/atm.log")

def log(func):
    def wrapper(*args, **kwargs):
        f = open(log_path, "a", encoding="utf-8")
        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\t"+func.__doc__+"\n")
        f.close()
        return func(*args, **kwargs)
    return wrapper

# 此处如果需要支持多个账户同时登陆，
# 需要为每个用户建立独立的文件来存放信息，
# 避免同时读写时信息不统一

class ATM(object):
    """实现ATM，用户信息的增删改查，管理员信息获取"""
    def get_users(self):
        """获取所有账户信息,return{dict}"""
        with open("../database/user.json", "r", encoding="utf-8") as f:
            users = json.load(f)
            return users

    def set_users(self, users):
        """设置所有用户信息,users{dict}"""
        with open("../database/user.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent="\t")
            return True

    def get_user(self, id):
        """获取单个用户信息,id{str},return{dict}"""
        users = self.get_users()
        user = users.get(id)
        return user

    def set_user(self,id, user):
        """设置单个用户信息,id{str},user{dict}"""
        users = self.get_users()
        users[id]=user
        self.set_users(users)

    def remove_user(self,id):
        """删除单个用户信息,id{str}"""
        users = self.get_users()
        if users:
            users.pop(id)
            self.set_users(users)
            return True
        else:
            return False

    def add_user(self, password, balance, limit, isLock):
        """添加新用户
        :param password: {str}密码
        :param balance: {int}余额
        :param limit: {int}额度
        :param isLock: {bool}是否锁定
        :return: id{str}新用户id
        """
        users = self.get_users()
        max_id = "000000"
        if users != {}:
            max_id = max(users.keys())
        cur_id = str(int(max_id) + 1).zfill(6)  # id自动+1，补足6位
        users[cur_id] = {
            "password": password,
            "balance": balance,
            "limit":limit,
            "isLock":isLock
        }
        self.set_users(users)
        return cur_id

    def get_manager(self):
        """获取管理员信息,return{dict}"""
        with open("../database/manager.json", "r") as f:
            manager = json.load(f)
            return manager

def verify(func):
    """账户验证"""
    def wrapper(self, *args, **kwargs):
        res = self.verify_account()
        if res == True:
            return func(self, *args, **kwargs)
        else:
            pass
    return wrapper


class Manager(object):
    """管理接口"""
    def __init__(self, manager_id, manager_password):
        self.id=manager_id
        self.password=manager_password

    @log
    @verify
    def add_user(self, password, balance=0, limit=1500, isLock=False):
        """添加新用户"""
        atm = ATM()
        user_id = atm.add_user(password, balance, limit, isLock)
        print("账户添加成功，id = %s" % user_id)

    @log
    @verify
    def remove_user(self, id):
        """删除账户 id{str} 账户id"""
        atm = ATM()
        res = atm.remove_user(id)
        if res:
            print("账户删除成功")
        else:
            print("账户不存在")

    @log
    @verify
    def set_user_limit(self, id, limit):
        """设置用户额度"""
        atm = ATM()
        user = atm.get_user(id)
        user["limit"] = limit
        atm.set_user(id, user)
        print("额度修改成功，当前额度为： %s " % limit)

    @verify
    def set_user_islock(self, id, islock):
        """修改账户状态，锁定，解锁"""
        atm = ATM()
        user = atm.get_user(id)
        user["isLock"] = islock
        atm.set_user(id, user)
        print("账户修改成功，当前状态为： %s " % ("锁定" if islock else "正常"))

    def verify_account(self):
        """登陆验证
        :return: {bool} True为通过，False为失败
        """
        atm = ATM()
        manager = atm.get_manager()
        is_pass = False
        if self.id != manager["id"]:
            print("账户验证失败：卡号不存在！")
        else:
            if self.password != manager["password"]:
                print("账户验证失败：密码错误！")
            else:
                print("账户验证成功！")
                is_pass = True
        return is_pass

class User(object):
    """用户接口"""
    def __init__(self, id, password):
        self.id=id
        self.password=password

    @log
    @verify
    def set_password(self, password):
        """更新密码"""
        atm =ATM()
        user = atm.get_user(self.id)
        user["password"] = password
        atm.set_user(user)
        print("密码修改成功")

    @verify
    def get_balance(self):
        """获取余额"""
        atm = ATM()
        user = atm.get_user(self.id)
        return user["balance"]


    def _add_balance(self, money):
        """增加余额,不需要验证账户"""
        atm = ATM()
        user = atm.get_user(self.id)
        if user != None:  # 验证账户存在
            user["balance"] += money
            if user["balance"] >= -user["limit"]:
                atm.set_user(self.id, user)
                return True
        return False

    @verify
    def _reduce_balance(self, money):
        """减少余额"""
        return self._add_balance(-money)

    @log
    def draw_money(self,money):
        """提现取款"""
        service_charge = int(money * 0.05)
        total = money + service_charge
        res = self._reduce_balance(total)
        if res == True:
            print("取款成功，金额： %s 手续费： %s" % (money, service_charge))
        else:
            print("取款失败,余额不足")
        return res

    @log
    def repayment(self,money):
        """还款"""
        res = self._add_balance(money)
        if res ==True:
            print("还款成功")
        else:
            print("还款失败")
        return res

    @log
    def payment(self,money):
        """付款"""
        res = self._reduce_balance(money)
        if res == True:
            print("付款成功")
        else:
            print("付款失败,余额不足")
        return res

    @log
    def show_info(self):
        """打印信息"""
        print("账户信息：")
        print("账户ID：",self.id)

    @log
    def remit(self, id, money):
        """转账汇款"""
        reduce_res = self._reduce_balance(money)  #取款
        if reduce_res == True:
             user = User(id, None)
             add_res = user._add_balance(money)  # 存款
             if add_res ==True:
                print("转账成功")
             else:
                self._add_balance(money)  # 存款失败，打回取款账户
                print("转账失败，对方用户异常")
        else:
            print("转账失败，余额不足")

    def verify_account(self):
        """登陆验证,return: {bool} True为通过，False为失败"""
        atm = ATM()
        user = atm.get_user(self.id)
        is_pass = False
        if user == None:
            print("账户验证失败：卡号不存在！")
        else:
            if self.password == user["password"]:
                # print("账户验证成功！")
                is_pass = True
            else:
                print("账户验证失败：密码错误！")
        return is_pass

def main():
    user = User("000001","123456")
    user.repayment(1000)
    user.draw_money(100)

if __name__ == "__main__":
    main()