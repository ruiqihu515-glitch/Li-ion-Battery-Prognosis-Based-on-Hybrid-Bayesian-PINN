# Reproduction Notes (Smoke Test First, No Full Training)

## 1) Local environment setup

```bash
cd /path/to/Li-ion-Battery-Prognosis-Based-on-Hybrid-Bayesian-PINN
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel setuptools
pip install -r requirements.txt
```

If your environment blocks outbound package downloads, install from your internal mirror or prebuilt wheel cache.

## 2) Data placement (do NOT commit data into GitHub)

- Do **not** store NASA battery data inside tracked repository files.
- `.gitignore` is configured to ignore common data and artifact folders/files.

`TF/battery_data.py` defines:
- `DATA_PATH = '../../data/'` (relative to `TF/`)

### Default directory behavior example

If repository path is:

`~/projects/Li-ion-Battery-Prognosis-Based-on-Hybrid-Bayesian-PINN`

then the default data root resolves to:

`~/projects/data`

## 3) Optional data root overrides

You can override the default data root in two ways:

1. Environment variable:
   ```bash
   export BATTERY_DATA_ROOT=/path/to/data
   python smoke_test.py
   ```
2. Command-line argument (highest priority):
   ```bash
   python smoke_test.py --data-root /path/to/data
   ```

## 4) Expected NASA `.mat` files under data root

- Variable charge dataset:
  - `Battery_Uniform_Distribution_Variable_Charge_Room_Temp_DataSet_2Post/data/Matlab/RW1.mat`
  - `Battery_Uniform_Distribution_Variable_Charge_Room_Temp_DataSet_2Post/data/Matlab/RW2.mat`
  - `Battery_Uniform_Distribution_Variable_Charge_Room_Temp_DataSet_2Post/data/Matlab/RW7.mat`
  - `Battery_Uniform_Distribution_Variable_Charge_Room_Temp_DataSet_2Post/data/Matlab/RW8.mat`

- Discharge dataset:
  - `Battery_Uniform_Distribution_Discharge_Room_Temp_DataSet_2Post/data/Matlab/RW3.mat`
  - `Battery_Uniform_Distribution_Discharge_Room_Temp_DataSet_2Post/data/Matlab/RW4.mat`
  - `Battery_Uniform_Distribution_Discharge_Room_Temp_DataSet_2Post/data/Matlab/RW5.mat`
  - `Battery_Uniform_Distribution_Discharge_Room_Temp_DataSet_2Post/data/Matlab/RW6.mat`

- Charge/discharge dataset:
  - `Battery_Uniform_Distribution_Charge_Discharge_DataSet_2Post/data/Matlab/RW9.mat`
  - `Battery_Uniform_Distribution_Charge_Discharge_DataSet_2Post/data/Matlab/RW10.mat`
  - `Battery_Uniform_Distribution_Charge_Discharge_DataSet_2Post/data/Matlab/RW11.mat`
  - `Battery_Uniform_Distribution_Charge_Discharge_DataSet_2Post/data/Matlab/RW12.mat`

## 5) Run smoke test

```bash
python smoke_test.py
python smoke_test.py --data-root /path/to/data
```

The smoke test verifies:
- dependency imports
- selected data root (default/env/CLI)
- expected `.mat` file presence
- key module imports (`BatteryModels`, `BatteryParameters`, `TF.battery_data`)

## 6) Next steps (still no full training)

1. Ensure dependencies install successfully.
2. Place NASA RW1..RW12 `.mat` files under the chosen data root.
3. Re-run smoke test until all checks pass.
4. Then run lightweight preprocessing only:
   ```bash
   cd TF
   mkdir -p training
   python save_input_data_ref_discharge.py
   python save_input_data_rw_discharge.py
   ```
5. Do **not** run `TF/train_mlp.py` full training (3000 epochs) at this stage.
