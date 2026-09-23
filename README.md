# Large Number Calculator

## Introduction
This project is created as a tutorial for the Alteryx Platform SDK.

## What is the Large Number Calculator?
This is a custom tool for Alteryx Designer. It accepts numbers exceeding the range of INT64 as strings and performs addition, subtraction, multiplication, and division in arbitrary-precision decimal.

## Tool Description
This tool uses the Python standard library's `decimal.Decimal` for calculations.

The implementation is in `large_number_calculator.py`'s `_calculate` method.

### Specifications

- Converts input values ​​to strings and then to `Decimal`
- Supports `+`, `-`, `*`, and `/`
- Outputs results as a string of `pyarrow.string()` values
- Handles very large integers because it does not convert to Python's standard `float` or Alteryx's INT64
- `Decimal` is a fixed-point, arbitrary-precision decimal type
- If the input is `Null`, the result is also `Null`
- Removes unnecessary trailing zeros
    - `123.4500` → `123.45`
    - `100.0` → `100`
- Exponential notation like `1E+100` is also expanded to standard numeric notation during output.

However, it does not have completely unlimited precision. The current code sets the precision based on the length of the input string.

```
precision = max(len(first_text), len(second_text)) * 2 + 50
```

In other words, calculations are performed with a precision of twice the maximum input length plus 50 digits. While this provides sufficient margin for normal addition, subtraction, and multiplication, division results in repeating decimals, and the result is rounded to this precision.

For example, `1/3` is an infinite decimal, so it is calculated up to the set precision.

Also, if the input source is initially a `float`, it may have been rounded before being passed to Python. For example, if a very long number is stored as a numeric type in Alteryx, precision is lost at that point, so it is important to input large numbers as strings.

## Prerequisites

- Windows 11
- Alteryx Designer 2026.1 or later
- Python 3.13
- Node.js 18 or later (used for UI building)
- npm

Python virtual environments and npm dependency packages are not included in the repository. Create the virtual environment locally using the following steps.

The setup instructions are available on [my Japanese blog](https://analytics-x.tech/archives/9023); please refer to it for further details.

## Setup

In PowerShell, navigate to the project's root directory and create the virtual environment.

```powershell
py -3.13 -m venv alteryx_venv
.\alteryx_venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install ayx_plugin_cli==1.4.0
python -m pip install -r backend\requirements-thirdparty.txt
python -m pip install -r backend\requirements-local.txt
```

If you cannot enable it due to PowerShell's execution policy, call the CLI directly from the virtual environment's executable file.

```powershell
.\alteryx_venv\Scripts\python.exe -m ayx_plugin_cli --help
```

For Command Prompt, use the following:

```
py -3.13 -m venv alteryx_venv
.\alteryx_venv\Scripts\Activate
python -m pip install --upgrade pip
python -m pip install ayx_plugin_cli==1.4.0
python -m pip install -r backend\requirements-thirdparty.txt
python -m pip install -r backend\requirements-local.txt
```

## Building the UI

```powershell
Set-Location ui\LargeNumberCalculator
npm install
npm run build
Set-Location ..\..
```

To launch the development UI, run the following command:

```powershell
Set-Location ui\LargeNumberCalculator
npm start
```

## Testing

Run this in the project root:

```powershell
python -m ayx_plugin_cli test
```

Alternatively, run the test directly. 

```powershell
python -m pytest backend\tests
```
## Installation in Designer

After building the UI, run the following in the project root:

```powershell
python -m ayx_plugin_cli designer-install`
```

After installation, restart Alteryx Designer, and it will be available under "Large Number Calculator" in the Preparation category.

## Creating a YXI Package

To create a YXI file for distribution, run the following after building the UI:

```powershell
python -m ayx_plugin_cli create-yxi`
```

The generated YXI will be output to `build\yxi\`. Even when installed in Designer, the YXI file is created in the same location.

## Directory Structure

```text
backend/ Python backend and tests
configuration/ Alteryx tool settings, icons, and generation settings
DcmSchemas/ DCM schema
ui/LargeNumberCalculator/ UI source and webpack settings
ayx_workspace.json Alteryx SDK workspace settings
```

Local environments and generated files such as `alteryx_venv/`, `build/`, `node_modules/`, `dist/`, and `.ayx_cli.cache/` are excluded using `.gitignore`.

## License

Code derived from the Alteryx SDK/API is subject to the Alteryx SDK and API License Agreement as described in each source file. For licenses of UI-dependent packages, please check the distribution terms of each package.
