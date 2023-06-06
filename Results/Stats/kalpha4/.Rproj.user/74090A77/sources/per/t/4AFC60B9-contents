library(tidyverse)
library(irr)
responses = read.csv("Coherence_kalpha.csv")
var1_data <- pivot_wider(responses, 
                         id_cols = rater, 
                         names_from = item, 
                         values_from = response)
var1_data <- select(var1_data, -rater)
var1_data <- as.matrix(var1_data)
kripp.alpha(var1_data, method = "nominal")