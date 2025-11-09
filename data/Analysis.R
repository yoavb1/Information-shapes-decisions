#install.packages('CRAN')
library(ggplot2); library(nlme); library(pastecs);
library(reshape); library(grid); library(car); library(tidyverse)
library(scales);  library(dplyr); library(jtools); library(mlogit);
library(lme4);library(sjPlot);library(emmeans);



df <- read.csv("data.csv");

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


######----------PD - block 3----------######
pd_glm <- glm(pd ~ condition + score_improvment,
              data = df[df$block == 3,],
              family = binomial(link = "logit"))
summary(pd_glm)
sjPlot::tab_model(pd_glm)

######----------PD - per block----------######
pd_glm <- glm(pd ~ condition + score_improvment + former_pd,
              data = df[df$block == 4,],
              family = binomial(link = "logit"))
summary(pd_glm)
sjPlot::tab_model(pd_glm)

######----------PD - per block----------######
pd_glm <- glm(pd ~ condition + score_improvment + former_pd,
              data = df[df$block == 5,],
              family = binomial(link = "logit"))
summary(pd_glm)
sjPlot::tab_model(pd_glm)



######----------Effective Sensitivity----------######
sensitivity <-lme(d ~ cost + sensitivity + block + pd + 
                    sensitivity:pd + cost:pd, random = ~1|id,
                  data = df,  method = "ML", na.action = na.exclude)
summary(sensitivity)
sjPlot::tab_model(sensitivity)

emmeans(sensitivity, pairwise ~ block)
emmeans(sensitivity, pairwise ~ sensitivity | pd)


# Sensitivity for PD=1 only
sensitivity <-lme(d ~ cost + sensitivity + block,
                  random = ~1|id,
                  data = block_with_ds,  method = "ML", na.action = na.exclude)
summary(sensitivity)
sjPlot::tab_model(sensitivity)


# Sensitivity for PD=0 only
sensitivity <-lme(d ~ cost + sensitivity + block,
                  random = ~1|id,
                  data = block_without_ds,  method = "ML", na.action = na.exclude)
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
