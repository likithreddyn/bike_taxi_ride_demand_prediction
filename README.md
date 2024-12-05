# bike_taxi_ride_demand_prediction
Hello friends i am thrilled to share my latest mini-project: Ola Bike Ride Demand Forecasting with ML! 🏍📊
I built a web application using Flask, HTML, and CSS to predict the demand for Ola bike rides. This application aims to optimize efficient rider fleet distribution and enhance user experience by providing accurate demand forecasts. By leveraging the powerful LightGBM algorithm and the collaborative power of Google Colab, I was able to effectively analyze, normalize, and model historical ride data.
Key Highlights:
 * Data Analysis and Normalization: Leveraged Google Colab for efficient data 
                                    exploration and preprocessing.
 * Model Building: Utilized the LightGBM algorithm for accurate demand forecasting.
 * Web App Development: Created a user-friendly interface using Flask, HTML, and CSS. 
                        Spyder IDE was used to run the Flask app locally.
 * Model Serialization: Used Pickle to serialize the trained model for future use and 
                        experimentation.
Looking forward to connecting with fellow data enthusiasts and industry professionals to discuss insights and potential applications.
Directory Structure
Your project directory should look something like this:
your_project_folder/
│
├── app.py               # Your main Flask app file             
├── models/              # Folder where your saved model(s) are located
│   └── lgb_model.pkl    # Your trained LightGBM model file
├── templates/           # Folder containing your HTML files
│   └── index.html       # Your main HTML file (Flask template)
├   └── results.html     # Your result card HTML file (Flask template)
├── static/              # Folder for static files like CSS, JS, images
│   └── style.css        # Your CSS file
└── requirements.txt     # Python dependencies
