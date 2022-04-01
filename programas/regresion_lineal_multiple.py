import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error



def rlm(datarlm, spoke_labels, contaminante, año, exclude_p):

    """
    Create a radar chart with variables to compare.

    This function receives parameters and with that a radar chart is created.

    Parameters
    ----------
    datarlm: list
        A list that contains one list for each dataset.

    """


    corr_matrix = datarlm.corr(method='pearson')
    corr_mat = corr_matrix.stack().reset_index()
    corr_mat.columns = ['variable_1','variable_2','r']
    corr_mat = corr_mat.loc[corr_mat['variable_1'] != corr_mat['variable_2'], :]
    corr_mat['abs_r'] = np.abs(corr_mat['r'])
    corr_mat = corr_mat.sort_values('abs_r', ascending=False)
    tidy_corr_matrix = (corr_matrix).head(10)
    # Heatmap matriz de correlaciones
    # ==============================================================================
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4, 4))
    sns.heatmap(
        corr_matrix,
        annot     = True,
        cbar      = False,
        annot_kws = {"size": 8},
        vmin      = -1,
        vmax      = 1,
        center    = 0,
        cmap      = sns.diverging_palette(20, 220, n=200),
        square    = True,
        ax        = ax
    )
    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation = 45,
        horizontalalignment = 'right',
    )
    ax.tick_params(labelsize = 10)
    # División de los datos en train y test
    # ==============================================================================
    X = datarlm[spoke_labels]
    y = datarlm[contaminante]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y.values.reshape(-1,1),
        train_size   = 0.8,
        random_state = 1234,
        shuffle      = True
    )
    # Creación del modelo utilizando matrices como en scikitlearn
    # ==============================================================================
    # A la matriz de predictores se le tiene que añadir una columna de 1s para el intercept del modelo
    X_train = sm.add_constant(X_train, prepend=True)
    modelo = sm.OLS(endog=y_train, exog=X_train,)
    modelo = modelo.fit()
    print(modelo.summary())
    sml = modelo.summary().as_latex()
    namefile = 'modelos_latex/' + 'regresion_lineal_multiple_' + contaminante + '_' + año + '.tex'
    f = open(namefile, 'w')
    with open(namefile, 'w') as f:
        f.write(sml)
    # Creación del modelo utilizando matrices
    # ==============================================================================
    # Se eliminan las columnas con p-value>0.5 del conjunto de train y test
    #X_train = X_train.drop(columns = exclude_p)
    #X_test  = X_test.drop(columns = exclude_p)
    # A la matriz de predictores se le tiene que añadir una columna de 1s para el
    # intercept del modelo
    #X_train = sm.add_constant(X_train, prepend=True)
    #modelo  = sm.OLS(endog=y_train, exog=X_train,)
    #modelo  = modelo.fit()
    #print(modelo.summary())
    #namefile = 'modelos_latex_fixed/' + 'regresion_lineal_multiple_' + contaminante + '_' + año + '.tex'
    #f = open(namefile, 'w')
    #with open(namefile, 'w') as f:
    #    f.write(sml)
    # Diagnóstico errores (residuos) de las predicciones de entrenamiento
    # ==============================================================================
    y_train = y_train.flatten()
    prediccion_train = modelo.predict(exog = X_train)
    residuos_train   = prediccion_train - y_train
    # Predicciones con intervalo de confianza 
    # ==============================================================================
    predicciones = modelo.get_prediction(exog = X_train).summary_frame(alpha=0.05)
    predicciones.head(4)
    # Error de test del modelo 
    # ==============================================================================
    X_test = sm.add_constant(X_test, prepend=True)
    predicciones = modelo.predict(exog = X_test)
    rmse = mean_squared_error(
        y_true  = y_test,
        y_pred  = predicciones,
        squared = False
    )
    vmin = abs(y_test.min())
    vmax = abs(y_test.max())
    pval = vmin + vmax
    pe = (rmse*100)/pval
    print(f"El error (rmse) de test es: {rmse}")
    #print(f"El porcentaje de error de test es: {pe}")
    
