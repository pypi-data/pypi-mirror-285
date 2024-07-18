"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SOLUTION OF EXAMPLE DISCRETE CHOICE MODELS 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# NOTE:
# varnames:     All explanatory variables that have been defined
# isvars:       Individual specific variables These variables do not vary across alternatives
# asvars:       Alternative specific variables These variables vary across alternatives.
# alts:         Alternatives for each choice. E.g., Choice = transport mode, Alternatives = {car, bus, train}
# base_alts:    The base (a.k.a., reference) alternative
# transvars:    Variables that have transformations applied to them
# randvars:     Ramdom variables
# corvars:      Correlated variables
# bcvars:       Box Cox transformed variables

''' ---------------------------------------------------------- '''
''' LIBRARIES                                                  '''
''' ---------------------------------------------------------- '''

from harmony import *
from siman import *
from threshold import *
from latent_class_mixed_model import LatentClassMixedModel
from latent_class_model import LatentClassModel
from mixed_logit import MixedLogit
from multinomial_logit import MultinomialLogit
import pandas as pd
from scipy import stats
import time

'''' ---------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def run_multinomial_logit():
    # {
    df = pd.read_csv("Swissmetro_final.csv")
    varnames = ['COST', 'TIME', 'HEADWAY', 'LUGGAGE_CAR', 'SEATS', 'AGE_TRAIN']
    model = MultinomialLogit()
    model.setup(X=df[varnames], y=df['CHOICE'], varnames=varnames,
                fit_intercept=True, alts=df['alt'], ids=df['custom_id'],
                avail=df['AV'], base_alt='SM', gtol=1e-04)
    model.fit()
    model.get_loglik_null()
    model.summarise()


# }

'''' ---------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def run_multinomial_logit_box():
    # {
    df = pd.read_csv("artificial_1b_multi_nonlinear.csv")

    varnames = ['added_fixed1', 'added_fixed2', 'added_fixed3', 'added_fixed4', 'added_fixed5', 'added_fixed6',
                'added_fixed7', 'added_fixed8', 'added_fixed9', 'added_fixed10', 'added_fixed11', 'added_fixed12',
                'added_fixed13', 'added_fixed14', 'added_fixed15', 'added_fixed16', 'added_fixed17', 'added_fixed18']

    model = MultinomialLogit()
    X = df[varnames].values
    y = df['choice'].values
    isvars = []
    transvars = ['added_fixed1', 'added_fixed2']
    model.setup(X, y, ids=df['id'], varnames=varnames, isvars=isvars, transvars=transvars, alts=df['alt'])
    model.fit()
    model.get_loglik_null()
    model.summarise()


# }


''' ----------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def run_mixed_logit():
    # {

    df = pd.read_csv("artificial_1h_mixed_corr_trans.csv")

    varnames = ['added_fixed1', 'added_fixed2', 'added_fixed3',
                'added_fixed4', 'added_fixed5', 'added_fixed6',
                'nonsig1', 'nonsig2', 'nonsig3', 'nonsig4', 'nonsig5',
                'added_random1', 'added_random2', 'added_random3',
                'added_random4', 'added_random5', 'added_random6', 'added_random7']

    isvars = []
    transvars = []  #['added_random4', 'added_random5']
    randvars = {'added_random1': 'n', 'added_random2': 'n', 'added_random3': 'n',
                'added_random4': 'n', 'added_random5': 'n', 'added_random6': 'u', 'added_random7': 't'}

    correlation = ['added_random1', 'added_random2', 'added_random3']

    model = MixedLogit()
    model.setup(X=df[varnames].values, y=df['choice'].values, ids=df['choice_id'].values,
                panels=df['ind_id'].values, varnames=varnames,
                isvars=isvars, transvars=transvars, correlation=correlation,
                randvars=randvars, fit_intercept=False, alts=df['alt'],
                n_draws=200, verbose=2)

    model.fit()
    model.summarise()


# }

''' ----------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def run_mixed_logit_box():
    # {
    df = pd.read_csv("artificial_1h_mixed_corr_trans.csv")
    df['bc_added_random4'] = stats.boxcox(df['added_random4'], 0.01)
    df['bc_added_random5'] = stats.boxcox(df['added_random5'], 0.0)

    varnames = ['added_fixed1', 'added_fixed2', 'added_fixed3', 'added_fixed4', 'added_fixed5', 'added_fixed6',
                #'nonsig1', 'nonsig2', 'nonsig3', 'nonsig4', 'nonsig5',
                'added_random1', 'added_random2', 'added_random3', 'added_random4', 'added_random5', 'added_random6',
                'added_random7']

    isvars = []
    transvars = ['added_random4', 'added_random5']
    randvars = {'added_random1': 'n', 'added_random2': 'n', 'added_random3': 'n',
                'added_random4': 'n', 'added_random5': 'n', 'added_random6': 'u', 'added_random7': 't'}

    correlation = ['added_random1', 'added_random2', 'added_random3']

    model = MixedLogit()
    model.setup(X=df[varnames].values, y=df['choice'].values, ids=df['choice_id'].values,
                panels=df['ind_id'].values, varnames=varnames,
                isvars=isvars, transvars=transvars, correlation=correlation,
                randvars=randvars, fit_intercept=False, alts=df['alt'],
                n_draws=200, verbose=2)

    model.fit()
    model.get_loglik_null()
    model.summarise()


# }

''' ----------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def run_latent_class():
    # {
    df = pd.read_csv("artificial_latent_new.csv")
    varnames = ['price', 'time', 'conven', 'comfort', 'meals', 'petfr', 'emipp', 'income', 'age',
                #'nonsig1', 'nonsig2', 'nonsig3', 'nonsig4', 'nonsig5',
                #'nonsig_isvar1', 'nonsig_isvar2'
                ]
    X = df[varnames].values
    y = df['choice'].values
    member_params_spec = np.array([['income', 'age']], dtype='object')
    class_params_spec = np.array([['price', 'time', 'conven', 'comfort'],
                                  ['price', 'time', 'meals', 'petfr', 'emipp']], dtype='object')

    model = LatentClassModel()  # Derived from MultinomialLogit
    model.setup(X, y, varnames=varnames, ids=df['id'], num_classes=2,  #random_state = 0,
                class_params_spec=class_params_spec, member_params_spec=member_params_spec,
                alts=[1, 2, 3], ftol_lccm=1e-3, gtol=1e-3, verbose=2)

    model.fit()
    model.summarise()


# }

''' ----------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def run_latent_class_mixed():
    # {

    df = pd.read_csv("synth_latent_mixed_3classes.csv")

    varnames = ['added_fixed1', 'added_fixed2', 'added_random1', 'added_random2', 'income', 'age']
    X = df[varnames].values
    y = df['choice'].values

    member_params_spec = np.array([['income', 'age'], ['income', 'age']], dtype='object')
    class_params_spec = np.array([['added_fixed1', 'added_fixed2', 'added_random1', 'added_random2'],
                                  ['added_fixed1', 'added_fixed2', 'added_random1', 'added_random2'],
                                  ['added_fixed1', 'added_fixed2', 'added_random1', 'added_random2']],
                                 dtype='object')

    randvars = {'added_random1': 'n', 'added_random2': 'n'}
    init_class_thetas = np.array([0.1, -0.03, -0.1, 0.02])

    init_class_betas = [
        np.array([-1, 2.5, 1.242992317, 2.040125077, 1.02, 0.90]),
        np.array([1.5, -1, 0.74, 0.81, 1.47, 1.36]),
        np.array([-2, 1, 1.20, 1.65, 1.27, 1.07])
    ]

    model = LatentClassMixedModel()
    model.setup(X, y, panels=df['ind_id'], n_draws=300, varnames=varnames, num_classes=3,
                class_params_spec=class_params_spec, member_params_spec=member_params_spec,
                gtol=1e-4, init_class_thetas=init_class_thetas, init_class_betas=init_class_betas,
                randvars=randvars, alts=[1, 2, 3])
    model.fit()
    model.summarise()


# }


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# META HEURISTIC OPTIMISATION APPROACH
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def call_meta_h(parameters, init_sol=None, hm=False):
    # {
    if hm:
        # {
        solver = HarmonySearch(parameters)
        solver.max_mem = 25
        solver.maxiter = 500
        solver.run()
    # }
    else:
        # {
        #ctrl = (10, 20, 10) # i.e., threshold, max_steps, max_iter
        #ctrl = (10, 10, 1)  # i.e., threshold, max_steps, max_iter
        #solver = TA(parameters, init_sol, ctrl)
        #solver.run()
        #solver.close_files()

        ctrl = (10, 0.001, 10, 10)  # i.e. (tI, tF, max_temp_steps, max_iter)
        #ctrl = (1000, 0.001, 20, 20)  # i.e. (tI,tF,max_temp_steps,max_iter)
        solver = SA(parameters, init_sol, ctrl)
        solver.run()
        solver.close_files()

        # OR
        #parsa = PARSA(parameters, ctrl, nthrds=4)
        #parsa.run(with_latent=with_latent)

        # Use max_iter = 10 when using PARCOPSA!

        # OR:
        '''
        parcopsa = PARCOPSA(parameters, ctrl, nthrds=8)
        tI = [1, 10, 100, 1000, np.random.randint(1, 10000), np.random.randint(1, 10000),
              np.random.randint(1, 10000), np.random.randint(1, 10000) ]
        for i in range(8):
            parcopsa.solvers[i].revise_tI(tI[i])

        parcopsa.run(with_latent=with_latent)
        '''

    # }


# }


''' ----------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def optimise_synth_latent():
    # {
    df = pd.read_csv("synth_latent_mixed_3classes.csv")
    df_test = None
    varnames = ['added_fixed1', 'added_fixed2', 'added_random1', 'added_random2', 'income', 'age']
    asvarnames = varnames
    isvarnames = []

    choice_id = df['choice_id']
    ind_id = df['ind_id']
    choices = df['choice']  # the df column name containing the choice variable
    alt_var = df['alt']  # the df column name containing the alternative variable
    base_alt = None  # Reference alternative
    distr = ['n', 'u', 't']  # List of random distributions to select from
    choice_set = ['1', '2', '3']
    criterions = [['loglik', 1]]
    #criterions = [['loglik',1], ['mae',-1]]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    parameters = Parameters(criterions=criterions, df=df, distr=distr, df_test=df_test, choice_set=choice_set,
                            alt_var=alt_var, varnames=varnames, isvarnames=isvarnames, asvarnames=asvarnames,
                            choices=choices,
                            choice_id=choice_id, ind_id=ind_id, latent_class=True, allow_random=True, base_alt=base_alt,
                            allow_bcvars=False, n_draws=200)

    init_sol = None
    hm = False  # True
    with_latent = True  # False
    call_meta_h(parameters, init_sol=init_sol, hm=hm)


# }

''' ----------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def optimise_electricity():
    # {
    """
    Description of electricity data: the choice of electricity supplier data collected in California by the
    Electric Power Research Institute (Goett, 1998). A stated-preference survey was conducted on 361 residential
    customers to study their preferences regarding electricity plans. The panel dataset includes a total of 4,308
    observations wherein each customer faced up to 12 choice scenarios with four different plans to choose from.
    Each choice scenario was designed using six attributes, including a fixed price (pf) for an electricity plan
    (7 or 9 cents/kWh), contract length (cl) during which a penalty is imposed if the customer chooses to
    switch plans (no contract, 1 year or 5 years), a dummy variable indicating if the supplier was well-known (wk),
    time of the day rates (tod) (11 cents/kWh from 8AM to 8PM and 5 cents/kWh from 8PM to 8AM), seasonal rates (seas)
    (10 cents/kWh for summer, 8 cents/kWh for winter and 6 cents/kWh in spring and fall) and, a dummy variable
     indicating if the supplier was a local (loc).
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # LOAD THE PROBLEM DATA
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    df = pd.read_csv("electricity.csv")
    df_test = None

    varnames = ['pf', 'cl', 'loc', 'wk', 'tod', 'seas']  # all explanatory variables to be included in the model
    asvarnames = varnames  # alternative-specific variables in varnames
    isvarnames = []  # individual-specific variables in varnames

    choice_id = df['chid']
    ind_id = df['id']
    choices = df['choice']  # the df column name containing the choice variable
    alt_var = df['alt']  # the df column name containing the alternative variable
    base_alt = None  # Reference alternative
    distr = ['n', 'u', 't']  # List of random distributions to select from
    choice_set = ['1', '2', '3', '4']

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # CHOOSE SINGLE OBJECTIVE OR MULTI-OBJECTIVE
    # SET KPI AND SIGN (I.E. TUPLE) AND PLACE IN LIST
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #criterions = [['mae',-1]]
    criterions = [['loglik', 1]]
    #criterions = [['bic',-1]]
    #criterions = [['aic',-1]]

    #criterions = [['loglik',1], ['mae',-1]]
    #criterions = [['bic',-1], ['mae',-1]]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # DEFINE PARAMETERS FOR THE SEARCH
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    latent_class = False  #False
    parameters = Parameters(criterions=criterions, df=df, distr=distr, df_test=df_test, choice_set=choice_set,
                            alt_var=alt_var, varnames=varnames, isvarnames=isvarnames, asvarnames=asvarnames,
                            choices=choices,
                            choice_id=choice_id, ind_id=ind_id, latent_class=latent_class, allow_random=True,
                            base_alt=base_alt,
                            allow_bcvars=False, n_draws=200)

    # Normally: allow_bcvars=True

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # DEFINE THE STARTING SOLUTION - NEW FEATURE WORTH CONSIDERING
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    init_sol = None

    # CAVEAT: THE USER MUST KNOW WHAT THEY ARE DOING. THEY MUST KNOW THE RULES

    '''nb_crit = len(criterions)
    init_sol = Solution(nb_crit)
    init_sol.set_asvar(['cl','wk','tod'])
    init_sol.set_randvar(['cl','tod','wk'], ['t','t','u'])
    .
    .
    .
    '''
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # RUN THE SEARCH
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    hm = False  #True
    call_meta_h(parameters, init_sol=init_sol, hm=hm)


# }

''' ----------------------------------------------------------- '''
''' SCRIPT                                                      '''
''' ----------------------------------------------------------- '''


def optimise_new_syn():
    # {

    df = pd.read_csv("New_Syn_MOOF_TRAIN_seed6.csv")
    df_test = pd.read_csv("New_Syn_MOOF_TEST_seed6.csv")

    # Manually transforming the variable to avoid estimation of lambda for better convergence
    df['bc_added_random4'] = stats.boxcox(df['added_random4'], 0.01)

    # Manually transforming the variable to avoid estimation of lambda for better convergence
    df['bc_added_random5'] = stats.boxcox(df['added_random5'], 0.05)

    # Manually transforming the variable to avoid estimation of lambda for better convergence
    df_test['bc_added_random4'] = stats.boxcox(df_test['added_random4'], 0.01)

    # Manually transforming the variable to avoid estimation of lambda for better convergence
    df_test['bc_added_random5'] = stats.boxcox(df_test['added_random5'], 0.05)

    choice_id = df['choice_id']
    test_choice_id = df_test['choice_id']

    ind_id = df['ind_id']
    test_ind_id = df_test['ind_id']

    alt_var = df['alt']
    test_alt_var = df_test['alt']

    distr = ['n', 'u', 't']
    choice_set = ['1', '2', '3']

    asvarnames = ['added_fixed1', 'added_fixed2', 'added_fixed3', 'added_fixed4', 'added_fixed5',
                  'added_fixed6', 'nonsig1', 'nonsig2', 'nonsig3', 'nonsig4', 'nonsig5', 'added_random1',
                  'added_random2', 'added_random3', 'added_random4',
                  'added_random5', 'added_random6', 'added_random7']

    isvarnames = []
    varnames = asvarnames + isvarnames
    # UNUSED CODE: trans_asvars = []
    choices = df['choice']
    test_choices = df_test['choice']  # CHANGED the df column name containing the choice variable

    criterions = [['loglik', 1]]
    # criterions = [['loglik', 1], ['mae', -1]]

    parameters = Parameters(criterions=criterions, df=df, distr=distr, df_test=df_test, choice_set=choice_set,
                            alt_var=alt_var, test_alt_var=test_alt_var, varnames=varnames, isvarnames=isvarnames,
                            asvarnames=asvarnames, choices=choices, test_choices=test_choices, choice_id=choice_id,
                            test_choice_id=test_choice_id, ind_id=ind_id, test_ind_id=test_ind_id, latent_class=False,
                            allow_random=True, base_alt=None, allow_bcvars=False, n_draws=200,

                            # gtol=1e-2, # intercept_opts=intercept_opts,
                            # avail_latent=avail_latent,# p_val=0.01,
                            # ="Synth_SOOF_seed6"
                            )

    hm = False  #True
    call_meta_h(parameters, hm)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # FIT MIXED LOGIT
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    '''varnames = ['added_fixed1', 'added_fixed2', 'added_fixed3', 'added_fixed4', 'added_fixed5', 'added_fixed6',
                'added_random1', 'added_random2', 'added_random3',
                'bc_added_random4', 'bc_added_random5', 'added_random6', 'added_random7']

    X = df[varnames].values
    y = df['choice'].values
    av = None
    test_av = None
    weight_var = None
    test_weight_var = None
    isvars = []
    transvars = []  # ['added_random4', 'added_random5']
    randvars = {'added_random1': 'n', 'added_random2': 'n', 'added_random3': 'n',
                'bc_added_random4': 'n', 'bc_added_random5': 'n', 'added_random6': 'u', 'added_random7': 't'}

    correlation = ['added_random1', 'added_random2', 'added_random3']
    model = MixedLogit()
    model.setup(X,y, ids=df['choice_id'].values, panels=df['ind_id'].values, varnames=varnames,
        isvars=isvars,  n_draws=200,verbose=2,correlation=correlation, transvars=transvars, randvars=randvars, alts=df['alt'] )
        #   gtol=2e-6, ftol=1e-8,method="L-BFGS-B",
    model.fit()
    model.summarise()

    choice_set = [1,2,3]
    def_vals = model.coeff_est
    X_test = df_test[varnames].values
    y_test = df_test['choice'].values


    # Calculating MAE
    # Choice frequecy obtained from estimated model applied on testing sample
    predicted_probabilities_val = model.pred_prob * 100
    obs_freq = model.obs_prob * 100
    MAE = round((1 / len(choice_set)) * (np.sum(abs(predicted_probabilities_val - obs_freq))), 2)
    MAPE = round((1 / len(choice_set)) * (np.sum(abs((predicted_probabilities_val - obs_freq) / obs_freq))))
    print("MAE = ", MAE,"; MAPE = ", MAPE)'''


# }


def test_mixed_vs_multinomial_setup():

    model = MultinomialLogit()
    df = pd.read_csv("electricity.csv")

    varnames = ['pf', 'cl', 'loc', 'wk', 'tod', 'seas']
    isvars = []
    X = df[varnames].values
    y = df['choice'].values

    transvars = []

    model.setup(X, y,
                ids=df['chid'].values,
                varnames=varnames,
                isvars=isvars,
                # transvars=transvars,
                fit_intercept=True,
                alts=df['alt'],
                verbose=2)
    model.fit()
    model.get_loglik_null()
    model.summarise()
    print('does this work, let us see')

    model = MixedLogit()
    df = pd.read_csv("electricity.csv")

    varnames = ['pf', 'cl', 'loc', 'wk', 'tod', 'seas']
    isvars = []
    X = df[varnames].values
    y = df['choice'].values

    transvars = []
    randvars = {'pf': 'n', 'cl': 'n', 'loc': 'n',
                'wk': 'n', 'tod': 'n',
                'seas': 'n'}

    correlation = ['pf', 'wk']

    model.setup(X, y,
                ids=df['chid'].values,
                panels=df['id'].values,
                varnames=varnames,
                isvars=isvars,
                # transvars=transvars,
                # correlation=True,
                randvars=randvars,
                fit_intercept=True,
                alts=df['alt'],
                n_draws=200,
                verbose=2,
                mnl_init=True
                # (Setting this to False also raises an error - not sure of both these errors are related)
                )
    model.fit()
    model.get_loglik_null()
    model.summarise()


def synth_3():
    print('testing synthetic experiment for the mixed latent class random parameters...')
    df = pd.read_csv("synth_latent_mixed_3classes.csv")
    model = LatentClassMixedModel()
    varnames = ['added_fixed1', 'added_fixed2', 'nonsig1', 'nonsig2', 'nonsig3',
                'added_random1', 'added_random2',
                'income', 'age', 'gender'
                #   'nonsig1', 'nonsig2', 'nonsig3',
                #   'nonsig4', 'nonsig5', 'nonsig_isvar1', 'nonsig_isvar2'
                ]

    X = df[varnames].values
    y = df['choice'].values
    member_params_spec = np.array([['income', 'gender'],
                                   ['income', 'age']], dtype='object')
    class_params_spec = np.array([['added_fixed1', 'added_fixed2'],
                                  ['added_fixed1', 'added_random1'],
                                  ['added_fixed2', 'added_random2']],
                                 dtype='object')

    randvars = {'added_random1': 'n', 'added_random2': 'n'}
    init_class_thetas = np.array([0.1, -0.03, -0.1, 0.02])
    init_class_betas = [np.array([-1, 2.5, 1.242992317, 2.040125077, 1.02, 0.90]),
                        np.array([1.5, -1, 0.74, 0.81, 1.47, 1.36]),
                        np.array([-2, 1, 1.20, 1.65, 1.27, 1.07])]

    model.setup(X,
                y,
                panels=df['ind_id'],
                n_draws=100,
                varnames=varnames,
                num_classes=3,
                class_params_spec=class_params_spec,
                member_params_spec=member_params_spec,
                #   ftol=1e-3,
                gtol=1e-5,
                ftol_lccmm=1e-4,
                # init_class_thetas=init_class_thetas,
                # init_class_betas=init_class_betas,
                randvars=randvars,
                alts=[1, 2, 3],
                #  verbose=2
                )
    model.reassign_penalty(1)
    model.fit()
    model.summarise()



'''' ---------------------------------------------------------- '''
''' MAIN PROGRAM                                                '''
''' ----------------------------------------------------------- '''

if __name__ == '__main__':
    # {
    #np.random.seed(int(time.time()))
    #np.random.seed(100) # THIS SEED CAUSES THE EXCEPTION.

    # Exception when seed = 1000, 3
    np.random.seed(1000)  # THIS SEED CAUSES THE EXCEPTION.

    #run_multinomial_logit()        # Runs 0.1-0.2s
    #run_multinomial_logit_box()    # Runs 1s
    #run_mixed_logit()              # Runs in about 12s +- 3s
    #run_mixed_logit_box()          # Runs in about 20s
    #run_latent_class()             # Runs in about 6s +- 2s
    #run_latent_class_mixed()       # Runs in about 160s + 30s
    #test_mixed_vs_multinomial_setup()
    #optimise()
    synth_3()

    success = 0
    fail = 0
    while fail < 1000:
        try:
            optimise_electricity()
            success += 1
        except Exception as e:
            print(e)
            fail += 1
        np.random.seed(fail+success)
    print(f'percentage of success {fail/(fail+success)}')

    #optimise_synth_latent()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # DEBUGGING PARETO FRONT GENERATION
    '''soln = [{'obj1': 45, 'obj2':2}, {'obj1': 64, 'obj2':8}, {'obj1': 21, 'obj2':2},
        {'obj1': 88, 'obj2':7}, {'obj1': 13, 'obj2':5}, {'obj1': 36, 'obj2':5}, {'obj1': 83, 'obj2':1},
        {'obj1': 39, 'obj2':10}, {'obj1': 45, 'obj2':10}, {'obj1': 60, 'obj2':9}]
    fronts = rank_solutions(soln, 'obj1', 'obj2')
    print("Fronts=",fronts)
    crowd = {}
    key =  'obj2'
    max_val = max(soln[i][key] for i in range(len(soln)))  # Compute max value of objective 'key'
    min_val = min(soln[i][key] for i in range(len(soln)))  # Compute min value of objective 'key'
    for front in fronts.values():
        compute_crowding_dist_front(front, soln, crowd, key, max_val, min_val)
    #print(crowd)

    sorted = sort_solutions(fronts, crowd, soln)
    print(sorted)
    '''
# }


# ISSUES

# 1. EXCEPTION TRIGGERED IN "evaluate_MNL" AND "evaluate_MXL" after a solution is generate from scratch
# 2. BCVAR DELETION AFTER BCVAR ADDING - EXCEPTION TRIGGERED
# 3. pvalues_member undefined

""" RULES:
    A variable cannot be an isvar and asvar simultaneously.
    An isvar or asvar can be a random variable – I don’t understand this?
    An isvar cannot be a randvar
    A bcvar cannot be a corvar at the same time
    corvar should be a list of at least 2 randvars
    num_classes (Q) should be > 1, for estimating latent class models
    length of member_params_spec should be == Q-1
    length of class_params_spec should be == Q
    coefficients for member_params_spec cannot be in randvars
"""
