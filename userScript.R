library(KOIOS)
setwd("C:/Users/ldyer/Documents/KOIOS2.0/KOIOS/")

##### Input #####

#Load the OMOP Genomic Concept library
concepts <- loadConcepts()

#Load the VCF file
vcf <- loadVCF(userVCF = "SomeVCF.vcf")

#Set the reference genome to "auto"
ref <- "hg19"

##### Run - Single VCF #####
if(ref == "auto"){
  ref <- findReference(vcf)
}

ref.df <- loadReference(ref)

vcf.df <- processVCF(vcf)
vcf.df <- generateHGVSG(vcf = vcf.df, ref = ref.df)
vcf.df <- processClinGen(vcf.df, ref = ref, progressBar = F)
vcf.df <- addConcepts(vcf.df, concepts, returnAll = T)

##### Run - Multiple VCFs #####

#Load the VCF directory
vcf <- loadVCF(userVCF = "SomeDirectory/")

#Set ref to hg19
ref <- "hg19"

concepts.df <- multiVCFPipeline(vcf, ref, concepts)

##### Alternative Data Formats #####

#cBioPortal
mutations <- read.csv("data_mutations.txt", sep = "\t")
mut_vcf <- processcBioPortal(mutations)
mut_vcf <- processClinGen(mut_vcf, ref = "hg19", progressBar = F)
mut_vcf <- addConcepts(mut_vcf,concepts)

#cBioPortal - Transcripts
concepts_ext <- loadConcepts_extended()

mutations <- read.csv("data_mutations.txt", sep = "\t")
mut_transcripts <- mutations[,c(5,6,7,11,13,14,38)]
mut_transcripts$Input_ID <- c(1:length(mut_transcripts$HGVSc))

mut_transcripts$match_hgvs <- gsub(".[0-9]*:",":",mut_transcripts$HGVSc)
concepts_ext$match_hgvs <- gsub(".[0-9]*:",":",concepts_ext$concept_synonym_name)

mut_merge <- merge(mut_transcripts,concepts_ext,by="match_hgvs")
