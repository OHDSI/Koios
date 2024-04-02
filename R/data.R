#' Default Concept Vocabulary
#'
#' A loadable concept vocabulary for OMOP Genomic
#' @format A data frame containing genomic variants
#' \describe{
#'   \item{concept_id}{OMOP Concept ID}
#'   \item{concept_name}{OMOP Concept Name}
#'   \item{concept_synonym_name}{OMOP Concept Synonyms in HGVSG format}
#'   \item{ver}{Specific version of reference genome}
#' }
"concepts"

#' Default Concept Vocabulary
#'
#' An extended loadable concept vocabulary for OMOP Genomic
#' @format A data frame containing genomic variants
#' \describe{
#'   \item{concept_id}{OMOP Concept ID}
#'   \item{concept_name}{OMOP Concept Name}
#'   \item{concept_synonym_name}{OMOP Concept Synonyms in HGVSG format}
#'   \item{concept_class_id}{Specific identity of origin}
#' }
"concepts_ext"
