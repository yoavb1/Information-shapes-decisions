#install.packages('CRAN')
library(ggplot2); library(nlme); library(pastecs);
library(reshape); library(grid); library(car); library(tidyverse)
library(scales);  library(dplyr); library(jtools); library(mlogit);
library(lme4);library(sjPlot);library(emmeans);



df <- read.csv("data.csv");
df$condition_fact <- as.factor(df$condition)
df$block_fact <- as.factor(df$block)
df$pd_fact <- as.factor(df$pd)

block_with_ds <-df[df$pd == 1,]
block_without_ds <-df[df$pd == 0,]

######----------PD----------######
# GLMM with Condition, Block and Condition X Block
pd <- glmer(pd ~ condition + block + condition:block + (1 | id),
            data = df,
            family = binomial(link = "logit"),
            control = glmerControl(optimizer = "bobyqa"), nAGQ = 1)
summary(pd)
sjPlot::tab_model(pd)


######----------Effective Sensitivity----------######
sensitivity <-lme(d ~ cost + sensitivity + block + pd + 
                    sensitivity:pd + cost:pd, random = ~1|id,
                  data = df,  method = "ML", na.action = na.exclude)
summary(sensitivity)
sjPlot::tab_model(sensitivity)


######----------Decision Time----------######
decision_time <-lme(time ~ cost + sensitivity + block + pd + 
                      sensitivity:pd + cost:pd,
                    random = ~1|id,
                    data = df,  method = "ML", na.action = na.exclude)
summary(decision_time)
sjPlot::tab_model(decision_time)


######----------Trust----------######
#-Compliance-#
compliance <-lme(compliance ~ cost + sensitivity + block + pd + sensitivity:pd + cost:pd,
                 random = ~1|id,
                 data = df,  method = "ML", na.action = na.exclude)
summary(compliance)
sjPlot::tab_model(compliance)

#-Reliance-#
reliance <-lme(reliance ~ cost + sensitivity + block + pd + sensitivity:pd + cost:pd,
                 random = ~1|id,
                 data = df,  method = "ML", na.action = na.exclude)
summary(reliance)
sjPlot::tab_model(reliance)
