# Copyright 2018 Regents of the University of Colorado. All Rights Reserved.
# Released under the MIT license.
# This software was developed at the University of Colorado's Laboratory for Atmospheric and Space Physics.
# Verify current version before use at: https://github.com/MAVENSDC/PyTplot

import os
import pickle
import numpy as np
import pytplot
from pytplot.options import options
from pytplot.store_data import store_data
from pytplot.tplot_options import tplot_options
from scipy.io import readsav
import logging


def tplot_restore(filename):
    """
    This function will restore tplot variables that have been saved with the "tplot_save" command.
    
    .. note::
        This function is compatible with the IDL tplot_save routine.  
        If you have a ".tplot" file generated from IDL, this procedure will restore the data contained in the file.
        Not all plot options will transfer over at this time.   
    
    Parameters:
        filename : str
            The file name and full path generated by the "tplot_save" command.  
            
    Returns:
        None
    
    Examples:
        >>> # Restore the saved data from the tplot_save example
        >>> import pytplot
        >>> pytplot.tplot_restore('C:/temp/variable1.pytplot')

    """
    
    #Error check
    if not (os.path.isfile(filename)):
        logging.error("%s is not a valid file name",filename)
        return
    
    #Check if the restored file was an IDL file
    
    if filename.endswith('.tplot'):
        temp_tplot = readsav(filename)
        for i in range(len(temp_tplot['dq'])):
            if isinstance(temp_tplot['dq'][i][0], str):
                logging.warning("Error reading variable; this error occurs when the variable wasn't loaded in IDL when the SAV file was created.")
                continue

            data_name = temp_tplot['dq'][i][0].decode("utf-8")
            temp_x_data = temp_tplot['dq'][i][1][0][0].squeeze()

            #Pandas reads in data the other way I guess
            if len(temp_tplot['dq'][i][1][0][2].shape) == 4:
                temp_y_data = np.transpose(temp_tplot['dq'][i][1][0][2], axes=(3, 2, 1, 0))
            elif len(temp_tplot['dq'][i][1][0][2].shape) == 3:
                temp_y_data = np.transpose(temp_tplot['dq'][i][1][0][2], axes=(2, 1, 0))
            elif len(temp_tplot['dq'][i][1][0][2].shape) == 2:
                temp_y_data = np.transpose(temp_tplot['dq'][i][1][0][2])
            else:
                temp_y_data = temp_tplot['dq'][i][1][0][2]
            
            # variable contains V1, V2 and V3 (e.g., DF as a function of energy, theta, phi)
            if len(temp_tplot['dq'][i][1][0]) == 10:
                temp_v1_data = temp_tplot['dq'][i][1][0][4]
                temp_v2_data = temp_tplot['dq'][i][1][0][6]
                temp_v3_data = temp_tplot['dq'][i][1][0][8]

                #Change from little endian to big endian, since pandas apparently hates little endian
                #We might want to move this into the store_data procedure eventually
                if (temp_x_data.dtype.byteorder == '>'):
                    temp_x_data = temp_x_data.byteswap().newbyteorder()
                if (temp_y_data.dtype.byteorder == '>'):
                    temp_y_data = temp_y_data.byteswap().newbyteorder()
                if (temp_v1_data.dtype.byteorder == '>'):
                    temp_v1_data = temp_v1_data.byteswap().newbyteorder()
                if (temp_v2_data.dtype.byteorder == '>'):
                    temp_v2_data = temp_v2_data.byteswap().newbyteorder()
                if (temp_v3_data.dtype.byteorder == '>'):
                    temp_v3_data = temp_v3_data.byteswap().newbyteorder()

                # support time-varying depends
                if len(temp_v1_data.shape) == 2:
                    temp_v1_data = np.transpose(temp_v1_data)
                if len(temp_v2_data.shape) == 2:
                    temp_v2_data = np.transpose(temp_v2_data)
                if len(temp_v3_data.shape) == 2:
                    temp_v3_data = np.transpose(temp_v3_data)

                store_data(data_name, data={'x': temp_x_data, 'y': temp_y_data, 'v1': temp_v1_data, 'v2': temp_v2_data, 'v3': temp_v3_data})
            # variable contains V1, V2 (e.g., DF as a function of energy, angle)
            elif len(temp_tplot['dq'][i][1][0]) == 8:
                temp_v1_data = temp_tplot['dq'][i][1][0][4]
                temp_v2_data = temp_tplot['dq'][i][1][0][6]

                #Change from little endian to big endian, since pandas apparently hates little endian
                #We might want to move this into the store_data procedure eventually
                if (temp_x_data.dtype.byteorder == '>'):
                    temp_x_data = temp_x_data.byteswap().newbyteorder()
                if (temp_y_data.dtype.byteorder == '>'):
                    temp_y_data = temp_y_data.byteswap().newbyteorder()
                if (temp_v1_data.dtype.byteorder == '>'):
                    temp_v1_data = temp_v1_data.byteswap().newbyteorder()
                if (temp_v2_data.dtype.byteorder == '>'):
                    temp_v2_data = temp_v2_data.byteswap().newbyteorder()

                # support time-varying depends
                if len(temp_v1_data.shape) == 2:
                    temp_v1_data = np.transpose(temp_v1_data)
                if len(temp_v2_data.shape) == 2:
                    temp_v2_data = np.transpose(temp_v2_data)

                store_data(data_name, data={'x': temp_x_data, 'y': temp_y_data, 'v1': temp_v1_data, 'v2': temp_v2_data})
            #If there are 4 fields, that means it is a spectrogram 
            # 6 fields is a spectrogram with a time varying Y axis
            elif len(temp_tplot['dq'][i][1][0]) == 5 or len(temp_tplot['dq'][i][1][0]) == 6:
                temp_v_data = temp_tplot['dq'][i][1][0][4]
                
                #Change from little endian to big endian, since pandas apparently hates little endian
                #We might want to move this into the store_data procedure eventually
                if (temp_x_data.dtype.byteorder == '>'):
                    temp_x_data = temp_x_data.byteswap().newbyteorder()
                if (temp_y_data.dtype.byteorder == '>'):
                    temp_y_data = temp_y_data.byteswap().newbyteorder()
                if (temp_v_data.dtype.byteorder == '>'):
                    temp_v_data = temp_v_data.byteswap().newbyteorder()
                
                # support time-varying depends
                if len(temp_v_data.shape) == 2:
                    temp_v_data = np.transpose(temp_v_data)

                store_data(data_name, data={'x':temp_x_data, 'y':temp_y_data, 'v':temp_v_data})
            else:
                #Change from little endian to big endian, since pandas apparently hates little endian
                #We might want to move this into the store_data procedure eventually
                if (temp_x_data.dtype.byteorder == '>'):
                    temp_x_data = temp_x_data.byteswap().newbyteorder()
                if (temp_y_data.dtype.byteorder == '>'):
                    temp_y_data = temp_y_data.byteswap().newbyteorder()
                store_data(data_name, data={'x':temp_x_data, 'y':temp_y_data})
            
            if temp_tplot['dq'][i][3].dtype.names is not None:
                for option_name in temp_tplot['dq'][i][3].dtype.names:
                    if option_name.lower() == 'data_att':
                        arr = temp_tplot['dq'][i][3][option_name][0]
                        att_names = arr.dtype.names

                        # extract the values associated with the field names
                        att_values = arr.item()

                        # ensure the values are decoded to strings
                        att_values = [value.decode('utf-8') for value in att_values if isinstance(value, bytes)]

                        # create a dictionary with the desired mappings
                        data_att = {name.lower(): value for name, value in zip(att_names, att_values)}
                        pytplot.data_quants[data_name].attrs['data_att'] = data_att

                    options(data_name, option_name, temp_tplot['dq'][i][3][option_name][0])

            pytplot.data_quants[data_name].attrs['plot_options']['trange'] = temp_tplot['dq'][i][4].tolist()
            pytplot.data_quants[data_name].attrs['plot_options']['create_time'] = temp_tplot['dq'][i][6]
        
            for option_name in temp_tplot['tv'][0][0].dtype.names:
                # the following should be set on the tplot variable, not for the entire session
                #if option_name == 'TRANGE':
                #    # x_range of [0, 0] causes tplot to create an empty figure
                #    if temp_tplot['tv'][0][0][option_name][0][0] != 0 or temp_tplot['tv'][0][0][option_name][0][1] != 0:
                #        tplot_options('x_range', temp_tplot['tv'][0][0][option_name][0])
                if option_name == 'WSIZE':
                    tplot_options('wsize', temp_tplot['tv'][0][0][option_name][0])
                if option_name == 'VAR_LABEL':
                    tplot_options('var_label', temp_tplot['tv'][0][0][option_name][0])
            if 'P' in temp_tplot['tv'][0][1].tolist():
                for option_name in temp_tplot['tv'][0][1]['P'][0].dtype.names:
                    if option_name == 'TITLE':
                        tplot_options('title', temp_tplot['tv'][0][1]['P'][0][option_name][0])

            # correct legend_names array
            plt_options = pytplot.data_quants[data_name].attrs['plot_options']
            yaxis_opts = plt_options.get('yaxis_opt')
            if yaxis_opts is not None:
                yaxis_opts = plt_options.get('yaxis_opt')
                if yaxis_opts.get('legend_names') is not None:
                    lnames = pytplot.data_quants[data_name].attrs['plot_options']['yaxis_opt']['legend_names'][0]
                    if isinstance(lnames, list) or isinstance(lnames, np.ndarray):
                        pytplot.data_quants[data_name].attrs['plot_options']['yaxis_opt']['legend_names'] = [lname.decode('utf-8') for lname in lnames]
                    else:
                        pytplot.data_quants[data_name].attrs['plot_options']['yaxis_opt']['legend_names'] = [lnames.decode('utf-8')]

                # decode any other string options
                for y_key in yaxis_opts.keys():
                    if isinstance(yaxis_opts[y_key], bytes):
                        yaxis_opts[y_key] = yaxis_opts[y_key].decode("utf-8")

        #temp_tplot['tv'][0][1] is all of the "settings" variables
            #temp_tplot['tv'][0][1]['D'][0] is "device" options
            #temp_tplot['tv'][0][1]['P'][0] is "plot" options
            #temp_tplot['tv'][0][1]['X'][0] is x axis options
            #temp_tplot['tv'][0][1]['Y'][0] is y axis options
        ####################################################################
    else:
        in_file = open(filename,"rb")
        temp = pickle.load(in_file)
        num_data_quants = temp[0]
        for i in range(0, num_data_quants):
            if isinstance(temp[i+1], dict):
                # NRV variable
                pytplot.data_quants[temp[i+1]['name']] = temp[i+1]
            else:
                pytplot.data_quants[temp[i+1].name] = temp[i+1]
        pytplot.tplot_opt_glob = temp[num_data_quants+1]
        in_file.close()
    
    return
