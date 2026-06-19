
from django.shortcuts import render, redirect, get_object_or_404

import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import VotingClassifier
# Create your views here.
from Remote_User.models import ClientRegister_Model,predict_ev_energy_consumption,detection_ratio,detection_accuracy
from functools import wraps
import os
import joblib

def user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('userid'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def login(request):


    if request.method == "POST" and 'submit1' in request.POST:

        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            enter = ClientRegister_Model.objects.get(username=username,password=password)
            request.session["userid"] = enter.id

            return redirect('ViewYourProfile')
        except:
            pass

    return render(request,'RUser/login.html')

def user_logout(request):
    if 'userid' in request.session:
        del request.session['userid']
    return redirect('login')

@user_required
def Add_DataSet_Details(request):

    return render(request, 'RUser/Add_DataSet_Details.html', {"excel_data": ''})


def Register1(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phoneno = request.POST.get('phoneno')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        ClientRegister_Model.objects.create(username=username, email=email, password=password, phoneno=phoneno,
                                            country=country, state=state, city=city, address=address, gender=gender)
        obj = "Registered Successfully"
        return render(request, 'RUser/Register1.html', {'object': obj})
    else:
        return render(request,'RUser/Register1.html')

@user_required
def ViewYourProfile(request):
    userid = request.session['userid']
    obj = ClientRegister_Model.objects.get(id= userid)
    return render(request,'RUser/ViewYourProfile.html',{'object':obj})


@user_required
def Prediction_Of_EV_Energy_Consumption_Type(request):
    if request.method == "POST":

        Fid= request.POST.get('Fid')
        Vehicle_Model= request.POST.get('Vehicle_Model')
        Battery_Capacity_kWh= request.POST.get('Battery_Capacity_kWh')
        Charging_Station_ID= request.POST.get('Charging_Station_ID')
        Charging_Station_Location= request.POST.get('Charging_Station_Location')
        Charging_Start_Time= request.POST.get('Charging_Start_Time')
        Charging_EndTime= request.POST.get('Charging_EndTime')
        Energy_Consumed_kWh= request.POST.get('Energy_Consumed_kWh')
        Charging_Duration_hours= request.POST.get('Charging_Duration_hours')
        Charging_Rate_kW= request.POST.get('Charging_Rate_kW')
        Charging_Cost_USD= request.POST.get('Charging_Cost_USD')
        Vehicle_Age_years= request.POST.get('Vehicle_Age_years')
        Charger_Type= request.POST.get('Charger_Type')
        User_Type= request.POST.get('User_Type')

        # Model Loading & Caching Logic
        if os.path.exists('ev_model.joblib'):
            print("Loading pre-trained ensemble model from cache...")
            serialized = joblib.load('ev_model.joblib')
            classifier = serialized['model']
            cv = serialized['cv']
        else:
            print("Model cache not found. Performing dynamic training fallback...")
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


            models = []
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.20)

            print("Quantile Regression Neural Network(QRNN)")

            from sklearn.neural_network import MLPClassifier
            mlpc = MLPClassifier().fit(X_train, y_train)
            models.append(('MLPClassifier', mlpc))

            # SVM Model
            print("SVM")
            from sklearn import svm

            lin_clf = svm.LinearSVC()
            lin_clf.fit(X_train, y_train)
            models.append(('svm', lin_clf))

            print("Logistic Regression")

            from sklearn.linear_model import LogisticRegression

            reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
            models.append(('logistic', reg))

            classifier = VotingClassifier(models)
            classifier.fit(X_train, y_train)

            # Save it so next runs are cached
            try:
                joblib.dump({'model': classifier, 'cv': cv}, 'ev_model.joblib')
            except Exception as e:
                print("Could not cache model:", e)

        Fid1 = [Fid]
        vector1 = cv.transform(Fid1).toarray()
        predict_text = classifier.predict(vector1)

        pred = str(predict_text).replace("[", "")
        pred1 = str(pred.replace("]", ""))

        prediction = int(pred1)

        if prediction == 0:
                val = 'Less'
        elif prediction == 1:
                val = 'More'

        print(prediction)
        print(val)

        predict_ev_energy_consumption.objects.create(
        Fid=Fid,
        Vehicle_Model=Vehicle_Model,
        Battery_Capacity_kWh=Battery_Capacity_kWh,
        Charging_Station_ID=Charging_Station_ID,
        Charging_Station_Location=Charging_Station_Location,
        Charging_Start_Time=Charging_Start_Time,
        Charging_EndTime=Charging_EndTime,
        Energy_Consumed_kWh=Energy_Consumed_kWh,
        Charging_Duration_hours=Charging_Duration_hours,
        Charging_Rate_kW=Charging_Rate_kW,
        Charging_Cost_USD=Charging_Cost_USD,
        Vehicle_Age_years=Vehicle_Age_years,
        Charger_Type=Charger_Type,
        User_Type=User_Type,
        Prediction=val)

        return render(request, 'RUser/Prediction_Of_EV_Energy_Consumption_Type.html',{'objs': val})
    return render(request, 'RUser/Prediction_Of_EV_Energy_Consumption_Type.html')



