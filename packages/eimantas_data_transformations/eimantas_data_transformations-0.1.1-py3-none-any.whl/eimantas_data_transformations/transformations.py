import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def transpose2d(input_matrix: list[list[float]]) -> list[list[float]]:
    """
    Transposes a 2D matrix (list of lists).

    This function takes a 2D matrix represented as a list of lists and
    returns a new matrix that is the transpose of the input matrix.
    Transposing a matrix means switching the rows and columns.

    Args:
    input_matrix (list[list[float]]): The matrix to be transposed, 
    represented as a list of lists of floats.

    Returns:
    list[list[float]]: The transposed matrix, 
    represented as a list of lists of floats.
    """
    try:
        input_array = np.array(input_matrix)
        number_of_rows, number_of_columns = input_array.shape
        logging.info(f"Transposing a matrix of shape {input_array.shape}")

        transposed_matrix = []

        for col_index in range(number_of_columns):
            new_row = []
            for row_index in range(number_of_rows):
                new_row.append(input_matrix[row_index][col_index])
            transposed_matrix.append(new_row)

        return transposed_matrix
    except Exception as e:
        logging.error(f"Error in transpose2d: {e}")
        raise


def window1d(
    input_array: list[float], size: int, shift: int = 1, stride: int = 1
) -> list[list[float]]:
    """
    Create windows from a 1D array with specified size, shift, and stride.

    Args:
    input_array (list or np.ndarray): The input 1D array of real numbers.
    size (int): The size (length) of each window.
    shift (int): The shift (step size) between different windows.
    stride (int): The stride (step size) within each window.

    Returns:
    list of list: A list containing the windows as lists of floats.
    """
    try:
        if size <= 0 or shift <= 0 or stride <= 0:
            raise ValueError(
                "Size, shift, and stride must be positive integers.")

        input_array = np.array(input_array)
        logging.info(
            f"Creating windows from array of length {len(input_array)} with size={
                size}, shift={shift}, stride={stride}"
        )

        if stride * (size - 1) >= len(input_array):
            raise ValueError(
                "Invalid stride or size. Stride or size are too large for the given input array length."
            )

        if size > len(input_array):
            raise ValueError("Invalid size. Window size is too big to fill.")

        windows = []
        for start in range(0, len(input_array) - (size - 1) * stride, shift):
            window = input_array[start: start + size * stride: stride].tolist()
            windows.append(window)

        return windows
    except Exception as e:
        logging.error(f"Error in window1d: {e}")
        raise


def convolution2d(
    input_matrix: np.ndarray, kernel: np.ndarray, stride: int = 1
) -> np.ndarray:
    """
    Perform a 2D cross-correlation (often referred to as convolution) 
    on the input matrix using the given kernel.

    Args:
    input_matrix (np.ndarray): The input 2D array of real numbers.
    kernel (np.ndarray): The kernel 2D array of real numbers.
    stride (int): The stride for moving the kernel over the input matrix.

    Returns:
    np.ndarray: The resulting 2D array after applying the cross-correlation.
    """
    try:
        if stride <= 0:
            raise ValueError("Stride must be a positive integer.")

        input_height, input_width = input_matrix.shape
        kernel_height, kernel_width = kernel.shape
        logging.info(
            f"Performing 2D convolution with input shape {
                input_matrix.shape}, kernel shape {kernel.shape}, stride={stride}"
        )

        if input_height < kernel_height or input_width < kernel_width:
            raise ValueError(
                "Kernel dimensions must be smaller than input dimensions.")

        output_height = (input_height - kernel_height) // stride + 1
        output_width = (input_width - kernel_width) // stride + 1
        output_matrix = np.zeros((output_height, output_width))

        for i in range(output_height):
            for j in range(output_width):
                start_i = i * stride
                start_j = j * stride
                input_region = input_matrix[
                    start_i: start_i + kernel_height, start_j: start_j + kernel_width
                ]
                output_matrix[i, j] = np.sum(input_region * kernel)

        return output_matrix
    except Exception as e:
        logging.error(f"Error in convolution2d: {e}")
        raise
