import os
import joblib
import frappe

@frappe.whitelist(allow_guest=True)
def predict_placement(iq, cgpa):
    try:
        # Convert inputs to float
        iq = float(iq)
        cgpa = float(cgpa)
        print("IQ:", iq)
        print("CGPA:", cgpa)

        # Get the current directory of the script
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct paths to the model and scaler
        model_path = os.path.join(current_dir, 'placement_model.pkl')
        scaler_path = os.path.join(current_dir, 'scaler.pkl')

        # Load the scaler and model separately
        scaler = joblib.load(scaler_path)
        model = joblib.load(model_path)

        # Scale the input data
        input_scaled = scaler.transform([[iq, cgpa]])
        print("Scaled Input:", input_scaled)

        # Make prediction
        prediction = model.predict(input_scaled)
        print("Prediction:", prediction)

        return prediction

    except Exception as e:
        frappe.log_error("Placement Prediction Error", str(e))
        return {"error": str(e)}
