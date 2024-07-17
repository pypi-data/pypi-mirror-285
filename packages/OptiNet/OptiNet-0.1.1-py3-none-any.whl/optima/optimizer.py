# from sklearn.datasets import load_digits
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.neural_network import MLPClassifier
# from sklearn.metrics import accuracy_score

# class Optima:
#     def __init__(self, model_name='dense'):
#         self.model_name = model_name
#         self.model = self._create_model()

#     def _create_model(self):
#         if self.model_name == 'dense':
#             return MLPClassifier(hidden_layer_sizes=(100,), max_iter=1000, random_state=42)
#         else:
#             raise NotImplementedError(f"Model '{self.model_name}' is not supported")

#     def prepare_data(self, dataset='digits', test_size=0.2, random_state=42):
#         if dataset == 'digits':
#             data = load_digits()
#         else:
#             raise NotImplementedError(f"Dataset '{dataset}' is not supported")

#         X_train, X_test, y_train, y_test = train_test_split(
#             data.data, data.target, test_size=test_size, random_state=random_state
#         )
#         return X_train, X_test, y_train, y_test

#     def train_model(self, X_train, y_train):
#         scaler = StandardScaler()
#         X_train = scaler.fit_transform(X_train)
#         self.model.fit(X_train, y_train)
#         self.scaler = scaler  # Save the scaler for later use

#     def evaluate_model(self, X_test, y_test):
#         if not hasattr(self, 'model'):
#             raise RuntimeError("You need to train the model before evaluating it.")
        
#         X_test = self.scaler.transform(X_test)
#         y_pred = self.model.predict(X_test)
#         accuracy = accuracy_score(y_test, y_pred)
#         return accuracy
