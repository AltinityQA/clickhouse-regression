#!/usr/bin/env python3
import os
import sys

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import Cluster
from helpers.argparser import argparser as base_argparser
from helpers.common import check_clickhouse_version
from clickhouse_keeper.requirements import *
from clickhouse_keeper.tests.steps import *
from clickhouse_keeper.tests.steps_ssl import *


def argparser(parser):
    """Custom argperser that add --ssl option."""
    base_argparser(parser)

    parser.add_argument(
        "--ssl",
        action="store_true",
        help="enable ssl connection for clickhouse keepers and clickhouse",
        default=False,
    )


xfails = {}


xflags = {}

ffails = {}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("clickhouse keeper")
@Requirements(RQ_SRS_024_ClickHouse_Keeper("1.0"))
@Specifications(SRS024_ClickHouse_Keeper)
def regression(
    self,
    local,
    clickhouse_binary_path,
    clickhouse_version,
    collect_service_logs,
    ssl=None,
    stress=None,
):
    """ClickHouse regression when using clickhouse-keeper."""
    nodes = {
        "zookeeper": ("zookeeper1", "zookeeper2", "zookeeper3", "zookeeper"),
        "bash_tools": ("bash_tools"),
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
            "clickhouse4",
            "clickhouse5",
            "clickhouse6",
            "clickhouse7",
            "clickhouse8",
            "clickhouse9",
            "clickhouse10",
            "clickhouse11",
            "clickhouse12",
            "clickhouse13",
        ),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    if ssl:
        self.context.tcp_port_secure = True
        self.context.secure = 1
        self.context.port = "9281"
        self.context.ssl = "true"
    else:
        self.context.tcp_port_secure = False
        self.context.secure = 0
        self.context.ssl = "false"
        self.context.port = "2181"

    from platform import processor as current_cpu

    folder_name = os.path.basename(current_dir())
    if current_cpu() == "aarch64":
        env = f"{folder_name}_env_arm64"
    else:
        env = f"{folder_name}_env"

    with Cluster(
        local,
        clickhouse_binary_path,
        collect_service_logs=collect_service_logs,
        nodes=nodes,
        docker_compose_project_dir=os.path.join(current_dir(), env),
    ) as cluster:
        self.context.cluster = cluster

        if check_clickhouse_version("<21.4")(self):
            skip(reason="only supported on ClickHouse version >= 21.4")

        if ssl:
            create_3_3_cluster_config_ssl()
            Feature(run=load("clickhouse_keeper.tests.sanity", "feature"))
            Feature(run=load("clickhouse_keeper.tests.cli", "feature"))
            Feature(run=load("clickhouse_keeper.tests.synchronization", "feature"))
            Feature(
                run=load(
                    "clickhouse_keeper.tests.non_distributed_ddl_queries", "feature"
                )
            )
            Feature(run=load("clickhouse_keeper.tests.keeper_cluster_tests", "feature"))
            Feature(
                run=load("clickhouse_keeper.tests.alter_column_distributed", "feature")
            )
            Feature(
                run=load(
                    "clickhouse_keeper.tests.alter_partition_distributed", "feature"
                )
            )
            Feature(run=load("clickhouse_keeper.tests.servers_start_up", "feature"))
        else:
            create_3_3_cluster_config()
            Feature(run=load("clickhouse_keeper.tests.sanity", "feature"))
            Feature(run=load("clickhouse_keeper.tests.migration", "feature"))
            Feature(run=load("clickhouse_keeper.tests.synchronization", "feature"))
            Feature(run=load("clickhouse_keeper.tests.cli", "feature"))
            Feature(run=load("clickhouse_keeper.tests.servers_start_up", "feature"))
            Feature(run=load("clickhouse_keeper.tests.cli_converter", "feature"))
            Feature(
                run=load(
                    "clickhouse_keeper.tests.non_distributed_ddl_queries", "feature"
                )
            )
            Feature(run=load("clickhouse_keeper.tests.keeper_cluster_tests", "feature"))
            Feature(
                run=load("clickhouse_keeper.tests.alter_column_distributed", "feature")
            )
            Feature(
                run=load(
                    "clickhouse_keeper.tests.alter_partition_distributed", "feature"
                )
            )
            Feature(
                run=load("clickhouse_keeper.tests.four_letter_word_commands", "feature")
            )
            Feature(
                run=load("clickhouse_keeper.tests.coordination_settings", "feature")
            )


if main():
    regression()
