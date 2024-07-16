# comparing isweep in simulation study
# Seth D. Temple, sdtemple@uw.edu
# May 15, 2023 originally
# October 2, 2023 added selscan

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
sims['FILE'] = sims['FOLDER'] + '/second.ranks.tsv.gz' # after running isweep
sims['EXISTS'] = sims['FILE'].apply(os.path.isfile)
sims=sims[sims['EXISTS']]
sims = sims.set_index("SIMNAME", drop=False)

rule all:
	input:
        # isafe
		[f"{sim.FOLDER}/isafe.ranks.fair.tsv.gz" for sim in sims.itertuples()],
		[f"{sim.FOLDER}/isafe.rank.fair.true.txt" for sim in sims.itertuples()],

# get a subset of SNPs

rule subset:
    input:
        vcf='{macro}/{micro}/{seed}/large.chr1.vcf.gz',
        centerfile='{macro}/{micro}/{seed}/third.best.hap.txt',
    output:
        vcfout='{macro}/{micro}/{seed}/fair.v2.chr1.vcf.gz',
    params:
        pm=str(config['FIXED']['SIMULATE']['BUFFER']),
        # center=str(config['FIXED']['SIMULATE']['LOC']),
        folder='{macro}/{micro}/{seed}',
    shell:
        """
        gunzip -c {input.vcf} | bgzip > {params.folder}/chrsubtemp.vcf.bgz
        tabix -fp vcf {params.folder}/chrsubtemp.vcf.bgz
        center=$(cut -f 2 {input.centerfile} | head -n 1)
        left=$(python -c "out = ${{center}} - {params.pm} ; print(out)")
        right=$(python -c "out = ${{center}} + {params.pm} ; print(out)")
        bcftools view {params.folder}/chrsubtemp.vcf.bgz \
            -r 1:${{left}}-${{right}} \
            -Oz -o {output.vcfout}
        rm {params.folder}/chrsubtemp.vcf.bgz
        """

# running main programs

rule isafe:
    input:
        vcf='{macro}/{micro}/{seed}/fair.v2.chr1.vcf.gz',
        centerfile='{macro}/{micro}/{seed}/third.best.hap.txt',
    output:
        out='{macro}/{micro}/{seed}/isafe.ranks.fair.iSAFE.out',
    params:
        head='{macro}/{micro}/{seed}/isafe.ranks.fair',
        pm=str(config['FIXED']["SIMULATE"]['BUFFER']),
    shell:
        """
        center=$(cut -f 2 {input.centerfile} | head -n 1)
        left=$(python -c "out = ${{center}} - {params.pm} ; print(out)")
        right=$(python -c "out = ${{center}} + {params.pm} ; print(out)")
        tabix -fp vcf {input.vcf}
        isafe --input {input.vcf} --output {params.head} --format vcf --region 1:${{left}}-${{right}}
        """

# sorting

rule isafe_sort:
    input:
        unsort='{macro}/{micro}/{seed}/isafe.ranks.fair.iSAFE.out',
    output:
        sort='{macro}/{micro}/{seed}/isafe.ranks.fair.tsv.gz',
    params:
        scripts=str(config['CHANGE']['FOLDERS']['TERMINALSCRIPTS']),
    shell:
        """
        python {params.scripts}/sort-pandas.py {input.unsort} {output.sort}
        """


# ranking

rule rank_isafe:
    input:
        filein='{macro}/{micro}/{seed}/isafe.ranks.fair.tsv.gz',
    output:
        fileout='{macro}/{micro}/{seed}/isafe.rank.fair.true.txt',
    params:
        scripts=str(config['CHANGE']['FOLDERS']['TERMINALSCRIPTS']),
        loc=str(config['FIXED']['SIMULATE']['LOC']),
    shell:
        """
        python {params.scripts}/truerank.py \
            {input.filein} \
            {output.fileout} \
            {params.loc} \
            1 \
            1 \
        """