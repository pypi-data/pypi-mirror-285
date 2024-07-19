import pandas as pd
import os
from AssayingAnomalies import Config
from concurrent.futures import ProcessPoolExecutor, as_completed
from AssayingAnomalies.Functions.calculate_car3_for_permno import calculate_car3_for_permno


def calculate_car3_multiple_permnos(permnos):
    results = {}
    # Parallel processing
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(calculate_car3_for_permno, permno): permno for permno in permnos}

        for future in as_completed(futures):
            permno = futures[future]
            try:
                results[permno] = future.result()
                print(f"Completed CAR3 calculation for {permno}")
            except Exception as exc:
                print(f"{permno} generated an exception: {exc}")

    return results


def make_CAR3():
    params = Config().load_params()
    crsp_folder = os.path.join(params.crspFolder, '')
    permnos = pd.read_csv(crsp_folder + 'permno.csv', index_col=0).astype(str).values.flatten()
    CAR3 = calculate_car3_multiple_permnos(permnos)
    CAR3 = pd.DataFrame(CAR3)
    CAR3 = CAR3.reindex(columns=permnos)
    CAR3.to_csv(crsp_folder + 'CAR3.csv', index=True)
    print("Finished 3-month cumulatve abnormal returns (CAR3).")
    return


if __name__ == '__main__':
    car3 = make_CAR3()

