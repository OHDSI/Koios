#' Process a cBioPortal object containing fusion data and add relevant concept IDs
#' @param fusions_data Input cBioPortal data object
#' @param concepts_fusion A dataframe object containing OMOP Genomic fusions
#' @return A fusions_data object with added concept_ids and concept_names
#' @export
generateFusions_cBioPortal <- function(fusions_data,concepts_fusion){

  fusions_data <- fusions_data[!grepl("intragenic",fusions_data$Event_Info),]
  fusions_data$Event_Info <- gsub(" fusion","",gsub("-","::",fusions_data$Event_Info))
  fusions_data <- merge(fusions_data,concepts_fusion,by.x="Event_Info",by.y="concept_synonym_name",all.x=TRUE)

  return(fusions_data)

}
