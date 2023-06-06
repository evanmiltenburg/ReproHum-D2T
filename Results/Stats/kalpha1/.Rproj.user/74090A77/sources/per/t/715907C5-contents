library(irr)
library(tidyverse)

responses = read.csv("Coherence_kalpha.csv",header=TRUE,na.strings=c(""))
only_responses = select(responses, -worker_id)
only_responses <- as.matrix(only_responses)
kripp.alpha(only_responses, method = "nominal")

responses = read.csv("Grammaticality_kalpha.csv",header=TRUE,na.strings=c(""))
only_responses = select(responses, -worker_id)
only_responses <- as.matrix(only_responses)
kripp.alpha(only_responses, method = "nominal")

responses = read.csv("Repetition_kalpha.csv",header=TRUE,na.strings=c(""))
only_responses = select(responses, -worker_id)
only_responses <- as.matrix(only_responses)
kripp.alpha(only_responses, method = "nominal")