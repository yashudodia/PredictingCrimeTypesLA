# -*- coding: utf-8 -*-
"""PredictingCounts.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EHMwEnpR6r_-D0Eg9nnIvDUvJVwE0dVM
"""

import pandas as pd
import io
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score,f1_score,classification_report,confusion_matrix
import warnings
warnings.filterwarnings("ignore")

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

from google.colab import drive
drive.mount('/content/drive')

file_path = '/content/drive/My Drive/FinalProjectExt/Crime_Data_from_2020_to_Present.csv'
df = pd.read_csv(file_path)

"""# Data Preprocessing and Exploratory Data Analysis"""

df.head()

df.info()

col = ['Date Rptd','DR_NO','AREA', 'Mocodes', 'Part 1-2', 'Status', 'Vict Age', 'Vict Sex', 'Vict Descent', 'Premis Desc', 'Weapon Desc', 'Status Desc', 'Crm Cd 1', 'Crm Cd 2', 'Crm Cd 3', 'Crm Cd 4', 'Cross Street','Weapon Used Cd']
df = df.drop(col,axis=1)

df.info()

df.isna().sum()/df.shape[0]

df.dropna(inplace=True)

df.isna().sum()/df.shape[0]

df.head()

df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], format='%m/%d/%Y %I:%M:%S %p')

df['year'] = df['DATE OCC'].dt.year
df['month'] = df['DATE OCC'].dt.month
df['day'] = df['DATE OCC'].dt.day
df['day_of_week'] = df['DATE OCC'].dt.day_name()

df['TIME OCC'] = df['TIME OCC'].astype('str')

df['TIME OCC'] = df['TIME OCC'].apply(lambda x: x.zfill(4))

df['hour'] = df['TIME OCC'].str[:2]
df['minute'] = df['TIME OCC'].str[2:]

df.head()

print(len(df["Crm Cd"].unique()))

df.columns

df['Crm Cd Desc']

df.shape

def Crime_type(crime):
  types = ["STOLEN",'BATTERY','THEFT', 'BURGLARY', 'VANDALISM', 'ASSAULT', 'CRIMINAL THREATS','TRESPASSING','VIOLATION',"CRIMINAL HOMICIDE", 'CHILD ABUSE', 'RAPE','ROBBERY']

  types_name = ["MOTOR VEHICLE THEFT",'BATTERY','THEFT', 'BURGLARY', 'VANDALISM', 'ASSAULT', 'CRIMINAL THREATS', 'TRESPASSING','VIOLATION',"CRIMINAL HOMICIDE", 'CHILD ABUSE', 'RAPE','ROBBERY']

  for name,t in zip(types_name,types) :
    if t in crime:
      return name
  return "OTHERS"

df["Crime"] = df["Crm Cd Desc"].apply(Crime_type)

df["Crime"].value_counts()

df = df.drop(['Crm Cd','Crm Cd Desc'],axis = 1)
df.head()

df.Crime.value_counts()

plt.figure(figsize=(14,10))
plt.title('Amount of Each Crimes')
plt.ylabel('Crime Type')
plt.xlabel('Amount of Crimes')
df.groupby([df['Crime']]).size().sort_values(ascending=True).plot(kind='barh')
plt.show()

crime_types_to_update = ['OTHERS','CRIMINAL THREATS', 'VIOLATION', 'TRESPASSING', 'RAPE', 'CRIMINAL HOMICIDE']

df.loc[df['Crime'].isin(crime_types_to_update), 'Crime'] = 'OTHERS'

df['Crime'].value_counts()

plt.figure(figsize=(12,8))
plt.title("Location ");
sns.scatterplot(x="LON",y="LAT",data=df);

df = df.drop(index = df[( df["LAT"] == 0 ) | ( df["LON"] == 0) ].index)

plt.figure(figsize=(12,8))
plt.title("Location ");
sns.scatterplot(x="LON",y="LAT",data=df);

df.info()

import folium
from folium.plugins import HeatMap
# create map centered at LA
la_map = folium.Map(location=[34.0522, -118.2437], zoom_start=10)

heat_data = [[row['LAT'], row['LON']] for index, row in df.iterrows()]
HeatMap(heat_data, min_opacity=0.2, max_val=10).add_to(la_map)
# display map
la_map

df['AREA NAME'] = df['AREA NAME'].astype('category')
df['Rpt Dist No'] = df['Rpt Dist No'].astype('category')
df['Premis Cd'] = df['Premis Cd'].astype('int')
df['Premis Cd'] = df['Premis Cd'].astype('category')
#df['hour'] = df['hour'].astype('category')
#df['minute'] = df['minute'].astype('category')
#df['day'] = df['day'].astype('category')
#df['month'] = df['month'].astype('category')
df['day_of_week'] = df['day_of_week'].astype('category')

df.info()

df['LOCATION'][0]

df[['Block', 'Street']] = df['LOCATION'].str.extract(r'(\d+)\s+(.+)')
df['Street'] = df['Street'].str.replace(r'\s+', ' ').str.strip()
df[['Block', 'Street']].replace(r'^\s*$', np.nan, regex=True, inplace=True)

df['Block'].unique()

df = df[df['Block'] != '00']

df.shape

df = df.dropna()

df.isna().sum().sum()

len(df['Street'].unique())

df.shape

df.describe()

df.info()

df.columns

#defining features for the model
features = ['LAT','LON','year','month','Crime']
df = df[features]
df.head()

sampled_df = df.sample(n=50000, random_state=42)
sampled_df.reset_index(drop=True, inplace=True)

# shape of sampled dataframe
sampled_df.shape

from sklearn.preprocessing import LabelEncoder
# Initializing LabelEncoder
label_encoder = LabelEncoder()
sampled_df['Crime'] = label_encoder.fit_transform(sampled_df['Crime'])

sampled_df.Crime.value_counts()

#from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
#encoder = OneHotEncoder(drop='first', sparse=True)
#encoded_cols = encoder.fit_transform(sampled_df[categorical_columns])

#encoded_df = pd.DataFrame(encoded_cols.toarray(), columns=encoder.get_feature_names_out(categorical_columns))

#sampled_df = sampled_df.drop(categorical_columns, axis=1)

#sampled_df = pd.concat([sampled_df.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)

sampled_df.head()

#aggregating columns to define crime count
crime_counts = df.groupby(['LAT','LON','year','month']).size().reset_index(name='crime_counts')

df_final = pd.merge(sampled_df, crime_counts, on=['LAT','LON','year','month'], how='left').fillna(0)

df_final.head()

df_final.info()

df_predict = df_final.copy()

df_predict.head()

#Defining X & y parameters
X = df_final.drop(columns=['crime_counts'])
y = df_final['crime_counts']

X.head()

y.head()

# Creating a DataFrame for the next 12 months
future_months = pd.date_range(start='2024-01-01', periods=12, freq='MS')

# Initializing an empty DataFrame for the future data
future_data = pd.DataFrame()

# Assuming we take an average or a representative sample of LAT and LON
mean_lat = df_predict['LAT'].mean()
mean_lon = df_predict['LON'].mean()

# Assuming we use only unique crime types

label_encoder = LabelEncoder()
df_predict['Crime'] = label_encoder.fit_transform(df_predict['Crime'])
unique_crimes = df_predict['Crime'].unique()

for date in future_months:
    temp_df = pd.DataFrame({
        'LAT': mean_lat,
        'LON': mean_lon,
        'year': date.year,
        'month': date.month,
        'Crime': unique_crimes
    })

    future_data = pd.concat([future_data, temp_df], ignore_index=True)

"""# Random Forest Regression Model"""

from sklearn.ensemble import RandomForestRegressor

# Splitting the dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initializing and training the RandomForestRegressor model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)

from sklearn.metrics import mean_squared_error
from math import sqrt

# Calculating RMSE of RandomForestRegressor
rmse = sqrt(mean_squared_error(y_test, y_pred))
print(f"RMSE: {rmse}")

# Predicting the crime counts for the next 12 months
future_predictions = rf_model.predict(future_data)

future_data['predicted_crime_counts'] = future_predictions

# Aggregating predictions by month and crime type
aggregated_predictions = future_data.groupby(['year', 'month', 'Crime']).sum()['predicted_crime_counts'].reset_index()

for index, row in aggregated_predictions.iterrows():
    print(f"Year: {row['year']}, Month: {row['month']}, Crime_Type: {row['Crime']}, Predicted_Count: {row['predicted_crime_counts']}")

"""# Linear Regression Model"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from math import sqrt

# Training the LinearRegression model
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

y_pred_lr = lr_model.predict(X_test)

# Calculating RMSE of LinearRegression Model
rmse_lr = sqrt(mean_squared_error(y_test, y_pred_lr))
print(f"Linear Regression RMSE: {rmse_lr}")

future_data['predicted_lr'] = lr_model.predict(future_data[['LAT', 'LON', 'year', 'month', 'Crime']])

# Aggregating predictions by month and crime type
aggregated_predictions = future_data.groupby(['year', 'month', 'Crime']).sum()['predicted_lr'].reset_index()

for index, row in aggregated_predictions.iterrows():
    print(f"Year: {row['year']}, Month: {row['month']}, Crime_Type: {row['Crime']}, Predicted_Count: {row['predicted_lr']}")

"""# K-Nearest Neighbors Regression Model"""

from sklearn.neighbors import KNeighborsRegressor

# Train
knn_model = KNeighborsRegressor()
knn_model.fit(X_train, y_train)

y_pred_knn = knn_model.predict(X_test)

# Calculating RMSE of KNN Model
rmse_knn = sqrt(mean_squared_error(y_test, y_pred_knn))
print(f"KNN RMSE: {rmse_knn}")

future_data['predicted_knn'] = knn_model.predict(future_data[['LAT', 'LON', 'year', 'month', 'Crime']])

# Aggregating predictions by month and crime type
aggregated_predictions = future_data.groupby(['year', 'month', 'Crime']).sum()['predicted_knn'].reset_index()

for index, row in aggregated_predictions.iterrows():
    print(f"Year: {row['year']}, Month: {row['month']}, Crime_Type: {row['Crime']}, Predicted_Count: {row['predicted_knn']}")

"""# Decision Tree Regression Model"""

from sklearn.tree import DecisionTreeRegressor

# Training the model
dt_model = DecisionTreeRegressor()
dt_model.fit(X_train, y_train)

y_pred_dt = dt_model.predict(X_test)

# Calculating RMSE of Decision Tree Model
rmse_dt = sqrt(mean_squared_error(y_test, y_pred_dt))
print(f"Decision Tree RMSE: {rmse_dt}")

# Future Predictions
future_data['predicted_dt'] = dt_model.predict(future_data[['LAT', 'LON', 'year', 'month', 'Crime']])

# Aggregating predictions by month and crime type
aggregated_predictions = future_data.groupby(['year', 'month', 'Crime']).sum()['predicted_dt'].reset_index()

for index, row in aggregated_predictions.iterrows():
    print(f"Year: {row['year']}, Month: {row['month']}, Crime_Type: {row['Crime']}, Predicted_Count: {row['predicted_dt']}")