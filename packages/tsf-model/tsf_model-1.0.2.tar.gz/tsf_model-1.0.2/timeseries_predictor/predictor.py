import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.python.framework import convert_to_constants
from xgboost import XGBRegressor
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, concatenate
from tensorflow.keras.layers import LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D, Add

class TimeSeriesPredictor:
    def __init__(self, model_type='LSTM', input_shape=(10, 1), units=50, dropout_rate=0.2, patience=5):
        self.model_type = model_type
        self.input_shape = input_shape
        self.units = units
        self.dropout_rate = dropout_rate
        self.patience = patience
        self.model = None
        self.scaler = None
        if model_type in ['LSTM', 'BiLSTM']:
            self.model = self.build_rnn_model()
        elif model_type == 'XGBoost':
            self.model = XGBRegressor()
        elif model_type in ['ARIMA', 'ARIMA-NN']:
            self.model = None  # These models are built during training
        elif model_type == 'Transformer':
            self.model = self.transformer_model()

    def build_rnn_model(self):
        model = Sequential()
        if self.model_type == 'LSTM':
            model.add(LSTM(units=self.units, return_sequences=True, input_shape=self.input_shape))
            model.add(Dropout(self.dropout_rate))
            model.add(LSTM(units=self.units))
        elif self.model_type == 'BiLSTM':
            model.add(Bidirectional(LSTM(units=self.units, return_sequences=True), input_shape=self.input_shape))
            model.add(Dropout(self.dropout_rate))
            model.add(Bidirectional(LSTM(units=self.units)))

        model.add(Dropout(self.dropout_rate))
        model.add(Dense(self.units, activation='relu'))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def transformer_block(self, x):
        attn_output = layers.MultiHeadAttention(num_heads=2, key_dim=self.units)(x, x)
        attn_output = layers.Dropout(self.dropout_rate)(attn_output)
        out1 = layers.LayerNormalization(epsilon=1e-6)(x + attn_output)

        ffn_output = Sequential([
            layers.Dense(self.units, activation='relu'),
            layers.Dense(self.units)
        ])(out1)
        ffn_output = layers.Dropout(self.dropout_rate)(ffn_output)
        return layers.LayerNormalization(epsilon=1e-6)(out1 + ffn_output)

    def transformer_model(self):
        input_layer = Input(shape=self.input_shape)
        x = layers.Dense(self.units)(input_layer)

        for _ in range(2):
            x = self.transformer_block(x)

        x = layers.GlobalAveragePooling1D()(x)
        output_layer = layers.Dense(1)(x)

        model = Model(inputs=input_layer, outputs=output_layer)
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.005), loss='mean_squared_error')
        return model

    def train(self, X_train, y_train, validation_data=None, validation_split=0.1, epochs=100, batch_size=32):
        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=validation_data, validation_split=validation_split, callbacks=[early_stopping])

    def predict(self, X_test):
        return self.model.predict(X_test)


    def train(self, X_train, y_train, validation_data=None, validation_split=0.0, epochs=50, batch_size=32):
        if self.model_type in ['LSTM', 'BiLSTM', 'Transformer']:
            early_stopping = EarlyStopping(monitor='val_loss', patience=self.patience, restore_best_weights=True)
            callbacks = [early_stopping]
            self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=validation_data, validation_split=validation_split, callbacks=callbacks)
        elif self.model_type == 'XGBoost':
            self.model.fit(X_train.reshape((X_train.shape[0], -1)), y_train)
        elif self.model_type == 'ARIMA':
            # p_values = [0, 1, 2, 4, 6, 8, 10]
            # d_values = [0, 1, 2]
            # q_values = [0, 1, 2, 4, 6, 8, 10]
            # best_cfg = self.grid_search_arima(y_train, p_values, d_values, q_values)
            self.model = ARIMA(y_train, order=(5, 1, 0)).fit()
        elif self.model_type == 'ARIMA_NN':
            self.scaler = StandardScaler()
            y_train_scaled = self.scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
            arima = ARIMA(y_train_scaled, order=(5, 1, 0)).fit()
            y_train_arima = y_train_scaled - arima.fittedvalues

            rnn_input = np.zeros((X_train.shape[0], X_train.shape[1], X_train.shape[2]+1))
            rnn_input[:, :, :-1] = X_train

            y_train_arima = np.tile(y_train_arima, (X_train.shape[1], 1)).T
            rnn_input[:, :, -1] = y_train_arima

            self.model = self.build_rnn_model()
            early_stopping = EarlyStopping(monitor='val_loss', patience=self.patience, restore_best_weights=True)
            callbacks = [early_stopping]
            self.model.fit(rnn_input, y_train_scaled.reshape(-1, 1), epochs=epochs, batch_size=batch_size, validation_data=validation_data, validation_split=validation_split, callbacks=callbacks)

    def predict(self, X_test):
        if self.model_type in ['LSTM', 'BiLSTM', 'Transformer']:
            return self.model.predict(X_test)
        elif self.model_type == 'XGBoost':
            return self.model.predict(X_test.reshape((X_test.shape[0], -1)))
        elif self.model_type == 'ARIMA':
            return self.model.forecast(steps=X_test.shape[0])
        elif self.model_type == 'ARIMA-NN':
            arima_forecast = self.model.forecast(steps=X_test.shape[0])
            rnn_input = np.zeros((X_test.shape[0], X_test.shape[1], X_test.shape[2] + 1))
            rnn_input[:, :, :-1] = X_test
            arima_forecast = np.tile(arima_forecast, (X_test.shape[1], 1)).T
            rnn_input[:, :, -1] = arima_forecast

            nn_forecast = self.model.predict(rnn_input)
            return self.scaler.inverse_transform(nn_forecast)

    def calculate_params(self):
        if self.model_type in ['LSTM', 'BiLSTM', 'Transformer']:
            return self.model.count_params()
        else:
            return None

    def calculate_flops(self):
        if self.model_type in ['LSTM', 'BiLSTM', 'Transformer']:
            concrete = tf.function(lambda inputs: self.model(inputs))
            concrete_func = concrete.get_concrete_function(
                tf.TensorSpec([1] + self.model.inputs[0].shape[1:], self.model.inputs[0].dtype))
            frozen_func = convert_to_constants.convert_variables_to_constants_v2(concrete_func)
            graph_def = frozen_func.graph.as_graph_def()

            with tf.compat.v1.Graph().as_default() as graph:
                tf.compat.v1.import_graph_def(graph_def, name='')
                run_meta = tf.compat.v1.RunMetadata()
                opts = tf.compat.v1.profiler.ProfileOptionBuilder.float_operation()
                flops = tf.compat.v1.profiler.profile(graph=graph, run_meta=run_meta, cmd='op', options=opts)
                return flops.total_float_ops
        else:
            return None

    def get_model_info(self):
        params = self.calculate_params()
        flops = self.calculate_flops()
        params_in_millions = params / 10**6 if params else 'N/A'
        flops_in_giga = flops / 10**9 if flops else 'N/A'
        return params_in_millions, flops_in_giga
    ####ARIMA 参数调优
    def evaluate_arima_model(self, X, arima_order):
        train_size = int(len(X) * 0.8)
        train, test = X[:train_size], X[train_size:]
        history = [x for x in train]
        predictions = list()
        for t in range(len(test)):
            model = ARIMA(history, order=arima_order)
            model_fit = model.fit()
            yhat = model_fit.forecast()[0]
            predictions.append(yhat)
            history.append(test[t])
        mse = mean_squared_error(test, predictions)
        return mse

    def grid_search_arima(self, data, p_values, d_values, q_values):
        best_score, best_cfg = float("inf"), None
        for p in p_values:
            for d in d_values:
                for q in q_values:
                    order = (p, d, q)
                    try:
                        mse = self.evaluate_arima_model(data, order)
                        if mse < best_score:
                            best_score, best_cfg = mse, order
                        print(f'ARIMA{order} MSE={mse}')
                    except:
                        continue
        print(f'Best ARIMA{best_cfg} MSE={best_score}')
        return best_cfg





