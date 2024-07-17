import functools
import os
import hail as hl
import pandas as pd
from bokeh.plotting import output_notebook

def once(func):
    """Decorator that execute the function only one time"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Initialize has_run on first call using getattr
        wrapper.has_run = getattr(wrapper, 'has_run', False)
        if not wrapper.has_run:
            wrapper.has_run = True
            func(*args, **kwargs)
        else:
            print("Hail was already initialized.")

    return wrapper


@once
def hail_init():
    # Get the Google billing project name and workspace name
    billing_project = os.environ['WORKSPACE_NAMESPACE']
    # workspace = os.environ['WORKSPACE_NAME']
    workspace = os.path.basename(os.path.dirname(os.getcwd()))
    bucket = os.environ['WORKSPACE_BUCKET'] + "/"

    # Verify that we've captured the environment variables
    print("Billing project: " + billing_project)
    print("Workspace: " + workspace)
    print("Workspace storage bucket: " + bucket)

    # After importing, start a Hail session
    hl.init(default_reference="GRCh38", log='LLABUTILS_extraction.log')
    output_notebook()


def genetable_fromMT(
        db=None,
        phenoFile=None,
        samples=None,
        gene=None,
        variant_type=None,
        output=None):
    """
    Filters a Hail MatrixTable based on gene symbol and consequence type.

    Args:
        db (str, required): Path to the Hail database (MT) file. Defaults to "path/to/your/hail.mt".
        phenoFile (str, required): Path to the phenotype file. Default ALS compute v2.
        samples (str/list, optional): subsample your table based on single sample or list.
        gene (str/list, required): Gene symbol to filter on. Defaults to None.
        variant_type (str/list, Optional): Consequence type (e.g., "missense") to filter on. Defaults to None.
        output (str, required): Path to export the filtered Hail table (row format) as a TSV file. Defaults to "output.tsv".

    Returns:
        None

    Type of variation:
    transcript_ablation
    splice_acceptor_variant
    splice_donor_variant
    stop_gained
    frameshift_variant
    stop_lost
    start_lost
    transcript_amplification
    feature_elongation
    feature_truncation
    inframe_insertion
    inframe_deletion
    missense_variant
    protein_altering_variant
    splice_donor_5th_base_variant
    splice_region_variant
    splice_donor_region_variant
    splice_polypyrimidine_tract_variant
    incomplete_terminal_codon_variant
    start_retained_variant
    stop_retained_variant
    synonymous_variant
    coding_sequence_variant
    mature_miRNA_variant
    5_prime_UTR_variant
    3_prime_UTR_variant
    non_coding_transcript_exon_variant
    intron_variant
    NMD_transcript_variant
    non_coding_transcript_variant
    coding_transcript_variant
    upstream_gene_variant
    downstream_gene_variant
    TFBS_ablation
    TFBS_amplification
    TF_binding_site_variant
    regulatory_region_ablation
    regulatory_region_amplification
    regulatory_region_variant
    intergenic_variant
    sequence_variant

    """
    # init hail:
    hail_init()
    # Load the hail database:
    mt = hl.read_matrix_table(db)
    # Load the subsample file:
    pheno = hl.import_table(phenoFile, delimiter='\t')
    # Annotate matrix with phenotypes
    pheno = pheno.key_by('Sample ID_alberto jcall')
    mt = mt.annotate_cols(pheno=pheno[mt.s])

    if samples is not None:
            if isinstance(samples, list):
                # Filter for multiple gene types using OR
                filter_expr = None
                for sample in samples:
                    if filter_expr is None:
                        filter_expr = (mt.s == sample)
                    else:
                        filter_expr = filter_expr | (mt.s == sample)
                mt = mt.filter_cols(filter_expr)
                # create new variant qc:
                mt = hl.variant_qc(mt)
                # filter WT using new allele frequency
                mt = mt.filter_rows(mt.variant_qc.AF[1] == 0, keep=False)
            else:
                # Filter for a single gene (use equality check)
                mt = mt.filter_cols(mt.s == samples)
                # create new variant qc:
                mt = hl.variant_qc(mt)
                # filter WT using new allele frequency
                mt = mt.filter_rows(mt.variant_qc.AF[1] == 0, keep=False)

    # Extract gene:
    if isinstance(gene, list):
        # Filter for multiple gene types using OR
        filter_expr = None
        for g in gene:
            if filter_expr is None:
                filter_expr = (mt.vep.transcript_consequences.gene_symbol[0] == g)
            else:
                filter_expr = filter_expr | (mt.vep.transcript_consequences.gene_symbol[0] == g)
        mt_ft = mt.filter_rows(filter_expr)
    else:
        # Filter for a single gene (use equality check)
        mt_ft = mt.filter_rows(mt.vep.transcript_consequences.gene_symbol[0] == gene)
    # annotate row with gene symbol
    mt_ft = mt_ft.annotate_rows(gene=mt_ft.vep.transcript_consequences.gene_symbol[0])
    # annotate with exon
    mt_ft = mt_ft.annotate_rows(exon=mt_ft.vep.transcript_consequences.exon)
    # annotate row with consequences
    mt_ft = mt_ft.annotate_rows(consequence=mt_ft.vep.most_severe_consequence)
    # annotate with aa:
    mt_ft = mt_ft.annotate_rows(amino_acids=mt_ft.vep.transcript_consequences.amino_acids)
    # protein end:
    mt_ft = mt_ft.annotate_rows(protein_end=mt_ft.vep.transcript_consequences.protein_end)
    # annotate row with het samples count
    mt_ft = mt_ft.annotate_rows(het_samples=hl.agg.count_where(mt_ft.GT.is_het()))
    # annotate row with homvar samples count
    mt_ft = mt_ft.annotate_rows(homvar_samples=hl.agg.count_where(mt_ft.GT.is_hom_var()))
    # annotate row with het samples IDs
    mt_ft = mt_ft.annotate_rows(het_sample_ids=hl.agg.filter(mt_ft.GT.is_het(), hl.agg.collect(mt_ft.s)))
    # annotate row with homvar samples IDs
    mt_ft = mt_ft.annotate_rows(hom_var_sample_ids=hl.agg.filter(mt_ft.GT.is_hom_var(), hl.agg.collect(mt_ft.s)))
    # anno entries with case and control info:
    mt_ft = mt_ft.annotate_entries(caco=mt_ft.pheno["status-joint call"])
    # annotate row with cases IDS:
    mt_ft = mt_ft.annotate_rows(
        cases_sample_ids=hl.agg.filter((((mt_ft.GT.is_het()) | (mt_ft.GT.is_hom_var())) & (mt_ft.caco == "case")),
                                       hl.agg.collect(mt_ft.s)))
    # annotate row with case samples count:
    mt_ft = mt_ft.annotate_rows(
        n_cases=hl.agg.count_where((((mt_ft.GT.is_het()) | (mt_ft.GT.is_hom_var())) & (mt_ft.caco == "case"))))
    # annotate row with controls IDS:
    mt_ft = mt_ft.annotate_rows(
        controls_sample_ids=hl.agg.filter((((mt_ft.GT.is_het()) | (mt_ft.GT.is_hom_var())) & (mt_ft.caco == "control")),
                                          hl.agg.collect(mt_ft.s)))
    # annotate row with control samples count:
    mt_ft = mt_ft.annotate_rows(
        n_controls=hl.agg.count_where((((mt_ft.GT.is_het()) | (mt_ft.GT.is_hom_var())) & (mt_ft.caco == "control"))))
    # drop not necessary rows:
    mt_ft = mt_ft.drop('hwe_ctrl', 'rsid', 'qual', 'filters', 'info', 'a_index', 'was_split', 'variant_qc', 'vep',
                       'vep_proc_id')
    # Filter rows based on variant type
    if variant_type is not None:
        if isinstance(variant_type, list):
            # Filter for multiple variant types using OR
            filter_expr = None
            for consequence in variant_type:
                if filter_expr is None:
                    filter_expr = (mt_ft.consequence == consequence)
                else:
                    filter_expr = filter_expr | (mt_ft.consequence == consequence)
            mt_ft = mt_ft.filter_rows(filter_expr)
        else:
            # Filter for a single variant type (use equality check)
            mt_ft = mt_ft.filter_rows(mt_ft.consequence == variant_type)
    # export table
    mt_ft.row.export(output)


def singlesample_fromMT(
        db=None,
        phenoFile=None,
        sample=None,
        gene=None,
        variant_type=None,
        output_type="table",
        output_path=None,
        output_name=None):
    """
    Filters a Hail MatrixTable based on single sample.

    Args:
        db (str, required): Path to the Hail database (MT) file. Defaults to "path/to/your/hail.mt".
        phenoFile (str, required): Path to the phenotype file. Default ALS compute v2.
        sample (str, required): subsample db.
        gene (str/list, required if table): Gene symbol to filter on. Defaults to None.
        variant_type (str/list, Optional): Consequence type (e.g., "missense") to filter on. Defaults to None.
        output_type (str, optional): table or vcf output. Default "table".
        output_path (str, required): Path to export the filtered Hail table (row format)
        output_name (str, required):  Outout file name.

    Returns:
        None
    """

    hail_init()
    # Load the hail database:
    mt = hl.read_matrix_table(db)
    # Load the subsample file:
    pheno = hl.import_table(phenoFile, delimiter='\t')
    # Annotate matrix with phenotypes
    pheno = pheno.key_by('Sample ID_alberto jcall')
    mt = mt.annotate_cols(pheno=pheno[mt.s])
    # anno entries with case and control info:
    mt = mt.annotate_entries(caco=mt.pheno["status-joint call"])
    # annotate row with case samples count:
    mt = mt.annotate_rows(n_cases=hl.agg.count_where((((mt.GT.is_het()) | (mt.GT.is_hom_var())) & (mt.caco == "case"))))
    # annotate row with control samples count:
    mt = mt.annotate_rows(
        n_controls=hl.agg.count_where((((mt.GT.is_het()) | (mt.GT.is_hom_var())) & (mt.caco == "control"))))
    # filter sample:
    mt = mt.filter_cols(mt.s == sample)
    # remove NA:
    mt = hl.variant_qc(mt)
    mt = mt.filter_rows(mt.variant_qc.AN > 0)
    # create a new row field eith the number of alternate alleles:
    mt = mt.annotate_rows(N_ALT_ALLELES=hl.agg.sum(mt.GT.n_alt_alleles()))
    # Filter matrix table, only if there at least 1 variant with ALT allele:
    mt = mt.filter_rows(mt.N_ALT_ALLELES > 0)
    if output_type == "table":
        # Extract gene:
        if isinstance(gene, list):
            # Filter for multiple gene types using OR
            filter_expr = None
            for g in gene:
                if filter_expr is None:
                    filter_expr = (mt.vep.transcript_consequences.gene_symbol[0] == g)
                else:
                    filter_expr = filter_expr | (mt.vep.transcript_consequences.gene_symbol[0] == g)
            mt_ft = mt.filter_rows(filter_expr)
        else:
            # Filter for a single gene (use equality check)
            mt_ft = mt.filter_rows(mt.vep.transcript_consequences.gene_symbol[0] == gene)

        # annotate row with gene symbol
        mt_ft = mt_ft.annotate_rows(gene=mt_ft.vep.transcript_consequences.gene_symbol[0])
        # annotate with exon
        mt_ft = mt_ft.annotate_rows(exon=mt_ft.vep.transcript_consequences.exon)
        # annotate row with consequences
        mt_ft = mt_ft.annotate_rows(consequence=mt_ft.vep.most_severe_consequence)
        # annotate with aa:
        mt_ft = mt_ft.annotate_rows(amino_acids=mt_ft.vep.transcript_consequences.amino_acids)
        # protein end:
        mt_ft = mt_ft.annotate_rows(protein_end=mt_ft.vep.transcript_consequences.protein_end)
        # annotate row with het samples count
        mt_ft = mt_ft.annotate_rows(het=hl.agg.count_where(mt_ft.GT.is_het()))
        # annotate row with homvar samples count
        mt_ft = mt_ft.annotate_rows(homvar=hl.agg.count_where(mt_ft.GT.is_hom_var()))
        # drop not necessary rows:
        mt_ft = mt_ft.drop('hwe_ctrl', 'rsid', 'qual', 'filters', 'info', 'a_index', 'was_split', 'variant_qc', 'vep',
                           'vep_proc_id')
        # Filter rows based on variant type
        if variant_type is not None:
            if isinstance(variant_type, list):
                # Filter for multiple variant types using OR
                filter_expr = None
                for consequence in variant_type:
                    if filter_expr is None:
                        filter_expr = (mt_ft.consequence == consequence)
                    else:
                        filter_expr = filter_expr | (mt_ft.consequence == consequence)
                mt_ft = mt_ft.filter_rows(filter_expr)
            else:
                # Filter for a single variant type (use equality check)
                mt_ft = mt_ft.filter_rows(mt_ft.consequence == variant_type)
        # export table
        mt_ft.row.export(f"{output_path}{output_name}")
    elif output_type == "vcf":
        hl.export_vcf(mt, f"{output_path}{output_name}.vcf.bgz")
    else:
        print("Output type error...please retry with vcf or table")


def jointVCF_fromMT(db=None,
                    samples_file=None,
                    output_path=None,
                    output_name=None):
    """
    Filters a Hail MatrixTable and create joint final VCFs.

    Args:
        db (str, required): Path to the Hail database (MT) file. Defaults to "path/to/your/hail.mt".
        samples_file (str, required): subsample file path.
        output_path (str, required): Export path.
        output_name (str, required): Output file name.

    Returns:
        None
    """

    hail_init()
    # Load the hail database:
    mt = hl.read_matrix_table(db)
    # Load the subsample file:
    anno_file = samples_file
    pheno = hl.import_table(anno_file, delimiter='\t')
    # Annotate matrix with phenotypes
    pheno = pheno.key_by('sampleID')
    mt = mt.annotate_cols(pheno=pheno[mt.s])
    df = pd.read_csv(samples_file, sep='\t', header=[0])
    group = df["subsample"].values[0]
    # Filter samples:
    mt = mt.filter_cols(mt.pheno.subsample == group)
    # create new variant qc:
    mt = hl.variant_qc(mt)
    # filter WT using allele frequency
    mt = mt.filter_rows(mt.variant_qc.AF[1] == 0, keep=False)
    # Filter and export chromosomes in a loop with string formatting
    for chr_num in range(1, 23):
        chr_name = f"chr{chr_num}"
        filtered_chr = mt.filter_rows(mt.locus.contig == chr_name)
        hl.export_vcf(filtered_chr, f"{output_path}{chr_name}{output_name}.vcf.bgz")

    # Filter and export chrX and chrY (if present)
    filtered_chrX = mt.filter_rows(mt.locus.contig == "chrX")
    hl.export_vcf(filtered_chrX, f"{output_path}CHRX{output_name}.vcf.bgz")

    filtered_chrY = mt.filter_rows(mt.locus.contig == "chrY")
    hl.export_vcf(filtered_chrY, f"{output_path}CHRY{output_name}.vcf.bgz")

def extract_regions(db=None,
                    phenoFile=None,
                    samples=None,
                    gene=None,
                    region=None,
                    output_type="table",
                    output = None):
    """
    Filters a Hail MatrixTable based on genomic regions.

    Args:
    db (str, required): Path to the Hail database (MT) file. Defaults to "path/to/your/hail.mt".
    phenoFile (str, required): Path to the phenotype file. Default ALS compute v2.
    samples (str, required): subsample db.
    gene (str/list, required if table): Gene symbol to filter on. Defaults to None.
    region (list, required): string or list of regions to extract.
    output_type (str, optional): table or vcf output. Default "table".
    output (str, required):  Output file path.

    Returns:
    None
    """
    # init hail:
    hail_init()
    # Load the hail database:
    mt = hl.read_matrix_table(db)
    # Load the subsample file:
    pheno = hl.import_table(phenoFile, delimiter='\t')
    # Annotate matrix with phenotypes
    pheno = pheno.key_by('Sample ID_alberto jcall')
    mt = mt.annotate_cols(pheno=pheno[mt.s])
    if samples is not None:
        if isinstance(samples, list):
            # Filter for multiple gene types using OR
            filter_expr = None
            for sample in samples:
                if filter_expr is None:
                    filter_expr = (mt.s == sample)
                else:
                    filter_expr = filter_expr | (mt.s == sample)
            mt = mt.filter_cols(filter_expr)
            # create new variant qc:
            mt = hl.variant_qc(mt)
            # filter WT using new allele frequency
            mt = mt.filter_rows(mt.variant_qc.AF[1] == 0, keep=False)
            # update AF, AN , AC info field:
            mt = mt.annotate_rows(info=mt.info.annotate(AC=mt.variant_qc.AC[1]))
            mt = mt.annotate_rows(info=mt.info.annotate(AF=mt.variant_qc.AF[1]))
            mt = mt.annotate_rows(info=mt.info.annotate(AN=mt.variant_qc.AN))
        else:
            # Filter for a single gene (use equality check)
            mt = mt.filter_cols(mt.s == samples)
            # create new variant qc:
            mt = hl.variant_qc(mt)
            # filter WT using new allele frequency
            mt = mt.filter_rows(mt.variant_qc.AF[1] == 0, keep=False)
            # update AF, AN , AC info field:
            mt = mt.annotate_rows(info=mt.info.annotate(AC=mt.variant_qc.AC[1]))
            mt = mt.annotate_rows(info=mt.info.annotate(AF=mt.variant_qc.AF[1]))
            mt = mt.annotate_rows(info=mt.info.annotate(AN=mt.variant_qc.AN))

            # Extract gene:
    if gene is not None:
        if isinstance(gene, list):
            # Filter for multiple gene types using OR
            filter_expr = None
            for g in gene:
                if filter_expr is None:
                    filter_expr = (mt.vep.transcript_consequences.gene_symbol[0] == g)
                else:
                    filter_expr = filter_expr | (mt.vep.transcript_consequences.gene_symbol[0] == g)
            mt_ft = mt.filter_rows(filter_expr)
        else:
            # Filter for a single gene (use equality check)
            mt_ft = mt.filter_rows(mt.vep.transcript_consequences.gene_symbol[0] == gene)

    # Filter region:
    mt = hl.filter_intervals(mt, [hl.parse_locus_interval(x, ) for x in region])

    if output_type == "table":
        # annotate row with gene symbol
        mt = mt.annotate_rows(gene=mt.vep.transcript_consequences.gene_symbol[0])
        # annotate with exon
        mt = mt.annotate_rows(exon=mt.vep.transcript_consequences.exon)
        # annotate row with consequences
        mt = mt.annotate_rows(consequence=mt.vep.most_severe_consequence)
        # annotate with aa:
        mt = mt.annotate_rows(amino_acids=mt.vep.transcript_consequences.amino_acids)
        # protein end:
        mt = mt.annotate_rows(protein_end=mt.vep.transcript_consequences.protein_end)
        # annotate row with het samples count
        mt = mt.annotate_rows(het_samples=hl.agg.count_where(mt.GT.is_het()))
        # annotate row with homvar samples count
        mt = mt.annotate_rows(homvar_samples=hl.agg.count_where(mt.GT.is_hom_var()))
        # annotate row with het samples IDs
        mt = mt.annotate_rows(het_sample_ids=hl.agg.filter(mt.GT.is_het(), hl.agg.collect(mt.s)))
        # annotate row with homvar samples IDs
        mt = mt.annotate_rows(hom_var_sample_ids=hl.agg.filter(mt.GT.is_hom_var(), hl.agg.collect(mt.s)))
        # anno entries with case and control info:
        mt = mt.annotate_entries(caco=mt.pheno["status-joint call"])
        # annotate row with cases IDS:
        mt = mt.annotate_rows(
            cases_sample_ids=hl.agg.filter((((mt.GT.is_het()) | (mt.GT.is_hom_var())) & (mt.caco == "case")),
                                           hl.agg.collect(mt.s)))
        # annotate row with case samples count:
        mt = mt.annotate_rows(
            n_cases=hl.agg.count_where((((mt.GT.is_het()) | (mt.GT.is_hom_var())) & (mt.caco == "case"))))
        # annotate row with controls IDS:
        mt = mt.annotate_rows(
            controls_sample_ids=hl.agg.filter((((mt.GT.is_het()) | (mt.GT.is_hom_var())) & (mt.caco == "control")),
                                              hl.agg.collect(mt.s)))
        # annotate row with control samples count:
        mt = mt.annotate_rows(
            n_controls=hl.agg.count_where((((mt.GT.is_het()) | (mt.GT.is_hom_var())) & (mt.caco == "control"))))
        # drop not necessary rows:
        mt = mt.drop('hwe_ctrl', 'rsid', 'qual', 'filters', 'info', 'a_index', 'was_split', 'variant_qc', 'vep',
                     'vep_proc_id')
        # export table:
        mt.row.export(output)

    elif output_type == "vcf":
        hl.export_vcf(mt, output)

    else:
        print("\n Output Type not recognized. Please use 'table' or 'vcf'")
