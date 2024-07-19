import numpy as np

# :TODO:F the spacing between column labels is off.
def prt_sort_results(res, lsprt=1):
    # print(f"lsprt: {lsprt}, Type: {type(lsprt)}")
    """
    Utility function to optionally print results by runUnivSort().

    Parameters:
    ----------
    res : dict
        A dictionary containing the results returned by runUnivSort().

    lsprt : int, optional
        A flag to indicate whether to print a long/short portfolio or not.
    """

    if res['w'].lower() == 'e':
        www = 'Equally-weighted '
    elif res['w'].lower() == 'v':
        www = 'Value-weighted'

    if isinstance(res['factorModel'], int):
        mdl = f"Fama and French {res['nFactors']}-factor model"
        if res['factorModel'] == 1:
            mdl = 'CAPM'
    else:
        mdl = f"User-defined {res['nFactors']}-factor model"

    heads = [label for label in res['factorLabels']]
    X = np.column_stack((res['xret'], res['alpha'], res['factorLoadings']))
    T = np.column_stack((res['txret'], res['talpha'], res['tfactors']))

    fmtb = "{:7.3f}"
    fmt = "[{:5.2f}]"
    S1 = " "  # one spaces
    S2 = "  "  # two spaces
    max_col_widths = [len(fmtb.format(val)) + 2 * len(S2) for val in X[0, :]]
    B = []
    for j in range(X.shape[0]):
        A = []
        A_t = []
        for i in range(X.shape[1]):
            coeff_space = " " * (max_col_widths[i] - len(fmtb.format(X[j, i])) - 2)
            tstat_space = " " * (max_col_widths[i] - len(fmt.format(T[j, i])) - 2)
            A.append(f"{S2}{fmtb.format(X[j, i])}{coeff_space}")
            A_t.append(f"{S2}{fmt.format(T[j, i])}{tstat_space}")

        B.append(S1.join(A))
        B.append(S1.join(A_t))

    Q = []
    if lsprt==1:
        for j in range(X.shape[0] - 1):
            Q.append(f"{S1}{'              '}{j + 1}")
            Q.append(f"{S1}{'              '}{S1 * 2}")
        Q.append(f"{'              '}L/S")
        Q.append(f"{S1}{'              '}{S1 * 2}")
    else:
        for j in range(X.shape[0]):
            Q.append(f"{S1}{'              '}{j + 1}")
            Q.append(f"{S1}{'              '}{S1 * 2}")

    # else:
    #     Q.append(f"{S1}{'              '}{X.shape[0]}{S1 * 2}")
    #     Q.append(f"{S1}{'              '}{S1 * 2}")

    B = [f"{q}{b}" for q, b in zip(Q, B)]

    c = f"{S1 * 21}xret       alpha"
    # for head in heads:
    #     c += f"{' ' * (9 - len(head))}{head}"
    # c = f"{S1 * 21}xret"
    for idx, head in enumerate(heads):
        spaces = " " * (max_col_widths[idx] - len(head))
        c += f"{spaces}{head}"

    print("     ----------------------------------------------------------------------------------------------------- ")
    print(f"              {www} portfolio sort, {res['hperiod']}-month holding period")
    print("              Excess returns, alphas, and loadings on:")
    print(f"              {mdl}")
    print("     ----------------------------------------------------------------------------------------------------- ")
    print(c)
    print("\n".join(B))
    print("     ----------------------------------------------------------------------------------------------------- ")

    return


# call below to test
# results = runUnivSort(ret.to_numpy(), indFF, me.to_numpy(), dates.values.flatten(), factorModel=1, printResults=1, plotFigure=0)
# prt_sort_results(results, lsprt=1)
# prt_sort_results(results, lsprt=0)
# results2 = runUnivSort(ret.to_numpy(), indFF, me.to_numpy(), dates.values.flatten(), factorModel=6, printResults=1, plotFigure=0)
# prt_sort_results(results2, lsprt=1)