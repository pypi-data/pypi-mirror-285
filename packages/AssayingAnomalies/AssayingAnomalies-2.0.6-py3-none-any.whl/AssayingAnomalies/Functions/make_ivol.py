from AssayingAnomalies import Config
import pandas as pd
import os
from AssayingAnomalies.Functions.calculate_ivol_for_permno import calculate_ivol_for_permno
from concurrent.futures import ProcessPoolExecutor, as_completed


def calculate_ivol_multiple_permnos(permnos, window_size, model):
    results = {}
    # Parallel processing
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(calculate_ivol_for_permno, permno, window_size, model): permno for permno in permnos}

        for future in as_completed(futures):
            permno = futures[future]
            try:
                results[permno] = future.result()
                print(f"Completed IVOL calculation for {permno}")
            except Exception as exc:
                print(f"{permno} generated an exception: {exc}")

    return results


def make_ivol():
    params = Config().load_params()
    crsp_folder = os.path.join(params.crspFolder, '')
    permnos = pd.read_csv(crsp_folder + 'permno.csv', index_col=0).astype(str).values.flatten()
    models = ['capm', 'ff3']
    windows = [21, 63]
    for model in models:
        for window in windows:
            if model == 'capm' and window == 21:
                save_name = 'ivol1'
            elif model == 'capm' and window == 63:
                save_name = 'ivol3'
            elif model == 'ff3' and window == 21:
                save_name = 'ff3ivol1'
            else:
                save_name = 'ff3ivol3'
            ivol = calculate_ivol_multiple_permnos(permnos, window, model)
            ivol = pd.DataFrame(ivol)
            ivol = ivol.reindex(columns=permnos)
            ivol.to_csv(crsp_folder + save_name + '.csv', index=True)


if __name__ == '__main__':
    make_ivol()

