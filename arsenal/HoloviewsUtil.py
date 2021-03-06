import numpy as np
import holoviews as hv


####################################################################################################
# Assemble and show the patterns
####################################################################################################
def assemble_patterns_image(data_holder, data_shape,
                            row_num, col_num, index,
                            value_range, height, width):
    """
    After the program has obtained the index of the patterns in the selected region,
    this function randomly choose several of the patterns to show in a grid-space.

    :param data_holder: The holder containing all the data shown in the diagram
    :param row_num: The row number of the grid space
    :param col_num: The column number of the grid space
    :param index: The index of all the data in the selected region
    :param value_range: The range of values to show a numpy array as RGB image.
    :param data_shape: The pattern shape
    :param height: The height of the samples in the sample panel
    :param width: The width of the samples in the sample panel.
    :return: hv.GridSpace
    """
    index = np.array(index)
    index_num = index.shape[0]

    if index_num >= row_num * col_num:

        # Randomly choose some index
        np.random.shuffle(index)
        # idxes: indexes for the chosen patterns
        idxes = index[:row_num * col_num]
        idxes = idxes.reshape((row_num, col_num))

        # Create a holder
        image_holder = {}
        for x in range(row_num):
            for y in range(col_num):
                tmp_image = hv.Image(data_holder[idxes[x, y]]).options(height=height,
                                                                       width=width,
                                                                       cmap='jet'
                                                                       ).redim.range(
                    z=(value_range[0],
                       value_range[1]))

                image_holder.update({(x, y): tmp_image})

    else:
        # When we do not have so many patterns, first show all the patterns available
        index_list = [(x, y) for x in range(row_num) for y in range(col_num)]
        image_holder = {}
        for l in range(index_num):
            tmp_image = hv.Image(data_holder[index[l]]).options(height=height,
                                                                width=width,
                                                                cmap='jet'
                                                                ).redim.range(z=(value_range[0],
                                                                                 value_range[1]))
            image_holder.update({index_list[l]: tmp_image})

        # Use blank image to fill in the other spaces
        image_holder.update({index_list[l]: hv.Image(np.zeros(data_shape,
                                                              dtype=np.float64)).options(
            height=height,
            width=width,
            cmap='jet')
                             for l in range(index_num, row_num * col_num)})

    return hv.GridSpace(image_holder).options(shared_xaxis=False, shared_yaxis=False)


def assemble_patterns_curve(y_data_array, x_data, row_num, col_num, index, height, width):
    """
    After the program has obtained the index of the patterns in the selected region,
    this function randomly choose several of the patterns to show in a grid-space.

    Specifically, each pattern in this function is a holoview curve object. This function also
    assume that all curves share the same x-axis.

    :param y_data_array: 2D numpy array of the shape [n, curve_length] where n is the
                        pattern number in total.
    :param x_data: The x coordinate of the curve.
    :param row_num: The row number of the grid space
    :param col_num: The column number of the grid space
    :param index: The index of all the data in the selected region
    :param height: The height of the samples in the sample panel
    :param width: The width of the samples in the sample panel.
    :return: hv.GridSpace
    """
    index = np.array(index)
    index_num = index.shape[0]

    # Get the span of x
    x_span = (x_data.max() - x_data.min())

    if index_num >= row_num * col_num:

        # Extract some samples from all the selected ones.
        np.random.shuffle(index)
        sampled_index = index[:row_num * col_num]
        sampled_index = sampled_index.reshape((row_num, col_num))

        # Assemble the patterns
        image_holder = {}
        for x in range(row_num):
            for y in range(col_num):
                # Get the span of the y values
                y_data = y_data_array[sampled_index[x, y]]
                y_span = y_data.max() - y_data.min()

                image_holder.update({(x, y): hv.Curve((x_data,
                                                       y_data
                                                       )).options(width=width,
                                                                  height=height
                                                                  ).redim.range(
                    x=(x_data.min() - x_span * 0.05,
                       x_data.max() + x_span * 0.05),
                    y=(y_data.min() - y_span * 0.05,
                       y_data.max() + y_span * 0.05))})
    else:
        # When we do not have so many patterns, first layout
        # all the patterns available and then fill the other
        # positions with patterns of zeros.
        index_list = [(x, y) for x in range(row_num) for y in range(col_num)]

        # Assemble the True patterns
        image_holder = {}
        for l in range(index_num):
            # Get the span of the y values
            y_data = y_data_array[index[l]]
            y_span = y_data.max() - y_data.min()

            image_holder.update({index_list[l]: hv.Curve((x_data,
                                                          y_data)
                                                         ).options(width=width,
                                                                   height=height
                                                                   ).redim.range(
                x=(x_data.min() - x_span * 0.05,
                   x_data.max() + x_span * 0.05),
                y=(y_data.min() - y_span * 0.05,
                   y_data.max() + y_span * 0.05))})

        # Assemble the psudo-image
        image_holder.update({index_list[l]: hv.Curve((x_data,
                                                      np.zeros_like(x_data))
                                                     ).options(width=width,
                                                               height=height
                                                               ).redim.range(x=(x_data.min()
                                                                                - x_span * 0.05,
                                                                                x_data.max()
                                                                                + x_span * 0.05),
                                                                             y=(-0.1, 1))
                             for l in range(index_num, row_num * col_num)})

    return hv.GridSpace(image_holder).options(shared_xaxis=False, shared_yaxis=False)
