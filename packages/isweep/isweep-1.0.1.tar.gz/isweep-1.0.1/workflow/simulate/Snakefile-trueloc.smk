# ibd analysis after simulating data
# you have to have first run snakemake -s Snakefile-simulate.smk

# setup macro folder
import os
macro=str(config['CHANGE']['FOLDERS']['MACRO'])
if not os.path.exists(macro):
	os.mkdir(macro)

# load in experiments, set up micro, simname folders
import pandas as pd
micro=str(config['CHANGE']["FOLDERS"]["MICRO"])
sims = pd.read_csv(micro, sep='\t', header=0)
J = sims.shape[0]
for j in range(J):
	row = sims.loc[j,]
	if not os.path.exists(macro+'/'+str(row.MICROEXP)):
		os.mkdir(macro+'/'+str(row.MICROEXP))
	if not os.path.exists(macro+'/'+str(row.MICROEXP)+'/'+str(row.SIMNAME)):
		os.mkdir(macro+'/'+str(row.MICROEXP)+'/'+str(row.SIMNAME))
sims['FOLDER'] = [macro + '/' + sims.loc[j].MICROEXP + '/' + str(sims.loc[j].SIMNAME) for j in range(J)]
sims = sims.set_index("SIMNAME", drop=False)

# include: 'rules/scan.smk'
# include: 'rules/first.smk'
# include: 'rules/second.smk'
# include: 'rules/third.smk'

rule all:
    input:
        [f"{sim.FOLDER}/results.trueloc.cM1.0.tsv".replace(" ","") for sim in sims.itertuples()],
        [f"{sim.FOLDER}/results.trueloc.cM2.0.tsv".replace(" ","") for sim in sims.itertuples()],
        [f"{sim.FOLDER}/results.trueloc.cM3.0.tsv".replace(" ","") for sim in sims.itertuples()],

rule about_ibd:
    input:
        ibd='{macro}/{micro}/{seed}/chr.cM{thr}.ibd.gz',
    output:
        ibd='{macro}/{micro}/{seed}/chr.cM{thr}.about.ibd.gz',
    params:
        soft=str(config['CHANGE']['FOLDERS']['SOFTWARE']),
        prog=str(config['CHANGE']['PROGRAMS']['FILTER']),
        thecenter=str(3999999),
    resources:
        mem_gb='{config[CHANGE][CLUSTER][LARGEMEM]}'
    shell:
        """
        zcat {input.ibd} | \
            java -Xmx{config[CHANGE][CLUSTER][LARGEMEM]}g -jar {params.soft}/{params.prog} \
            "I" 6 0.00 {params.thecenter} | \
            java -Xmx{config[CHANGE][CLUSTER][LARGEMEM]}g -jar {params.soft}/{params.prog} \
            "I" 7 {params.thecenter} 10000000000 | \
            gzip > {output.ibd}
        """

rule about_est:
    input:
        long='{macro}/{micro}/{seed}/chr.cM{thr}.about.ibd.gz',
        freq='{macro}/{micro}/{seed}/slimulation.freq',
    output:
        fileout='{macro}/{micro}/{seed}/results.trueloc.cM{thr}.tsv',
    params:
        scripts=str(config['CHANGE']['FOLDERS']['TERMINALSCRIPTS']),
        nboot=str(config['FIXED']['ISWEEP']['NBOOT']),
        # mlecutoff=str(config['FIXED']['ISWEEP']['MLECUTOFF']),
        n=str(config['CHANGE']['SIMULATE']['SAMPSIZE']),
        ploidy=str(config['FIXED']['SIMULATE']['PLOIDY']),
        effdemo=str(config['CHANGE']['SIMULATE']['iNe']),
    shell:
        """
        ibdest=$(zcat {input.long} | wc -l)
        freqest=$(tail -n 1 {input.freq} | cut -f 1)
        python {params.scripts}/estimate.py \
            {output.fileout} \
            ${{ibdest}} \
            ${{freqest}} \
            {params.nboot} \
            {wildcards.thr} \
            {params.n} \
            {params.effdemo} \
            {params.ploidy}
        """
