import numpy as np
from scipy.stats import truncnorm, multivariate_normal
from scipy.linalg import sqrtm


def q_draw(p, q, c, varu):
    # Check for length mismatch and scalar requirement
    if len(p) != len(q):
        raise ValueError("p and q are of different lengths.")
    if not np.isscalar(c) or not np.isscalar(varu):
        raise ValueError("c and varu should be scalars.")

    # Initialize
    n_obs = len(p)
    q_nonzero = q != 0
    n_skip = 2
    modp = np.mod(range(1, n_obs+1), n_skip)
    ru = np.random.uniform(size=n_obs)
    # print(ru)
    # Create doubled variables
    p2 = np.column_stack((p, p))
    q = np.column_stack((q, q))

    # Iterate over skip values
    for i_start in range(n_skip):
        # Identify indices to update in this iteration
        k = modp == i_start
        jnz = np.where(k & q_nonzero)[0]

        if len(jnz) > 0:
            # Temporary q for calculations
            # temp_q = np.copy(q2)
            q[jnz, 0] = 1
            q[jnz, 1] = -1

            # Compute u
            cq = c * q
            v = p2 - cq
            u = v[1:, :] - v[:-1, :]
            # print(f'u = {u}')

            # Compute s and log odds
            s = (u ** 2) / (2 * varu)
            # print(f"s = {s}")
            s_sum = s[:-1, :] + s[1:, ]
            # The next 2 lines have the effect of adding a row of 0s to the top and bottom of s before summing.
            s_sum = np.insert(s_sum, 0, s[0], axis=0)
            s_sum = np.append(s_sum, [s[-1]], axis=0)
            s_sum_reduced = s_sum[jnz]

            log_odds = s_sum_reduced[:, 1] - s_sum_reduced[:, 0]

            # Prevent overflow in exp
            log_odds[log_odds > 500] = 500
            odds = np.exp(log_odds)
            p_buy = odds / (1 + odds)

            # Draw new q based on probabilities
            qknz = 1 - 2 * (ru[jnz] > p_buy)
            q[jnz, 0] = qknz
            if i_start < n_skip-1:
                q[jnz, 1] = qknz
    q = q[:, 0]
    return q

def q_draw_vec(p, q, c, varu):
    # Validate the lengths of the input arrays
    if len(p) != len(q):
        raise ValueError("p and q are of different lengths.")

    # Check that c and varu are either scalars or arrays of appropriate lengths
    if not (np.isscalar(c) or len(c) == len(p)) or not (np.isscalar(varu) or len(varu) == len(p) - 1):
        raise ValueError("Invalid dimensions for c or varu.")

    # Create a boolean array indicating where q is not zero
    q_nonzero = q != 0

    # Duplicate the price array p and the trade direction array q
    p2 = np.tile(p, (2, 1)).T
    q_double = np.tile(q, (2, 1)).T

    # Define a constant for the number of elements to skip in the loop
    n_skip = 2

    # Create an array for modulo calculations to determine the update pattern
    mod_p = np.mod(np.arange(len(p)), n_skip)

    for i_start in range(n_skip):

        # Calculate indices for updating q based on the current iteration and nonzero elements in q
        k = mod_p == i_start
        jnz = np.where(k & q_nonzero)[0]

        if len(jnz) > 0:
            # Update the elements of q_double to be alternately 1 and -1 for the indices in jnz
            q_double[jnz, 0] = 1
            q_double[jnz, 1] = -1

            # Calculate cq based on whether c is a scalar or a vector
            if np.isscalar(c):
                cq = c * q_double
            else:
                c2 = np.vstack((c, c)).T
                cq = c2 * q_double

            # Compute the difference between doubled prices and cq
            v = p2 - cq
            u = v[1:] - v[:-1]

            # Calculate s based on whether varu is a scalar or a vector
            if np.isscalar(varu):
                s = (u ** 2) / (2 * varu)
            else:
                varu2 = 2 * np.vstack((varu, varu)).T
                s = (u ** 2) / varu2

            # Extend s to have the same length as p
            s_extended = np.vstack([s, np.zeros((len(p2) - len(s), 2))])

            # Calculate s_sum_all by combining s_extended with itself
            s_sum_all = np.vstack((s_extended[:, 0], np.zeros(len(p2)))).T + np.vstack(
                (np.zeros(len(p2)), s_extended[:, 1])).T

            # Select the relevant rows from s_sum_all
            s_sum = s_sum_all[jnz, :]
            log_odds = s_sum[:, 1] - s_sum[:, 0]

            # Adjust log odds to avoid overflow and calculate the odds
            log_okay = log_odds < 500
            odds = np.exp(log_odds * log_okay)

            # Calculate the probability of buying and adjust it based on log_okay
            p_buy = odds / (1 + odds)
            p_buy = p_buy * log_okay

            # Generate random uniform values and calculate qknz
            ru = np.random.uniform(size=len(p_buy))
            qknz = 1 - 2 * (ru > p_buy)

            # Update q at the indices specified in jnz
            q[jnz] = qknz

    # Return the updated q array
    return q


def bayes_regression_update(prior_mu, prior_cov, y, X, d_var):
    if prior_mu.shape[1] != 1:
        raise ValueError("priorMu should be a column vector")
    if X.shape[0] < X.shape[1]:
        raise ValueError(f"X has fewer rows than columns with dimensions {X.shape[0]}x{X.shape[1]}")
    if X.shape[0] != y.shape[0] or y.shape[1] != 1:
        raise ValueError("Dimensions of X and y are not compatible")
    if prior_mu.shape[0] != X.shape[1]:
        raise ValueError("priorMu and X are not conformable")
    if prior_cov.shape[0] != prior_cov.shape[1] or prior_cov.shape[0] != prior_mu.shape[0]:
        raise ValueError("Dimensions of priorCov are not compatible with priorMu")

    # Create a boolean mask for NaN values
    nan_mask_y = np.isnan(y).flatten()  # Flatten y to make it a 1D array for compatibility
    nan_mask_X = np.isnan(X).any(axis=1)  # Check for NaN in any column of X for each row

    # Combine masks to get rows with NaN in either y or X
    combined_mask = nan_mask_y | nan_mask_X

    # Step 2: Filter out rows with NaN from both y and X
    y = y[~combined_mask]
    X = X[~combined_mask]

    # print(f"d_var = {d_var}")
    # print(f"X = {X}")
    # print(f"y = {y}")
    cov_inv = np.linalg.inv(prior_cov)
    # print(f"cov_inv = {cov_inv}")
    Di = (1 / d_var) * np.dot(X.T, X) + cov_inv
    # print(f"Di = {Di}")
    D = np.linalg.inv(Di)
    dd = (1 / d_var) * np.dot(X.T, y) + np.dot(cov_inv, prior_mu)
    # print(f"dd = {dd}")
    post_mu = np.dot(D, dd)
    post_cov = D

    return post_mu, post_cov


def bayes_variance_update(prior_alpha, prior_beta, u):
    """
    Updates the posterior alpha and beta parameters for an inverted gamma distribution.

    Parameters:
    prior_alpha (float): The prior alpha parameter of the inverted gamma distribution.
    prior_beta (float): The prior beta parameter of the inverted gamma distribution.
    u (numpy.ndarray): Vector of estimated disturbances.

    Returns:
    post_alpha (float): Updated posterior alpha parameter.
    post_beta (float): Updated posterior beta parameter.
    """
    u_cleaned = u[~np.isnan(u)]

    # Update the posterior alpha parameter
    post_alpha = prior_alpha + len(u_cleaned) / 2

    # Update the posterior beta parameter
    post_beta = prior_beta + np.sum(u_cleaned ** 2) / 2

    return post_alpha, post_beta


def rand_std_norm_t(zlow, zhigh):
    PROBNLIMIT = 6
    eps = 100 * np.finfo(float).eps # A small epsilon value

    if zlow == float('-inf') and zhigh == float('inf'):
        return np.random.normal()
    if zlow > PROBNLIMIT and (zhigh == float('inf') or zhigh > PROBNLIMIT):
        return zlow + 100 * eps
    if zhigh < -PROBNLIMIT and (zlow == float('-inf') or zlow < -PROBNLIMIT):
        return zhigh - 100 * eps

    a, b = zlow, zhigh
    # print(f"a, b = {a.dtype}, {b.dtype}")
    if zlow == float('-inf'):
        a = -np.inf
    if zhigh == float('inf'):
        b = np.inf

    if not a<=b:
        raise ValueError(f"Invalid bounds for truncnorm: a={a}, b={b}")
    return truncnorm.rvs(a, b, loc=0, scale=1)


def mvnrnd_t(mu, cov, v_lower, v_upper):
    # f = sqrtm(cov).T  # I'm pretty sure this is incorrect.
    f = np.linalg.cholesky(cov).T
    n = np.prod(mu.shape)
    eta = np.zeros(n)
    # print(f"f = sqrtm(cov) = {f}")
    # print(f"eta = np.zeros(n) = {eta}")


    for k in range(n):
        etasum = np.dot(f[k, :k], eta[:k])
        # print(f"etasum = {etasum}")
        low = (v_lower[k] - mu[k] - etasum) / f[k, k]
        high = (v_upper[k] - mu[k] - etasum) / f[k, k]
        eta[k] = rand_std_norm_t(low, high)

    return mu + np.dot(f, eta)


def roll_gibbs_beta(p, pm, q, n_sweeps, reg_draw, varu_draw, q_draw_bool, varu_start, c_start, beta_start):
    """
    Perform Gibbs sampling to estimate parameters in the Roll model.

    Parameters:
    p (numpy.ndarray): Vector of trade prices.
    pm (numpy.ndarray): Vector of mid prices.
    q (numpy.ndarray): Vector of trade directions.
    n_sweeps (int): Number of Gibbs sampling iterations.
    reg_draw (bool): Flag to perform regression draw.
    varu_draw (bool): Flag to perform variance draw.
    q_draw_bool (bool): Flag to perform q draw.
    varu_start (float): Initial value of variance.
    c_start (float): Initial value of cost parameter c.
    beta_start (float): Initial value of beta.
    print_level (int): Verbosity level for printing diagnostics.

    Returns:
    numpy.ndarray: Output matrix with parameters from each sweep. Columns are c, beta, and varu.
    """
    n_obs = len(p)

    # Check for length mismatch
    if len(q) != n_obs or len(pm) != n_obs:
        print('RollGibbsBeta length mismatch')
        return None

    # Calculate price change
    dp = p[1:] - p[:-1]

    # Initialize q based on price sign changes if required
    if q_draw_bool:
        q_initial = np.sign(dp)
        q_initial = np.insert(q_initial, 0, 1)  # Insert 1 at beginning to match length of q
        q = np.where(q != 0, q_initial, q)

    # Initialize variance, cost, and beta parameters
    # print(f"varu_start = {varu_start}")
    varu = max(varu_start, 0.001)
    c = max(c_start, 0.01)
    beta = max(beta_start, 1)

    # Output matrix initialization
    parm_out = np.zeros((n_sweeps, 3))

    for sweep in range(n_sweeps):
        # print(f"Sweep {sweep + 1}/{n_sweeps}")
        # Calculate changes in trade directions and mid prices
        dq = q[1:] - q[:-1]
        dpm = pm[1:] - pm[:-1]
        # Perform regression draw if enabled
        if reg_draw:
            # varu = max(varu_start, 0.001)
            prior_mu = np.array([[0], [1]])  # Prior mean
            prior_cov = np.diag([1, 2])  # Prior covariance
            X = np.column_stack((dq, dpm))  # Design matrix
            # print(f"X has dimensions {X.shape}")
            # print(f'varu = {varu}')
            post_mu, post_cov = bayes_regression_update(prior_mu, prior_cov, dp.reshape(-1, 1), X, varu)
            # print(f"Post cov = {post_cov}")
            coeff_lower = np.array([0, float('-inf')])
            coeff_upper = np.array([float('inf'), float('inf')])
            coeff_draw = mvnrnd_t(post_mu.flatten(), post_cov, coeff_lower, coeff_upper)
            c, beta = coeff_draw[0], coeff_draw[1]  # Extract c and beta

        # Perform variance draw if enabled
        if varu_draw:
            u = dp - c * dq[:len(dp)] - beta * dpm[:len(dp)]  # Calculate disturbances
            prior_alpha = 1e-12
            prior_beta = 1e-12
            post_alpha, post_beta = bayes_variance_update(prior_alpha, prior_beta, u)
            varu = 1 / np.random.gamma(post_alpha, 1 / post_beta)
            # print(f"Sweep {sweep}, varu={varu}, post_alpha={post_alpha}, post_beta={post_beta}")

        # Update q if required
        if q_draw_bool:
            p2 = p - beta * pm
            q = q_draw(p2, q, c, varu)

        # Store parameters in output array
        parm_out[sweep, :] = [c, beta, varu]

    return parm_out

#
# "Testing bayes_regression_update and roll_gibbs_beta"
# # Example test data
# np.random.seed(0)  # for reproducibility
# n_samples = 100
# n_features = 2
#
# X_test = np.random.randn(n_samples, n_features)  # Design matrix
# y_test = np.random.randn(n_samples, 1) * 0.5  # Dependent variable with some noise
#
# prior_mu_test = np.zeros((n_features, 1))  # Prior mean (zero)
# prior_cov_test = np.eye(n_features)  # Prior covariance (identity matrix)
# d_var_test = 0.5  # Variance of error
#
# # Run bayes_regression_update
# post_mu, post_cov = bayes_regression_update(prior_mu_test, prior_cov_test, y_test, X_test, d_var_test)
#
# # Print or inspect the results
# print("Posterior Mean (post_mu):", post_mu)
# print("Posterior Covariance (post_cov):", post_cov)
#
# # Example test data for roll_gibbs_beta
# p_test = np.random.normal(size=100)
# pm_test = np.random.normal(size=100)
# q_test = np.random.choice([-1, 1], size=100)
#
# # Parameters for the Gibbs sampler
# n_sweeps_test = 1000
# reg_draw_test = True
# varu_draw_test = True
# q_draw_test = True
# varu_start_test = 0.001
# c_start_test = 0.01
# beta_start_test = 1
# print_level_test = 1
#
# # Run roll_gibbs_beta
# results = roll_gibbs_beta(p_test, pm_test, q_test, n_sweeps_test, reg_draw_test, varu_draw_test, q_draw_test, varu_start_test, c_start_test, beta_start_test, print_level_test)
#
# # Inspect results
# print("Results from RollGibbsBeta:", results)
#

"To test q_draw"

# # Example test data
# # Define p array
# p = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
#               11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
#               21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
#               31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
#               41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
#               51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
#               61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
#               71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
#               81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
#               91, 92, 93, 94, 95, 96, 97, 98, 99, 100])
#
# # Define q array
# q = np.array([-1, 1, -1, -1, 1, -1, 1, 1, -1, 1,
#               -1, 1, -1, 1, 1, 1, 1, 1, 1, 1,
#               1, -1, -1, -1, -1, 1, 1, -1, -1, -1,
#               1, 1, 1, -1, 1, 1, 1, 1, 1, -1,
#               1, 1, -1, 1, 1, 1, 1, -1, 1, 1,
#               1, 1, -1, -1, -1, 1, -1, 1, 1, 1,
#               1, -1, -1, -1, -1, -1, -1, -1, 1, -1,
#               -1, -1, 1, -1, 1, -1, 1, -1, -1, 1,
#               1, 1, -1, 1, -1, 1, 1, -1, -1, 1,
#               -1, -1, -1, -1, 1, 1, -1, -1, 1, -1])
#
# ru = np.array([
#     0.7223837, 0.1345663, 0.4886556, 0.1905619, 0.968369, 0.1272038, 0.8160228, 0.5720403, 0.8358008, 0.9459323,
#     0.5218109, 0.3258735, 0.7206986, 0.8455685, 0.3894503, 0.5619935, 0.9888516, 0.4692584, 0.7506123, 0.3037273,
#     0.685163, 0.7390812, 0.734625, 0.7475037, 0.6117248, 0.7370916, 0.1971345, 0.3631171, 0.6971642, 0.9983765,
#     0.0003153, 0.6928824, 0.5568195, 0.6228948, 0.6122706, 0.5200895, 0.1128145, 0.80839, 0.1276258, 0.7178436,
#     0.8036793, 0.4268984, 0.7352105, 0.9730008, 0.320453, 0.2439898, 0.9974192, 0.3417673, 0.3071908, 0.5365895,
#     0.267439, 0.7800667, 0.0860517, 0.9082585, 0.5879633, 0.9047471, 0.6610216, 0.5806289, 0.5081874, 0.8883773,
#     0.4213902, 0.7945829, 0.8044851, 0.9464459, 0.2317895, 0.5462842, 0.5559665, 0.6792165, 0.47886, 0.964277,
#     0.7418761, 0.8125367, 0.2915919, 0.4914265, 0.4479994, 0.4391654, 0.0639266, 0.5267615, 0.2011821, 0.2892307,
#     0.1991538, 0.0163052, 0.7327378, 0.721235, 0.4327409, 0.9739116, 0.1942334, 0.5365691, 0.7504959, 0.7876037,
#     0.5749443, 0.8453409, 0.4943481, 0.4200899, 0.263467, 0.1557632, 0.3722185, 0.7363796, 0.582786, 0.6489519
# ])
#
# c = 0.5  # Scalar value
# varu = 2.0  # Scalar value
# print_level = 0  # Verbosity level
#
# q_updated = q_draw(p, q, c, varu, print_level, ru)
