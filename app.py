import base64
import numpy as np
import mysql.connector
#初始化資料庫
import pymongo
import time
import matplotlib.pyplot as plt
from flask import *
from py3dbp import Packer, Item, Bin, Painter
from camera import VideoCamera
import cv2

app = Flask(__name__, static_folder="static", static_url_path="/")
app.secret_key = "any string but secret"
client = pymongo.MongoClient("mongodb+srv://root:root123@mycluster.xucyx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.member_system
connection = mysql.connector.connect(host='localhost',
                                         database='product',
                                         user='root',
                                         password='Au3xl3gj3')
my_cursor = connection.cursor()




@app.route('/video')
def video():
    return render_template("video.html")
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    print(type(gen(VideoCamera)))
    print(gen(VideoCamera))
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/member')
def member():
    if "nickname" in session:
        return render_template("member.html")
@app.route("/error")
def error():
    message = request.args.get("msg", "發生錯誤請聯繫克服")
    return render_template("error.html", message=message)

@app.route("/signup", methods=["POST"])
def signup():
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    collection = db.user
    result = collection.find_one({
        "email": email
    })
    if result != None:
        return redirect("/error?msg=信箱已被註冊")
    collection.insert_one({
        "nickname": nickname,
        "email": email,
        "password": password
    })
    return redirect("/")
@app.route("/signin", methods=["POST"])
def sign():
    email = request.form["email"]
    password = request.form["password"]
    collection = db.user
    result = collection.find_one({
        "$and": [
            {"email": email},
            {"password": password}
        ]
    })
    if result == None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    session["nickname"] = result["nickname"]
    return redirect("/member")
@app.route("/signout")
def signout():
    del session["nickname"]
    return redirect("/")
@app.route('/sqldata')
def sqldata():
    # if session["nickname"] == None:
    #     return render_template('/')
    # else:
    sql = 'select * from product'
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    sql = 'show fields from product'
    my_cursor.execute(sql)
    labels = my_cursor.fetchall()
    print(labels)
    labels = [l[0] for l in labels]
    print(labels)
    return render_template('product.html', product=my_result, labels=labels)
@app.route('/order_query')
def order_query():

    return render_template('order.html')
@app.route('/order_result', methods=["POST"])
def order_result():
    order_number = request.form["order_number"]

    # 抓表頭
    sql = 'show fields from product.order'
    my_cursor.execute(sql)
    labels = my_cursor.fetchall()
    labels = [l[0] for l in labels]
    #抓欄位名稱
    sql = f"""select * from product.order
          where order_id = {order_number}"""
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    session["order_number"] = order_number
    #

    return render_template("order_result.html", order=my_result, labels=labels)
@app.route("/just_picture")
def just_picture():
    # 抓長寬高準備包裝
    order_number = session.get('order_number')
    dict_1 = {}
    list_1 = []
    start = time.time()
    my_cursor.execute(f"SELECT product_id,quantity FROM product.order where order_id={order_number}")
    data = my_cursor.fetchall()
    for i in data:
        inner_list = list(i)
        my_cursor.execute(f"SELECT length,width,height FROM product.product where product_id={i[0]}")
        datas = my_cursor.fetchall()
        for k in datas:
            inner_list.extend(list(k))
        list_1.append(inner_list)
    list_max = []
    total_v = 0
    for d in range(len(list_1)):
        width = list_1[d][2]
        length = list_1[d][3]
        height = list_1[d][4]
        qaulity = list_1[d][1]
        volume = width * length * height
        total_v = total_v + volume
        list_max.append(max(tuple(list_1[d][2:])))
    list_color = ['red', 'blue', 'orange', 'lawngreen', 'purple', 'lawngreen', 'yellow', 'gray', 'pink', 'brown',
                  'cyan', 'olive', 'darkgreen', 'orange']
    if total_v < 4500:
        if max(list_max) < 25:
            print("使用一號箱")
            box_size = (25, 18, 10)
        elif max(list_max) < 32:
            print("使用二號箱")
            box_size = (32, 25, 15)
        elif max(list_max) < 35:
            print("使用三號箱")
            box_size = (35, 26, 16)
        elif max(list_max) < 50:
            print("使用五號箱")
            box_size = (50, 35, 35)
        else:
            print("使用特規箱")
            box_size = (100, 100, 100)
    elif 4500 < total_v < 12000:
        if max(list_max) < 32:
            print("使用二號箱")
            box_size = (32, 25, 15)
        elif max(list_max) < 35:
            print("使用三號箱")
            box_size = (35, 26, 16)
        elif max(list_max) < 50:
            print("使用五號箱")
            box_size = (50, 35, 35)
        else:
            print("使用特規箱")
            box_size = (100, 100, 100)
    elif 12000 < total_v < 14560:
        if max(list_max) < 35:
            print("使用三號箱")
            box_size = (35, 26, 16)
        elif max(list_max) < 50:
            print("使用五號箱")
            box_size = (50, 35, 35)
        else:
            print("使用特規箱")
            box_size = (100, 100, 100)
    elif 14560 < total_v < 36750:
        if max(list_max) < 35:
            print("使用四號箱")
            box_size = (35, 30, 35)
        elif max(list_max) < 50:
            print("使用五號箱")
            box_size = (50, 35, 35)
        else:
            print("使用特規箱")
            box_size = (100, 100, 100)
    elif 36750 < total_v < 61250:
        if max(list_max) < 50:
            print("使用五號箱")
            box_size = (50, 35, 35)
        else:
            box_size = (100, 100, 100)
            print("使用特規箱")
    else:
        print("請使用特殊規格箱")
        box_size = (100, 100, 100)
    print(box_size)
    packer = Packer()
    #  init bin
    # box_ = (box_length, box_winth, box_height)
    box = Bin('example1', box_size, 70.0, 0, 0)
    packer.addBin(box)
    #  add item
    for f in range(len(list_1)):
        packer.addItem(Item(f, list_1[f][1], 'cube', tuple(list_1[f][2:]), 1, 1, 100, True, list_color[f]))
        if list_1[f][1] > 1:
            for s in range(int(list_1[f][1]) - 1):
                packer.addItem(Item(f, list_1[f][1], 'cube', tuple(list_1[f][2:]), 1, 1, 100, True, list_color[f]))
    packer.pack(bigger_first=True, distribute_items=False, fix_point=True, number_of_decimals=0)

    # put_text result
    b = packer.bins[0]
    volume = b.width * b.height * b.depth
    print(":::::::::::", b.string())

    print("FITTED ITEMS:")
    volume_t = 0
    volume_f = 0
    unfitted_name = ''
    for item in b.items:
        volume_t += float(item.width) * float(item.height) * float(item.depth)
    for item in b.unfitted_items:
        volume_f += float(item.width) * float(item.height) * float(item.depth)
        unfitted_name += '{},'.format(item.partno)
    use_rate = round(volume_t / float(volume) * 100, 2)
    remain = (float(volume) - volume_t)
    print("***************************************************")
    print('空間利用率 : {}%'.format(round(volume_t / float(volume) * 100, 2)))
    print('空間剩餘量 : ', float(volume) - volume_t)
    print('沒裝進的貨物 : ', unfitted_name)
    print('沒裝進的貨物體積 : ', volume_f)
    print("重力分布 : ", b.gravity)
    stop = time.time()
    print('使用時間 : ', stop - start)

    painter = Painter(b)
    result = painter.plotBoxAndItems()
    session['order_number'] = False
    return render_template('just_picture.html', use_rate=use_rate, remain=remain, volume_f=volume_f)


app.run(debug=True, port=3002)