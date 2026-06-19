
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import RandomForestClassifier

# Create your views here.
from Remote_User.models import ClientRegister_Model,predict_ev_energy_consumption,detection_ratio,detection_accuracy
from functools import wraps
import joblib

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            return redirect('serviceproviderlogin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            detection_accuracy.objects.all().delete()
            request.session['admin_logged_in'] = True
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')

def admin_logout(request):
    if 'admin_logged_in' in request.session:
        del request.session['admin_logged_in']
    return redirect('serviceproviderlogin')

@admin_required
def View_Prediction_Of_EV_Energy_Consumption_Type_Ratio(request):
    detection_ratio.objects.all().delete()
    ratio = 0
    kword = 'Less'
    print(kword)
    obj = predict_ev_energy_consumption.objects.all().filter(Q(Prediction=kword))
    obj1 = predict_ev_energy_consumption.objects.all()
    count = obj.count()
    count1 = obj1.count()
    if count1 > 0:
        ratio = (count / count1) * 100
    if ratio != 0:
        detection_ratio.objects.create(names=kword, ratio=ratio)

    ratio1 = 0
    kword1 = 'More'
    print(kword1)
    obj1 = predict_ev_energy_consumption.objects.all().filter(Q(Prediction=kword1))
    obj11 = predict_ev_energy_consumption.objects.all()
    count1 = obj1.count()
    count11 = obj11.count()
    if count11 > 0:
        ratio1 = (count1 / count11) * 100
    if ratio1 != 0:
        detection_ratio.objects.create(names=kword1, ratio=ratio1)

    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/View_Prediction_Of_EV_Energy_Consumption_Type_Ratio.html', {'objs': obj})

@admin_required
def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

@admin_required
def ViewTrendings(request):
    topic =predict_ev_energy_consumption.objects.values('Vehicle_Model').annotate(dcount=Count('Vehicle_Model')).order_by('-dcount')
    return  render(request,'SProvider/ViewTrendings.html',{'objects':topic})

@admin_required
def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

@admin_required
def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

@admin_required
def View_Prediction_Of_EV_Energy_Consumption_Type(request):
    obj =predict_ev_energy_consumption.objects.all()
    return render(request, 'SProvider/View_Prediction_Of_EV_Energy_Consumption_Type.html', {'list_objects': obj})

@admin_required
def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'chart_type':like_chart, 'like_chart':like_chart})


@admin_required
def Download_Trained_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Data.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = predict_ev_energy_consumption.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1

        ws.write(row_num, 0, my_row.Fid, font_style)
        ws.write(row_num, 1, my_row.Vehicle_Model, font_style)
        ws.write(row_num, 2, my_row.Battery_Capacity_kWh, font_style)
        ws.write(row_num, 3, my_row.Charging_Station_ID, font_style)
        ws.write(row_num, 4, my_row.Charging_Station_Location, font_style)
        ws.write(row_num, 5, my_row.Charging_Start_Time, font_style)
        ws.write(row_num, 6, my_row.Charging_EndTime, font_style)
        ws.write(row_num, 7, my_row.Energy_Consumed_kWh, font_style)
        ws.write(row_num, 8, my_row.Charging_Duration_hours, font_style)
        ws.write(row_num, 9, my_row.Charging_Rate_kW, font_style)
        ws.write(row_num, 10, my_row.Charging_Cost_USD, font_style)
        ws.write(row_num, 11, my_row.Vehicle_Age_years, font_style)
        ws.write(row_num, 12, my_row.Charger_Type, font_style)
        ws.write(row_num, 13, my_row.User_Type, font_style)
        ws.write(row_num, 14, my_row.Prediction, font_style)

    wb.save(response)
    return response

@admin_required
def train_model(request):
    detection_accuracy.objects.all().delete()
    data = pd.read_csv("Datasets.csv", encoding='latin-1')

    def apply_results(label):
        if (label == 0):
            return 0
        elif (label == 1):
            return 1

    data['Results'] = data['Label'].apply(apply_results)
    x = data['Fid'].apply(str)
    y = data['Results']

    cv = CountVectorizer()
    x = cv.fit_transform(x)

    print(x)
    print("Y")
    print(y)

    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    print("Quantile Regression Neural Network(QRNN)")

    from sklearn.neural_network import MLPClassifier
    mlpc = MLPClassifier().fit(X_train, y_train)
    y_pred = mlpc.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    models.append(('MLPClassifier', mlpc))
    detection_accuracy.objects.create(names="Quantile Regression Neural Network(QRNN)",ratio=accuracy_score(y_test, y_pred) * 100)

    # SVM Model
    print("SVM")
    from sklearn import svm

    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print("ACCURACY")
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Logistic Regression")

    from sklearn.linear_model import LogisticRegression

    reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)

    print("Decision Tree Classifier")
    dtc = DecisionTreeClassifier()
    dtc.fit(X_train, y_train)
    dtcpredict = dtc.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, dtcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, dtcpredict))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, dtcpredict))
    detection_accuracy.objects.create(names="Decision Tree Classifier", ratio=accuracy_score(y_test, dtcpredict) * 100)

    # Build ensemble VotingClassifier and save to disk
    models_ensemble = [
        ('MLPClassifier', mlpc),
        ('svm', lin_clf),
        ('logistic', reg)
    ]
    ensemble_clf = VotingClassifier(models_ensemble)
    ensemble_clf.fit(X_train, y_train)

    joblib.dump({'model': ensemble_clf, 'cv': cv}, 'ev_model.joblib')

    labeled = 'labeled_data.csv'
    data.to_csv(labeled, index=False)
    data.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/train_model.html', {'objs': obj})