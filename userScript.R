library(KOIOS)
setwd("C:/Users/ldyer/Documents/KOIOS_Symposium/")

##### Input #####

#Load the OMOP Genomic Concept library
concepts <- loadConcepts()

#Load the VCF file
vcf <- loadVCF(userVCF = "Something.VCF")

#Set the reference genome to "auto"
ref <- "auto"

#Toggle return all transcript alleles (as well as genomic alleles)
generateTranscripts <- "TRUE"

##### Run - Single VCF #####
if(ref == "auto"){
  ref <- findReference(vcf)
}

ref.df <- loadReference(ref)

vcf.df <- processVCF(vcf)

vcf.df <- generateHGVSG(vcf = vcf.df, ref = ref.df)

alleles.df <- processClinGen(vcf.df,ref,generateAll = generateTranscripts, progressBar = T)

concepts.df <- addConcepts(alleles.df, concepts, returnAll = T)

concepts.df.filt <- concepts.df[!is.na(concepts.df$concept_name),]



##### Run - Multiple VCFs #####

#Load the VCF directory
vcf <- loadVCF(userVCF = "SomeDirectory/")

#Set ref to hg19
ref <- "hg19"

output <- multiVCFPipeline(vcf, ref, generateTranscripts, concepts)

alleles.df <- output[[1]]
concepts.df <- output[[2]]

concepts.df.filt <- concepts.df[!is.na(concepts.df$concept_id),]



