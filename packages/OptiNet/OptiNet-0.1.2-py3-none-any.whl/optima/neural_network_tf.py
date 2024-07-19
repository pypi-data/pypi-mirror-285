# import tensorflow as tf
# from tensorflow.python.keras.layers import Dense
# from tensorflow.python.keras.models import Sequential
# from tensorflow.python.keras.layers import Dense, ReLU, Softmax
# from tensorflow.python.keras.optimizer_v2 import adam
# from tensorflow.python.keras.losses import SparseCategoricalCrossentropy

# class NeuralNetworkModelTF:
#     def __init__(self, input_size, hidden_size, output_size, learning_rate=0.001):
#         self.model = Sequential([
#             Dense(hidden_size, input_shape=(input_size,), activation='relu'),
#             Dense(output_size, activation='softmax')
#         ])
#         self.model.compile(optimizer=adam(learning_rate=learning_rate),
#                            loss=SparseCategoricalCrossentropy(),
#                            metrics=['accuracy'])

#     def fit(self, X_train, y_train, epochs=10, batch_size=32):
#         self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size)

#     def predict(self, X_test):
#         predictions = self.model.predict(X_test)
#         return tf.argmax(predictions, axis=1).numpy()






import numpy as np
from tensorflow.python.keras.models  import Sequential
from tensorflow.python.keras.layers import  LSTM, Dense


# Prepare the data
characters = 'ABC'
char_to_index = {ch: i for i, ch in enumerate(characters)}
index_to_char = {i: ch for i, ch in enumerate(characters)}

# Generate sequences
sequences = ['A', 'B', 'C', 'AB', 'BA', 'AC', 'CA', 'BC', 'CB', 'ABC', 'ACB', 'BAC', 'BCA', 'CAB', 'CBA']
max_seq_length = max([len(seq) for seq in sequences])

# Prepare training data
X = []
y = []

for seq in sequences:
    for i in range(len(seq)):
        input_seq = seq[:i]
        target_char = seq[i]
        
        input_seq_padded = input_seq + ' ' * (max_seq_length - len(input_seq))
        input_seq_indices = [char_to_index[ch] if ch != ' ' else -1 for ch in input_seq_padded]
        target_char_index = char_to_index[target_char]
        
        X.append(input_seq_indices)
        y.append(target_char_index)
def to_categorical(y, num_classes=None, dtype='float32'):
    return np.eye(num_classes, dtype=dtype)[y]

X = np.array(X)
y = to_categorical(y, num_classes=len(characters))

# Define the model
model = Sequential()
model.add(LSTM(50, input_shape=(max_seq_length, len(characters)), return_sequences=False))
model.add(Dense(len(characters), activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
model.fit(X, y, epochs=100, verbose=2)

# Generate names
def generate_name(model, start_char, length):
    name = start_char
    for _ in range(length - 1):
        input_seq = name[-max_seq_length:]
        input_seq_padded = input_seq + ' ' * (max_seq_length - len(input_seq))
        input_seq_indices = [char_to_index[ch] if ch != ' ' else -1 for ch in input_seq_padded]
        input_seq_onehot = to_categorical(input_seq_indices, num_classes=len(characters)).reshape(1, max_seq_length, len(characters))
        
        predicted_index = np.argmax(model.predict(input_seq_onehot), axis=-1)
        predicted_char = index_to_char[predicted_index[0]]
        name += predicted_char
        
    return name

# Example usage
print(generate_name(model, 'A', 5))
# # Define the alphabet
# alphabet = "ABC"
# char_to_int = {c: i for i, c in enumerate(alphabet)}
# int_to_char = {i: c for i, c in enumerate(alphabet)}

# # Generate more varied sequences
# sequences = []
# next_chars = []

# for i in range(3):  # Generate patterns of length 3
#     for j in range(3):
#         for k in range(3):
#             sequences.append([char_to_int[alphabet[i]], char_to_int[alphabet[j]]])
#             next_chars.append(char_to_int[alphabet[k]])

# # Function to convert to one-hot encoding
# def to_categorical(y, num_classes=None, dtype='float32'):
#     return np.eye(num_classes, dtype=dtype)[y]

# # Convert to one-hot encoding
# X = to_categorical(np.array(sequences).flatten(), num_classes=len(alphabet)).reshape(len(sequences), 2, len(alphabet))
# y = to_categorical(next_chars, num_classes=len(alphabet))

# # Build the model
# model = Sequential()
# model.add(SimpleRNN(10, input_shape=(2, len(alphabet)), return_sequences=False))
# model.add(Dense(len(alphabet), activation='softmax'))

# model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# model.summary()

# # Train the model
# model.fit(X, y, epochs=100, batch_size=1, verbose=2)

# # Function to generate a name
# def generate_name(model, seed, length):
#     result = seed
#     for _ in range(length - len(seed)):
#         x = np.reshape(to_categorical([char_to_int[char] for char in result[-2:]], num_classes=len(alphabet)), (1, 2, len(alphabet)))
#         prediction = model.predict(x, verbose=0)
#         index = np.argmax(prediction)
#         next_char = int_to_char[index]
#         result += next_char
#     return result

# # Generate a name of length 10 starting with 'AB'
# generated_name = generate_name(model, 'AB', 10)
# print("Generated name:", generated_name)