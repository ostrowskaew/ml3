# --------------------------------------------------------------------------
# ------------  Metody Systemowe i Decyzyjne w Informatyce  ----------------
# --------------------------------------------------------------------------
#  Zadanie 3: Regresja logistyczna
#  autorzy: A. Gonczarek, J. Kaczmar, S. Zareba
#  2017
# --------------------------------------------------------------------------

import numpy as np


def sigmoid(x):
    '''
    :param x: wektor wejsciowych wartosci Nx1
    :return: wektor wyjściowych wartości funkcji sigmoidalnej dla wejścia x, Nx1
    '''
    return 1 / (1 + np.exp(-x))


def logistic_cost_function(w, x_train, y_train):
    '''
    :param w: parametry modelu Mx1
    :param x_train: ciag treningowy - wejscia NxM
    :param y_train: ciag treningowy - wyjscia Nx1
    :return: funkcja zwraca krotke (val, grad), gdzie val oznacza wartosc funkcji logistycznej, a grad jej gradient po w
    '''
    N = x_train.shape[0]
    sig_arr = sigmoid(x_train @ w)  # NxM @ Mx1 = Nx1
    out_arr = y_train * np.log(sig_arr) + (1 - y_train) * np.log(1 - sig_arr)
    grad = x_train.transpose() @ (sig_arr - y_train) / N  # MxN @ Nx1 = Mx1
    return -1 / N * np.sum(out_arr), grad


def gradient_descent(obj_fun, w0, epochs, eta):
    '''
    :param obj_fun: funkcja celu, ktora ma byc optymalizowana. Wywolanie val,grad = obj_fun(w).
    :param w0: punkt startowy Mx1
    :param epochs: liczba epok / iteracji algorytmu
    :param eta: krok uczenia
    :return: funkcja wykonuje optymalizacje metoda gradientu prostego dla funkcji obj_fun. Zwraca krotke (w,func_values),
    gdzie w oznacza znaleziony optymalny punkt w, a func_valus jest wektorem wartosci funkcji [epochs x 1] we wszystkich krokach algorytmu
    '''
    func_values = []
    w = w0
    _, grad = obj_fun(w)
    for k in range(epochs):
        w = w - eta * grad
        val, grad = obj_fun(w)
        func_values.append(val)
    return w, np.reshape(np.array(func_values), (epochs, 1))


def stochastic_gradient_descent(obj_fun, x_train, y_train, w0, epochs, eta, mini_batch):
    '''
    :param obj_fun: funkcja celu, ktora ma byc optymalizowana. Wywolanie val,grad = obj_fun(w,x,y), gdzie x,y oznaczaja podane
    podzbiory zbioru treningowego (mini-batche)
    :param x_train: dane treningowe wejsciowe NxM
    :param y_train: dane treningowe wyjsciowe Nx1
    :param w0: punkt startowy Mx1
    :param epochs: liczba epok
    :param eta: krok uczenia
    :param mini_batch: wielkosc mini-batcha
    :return: funkcja wykonuje optymalizacje metoda stochastycznego gradientu prostego dla funkcji obj_fun. Zwraca krotke (w,func_values),
    gdzie w oznacza znaleziony optymalny punkt w, a func_values jest wektorem wartosci funkcji [epochs x 1] we wszystkich krokach algorytmu. Wartosci
    funkcji do func_values sa wyliczane dla calego zbioru treningowego!
    '''
    x_subsets = []
    y_subsets = []
    M = int(y_train.shape[0] / mini_batch)
    for m in range(M):
        x_subsets.append(x_train[m * mini_batch: (m + 1) * mini_batch])
        y_subsets.append(y_train[m * mini_batch: (m + 1) * mini_batch])
    w = w0
    vals = []
    for k in range(epochs):
        for m in range(M):
            _, w_grad = obj_fun(w, x_subsets[m], y_subsets[m])
            w = w - eta * w_grad
        val, _ = obj_fun(w, x_train, y_train)
        vals.append(val)
    return w, np.reshape(np.array(vals), (epochs, 1))


def regularized_logistic_cost_function(w, x_train, y_train, regularization_lambda):
    '''
    :param w: parametry modelu Mx1
    :param x_train: ciag treningowy - wejscia NxM
    :param y_train: ciag treningowy - wyjscia Nx1
    :param regularization_lambda: parametr regularyzacji
    :return: funkcja zwraca krotke (val, grad), gdzie val oznacza wartosc funkcji logistycznej z regularyzacja l2,
    a grad jej gradient po w
    '''
    val0, grad0 = logistic_cost_function(w, x_train, y_train)
    ws = np.delete(w, 0)
    regularization = regularization_lambda / 2 * np.linalg.norm(ws) ** 2
    wz = w.copy()
    wz[0] = 0
    grad = grad0 + regularization_lambda * wz
    return val0 + regularization, grad


def prediction(x, w, theta):
    '''
    :param x: macierz obserwacji NxM
    :param w: wektor parametrow modelu Mx1
    :param theta: prog klasyfikacji z przedzialu [0,1]
    :return: funkcja wylicza wektor y o wymiarach Nx1. Wektor zawiera wartosci etykiet ze zbioru {0,1} dla obserwacji z x
     bazujac na modelu z parametrami w oraz progu klasyfikacji theta
    '''
    sig_arr = sigmoid(x @ w)
    return sig_arr > theta


def f_measure(y_true, y_pred):
    '''
    :param y_true: wektor rzeczywistych etykiet Nx1
    :param y_pred: wektor etykiet przewidzianych przed model Nx1
    :return: funkcja wylicza wartosc miary F
    '''
    TP = np.sum(np.bitwise_and(y_true, y_pred))
    FP = np.sum(np.bitwise_and(np.bitwise_not(y_true), y_pred))
    FN = np.sum(np.bitwise_and(y_true, np.bitwise_not(y_pred)))
    return 2 * TP / (2 * TP + FP + FN)


def model_selection(x_train, y_train, x_val, y_val, w0, epochs, eta, mini_batch, lambdas, thetas):
    '''
    :param x_train: ciag treningowy wejsciowy NxM
    :param y_train: ciag treningowy wyjsciowy Nx1
    :param x_val: ciag walidacyjny wejsciowy Nval x M
    :param y_val: ciag walidacyjny wyjsciowy Nval x 1
    :param w0: wektor poczatkowych wartosci parametrow
    :param epochs: liczba epok dla SGD
    :param eta: krok uczenia
    :param mini_batch: wielkosc mini batcha
    :param lambdas: lista wartosci parametru regularyzacji lambda, ktore maja byc sprawdzone
    :param thetas: lista wartosci progow klasyfikacji theta, ktore maja byc sprawdzone
    :return: funckja wykonuje selekcje modelu. Zwraca krotke (regularization_lambda, theta, w, F), gdzie regularization_lambda
    to najlpszy parametr regularyzacji, theta to najlepszy prog klasyfikacji, a w to najlepszy wektor parametrow modelu.
    Dodatkowo funkcja zwraca macierz F, ktora zawiera wartosci miary F dla wszystkich par (lambda, theta). Do uczenia nalezy
    korzystac z algorytmu SGD oraz kryterium uczenia z regularyzacja l2.
    '''
    F = []
    best_measure = -1
    for a_lambda in lambdas:
        obj_fun = lambda w, x_train, y_train: regularized_logistic_cost_function(w, x_train, y_train, a_lambda)
        w, _ = stochastic_gradient_descent(obj_fun, x_train, y_train, w0, epochs, eta, mini_batch)
        for theta in thetas:
            measure = f_measure(y_val, prediction(x_val, w, theta))
            F.append(measure)
            if measure > best_measure:
                best_measure = measure
                best_w = w
                best_lambda = a_lambda
                best_theta = theta
    return best_lambda, best_theta, best_w, np.array(F).reshape(len(lambdas), len(thetas))