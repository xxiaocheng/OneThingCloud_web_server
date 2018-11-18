from flask import render_template,redirect,flash,session,url_for,request,abort

import json

from .import cloud
from .form import CreateTaskForm
from app.OneThingCloud_API import dict2otc,OTC


@cloud.before_app_request
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

@cloud.route('/',methods=['POST','GET'])
def index():
    dict_otc=session.get('current_otc',None)
    my_otc=dict2otc(json.loads(dict_otc))
    flag,result=my_otc.get_remote_download_info()
    form=CreateTaskForm()
    if form.validate_on_submit():
            job = {
            "filesize": 0,
            "name": '',
            "url" : form.url.data
            }
            job_list=[job]
            flag,_=my_otc.create_task(job_list)
            if flag:
                flash('添加成功')
            else:
                flash('添加失败')
            return redirect(url_for('cloud.index'))

    if flag:
        try:
            download_num=result['dlNum']  #正在下载的个数
            tasks=result['tasks']   
            new_result=[]
            for task in tasks:
                t={}
                t['name']=task['name']
                t['id']=task['id']
                t['size']=str(int(task['size'])/1024/1024/1024)
                new_result.append(t)
            return render_template('cloud/mycloud.html',num=download_num,tasks=new_result,form=form)
        except:
            msg='获取失败,请重试!'
            return render_template('cloud/mycloud.html',msg=msg,form=form)
    else:
        return render_template('cloud/mycloud.html',msg='获取失败,请重试!',form=form)
    
@cloud.route('/coutrol')
def control_task():
    task_id=request.args.get('taskId')
    type=request.args.get('type')
    if not task_id or not type  :
        return redirect(url_for('cloud.index'))
    dict_otc=session.get('current_otc',None)
    my_otc=dict2otc(json.loads(dict_otc))
    flag,_=my_otc.control_download_task(task_id=str(task_id),sign=int(type))
    if flag:
        if type==0:
            flash('已开始任务!')
        else:
            flash('已暂停任务!')
    return redirect(url_for('cloud.index'))


