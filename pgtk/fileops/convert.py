from pgtk.io.vcf import convert_vcf_to_zarr


def run_convert(args):
    convert_vcf_to_zarr(args.vcf, args.tmpdir)
