import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import arff
import json
import numpy as np
import tensorflow
from tensorflow.keras import layers, models
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler

def get_data(): 
    for i in range(0, 3): 
        # with open(f'./Epilepsy/EpilepsyDimension{i+1}_TRAIN.arff', 'r') as file:
        #     data = arff.load(file)

        #     with open(f'seizure{i+1}.json', 'w') as json_file:
        #         json.dump(data["data"], json_file, indent=2)

        with open(f'./Epilepsy/EpilepsyDimension{i+1}_TEST.arff', 'r') as file:
            data = arff.load(file)

            with open(f'seizure{i+1}_test.json', 'w') as json_file:
                json.dump(data["data"], json_file, indent=2)

def parse_data():
    # with open('seizure1.json', 'r') as s1, open('seizure2.json', 'r') as s2, open('seizure3.json', 'r') as s3:
    #     seizure_data1 = json.load(s1)
    #     seizure_data2 = json.load(s2)
    #     seizure_data3 = json.load(s3)

    #     combined_data = []
    #     for line1, line2, line3 in zip(seizure_data1, seizure_data2, seizure_data3):
    #         if (line1[-1] == line2[-1] == line3[-1]):
    #             label = line1[-1]
    #             if (label != "EPILEPSY"):
    #                 label = "NORMAL"
    #             combined_data.append([line1[:-1], line2[:-1], line3[:-1], label])

    #     with open(f'seizure_data.json', 'w') as json_file:
    #             json.dump(combined_data, json_file, indent=1)

    
    with open('seizure1_test.json', 'r') as s1, open('seizure2_test.json', 'r') as s2, open('seizure3_test.json', 'r') as s3:
        seizure_data1 = json.load(s1)
        seizure_data2 = json.load(s2)
        seizure_data3 = json.load(s3)

        combined_data = []
        for line1, line2, line3 in zip(seizure_data1, seizure_data2, seizure_data3):
            if (line1[-1] == line2[-1] == line3[-1]):
                label = line1[-1]
                if (label != "EPILEPSY"):
                    label = "NORMAL"
                combined_data.append([line1[:-1], line2[:-1], line3[:-1], label])

        with open(f'seizure_data_test.json', 'w') as json_file:
                json.dump(combined_data, json_file)

def load_training_data(): 
    with open('seizure_data.json', 'r') as s: 
        data = json.load(s)
        X = np.array([np.column_stack((x,y,z)) for x,y,z,_ in data])

        le = LabelEncoder()
        y = le.fit_transform([label for _,_,_,label in data])
    
    return X, np.array(y)

def load_testing_data(): 
    with open('seizure_data_test.json', 'r') as s: 
        data = json.load(s)
        X = np.array([np.column_stack((x,y,z)) for x,y,z,_ in data])

        le = LabelEncoder()
        y = le.fit_transform([label for _,_,_,label in data])  
    return X, np.array(y)

def model(input_shape):
    model = models.Sequential()
    model.add(layers.Conv1D(64, 3, activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling1D(2))
    model.add(layers.Conv1D(128, 3, activation='relu'))
    model.add(layers.MaxPooling1D(2))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(1, activation='sigmoid'))
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model
    


if __name__ == "__main__":
    # get_data()
    # parse_data()
    X_train, y_train = load_training_data()
    X_test, y_test = load_testing_data()

    scaler = StandardScaler()
    X_train_reshaped = X_train.reshape(-1, 3)
    X_train_scaled = scaler.fit_transform(X_train_reshaped)
    X_train_scaled = X_train_scaled.reshape(X_train.shape)

    X_test_reshaped = X_test.reshape(-1, 3)
    X_test_scaled = scaler.fit_transform(X_test_reshaped)
    X_test_scaled = X_test_scaled.reshape(X_test.shape)
   
    cnn_model = model((X_train.shape[1], 3))
    cnn_model.fit(X_train_scaled, y_train,
        validation_split=0.2,
        epochs=100,
        batch_size=32,
        verbose=1
    )

    cnn_model.save('model_cnn.keras')

    y_pred = (cnn_model.predict(X_test_scaled) > 0.5).astype(int)
    
    print(f"Model Evaluation:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))


