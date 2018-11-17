from flask import render_template,url_for,flash,session,redirect,request
from app.OneThingCloud_API import dict2otc
from . import wkb
import json

@wkb.route('/',methods=['GET','POST'])
def index():
    dict_otc=session.get('current_otc',None)
    my_otc=dict2otc(json.loads(dict_otc))
    flag,account_info=my_otc.get_wkb_account_info()
    if flag:
        try:
            addr_bind=account_info['data']['addr']   #绑定的钱包地址
            balance=account_info['data']['balance']  #账户余额
            return render_template('wkb/myaccount.html',addr_bind=addr_bind,balance=balance)
        except:
            msg='获取信息失败,请重试!'
            return render_template('wkb/myaccount.html',msg=msg)
    return render_template('wkb/myaccount.html',msg=msg)

@wkb.route('/draw')
def draw_wkb():
    # 提现到钱包
    dict_otc=session.get('current_otc',None)
    my_otc=dict2otc(json.loads(dict_otc))
    flag,msg=my_otc.draw_wkb()
    if flag:
        msg=msg.get('sMsg',None)
    else:
        msg='提现失败'
    flash(msg)
    return redirect(url_for('wkb.index'))


@wkb.route('/history_income',methods=['POST','GET'])
def history_income():
    # 查询入账记录
    dict_otc=session.get('current_otc',None)
    my_otc=dict2otc(json.loads(dict_otc))
    current_page=request.args.get('page','0')
    flag,result=my_otc.get_wkb_history(type='income',page=current_page)
    if flag:
        try:
            total_income=result['data']['totalIncome']
            next_page=result['data']['nextPage']
            income_array=result['data']['incomeArr']
            return render_template('wkb/history.html',title='收入记录',total_income=total_income,up_page=int(current_page)-1,next_page=next_page,income_array=income_array)
        except:
            msg='查询失败,请重试!'
    msg='查询失败,请重试!'
    return render_template('wkb/history.html',title='收入记录',msg=msg)


@wkb.route('/history_outcome',methods=['POST','GET'])
def history_outcome():
    # 查询提现记录
    dict_otc=session.get('current_otc',None)
    my_otc=dict2otc(json.loads(dict_otc))
    current_page=request.args.get('page','0')
    flag,result=my_otc.get_wkb_history(type='outcome',page=current_page)
    if flag:
        try:
            total_outcome=result['data']['totalOutcome']
            next_page=result['data']['nextPage']
            outcome_array=result['data']['outcomeArr']
            return render_template('wkb/history.html',title='提现记录',total_outcome=total_outcome,up_page=int(current_page)-1,next_page=next_page,outcome_array=outcome_array)
        except:
            msg='查询失败,请重试!'
    msg='查询失败,请重试!'
    return render_template('wkb/history.html',title='提现记录',msg=msg)