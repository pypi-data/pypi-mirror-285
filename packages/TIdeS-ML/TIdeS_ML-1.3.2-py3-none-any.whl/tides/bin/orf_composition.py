#!/usr/bin/env python3

"""
Provides a quick summary of the basic composition of a given FASTA file of
nucleotide sequences.

Returns a table of GC1, GC2, GC3, GC12, and GC3 at four-fold degenerate sites.
"""

import sys
from pathlib import Path

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def eval_gcode(gencode: str) -> list:
    supp_codes = {
        '1':['TGA','TAG','TAA'], '4':['TAG','TAA'], '6':['TGA'], '10':['TAG','TAA'], '12':['TGA','TAG','TAA'],
        '29':['TGA'], '30':['TGA']
    }
    if gencode in supp_codes:
        return supp_codes[gencode]
    else:
        print('Error: Unsupported Genetic Code Provided.')
        print('For stop-codon recognition, the only supported codes are:')
        print('--- 1, 12      [TGA, TAG, TAA]')
        print('--- 6, 29, 30  [TGA]')
        print('--- 4, 10      [TAG, TAA]')
        sys.exit()


def calc_gc_content(gc_val: str) -> str:
    try:
        val = f'{100*(gc_val.count("G") + gc_val.count("C"))/len(gc_val):.2f}'
    except:
        print(gc_val)
        sys.exit()
    return val


def calc_gc_stats(seq: str, stop_codons: list) -> list:
    gc_stats = {'GC1':[], 'GC2':[], 'GC3':[], 'GC12':[], 'GC3_DGN':[]}
    gc1 = ''
    gc2 = ''
    gc3 = ''
    gc12 = ''
    gc3_dgn = ''
    degenerate_codons = ['TC','CT','CC','CG','AC','GT','GC','GG']
    for n in range(0, len(seq), 3):
        if seq[n:n+3] not in stop_codons and len(seq[n:n+3]) == 3:
            gc_stats['GC1'] += seq[n]
            gc_stats['GC2'] += seq[n+1]
            gc_stats['GC3'] += seq[n+2]
            gc_stats['GC12'] += seq[n:n+2]
            if seq[n:n+2] in degenerate_codons:
                gc_stats['GC3_DGN'] += seq[n+2]
    for k, v in gc_stats.items():
        if not v:
            gc_stats[k] = 0
            print(k, ''.join(v))
            continue
        gc_stats[k] = calc_gc_content(''.join(v))
    gc_stats['Seq_Length'] = len(seq)
    return gc_stats


def parse_fasta_file(fasta_file: str, taxon_code: str, gencode: str) -> dict:
    seq_comp_dict = {}

    outdir = f'{taxon_code}_TIdeS/ORF_Composition/'

    Path(outdir).mkdir(exist_ok = True, parents = True)

    out_tsv = f'{outdir}/{fasta_file.rpartition("/")[-1].rpartition(".fa")[0]}.CompSummary.tsv'

    stop_codons = eval_gcode(gencode)

    for i in open(fasta_file).read().split('>')[1:]:
        seq_id = i.partition('\n')[0]
        seq = i.partition('\n')[2].replace('\n','').upper()
        seq_comp_dict[seq_id] = calc_gc_stats(seq, stop_codons)

    df = pd.DataFrame.from_dict(seq_comp_dict, orient = 'index')
    df.index.name = 'ORF'
    df.to_csv(out_tsv, sep = '\t')
    return out_tsv, outdir


def make_plots(fasta_file, taxon_code, gencode) -> None:
    comp_tsv, outdir = parse_fasta_file(fasta_file, taxon_code, gencode)

    df = pd.read_table(comp_tsv)

    out_png = f'{outdir}{fasta_file.rpartition("/")[-1].rpartition(".fa")[0]}.ORF_Comp.png'
    out_png2 = f'{outdir}{fasta_file.rpartition("/")[-1].rpartition(".fa")[0]}.ORF_Comp.GC3_dgn.png'

    if 'Group' in df.columns:
        ax = sns.jointplot(data = df, x = 'GC3', y = 'GC12', kind = 'kde', hue = 'Group')

    else:
        ax = sns.jointplot(data = df, x = 'GC3', y = 'GC12', kind = 'kde')

    ax.ax_marg_x.set_xlim(0, 105)
    ax.ax_marg_y.set_ylim(0, 105)
    plt.xlabel('GC3 (%GC at codon 3rd positions)')
    plt.ylabel('GC12 (%GC at codon 1/2nd positions)')
    plt.tight_layout()
    ax.savefig(out_png)
    plt.clf()
