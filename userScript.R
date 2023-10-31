library(KOIOS)

##### INPUT #####

#Load concept library
concepts <- loadConcepts()

#Input VCF
vcf <- loadVCF(userVCF = "../KOIOS_testing/")

#Please enter one of hg18, hg19, hg38 or "auto"
ref <- "hg19"

#Please indicate whether or not you would like to return all transcript alleles
generateTranscripts <- "TRUE"

##### MAIN #####
if(typeof(vcf) == "list"){

  if(ref=="auto"){
    message("Ref is set to auto in list mode - This may lead to a long runtime!")
    refWasAuto <- TRUE
  } else{
    refWasAuto <- FALSE
  }

  alleles.df.All <- as.data.frame(matrix(ncol = 8))[-1,]
  colnames(alleles.df.All) <- c("Allele#", "variantClinGenURL", "hgvsg", "varType", "geneSymbol", "chr",
                                "ref", "fileName")

  concepts.df.All <- as.data.frame(matrix(ncol = 11))[-1,]
  colnames(concepts.df.All) <- c("Allele#", "concept_id", "hgvsg", "variantClinGenURL", "varType", "geneSymbol", "chr",
                                "ref", "concept_name", "concept_class_id","fileName")

  for(i in c(1:length(vcf))){

    print(i)

    if(refWasAuto==TRUE){
      ref <- "auto"
    }

    if(length(vcfR::getFIX(vcf[[i]])) < 1){
      next
    }

    tempName <- names(vcf)[i]
    tempVCF <- vcf[[i]]

    #Automatic mode - sampling and testing
    if(ref == "auto"){
      ref <- findReference(tempVCF)
    }

    ref.df <- loadReference(ref)

    vcf.df <- processVCF(tempVCF)

    vcf.df <- generateHGVSG(vcf = vcf.df, ref = ref.df)

    alleles.df <- processClinGen(vcf.df,ref,generateAll = generateTranscripts, progressBar = T)
    alleles.df$fileName <- tempName

    alleles.df.All <- rbind(alleles.df.All,alleles.df)

    concepts.df <- addConcepts(alleles.df, concepts, returnAll = T)
    concepts.df$fileName <- tempName

    concepts.df.All <- rbind(concepts.df.All,concepts.df)
  }

  write.csv(concepts.df.All, "Concepts_DF_All.csv", row.names = F)
  write.csv(alleles.df.All, "Alleles_DF_All.csv", row.names = F)

} else {

  #Automatic mode - sampling and testing
  if(ref == "auto"){
    ref <- findReference(vcf)
  }

  ref.df <- loadReference(ref)

  vcf.df <- processVCF(vcf)

  vcf.df <- generateHGVSG(vcf = vcf.df, ref = ref.df)

  alleles.df <- processClinGen(vcf.df,ref,generateAll = generateTranscripts, progressBar = T)

  concepts.df <- addConcepts(alleles.df, concepts, returnAll = T)

  write.csv(concepts.df, "Concepts_DF.csv", row.names = F)
  write.csv(alleles.df, "Alleles_DF.csv", row.names = F)


}
