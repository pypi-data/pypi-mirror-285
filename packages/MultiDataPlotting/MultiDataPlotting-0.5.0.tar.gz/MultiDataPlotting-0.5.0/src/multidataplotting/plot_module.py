import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
import copy
from scipy.stats import kde
from scipy.optimize import curve_fit
from scipy.interpolate import griddata
from matplotlib.colors import to_rgba
from matplotlib.colors import Normalize, ListedColormap, LinearSegmentedColormap
from matplotlib.colorbar import ColorbarBase
from matplotlib.cm import get_cmap
import matplotlib.patches as patches
from matplotlib.legend_handler import HandlerPatch
from datetime import datetime, timedelta


class __HandlerRect(HandlerPatch):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        # Customize the size and location of the rectangle for the legend symbol
        center = 0.5 * width - 0.5 * xdescent, 0.5 * ydescent
        p = patches.Rectangle(xy=center, width=width * 0.6, height=height * 1.5)  # Custom size
        self.update_prop(p, orig_handle, legend)
        p.set_transform(trans)
        return [p]

def __create_transparent_cmap(cmap, alpha=0.5):
    """Create a transparent version of the given colormap."""
    colors = cmap(np.arange(cmap.N))
    colors[:, -1] = alpha  # Set the alpha channel
    return LinearSegmentedColormap.from_list(cmap.name + "_alpha", colors)
def __get_bar_data(input_list, bin_tuple_list):
    # bin_tuple_list is a list of tuples, each tuple contains the start and end of a bin
    res = []
    for i in range(len(bin_tuple_list)):
        if i == 0:
            end = bin_tuple_list[i]
            start = -999
        elif i == len(bin_tuple_list) - 1:
            start = bin_tuple_list[i]
            end = 999999
        else:
            start, end = bin_tuple_list[i][0], bin_tuple_list[i][1]
        count = 0
        for j in range(len(input_list)):
            if start <= input_list[j] < end:
                count += 1
        res.append(count)
    return res

def __find_bin_ind(val, bin_ticks, min_val = 0, max_val = 999999):
    if min_val <= val < bin_ticks[0]:
        return 0
    elif val >= bin_ticks[-1]:
        return len(bin_ticks)
    else:
        for i in range(len(bin_ticks) - 1):
            temp_tick = bin_ticks[i]
            if temp_tick <= val < bin_ticks[i + 1]:
                return i + 1
    

def __analyze_cross_relationship(data, key1, key2, key1_ticks = None, key2_ticks = None, x_scale = 1, y_scale = 1):
    """
    Analyzes the cross-relationship between two variables in a list of dictionaries.

    :param data: List of dictionaries containing the data.
    :param key1: The first key in the dictionaries to analyze.
    :param key2: The second key in the dictionaries to analyze.
    :return: A dictionary with keys as tuple pairs of values from key1 and key2, and values as their frequency.
    """
    pair_frequency = {}
    if isinstance(data, pd.DataFrame):
        for index, row in data.iterrows():
            # Extract the values associated with key1 and key2
            value1 = row.get(key1) / x_scale
            value2 = row.get(key2) / y_scale
            
            # Skip entries where either key is missing
            if value1 is None or value2 is None:
                continue
            
            # Create a tuple from the two values
            if key1_ticks is None or key2_ticks is None:
                key_pair = (value1, value2)
            else:
                key_pair = (__find_bin_ind(value1, key1_ticks), __find_bin_ind(value2, key2_ticks))
            if key_pair[0] is None:
                print(value1)
            # Increment the count for this key pair in the dictionary
            if key_pair in pair_frequency:
                pair_frequency[key_pair] += 1
            else:
                pair_frequency[key_pair] = 1
    else:
        for entry in data:
            #print(entry)
            # Extract the values associated with key1 and key2
            value1 = entry.get(key1) / x_scale
            value2 = entry.get(key2) / y_scale
            
            # Skip entries where either key is missing
            if value1 is None or value2 is None:
                continue
            
            # Create a tuple from the two values
            if key1_ticks is None or key2_ticks is None:
                key_pair = (value1, value2)
            else:
                key_pair = (__find_bin_ind(value1, key1_ticks), __find_bin_ind(value2, key2_ticks))
            if key_pair[0] is None:
                print(value1)
            # Increment the count for this key pair in the dictionary
            if key_pair in pair_frequency:
                pair_frequency[key_pair] += 1
            else:
                pair_frequency[key_pair] = 1

    return pair_frequency

def __generate_ticklabels(tick_bins, is_close_1, is_close_2):
        res = []
        if not is_close_1:
            res.append(f'<{tick_bins[0]}')
        for i in range(len(tick_bins) - 1):
            res.append(f'{tick_bins[i]}-{tick_bins[i + 1]}')
        if not is_close_2:
            res.append(f'>{tick_bins[-1]}')
        return res

def __process_text_labels(orig_label, sep='_'):
    lowercase_words = {'of', 'at', 'on', 'in', 'to', 'for', 'with', 'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'so', 'yet', 'against'}
    
    # Split the sentence into words
    words = orig_label.split(sep)
    
    # Capitalize the first word and others based on their position and whether they are in the lowercase_words set
    title_cased_words = [words[0].capitalize()] + [word.capitalize() if word.lower() not in lowercase_words else word for word in words[1:]]
    
    # Join the words back into a sentence
    return ' '.join(title_cased_words)

def __generate_bin_ticks(data, num_bins, mode='data', smart_round=False):
    """
    Generate bin ticks based on percentiles or range for given data, with optional generalized smart rounding.
    
    Args:
    data (sequence): A sequence of numeric data (list, tuple, numpy array, etc.).
    num_bins (int): The number of bins to divide the data into.
    mode (str): 'data' for percentile-based bins, 'range' for evenly spaced bins.
    smart_round (bool): Apply generalized smart rounding to the bin edges based on their magnitude.
    
    Returns:
    np.array: An array containing the bin edges.
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)  # Convert data to numpy array if not already
    
    if mode == 'data':
        percentiles = np.linspace(0, 100, num_bins + 1)
        bin_edges = np.percentile(data, percentiles)
    elif mode == 'range':
        min_val, max_val = np.min(data), np.max(data)
        bin_edges = np.linspace(min_val, max_val, num_bins + 1)
    else:
        raise ValueError("Mode must be 'data' or 'range'")

    if smart_round:
        bin_edges = np.vectorize(__smart_rounding)(bin_edges)
    
    return bin_edges   

def __smart_rounding(value):
    """
    Dynamically round the value based on its magnitude.
    
    Args:
    value (float): The value to be rounded.
    
    Returns:
    float: The rounded value.
    """
    if value == 0:
        return 0
    magnitude = int(np.floor(np.log10(abs(value))))
    if magnitude < -2:
        return round(value, -magnitude + 1)
    elif magnitude < 0:
        return round(value, -magnitude)
    else:
        power = 10 ** magnitude
        return round(value / power) * power
    
def __generate_levels(data, num_levels, density_threshold = None):
    """
    Generate contour levels based on the data and number of levels.
    """
    if density_threshold == None:
        levels = np.linspace(data.min(), data.max(), num_levels)
    else:
        bottom_thresh = max(data.min(), density_threshold)
        levels = np.linspace(bottom_thresh, data.max(), num_levels - 1)
    return levels

def __find_tick_digits(input_val):
    if input_val == 0:
        return 0
    magnitude = int(np.floor(np.log10(abs(input_val))))
    return magnitude
    
def __round_to_nearest(number, power):
    factor = 10 ** power
    return round(number / factor) * factor

def plot_bar_plots(list_of_lists, tuple_range_list, titles = '', ylabels='', bar_color='blue', bar_edgecolor='black', fig_size=(10, 6), tick_fontname='Arial',
                    tick_fontsize=12, title_fontsize=14, label_fontsize=14, line_color='red', show_all_xticklabels=True, bar_width = 1,
                    line_style='--', line_width=2, is_legend=False, unit='m', is_fixed_y_range=True, y_range=[0, 20], is_mean_value = False,
                    is_scaled=False, scale_factor=10, save_path='', is_show=False, is_save=True, transparent_bg=True, horizontal = True, 
                    convert_minute = True, hspace=0.05):
    '''
    This function is used to plot multiple bar plots in one figure. The input data should be a list of lists, where each list contains the data for one bar plot.
    
    Parameters:
    list_of_lists: list of lists, the input data for the bar plots
    tuple_range_list: list of tuples, the range of each bar
    titles: str or list of str, the title of each bar plot, if it is empty, no title will be shown
    ylabels: str or list of str, the y label of each bar plot, if it is empty, no y label will be shown
    bar_color: str, the color of the bars
    bar_edgecolor: str, the edge color of the bars
    fig_size: tuple, the size of the figure
    tick_fontname: str, the font name of the ticks
    tick_fontsize: int, the font size of the ticks
    title_fontsize: int, the font size of the titles
    label_fontsize: int, the font size of the labels
    line_color: str, the color of the mean line
    show_all_xticklabels: bool, whether to show all x tick labels
    bar_width: float, the width of the bars
    line_style: str, the style of the mean line
    line_width: float, the width of the mean line
    is_legend: bool, whether to show the legend
    unit: str, the unit of the data
    is_fixed_y_range: bool, whether to fix the y range
    y_range: list, the y range
    is_mean_value: bool, whether to show the mean value
    is_scaled: bool, whether to scale the data
    scale_factor: float, the scale factor
    save_path: str, the path to save the figure
    is_show: bool, whether to show the figure
    is_save: bool, whether to save the figure
    transparent_bg: bool, whether to set the background to be transparent
    horizontal: bool, whether to plot the bar horizontally
    convert_minute: bool, whether to convert the x tick labels to minutes
    hspace: float, the space between subplots
    
    Returns:
    None
    
    If you want to customize the plot, you can modify the code in this function.
    
    '''
    
    n = len(list_of_lists)
    w, h = fig_size
    
    if is_fixed_y_range and y_range is None:
        max_bar_value = 0
        for data in list_of_lists:
            if is_scaled:
                data = np.array(data) / scale_factor
            bars = __get_bar_data(data, tuple_range_list)
            max_bar_value = max(max_bar_value, bars.max())
        y_range = [0, max_bar_value * 1.05]
    
    fig, axs = plt.subplots(n, 1, figsize=(w, h * n))

    for i, data in enumerate(list_of_lists):
        if is_scaled:
            data = np.array(data) / scale_factor
        
        bar_positions = np.arange(len(tuple_range_list))
        bars = __get_bar_data(data, tuple_range_list)  # This function needs to be defined to get bar data
        bars = np.array(bars) / np.sum(bars) * 100
        if horizontal:
            axs[i].barh(bar_positions, bars, color=bar_color, edgecolor=bar_edgecolor)
        else:
            axs[i].bar(bar_positions, bars, color=bar_color, edgecolor=bar_edgecolor, width=bar_width)
        
        # Calculate and plot the mean line
        if is_mean_value:
            mean_value = np.mean(data)
            axs[i].axvline(mean_value, color=line_color, linestyle=line_style, linewidth=line_width, label=f'Mean: {mean_value:.2f} {unit}')
        
        temp_title = titles if titles == None or isinstance(titles, str) else titles[i]
        if temp_title:
            axs[i].set_title(temp_title, fontsize=title_fontsize, fontname=tick_fontname)
        
        x_tick_labels = []
        convert_factor = 1 if not convert_minute else 60
        for j in range(len(tuple_range_list)):
            if j == len(tuple_range_list) - 1:
                if tuple_range_list[j]/60 >= 1:
                    x_tick_labels.append(f'>{round(tuple_range_list[j]/convert_factor)}')
                else:
                    x_tick_labels.append(f'>{tuple_range_list[j]/convert_factor}')
            elif j == 0:
                if tuple_range_list[j]/60 >= 1:
                    x_tick_labels.append(f'<{round(tuple_range_list[j]/convert_factor)}')
                else:
                    x_tick_labels.append(f'<{tuple_range_list[j]/convert_factor}')
                
            else:
                if tuple_range_list[j][0]/60 >= 1:
                    x_tick_labels.append(f'{round(tuple_range_list[j][0]/convert_factor)}-{round(tuple_range_list[j][1]/convert_factor)}')
                elif tuple_range_list[j][1]/60 >= 1:
                    x_tick_labels.append(f'{tuple_range_list[j][0]/convert_factor}-{round(tuple_range_list[j][1]/convert_factor)}')
                else:
                    x_tick_labels.append(f'{tuple_range_list[j][0]/convert_factor}-{tuple_range_list[j][1]/convert_factor}')
        
        if horizontal:
            axs[i].set_yticks(bar_positions)
            axs[i].set_yticklabels(x_tick_labels,fontsize=tick_fontsize, fontname=tick_fontname)
            # Also needs to make the tick label orientation align with y
            axs[i].tick_params(axis='y', rotation=45)
        else:
            if i == len(list_of_lists) - 1:
                # last x label for each bar should be the range of tuple, also consider that the last tuple should be >, the first should be >
                axs[i].set_xticks(bar_positions)
                axs[i].set_xticklabels(x_tick_labels, fontsize=tick_fontsize, fontname=tick_fontname)
        if i < len(list_of_lists) - 1:
            axs[i].set_xticks([])
        
        if isinstance(ylabels, list) and ylabels[i]:
            axs[i].set_ylabel(ylabels[i], fontsize=label_fontsize, fontname=tick_fontname)
        
        if is_legend:
            axs[i].legend(loc="upper left")
        
        axs[i].grid(False)
        axs[i].tick_params(axis='both', which='major', labelsize=tick_fontsize)
        
        if not show_all_xticklabels and i != n - 1:
            axs[i].set_xticklabels([])
        if is_fixed_y_range:
            axs[i].set_ylim(y_range) if not horizontal else axs[i].set_xlim(y_range)
        if transparent_bg:
            axs[i].patch.set_alpha(0)

    plt.tight_layout()
    plt.subplots_adjust(hspace=hspace)
    if is_show:
        plt.show()
    if is_save:
        if save_path:
            fig.savefig(save_path, dpi=600, transparent=transparent_bg)
        else:
            print("Please provide a valid path to save the figure.")

def draw_cat_bar_curveplots(main_result, other_data_list, bar_colors=None, bar_thickness=0.8, bar_edge_color='black', line_color='black', cat_labels = None,
                       y_range=None, figsize=(10, 6), xlabels = None, ylabels = None, line_thickness=1, tick_fontsize=10, tick_fontname='sans-serif', x_tick_interval=1, is_show=False, 
                       is_save=True, save_path=''):
    '''
    This function is used to draw bar plots with multiple curve plots with a line plot for each dataset.
    
    Parameters:
    main_result: dict, the main result for the stacked bar plot
    other_data_list: list of dict, the other datasets for the line plots
    bar_colors: list, the colors for the bars
    bar_thickness: float, the thickness of the bars
    bar_edge_color: str, the edge color of the bars
    line_color: str, the color of the line plots
    cat_labels: list, the labels for each category
    xlabels: list, the labels for the x-axis
    ylabels: list, the labels for the y-axis
    y_range: list, the y range for each subplot
    figsize: tuple, the size of the figure
    line_thickness: float or list, the thickness of the line plots
    tick_fontsize: int, the font size of the ticks
    tick_fontname: str, the font name of the ticks
    x_tick_interval: int, the interval of the x ticks
    is_show: bool, whether to show the figure
    is_save: bool, whether to save the figure
    save_path: str, the path to save the figure
    
    Returns:
    None
    
    If you want to customize the plot, you can modify the code in this function.
    
    
    '''
    def prepare_data(result):
        dates = list(result.keys())
        values = list(result.values())
        return pd.DataFrame(values, index=pd.to_datetime(dates))
    
    def is_number(variable):
        return isinstance(variable, (int, float))

    main_df = prepare_data(main_result)
    all_series = [prepare_data(data) for data in other_data_list]

    fig, axes = plt.subplots(len(all_series) + 1, 1, figsize=figsize, sharex=True)

    # If bar_colors are not provided, use a default color list
    if bar_colors is None:
        bar_colors = ['#377eb8', '#ff7f00', '#4daf4a', '#e41a1c', '#984ea3']

    # Plot the main result as a stacked bar plot
    bottom_series = None
    for i, col in enumerate(main_df.columns):
        color = bar_colors[i % len(bar_colors)]
        axes[0].bar(main_df.index, main_df[col], bottom=bottom_series, color=color, edgecolor=bar_edge_color, width=bar_thickness, label=col)
        if bottom_series is None:
            bottom_series = main_df[col]
        else:
            bottom_series += main_df[col]

    axes[0].tick_params(axis='x', labelsize=tick_fontsize)
    axes[0].tick_params(axis='y', labelsize=tick_fontsize)
    for tick in axes[0].get_xticklabels():
        tick.set_fontname(tick_fontname)
    for tick in axes[0].get_yticklabels():
        tick.set_fontname(tick_fontname)
    if y_range:
        axes[0].set_ylim(y_range[0])
    if cat_labels == None:
        axes[0].legend()
    else:
        axes[0].legend(cat_labels)

    # Plot each additional dataset as a line plot
    for idx, series in enumerate(all_series, start=1):
        axes[idx].plot(series.index, series.values, color=line_color)
        axes[idx].tick_params(axis='x', labelsize=tick_fontsize)
        axes[idx].tick_params(axis='y', labelsize=tick_fontsize)
        for tick in axes[idx].get_xticklabels():
            tick.set_fontname(tick_fontname)
        for tick in axes[idx].get_yticklabels():
            tick.set_fontname(tick_fontname)
        if y_range:
            axes[idx].set_ylim(y_range[idx])
        if line_thickness is not None:
            if is_number(line_thickness):
                axes[idx].plot(series.index, series.values, color=line_color, linewidth=line_thickness)
            else:
                if line_thickness[idx - 1] != 0:
                    axes[idx].plot(series.index, series.values, color=line_color, linewidth=line_thickness[idx - 1])
                else:
                    axes[idx].scatter(series.index, series.values, color=line_color, s=1)
    if not xlabels:
        xlabels = [''] * (1 + len(other_data_list))
    if not ylabels:
        ylabels = [''] * (1 + len(other_data_list))
    for i, ax in enumerate(axes):
        ax.set_xlabel(xlabels[i])
        ax.set_ylabel(ylabels[i])
        
    # Set date format on x-axis and set tick interval for all subplots
    axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=x_tick_interval))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    fig.autofmt_xdate()  # Auto format x-axis dates for better appearance

    fig.tight_layout()
    if is_show:
        plt.show()
    if is_save:
        if save_path:
            fig.savefig(save_path, dpi=600)
        else:
            print("Please provide a valid path to save the figure.")
            
def plot_histograms(list_of_lists, titles, xlabels='', ylabels='', bins=10, color='blue', edgecolor='black', fig_size=(10, 6), tick_fontname='Arial',
                    tick_fontsize=12, title_fontsize=14, label_fontsize=14, value_range=None, line_color='red', show_all_xticklabels=True,
                    line_style='--', line_width=2, is_legend=False, unit='m', is_log=False, is_log_x=False, is_fixed_y_range=False, 
                    y_range=None, is_mean_value = True, label_sep='_',
                    is_scaled=False, scale_factor=10, save_path='', is_show=False, is_save=True, transparent_bg=True, hspace=0.1):
    
    '''
    This function is used to plot multiple histograms in one figure. The input data should be a list of lists, where each list contains the data for one histogram.
    
    Parameters:
    list_of_lists: list of lists, the input data for the histograms
    titles: list of str, the title of each histogram
    xlabels: str or list of str, the x label of each histogram, if it is empty, no x label will be shown
    ylabels: str or list of str, the y label of each histogram, if it is empty, no y label will be shown
    bins: int, the number of bins
    color: str, the color of the bars
    edgecolor: str, the edge color of the bars
    fig_size: tuple, the size of the figure
    tick_fontname: str, the font name of the ticks
    tick_fontsize: int, the font size of the ticks
    title_fontsize: int, the font size of the titles
    label_fontsize: int, the font size of the labels
    value_range: list, the range of the values
    line_color: str, the color of the mean line
    show_all_xticklabels: bool, whether to show all x tick labels
    line_style: str, the style of the mean line
    line_width: float, the width of the mean line
    is_legend: bool, whether to show the legend
    unit: str, the unit of the data
    is_log: bool, whether to plot the histogram in log scale
    is_log_x: bool, whether to plot the histogram in log scale for x axis
    is_fixed_y_range: bool, whether to fix the y range
    y_range: list, the y range
    is_mean_value: bool, whether to show the mean value
    is_scaled: bool, whether to scale the data
    scale_factor: float, the scale factor
    save_path: str, the path to save the figure
    is_show: bool, whether to show the figure
    is_save: bool, whether to save the figure
    transparent_bg: bool, whether to set the background to be transparent
    hspace: float, the space between subplots
    label_sep: str, the separator for the labels
    Returns:
    None
    
    If you want to customize the plot, you can modify the code in this function.
    
    '''
    
    n = len(list_of_lists)
    w, h = fig_size
    
    if is_fixed_y_range and y_range is None:
        max_frequency = 0
        for data in list_of_lists:
            if is_scaled:
                data = np.array(data) / scale_factor
            if is_log_x:
                min_data, max_data = min(data), max(data)
                bins = np.logspace(np.log10(min_data), np.log10(max_data), bins)
            hist, _ = np.histogram(data, bins=bins, range=value_range)
            max_frequency = max(max_frequency, hist.max())
        y_range = [0, max_frequency * 1.05]
    
    fig, axs = plt.subplots(n, 1, figsize=(w, h * n))
    if xlabels == None:
        xlabels = ['X'] * n
    elif isinstance(xlabels, str):
        xlabels = [xlabels] * n
    if ylabels == None:
        ylabels = ['Frequency (%)'] * n
    elif isinstance(ylabels, str):
        ylabels = [ylabels] * n
    for i, data in enumerate(list_of_lists):
        if is_scaled:
            data = np.array(data) / scale_factor
        
        if is_log_x:
            min_data, max_data = min(data), max(data)
            bins = np.logspace(np.log10(min_data), np.log10(max_data), bins)
            axs[i].hist(data, bins=bins, color=color, edgecolor=edgecolor, weights=np.ones_like(data) / len(data) * 100)
            axs[i].set_xscale('log')
        else:
            axs[i].hist(data, bins=bins, color=color, edgecolor=edgecolor, weights=np.ones_like(data) / len(data) * 100, range=value_range, log=is_log)
        
        # Calculate and plot the mean line
        if is_mean_value:
            mean_value = np.mean(data)
            axs[i].axvline(mean_value, color=line_color, linestyle=line_style, linewidth=line_width, label=f'Mean: {mean_value:.2f} {unit}')
        
        if titles[i]:
            axs[i].set_title(__process_text_labels(titles[i],sep=label_sep), fontsize=title_fontsize, fontname=tick_fontname)

        if xlabels[i]:
            axs[i].set_xlabel(__process_text_labels(xlabels[i], sep=label_sep), fontsize=label_fontsize, fontname=tick_fontname)
        else:
            axs[i].set_xticks([])
        
        if ylabels[i]:
            axs[i].set_ylabel(__process_text_labels(ylabels[i], sep=label_sep), fontsize=label_fontsize, fontname=tick_fontname)
        
        if is_legend:
            axs[i].legend(loc="upper left")
        
        axs[i].grid(False)
        axs[i].tick_params(axis='both', which='major', labelsize=tick_fontsize)
        
        if not show_all_xticklabels and i != n - 1:
            axs[i].set_xticklabels([])
        if is_fixed_y_range:
            axs[i].set_ylim(y_range)
        if transparent_bg:
            axs[i].patch.set_alpha(0)

    plt.tight_layout()
    plt.subplots_adjust(hspace=hspace)
    if is_show:
        plt.show()
    if is_save:
        if save_path:
            fig.savefig(save_path, dpi=600, transparent=transparent_bg)
        else:
            print("Please provide a valid path to save the figure.")
            
def plot_polylines(df, x, ys, line_styles=None, line_widths=None, line_colors=None, legends=None, show_legend=True,
                   marker_colors=None, figsize=(10, 6), x_tick_interval=1, markers=None, y_label = None, label_sep = '_',
                   show_grid=True, font_name='Arial', font_size=12, save_path=None, dpi=600, y_range = None, is_show = True):
    """
    Plots multiple lines from a DataFrame using column indices for x and ys with customizable font settings
    and an option to save the figure.

    Parameters:
    df (DataFrame): The DataFrame containing the data.
    x (int): Index of the column to use as x-axis.
    ys (list of int): List of indices of columns to plot on the y-axis.
    line_styles (dict): Dictionary mapping column indices to line styles.
    line_widths (dict): Dictionary mapping column indices to line widths.
    line_colors (dict): Dictionary mapping column indices to line colors.
    legends (list): Optional list of legend labels.
    marker_colors (dict): Dictionary mapping column indices to marker colors.
    figsize (tuple): Figure size.
    x_tick_interval (int): Interval between x-ticks.
    markers (dict): Dictionary mapping column indices to markers.
    show_grid (bool): Whether to show grid.
    font_name (str): Font name for all text elements.
    font_size (int): Font size for all text elements.
    save_path (str): Path to save the figure. If None, the figure is not saved.
    dpi (int): The resolution in dots per inch of the saved figure.
    label_sep (str): Separator for the labels.
    is_show (bool): Whether to display the plot.
    Returns:
    None
    
    """
    plt.figure(figsize=figsize)
    ax = plt.gca()

    # Set global font properties
    plt.rcParams.update({'font.size': font_size, 'font.family': font_name})

    for y in ys:
        if line_styles is None:
            line_styles = {'-999':'-'}
        if line_widths is None:
            line_widths = {'-999':2}
        if line_colors is None:
            line_colors = {'-999':'blue'}
        if marker_colors is None:
            marker_colors = {'-999':'blue'}
        if markers is None:
            markers = {'-999':''}
        plt.plot(df.iloc[:, x], df.iloc[:, y],
                 linestyle=line_styles.get(y, '-'),  # Default to solid line
                 linewidth=line_widths.get(y, 2),    # Default line width
                 color=line_colors.get(y, 'blue'),   # Default line color
                 marker=markers.get(y, ''),          # Default no markers
                 markerfacecolor=marker_colors.get(y, 'blue'))  # Default marker color

    # Set x-ticks interval
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    # only show the ticks of intervals
    plt.xticks(np.arange(min(df.iloc[:, x]), max(df.iloc[:, x]) + 1, x_tick_interval))
    plt.xticks(rotation=0)
    plt.xlabel(__process_text_labels(df.columns[x], sep=label_sep))
    y_label = "Percent (%)" if y_label is None else y_label
    plt.ylabel(__process_text_labels(y_label, sep = label_sep))
    plt.title("")
    if show_grid:
        plt.grid(True)

    # Legend using column names or provided custom legends
    legend_labels = [df.columns[y] for y in ys] if not legends else legends
    if show_legend:
        plt.legend(legend_labels)
    
    if y_range:
        plt.ylim(y_range)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=dpi)
        print(f"Figure saved to {save_path} at {dpi} dpi.")
    if is_show:
        plt.show()
    
def plot_time_histogram(histogram, color='blue', edgecolor='black', fig_size=(10, 6),
                        tick_fontname='Arial', tick_fontsize=12, title_fontsize=14, 
                        label_fontsize=14, y_range=None, 
                        x_tick_interval_minutes=5, x_ticklabel_format='HH:MM', 
                        is_legend=False, save_path='', is_show=True, 
                        is_save=False, transparent_bg=True):
    '''
    This function is used to plot a histogram of time ranges.
    
    Parameters:
    histogram: dict, the histogram of time ranges
    color: str, the color of the bars
    edgecolor: str, the edge color of the bars
    fig_size: tuple, the size of the figure
    tick_fontname: str, the font name of the ticks
    tick_fontsize: int, the font size of the ticks
    title_fontsize: int, the font size of the titles
    label_fontsize: int, the font size of the labels
    y_range: list, the y range
    x_tick_interval_minutes: int, the interval of the x ticks in minutes
    x_ticklabel_format: str, the format of the x tick labels
    is_legend: bool, whether to show the legend
    save_path: str, the path to save the figure
    is_show: bool, whether to show the figure
    is_save: bool, whether to save the figure
    transparent_bg: bool, whether to set the background to be transparent
    
    '''
    
    fig, ax = plt.subplots(figsize=fig_size)
    
    # Convert the time range strings to datetime objects and calculate bar widths
    starts = []
    ends = []
    values = list(histogram.values())
    for time_range in histogram.keys():
        start_time_str, end_time_str = time_range.split(' - ')
        start_datetime = datetime.strptime(start_time_str, '%H:%M:%S')
        end_datetime = datetime.strptime(end_time_str, '%H:%M:%S')
        starts.append(start_datetime)
        ends.append(end_datetime)
    
    # Plotting the bar chart
    for start, end, value in zip(starts, ends, values):
        width = end - start  # timedelta object
        # Convert width from timedelta to the fraction of the day for plotting
        width_in_days = width.total_seconds() / 86400
        ax.bar(start + width/2, value, width=width_in_days, color=color, edgecolor=edgecolor, align='center')
    
    if y_range:
        ax.set_ylim(y_range)

    ax.xaxis.set_major_formatter(mdates.DateFormatter(x_ticklabel_format))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=x_tick_interval_minutes))
    
    ax.tick_params(axis='both', labelsize=tick_fontsize, labelcolor='black')
    plt.xticks(fontname=tick_fontname)
    plt.yticks(fontname=tick_fontname)
    
    ax.set_title('Histogram of Time Ranges', fontsize=title_fontsize)
    ax.set_xlabel('Time', fontsize=label_fontsize)
    ax.set_ylabel('Frequency', fontsize=label_fontsize)
    
    if is_legend:
        ax.legend()

    if is_save and save_path:
        plt.savefig(save_path, transparent=transparent_bg, bbox_inches='tight', dpi=600)
    
    if is_show:
        plt.show()
    
    plt.close()

def plot_2D_heatmap(pair_freq, x_bin_ticks=None, y_bin_ticks=None, fig_size=(10, 8), title='Cross Relationship Heatmap', title_fontsize=16,
                 xlabel='Variable 1', ylabel='Variable 2', label_fontsize=14, tick_fontsize=12, vmin = None, vmax = None,
                 cmap='viridis', cbar_label='Frequency', save_path='', is_show=True, x_ticklabel_left_close = False, x_ticklabel_right_close = False,
                 y_ticklabel_top_close = False, y_ticklabel_bottom_close = False,is_annotate = False, is_percent = True, label_sep = '_',
                 xtick_rotation=0, ytick_rotation=0, xticklabels=None, yticklabels=None):
    """
    Plots a heatmap of the frequency of tuple pairs.
    
    :param pair_freq: Dictionary with keys as tuple pairs of values and values as their frequency, or orig data with two columns.
    :param fig_size: Size of the figure.
    :param title: Title of the heatmap.
    :param title_fontsize: Font size for the title.
    :param xlabel: Label for the x-axis.
    :param ylabel: Label for the y-axis.
    :param label_fontsize: Font size for labels.
    :param tick_fontsize: Font size for tick labels.
    :param cmap: Color map of the heatmap.
    :param vmin: Minimum value for the color bar.
    :param vmax: Maximum value for the color bar.
    :param is_percent: Whether to show the frequency as a percentage.
    :param cbar_label: Label for the color bar.
    :param save_path: Path to save the figure.
    :param is_show: Whether to display the plot.
    :param x_ticklabel_left_close: Whether to close the left side of x-tick labels.
    :param x_ticklabel_right_close: Whether to close the right side of x-tick labels.
    :param y_ticklabel_top_close: Whether to close the top side of y-tick labels.
    :param y_ticklabel_bottom_close: Whether to close the bottom side of y-tick labels.
    :param is_annotate: Whether to annotate the heatmap with the frequency values.
    :param label_sep: Separator for the labels.
    :param xtick_rotation: Rotation angle of x-tick labels.
    :param ytick_rotation: Rotation angle of y-tick labels.
    :param xticklabels: Custom labels for the x-axis ticks.
    :param yticklabels: Custom labels for the y-axis ticks.
    """
    if isinstance(pair_freq, pd.DataFrame):
        if x_bin_ticks is None:
            x_vals = pair_freq.iloc[:, 0].values
            x_bin_nums = 2 if max(x_vals) - min(x_vals) <= 1 else min(10, max(x_vals) - min(x_vals))
            x_bin_ticks = __generate_bin_ticks(x_vals, x_bin_nums, mode='range')
        if y_bin_ticks is None:
            y_vals = pair_freq.iloc[:, 0].values
            y_bin_nums = 2 if max(y_vals) - min(y_vals) <= 1 else min(10, max(y_vals) - min(y_vals))
            y_bin_ticks = __generate_bin_ticks(y_vals, y_bin_nums, mode='range')
        key1 = pair_freq.columns[0]
        key2 = pair_freq.columns[1]
        
        pair_frequency = __analyze_cross_relationship(pair_freq, key1, key2, x_bin_ticks, y_bin_ticks)
    else:
        pair_frequency = copy.deepcopy(pair_freq)
    
    index = list(range(0, len(x_bin_ticks) - 1))
    columns = list(range(0, len(y_bin_ticks) - 1))
    
    if not x_ticklabel_left_close:
        columns.append(columns[-1] + 1)
    if not x_ticklabel_right_close:
        columns.append(columns[-1] + 1)
    if not y_ticklabel_top_close:
        index.append(index[-1] + 1)
    if not y_ticklabel_bottom_close:
        index.append(index[-1] + 1)

    # Create a DataFrame from the pair_frequency
    data = np.zeros((len(columns), len(index)))
    for (var1, var2), freq in pair_frequency.items():
        i = index.index(var1)
        j = columns.index(var2)
        data[j, i] = freq
    
    if is_percent:
        data = data / np.sum(data) * 100
        
    df = pd.DataFrame(data, index=columns, columns=index)

    # Plotting
    plt.figure(figsize=fig_size)
    if vmin is None or vmax is None:
        heatmap = sns.heatmap(df, annot=is_annotate, fmt=".0f", cmap=cmap, linewidths=.5, 
                          cbar_kws={'label': cbar_label})
    else:
        heatmap = sns.heatmap(df, annot=is_annotate, fmt=".0f", cmap=cmap, linewidths=.5, vmin=vmin, vmax=vmax,
                          cbar_kws={'label': cbar_label})
    plt.title(__process_text_labels(title, sep=label_sep), fontsize=title_fontsize)
    plt.xlabel(__process_text_labels(xlabel, sep=label_sep), fontsize=label_fontsize)
    plt.ylabel(__process_text_labels(ylabel, sep=label_sep), fontsize=label_fontsize)

    # Custom or default tick labels
    if xticklabels is None:
        xticklabels = __generate_ticklabels(x_bin_ticks, x_ticklabel_left_close, x_ticklabel_right_close)
        
    plt.xticks(ticks=np.arange(len(index)) + 0.5, labels=xticklabels, rotation=xtick_rotation, fontsize=tick_fontsize)
    if yticklabels is None:
        yticklabels = __generate_ticklabels(y_bin_ticks, y_ticklabel_top_close, y_ticklabel_bottom_close)
        
    plt.yticks(ticks=np.arange(len(columns)) + 0.5, labels=yticklabels, rotation=ytick_rotation, fontsize=tick_fontsize)
    # Save the plot
    if save_path:
        plt.savefig(save_path, bbox_inches='tight',dpi=600)
    
    # Show the plot
    if is_show:
        plt.show()
    plt.close()

def plot_contour_map(data, fig_size=(10, 8), title='Contour Map', title_fontsize=16,
                     xlabel='X Coordinate', ylabel='Y Coordinate', colorbar_label='Frequency (%)', label_fontsize=14,
                     tick_fontsize=12, contour_levels=20, cmap='viridis', is_contour_line=True,
                     contour_line_colors='white', contour_line_width=1.0, is_contour_label=True,
                     contour_label_color='white', contour_label_size=10, label_interval=2,
                     save_path='', is_show=True, xticks=None, yticks=None, xtick_labels=None, ytick_labels=None):
    """
    Plots a contour map for data with optional tick intervals and custom labels.
    
    :param data: Dictionary or DataFrame containing the data to plot.
    :param fig_size: Size of the figure.
    :param title: Title of the plot.
    :param title_fontsize: Font size for the title.
    :param xlabel: Label for the x-axis.
    :param ylabel: Label for the y-axis.
    :param colorbar_label: Label for the colorbar.
    :param label_fontsize: Font size for labels.
    :param tick_fontsize: Font size for tick labels.
    :param contour_levels: Number of contour levels.
    :param cmap: Colormap for the plot.
    :param is_contour_line: Whether to display contour lines.
    :param contour_line_colors: Color of the contour lines.
    :param contour_line_width: Width of the contour lines.
    :param is_contour_label: Whether to display contour labels.
    :param contour_label_color: Color of the contour labels.
    :param contour_label_size: Font size of the contour labels.
    :param label_interval: Interval for displaying contour labels.
    :param save_path: Path to save the figure.
    :param is_show: Whether to display the plot.
    :param xticks: Custom tick intervals for the x-axis.
    :param yticks: Custom tick intervals for the y-axis.
    :param xtick_labels: Custom labels for the x-axis ticks.
    :param ytick_labels: Custom labels for the y-axis ticks.
    
    """
    if isinstance(data, dict):
        points = np.array([(key[0], key[1]) for key in data.keys()])
        values = np.array(list(data.values()))
    elif isinstance(data, pd.DataFrame):
        if data.shape[1] != 2:
            raise ValueError("DataFrame must have exactly two columns for x and y values.")
        points = np.array([(key[0], key[1]) for key in data.iloc[:, 0].values])
        values = data.iloc[:, -1].values
        print(points)
        print(values)
    else:
        raise TypeError("Input data must be a dictionary or a pandas DataFrame.")

    # Generate a grid to interpolate onto
    x = np.linspace(np.min(points[:, 0]), np.max(points[:, 0]), 100)
    y = np.linspace(np.min(points[:, 1]), np.max(points[:, 1]), 100)
    X, Y = np.meshgrid(x, y)
    
    # Interpolate data
    Z = griddata(points, values, (X, Y), method='cubic')

    # Plotting
    plt.figure(figsize=fig_size)
    plt.contourf(X, Y, Z, levels=contour_levels, cmap=cmap)
    cbar = plt.colorbar()
    cbar.set_label(colorbar_label, size=label_fontsize)
    cbar.ax.tick_params(labelsize=tick_fontsize)

    if is_contour_line:
        contour_lines = plt.contour(X, Y, Z, levels=contour_levels, colors=contour_line_colors, linewidths=contour_line_width)
    if is_contour_line and is_contour_label:
        labels = plt.clabel(contour_lines, inline=True, fontsize=contour_label_size, colors=contour_label_color)
        for label in labels:
            label.set_visible(False)
        for i, label in enumerate(labels):
            if i % label_interval == 0:
                label.set_visible(True)

    plt.title(title, fontsize=title_fontsize)
    plt.xlabel(xlabel, fontsize=label_fontsize)
    plt.ylabel(ylabel, fontsize=label_fontsize)

    # Set custom tick intervals and labels if provided
    if xticks is not None:
        plt.xticks(xticks, xtick_labels if xtick_labels is not None else xticks, fontsize=tick_fontsize)
    else:
        plt.xticks(fontsize=tick_fontsize)
    if yticks is not None:
        plt.yticks(yticks, ytick_labels if ytick_labels is not None else yticks, fontsize=tick_fontsize)
    else:
        plt.yticks(fontsize=tick_fontsize)

    # Save the plot
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    
    # Show the plot
    if is_show:
        plt.show()
    plt.close()
    
def plot_3d_stacked_bar(pair_freq, x_bin_ticks, y_bin_ticks, fig_size=(12, 10), title='3D Stacked Bar Plot', title_fontsize=16,
                        xlabel='Variable 1', ylabel='Variable 2', zlabel='Frequency', label_fontsize=10, tick_fontsize=10, grid_alpha=0.5,
                        color_map=plt.cm.viridis, save_path='', is_show=True, x_ticklabel_left_close = False, x_ticklabel_right_close = False,
                        y_ticklabel_top_close = False, y_ticklabel_bottom_close = False, zmin = None, zmax = None, grid_style='dashed',
                        xtick_rotation=0, ytick_rotation=0, xticklabels=None, yticklabels=None, is_percent=False, elevation=30, azimuth=30,
                        background_color='white'):
    """
    Plots a 3D stacked bar plot of the frequency of tuple pairs.

    :param pair_freq: Dictionary with keys as tuple pairs of values (x, y) and values as their frequency.
    :param fig_size: Size of the figure.
    :param title: Title of the plot.
    :param title_fontsize: Font size for the title.
    :param xlabel: Label for the x-axis.
    :param ylabel: Label for the y-axis.
    :param zlabel: Label for the z-axis.
    :param is_percent: Whether to display the z-axis as a percentage.
    :param label_fontsize: Font size for labels.
    :param tick_fontsize: Font size for tick labels.
    :param color_map: Color map for the bars.
    :param save_path: Path to save the figure.
    :param is_show: Whether to display the plot.
    :param x_ticklabel_left_close: Whether to close the left side of x-tick labels.
    :param x_ticklabel_right_close: Whether to close the right side of x-tick labels.
    :param y_ticklabel_top_close: Whether to close the top side of y-tick labels.
    :param y_ticklabel_bottom_close: Whether to close the bottom side of y-tick labels.
    :param xtick_rotation: Rotation angle of x-tick labels.
    :param ytick_rotation: Rotation angle of y-tick labels.
    :param xticklabels: Custom labels for the x-axis ticks.
    :param yticklabels: Custom labels for the y-axis ticks.
    :param grid_alpha: Transparency of the grid lines.
    :param zmin: Minimum value for the z-axis.
    :param zmax: Maximum value for the z-axis.
    :param elevation: Elevation angle of the plot.
    :param azimuth: Azimuth angle of the plot.
    :param grid_style: Style of the grid lines, solid or dashed.
    :param background_color: Background color of the plot.
    """
    if isinstance(pair_freq, pd.DataFrame):
        if x_bin_ticks is None:
            x_bin_ticks = __generate_bin_ticks(pair_freq.iloc[:, 0], 10, mode='range')
        if y_bin_ticks is None:
            y_bin_ticks = __generate_bin_ticks(pair_freq.iloc[:, 1], 10, mode='range')
        key1 = pair_freq.columns[0]
        key2 = pair_freq.columns[1]
        pair_frequency = __analyze_cross_relationship(pair_freq, key1, key2, x_bin_ticks, y_bin_ticks)
    else:
        pair_frequency = copy.deepcopy(pair_freq)
    
    if is_percent:
        pair_frequency = {key: val / len(pair_freq) * 100 for key, val in pair_frequency.items()}
    
    fig = plt.figure(figsize=fig_size)
    fig.patch.set_facecolor(background_color)  # Set the figure background color
    ax = fig.add_subplot(111, projection='3d')
    
    xs = list(range(0, len(x_bin_ticks) - 1))
    ys = list(range(0, len(y_bin_ticks) - 1))
    
    if not x_ticklabel_left_close:
        xs.append(xs[-1] + 1)
    if not x_ticklabel_right_close:
        xs.append(xs[-1] + 1)
    if not y_ticklabel_top_close:
        ys.append(ys[-1] + 1)
    if not y_ticklabel_bottom_close:
        ys.append(ys[-1] + 1)
    
    # Create data arrays
    xs = np.arange(len(x_bin_ticks) + 1)
    ys = np.arange(len(y_bin_ticks) + 1)
    data = np.zeros((len(ys), len(xs)))

    for (x, y), freq in pair_frequency.items():
        x_index = xs.tolist().index(x)
        y_index = ys.tolist().index(y)
        data[y_index, x_index] += freq

    # Create bars
    for x in xs:
        for y in ys:
            ax.bar3d(x, y, 0, 1, 1, data[y, x], color=color_map(data[y, x] / np.max(data)))

    ax.set_title(title, fontsize=title_fontsize)
    ax.set_xlabel(xlabel, fontsize=label_fontsize, labelpad = 10)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.set_zlabel(zlabel, fontsize=label_fontsize)

    if xticklabels is None:
        xticklabels = __generate_ticklabels(x_bin_ticks, x_ticklabel_left_close, x_ticklabel_right_close)
    
    if yticklabels is None:
        yticklabels = __generate_ticklabels(y_bin_ticks, y_ticklabel_top_close, y_ticklabel_bottom_close)
    # print(xs)
    # print(xticklabels)
    ax.set_xticks(xs + 0.5)
    ax.set_xticklabels(xticklabels, fontsize=tick_fontsize, rotation=xtick_rotation, ha='center')

    ax.set_yticks(ys + 0.5)
    ax.set_yticklabels(yticklabels, fontsize=tick_fontsize, rotation=ytick_rotation, ha = 'left', va='bottom')
    
    if zmin is not None and zmax is not None:
        ax.set_zlim3d(zmin, zmax)
    ax.set_zticklabels(ax.get_zticks(), fontsize=tick_fontsize)
    # Adjust the view angle
    ax.view_init(elev=elevation, azim=azimuth)  # Apply view angle settings
    
    # Make gridlines more transparent
    gridline_style = {'linestyle': grid_style, 'alpha': grid_alpha}
    ax.xaxis._axinfo["grid"].update(gridline_style)
    ax.yaxis._axinfo["grid"].update(gridline_style)
    ax.zaxis._axinfo["grid"].update(gridline_style)
    
    # Save the plot
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=600)
    
    # Show the plot
    if is_show:
        plt.show()
    plt.close()
    
def plot_rose_map(input_data, key_1, key_2, interval=10, value_interval=None,
                  title="Rose Map", label_size=12, label_interval=1, color_ramp="viridis", 
                  tick_label_size = 12, tick_label_color = 'black', tick_font_name='Arial', 
                  figsize=(10, 8), colorbar_label='Intensity',
                  colorbar_label_size=12, max_radius = None, save_path='', is_show=True):
    """
    Plots a rose map for directional data with optional value binning.
    
    Args:
    input_data (pd.DataFrame): The input DataFrame containing the data.
    key_1 (str): The column name for the directional data.
    key_2 (str): The column name for the value data.
    interval (int): The bin size for the directional data in degrees.
    value_interval (int): The bin size for the value data.
    title (str): The title of the plot.
    label_size (int): The font size for the labels.
    label_interval (int): The interval for displaying labels on the plot.
    color_ramp (str): The color ramp to use for the plot.
    tick_label_size (int): The font size for the tick labels.
    tick_label_color (str): The color for the tick labels.
    tick_font_name (str): The font name for the tick labels.
    figsize (tuple): The size of the figure.
    colorbar_label (str): The label for the colorbar.
    colorbar_label_size (int): The font size for the colorbar label.
    max_radius (float): The maximum radius for the plot.
    save_path (str): The path to save the plot.
    is_show (bool): Whether to display the plot.
    
    """
    # Check for required columns
    if key_1 not in input_data.columns or key_2 not in input_data.columns:
        raise ValueError(f"Columns {key_1} and {key_2} must exist in the DataFrame.")

    num_bins = int(360 / interval)
    bin_edges = np.linspace(0, 360, num_bins + 1)
    input_data['binned_direction'] = pd.cut(input_data[key_1], bins=bin_edges, labels=bin_edges[:-1], right=False)

    if value_interval:
        max_value = input_data[key_2].max()
        value_bin_edges = np.arange(0, max_value + value_interval, value_interval)
        input_data['binned_value'] = pd.cut(input_data[key_2], bins=value_bin_edges, labels=value_bin_edges[:-1], right=False)
        grouped = input_data.groupby(['binned_direction', 'binned_value'])[key_2].count().unstack(fill_value=0)
        stats = grouped
    else:
        grouped = input_data.groupby('binned_direction')[key_2].agg(['max', 'mean'])
        stats = grouped

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=figsize)
    cmap = get_cmap(color_ramp)

    # Plot each segment if value_interval is used
    norm = Normalize(vmin=0, vmax=max_value if value_interval else stats['mean'].max())
    if value_interval:
        for idx, row in stats.iterrows():
            base_radius = 0
            for value_idx, count in enumerate(row):
                if count > 0:
                    theta = float(idx) * np.pi / 180
                    radius = count
                    color = cmap(norm(value_idx * value_interval + value_interval / 2))
                    ax.bar(theta, radius, width=np.deg2rad(interval), bottom=base_radius, color=color, edgecolor='black', align='edge')
                    base_radius += radius
    else:
        radii = stats['max']
        colors = [cmap(norm(value)) for value in stats['mean']]
        bars = ax.bar(stats.index.astype(float) * np.pi / 180, radii, width=np.deg2rad(interval), color=colors, edgecolor='black', align='edge')

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks(np.linspace(0, 2 * np.pi, num_bins, endpoint=False))
    ax.set_xticklabels([f"{int(angle)}°" if i % label_interval == 0 else '' for i, angle in enumerate(np.linspace(0, 360, num_bins, endpoint=False))], fontsize=label_size, fontname=tick_font_name)
    ax.set_title(title, va='bottom', fontsize=label_size + 2)

    ax.yaxis.set_tick_params(labelsize=tick_label_size, colors=tick_label_color)
    
    # Customize radial axis
    if max_radius is None:
        max_radius = stats['max'].max() if not value_interval else value_bin_edges[-1]
    ax.set_ylim(0, max_radius)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.1)
    cbar.set_label(colorbar_label, size=colorbar_label_size)
    cbar.ax.tick_params(labelsize=tick_label_size)
    if is_show:
        plt.show()
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi = 600)
        
def plot_rose_contour_map(input_data, key_1, key_2, title="Rose Contour Map", label_size=12, color_ramp="viridis",
                          figsize=(10, 8), num_levels=10, max_radius=None, density_threshold=None, z_label = 'Density',
                          boundary_line_color='black', boundary_line_thickness=2, is_percent = True, tick_spacing = 2,
                          save_path='', is_show=True):
    """
    Plots a rose contour map for directional data with a boundary line at the density threshold, handling cases where no contours are found.
    
    Args:
    input_data (pd.DataFrame): The input DataFrame containing the data.
    key_1 (str): The column name for the directional data.
    key_2 (str): The column name for the value data.
    title (str): The title of the plot.
    label_size (int): The font size for the labels.
    color_ramp (str): The color ramp to use for the plot.
    figsize (tuple): The size of the figure.
    num_levels (int): The number of contour levels to plot.
    max_radius (float): The maximum radius for the plot.
    density_threshold (float): The density threshold for the boundary line.
    z_label (str): The label for the colorbar.
    boundary_line_color (str): The color for the boundary line.
    boundary_line_thickness (float): The thickness of the boundary line.
    is_percent (bool): Whether to show the colorbar as a percentage.
    tick_spacing (int): The spacing between ticks on the colorbar.
    save_path (str): The path to save the plot.
    is_show (bool): Whether to display the plot.
    
    """
    if key_1 not in input_data.columns or key_2 not in input_data.columns:
        raise ValueError(f"Columns {key_1} and {key_2} must exist in the DataFrame.")

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=figsize)

    # Convert directions to radians for plotting
    theta = np.radians(input_data[key_1])
    r = input_data[key_2]

    # Set up the KDE for the polar data
    k = kde.gaussian_kde([theta, r])
    t_i = np.linspace(0, 2 * np.pi, 360)
    r_i = np.linspace(0, r.max() if max_radius is None else max_radius, 100)
    T, R = np.meshgrid(t_i, r_i)
    Z = k(np.vstack([T.ravel(), R.ravel()])).reshape(T.shape)
    # print(Z)
    # Normalize and create the colormap
    norm = Normalize(vmin=Z.min(), vmax=Z.max())
    
    original_cmap = get_cmap(color_ramp)

    colors = original_cmap(np.linspace(0, 1, original_cmap.N))
    
    if density_threshold is not None:
        # Check if the density threshold is within the KDE output range
        if not (Z.min() <= density_threshold <= Z.max()):
            print("Warning: Density threshold is out of the data range. Adjusting to fit within the range.")
            density_threshold = Z.min() + (Z.max() - Z.min()) * 0.1  # Example adjustment
        # Set the colors for the threshold and below to white
        ind = (density_threshold - Z.min()) / (Z.max() - Z.min()) * len(colors)
        
        colors[: int(ind)] = [1, 1, 1, 1]  # RGBA for white
        new_cmap = ListedColormap(colors)
    else:
        new_cmap = original_cmap

    color_levels = __generate_levels(Z, num_levels, density_threshold = density_threshold)
    # Plotting the contour map
    c = ax.contourf(T, R, Z, levels=color_levels, norm=norm, cmap=new_cmap, extend = 'min')

    # Optionally add a boundary line at the threshold
    if density_threshold is not None:
        try:
            cs = ax.contour(T, R, Z, levels=[density_threshold], colors=boundary_line_color, linewidths=boundary_line_thickness)
            for collection in cs.collections:
                for path in collection.get_paths():
                    ax.plot(path.vertices[:, 0], path.vertices[:, 1], color=boundary_line_color, linewidth=boundary_line_thickness)
        except ValueError:
            print("No valid contours were found at the specified threshold.")

    # Colorbar
    cbar = plt.colorbar(c, ax=ax, orientation='vertical')
    cbar.set_label(z_label, size=label_size)
    cbar.ax.tick_params(labelsize=label_size)
    
    tick_digits = __find_tick_digits(color_levels[0]) - 1
 
    tick_interval = 10 ** tick_digits * tick_spacing
    
    if density_threshold is not None:
        min_val = __round_to_nearest(density_threshold, tick_digits)
    else:
        min_val = __round_to_nearest(Z.min(), tick_digits)
    tick_positions = np.arange(min_val, __round_to_nearest(Z.max(), tick_digits), tick_interval)
    cbar.set_ticks(tick_positions)
    if is_percent:
        cbar.set_ticklabels([f'{__round_to_nearest(100 * i, tick_digits + 2)}' for i in tick_positions])
    else:
        cbar.set_ticklabels([f'{i}' for i in tick_positions])
    # print(Z.min(), Z.max(), tick_digits, 10**tick_digits)
    # print(__round_to_nearest(Z.max(), tick_digits - 1))
    # print(tick_positions)
    # Setting labels and title
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks(np.linspace(0, 2 * np.pi, 8, endpoint=False))
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    ax.set_title(title, va='bottom', fontsize=label_size + 2)
    if is_show:
        plt.show()
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=600)

def plot_cdfs(data_lists, figsize=(10, 6), line_styles=None, line_widths=None,
              line_colors=None, legends=None, marker_colors=None, x_tick_interval=10,
              markers=None, show_grid=True, font_name='Arial', font_size=12, save_path=None,
              dpi=100, is_same_figure=True, is_log_x=False):
    """
    Plot the CDF for each set of data in data_lists with extensive customization options,
    including the option to plot all on the same figure or on individual subplots, and
    setting the x-axis to logarithmic scale.

    Parameters:
    - data_lists: List of lists, each containing numerical data.
    - figsize: Tuple indicating the figure size.
    - line_styles: Dictionary mapping column indices to line styles.
    - line_widths: Dictionary mapping column indices to line widths.
    - line_colors: Dictionary mapping column indices to line colors.
    - legends: List of legend labels.
    - marker_colors: Dictionary mapping column indices to marker colors.
    - x_tick_interval: Interval between x-ticks.
    - markers: Dictionary mapping column indices to markers.
    - show_grid: Whether to show grid lines.
    - font_name: Font name for all text elements.
    - font_size: Font size for all text elements.
    - save_path: Path to save the figure. If None, the figure is not saved.
    - dpi: The resolution in dots per inch of the saved figure.
    - is_same_figure: Whether to plot all datasets in the same figure.
    - is_log_x: Whether to use a logarithmic scale for the x-axis.
    """
    if is_same_figure:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig, axs = plt.subplots(len(data_lists), 1, figsize=figsize)
    
    plt.rc('font', family=font_name, size=font_size)

    for i, data in enumerate(data_lists):
        sorted_data = np.sort(data)
        yvals = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

        style = line_styles.get(i, '-')
        width = line_widths.get(i, 1)
        color = line_colors.get(i, 'b')
        marker = markers.get(i, None)
        marker_color = marker_colors.get(i, color)
        legend = legends[i] if legends and i < len(legends) else f"Data {i+1}"

        current_ax = ax if is_same_figure else axs[i]
        
        if is_log_x:
            current_ax.set_xscale('log')

        current_ax.plot(sorted_data, yvals, linestyle=style, linewidth=width, color=color,
                        marker=marker, markerfacecolor=marker_color, label=legend)
        
        if x_tick_interval and not is_log_x:
            current_ax.set_xticks(np.arange(0, 1.1, 1 / x_tick_interval))
        
        if show_grid:
            current_ax.grid(True)

        current_ax.legend()

    plt.suptitle("CDF Plots of Given Datasets")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if save_path:
        plt.savefig(save_path, dpi=dpi)
    
    plt.show()

def plot_intensity_velocity_and_classes(intensity_data, velocity_list, classification_data, v_choice='component',
                                                 primary_colormap='jet', edge_colormap='rainbow',
                                                 edge_thickness=2, face_alpha=1.0, arrow_scale=0.1,
                                                 face_label = None, edge_label = None, class_labels = None, is_legend = True,
                                                 is_show = True, save_path = None,
                                                 arrow_colors='black', arrow_styles='->', arrow_thicknesses=1, figsize=(10, 8)):
    """
    Plots a heatmap with edges, velocity arrows, and classification patterns.

    Parameters:
    - intensity_data (list of np.array): List containing up to two 2D numpy arrays with intensity values.
    - velocity_list (list of np.array): List containing pairs of arrays representing velocity components.
    - classification_data (list of np.array): List containing a single array with classification integers for each cell.
    - v_choice (str): 'component' for Cartesian coordinates, 'theta' for polar coordinates (magnitude, direction).
    - primary_colormap (str), edge_colormap (str): Colormap identifiers.
    - edge_thickness (float): Thickness of the edges.
    - face_alpha (float): Transparency of the cell faces.
    - arrow_scale (float): Scaling factor for the arrows.
    - face_label (str), edge_label (str): Labels for the colorbars.
    - class_labels (list): List of class labels for the legend.
    - is_legend (bool): Whether to display the legend.
    - is_show (bool): Whether to display the plot.
    - save_path (str): Path to save the plot.
    - arrow_colors, arrow_styles, arrow_thicknesses: Properties for arrows.
    - figsize (tuple): Figure size.
    """
    fig, ax = plt.subplots(figsize=figsize)
    data = intensity_data[0]
    n_rows, n_cols = data.shape

    # Normalize the face colors
    norm = Normalize(vmin=np.min(data), vmax=np.max(data))
    face_cmap = get_cmap(primary_colormap)
    face_colors = face_cmap(norm(data))

    # Prepare patterns based on classification data
    patterns = ['/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*', '///', '\\\\', '|||', '---', 'xxx', 'ooo', 'OOO', '...', '***']
    class_data = classification_data[0]
    if class_labels ==  None:
        pattern_handles = [patches.Patch(facecolor='white', edgecolor = 'black', hatch=pat, label=f'Class {i+1}') \
            for i, pat in enumerate(patterns[:len(np.unique(class_data))])]
    else:
        pattern_handles = [patches.Patch(facecolor='white', edgecolor = 'black', hatch=pat, label=class_labels[i]) \
            for i, pat in enumerate(patterns[:len(np.unique(class_data))])]
    # Prepare edge colors if provided
    if len(intensity_data) > 1:
        edge_data = intensity_data[1]
        edge_norm = Normalize(vmin=np.min(edge_data), vmax=np.max(edge_data))
        edge_cmap = get_cmap(edge_colormap)
        edge_colors = edge_cmap(edge_norm(edge_data))
    else:
        edge_data = None
        
    for i in range(n_rows):
        for j in range(n_cols):
            face_color = face_colors[i, j]
            pattern = patterns[class_data[i, j] % len(patterns)]
            if len(intensity_data) > 1:
                edge_color = edge_colors[i, j]
                # Two rectangles to manage separate face and edge coloring
                rect0 = plt.Rectangle((j + 0.01, n_rows - i - 1 + 0.01), 0.99, 0.99, facecolor=face_color,
                                      alpha=face_alpha)
                ax.add_patch(rect0)
                
                pattern_rect = patches.Rectangle((j, n_rows - i - 1), 1, 1, hatch=pattern, fill=False,
                                                edgecolor='black', linewidth=0)
                ax.add_patch(pattern_rect)
                
                rect1 = plt.Rectangle((j + 0.05, n_rows - i - 1 + 0.05), 0.9, 0.9, facecolor='none',
                                      edgecolor=edge_color, linewidth=edge_thickness)
                ax.add_patch(rect1)
                
            else:
                rect = plt.Rectangle((j + 0.01, n_rows - i - 1 + 0.01), 0.99, 0.99, facecolor=face_color,
                                     edgecolor='black', linewidth=edge_thickness, alpha=face_alpha)
                ax.add_patch(rect)
                pattern_rect = patches.Rectangle((j, n_rows - i - 1), 1, 1, hatch=pattern, fill=False,
                                                edgecolor='white' if np.mean(face_color) < 0.5 else 'black', linewidth=0)
                ax.add_patch(pattern_rect)
                
                # Add pattern with transparency
                # Add pattern with contrasting color
            

            # Center of the cell for placing the arrow
            x_center, y_center = j + 0.5, n_rows - i - 0.5

            # Process each pair of arrays in velocity_list
            for k in range(0, len(velocity_list), 2):
                if v_choice == 'component':
                    dx, dy = velocity_list[k][i, j], velocity_list[k+1][i, j]
                elif v_choice == 'theta':
                    magnitude = velocity_list[k][i, j]
                    direction = velocity_list[k+1][i, j]
                    dx = magnitude * np.cos(direction)
                    dy = magnitude * np.sin(direction)

                # Get arrow properties
                color = arrow_colors[k // 2] if isinstance(arrow_colors, list) else arrow_colors
                style = arrow_styles[k // 2] if isinstance(arrow_styles, list) else arrow_styles
                thickness = arrow_thicknesses[k // 2] if isinstance(arrow_thicknesses, list) else arrow_thicknesses

                ax.arrow(x_center, y_center, dx * arrow_scale, dy * arrow_scale, color=color,
                         head_width=0.1, head_length=0.15, linewidth=thickness, linestyle=style)
    if is_legend:
        ax.legend(handles=pattern_handles, title="Classification", handler_map={patches.Patch: __HandlerRect()}, loc='upper left', bbox_to_anchor=(0.98, 0.98))
    # Colorbar for intensity
     # Adding colorbar for face colors
    
    ax.axis('off')  # Turn off axis markers, labels, and grid
    
    if is_legend:
        face_label = face_label if face_label is not None else 'Intensity'
        edge_label = edge_label if edge_label is not None else 'Edge Intensity'
        
        # Adding colorbar for face colors
        face_cbar_ax = fig.add_axes([0.9, 0.15, 0.015, 0.4])  # Adjust these values as needed
        sm_face = plt.cm.ScalarMappable(cmap=__create_transparent_cmap(face_cmap, alpha=face_alpha), norm=norm)
        sm_face.set_array([])
        cbar_face = plt.colorbar(sm_face, cax=face_cbar_ax, orientation='vertical')
        cbar_face.set_label(face_label, fontsize=10)  # Smaller label size
        cbar_face.ax.tick_params(labelsize=10)  # Smaller tick size

        # Adding colorbar for edge colors if applicable
        if edge_data is not None:
            edge_cbar_ax = fig.add_axes([0.97, 0.15, 0.015, 0.4])  # Adjust these values as needed
            sm_edge = plt.cm.ScalarMappable(cmap=edge_cmap, norm=edge_norm)
            sm_edge.set_array([])
            cbar_edge = plt.colorbar(sm_edge, cax=edge_cbar_ax, orientation='vertical')
            cbar_edge.set_label(edge_label, fontsize=10)  # Smaller label size
            cbar_edge.ax.tick_params(labelsize=10)  # Smaller tick size
    if is_show:
        plt.show()
    if save_path:
        plt.savefig(save_path, dpi=600, bbox_inches='tight')