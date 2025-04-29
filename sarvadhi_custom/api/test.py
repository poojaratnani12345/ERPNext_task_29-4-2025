# import pandas as pd
# import pymysql
# import joblib
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler

# import frappe

# # Connect to database
# conn = pymysql.connect(
#     host='127.0.0.1',
#     user='root',
#     password='root',
#     database='_ab9abb0468af9c4b'
# )

# # Load data
# query = "SELECT iq, cgpa, placed FROM tabsample"
# df = pd.read_sql(query, conn)

# # Check the number of rows before cleaning
# print("Number of rows in the dataset before cleaning:", len(df))

# # Check unique values in 'placed' column before cleaning
# print("Unique values in 'placed' column before cleaning:", df['placed'].unique())

# # Clean the data by removing any rows where 'placed' column is NaN
# df = df.dropna(subset=['placed'])

# # Verify if any NaN values remain
# print("NaN values in dataset after cleaning:", df.isna().sum())

# # Check the number of rows after cleaning
# print("Number of rows in the dataset after cleaning:", len(df))

# # Proceed with model training if there are enough rows
# if len(df) > 0:
#     # Define the feature set (X) and target variable (y)
#     X = df[['iq', 'cgpa']]
#     y = df['placed']

#     # Train/test split
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

#     # Scale the features
#     scaler = StandardScaler()
#     X_train_scaled = scaler.fit_transform(X_train)

#     # Train the logistic regression model
#     model = LogisticRegression()
#     model.fit(X_train_scaled, y_train)

#     # Save the trained model and scaler
#     joblib.dump(model, '/Users/maci71401/erpnext_bench/apps/sarvadhi_custom/sarvadhi_custom/api/model.pkl')
#     joblib.dump(scaler, '/Users/maci71401/erpnext_bench/apps/sarvadhi_custom/sarvadhi_custom/api/scaler.pkl')

#     print("Model and scaler saved!")
# else:
#     print("Insufficient data for training. Please check the dataset.")

# conn.close()



import joblib
import pandas as pd

import frappe

def place(doc, method):
    print("Place called")
    try:
        # Load trained model and scaler
        model = joblib.load('/Users/maci71401/erpnext_bench/apps/sarvadhi_custom/sarvadhi_custom/api/model.pkl')
        scaler = joblib.load('/Users/maci71401/erpnext_bench/apps/sarvadhi_custom/sarvadhi_custom/api/scaler.pkl')

        # Get input from doc
        iq = doc.iq
        cgpa = doc.cgpa
        print(f"Input: IQ: {iq}, CGPA: {cgpa}")

        # Use DataFrame to avoid feature name warning
        new_input = pd.DataFrame([[iq, cgpa]], columns=['iq', 'cgpa'])
        new_input_scaled = scaler.transform(new_input)

        # Predict class and probability
        prediction = model.predict(new_input_scaled)
        proba = model.predict_proba(new_input_scaled)

        # Predict
        result = int(prediction[0])
        confidence = round(max(proba[0]) * 100, 2)

        print(f"Prediction: {result}")
        print(f"Confidence: {confidence}%")

        # Store "Yes" or "No"
        doc.placed = "Yes" if result == 1 else "No"
        frappe.msgprint(f"Prediction: {doc.placed} with {confidence}% confidence")
        print("Placed ✅" if result == 1 else "Not Placed ❌")

    except Exception as e:
        print("Error in prediction:", e)

