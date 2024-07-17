import collections
import os
from abc import ABC
from pathlib import Path
import re
from typing import Union

import numpy as np
import pandas as pd
import xarray as xr
from hydrodataset import HydroDataset
from hydroutils import hydro_file, hydro_time
from tqdm import tqdm

import hydrodatasource.configs.config as conf
from hydrodatasource.configs.config import SETTING
from hydrodatasource.reader import access_fs
from hydrodatasource.reader.reader import DataHandler

CACHE_DIR = hydro_file.get_cache_dir()


class HydroData(ABC):
    """An interface for reading multi-modal data sources.

    Parameters
    ----------
    ABC : _type_
        _description_
    """

    def __init__(self, data_path):
        self.data_source_dir = data_path

    def get_name(self):
        raise NotImplementedError

    def set_data_source_describe(self):
        raise NotImplementedError

    def read_data(self):
        raise NotImplementedError


class SelfMadeHydroDataset(HydroData):
    """A class for reading hydrodataset, but not really ready-datasets,
    just some data directorys organized like a HydroDataset.

    NOTE:
    We compile forcing data and attr data into a directory,
    organized like a ready dataset -- like Caravan.
    Only two directories are needed: attributes and timeseries
    """

    def __init__(self, data_path, download=False):
        """Initialize a self-made CAMELS dataset.

        Parameters
        ----------
        data_path : _type_
            _description_
        download : bool, optional
            _description_, by default False
        """
        super().__init__(data_path)
        self.data_source_description = self.set_data_source_describe()
        if download:
            self.download_data_source()
        self.camels_sites = self.read_site_info()

    @property
    def streamflow_unit(self):
        return "m^3/s"

    def get_name(self):
        return "SelfMadeHydroDataset"

    def set_data_source_describe(self):
        data_root_dir = self.data_source_dir
        ts_dir = os.path.join(data_root_dir, "timeseries")
        attr_dir = os.path.join(data_root_dir, "attributes")
        attr_file = os.path.join(attr_dir, "attributes.csv")
        units_file = os.path.join(data_root_dir, "units_info.json")
        return collections.OrderedDict(
            DATA_DIR=data_root_dir,
            TS_DIR=ts_dir,
            ATTR_DIR=attr_dir,
            ATTR_FILE=attr_file,
            UNITS_FILE=units_file,
        )

    def download_data_source(self):
        print(
            "Please download it manually and put all files of a CAMELS dataset in the CAMELS_DIR directory."
        )
        print("We unzip all files now.")

    def read_site_info(self):
        camels_file = self.data_source_description["ATTR_FILE"]
        attrs = pd.read_csv(camels_file, dtype={"basin_id": str})
        return attrs[["basin_id", "area"]]

    def read_object_ids(self, object_params=None) -> np.array:
        return self.camels_sites["basin_id"].values

    def read_timeseries(
        self, object_ids=None, t_range_list: list = None, relevant_cols=None, **kwargs
    ) -> Union[np.array, list]:
        """3d data (site_num * time_length * var_num), time-series data"""
        region = kwargs.get("region", None)
        t_range_list = pd.date_range(
            start=t_range_list[0], end=t_range_list[-1], freq=kwargs.get("freq", "D")
        )
        nt = t_range_list.shape[0]
        x = np.full([len(object_ids), nt, len(relevant_cols)], np.nan)
        for k in tqdm(
            range(len(object_ids)), desc="Read timeseries data of SelfMadeHydroDataset"
        ):
            prefix_ = "" if region is None else region + "_"
            ts_file = os.path.join(
                self.data_source_description["TS_DIR"],
                prefix_ + object_ids[k] + ".csv",
            )
            ts_data = pd.read_csv(ts_file)
            date = pd.to_datetime(ts_data["time"]).values
            [c, ind1, ind2] = np.intersect1d(date, t_range_list, return_indices=True)
            for j in range(len(relevant_cols)):
                if (
                    "precipitation" in relevant_cols[j]
                    or "evaporation" in relevant_cols[j]
                ):
                    prcp = ts_data[relevant_cols[j]].values
                    # there are a few negative values for prcp, set them 0
                    prcp[prcp < 0] = 0.0
                    x[k, ind2, j] = prcp[ind1]
                else:
                    x[k, ind2, j] = ts_data[relevant_cols[j]].values[ind1]
        return x

    def read_attributes(
        self, object_ids=None, constant_cols=None, **kwargs
    ) -> np.array:
        """2d data (site_num * var_num), non-time-series data"""
        attr_file = self.data_source_description["ATTR_FILE"]
        attrs = pd.read_csv(attr_file, dtype={"basin_id": str})
        if object_ids is None:
            if constant_cols is None:
                return attrs
            object_ids = attrs["basin_id"].values
        if constant_cols is None:
            constant_cols = attrs.columns.values
        x = np.full([len(object_ids), len(constant_cols)], np.nan)
        for k in range(len(object_ids)):
            ind = attrs["basin_id"] == object_ids[k]
            for j in range(len(constant_cols)):
                x[k, j] = attrs[constant_cols[j]][ind].values
        return x

    def get_attributes_cols(self) -> np.array:
        """the constant cols in this data_source"""
        attr_file = self.data_source_description["ATTR_FILE"]
        attrs = pd.read_csv(attr_file, dtype={"basin_id": str})
        attr_units = attrs.columns.values
        return self._check_vars_in_unitsinfo(attr_units)

    def get_timeseries_cols(self) -> np.array:
        """the relevant cols in this data_source"""
        ts_dir = self.data_source_description["TS_DIR"]
        ts_file = os.path.join(ts_dir, os.listdir(ts_dir)[0])
        ts_tmp = pd.read_csv(ts_file, dtype={"basin_id": str})
        forcing_units = ts_tmp.columns.values[1:]
        return self._check_vars_in_unitsinfo(forcing_units)

    def _check_vars_in_unitsinfo(self, vars):
        """If a var is not recorded in a units_info file, we will not use it.

        Parameters
        ----------
        vars : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        units_info = hydro_file.unserialize_json(
            self.data_source_description["UNITS_FILE"]
        )
        vars_final = [var_ for var_ in vars if var_ in units_info]
        return np.array(vars_final)

    def cache_attributes_xrdataset(self, region=None):
        """Convert all the attributes to a single dataset

        Returns
        -------
        None
        """
        # NOTICE: although it seems that we don't use pint_xarray, we have to import this package
        import pint_xarray  # noqa: F401

        df_attr = self.read_attributes()
        df_attr.set_index("basin_id", inplace=True)
        # Mapping provided units to the variables in the datasets
        units_dict = hydro_file.unserialize_json(
            self.data_source_description["UNITS_FILE"]
        )

        # Convert string columns to categorical variables and record categorical mappings
        categorical_mappings = {}
        for column in df_attr.columns:
            if df_attr[column].dtype == "object":
                df_attr[column] = df_attr[column].astype("category")
                categorical_mappings[column] = dict(
                    enumerate(df_attr[column].cat.categories)
                )
                df_attr[column] = df_attr[column].cat.codes

        ds = xr.Dataset()
        for column in df_attr.columns:
            attrs = {"units": units_dict.get(column, "unknown")}
            if column in categorical_mappings:
                attrs["category_mapping"] = categorical_mappings[column]

            data_array = xr.DataArray(
                data=df_attr[column].values,
                dims=["basin"],
                # we have set gage_id as index so that it won't be saved as numeric values
                coords={"basin": df_attr.index.values.astype(str)},
                attrs=attrs,
            )
            ds[column] = data_array

        # Convert categorical mappings to strings
        for column in ds.data_vars:
            if "category_mapping" in ds[column].attrs:
                # Convert the dictionary to a string
                mapping_str = str(ds[column].attrs["category_mapping"])
                ds[column].attrs["category_mapping"] = mapping_str
        prefix_ = "" if region is None else region + "_"
        ds.to_netcdf(os.path.join(CACHE_DIR, f"{prefix_}attributes.nc"))

    def cache_timeseries_xrdataset(
        self, region=None, t_range=None, freq="D", batchsize=100
    ):
        """Save all timeseries data in a netcdf file

        Parameters
        ----------
        region : _type_, optional
            A prefix used in cache file, by default None
        t_range : _type_, optional
            _description_, by default None
        freq : str, optional
            _description_, by default "D"
        batchsize : int, optional
            _description_, by default 100

        Yields
        ------
        _type_
            _description_
        """
        if t_range is None:
            t_range = ["1980-01-01", "2023-12-31"]
        variables = self.get_timeseries_cols()
        basins = self.camels_sites["basin_id"].values
        times = (
            pd.date_range(start=t_range[0], end=t_range[-1], freq=freq)
            .strftime("%Y-%m-%d")
            .tolist()
        )

        units_info = hydro_file.unserialize_json(
            self.data_source_description["UNITS_FILE"]
        )

        # Define the generator function for batching
        def data_generator(basins, batch_size):
            for i in range(0, len(basins), batch_size):
                yield basins[i : i + batch_size]

        for basin_batch in data_generator(basins, batchsize):
            data = self.read_timeseries(
                object_ids=basin_batch,
                t_range_list=t_range,
                relevant_cols=variables,
                freq=freq,
            )

            dataset = xr.Dataset(
                data_vars={
                    **{
                        variables[i]: (
                            ["basin", "time"],
                            data[:, :, i],
                            {"units": units_info[variables[i]]},
                        )
                        for i in range(len(variables))
                    }
                },
                coords={
                    "basin": basin_batch,
                    "time": pd.to_datetime(times),
                },
            )

            # Save the dataset to a NetCDF file for the current batch
            prefix_ = "" if region is None else region + "_"
            batch_file_path = os.path.join(
                CACHE_DIR,
                f"{prefix_}timeseries_batch_{basin_batch[0]}_{basin_batch[-1]}.nc",
            )
            dataset.to_netcdf(batch_file_path)

            # Release memory by deleting the dataset
            del dataset
            del data

    def cache_xrdataset(self, region=None, t_range=None, freq="D"):
        """Save all data in a netcdf file in the cache directory"""
        self.cache_attributes_xrdataset(region=region)
        self.cache_timeseries_xrdataset(region=region, t_range=t_range, freq=freq)

    def read_ts_xrdataset(
        self,
        gage_id_lst: list = None,
        t_range: list = None,
        var_lst: list = None,
        **kwargs,
    ):
        """
        Read time-series xarray dataset from multiple NetCDF files.

        Parameters:
        ----------
        gage_id_lst: list - List of gage IDs to select.
        t_range: list - List of two elements [start_time, end_time] to select time range.
        var_lst: list - List of variables to select.
        **kwargs: Additional arguments.

        Returns:
        ----------
        xarray.Dataset - Merged dataset containing the selected gage IDs, time range, and variables.
        """
        region = kwargs.get("region", None)
        if var_lst is None:
            return None

        # Collect all batch files in the cache directory
        prefix_ = "" if region is None else region + "_"
        batch_files = [
            os.path.join(CACHE_DIR, f)
            for f in os.listdir(CACHE_DIR)
            if re.match(
                rf"^{prefix_}timeseries_batch_[A-Za-z0-9_]+_[A-Za-z0-9_]+\.nc$", f
            )
        ]

        if not batch_files:
            # Cache the data if no batch files are found
            self.cache_timeseries_xrdataset(region=region, **kwargs)
            batch_files = [
                os.path.join(CACHE_DIR, f)
                for f in os.listdir(CACHE_DIR)
                if re.match(
                    rf"^{region}_timeseries_batch_[A-Za-z0-9]+_[A-Za-z0-9]+\.nc$", f
                )
            ]

        selected_datasets = []

        for batch_file in batch_files:
            ds = xr.open_dataset(batch_file)
            all_vars = ds.data_vars
            if any(var not in ds.variables for var in var_lst):
                raise ValueError(f"var_lst must all be in {all_vars}")
            if valid_gage_ids := [
                gid for gid in gage_id_lst if gid in ds["basin"].values
            ]:
                ds_selected = ds[var_lst].sel(
                    basin=valid_gage_ids, time=slice(t_range[0], t_range[1])
                )
                selected_datasets.append(ds_selected)

            ds.close()  # Close the dataset to free memory
        return (
            xr.concat(selected_datasets, dim="basin")
            if selected_datasets
            else xr.Dataset()
        )

    def read_attr_xrdataset(self, gage_id_lst=None, var_lst=None, **kwargs):
        region = kwargs.get("region", None)
        prefix_ = "" if region is None else region + "_"
        if var_lst is None or len(var_lst) == 0:
            return None
        try:
            attr = xr.open_dataset(os.path.join(CACHE_DIR, f"{prefix_}attributes.nc"))
        except FileNotFoundError:
            self.cache_xrdataset()
            attr = xr.open_dataset(os.path.join(CACHE_DIR, f"{prefix_}attributes.nc"))
        return attr[var_lst].sel(basin=gage_id_lst)

    def read_area(self, gage_id_lst=None):
        """read area of each basin/unit"""
        return self.read_attr_xrdataset(gage_id_lst, ["area"])

    def read_mean_prcp(self, gage_id_lst=None):
        """read mean precipitation of each basin/unit"""
        return self.read_attr_xrdataset(gage_id_lst, ["pre_mm_syr"])


class HydroBasins(HydroData):
    def __init__(self, data_path):
        super().__init__(data_path)

    def get_name(self):
        return " HydroBasins"

    def set_data_source_describe(self):
        self.data_source = "MINIO"
        self.data_source_bucket = "basins-origin"

    def read_BA_xrdataset(self, gage_id_lst: list, var_lst: list, path):
        attr = access_fs.spec_path(path, head="minio")
        if "all" in var_lst:
            return attr.sel(basin=gage_id_lst)
        return attr[var_lst].sel(basin=gage_id_lst)

    def read_MP(self, gage_id_lst, path):
        mean_prep = access_fs.spec_path(path, head="minio")
        return mean_prep["pet_mm_syr"].sel(basin=gage_id_lst)

    def merge_nc_minio_datasets(self, folder_path, basin, var_lst, gap="3h"):
        datasets = []
        basins = []

        file_lst = self.read_file_lst(folder_path)

        for file_path in file_lst:
            basin_id = file_path.split("_")[-1].split(".")[0]
            if basin_id in basin:
                basins.append(basin_id)
                if "ftproot" in file_path:
                    ds = access_fs.spec_path(file_path)
                else:
                    ds = access_fs.spec_path(file_path, head="minio")
                if gap != "1h":
                    ds = self.aggregate_dataset(ds, gap, basin_id)
                    # ds = self.aggeragate_dataset(ds, gap)
                # ds = ds.assign_coords({"basin": basin_id})
                # ds = ds.expand_dims("basin")
                datasets.append(ds[var_lst])

        return xr.concat(datasets, dim="basin")

    # def aggeragate_dataset(self, ds: xr.Dataset, gap):
    #     df_res = ds.to_dataframe()
    #     if "total_evaporation_hourly" in df_res.columns:
    #         df_res["total_evaporation_hourly"] = (
    #             df_res["total_evaporation_hourly"].resample(gap, origin="start").sum()
    #         )
    #         df_res["total_evaporation_hourly"] *= -1000
    #         df_res["total_precipitation_hourly"] = (
    #             df_res["total_precipitation_hourly"].resample(gap, origin="start").sum()
    #         )
    #         df_res["total_precipitation_hourly"] *= 1000
    #     elif "gpm_tp" in df_res.columns:
    #         df_res["gpm_tp"] = df_res["gpm_tp"].resample(gap, origin="start").sum()
    #     df_res["streamflow"] = df_res["streamflow"].resample(gap, origin="start").sum()
    #     df_res = df_res.resample(gap).mean()
    #     return xr.Dataset.from_dataframe(df_res)

    def aggregate_dataset(self, ds: xr.Dataset, gap, basin_id):
        if gap == "3h":
            gap = 3
            start_times = [2, 5, 8, 11, 14, 17, 20, 23]
            end_times = [1, 4, 7, 10, 13, 16, 19, 22]
            time_index = ds.indexes["time"]

            # 修剪开始时间
            while time_index[0].hour not in start_times:
                ds = ds.isel(time=slice(1, None))
                time_index = ds.indexes["time"]

            # 修剪结束时间
            while time_index[-1].hour not in end_times:
                ds = ds.isel(time=slice(None, -1))
                time_index = ds.indexes["time"]

        df_res = ds.to_dataframe().reset_index()
        df_res.set_index("time", inplace=True)

        numeric_cols = df_res.select_dtypes(include=[np.number]).columns
        aggregated_data = {}
        sm_surface_data = []
        sm_rootzone_data = []

        for col in numeric_cols:
            if col in ["sm_surface", "sm_rootzone"]:
                continue

            data = df_res[col].values
            aggregated_values = []
            for start in range(0, len(data), gap):
                chunk = data[start : start + gap]
                if np.isnan(chunk).any():
                    aggregated_values.append(np.nan)
                else:
                    aggregated_values.append(np.sum(chunk))

            aggregated_times = df_res.index[gap - 1 :: gap][: len(aggregated_values)]
            aggregated_data[col] = xr.DataArray(
                np.array(aggregated_values).reshape(-1, 1),
                dims=["time", "basin"],
                coords={"time": aggregated_times, "basin": [basin_id]},
            )

        # 处理 sm_surface 和 sm_rootzone 变量
        if "sm_surface" in df_res.columns:
            sm_surface_data = df_res["sm_surface"].iloc[gap - 1 :: gap].values
            aggregated_data["sm_surface"] = xr.DataArray(
                sm_surface_data.reshape(-1, 1),
                dims=["time", "basin"],
                coords={"time": aggregated_times, "basin": [basin_id]},
            )

        if "sm_rootzone" in df_res.columns:
            sm_rootzone_data = df_res["sm_rootzone"].iloc[gap - 1 :: gap].values
            aggregated_data["sm_rootzone"] = xr.DataArray(
                sm_rootzone_data.reshape(-1, 1),
                dims=["time", "basin"],
                coords={"time": aggregated_times, "basin": [basin_id]},
            )

        if "total_evaporation_hourly" in df_res.columns:
            aggregated_data["total_precipitation_hourly"] *= 1000
            aggregated_data["total_evaporation_hourly"] *= -1000

        result_ds = xr.Dataset(
            aggregated_data,
            coords={"time": aggregated_times, "basin": [basin_id]},
        )

        result_ds = result_ds.transpose("basin", "time")

        return result_ds

    def read_grid_data(self, file_lst, basin):
        def get_basin_id(file_path):
            return file_path.split("_")[-1].split(".")[0]

        matched_path = next(
            (path for path in file_lst if get_basin_id(path) in basin), None
        )

        if matched_path:
            grid_data = access_fs.spec_path(matched_path, head="minio")
            return grid_data

        return None

    def read_file_lst(self, folder_path):
        if "ftproot" in folder_path:
            return glob.glob(folder_path + "/*")[1:]
        url_path = "s3://" + folder_path
        return conf.FS.glob(url_path + "/**")[1:]
