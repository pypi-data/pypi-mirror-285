# Supported tools
SAMTOOLS_STATS = "samtools_stats"
BAMSTATS = "bamstats"
RNASEQC = "rnaseqc"
PICARD_COLLECT_ALIGNMENT_SUMMARY_METRICS = "picard_CollectAlignmentSummaryMetrics"
PICARD_COLLECT_INSERT_SIZE_METRICS = "picard_CollectInsertSizeMetrics"
PICARD_COLLECT_WGS_METRICS = "picard_CollectWgsMetrics"
FASTQC = "fastqc"
NANOPLOT = "nanoplot"
VERIFYBAMID = "verifybamid2"

import sys
from src.metrics_to_extract import metrics
from src.metrics_to_calculate import (
    samtools_stats_calculated_metrics,
    bamstats_calculated_metrics,
)
from src.utils import add_calculated_metrics, safe_cast
from src.QMGeneric import QMValue
from typing import List
import json


class Parser:

    def __init__(self, tool: str, metrics_file: str):

        self.tool = tool
        self.path = metrics_file

    def parse(self):

        if self.tool == SAMTOOLS_STATS:
            return self.parse_samtools_stats()
        elif self.tool == PICARD_COLLECT_ALIGNMENT_SUMMARY_METRICS:
            return self.parse_picard_CollectAlignmentSummaryMetrics()
        elif self.tool == PICARD_COLLECT_INSERT_SIZE_METRICS:
            return self.parse_picard_CollectInsertSizeMetrics()
        elif self.tool == PICARD_COLLECT_WGS_METRICS:
            return self.parse_picard_CollectWgsMetrics()
        elif self.tool == RNASEQC:
            return self.parse_rnaseqc()
        elif self.tool == BAMSTATS:
            return self.parse_bamstats()
        elif self.tool == FASTQC:
            return self.parse_fastqc()
        elif self.tool == NANOPLOT:
            return self.parse_nanoplot()
        elif self.tool == VERIFYBAMID:
            return self.parse_verifybamid()
        else:
            sys.exit(f"{self.tool} is not supported. Please add a parser to Parser.py")

    def parse_samtools_stats(self) -> List[QMValue]:
        qm_values = []
        # Parse file and save values
        with open(self.path) as fi:
            for line in fi:
                if line.startswith("SN"):
                    line = line.rstrip().split("\t")
                    field, value = line[1].replace(":", ""), line[2]
                    if field in metrics[SAMTOOLS_STATS]:
                        m = metrics[SAMTOOLS_STATS][field]
                        value_cast = safe_cast(value, m["type"])
                        if value_cast == None:
                            continue
                        qmv = QMValue(m, value_cast)
                        qm_values.append(qmv)
        add_calculated_metrics(qm_values, samtools_stats_calculated_metrics)
        return qm_values

    def parse_bamstats(self) -> List[QMValue]:
        qm_values = []
        # Parse file and save values
        fi = open(self.path)
        bamstats_res = json.load(fi)
        for key in bamstats_res.keys():
            if key in metrics[BAMSTATS]:
                m = metrics[BAMSTATS][key]
                value = bamstats_res[key]
                value_cast = safe_cast(value, m["type"])
                if value_cast == None:
                    continue
                qmv = QMValue(m, value_cast)
                qm_values.append(qmv)
        fi.close()
        add_calculated_metrics(qm_values, bamstats_calculated_metrics)
        return qm_values

    def parse_fastqc(self) -> List[QMValue]:
        qm_values = []
        # Parse file and save values
        with open(self.path) as fi:
            for line in fi:
                value, field, _ = line.rstrip().split("\t")
                if field in metrics[FASTQC]:
                    m = metrics[FASTQC][field]
                    value_cast = safe_cast(value, m["type"])
                    qmv = QMValue(m, value_cast)
                    qm_values.append(qmv)
        return qm_values

    def parse_rnaseqc(self) -> List[QMValue]:
        qm_values = []
        with open(self.path) as f:
            rnaseqc_results = json.load(f)
            for field in rnaseqc_results.keys():
                value = rnaseqc_results[field]
                if field in metrics[RNASEQC]:
                    m = metrics[RNASEQC][field]
                    value_cast = safe_cast(value, m["type"])
                    qmv = QMValue(m, value_cast)
                    qm_values.append(qmv)
        return qm_values
    
    def parse_verifybamid(self) -> List[QMValue]:
        qm_values = []
        with open(self.path) as fi:
            for line in fi:
                field, value = line.rstrip().split(":", maxsplit=1)
                if field in metrics[VERIFYBAMID]:
                    m = metrics[VERIFYBAMID][field]
                    value_cast = safe_cast(value, m["type"])
                    qmv = QMValue(m, value_cast)
                    qm_values.append(qmv)
        return qm_values

    def parse_nanoplot(self) -> List[QMValue]:
        qm_values = []
        # Parse file and save values
        with open(self.path) as fi:
            for line in fi:
                columns = line.rstrip().split(":")
                if len(columns) != 2:
                    continue
                field = columns[0]
                value = columns[1]

                if field in metrics[NANOPLOT]:
                    m = metrics[NANOPLOT][field]
                    if field.startswith(">Q"):
                        value_extracted = value.split("(")[1]
                        value_extracted = value_extracted.split(")")[0]
                        value_extracted = value_extracted.replace("%", "")
                        value_cast = safe_cast(value_extracted, m["type"])
                    else:
                        # Can't convert '2.0' directly to int
                        value_stripped = float(value.strip().replace(",", ""))
                        value_cast = safe_cast(value_stripped, m["type"])
                    qmv = QMValue(m, value_cast)
                    qm_values.append(qmv)
        return qm_values

    def parse_picard_CollectAlignmentSummaryMetrics(self) -> List[QMValue]:
        qm_values = []
        header, pair, unpair = [], [], []
        with open(self.path) as fi:
            for line in fi:
                if line.startswith("CATEGORY"):
                    header = line.rstrip().split("\t")
                elif line.startswith("PAIR"):
                    pair = line.rstrip().split("\t")
                elif line.startswith("UNPAIRED"):
                    unpair = line.rstrip().split("\t")

        # Check for both PAIR and UNPAIRED -> ERROR
        if pair and unpair:
            sys.exit(f"Paired-end BAM file contains unpaired reads")
        elif unpair:
            pair = unpair

        for i, field in enumerate(header):
            if field in metrics[PICARD_COLLECT_ALIGNMENT_SUMMARY_METRICS]:
                m = metrics[PICARD_COLLECT_ALIGNMENT_SUMMARY_METRICS][field]
                value_cast = safe_cast(pair[i], m["type"])
                if value_cast == None:
                    continue
                qmv = QMValue(m, value_cast)
                qm_values.append(qmv)
        return qm_values

    def parse_picard_CollectInsertSizeMetrics(self) -> List[QMValue]:
        qm_values = []
        header, pairs, is_block = [], [], False
        with open(self.path) as fi:
            for line in fi:
                line = line.rstrip()
                if line:
                    if line.startswith("## HISTOGRAM"):
                        break
                    elif line.startswith("MEDIAN_INSERT_SIZE"):
                        is_block = True
                        header = line.split("\t")
                    elif is_block:
                        line = line.split("\t")
                        pairs.append(line)

        for pair in pairs:
            orientation = pair[8]
            for i, field in enumerate(header):
                if field in metrics[PICARD_COLLECT_INSERT_SIZE_METRICS]:
                    m = metrics[PICARD_COLLECT_INSERT_SIZE_METRICS][field]
                    value_cast = safe_cast(pair[i], m["type"])
                    if value_cast == None:
                        continue
                    qmv = QMValue(m, value_cast)
                    qm_values.append(qmv)
        return qm_values

    def parse_picard_CollectWgsMetrics(self) -> List[QMValue]:
        qm_values = []
        header, stats, is_block = [], [], False
        with open(self.path) as fi:
            for line in fi:
                line = line.rstrip()
                if line:
                    if line.startswith("## HISTOGRAM"):
                        break
                    elif line.startswith("GENOME_TERRITORY"):
                        is_block = True
                        header = line.split("\t")
                    elif is_block:
                        stats = line.split("\t")

        for i, field in enumerate(header):
            if field in metrics[PICARD_COLLECT_WGS_METRICS]:
                m = metrics[PICARD_COLLECT_WGS_METRICS][field]
                value_cast = safe_cast(stats[i], m["type"])
                if value_cast == None:
                    continue
                qmv = QMValue(m, value_cast)
                qm_values.append(qmv)
        return qm_values
