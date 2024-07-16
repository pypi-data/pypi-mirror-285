import numpy as np, pandas as pd



def metrics_eval(ypred:np.ndarray=None,  ytrue:np.ndarray=None,
                 metric_list:list=["mean_squared_error", "mean_absolute_error"],
                 ypred_proba:np.ndarray=None, return_dict:bool=False, metric_pars:dict=None)->pd.DataFrame:
    """ Generic metrics calculation, using sklearn naming pattern.
    Doc::
    
          dfres = metrics_eval(ypred,  ytrue,
                    metric_lis=["mean_squared_error", "mean_absolute_error"],
                    ypred_proba=None, return_dict=False, metric_pars:dict=None)                 
          print(df[[ 'metric_name', 'metric_val']])

          
                  
          Metric names are below
          https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics


          #### Regression metrics
          explained_variance_score(y_true,...)
          max_error(y_true,y_pred)
          mean_absolute_error(y_true,y_pred,*)
          mean_squared_error(y_true,y_pred,*)
          mean_squared_log_error(y_true,y_pred,*)
          median_absolute_error(y_true,y_pred,*)
          mean_absolute_percentage_error(...)
          r2_score(y_true,y_pred,*[,...])
          mean_poisson_deviance(y_true,y_pred,*)
          mean_gamma_deviance(y_true,y_pred,*)
          mean_tweedie_deviance(y_true,y_pred,*)
          d2_tweedie_score(y_true,y_pred,*)
          mean_pinball_loss(y_true,y_pred,*)


          #### Classification metrics
          accuracy_score(y_true,y_pred,*[,...])
          auc(x,y)
          average_precision_score(y_true,...)
          balanced_accuracy_score(y_true,...)
          brier_score_loss(y_true,y_prob,*)
          classification_report(y_true,y_pred,*)
          cohen_kappa_score(y1,y2,*[,...])
          confusion_matrix(y_true,y_pred,*)
          dcg_score(y_true,y_score,*[,k,...])
          det_curve(y_true,y_score[,...])
          f1_score(y_true,y_pred,*[,...])
          fbeta_score(y_true,y_pred,*,beta)
          hamming_loss(y_true,y_pred,*[,...])
          hinge_loss(y_true,pred_decision,*)
          jaccard_score(y_true,y_pred,*[,...])
          log_loss(y_true,y_pred,*[,eps,...])
          matthews_corrcoef(y_true,y_pred,*)
          multilabel_confusion_matrix(y_true,...)
          ndcg_score(y_true,y_score,*[,k,...])
          precision_recall_curve(y_true,...)
          precision_recall_fscore_support(...)
          precision_score(y_true,y_pred,*[,...])
          recall_score(y_true,y_pred,*[,...])
          roc_auc_score(y_true,y_score,*[,...])
          roc_curve(y_true,y_score,*[,...])
          top_k_accuracy_score(y_true,y_score,*)
          zero_one_loss(y_true,y_pred,*[,...])
          
          #### Multilabel ranking metrics
          coverage_error(y_true,y_score,*[,...])
          label_ranking_average_precision_score(...)
          label_ranking_loss(y_true,y_score,*)


          ##### Clustering
          supervised, which uses a ground truth class values for each sample.
          unsupervised, which does not and measures ‘quality’ of model itself.

          adjusted_mutual_info_score(...[,...])
          adjusted_rand_score(labels_true,...)
          calinski_harabasz_score(X,labels)
          davies_bouldin_score(X,labels)
          completeness_score(labels_true,...)
          cluster.contingency_matrix(...[,...])
          cluster.pair_confusion_matrix(...)
          fowlkes_mallows_score(labels_true,...)
          homogeneity_completeness_v_measure(...)
          homogeneity_score(labels_true,...)
          mutual_info_score(labels_true,...)
          normalized_mutual_info_score(...[,...])
          rand_score(labels_true,labels_pred)
          silhouette_score(X,labels,*[,...])
          silhouette_samples(X,labels,*[,...])
          v_measure_score(labels_true,...[,beta])
          consensus_score(a,b,*[,similarity])



          #### Pairwise metrics
          pairwise.additive_chi2_kernel(X[,Y])
          pairwise.chi2_kernel(X[,Y,gamma])
          pairwise.cosine_similarity(X[,Y,...])
          pairwise.cosine_distances(X[,Y])
          pairwise.distance_metrics()
          pairwise.euclidean_distances(X[,Y,...])
          pairwise.haversine_distances(X[,Y])
          pairwise.kernel_metrics()
          pairwise.laplacian_kernel(X[,Y,gamma])
          pairwise.linear_kernel(X[,Y,...])
          pairwise.manhattan_distances(X[,Y,...])
          pairwise.nan_euclidean_distances(X)
          pairwise.pairwise_kernels(X[,Y,...])
          pairwise.polynomial_kernel(X[,Y,...])
          pairwise.rbf_kernel(X[,Y,gamma])
          pairwise.sigmoid_kernel(X[,Y,...])
          pairwise.paired_euclidean_distances(X,Y)
          pairwise.paired_manhattan_distances(X,Y)
          pairwise.paired_cosine_distances(X,Y)
          pairwise.paired_distances(X,Y,*[,...])
          pairwise_distances(X[,Y,metric,...])
          pairwise_distances_argmin(X,Y,*[,...])
          pairwise_distances_argmin_min(X,Y,*)
          pairwise_distances_chunked(X[,Y,...])



    """
    import pandas as pd, importlib, sklearn
    mdict = {"metric_name": [],
             "metric_val": [],
             "n_sample": [len(ytrue)] * len(metric_list),
             "n_sample_y1": [sum(ytrue)] * len(metric_list),             
            }

    if isinstance(metric_list, str):
        metric_list = [metric_list]

    for metric_name in metric_list:
        mod = "sklearn.metrics"

        if metric_name in ["roc_auc_score"]:
            #### Ok for Multi-Class
            metric_scorer = getattr(importlib.import_module(mod), metric_name)
            assert len(ypred_proba)>0, 'Require ypred_proba'
            mval_=[]
            for i_ in range(ypred_proba.shape[1]):
                mval_.append(metric_scorer(pd.get_dummies(ytrue).to_numpy()[:,i_], ypred_proba[:,i_]))
            mval          = np.mean(np.array(mval_))

        elif metric_name in ["root_mean_squared_error"]:
            metric_scorer = getattr(importlib.import_module(mod), "mean_squared_error")
            mval          = np.sqrt(metric_scorer(ytrue, ypred))

        else:
            ll = ["recall", "precision", "f1", "accuracy" ]
            if metric_name in ll : metric_name += "_score"

            metric_scorer = getattr(importlib.import_module(mod), metric_name)
            mval = metric_scorer(ytrue, ypred)
            
            if metric_name in ["confusion_matrix"]:
                mval = str(mval).replace("\n ", "").replace("  ", " ").replace("[ ", "[")
                # mval = mval.replace("][]", ";")

        mdict["metric_name"].append(metric_name.replace("_score", ""))
        mdict["metric_val"].append(mval)

    if return_dict: return mdict

    mdict = pd.DataFrame(mdict)
    mdict = mdict[[ "metric_name", "metric_val", "n_sample", "n_sample_y1" ]]
    return mdict


def metrics_plot(ypred=None,  ytrue=None,  metric_list=["mean_squared_error"], plotname='histo', ypred_proba=None, return_dict=False):
    """ Generic metrics Plotting.
    Doc::

          https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics

          #### Plotting
          plot_confusion_matrix(estimator,X,...)
          plot_det_curve(estimator,X,y,*[,...])
          plot_precision_recall_curve(...[,...])
          plot_roc_curve(estimator,X,y,*[,...])
          ConfusionMatrixDisplay(...[,...])
          DetCurveDisplay(*,fpr,fnr[,...])
          PrecisionRecallDisplay(precision,...)
          RocCurveDisplay(*,fpr,tpr[,...])
          calibration.CalibrationDisplay(prob_true,...)

    """
    pass




def np_to_single_array(array_array ):
   """    Convert a nested list of arrays into a single array.
   Docs::

        Parameters:  array_array (list): A nested list of arrays.
        Returns: A single array 
   """
   return np.array([list(arr) for arr in array_array ])




