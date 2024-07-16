# Nanosense
Nanosense is a powerful and comprehensive Python package designed for analyzing and visualizing nanopore data. It provides a suite of 12 applications that offer a wide range of tools and functionalities to facilitate the exploration, processing, and interpretation of nanopore measurements.

## Features

- **Plotting and Selecting**: Plot `.abf` and `.hdf5` files, apply low-pass filters, and select specific parts of the file based on various conditions.
- **Data Reduction**: Reduce nanopore data, perform event fitting, standardization, and ML-based data reduction using parallel processing.
- **Data Visualization**: Plot data files, perform PCA analysis, generate correlation matrices, and create density plots.
- **Frequency and Multiplots**: Plot data from different files, calculate the frequency of events per second, and filter data using various filters.
- **Event Analysis**: Analyze individual events in nanopore data and extract meaningful information.
- **Combine Datasets**: Merge datasets from data reduction or ML data obtained from different files.
- **Clustering and Data Reduction**: Cluster events and perform data reduction on individual events for both ML and normal analysis.
- **ML Analysis**: Train and test different ensemble-based and deep learning-based classifiers on nanopore data.
- **Spectrogram and PSD**: Calculate and plot spectrograms and Power Spectral Density (PSD) for selected data.
- **Nanopore Size Calculation**: Determine the size of nanopores based on conductance and solution conductivity measurements.
- **Resource Monitor**: Monitor the utilization of computer resources, including GPU, CPU cores, and RAM.
- **Reduction Settings Viewer**: Easily view and review the settings used for data reduction.

## Installation
You can install Nanosense using pip:
```bash
pip install nanosense
```

## Usage
To get started with Nanosense, simply import the package in your Python script:
```python
import nanosense
```

## Contributing
Contributions to Nanosense are welcome! If you encounter any issues, have suggestions for improvements, or would like to contribute new features, please open an issue or submit a pull request on the GitHub repository.

## License
Nanosense is open-source software released under the MIT License.

## Contact
For any questions or inquiries, please contact Shankar Dutt at [shankar.dutt@anu.edu.au](mailto:shankar.dutt@anu.edu.au).
