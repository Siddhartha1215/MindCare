# Numpy and pandas for mathematical operations
import numpy as np
import pandas as pd
import csv
import re
from sklearn import preprocessing
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from flask import render_template, request, Blueprint

app = Blueprint('symptom', __name__, template_folder='templates')
training = pd.read_csv('symptom/ui/Training.csv')
cols= training.columns
cols= cols[:-1]
x = training[cols]
y = training['prognosis']
reduced_data = training.groupby(training['prognosis']).max()
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)
# x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)
clf1  = DecisionTreeClassifier()
clf = clf1.fit(x,y)
def check_pattern(dis_list,inp):
    pred_list=[]
    inp=inp.replace(' ','_')
    patt = f"{inp}"
    regexp = re.compile(patt)
    pred_list=[item for item in dis_list if regexp.search(item)]
    if(len(pred_list)>0):
        return 1,pred_list
    else:
        return 0,[]
    
def sec_predict(symptoms_exp):
    df = pd.read_csv('symptom/ui/Training.csv')
    X = df.iloc[:, :-1]
    y = df['prognosis']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=20)
    rf_clf = DecisionTreeClassifier()
    rf_clf.fit(X_train, y_train)
    symptoms_dict = {symptom: index for index, symptom in enumerate(X)}
    input_vector = np.zeros(len(symptoms_dict))
    for item in symptoms_exp:
      input_vector[[symptoms_dict[item]]] = 1
    return rf_clf.predict([input_vector])

def print_disease(node):
    node = node[0]
    val  = node.nonzero()
    disease = le.inverse_transform(val[0])
    return list(map(lambda x:x.strip(),list(disease)))

options=['itching', 'skin_rash','continuous_sneezing','shivering','joint_pain','stomach_pain','fatigue','high_fever','cough','sweating','dehydration','indigestion','chest_pain','muscle_pain']



def tree_to_code(tree, feature_names, disease_input):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    chk_dis = ",".join(feature_names).split(",")
    symptoms_present = []
    
    conf, cnf_dis = check_pattern(chk_dis, disease_input)
    if conf == 1:
        if len(cnf_dis) > 0:
            disease_input = cnf_dis[0]  # Automatically select the first suggestion for simplicity
        else:
            return "No disease found."

    symptoms_exp = []
    for syms in feature_name:
        if syms:  # Only ask about existing symptoms
            response = request.form.get(syms, 'no')
            if response.lower() == 'yes':
                symptoms_exp.append(syms)
    
    second_prediction = sec_predict(symptoms_exp)
    return second_prediction

@app.route('/symptom', methods=['GET', 'POST'])
def symptom():
    if request.method == 'POST':
        selected_symptom = request.form.get('symptom')
        if selected_symptom:
            return render_template('symptom_selection.html', selected_symptom=selected_symptom, options=options)

    return render_template('symptom.html', options=options)

@app.route('/predict', methods=['POST'])
def predict():
    print(request.form)
    selected_symptom = request.form.get('selected_symptom')
    additional_symptoms = request.form.getlist('additional_symptoms')
    
    # Combine selected symptom with additional symptoms
    all_symptoms = [selected_symptom] + additional_symptoms
    
    prediction = tree_to_code(clf, cols, ', '.join(all_symptoms))  # Make sure clf and cols are defined
    return render_template('result.html', prediction=prediction)
