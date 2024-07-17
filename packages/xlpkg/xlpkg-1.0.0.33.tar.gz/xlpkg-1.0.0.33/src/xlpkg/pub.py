import re,os,json,logging,jsonify ,webbrowser, pymysql

from flask import Flask
from user import bp_user
from customer import bp_customer as bp_cust
#
from datetime import datetime,timedelta
from flask import Flask,request, render_template
from screeninfo import get_monitors

# 列出所有文件
def f_getallfiles(path=os.getcwd()):
    x=[]
    for root, dirs, files in os.walk(path):
        for file in files:
            x.append(os.path.join(root, file))
            print(os.path.join(root, file))
    return(x)

#判断一个点是否在一个多边形区域内。
#使用射线交点法。通过从给定点引一条射线，然后计算这条射线与多边形边的交点数量来判断点是否在多边形内部。如果交点数量是奇数，点在多边形内部；如果是偶数，点在多边形外部。
def f_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside
    pass



# 配置日志
def f_logging(app,logpath):
    # 设置日志的格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建FileHandler，用于写入日志文件
    #file_handler = logging.FileHandler('./logs/app.log')
    file_handler = logging.FileHandler(logpath)
    file_handler.setFormatter(formatter)
    
    # 如果在应用上下文中，则配置日志
    if not app.debug:
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
    pass

#与types相同
products=(
        ('all','全部'),
        ('15','跑腿快车'),
        ('16','快车超市'),
        ('18','快车代驾'),
        ('20','客服问题'),
        ('!20','非客服问题'))
groups=(
        ('all',     '全部'),
        ('devel',   '开发'),
        ('test',    '测试'),
        ('design',  '产品'),
        ('check',   '验收'),
        ('ui',      'UI'))
groups_bug=(
        ('all',     '全部'),
        ('test',   '测试'),
        ('kf',      '客服'))
#与groups相同
types=(
        ('all','    全部'),
        ('devel',   '开发'),
        ('test',    '测试'),
        ('design',  '产品'),
        ('check',   '验收'),
        ('ui',      'UI'))

names_all=(
        ('all','全部'),
        ('liuchengjie',     '刘成杰'), 
        ('huanglinqiang',   '黄林强'), 
        ('wangjun',          '王军'), 
        ('jiangjiapei',     '江佳沛'), 
        ('huangligen',      '黄立根'), 
        ('luyonghui',       '卢永辉'), 
        ('liudong',         '刘东'), 
        ('liuyunlong' ,     '刘允隆'),
        ('guoweihong',      '郭伟红'),
        ('litulong',        '李土龙'), 
        ('luojianbo',       '罗剑波'),
        ('- - - -','- - - -'), 
        ('xiongqi',         '熊琪' ), 
        ('xiaolong',        '肖龙'), 
        ('huanglifei',      '黄麗妃'), 
        ('liuyifei',        '刘怡妃') ,
        ('gongcandong',     '龚灿东'), 
        ('huangfengming',   '黄凤明'), 
        ('wangechen',       '王郴')) 

names_test=(
        ('all',             '全部'), 
        ('xiongqi',         '熊琪' ), 
        ('xiaolong',        '肖龙'), 
        ('huanglifei',      '黄麗妃'), 
        ('liuyifei',        '刘怡妃')) 
names_devel=(
        ('all',             '全部'),
        ('liuchengjie',     '刘成杰'), 
        ('huanglinqiang',   '黄林强'), 
        ('wangjun',         '王军'), 
        ('jiangjiapei',     '江佳沛'), 
        ('huangligen',      '黄立根'), 
        ('luyonghui',       '卢永辉'), 
        ('liudong',         '刘东'), 
        ('liuyunlong' ,     '刘允隆'),
        ('guoweihong',      '郭伟红'),
        ('litulong',        '李土龙'), 
        ('luojianbo',       '罗剑波') 
        )

names_design=(
        ('all',             '全部'), 
        ('gongcandong',     '龚灿东'), 
        ('huangfengming',   '黄凤明'))
names_front=(
        ('all',             '全部'),
        ('liuchengjie',     '刘成杰'), 
        ('huanglinqiang',   '黄林强'), 
        ('wangjun',         '王军'), 
        ('jiangjiapei',     '江佳沛'), 
        ('huangligen',      '黄立根'), 
        ('luyonghui',       '卢永辉')
        )

names_background=(
        ('all',             '全部'),
        ('liudong',         '刘东'), 
        ('liuyunlong' ,     '刘允隆'),
        ('guoweihong',      '郭伟红'),
        ('litulong',        '李土龙'), 
        ('luojianbo',       '罗剑波') 
        )
names_ui=(
        ('all',             '全部'), 
        ('wangchen',        '王郴'))
names_kf=(
        ('all',             '全部'), 
        ('liaojianbing',    '廖健兵'),
        ('yanliren',        '杨莉仁'),
        ('xiaolong',        '肖龙')
        )
names_ops=(
        ('all','全部'),
        ('liangyuqi',       '梁玉琦'),
        ('xieliangbin',     '谢亮斌'))

status_bug=(
        ('all',             '全部'),
        ('active',          '激活'),
        ('resolved',        '已解决'),
        ('closed',          '已关闭')
        )
status_task=(
        ('all',             '全部'),
        ('pause',           '暂停'  ), 
        ('wait',            '准备中' ), 
        ('doing',           '进行中' ), 
        ('closed',          '已关闭' ), 
        ('done',            '已完成'),
        ('!done',           '未完成'))

#task
time_task=( 
        ('openedDate',      '创建时间'),
        ('assignedDate',    '指派时间'),
        ('realStarted',     '开始时间'),
        ('closedDate',      '完成时间'))

titles_task=( 
        ('0','Product'), 
        ('1','ID'), 
        ('2','需求'), 
        ('3','任务名称'), 
        ('4','小组'), 
        ('5','责任人'), 
        ('6','任务状态'), 
        ('7','说明')) 

titles_buglist=( 
        ('0','Product'),
        ('1','BugID'),
        ('2','Bug标题'),
        ('3','严重程度'),
        ('4','优先级'),
        ('5','创建时间'),
        ('6','关闭时间'),
        ('7','创建人'),
        ('8','指派给'),
        ('9','状态'))

titles_bugtj1=( 
        ('0','Product'),
        ('1','严重程度'),
        ('2','数量'))

titles_bugtj2=( 
        ('0','Product'),
        ('1','严重程度'),
        ('2','状态'),
        ('3','数量'))

task_p=( 
        ('10','10行'),
        ('20','20行'),
        ('50','50行'),
        ('100','100行'),
        ('200','200行'))

#bug
bug_titles=( 
        ('0','Product'),
        ('1','BugID'),
        ('2','Bug标题'),
        ('3','严重程度'),
        ('4','优先级'),
        ('5','创建人'),
        ('6','状态'))
bug_p=( 
        ('0','10'),
        ('1','20'),
        ('2','50'),
        ('3','100'),
        ('4','200')
        )

#kf
kf_names=(
        ('0','全部'),
        ('1','波'),
        ('2','隆'),
        ('3','龙'),
        ('4','红'),
        ('5','刘东'),
        ('6','黄麗妃'),
        ('7','龚灿东'))
kf_types=( 
        ('0','创建时间'),
        ('1','指派时间'),
        ('2','解决时间'),
        ('3','关闭时间')
        )

kf_stas=( 
        ('0','全部',), 
        ('2','激活',), 
        ('3','已解决',), 
        ('4','已关闭',)
        )
kf_titles=( 
        ('0','产品名称'),
        ('1','模块名称'),
        ('2','问题编号'),
        ('3','问题描述'),
        ('4','严重程度'),
        ('5','优先级'),
        ('6','提交人'),
        ('7','创建时间'),
        ('8','解决时间'),
        ('8','关闭时间'),
        ('9','状态')
        )
kf_p=( 
        ('0','10'),
        ('1','20'),
        ('2','50'),
        ('3','100'),
        ('4','200'))

kfcx_titles=(
        ('0','代理商ID'),
        ('1','商家ID'),
        ('2','商家名称'),
        ('3','商家电话'),
        ('4','商家地址'),
        ('5','订单编号'),
        ('6','订单类型'),
        ('7','抽成方式'),
        ('8','订单状态'),
        
        ('9','取消状态'),('10','退款状态'))
kfcxprinter_titles=(
        ('0','代理商ID'),
        ('1','代理商名称'),
        ('2','商家ID'),
        ('3','商家名称'),
        ('4','商家电话'),
        ('5','外卖电话'),
        ('6','商家地址'),
        ('7','statu'),
        ('8','status'),
        ('9','statusx'),
        ('10','自动标签打印'),
        ('11','是否删除'),
        ('12','是否代理商删除'))
titles_fyinfo=(
        ('0','平台编码'), 
        ('1','代理商id'), 
        ('2','代理商名称'), 
        ('3','商家id'), 
        ('4','商家名称'), 
        ('5','商家联系电话'), 
        ('6','第三方类型'), 
        ('7','入账方主体类型'), 
        ('8','到账周期类型'), 
        ('9','最后申请日期'), 
        ('10','入账账户类型'), 
        ('11','入账商家名称'), 
        ('12','入账方类型'), 
        ('13','入账证件到期日'), 
        ('14','入账方主体名称'), 
        ('15','入账卡号'), 
        ('16','入账卡用户名称'), 
        ('17','入账卡银行预留手机号'), 
        ('18','入账卡开户行名称'), 
        ('19','开户许可证照片地址'), 
        ('20','开户行行号'), 
        ('21','开户证件类型'), 
        ('22','开户证件名称'), 
        ('23','开办资金'), 
        ('24','开户证件代码'), 
        ('25','开户证件有效期'), 
        ('26','证件扫码图片地址'), 
        ('27','品牌名称') , 
        ('28','电子邮件' ), 
        ('29','联系人名称'), 
        ('30','联系人电话'), 
        ('31','证件号'), 
        ('32','证件到期日'), 
        ('33','证件类型'), 
        ('34','身份证正面照片'), 
        ('35','身份证反面照片'), 
        ('36','分账合同名称'), 
        ('37','合同开始时间'), 
        ('38','合同到期时间'), 
        ('38','合同照片路径'), 
        ('40','合同最大分成比例'), 
        ('41','入账方的商户编号'), 
        ('42','入账方合同编号'), 
        ('43','入账合同规则'), 
        ('44','最后申请状态'), 
        ('45','创建时间'), 
        ('46','更新时间'))


help_sms={"01":"/ /help  接口用法帮助","/sms?m=15975576669":"根据手机号码查询短信验证码"}

app = Flask(__name__)
app.config['CHARSET']='utf-8'
app.config['JSON_AS_ASCII']= False
app.json.ensure_ascii=False

def f_mask_phone(phone,reg1,reg2):
    #return re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', phone)
    # 使用正则表达式匹配电话号码，替换中间4位数字为星号
    return re.sub(reg1,reg2, phone)
    pass



#数字前补0
def f_pad(num,n=0):
    return(str(num).zfill(n))
    pass
    
#数字前补0
def f_pad1(num,n=0,s='0'):
    return(str(num).rjust(n,s))
    pass

#根据坐标绘制多边形
def f_draw(x,folder,fname):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    if not os.path.exists(folder):
        os.makedirs(folder)

    #x=[[0,0],[10,0],[10,10],[12,12],[2,12],[0,10],[10,10],[0,10]]
    p1 = patches.Polygon(x, edgecolor='green', facecolor='none')
    plt.gca().add_patch(p1)
    plt.axis('scaled')
    plt.savefig(os.path.join(folder,fname))
    plt.show()
    pass


def f_basedir():
	basedir = os.path.abspath(os.path.dirname(__file__))
	return(basedir)
	pass
#uuid
def f_uuid():
    return(uuid.uuid5(uuid.NAMESPACE_DNS,'000000'))
    pass


# 数据库连接
def f_conn(x):
    conn=None
    match x:
        case 'l'|'local':   #本机
            conn = pymysql.connect( host='localhost', user='root', password='000000', database='xl')
            pass

        case 'ptkc':        #跑腿快车测试环境
            conn= pymysql.connect( host='192.168.2.41', user='wd_local', password='wd_PTKC', database='runfast_trade')
            #conn= pymysql.connect( host='192.168.2.41', user='wd_local', password='wd_PTKC', database='runfast_trade',cursorclass='pymysql.cursors.DictCursor')
            #conn= pymysql.connect( host='172.18.6.153', user='wd_local', password='wd_PTKC', database='runfast_trade')
            pass

        case 'ptkc_prod':        #跑腿快车生产环境
            conn= pymysql.connect( host='172.18.1.26', user='wd_test', password='wd2021ptkc@test', database='runfast_trade')
            pass

        case 'zt'|'zentao': #禅道
            conn = pymysql.connect( host='172.18.2.135', user='test', password='test@123', database='zentao')
            pass
    return(conn)
    pass

#用浏览器打开html文件
def f_openhtml(html):
    webbrowser.open(html)
    pass

#获取当前文件名
def f_filename():
    return(__file__)
    pass


# 获取屏幕大小
def f_screensize():
    m = get_monitors()[0]
    return (m.width,m.height)
    pass

#日期时间
def f_dt(n=0,fmt=0):
    curr=datetime.now()+timedelta(days=n)
    match fmt:
        case 0:
            return(curr.strftime("%Y.%m.%d %H:%M:%S"))
        case 1:
            return(curr.strftime("%Y.%m.%d"))
        case 2:
            return(curr.strftime("%H:%M:%S"))
    pass


#===================

#文件按行倒序：
#1.使用file.readlines()和列表切片
def f_frev01(fname):
    with open(fname, "r") as file:
        lines = file.readlines()
        reversed_lines = lines[::-1]
        for line in reversed_lines:
            print(line.strip())
    pass

#2.使用file.readlines()和reversed()函数

def f_frev02(fname):
    with open(fname, "r") as file:
        lines = file.readlines()
        reversed_lines = reversed(lines)
        for line in reversed_lines:
            print(line.strip())
    pass

#3.使用file.readlines()和list.reverse()方法

def f_frev03(fname):
    with open(fname, "r") as file:
        lines = file.readlines()
        lines.reverse()
        for line in lines:
            print(line.strip())
    pass

#4.使用file.readlines()和自定义逆序迭代器

def rev_iterator(iterable):
    for i in range(len(iterable)-1, -1, -1):
        yield iterable[i]
    pass

def f_frev04(fname):
    with open(fname, "r") as file:
        lines = file.readlines()
        rev_lines = rev_iterator(lines)
        for line in rev_lines:
            print(line.strip())
        pass
    pass


def f_frw(fname,newname):
    # 打开原始文件以读取内容
    with open(fname, 'r') as file:
        lines = file.readlines()
     
    # 倒序文件内容
    reversed_lines = reversed(lines)
     
    # 打开目标文件以写入倒序后的内容
    with open(newname, 'w') as file:
        file.writelines(reversed_lines)
    return(newname)
    pass


if __name__=="__main__":
    fname='file.txt'
    f_frev01(fname)
    f_frev02(fname)
    f_frev03(fname)
    f_frev04(fname)
    pass
