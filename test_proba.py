import pickle, numpy as np

m = pickle.load(open('models/model.pkl', 'rb'))

test_cases = [
    {'name': 'Rice Profile', 'data': [90, 42, 43, 20.8, 82, 6.5, 202]},
    {'name': 'Apple Profile', 'data': [20, 130, 200, 22, 90, 5.5, 110]},
    {'name': 'Coffee Profile', 'data': [100, 20, 30, 25, 50, 6.5, 150]},
    {'name': 'Cotton Profile', 'data': [120, 40, 20, 24, 80, 7.0, 80]},
    {'name': 'Grapes Profile', 'data': [25, 130, 200, 15, 80, 6.0, 70]},
    {'name': 'Jute Profile', 'data': [80, 40, 40, 25, 80, 6.5, 170]},
]

for case in test_cases:
    x = np.array([case['data']])
    p = m.predict_proba(x)[0]
    conf = np.max(p)*100
    print(f"{case['name']}: {conf}% - Predicted: {m.predict(x)[0]}")
