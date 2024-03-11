library(KOIOS)
setwd("C:/Users/ldyer/Documents/KOIOS2.0/KOIOS/")

##### Input #####

#Load the OMOP Genomic Concept library
concepts <- loadConcepts()

#Load the VCF file
vcf <- loadVCF(userVCF = "../KOIOS_testing/VCF/")

#Set the reference genome to "auto"
ref <- "hg19"

#Toggle return all transcript alleles (as well as genomic alleles)
generateTranscripts <- "TRUE"

##### Run - Single VCF #####
if(ref == "auto"){
  ref <- findReference(vcf)
}

ref.df <- loadReference(ref)

vcf.df <- processVCF(vcf)

vcf.df <- generateHGVSG(vcf = vcf.df, ref = ref.df)

concepts.df <- addConcepts(vcf.df, concepts, returnAll = T)

##### Run - Multiple VCFs #####

#Load the VCF directory
vcf <- loadVCF(userVCF = "SomeDirectory/")

#Set ref to hg19
ref <- "hg19"

concepts.df <- multiVCFPipeline(vcf, ref, generateTranscripts, concepts)

concepts.df.filt <- concepts.df[!is.na(concepts.df$concept_id),]



