#' Generate a set of processed alignments given a stringDF dataframe
#' @return A set of concept synonyms for the OMOP Genomic dataset, derived from ATHENA
#' @export
loadConcepts <- function(){
  return(KOIOS::concepts)
}

#' Generate a set of reference maps between chromosome IDs
#' @param ref The chosen reference genome, hg18/hg19/hg38
#' @return A map of synonyms between chromosome IDs for a given reference genome
#' @export
loadReference <- function(ref=ref){
  if(ref == "hg18"){
    ref.data <- GenomeInfoDb::getChromInfoFromNCBI(assembly = "NCBI36")
  } else if(ref == "hg19"){
    ref.data <- GenomeInfoDb::getChromInfoFromNCBI(assembly = "GRCh37")
  } else if(ref == "hg38"){
    ref.data <- GenomeInfoDb::getChromInfoFromNCBI(assembly = "GRCh38")
  }

  ref.data <- ref.data[,c(1,4,9,6)] %>%
    tidyr::pivot_longer(cols = c("SequenceName","GenBankAccn","UCSCStyleName"))

  ref.df <- ref.data[,c(3,1)]
  colnames(ref.df) <- c("Molecule_name","RefSeq_sequence")

  ref.df <- ref.df[!(is.na(ref.df$Molecule_name)|is.na(ref.df$RefSeq_sequence)),]

  return(ref.df)
}

#' Load a single .vcf file or a set of .vcf's located in a single directory
#' @param userVCF A user-defined .vcf file or a directory containing several .vcf objects
#' @return Either a single vcfR object or a list of vcfR objects
#' @export
loadVCF <- function(userVCF){

  if(file.exists(userVCF) && !dir.exists(userVCF)) {

    vcf <- vcfR::read.vcfR(file = userVCF, verbose = 0)

    return(vcf)

  } else if(dir.exists(userVCF)) {

    outList <- list()
    fileList <- list.files(path = userVCF)

    message(paste("Found ", length(fileList), " files in input directory.", sep=""))

    for(file in fileList){

      vcfTemp <- vcfR::read.vcfR(file = paste(here::here(),"/",userVCF,"/",file,sep=""), verbose = 0)
      outList <- append(outList,vcfTemp)

    }

    names(outList) <- fileList

    return(outList)

  }
}
