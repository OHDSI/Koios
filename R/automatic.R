#' Attempt to uncover the underlying reference genome used to generate a given VCF file
#' @param vcf A vcf object read by loadVCF()
#' @return A string indicating the reference genome used
#' @export
findReference <- function(vcf){
  vcf.df <- processVCF(vcf)

  vcf.snv <- vcf.df[stringr::str_length(vcf.df$REF) == 1 & stringr::str_length(vcf.df$ALT) == 1,]

  if(dim(vcf.snv)[1] < 15){
    message("Less than 15 SNVs detected. Sampling indels.")
    vcf.snv <- vcf.df
    if(dim(vcf.snv)[1] > 50){
      vcf.snv <- vcf.snv[sample(x = dim(vcf.snv)[1], size = 50, replace = F),]
    } else{
      message("Less than 50 variants detected. Manual reference check reccomended.")
    }
  } else {
    vcf.snv <- vcf.snv[sample(x = dim(vcf.snv)[1], size = 15, replace = F),]
  }

  ref.hg18 <- loadReference("hg18")
  ref.hg19 <- loadReference("hg19")
  ref.hg38 <- loadReference("hg38")

  vcf.hg18 <- generateHGVSG(vcf.df = vcf.snv, ref.df = ref.hg18)
  vcf.hg19 <- generateHGVSG(vcf.df = vcf.snv, ref.df = ref.hg19)
  vcf.hg38 <- generateHGVSG(vcf.df = vcf.snv, ref.df = ref.hg38)

  alleles.hg18 <- processClinGen(vcf.df = vcf.hg18, ref = "hg18", generateAll = F, progressBar = F)
  alleles.hg19 <- processClinGen(vcf.df = vcf.hg19, ref = "hg19", generateAll = F, progressBar = F)
  alleles.hg38 <- processClinGen(vcf.df = vcf.hg38, ref = "hg38", generateAll = F, progressBar = F)

  alleles.hg18 <- alleles.hg18[!is.na(alleles.hg18$hgvsg),]
  alleles.hg19 <- alleles.hg19[!is.na(alleles.hg19$hgvsg),]
  alleles.hg38 <- alleles.hg38[!is.na(alleles.hg38$hgvsg),]

  alleles.hg18 <- alleles.hg18[!duplicated(alleles.hg18$variantClinGenURL),]
  alleles.hg19 <- alleles.hg19[!duplicated(alleles.hg19$variantClinGenURL),]
  alleles.hg38 <- alleles.hg38[!duplicated(alleles.hg38$variantClinGenURL),]

  #Find reference genome
  resultLength <- c(dim(alleles.hg18)[1],dim(alleles.hg19)[1],dim(alleles.hg38)[1])

  if(resultLength[which.max(resultLength)] < dim(vcf.snv)[1]){
    message(paste("Only ", resultLength[which.max(resultLength)],
                  " results returned from ",dim(vcf.snv)[1],
                  " tested records. We reccomend checking your VCF data."))
  }

  #Set reference genome
  ref <- c("hg18","hg19","hg38")[which.max(resultLength)]

  message(paste("Reference set as: ", ref, sep = ""))

  return(ref)
}

#' Run the default pipeline on a set of VCF objects submitted as a directory input
#' @param vcf A vcf object read by loadVCF(), containing a list of VCF files
#' @param ref A reference specification for the original reference genome, one of "hg18", "hg19", "hg38" or "auto"
#' @param generateAll A reference specification for the original reference genome, one of "hg18", "hg19", "hg38" or "auto"
#' @param concepts A concept set derived from loadConcepts()
#' @return A list containing the relevant set of outputs for a list of VCF files
#' @export
multiVCFPipeline <- function(vcf, ref, generateAll, concepts){

  if(ref=="auto"){
    message("Ref is set to auto in list mode - This may lead to a long runtime!")
    refWasAuto <- TRUE
  } else{
    ref.df <- loadReference(ref)
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
      ref.df <- loadReference(ref)
    }

    vcf.df <- processVCF(tempVCF)

    vcf.df <- generateHGVSG(vcf.df = vcf.df, ref.df = ref.df)

    alleles.df <- processClinGen(vcf.df, ref, generateAll = generateAll, progressBar = T)
    alleles.df$fileName <- tempName

    alleles.df.All <- rbind(alleles.df.All,alleles.df)

    concepts.df <- addConcepts(alleles.df, concepts, returnAll = T)
    concepts.df$fileName <- tempName

    concepts.df.All <- rbind(concepts.df.All,concepts.df)
  }

  return(list(alleles.df.All,concepts.df.All))

}

