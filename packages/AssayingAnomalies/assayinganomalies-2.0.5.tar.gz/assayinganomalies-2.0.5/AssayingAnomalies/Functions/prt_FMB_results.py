def prt_FMB_results(p, bhat, t):
    """
    Print results from Fama-MacBeth regressions.

    :param p: Parsed input object from runFamaMacBeth.
    :param bhat: Vector of coefficient estimates.
    :param t: Vector of t-statistics.
    """
    # Determine the number of variables
    nX = len(bhat) - 1 if p['noConst'] == 0 else len(bhat)

    # Prepare row names
    rnames = []
    if 'labels' in p and p['labels']:
        if p['noConst'] == 1:
            for label in p['labels']:
                rnames.append(f"{label:25}")
        else:
            rnames.append("Constant")
            for label in p['labels']:
                rnames.append(f"{label:25}")
    else:
        for i in range(nX):
            rnames.append(f"var {i+1:20}")
        if p['noConst'] == 0:
            rnames = ['var 0                     '] + rnames

    # Print the results
    print('-' * 70)
    print('           Results from Fama - MacBeth regressions')
    print('-' * 70)
    header_format = "{:25} {:>12} {:>12}"
    print(header_format.format("", "Coeff", "t-stat"))
    for name, coef, t_stat in zip(rnames, bhat, t):
        row_format = "{:25} {:12.3f} {:12.3f}"
        print(row_format.format(name, coef, t_stat))

