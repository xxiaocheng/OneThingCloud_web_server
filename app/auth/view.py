from flask import render_template,url_for,flash,redirect,session

import json

from . import auth
from .form import LoginFrom
from app.OneThingCloud_API import OTC


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
        # flash('登录失败!')
    return render_template('auth/login.html',form=form)


@auth.route('/logout')
def logout():
    session['current_otc']=None
    return redirect(url_for('auth.login'))

