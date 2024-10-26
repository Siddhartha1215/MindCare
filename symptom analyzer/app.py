from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearnex import patch_sklearn

patch_sklearn()

# Initialize Flask app
app = Flask(__name__)

# Load and preprocess data
DATA_PATH = "ui/Training.csv"
data = pd.read_csv(DATA_PATH).dropna(axis=1)

encoder = LabelEncoder()
data["prognosis"] = encoder.fit_transform(data["prognosis"])

X = data.iloc[:, :-1]
y = data.iloc[:, -1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=24)

# Initialize models
models = {
    "SVC": SVC(),
    "Gaussian NB": GaussianNB(),
    "Random Forest": RandomForestClassifier(random_state=18)
}

best_model = None
best_accuracy = 0

# Train models and select the best one
for model_name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model

# Create a symptom index for mapping
symptoms = X.columns.values
symptom_index = {" ".join([i.capitalize() for i in val.split("_")]): idx for idx, val in enumerate(symptoms)}

# Store the symptom index and classes
data_dict = {
    "symptom_index": symptom_index,
    "predictions_classes": encoder.classes_
}

# Prediction function
def predictDisease(symptoms):
    input_data = [0] * len(data_dict["symptom_index"])
    
    for symptom in symptoms:
        if symptom not in data_dict["symptom_index"]:
            return f"Symptom '{symptom}' not found."
        index = data_dict["symptom_index"][symptom]
        input_data[index] = 1
    
    input_data = np.array(input_data).reshape(1, -1)
    
    # Predict using the best model
    prediction = data_dict["predictions_classes"][best_model.predict(input_data)[0]]
    
    return prediction

# Route to display the symptom selection form
@app.route('/')
def index():
    return render_template('index.html', symptoms=data_dict["symptom_index"].keys())

# Route to handle the form submission
@app.route('/predict', methods=['POST'])
def predict():
    symptoms_selected = request.form.getlist('symptoms')  # Get selected symptoms
    if not symptoms_selected:
        return jsonify({"error": "No symptoms selected"}), 400
    
    prediction = predictDisease(symptoms_selected)
    return render_template('result.html', prediction=prediction)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
