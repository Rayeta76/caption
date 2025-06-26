# Caption

Caption (also known as *StockPrep*) is a small GUI application for generating image captions using the [Florence‑2](https://aka.ms/florence) model. It processes entire folders of images, producing a description, detected objects and simple keywords for each file. Results can be exported in JSON, CSV or XML format and images may optionally be renamed or copied to a separate directory.

## Installation

1. Clone this repository.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   A CUDA‑enabled GPU is recommended to run the model.

## Usage

Run the application with:
```bash
python main.py
```
This launches the StockPrep window. From there you can:

1. Select the folder containing your images.
2. Choose an output directory.
3. Load the Florence‑2 model (the first time may take a while).
4. Click **Process** to generate captions. Progress and logs appear in the window.

Processed images and the export file will be placed in the output folder you selected.
