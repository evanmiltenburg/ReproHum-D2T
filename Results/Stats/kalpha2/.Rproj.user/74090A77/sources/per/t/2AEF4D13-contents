library(tidyverse)
library(irr)
responses = read.csv("Grammaticality_kalpha.csv")
var1_data <- pivot_wider(responses, 
                         id_cols = WorkerId, 
                         names_from = Input.code, 
                         values_from = Answer.best_grammar)
var1_data <- select(var1_data, -WorkerId)
var1_data <- as.matrix(var1_data)
kripp.alpha(var1_data, method = "nominal")