#' Process a vcf.df dataframe to return clingen data for all variants
#' @param vcf.df Input vcf.df object
#' @param ref A string indicating the reference genome used
#'                Must be one of: hg18
#'                                hg19
#'                                hg38
#' @param generateAll A toggle indicating whether all transcript alleles, as well as
#' all genomic alleles, should be returned
#' @param progressBar A toggle indicating whether or not a progress bar will be displayed
#' @return A dataframe containing data derived from the relevant ClinGen URL
#' for each allele found corresponding to a vcf row
#' @export
processClinGen <- function(vcf.df, ref, generateAll = FALSE, progressBar = TRUE){

  #Create a handle
  thisHandle <- httr::handle("http://reg.test.genome.network/")

  vcf.df$URL <- paste("http://reg.test.genome.network/allele?hgvs=",vcf.df$hgvsg,sep="")

  returnDat <- as.data.frame(matrix(ncol = 8))
  colnames(returnDat) <- c("Allele#","variantClinGenURL","hgvsg",
                           "varType","geneSymbol","chr","ref","communityStandardTitle")

  start <- proc.time()[3]

  k <- 1

  for(i in c(1:length(vcf.df$URL))) {

    skip_to_next <- FALSE

    tempVCF <- vcf.df[i,]

    urlTest <- httr::GET(handle = thisHandle,
                         path = gsub(thisHandle$url,"",tempVCF$URL),
                         encoding = "UTF-8", as = "text")

    variant <- RcppSimdJson::fparse(urlTest$content)

    if(progressBar == TRUE){
      progress(x = i, max = length(vcf.df$URL))
      eta(x = i, max = length(vcf.df$URL), start)
    }

    genes <- c()

    if(!is.null(variant$transcriptAlleles)){

      for(l in c(1:dim(variant$transcriptAlleles)[1])){

        genes <- c(genes,
                   variant$transcriptAlleles$geneSymbol[l])

      }

    }

    genes <- paste(na.omit(unique(genes)),collapse = ", ")

    if(!is.null(variant$transcriptAlleles)){

      for(l in c(1:dim(variant$transcriptAlleles)[1])){

        if(generateAll == TRUE){
          if("MANE" %in% colnames(variant$transcriptAlleles)){

            if(!is.na(variant$transcriptAlleles$MANE[[l]][[1]])){

              returnDat[k,]$`Allele#` <- i
              returnDat[k,]$variantClinGenURL <- tempVCF$URL
              returnDat[k,]$hgvsg <- variant$transcriptAlleles$MANE[[l]]$nucleotide$RefSeq$hgvs
              returnDat[k,]$geneSymbol <- paste(unique(genes),collapse=", ")
              returnDat[k,]$varType <- tempVCF$TYPE
              returnDat[k,]$chr <- tempVCF$CHROM
              returnDat[k,]$ref <- ref
              returnDat[k,]$communityStandardTitle <- variant$communityStandardTitle[[1]]

              k <- k + 1

              returnDat[k,]$`Allele#` <- i
              returnDat[k,]$variantClinGenURL <- tempVCF$URL
              returnDat[k,]$hgvsg <- variant$transcriptAlleles$MANE[[l]]$protein$RefSeq$hgvs
              returnDat[k,]$geneSymbol <- paste(unique(genes),collapse=", ")
              returnDat[k,]$varType <- tempVCF$TYPE
              returnDat[k,]$chr <- tempVCF$CHROM
              returnDat[k,]$ref <- ref
              returnDat[k,]$communityStandardTitle <- variant$communityStandardTitle[[1]]

              k <- k + 1

            }

          }

        }

      }

    }


    if(!is.null(variant$genomicAlleles)){

      for(j in c(1:dim(variant$genomicAlleles)[1])){

        returnDat[k,]$`Allele#` <- i
        returnDat[k,]$variantClinGenURL <- tempVCF$URL
        returnDat[k,]$hgvsg <- variant$genomicAlleles$hgvs[[j]][[1]]
        returnDat[k,]$geneSymbol <- genes
        returnDat[k,]$varType <- tempVCF$TYPE
        returnDat[k,]$chr <- tempVCF$CHROM
        returnDat[k,]$ref <- ref
        returnDat[k,]$communityStandardTitle <- variant$communityStandardTitle[[1]]

        k <- k ++ 1

      }

    }

  }

  if(generateAll == TRUE){
    returnDat <- returnDat[!is.na(returnDat$hgvsg),]
  }

  if(dim(returnDat[grepl("[p\\.[a-zA-Z]{3}\\d*[a-zA-Z]{3}",returnDat$communityStandardTitle),])[1] > 0){

    returnDat$aminoCode <- NA
    returnDat$aminoCode_S <- NA

    returnDat[grepl("[p\\.[a-zA-Z]{3}\\d*[a-zA-Z]{3}",returnDat$communityStandardTitle),]$aminoCode <- gsub("\\)","",gsub(".*\\(p\\.","",returnDat[grepl("[p\\.[a-zA-Z]{3}\\d*[a-zA-Z]{3}",returnDat$communityStandardTitle),]$communityStandardTitle))

    returnDat[grepl("[p\\.[a-zA-Z]{3}\\d*[a-zA-Z]{3}",returnDat$communityStandardTitle),]$aminoCode_S <- stringr::str_replace_all(returnDat[grepl("[p\\.[a-zA-Z]{3}\\d*[a-zA-Z]{3}",returnDat$communityStandardTitle),]$aminoCode,
                                                                                                                                  c(
                                                                                                                                    "Ala"="A", "Arg"="R", "Asn"="N", "Asp"="D",
                                                                                                                                    "Cys"="C", "Glu"="E", "Gln"="Q", "Gly"="G",
                                                                                                                                    "His"="H", "Ile"="I", "Leu"="L", "Lys"="K",
                                                                                                                                    "Met"="M", "Phe"="F", "Pro"="P", "Ser"="S",
                                                                                                                                    "Thr"="T", "Trp"="W", "Tyr"="Y", "Val"="V",
                                                                                                                                    "fs" = "_fs_"
                                                                                                                                  )
    )
  }

  return(returnDat)

}

conceptToConcept <- function(concepts, progressBar = TRUE, generateAll = TRUE){

  #Create a handle
  thisHandle <- httr::handle("http://reg.test.genome.network/")

  concepts$info <- ""
  concepts[grepl("NM_|NC_|NP_|NG_|EST_|ENST[0-9]+",concepts$concept_code),]$info <- "Variant"

  concepts_with_URL <- concepts[concepts$info=="Variant",]
  concepts_with_URL$URL <- paste("http://reg.test.genome.network/allele?hgvs=",concepts_with_URL$concept_code,sep="")

  returnDat <- as.data.frame(matrix(ncol = 6))
  colnames(returnDat) <- c("Allele#","variantClinGenURL","hgvsg",
                           "geneSymbol","concept_id","community_standard_title")

  start <- proc.time()[3]

  k <- 1

  for(i in c(1:length(concepts_with_URL$URL))) {

    skip_to_next <- FALSE

    tempVCF <- concepts_with_URL[i,]

    urlTest <- httr::GET(handle = thisHandle,
                         path = gsub(thisHandle$url,"",tempVCF$URL),
                         encoding = "UTF-8", as = "text")

    variant <- RcppSimdJson::fparse(urlTest$content)

    communityStandardTitle <- paste(unique(variant$communityStandardTitle),collapse = "; ")

    if(progressBar == TRUE){
      progress(x = i, max = length(concepts_with_URL$URL))
      eta(x = i, max = length(concepts_with_URL$URL), start)
    }

    genes <- c()

    if(!is.null(variant$transcriptAlleles)){

      for(l in c(1:dim(variant$transcriptAlleles)[1])){

        genes <- c(genes,
                   variant$transcriptAlleles$geneSymbol[l])

      }

    }

    genes <- paste(na.omit(unique(genes)),collapse = ", ")

    if(!is.null(variant$transcriptAlleles)){

      for(l in c(1:dim(variant$transcriptAlleles)[1])){

        if(generateAll == TRUE){
          if("MANE" %in% colnames(variant$transcriptAlleles)){

            if(!is.na(variant$transcriptAlleles$MANE[[l]][[1]])){

              returnDat[k,]$`Allele#` <- i
              returnDat[k,]$variantClinGenURL <- tempVCF$URL
              returnDat[k,]$hgvsg <- variant$transcriptAlleles$MANE[[l]]$nucleotide$RefSeq$hgvs
              returnDat[k,]$geneSymbol <- paste(unique(genes),collapse=", ")
              returnDat[k,]$concept_id <- tempVCF$concept_id
              returnDat[k,]$community_standard_title <- communityStandardTitle

              k <- k + 1

              returnDat[k,]$`Allele#` <- i
              returnDat[k,]$variantClinGenURL <- tempVCF$URL
              returnDat[k,]$hgvsg <- variant$transcriptAlleles$MANE[[l]]$protein$RefSeq$hgvs
              returnDat[k,]$geneSymbol <- paste(unique(genes),collapse=", ")
              returnDat[k,]$concept_id <- tempVCF$concept_id
              returnDat[k,]$community_standard_title <- communityStandardTitle

              k <- k + 1

            }

          }

        }

      }

    }


    if(!is.null(variant$genomicAlleles)){

      for(j in c(1:dim(variant$genomicAlleles)[1])){

        returnDat[k,]$`Allele#` <- i
        returnDat[k,]$variantClinGenURL <- tempVCF$URL
        returnDat[k,]$hgvsg <- variant$genomicAlleles$hgvs[[j]][[1]]
        returnDat[k,]$geneSymbol <- genes
        returnDat[k,]$chr <- tempVCF$CHROM
        returnDat[k,]$concept_id <- tempVCF$concept_id
        returnDat[k,]$community_standard_title <- communityStandardTitle

        k <- k ++ 1

      }

    }

  }

  return(returnDat)

}


#' Adds concept information to an alleles.df dataframe
#' @param vcf.df An alleles.df dataframe returned by
#' @param concepts The ATHENA concept set, derived from loadConcepts (or User input)
#' @param returnAll A paramatere indicating whether or not to return results
#' not in the OMOP Genomic vocab
#' @return A dataframe containing only alleles found in the OMOP Genomic vocab
#' and their associated data
#' @export
addConcepts <- function(vcf.df, concepts, returnAll = FALSE) {

  fullDat <- merge(vcf.df,concepts,
                   by.x = "hgvsg",
                   by.y = "concept_synonym_name",
                   all.x = TRUE) %>%
    dplyr::distinct()

  fullDat <- fullDat[,c(9,10,1,2:8)]

  return(fullDat)

}
