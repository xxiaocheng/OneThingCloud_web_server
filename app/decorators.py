from flask import session,redirect,url_for
from functools import wraps
import json
from app.OneThingCloud_API import dict2otc,OTC

def session_check(view):
    @wraps(view)
    def wrapped_view(**kwargs):
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
        return view(**kwargs)
    return wrapped_view