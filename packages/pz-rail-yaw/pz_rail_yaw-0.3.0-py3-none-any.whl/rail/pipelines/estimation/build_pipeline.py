#!/usr/bin/env python3
#
# This script produces a pipeline file akin to the yet_another_wizz example
# notebook as well as the input test data required to run the pipeline.
#

# pylint: skip-file
import os
from shutil import rmtree

from yaw import UniformRandoms

from rail.core.stage import RailStage
import rail.stages

rail.stages.import_and_attach_all()
from rail.stages import *
from rail.yaw_rail.backports import FixedRailPipeline
from rail.yaw_rail.utils import get_dc2_test_data

try:  # TODO: remove when integrated in RAIL
    YawCacheCreate
except NameError:
    from rail.estimation.algos.cc_yaw import *


DATA = "data"
LOGS = "logs"
VERBOSE = "debug"  # verbosity level of built-in logger, disable with "error"

# configuration for the correlation measurements
corr_config = dict(
    rmin=100,
    rmax=1000,
    zmin=0.0,
    zmax=3.0,
    zbin_num=8,
    verbose=VERBOSE,
)


def create_datasets(root):
    test_data = get_dc2_test_data()
    redshifts = test_data["z"].to_numpy()
    n_data = len(test_data)

    data_name = "input_data.parquet"
    data_path = os.path.join(root, data_name)
    test_data.to_parquet(data_path)

    angular_rng = UniformRandoms(
        test_data["ra"].min(),
        test_data["ra"].max(),
        test_data["dec"].min(),
        test_data["dec"].max(),
        seed=12345,
    )
    test_rand = angular_rng.generate(n_data * 10, draw_from=dict(z=redshifts))

    rand_name = "input_rand.parquet"
    rand_path = os.path.join(root, rand_name)
    test_rand.to_parquet(rand_path)

    return (data_path, rand_path)


class YawPipeline(FixedRailPipeline):

    def __init__(self):
        FixedRailPipeline.__init__(self)

        DS = RailStage.data_store
        DS.__class__.allow_overwrite = True

        self.cache_ref = YawCacheCreate.build(
            aliases=create_yaw_cache_alias("ref"),
            path=os.path.join(DATA, "test_ref"),
            overwrite=True,
            ra_name="ra",
            dec_name="dec",
            redshift_name="z",
            n_patches=5,
            verbose=VERBOSE,
        )

        self.cache_unk = YawCacheCreate.build(
            connections=dict(
                patch_source=self.cache_ref.io.output,
            ),
            aliases=create_yaw_cache_alias("unk"),
            path=os.path.join(DATA, "test_unk"),
            overwrite=True,
            ra_name="ra",
            dec_name="dec",
            verbose=VERBOSE,
        )

        self.auto_corr = YawAutoCorrelate.build(
            connections=dict(
                sample=self.cache_ref.io.output,
            ),
            **corr_config,
        )

        self.cross_corr = YawCrossCorrelate.build(
            connections=dict(
                reference=self.cache_ref.io.output,
                unknown=self.cache_unk.io.output,
            ),
            **corr_config,
        )

        self.summarize = YawSummarize.build(
            connections=dict(
                cross_corr=self.cross_corr.io.output,
                auto_corr_ref=self.auto_corr.io.output,
            ),
            verbose=VERBOSE,
        )


if __name__ == "__main__":
    for folder in (DATA, LOGS):
        if os.path.exists(folder):
            rmtree(folder)
        os.mkdir(folder)
    data_path, rand_path = create_datasets(DATA)

    pipe = YawPipeline()
    pipe.initialize(
        overall_inputs=dict(
            data_ref=data_path,
            rand_ref=rand_path,
            data_unk=data_path,
            rand_unk="none",
            patch_source_ref="none",
            auto_corr_unk="none",
        ),
        run_config=dict(output_dir=DATA, log_dir=LOGS, resume=False),
        stages_config=None,
    )
    pipe.save("yaw_pipeline.yml", site_name="local")
