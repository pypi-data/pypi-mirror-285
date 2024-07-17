
# AILungMeasure

AILungMeasure is a Python package designed for automated lung size measurements using deep learning and computer vision on portable chest radiographs. This package aims to improve accuracy, reduce variability, and streamline the lung transplantation size matching process.

## Features

- Automated lung mask extraction from chest radiographs
- Feature points detection to generate lung height and width measurements
- Validation against measurements reported by radiologists
- Robust performance even with technically challenging radiographs

## Installation

You can install AILungMeasure via pip:

```bash
pip install AILungMeasure
```

## Usage

### Loading the Model

AILungMeasure includes a pre-trained model for lung size measurements. You can load the model using:

```python
import AILungMeasure

# Load the pre-trained model
model = AILungMeasure.load_model()
```

### Segmenting Lung Images

To segment lung images and generate measurements, use the `segment` function:

```python
im_folder = '/path/to/your/dicom/images'
imagename = os.path.join(im_folder, 'example_image')

out_name = './output_directory'

# Segment the lung image
AILungMeasure.segment(imagename, out_name, model=model, equalize=1, out_dicom=1)
```

### Plotting Measurements

To plot the lung measurements, use the `plot_measurments` function:

```python
AILungMeasure.plot_measurments(out_name, imname=imagename, plot=1, alpha=0.5, cmap='jet', radius=40)
```

### Example Script

Here’s a complete example script using AILungMeasure:

```python
import AILungMeasure
import os

# Load the pre-trained model
model = AILungMeasure.load_model()

# Example paths (update these paths as needed)
im_folder = '/path/to/your/dicom/images'
imagename = os.path.join(im_folder, 'example_image')

out_name = './output_directory'

# Perform segmentation
AILungMeasure.segment(imagename, out_name, model=model, equalize=1, out_dicom=1)

# Plot measurements
AILungMeasure.plot_measurments(out_name, imname=imagename, plot=1, alpha=0.5, cmap='jet', radius=40, mode=1)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and use a feature branch. Pull requests should be made against the `main` branch.

## Contact

For questions or issues, please contact Mostafa Ismail at mostafa.ismail.k@gmail.com.
