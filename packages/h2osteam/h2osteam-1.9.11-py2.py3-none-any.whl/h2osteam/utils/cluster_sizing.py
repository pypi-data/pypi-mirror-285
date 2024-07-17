# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import math
import ntpath
import warnings


def get_filename_from_path(path):
    return ntpath.basename(path)


# Validates dataset params
def validate_dataset_params(dataset_size_gb, dataset_dimension):
    if dataset_size_gb is not None and dataset_dimension is not None:
        raise Exception("use either dataset_size_gb when using uncompressed data source or dataset_dimension when using"
                        " compressed data source, but not both")

    if dataset_size_gb is not None:
        if dataset_size_gb < 1:
            raise Exception("dataset_size_gb must be a positive number")

    if dataset_dimension is not None:
        if type(dataset_dimension) is not tuple:
            raise Exception("dataset_dimension must be of type tuple with two numerical values (n_rows, n_cols)")

        if len(dataset_dimension) != 2:
            raise Exception("dataset_dimension tuple must have exactly two values (n_rows, n_cols)")

        if dataset_dimension[0] < 1:
            raise Exception("dataset_dimension first value in tuple (n_rows) must be a positive number")

        if dataset_dimension[1] < 1:
            raise Exception("dataset_dimension second value in tuple (n_cols) must be a positive number")


# Resolves profile params, parameter name for nodes and memory per node attributes
def get_profile_specific_params(profile):
    # Resolve profile type
    profile_type = profile["profile_type"]
    profile_params = profile[profile_type]

    # Resolve correct param names
    if profile_type == "h2o":
        return profile_params, "h2o_nodes", "h2o_memory"
    if profile_type == "h2o_kubernetes":
        return profile_params, "node_count", "memory_gb"

    # Default for SW (both internal and external)
    return profile_params, "num_executors", "executor_memory"


# Sets cluster params that can be scaled based on dataset parameters
def set_scalable_cluster_params(profile, rec_cluster_memory, nodes, node_memory_gb, extra_memory_percent):
    # Get scaled values from dataset parameters
    nodes_scaled, node_memory_gb_scaled, extra_memory_percent_scaled = get_scaled_cluster_params(profile,
                                                                                                 rec_cluster_memory)

    # Resolve profile types and param names
    profile_params, nodes_param, memory_param = get_profile_specific_params(profile)

    # Issue warnings if user-provided params override recommended values
    rec_total_memory = rec_cluster_memory["total_memory_gb"]
    rec_extra_mem_percent = rec_cluster_memory["extra_mem_percent"]

    if nodes is not None and rec_total_memory != 0:
        warnings.warn(
            "User-specified node count of %s overrides recommended value calculated from dataset parameters" % nodes_param)

    if node_memory_gb is not None and rec_total_memory != 0:
        warnings.warn(
            "User-specified memory of %s overrides recommended value calculated from dataset parameters" % memory_param)

    if extra_memory_percent is not None and rec_extra_mem_percent != 0:
        warnings.warn("User-specified value of extra_memory_percent overrides recommended value for XGBoost")

    # Use user-specified values if provided, scaled values if computed, profile initial as default
    if nodes is None:
        nodes = profile_params[nodes_param]['initial'] if nodes_scaled is None else nodes_scaled
    if node_memory_gb is None:
        node_memory_gb = profile_params[memory_param][
            'initial'] if node_memory_gb_scaled is None else node_memory_gb_scaled
    if extra_memory_percent is None:
        extra_memory_percent = profile_params['h2o_extramempercent'][
            'initial'] if extra_memory_percent_scaled is None else extra_memory_percent_scaled

    return nodes, node_memory_gb, extra_memory_percent


# Scales cluster params based on recommended memory, set params as profile default if dataset params not provided
def get_scaled_cluster_params(profile, rec_cluster_memory):
    # Preset values to None
    nodes, node_memory_gb, extra_memory_percent = None, None, None

    profile_params, nodes_param, memory_param = get_profile_specific_params(profile)

    rec_total_memory = rec_cluster_memory["total_memory_gb"]
    rec_extra_mem_percent = rec_cluster_memory["extra_mem_percent"]

    # Set nodes and node_memory_gb
    if rec_total_memory != 0:
        required_nodes = rec_total_memory / profile_params[memory_param]['max']

        if required_nodes <= profile_params[nodes_param]['min']:
            nodes = profile_params[nodes_param]['min']
            if rec_total_memory <= profile_params[memory_param]['min']:
                node_memory_gb = profile_params[memory_param]['min']
            else:
                node_memory_gb = rec_total_memory
        elif required_nodes <= profile_params[nodes_param]['max']:
            nodes = math.ceil(required_nodes)
            node_memory_gb = profile_params[memory_param]['max']
        else:
            nodes = profile_params[nodes_param]['max']
            node_memory_gb = profile_params[memory_param]['max']

    # Set extra_memory_percent
    if rec_extra_mem_percent != 0:

        extra_memory_percent = rec_extra_mem_percent

        if profile_params['h2o_extramempercent']['max'] <= rec_extra_mem_percent:
            extra_memory_percent = profile_params['h2o_extramempercent']['max']
        if profile_params['h2o_extramempercent']['min'] >= rec_extra_mem_percent:
            extra_memory_percent = profile_params['h2o_extramempercent']['min']

    return nodes, node_memory_gb, extra_memory_percent
