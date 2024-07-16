import sys 
import os 
from PySide6 .QtWidgets import QApplication ,QMainWindow ,QWidget ,QHBoxLayout ,QSplitter ,QVBoxLayout ,QLabel ,QTabWidget ,QComboBox ,QGroupBox ,QCheckBox ,QPushButton ,QFileDialog ,QGridLayout ,QTextEdit ,QScrollArea ,QMessageBox ,QSizePolicy ,QSpinBox ,QStyleFactory 
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QTextOption ,QPalette ,QColor 
from matplotlib .backends .backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib .backends .backend_qt5agg import NavigationToolbar2QT as NavigationToolbar 
from matplotlib .figure import Figure 
import numpy as np 
import json 
from sklearn .ensemble import RandomForestClassifier ,GradientBoostingClassifier ,AdaBoostClassifier ,ExtraTreesClassifier 
from sklearn .model_selection import KFold 
from sklearn .metrics import confusion_matrix ,accuracy_score ,f1_score ,recall_score ,precision_score 
from lightgbm import LGBMClassifier 
from sklearn .neighbors import KNeighborsClassifier 
from sklearn .neural_network import MLPClassifier 
from sklearn .naive_bayes import GaussianNB 
from sklearn .tree import DecisionTreeClassifier 
from sklearn .linear_model import LogisticRegression 
from sklearn .preprocessing import LabelEncoder 
from sklearn .svm import SVC 
import torch 
import torch .nn as nn 
import torch .optim as optim 
from torch .utils .data import DataLoader ,TensorDataset 
import platform 
import pickle 
import tensorflow as tf 
from datetime import datetime 
if torch .cuda .is_available ():
    import cudf 
    import cuml 



def save_classifiers (classifiers ,save_path ):
    for classifier_name ,classifier_data in classifiers .items ():
        model =classifier_data ['model']

        if isinstance (model ,(tf .keras .Sequential ,tf .keras .Model )):

            file_name =f"{classifier_name}.h5"
            file_path =os .path .join (save_path ,file_name )
            model .save (file_path )
        elif classifier_name .startswith ("RAPIDS"):

            file_name =f"{classifier_name}.pkl"
            file_path =os .path .join (save_path ,file_name )
            with open (file_path ,'wb')as file :
                pickle .dump (model ,file )
        else :

            file_name =f"{classifier_name}.pkl"
            file_path =os .path .join (save_path ,file_name )
            with open (file_path ,'wb')as file :
                pickle .dump (model ,file )

def load_classifiers (classifier_files ):
    classifiers ={}
    for file_path in classifier_files :
        classifier_name =os .path .splitext (os .path .basename (file_path ))[0 ]

        if file_path .endswith (".h5"):

            model =tf .keras .models .load_model (file_path )
        elif file_path .endswith (".pkl"):

            with open (file_path ,'rb')as file :
                model =pickle .load (file )

        classifiers [classifier_name ]=model 

    return classifiers 

def load_data (npz_file_path ):
    with np .load (npz_file_path ,allow_pickle =True )as data :
        X =data ['X']
        settings =json .loads (data ['settings'].item ())
        label =settings .get ('ML_tag')
    return X ,label 

def prepare_data (npz_file_paths ):
    features =[]
    labels =[]
    min_events =float ('inf')

    for file_path in npz_file_paths :
        X ,label =load_data (file_path )
        min_events =min (min_events ,len (X ))

    for file_path in npz_file_paths :
        X ,label =load_data (file_path )
        if len (X )>min_events :
            indices =np .random .choice (len (X ),min_events ,replace =False )
            X =X [indices ]

        for event_features in X :
            event_features =np .nan_to_num (event_features ,nan =0.0 ,posinf =0.0 ,neginf =0.0 )
            features .append (event_features )
            labels .append (label )

    return np .array (features ),np .array (labels )


class Net (nn .Module ):
    def __init__ (self ,input_size ,hidden_size ,num_classes ):
        super (Net ,self ).__init__ ()
        self .fc1 =nn .Linear (input_size ,hidden_size )
        self .relu =nn .ReLU ()
        self .fc2 =nn .Linear (hidden_size ,num_classes )

    def forward (self ,x ):
        out =self .fc1 (x )
        out =self .relu (out )
        out =self .fc2 (out )
        return out 

def train_pytorch_model (X_train ,y_train ,input_size ,hidden_size ,num_classes ,num_epochs ,batch_size ,learning_rate ):
    label_encoder =LabelEncoder ()
    y_train_encoded =label_encoder .fit_transform (y_train )

    train_dataset =TensorDataset (torch .from_numpy (X_train ),torch .from_numpy (y_train_encoded ))
    train_loader =DataLoader (train_dataset ,batch_size =batch_size ,shuffle =True )

    model =Net (input_size ,hidden_size ,num_classes )

    criterion =nn .CrossEntropyLoss ()
    optimizer =optim .Adam (model .parameters (),lr =learning_rate )

    for epoch in range (num_epochs ):
        for batch_idx ,(data ,target )in enumerate (train_loader ):
            optimizer .zero_grad ()
            output =model (data .float ())
            loss =criterion (output ,target .long ())
            loss .backward ()
            optimizer .step ()

    return model 

def evaluate_pytorch_model (model ,X_test ,label_encoder ):
    model .eval ()
    with torch .no_grad ():
        inputs =torch .from_numpy (X_test .astype (np .float32 ))
        outputs =model (inputs )
        _ ,predicted =torch .max (outputs .data ,1 )
        y_pred_encoded =predicted .numpy ()
        y_pred =label_encoder .inverse_transform (y_pred_encoded )
    return y_pred 


def train_tensorflow_dnn_model (X ,y ,input_size ,hidden_size ,num_classes ,num_epochs ,batch_size ,learning_rate ):
    model =tf .keras .Sequential ([
    tf .keras .layers .Dense (hidden_size ,activation ='relu',input_shape =(input_size ,)),
    tf .keras .layers .Dense (hidden_size ,activation ='relu'),
    tf .keras .layers .Dense (num_classes ,activation ='softmax')
    ])

    model .compile (optimizer =tf .keras .optimizers .Adam (learning_rate =learning_rate ),
    loss ='sparse_categorical_crossentropy',
    metrics =['accuracy'])

    return model 


def train_tensorflow_cnn_model (X ,y ,input_size ,num_classes ,num_epochs ,batch_size ,learning_rate ):
    model =tf .keras .Sequential ([
    tf .keras .layers .Conv1D (filters =32 ,kernel_size =3 ,activation ='relu',input_shape =(input_size ,1 )),
    tf .keras .layers .MaxPooling1D (pool_size =2 ),
    tf .keras .layers .Conv1D (filters =64 ,kernel_size =3 ,activation ='relu'),
    tf .keras .layers .MaxPooling1D (pool_size =2 ),
    tf .keras .layers .Flatten (),
    tf .keras .layers .Dense (128 ,activation ='relu'),
    tf .keras .layers .Dense (num_classes ,activation ='softmax')
    ])

    model .compile (optimizer =tf .keras .optimizers .Adam (learning_rate =learning_rate ),
    loss ='sparse_categorical_crossentropy',
    metrics =['accuracy'])

    return model 


def train_tensorflow_rnn_model (X ,y ,input_size ,hidden_size ,num_layers ,num_classes ,num_epochs ,batch_size ,learning_rate ):
    model =tf .keras .Sequential ([
    tf .keras .layers .LSTM (hidden_size ,return_sequences =True ,input_shape =(1 ,input_size )),
    *[tf .keras .layers .LSTM (hidden_size ,return_sequences =True )for _ in range (num_layers -2 )],
    tf .keras .layers .LSTM (hidden_size ),
    tf .keras .layers .Dense (num_classes ,activation ='softmax')
    ])

    model .compile (optimizer =tf .keras .optimizers .Adam (learning_rate =learning_rate ),
    loss ='sparse_categorical_crossentropy',
    metrics =['accuracy'])

    return model 


def train_tensorflow_capsule_model (X ,y ,input_size ,num_classes ,num_epochs ,batch_size ,learning_rate ):
    input_layer =tf .keras .layers .Input (shape =(input_size ,))
    reshape_layer =tf .keras .layers .Reshape ((input_size ,1 ,1 ))(input_layer )
    conv1 =tf .keras .layers .Conv2D (filters =256 ,kernel_size =(input_size ,1 ),strides =1 ,activation ='relu')(reshape_layer )
    primary_caps =tf .keras .layers .Conv2D (filters =32 ,kernel_size =1 ,strides =1 ,activation ='relu')(conv1 )
    primary_caps =tf .keras .layers .Reshape (target_shape =(-1 ,8 ))(primary_caps )
    primary_caps =tf .keras .layers .Lambda (squash )(primary_caps )
    digit_caps =capsule_layer (num_capsules =num_classes ,dim_capsule =16 ,routings =3 )(primary_caps )
    output =tf .keras .layers .Lambda (lambda x :tf .sqrt (tf .reduce_sum (tf .square (x ),axis =-1 ,keepdims =True )))(digit_caps )
    output =tf .keras .layers .Reshape (target_shape =(-1 ,))(output )
    model =tf .keras .models .Model (inputs =input_layer ,outputs =output )
    model .compile (optimizer =tf .keras .optimizers .Adam (learning_rate =learning_rate ),
    loss ='sparse_categorical_crossentropy',
    metrics =['accuracy'])
    return model 


def squash (vectors ,axis =-1 ):
    s_squared_norm =tf .reduce_sum (tf .square (vectors ),axis =axis ,keepdims =True )
    scale =s_squared_norm /(1 +s_squared_norm )/tf .sqrt (s_squared_norm +1e-8 )
    return scale *vectors 


def capsule_layer (num_capsules ,dim_capsule ,routings =3 ):
    def capsule (inputs ):
        input_shape =tf .shape (inputs )
        inputs =tf .reshape (inputs ,(input_shape [0 ],input_shape [1 ],1 ,input_shape [2 ]))
        inputs =tf .tile (inputs ,[1 ,1 ,num_capsules ,1 ])
        inputs =tf .reshape (inputs ,(-1 ,input_shape [1 ],num_capsules ,dim_capsule ))

        b =tf .zeros_like (inputs [:,:,:,0 ])

        for i in range (routings ):
            c =tf .nn .softmax (b ,axis =1 )
            outputs =squash (tf .matmul (c ,inputs ))

            if i <routings -1 :
                b +=tf .matmul (outputs ,inputs ,transpose_b =True )

        return tf .reshape (outputs ,(-1 ,num_capsules ,dim_capsule ))

    return tf .keras .layers .Lambda (capsule )


def train_and_evaluate_classifiers (X ,y ,selected_classifiers ,k ,n_estimators ,random_state ,hidden_layer_sizes ,criterion ,n_jobs ,shuffle ,num_layers ,num_epochs ,batch_size ,learning_rate ):
    results ={}

    for classifier_name in selected_classifiers :
        if classifier_name =="Deep Neural Networks":

            label_encoder =LabelEncoder ()
            y =label_encoder .fit_transform (y )

            input_size =X .shape [1 ]
            num_classes =len (np .unique (y ))

            model =train_tensorflow_dnn_model (X ,y ,input_size ,hidden_layer_sizes [0 ],num_classes ,num_epochs ,batch_size ,learning_rate )


            kf =KFold (n_splits =k ,shuffle =shuffle ,random_state =random_state )
            accuracies =[]
            f1_scores =[]
            sensitivities =[]
            specificities =[]
            confusion_matrices =[]





            for train_index ,test_index in kf .split (X ):
                X_train ,X_test =X [train_index ],X [test_index ]
                y_train ,y_test =y [train_index ],y [test_index ]

                model .fit (X_train ,y_train ,epochs =num_epochs ,batch_size =batch_size ,verbose =0 )
                y_pred =np .argmax (model .predict (X_test ),axis =1 )

                accuracy =accuracy_score (y_test ,y_pred )
                accuracies .append (accuracy )

                f1 =f1_score (y_test ,y_pred ,average ='weighted')
                f1_scores .append (f1 )

                sensitivity =recall_score (y_test ,y_pred ,average ='weighted')
                sensitivities .append (sensitivity )

                specificity =precision_score (y_test ,y_pred ,average ='weighted')
                specificities .append (specificity )

                cm =confusion_matrix (y_test ,y_pred )
                confusion_matrices .append (cm )

            avg_accuracy =np .mean (accuracies )
            avg_f1_score =np .mean (f1_scores )
            avg_sensitivity =np .mean (sensitivities )
            avg_specificity =np .mean (specificities )
            avg_confusion_matrix =np .mean (confusion_matrices ,axis =0 )

            results [classifier_name ]={
            'model':model ,
            'avg_accuracy':avg_accuracy ,
            'avg_f1_score':avg_f1_score ,
            'avg_sensitivity':avg_sensitivity ,
            'avg_specificity':avg_specificity ,
            'avg_confusion_matrix':avg_confusion_matrix 
            }

        elif classifier_name =="Convolutional Neural Networks":
            label_encoder =LabelEncoder ()
            y =label_encoder .fit_transform (y )

            input_size =X .shape [1 ]
            num_classes =len (np .unique (y ))

            model =train_tensorflow_cnn_model (X ,y ,input_size ,num_classes ,num_epochs ,batch_size ,learning_rate )


            kf =KFold (n_splits =k ,shuffle =shuffle ,random_state =random_state )
            accuracies =[]
            f1_scores =[]
            sensitivities =[]
            specificities =[]
            confusion_matrices =[]

            for train_index ,test_index in kf .split (X ):
                X_train ,X_test =X [train_index ],X [test_index ]
                y_train ,y_test =y [train_index ],y [test_index ]

                model .fit (X_train .reshape (-1 ,input_size ,1 ),y_train ,epochs =num_epochs ,batch_size =batch_size ,verbose =0 )
                y_pred =np .argmax (model .predict (X_test .reshape (-1 ,input_size ,1 )),axis =1 )

                accuracy =accuracy_score (y_test ,y_pred )
                accuracies .append (accuracy )

                f1 =f1_score (y_test ,y_pred ,average ='weighted')
                f1_scores .append (f1 )

                sensitivity =recall_score (y_test ,y_pred ,average ='weighted')
                sensitivities .append (sensitivity )

                specificity =precision_score (y_test ,y_pred ,average ='weighted')
                specificities .append (specificity )

                cm =confusion_matrix (y_test ,y_pred )
                confusion_matrices .append (cm )

            avg_accuracy =np .mean (accuracies )
            avg_f1_score =np .mean (f1_scores )
            avg_sensitivity =np .mean (sensitivities )
            avg_specificity =np .mean (specificities )
            avg_confusion_matrix =np .mean (confusion_matrices ,axis =0 )

            results [classifier_name ]={
            'model':model ,
            'avg_accuracy':avg_accuracy ,
            'avg_f1_score':avg_f1_score ,
            'avg_sensitivity':avg_sensitivity ,
            'avg_specificity':avg_specificity ,
            'avg_confusion_matrix':avg_confusion_matrix 
            }

        elif classifier_name =="Recurrent Neural Networks":
            label_encoder =LabelEncoder ()
            y =label_encoder .fit_transform (y )

            input_size =X .shape [1 ]
            hidden_size =hidden_layer_sizes [0 ]
            num_classes =len (np .unique (y ))

            model =train_tensorflow_rnn_model (X ,y ,input_size ,hidden_size ,num_layers ,num_classes ,num_epochs ,batch_size ,learning_rate )


            kf =KFold (n_splits =k ,shuffle =shuffle ,random_state =random_state )
            accuracies =[]
            f1_scores =[]
            sensitivities =[]
            specificities =[]
            confusion_matrices =[]

            for train_index ,test_index in kf .split (X ):
                X_train ,X_test =X [train_index ],X [test_index ]
                y_train ,y_test =y [train_index ],y [test_index ]

                model .fit (X_train .reshape (-1 ,1 ,input_size ),y_train ,epochs =num_epochs ,batch_size =batch_size ,verbose =0 )
                y_pred =np .argmax (model .predict (X_test .reshape (-1 ,1 ,input_size )),axis =1 )

                accuracy =accuracy_score (y_test ,y_pred )
                accuracies .append (accuracy )

                f1 =f1_score (y_test ,y_pred ,average ='weighted')
                f1_scores .append (f1 )

                sensitivity =recall_score (y_test ,y_pred ,average ='weighted')
                sensitivities .append (sensitivity )

                specificity =precision_score (y_test ,y_pred ,average ='weighted')
                specificities .append (specificity )

                cm =confusion_matrix (y_test ,y_pred )
                confusion_matrices .append (cm )

            avg_accuracy =np .mean (accuracies )
            avg_f1_score =np .mean (f1_scores )
            avg_sensitivity =np .mean (sensitivities )
            avg_specificity =np .mean (specificities )
            avg_confusion_matrix =np .mean (confusion_matrices ,axis =0 )

            results [classifier_name ]={
            'model':model ,
            'avg_accuracy':avg_accuracy ,
            'avg_f1_score':avg_f1_score ,
            'avg_sensitivity':avg_sensitivity ,
            'avg_specificity':avg_specificity ,
            'avg_confusion_matrix':avg_confusion_matrix 
            }

        elif classifier_name =="Capsule Networks":
            label_encoder =LabelEncoder ()
            y =label_encoder .fit_transform (y )

            input_size =X .shape [1 ]
            num_classes =len (np .unique (y ))

            model =train_tensorflow_capsule_model (X ,y ,input_size ,num_classes ,num_epochs ,batch_size ,learning_rate )


            kf =KFold (n_splits =k ,shuffle =shuffle ,random_state =random_state )
            accuracies =[]
            f1_scores =[]
            sensitivities =[]
            specificities =[]
            confusion_matrices =[]

            for train_index ,test_index in kf .split (X ):
                X_train ,X_test =X [train_index ],X [test_index ]
                y_train ,y_test =y [train_index ],y [test_index ]

                model .fit (X_train ,y_train ,epochs =num_epochs ,batch_size =batch_size ,verbose =0 )
                y_pred =np .argmax (model .predict (X_test ),axis =1 )

                accuracy =accuracy_score (y_test ,y_pred )
                accuracies .append (accuracy )

                f1 =f1_score (y_test ,y_pred ,average ='weighted')
                f1_scores .append (f1 )

                sensitivity =recall_score (y_test ,y_pred ,average ='weighted')
                sensitivities .append (sensitivity )

                specificity =precision_score (y_test ,y_pred ,average ='weighted')
                specificities .append (specificity )

                cm =confusion_matrix (y_test ,y_pred )
                confusion_matrices .append (cm )

            avg_accuracy =np .mean (accuracies )
            avg_f1_score =np .mean (f1_scores )
            avg_sensitivity =np .mean (sensitivities )
            avg_specificity =np .mean (specificities )
            avg_confusion_matrix =np .mean (confusion_matrices ,axis =0 )

            results [classifier_name ]={
            'model':model ,
            'avg_accuracy':avg_accuracy ,
            'avg_f1_score':avg_f1_score ,
            'avg_sensitivity':avg_sensitivity ,
            'avg_specificity':avg_specificity ,
            'avg_confusion_matrix':avg_confusion_matrix 
            }

        elif classifier_name .startswith ("RAPIDS"):

            if classifier_name =="RAPIDS RandomForestClassifier":
                classifier =cuml .ensemble .RandomForestClassifier (n_estimators =n_estimators ,random_state =random_state ,n_jobs =n_jobs )
            elif classifier_name =="RAPIDS GradientBoostingClassifier":
                classifier =cuml .ensemble .GradientBoostingClassifier (n_estimators =n_estimators ,random_state =random_state )
            elif classifier_name =="RAPIDS XGBoostClassifier":
                classifier =cuml .XGBClassifier (n_estimators =n_estimators ,random_state =random_state ,n_jobs =n_jobs )


            kf =KFold (n_splits =k ,shuffle =shuffle ,random_state =random_state )
            accuracies =[]
            f1_scores =[]
            sensitivities =[]
            specificities =[]
            confusion_matrices =[]
            feature_importances_list =[]

            for train_index ,test_index in kf .split (X ):
                X_train ,X_test =X [train_index ],X [test_index ]
                y_train ,y_test =y [train_index ],y [test_index ]

                classifier .fit (X_train ,y_train )
                y_pred =classifier .predict (X_test )

                accuracy =accuracy_score (y_test ,y_pred )
                accuracies .append (accuracy )

                f1 =f1_score (y_test ,y_pred ,average ='weighted')
                f1_scores .append (f1 )

                sensitivity =recall_score (y_test ,y_pred ,average ='weighted')
                sensitivities .append (sensitivity )

                specificity =precision_score (y_test ,y_pred ,average ='weighted')
                specificities .append (specificity )

                cm =confusion_matrix (y_test ,y_pred )
                confusion_matrices .append (cm )

                if hasattr (classifier ,'feature_importances_'):
                    feature_importances_list .append (classifier .feature_importances_ )

            avg_accuracy =np .mean (accuracies )
            avg_f1_score =np .mean (f1_scores )
            avg_sensitivity =np .mean (sensitivities )
            avg_specificity =np .mean (specificities )
            avg_confusion_matrix =np .mean (confusion_matrices ,axis =0 )

            if feature_importances_list :
                avg_feature_importances =np .mean (feature_importances_list ,axis =0 )
            else :
                avg_feature_importances =None 

            results [classifier_name ]={
            'model':classifier ,
            'avg_accuracy':avg_accuracy ,
            'avg_f1_score':avg_f1_score ,
            'avg_sensitivity':avg_sensitivity ,
            'avg_specificity':avg_specificity ,
            'avg_confusion_matrix':avg_confusion_matrix ,
            'avg_feature_importances':avg_feature_importances 
            }

        else :

            classifier ={
            "RandomForestClassifier":RandomForestClassifier (n_estimators =n_estimators ,random_state =random_state ,n_jobs =n_jobs ,criterion =criterion ),
            "GradientBoostingClassifier":GradientBoostingClassifier (n_estimators =n_estimators ,random_state =random_state ),
            "LGBMClassifier":LGBMClassifier (n_estimators =n_estimators ,random_state =random_state ,n_jobs =n_jobs ),
            "AdaBoostClassifier":AdaBoostClassifier (n_estimators =n_estimators ,random_state =random_state ),
            "DecisionTreeClassifier":DecisionTreeClassifier (random_state =random_state ,criterion =criterion ),
            "ExtraTreesClassifier":ExtraTreesClassifier (n_estimators =n_estimators ,random_state =random_state ,n_jobs =n_jobs ,criterion =criterion ),
            "SVC":SVC (kernel ='rbf',random_state =random_state ),
            "KNeighborsClassifier":KNeighborsClassifier (n_neighbors =5 ),
            "LogisticRegression":LogisticRegression (random_state =random_state ),
            "GaussianNB":GaussianNB (),
            "MLPClassifier":MLPClassifier (hidden_layer_sizes =(100 ,),random_state =random_state )
            }[classifier_name ]


            kf =KFold (n_splits =k ,shuffle =shuffle ,random_state =random_state )
            accuracies =[]
            f1_scores =[]
            sensitivities =[]
            specificities =[]
            confusion_matrices =[]
            feature_importances_list =[]
            y_true_all =[]
            y_pred_all =[]

            for train_index ,test_index in kf .split (X ):
                X_train ,X_test =X [train_index ],X [test_index ]
                y_train ,y_test =y [train_index ],y [test_index ]

                classifier .fit (X_train ,y_train )
                y_pred =classifier .predict (X_test )

                accuracy =accuracy_score (y_test ,y_pred )
                accuracies .append (accuracy )

                f1 =f1_score (y_test ,y_pred ,average ='weighted')
                f1_scores .append (f1 )

                sensitivity =recall_score (y_test ,y_pred ,average ='weighted')
                sensitivities .append (sensitivity )

                specificity =precision_score (y_test ,y_pred ,average ='weighted')
                specificities .append (specificity )

                y_true_all .extend (y_test )
                y_pred_all .extend (y_pred )




                if hasattr (classifier ,'feature_importances_'):
                    feature_importances_list .append (classifier .feature_importances_ )
                elif hasattr (classifier ,'coef_'):
                    feature_importances_list .append (classifier .coef_ .ravel ())

            avg_accuracy =np .mean (accuracies )
            avg_f1_score =np .mean (f1_scores )
            avg_sensitivity =np .mean (sensitivities )
            avg_specificity =np .mean (specificities )

            avg_confusion_matrix =confusion_matrix (y_true_all ,y_pred_all )

            if feature_importances_list :
                avg_feature_importances =np .abs (np .mean (feature_importances_list ,axis =0 ))
            else :
                avg_feature_importances =None 

            results [classifier_name ]={
            'model':classifier ,
            'avg_accuracy':avg_accuracy ,
            'avg_f1_score':avg_f1_score ,
            'avg_sensitivity':avg_sensitivity ,
            'avg_specificity':avg_specificity ,
            'avg_confusion_matrix':avg_confusion_matrix ,
            'avg_feature_importances':avg_feature_importances 
            }

    return results 

class ResultsWidget (QWidget ):
    def __init__ (self ,classifier_name ):
        super ().__init__ ()

        layout =QGridLayout (self )


        self .confusion_matrix_plot =FigureCanvas (Figure (figsize =(5 ,5 )))
        self .confusion_matrix_toolbar =NavigationToolbar (self .confusion_matrix_plot ,self )
        layout .addWidget (self .confusion_matrix_plot ,0 ,0 )
        layout .addWidget (self .confusion_matrix_toolbar ,1 ,0 )

        self .feature_importance_plot =FigureCanvas (Figure (figsize =(5 ,5 )))
        self .feature_importance_toolbar =NavigationToolbar (self .feature_importance_plot ,self )
        layout .addWidget (self .feature_importance_plot ,0 ,1 )
        layout .addWidget (self .feature_importance_toolbar ,1 ,1 )

        self .test_confusion_matrix_plot =FigureCanvas (Figure (figsize =(5 ,5 )))
        self .test_confusion_matrix_toolbar =NavigationToolbar (self .test_confusion_matrix_plot ,self )
        layout .addWidget (self .test_confusion_matrix_plot ,2 ,0 )
        layout .addWidget (self .test_confusion_matrix_toolbar ,3 ,0 )


        self .info_text_edit =QTextEdit ()
        self .info_text_edit .setReadOnly (True )
        self .info_text_edit .setWordWrapMode (QTextOption .WrapMode .WrapAtWordBoundaryOrAnywhere )
        layout .addWidget (self .info_text_edit ,2 ,1 )

    def update_plots (self ,confusion_matrix ,feature_importances ,test_confusion_matrix ,labels ):


        if confusion_matrix is not None :
            self .confusion_matrix_plot .figure .clear ()
            ax =self .confusion_matrix_plot .figure .add_subplot (111 )

            confusion_matrix_norm =confusion_matrix .astype ('float')/confusion_matrix .sum (axis =1 )[:,np .newaxis ]

            im =ax .imshow (confusion_matrix_norm ,cmap ='Blues',interpolation ='nearest')
            ax .set_title ("Average Confusion Matrix")
            ax .set_xlabel ("Predicted Label")
            ax .set_ylabel ("True Label")
            ax .set_xticks (np .arange (len (labels )))
            ax .set_yticks (np .arange (len (labels )))
            ax .set_xticklabels (labels )
            ax .set_yticklabels (labels )


            for i in range (len (labels )):
                for j in range (len (labels )):
                    ax .text (j ,i ,f"{confusion_matrix_norm[i, j]*100:.1f}%",ha ='center',va ='center',color ='black')

            self .confusion_matrix_plot .figure .colorbar (im )
            self .confusion_matrix_plot .draw ()
        elif self .confusion_matrix_plot .figure .get_axes ():
            pass 


        if feature_importances is not None :
            self .feature_importance_plot .figure .clear ()
            ax =self .feature_importance_plot .figure .add_subplot (111 )
            ax .bar (range (len (feature_importances )),feature_importances )
            ax .set_title ("Feature Importances")
            ax .set_xlabel ("Feature")
            ax .set_ylabel ("Importance")
            self .feature_importance_plot .draw ()
        elif self .feature_importance_plot .figure .get_axes ():
            pass 


        self .test_confusion_matrix_plot .figure .clear ()
        ax =self .test_confusion_matrix_plot .figure .add_subplot (111 )

        if test_confusion_matrix is not None :

            test_confusion_matrix_norm =test_confusion_matrix .astype ('float')/test_confusion_matrix .sum (axis =1 )[:,np .newaxis ]
            test_confusion_matrix_norm =np .nan_to_num (test_confusion_matrix_norm ,nan =0.0 )

            im =ax .imshow (test_confusion_matrix_norm ,cmap ='Blues',interpolation ='nearest')
            ax .set_title ("Test Confusion Matrix")
            ax .set_xlabel ("Predicted Label")
            ax .set_ylabel ("True Label")
            ax .set_xticks (np .arange (len (labels )))
            ax .set_yticks (np .arange (len (labels )))
            ax .set_xticklabels (labels )
            ax .set_yticklabels (labels )


            for i in range (len (labels )):
                for j in range (len (labels )):
                    ax .text (j ,i ,f"{test_confusion_matrix_norm[i, j]*100:.1f}%",ha ='center',va ='center',color ='black')

            self .test_confusion_matrix_plot .figure .colorbar (im )
        else :
            ax .text (0.5 ,0.5 ,"Test confusion matrix not available",horizontalalignment ='center',verticalalignment ='center')
        self .test_confusion_matrix_plot .draw ()

    def update_info (self ,info_text ):
        self .info_text_edit .append (info_text )

class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("SD ML Training and Testing Tool")


        main_widget =QWidget ()
        main_layout =QHBoxLayout (main_widget )
        self .setCentralWidget (main_widget )


        splitter =QSplitter ()
        main_layout .addWidget (splitter )


        left_widget =QWidget ()
        right_widget =QWidget ()
        splitter .addWidget (left_widget )
        splitter .addWidget (right_widget )
        splitter .setSizes ([300 ,700 ])


        left_layout =QVBoxLayout (left_widget )

        self .app_name_label =QLabel ("SD ML Training and Testing Tool")
        self .app_name_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .app_name_label .setStyleSheet ("font-size: 22px; font-weight: bold;")
        self .app_name_label .setWordWrap (True )
        left_layout .addWidget (self .app_name_label )
        self .email_label =QLabel ("shankar.dutt@anu.edu.au")
        self .email_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .email_label .setWordWrap (True )
        left_layout .addWidget (self .email_label )
        left_tab_widget =QTabWidget ()
        left_layout .addWidget (left_tab_widget )


        general_tab =QWidget ()
        general_tab_layout =QVBoxLayout (general_tab )
        settings_tab =QWidget ()
        settings_tab_layout =QVBoxLayout (settings_tab )
        left_tab_widget .addTab (general_tab ,"General")
        left_tab_widget .addTab (settings_tab ,"Settings")


        general_scroll_area =QScrollArea ()
        general_scroll_area .setWidgetResizable (True )
        general_scroll_widget =QWidget ()
        general_scroll_area .setWidget (general_scroll_widget )
        general_layout =QVBoxLayout (general_scroll_widget )
        general_tab_layout .addWidget (general_scroll_area )


        self .classifier_type_combo =QComboBox ()
        self .classifier_type_combo .addItem ("Train New Classifier")
        self .classifier_type_combo .addItem ("Load Trained Classifier")
        general_layout .addWidget (self .classifier_type_combo )

        self .training_sets_group =QGroupBox ("Training Sets")
        training_sets_layout =QVBoxLayout ()
        self .num_training_sets_combo =QComboBox ()
        for i in range (2 ,11 ):
            self .num_training_sets_combo .addItem (str (i ))
        training_sets_layout .addWidget (self .num_training_sets_combo )
        self .training_file_buttons =[]
        self .training_file_labels =[]
        training_sets_layout .addStretch (1 )
        self .training_sets_group .setLayout (training_sets_layout )
        general_layout .addWidget (self .training_sets_group )

        self .classifier_group =QGroupBox ("Classifier Options")
        classifier_layout =QVBoxLayout ()
        self .classifier_checkboxes =[]
        classifier_layout .addStretch (1 )
        self .classifier_group .setLayout (classifier_layout )
        general_layout .addWidget (self .classifier_group )

        self .save_classifier_checkbox =QCheckBox ("Save Trained Classifier")
        general_layout .addWidget (self .save_classifier_checkbox )

        self .train_button =QPushButton ("Train Classifier")
        general_layout .addWidget (self .train_button )

        self .test_group =QGroupBox ("Testing")
        test_layout =QVBoxLayout ()
        self .select_test_button =QPushButton ("Select Test/Unknown Dataset")
        test_layout .addWidget (self .select_test_button )

        self .test_file_label =QTextEdit ()
        self .test_file_label .setReadOnly (True )
        self .test_file_label .setWordWrapMode (QTextOption .WrapMode .WrapAtWordBoundaryOrAnywhere )
        self .test_file_label .setFixedHeight (60 )
        test_layout .addWidget (self .test_file_label )

        self .perform_test_button =QPushButton ("Perform Test")
        test_layout .addWidget (self .perform_test_button )
        test_layout .addStretch (1 )
        self .test_group .setLayout (test_layout )
        general_layout .addWidget (self .test_group )


        general_settings_group =QGroupBox ("General Settings")
        cpu_settings_group =QGroupBox ("CPU Settings")
        gpu_settings_group =QGroupBox ("GPU Settings")


        general_settings_layout =QVBoxLayout ()
        cpu_settings_layout =QVBoxLayout ()
        gpu_settings_layout =QVBoxLayout ()


        general_settings_layout .addWidget (QLabel ("Number of K-Fold Cross Validation:"))
        self .k_fold_combo =QComboBox ()
        for i in range (2 ,11 ):
            self .k_fold_combo .addItem (str (i ))
        self .k_fold_combo .setCurrentText ("5")
        general_settings_layout .addWidget (self .k_fold_combo )

        general_settings_layout .addWidget (QLabel ("Random State:"))
        self .random_state_spinbox =QSpinBox ()
        self .random_state_spinbox .setMinimum (0 )
        self .random_state_spinbox .setMaximum (100000 )
        self .random_state_spinbox .setValue (42 )
        general_settings_layout .addWidget (self .random_state_spinbox )

        general_settings_layout .addWidget (QLabel ("Shuffle:"))
        self .shuffle_combo =QComboBox ()
        self .shuffle_combo .addItem ("True")
        self .shuffle_combo .addItem ("False")
        self .shuffle_combo .setCurrentText ("True")
        general_settings_layout .addWidget (self .shuffle_combo )

        general_settings_group .setLayout (general_settings_layout )


        cpu_settings_layout .addWidget (QLabel ("Number of Estimators:"))
        self .num_estimators_combo =QComboBox ()
        self .num_estimators_combo .addItem ("100")
        self .num_estimators_combo .addItem ("500")
        self .num_estimators_combo .addItem ("1000")
        self .num_estimators_combo .setCurrentText ("1000")
        cpu_settings_layout .addWidget (self .num_estimators_combo )

        cpu_settings_layout .addWidget (QLabel ("Criterion:"))
        self .criterion_combo =QComboBox ()
        self .criterion_combo .addItem ("gini")
        self .criterion_combo .addItem ("entropy")
        self .criterion_combo .setCurrentText ("gini")
        cpu_settings_layout .addWidget (self .criterion_combo )

        cpu_settings_layout .addWidget (QLabel ("Number of Jobs:"))
        self .n_jobs_combo =QComboBox ()
        self .n_jobs_combo .addItem ("1")
        self .n_jobs_combo .addItem ("2")
        self .n_jobs_combo .addItem ("4")
        self .n_jobs_combo .addItem ("-1")
        self .n_jobs_combo .setCurrentText ("-1")
        cpu_settings_layout .addWidget (self .n_jobs_combo )

        cpu_settings_group .setLayout (cpu_settings_layout )


        gpu_settings_layout .addWidget (QLabel ("Hidden Layer Sizes:"))
        self .hidden_layer_sizes_spinbox =QSpinBox ()
        self .hidden_layer_sizes_spinbox .setMinimum (1 )
        self .hidden_layer_sizes_spinbox .setMaximum (10000 )
        self .hidden_layer_sizes_spinbox .setValue (1000 )
        gpu_settings_layout .addWidget (self .hidden_layer_sizes_spinbox )

        gpu_settings_layout .addWidget (QLabel ("Number of Layers:"))
        self .num_layers_spinbox =QSpinBox ()
        self .num_layers_spinbox .setMinimum (1 )
        self .num_layers_spinbox .setMaximum (10 )
        self .num_layers_spinbox .setValue (2 )
        gpu_settings_layout .addWidget (self .num_layers_spinbox )

        gpu_settings_layout .addWidget (QLabel ("Number of Epochs:"))
        self .num_epochs_spinbox =QSpinBox ()
        self .num_epochs_spinbox .setMinimum (1 )
        self .num_epochs_spinbox .setMaximum (1000 )
        self .num_epochs_spinbox .setValue (50 )
        gpu_settings_layout .addWidget (self .num_epochs_spinbox )

        gpu_settings_layout .addWidget (QLabel ("Batch Size:"))
        self .batch_size_spinbox =QSpinBox ()
        self .batch_size_spinbox .setMinimum (1 )
        self .batch_size_spinbox .setMaximum (1000 )
        self .batch_size_spinbox .setValue (32 )
        gpu_settings_layout .addWidget (self .batch_size_spinbox )

        gpu_settings_layout .addWidget (QLabel ("Learning Rate:"))
        self .learning_rate_combo =QComboBox ()
        self .learning_rate_combo .addItem ("0.001")
        self .learning_rate_combo .addItem ("0.01")
        self .learning_rate_combo .addItem ("0.1")
        self .learning_rate_combo .setCurrentText ("0.001")
        gpu_settings_layout .addWidget (self .learning_rate_combo )

        gpu_settings_group .setLayout (gpu_settings_layout )


        settings_tab_layout .addWidget (general_settings_group )
        settings_tab_layout .addWidget (cpu_settings_group )
        settings_tab_layout .addWidget (gpu_settings_group )
        settings_tab_layout .addStretch (1 )


        right_layout =QVBoxLayout (right_widget )
        self .right_tab_widget =QTabWidget ()
        scroll_area =QScrollArea ()
        scroll_area .setWidgetResizable (True )
        scroll_area .setWidget (self .right_tab_widget )
        right_layout .addWidget (scroll_area )


        self .classifier_type_combo .currentIndexChanged .connect (self .update_classifier_options )
        self .num_training_sets_combo .currentIndexChanged .connect (self .update_training_file_buttons )
        self .train_button .clicked .connect (self .train_classifier )
        self .select_test_button .clicked .connect (self .select_test_dataset )
        self .perform_test_button .clicked .connect (self .perform_test )


        self .update_classifier_options ()
        self .update_training_file_buttons ()


        self .trained_classifiers ={}
        self .loaded_classifiers ={}

    def update_classifier_options (self ):
        classifier_type =self .classifier_type_combo .currentText ()


        for checkbox in self .classifier_checkboxes :
            checkbox .deleteLater ()
        self .classifier_checkboxes .clear ()


        if classifier_type =="Train New Classifier":
            self .training_sets_group .setTitle ("Training Sets")
            self .save_classifier_checkbox .setVisible (True )
            self .train_button .setVisible (True )
            self .classifier_group .setVisible (True )


            self .num_training_sets_combo .clear ()
            for i in range (2 ,11 ):
                self .num_training_sets_combo .addItem (str (i ))
            self .num_training_sets_combo .setCurrentIndex (0 )

        else :
            self .training_sets_group .setTitle ("Trained Classifiers")
            self .save_classifier_checkbox .setVisible (False )
            self .train_button .setVisible (False )
            self .classifier_group .setVisible (False )


            self .num_training_sets_combo .clear ()
            for i in range (1 ,11 ):
                self .num_training_sets_combo .addItem (str (i ))
            self .num_training_sets_combo .setCurrentIndex (0 )


        if classifier_type =="Train New Classifier":

            cpu_classifiers =[
            "RandomForestClassifier",
            "GradientBoostingClassifier",
            "LGBMClassifier",
            "AdaBoostClassifier",
            "DecisionTreeClassifier",
            "ExtraTreesClassifier",
            "SVC",
            "KNeighborsClassifier",
            "LogisticRegression",
            "GaussianNB",
            "MLPClassifier"
            ]


            tensor_classifiers =[
            "Deep Neural Networks",
            "Convolutional Neural Networks",
            "Recurrent Neural Networks",
            "Capsule Networks"
            ]


            gpu_classifiers =[]
            if torch .cuda .is_available ():
                gpu_classifiers =[
                "RAPIDS RandomForestClassifier",
                "RAPIDS GradientBoostingClassifier",
                "RAPIDS XGBoostClassifier"
                ]


            cpu_group =QGroupBox ("CPU-based Classifiers")
            cpu_layout =QVBoxLayout ()
            for classifier in cpu_classifiers :
                checkbox =QCheckBox (classifier )
                self .classifier_checkboxes .append (checkbox )
                cpu_layout .addWidget (checkbox )
            cpu_group .setLayout (cpu_layout )

            tensor_group =QGroupBox ("Tensorflow-based Classifiers (GPU/CPU based on the system)")
            tensor_layout =QVBoxLayout ()
            for classifier in tensor_classifiers :
                checkbox =QCheckBox (classifier )
                self .classifier_checkboxes .append (checkbox )
                tensor_layout .addWidget (checkbox )
            tensor_group .setLayout (tensor_layout )

            gpu_group =QGroupBox ("Nvidia GPU-based Classifiers (RAPIDS)")
            gpu_layout =QVBoxLayout ()
            for classifier in gpu_classifiers :
                checkbox =QCheckBox (classifier )
                self .classifier_checkboxes .append (checkbox )
                gpu_layout .addWidget (checkbox )
            gpu_group .setLayout (gpu_layout )


            self .classifier_group .layout ().addWidget (cpu_group )
            self .classifier_group .layout ().addWidget (tensor_group )
            self .classifier_group .layout ().addWidget (gpu_group )
            self .classifier_group .layout ().addStretch (1 )

        self .update_training_file_buttons ()

    def update_training_file_buttons (self ):
        current_text =self .num_training_sets_combo .currentText ()
        if current_text :
            num_sets =int (current_text )
        else :
            num_sets =0 


        for button in self .training_file_buttons :
            button .deleteLater ()
        for label in self .training_file_labels :
            label .deleteLater ()

        self .training_file_buttons .clear ()
        self .training_file_labels .clear ()


        for i in range (num_sets ):
            if self .classifier_type_combo .currentText ()=="Train New Classifier":
                button =QPushButton (f"Select Training File {i+1}")
                button .clicked .connect (lambda _ ,idx =i :self .select_training_file (idx ))
            else :
                button =QPushButton (f"Select Trained Classifier {i+1}")
                button .setProperty ("index",i )
                button .clicked .connect (self .select_trained_classifier )

            self .training_file_buttons .append (button )

            label =QTextEdit ()
            self .training_file_labels .append (label )


        for button ,label in zip (self .training_file_buttons ,self .training_file_labels ):
            self .training_sets_group .layout ().insertWidget (self .training_sets_group .layout ().count ()-1 ,button )
            self .training_sets_group .layout ().insertWidget (self .training_sets_group .layout ().count ()-1 ,label )

    def select_trained_classifier (self ):
        button =self .sender ()
        index =button .property ("index")
        file_dialog =QFileDialog ()
        file_path ,_ =file_dialog .getOpenFileName (self ,"Select Trained Classifier","","Classifier Files (*.pkl *.h5)")
        if file_path :
            classifier_name =os .path .splitext (os .path .basename (file_path ))[0 ]
            file_extension =os .path .splitext (file_path )[1 ]

            try :
                if file_extension ==".h5":

                    classifier =tf .keras .models .load_model (file_path )
                else :

                    with open (file_path ,'rb')as file :
                        classifier =pickle .load (file )


                if not (hasattr (classifier ,'predict')or hasattr (classifier ,'predict_proba')):
                    raise ValueError ("Invalid classifier object")

                self .loaded_classifiers [classifier_name ]=classifier 
                self .update_loaded_classifiers_info (file_path ,index )
            except (IOError ,pickle .UnpicklingError ,ValueError )as e :
                QMessageBox .critical (self ,"Error",f"Failed to load classifier: {str(e)}")

    def update_loaded_classifiers_info (self ,file_path ,index ):
        self .training_file_labels [index ].clear ()
        self .training_file_labels [index ].append (f"Classifier: {os.path.splitext(os.path.basename(file_path))[0]}")
        self .training_file_labels [index ].append (f"File Path: {file_path}")
        self .training_file_labels [index ].setReadOnly (True )
        self .training_file_labels [index ].setWordWrapMode (QTextOption .WrapMode .WrapAtWordBoundaryOrAnywhere )


    def perform_test (self ):
        if self .classifier_type_combo .currentText ()=="Load Trained Classifier":
            if not hasattr (self ,'loaded_classifiers'):
                QMessageBox .warning (self ,"Warning","No classifiers were loaded.")
                return 
            classifiers =self .loaded_classifiers 
        else :
            classifiers =self .trained_classifiers 
            if not classifiers :
                QMessageBox .warning (self ,"Warning","No classifiers were trained.")
                return 

        if hasattr (self ,'test_file_path'):
            X_test ,y_test_true =load_data (self .test_file_path )

            X_test =np .nan_to_num (X_test ,nan =0.0 )

            for classifier_name ,classifier in classifiers .items ():
                if isinstance (classifier ,(tf .keras .Sequential ,tf .keras .Model )):

                    if classifier_name =="Deep Neural Networks":
                        y_pred =np .argmax (classifier .predict (X_test ),axis =1 )
                    elif classifier_name =="Convolutional Neural Networks":
                        y_pred =np .argmax (classifier .predict (X_test .reshape (-1 ,X_test .shape [1 ],1 )),axis =1 )
                    elif classifier_name =="Recurrent Neural Networks":
                        y_pred =np .argmax (classifier .predict (X_test .reshape (-1 ,1 ,X_test .shape [1 ])),axis =1 )
                    elif classifier_name =="Capsule Networks":
                        y_pred =np .argmax (classifier .predict (X_test .reshape (-1 ,X_test .shape [1 ],1 ,1 )),axis =1 )
                elif classifier_name .startswith ("RAPIDS"):

                    X_test_cudf =cudf .DataFrame (X_test )
                    y_pred =classifier .predict (X_test_cudf )
                    y_pred =y_pred .to_array ()
                else :

                    y_pred =classifier .predict (X_test )

                unique_types ,counts =np .unique (y_pred ,return_counts =True )

                y_mixture =[]
                for biomolecule_type ,count in zip (unique_types ,counts ):
                    y_mixture .extend ([biomolecule_type ]*count )
                y_mixture =np .array (y_mixture )


                test_confusion_matrix =confusion_matrix (y_mixture ,y_pred )

                info_text =f"Biomolecule Type Identification Results for Test Dataset using {classifier_name}:\n"
                for biomolecule_type ,count in zip (unique_types ,counts ):
                    info_text +=f"Biomolecule Type: {biomolecule_type}, Count: {count}\n"

                self .display_results (classifier_name ,None ,None ,test_confusion_matrix ,info_text ,unique_types )


    def train_classifier (self ):

        training_files =[]
        for i ,label in enumerate (self .training_file_labels ):
            if label .toPlainText ():
                training_files .append (label .toPlainText ().split ('\n')[0 ].split (': ')[1 ])


        selected_classifiers =[]
        for checkbox in self .classifier_checkboxes :
            if checkbox .isChecked ():
                selected_classifiers .append (checkbox .text ())


        X ,y =prepare_data (training_files )


        k =int (self .k_fold_combo .currentText ())
        n_estimators =int (self .num_estimators_combo .currentText ())
        random_state =int (self .random_state_spinbox .value ())
        hidden_layer_sizes =(int (self .hidden_layer_sizes_spinbox .value ()),)
        criterion =self .criterion_combo .currentText ()
        n_jobs =int (self .n_jobs_combo .currentText ())
        shuffle =self .shuffle_combo .currentText ()=="True"
        num_layers =int (self .num_layers_spinbox .value ())
        num_epochs =int (self .num_epochs_spinbox .value ())
        batch_size =int (self .batch_size_spinbox .value ())
        learning_rate =float (self .learning_rate_combo .currentText ())


        results =train_and_evaluate_classifiers (X ,y ,selected_classifiers ,k ,n_estimators ,random_state ,hidden_layer_sizes ,criterion ,n_jobs ,shuffle ,num_layers ,num_epochs ,batch_size ,learning_rate )


        self .trained_classifiers ={name :result ['model']for name ,result in results .items ()}


        if self .save_classifier_checkbox .isChecked ():
            file_dialog =QFileDialog ()
            save_path =file_dialog .getExistingDirectory (self ,"Select Save Directory")
            if save_path :
                save_classifiers (results ,save_path )


        for classifier_name ,result in results .items ():
            confusion_matrix =result ['avg_confusion_matrix']
            feature_importances =result .get ('avg_feature_importances')
            labels =np .unique (y )

            info_text =f"Date and Time: {datetime.now()}\n\n"
            info_text +=f"Classifier: {classifier_name}\n\n"
            info_text +=f"Average Accuracy: {result['avg_accuracy']:.4f}\n"
            info_text +=f"Average F1 Score: {result['avg_f1_score']:.4f}\n"
            info_text +=f"Average Sensitivity: {result['avg_sensitivity']:.4f}\n"
            info_text +=f"Average Specificity: {result['avg_specificity']:.4f}\n\n"
            info_text +="Settings:\n"
            info_text +=f"Number of K-Fold Cross Validation: {k}\n"
            info_text +=f"Number of Estimators: {n_estimators}\n"
            info_text +=f"Random State: {random_state}\n"
            info_text +=f"Hidden Layer Sizes: {hidden_layer_sizes}\n"
            info_text +=f"Criterion: {criterion}\n"
            info_text +=f"Number of Jobs: {n_jobs}\n"
            info_text +=f"Shuffle: {shuffle}\n"
            info_text +=f"Number of Layers: {num_layers}\n"
            info_text +=f"Number of Epochs: {num_epochs}\n"
            info_text +=f"Batch Size: {batch_size}\n"
            info_text +=f"Learning Rate: {learning_rate}\n"
            info_text +=f"_____________________________________________________________________ \n\n"

            self .display_results (classifier_name ,confusion_matrix ,feature_importances ,None ,info_text ,labels )

        return results 


    def select_training_file (self ,index ):
        file_dialog =QFileDialog ()
        file_path ,_ =file_dialog .getOpenFileName (self ,"Select Training File","","NPZ Files (*.MLdataset.npz)")

        if file_path :
            X ,label =load_data (file_path )
            self .training_file_labels [index ].setPlainText (f"File: {file_path}\nLabel: {label}")
            self .training_file_labels [index ].setReadOnly (True )
            self .training_file_labels [index ].setWordWrapMode (QTextOption .WrapMode .WrapAtWordBoundaryOrAnywhere )
            self .training_file_labels [index ].setFixedHeight (60 )


    def select_test_dataset (self ):
        file_dialog =QFileDialog ()
        file_path ,_ =file_dialog .getOpenFileName (self ,"Select Test/Unknown Dataset","","NPZ Files (*.MLdataset.npz)")

        if file_path :
            self .test_file_path =file_path 
            X_test ,label =load_data (file_path )
            self .test_file_label .setPlainText (f"File: {file_path}\nLabel: {label}")


    def display_results (self ,classifier_name ,confusion_matrix ,feature_importances ,test_confusion_matrix ,info_text ,labels ):


        for i in range (self .right_tab_widget .count ()):
            if self .right_tab_widget .tabText (i )==classifier_name :

                results_widget =self .right_tab_widget .widget (i )
                break 
        else :

            results_widget =ResultsWidget (classifier_name )
            self .right_tab_widget .addTab (results_widget ,classifier_name )

        if confusion_matrix is not None :
            results_widget .update_plots (confusion_matrix ,feature_importances ,None ,labels )


        if test_confusion_matrix is not None :
            results_widget .update_plots (None ,None ,test_confusion_matrix ,labels )

        results_widget .update_info (info_text )

if __name__ =="__main__":
    app =QApplication (sys .argv )
    app .setStyle (QStyleFactory .create ('Fusion'))

    palette =QPalette ()
    palette .setColor (QPalette .ColorRole .Window ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .WindowText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Base ,QColor (25 ,25 ,25 ))
    palette .setColor (QPalette .ColorRole .AlternateBase ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .ToolTipBase ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .ToolTipText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Text ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .Button ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .ButtonText ,Qt .GlobalColor .white )
    palette .setColor (QPalette .ColorRole .BrightText ,Qt .GlobalColor .red )
    palette .setColor (QPalette .ColorRole .Link ,QColor (42 ,130 ,218 ))
    palette .setColor (QPalette .ColorRole .Highlight ,QColor (42 ,130 ,218 ))
    palette .setColor (QPalette .ColorRole .HighlightedText ,Qt .GlobalColor .black )
    app .setPalette (palette )
    window =MainWindow ()
    window .showMaximized ()
    sys .exit (app .exec ())