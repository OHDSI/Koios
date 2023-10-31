#' Process a vcfR object, or list of vcfR objects, to return a dataframe
#' containing hgvsg notation for all variants, as well as all clingen urls
#' @param vcfR Input vcfR object
#' @return A dataframe containing hgvsg notation and clingen urls for all variants
#' @export
processVCF <- function(vcfR){

  if(length(vcfR::getCHROM(vcfR))==1){
    vcf.df <- as.data.frame(t(as.data.frame(vcfR::getFIX(vcfR))))
  } else {
    vcf.df <- as.data.frame(vcfR::getFIX(vcfR))
  }

  colnames(vcf.df) <- c("CHROM","POS","ID","REF","ALT","QUAL","FILTER")

  return(vcf.df)

}

#' Process a single vcfR object to return a dataframe containing hgvsg notation
#' @param vcf.df Input vcf.df object
#' @param ref.df A ref.df object containing chrom specifications
#' @return A dataframe containing hgvsg notation for all variants
#' @export
generateHGVSG <- function(vcf.df, ref.df){

  #Convert conditional SNPs into two distinct rows
  vcf.df <- vcf.df %>%
    tidyr::separate_rows("ALT",sep = ",")

  #Remove NA rows (For now)
  vcf.df <- vcf.df[!is.na(vcf.df$REF),]
  vcf.df <- vcf.df[!is.na(vcf.df$ALT),]
  vcf.df <- vcf.df[!is.na(vcf.df$POS),]

  #Remove "chr", "Chr" and "chr "
  vcf.df$CHROM <- gsub("chr|Chr|chr ","",vcf.df$CHROM)

  vcf.df <- vcf.df %>%
    dplyr::mutate(REF_L = stringr::str_length(.data$REF), ALT_L = stringr::str_length(.data$ALT)) %>%
    dplyr::mutate(TYPE = ifelse(.data$REF_L == 1 & .data$ALT_L == 1, "SNP",
                                ifelse(.data$REF_L > .data$ALT_L & .data$ALT_L == 1, "DEL",
                                       ifelse(.data$ALT_L > .data$REF_L & .data$REF_L == 1, "INS", "DELINS")))) %>%
    dplyr::select(.data$CHROM,.data$POS,.data$REF,
                  .data$REF_L,.data$ALT,.data$ALT_L,
                  .data$TYPE)

  vcf.df$hgvsg <- apply(vcf.df, 1, FUN = function(x)
    hgvsgConvert(row = x, ref.df = ref.df))

  return(vcf.df)

}

#' Generate a hgvsg string
#' @param row A vcf.df row
#' @param ref.df A ref.df object containing chrom specifications
#' @return A single hgvsg string
#' @export
hgvsgConvert <- function(row,ref.df){

  Chr <- ref.df[ref.df$Molecule_name == row[1],]$RefSeq_sequence

  if(row[7] == "SNP"){
    hgvsg <- paste(Chr,":g.",row[2],row[3],">",row[5],sep="")
  } else if(row[7] == "DEL"){
    modPOS <- as.numeric(row[2])+1
    hgvsg <- paste(Chr,":g.",modPOS,"_",modPOS+as.numeric(row[4])-2,"del",sep="")
  } else if(row[7] == "INS"){
    modPOS <- as.numeric(row[2])+1
    hgvsg <- paste(Chr,":g.",row[2],"_",modPOS,"ins",gsub("^.","",row[5]),sep="")
  } else if(row[7] == "DELINS"){
    modPOS <- as.numeric(row[2])+1
    hgvsg <- paste(Chr,":g.",row[2],"_",modPOS,"delins",row[5],sep="")
  }

  return(hgvsg)

}
