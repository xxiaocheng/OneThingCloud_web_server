from flask import render_template,url_for,flash,redirect,session

import json

from . import auth
from .form import LoginFrom
from app.OneThingCloud_API import OTC,dict2otc


@auth.before_app_request
def before_request():
    dict_otc=session.get('current_otc',None)
    if not dict_otc :
        return redirect(url_for('auth.login'))
    my_otc=dict2otc(json.loads(dict_otc))
    flag,_=my_otc.getListPeer()
    if not flag:
        my_otc=OTC(user_phone_number=my_otc.user_phone_number,user_password=my_otc.user_password)
        flag,_=my_otc.getListPeer()
        if not flag:
            return redirect('auth.login')
        else:
            otc_json=json.dumps(my_otc, default=lambda obj: obj.__dict__) 
            session['current_otc']=otc_json

@auth.route('/login',methods=['GET','POST'])
def login():
    current_otc=session.get('current_otc',None)
    if current_otc:
        return redirect(url_for('main.index'))
    form=LoginFrom()
    if form.validate_on_submit():
        otc=OTC(form.phone.data,user_password=form.password.data)
        if otc.is_logined:
            otc_json=json.dumps(otc, default=lambda obj: obj.__dict__) # 将otc对象序列化,以存入session
            session['current_otc']=otc_json
            return redirect(url_for('main.index'))
        flash('登录失败!')
    return render_template('auth/login.html',form=form)


@auth.route('/logout')
def logout():
    session['current_otc']=None
    flash('已退出登录!')
    return redirect(url_for('auth.login'))

