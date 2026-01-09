from flask import Flask, request, render_template
from pandas.core.dtypes.cast import np_find_common_type
from pipeline.prediction_pipeline import hybrid_recommendation

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    print("Home page", request.method)
    recommendations = None
    if request.method == 'POST':
        try: 
            user_id = request.form['user_id']
            print("User ID", user_id)
            recommendations = hybrid_recommendation(int(user_id))
            print("Recommendations", recommendations)

        except Exception as e:
            print(f"Error: {e}")

    return render_template('index.html', recommendations=recommendations)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)