import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
import biogeme.models as models

pandas = pd.read_table("swissmetro.dat")
database = db.Database("swissmetro",pandas)

# The Pandas data structure is available as database.data. Use all the
# Pandas functions to invesigate the database
#print(database.data.describe())

from headers import *

# Removing some observations can be done directly using pandas.
#remove = (((database.data.PURPOSE != 1) & (database.data.PURPOSE != 3)) | (database.data.CHOICE == 0))
#database.data.drop(database.data[remove].index,inplace=True)

# Here we use the "biogeme" way for backward compatibility
exclude = (( PURPOSE != 1 ) * (  PURPOSE   !=  3  ) +  ( CHOICE == 0 )) > 0
database.remove(exclude)

ASC_TRAIN = Beta('ASC_TRAIN', -0.701188,None,None,0)
B_TIME = Beta('B_TIME', -1.27786,None,None,0)
B_COST = Beta('B_COST', -1.08379,None,None,0)
ASC_SM = Beta('ASC_SM', 0,None,None,0)
ASC_CAR = Beta('ASC_CAR', -0.154633,None,None,0)

SM_COST =  SM_CO   * (  GA   ==  0  ) 
TRAIN_COST =  TRAIN_CO   * (  GA   ==  0  )

TRAIN_TT_SCALED = TRAIN_TT  / 100.0
TRAIN_COST_SCALED =  TRAIN_COST / 100
SM_TT_SCALED = SM_TT / 100.0
SM_COST_SCALED = SM_COST / 100.0
CAR_TT_SCALED = CAR_TT / 100.0
CAR_CO_SCALED = CAR_CO / 100.0

V1 = ASC_TRAIN + \
     B_TIME * TRAIN_TT_SCALED + \
     B_COST * TRAIN_COST_SCALED
V2 = ASC_SM + \
     B_TIME * SM_TT_SCALED + \
     B_COST * SM_COST_SCALED
V3 = ASC_CAR + \
     B_TIME * CAR_TT_SCALED + \
     B_COST * CAR_CO_SCALED

# Associate utility functions with the numbering of alternatives
V = {1: V1,
     2: V2,
     3: V3}


# Associate the availability conditions with the alternatives
CAR_AV_SP =  DefineVariable('CAR_AV_SP',CAR_AV  * (  SP   !=  0  ),database)
TRAIN_AV_SP =  DefineVariable('TRAIN_AV_SP',TRAIN_AV  * (  SP   !=  0  ),database)

av = {1: TRAIN_AV_SP,
      2: SM_AV,
      3: CAR_AV_SP}

# The choice model is a logit, with availability conditions
prob1 = models.logit(V,av,1)
prob2 = models.logit(V,av,2)
prob3 = models.logit(V,av,3)

# Elasticities can be computed. We illustrate below two
# formulas. Check in the output file that they produce the same
# result.

# First, the general definition of elasticities. This illustrates the
# use of the Derive expression, and can be used with any model,
# however complicated it is. Note the quotes in the Derive opertor.

genelas1 = Derive(prob1,'TRAIN_TT') * TRAIN_TT / prob1
genelas2 = Derive(prob2,'SM_TT') * SM_TT / prob2
genelas3 = Derive(prob3,'CAR_TT') * CAR_TT / prob3

# Second, the elasticity of logit models. See Ben-Akiva and Lerman for
# the formula

logitelas1 = TRAIN_AV_SP * (1.0 - prob1) * TRAIN_TT_SCALED * B_TIME
logitelas2 = SM_AV * (1.0 - prob2) * SM_TT_SCALED * B_TIME
logitelas3 = CAR_AV_SP * (1.0 - prob3) * CAR_TT_SCALED * B_TIME

simulate = {'Prob. train': prob1,
            'Prob. Swissmetro': prob2,
            'Prob. car':prob3,
            'logit elas. 1':logitelas1,
            'generic elas. 1':genelas1,
            'logit elas. 2':logitelas2,
            'generic elas. 2':genelas2,
            'logit elas. 3':logitelas3,
            'generic elas. 3':genelas3}

biogeme  = bio.BIOGEME(database,simulate)
biogeme.modelName = "01logit_simul"
results = biogeme.simulate()
print("Results=",results.describe())


