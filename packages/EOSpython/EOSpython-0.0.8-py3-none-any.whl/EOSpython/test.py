### Example script as test

# Without package installed (only having run the functions - otherwise call the functions in the readme!)
sat_TLEs = [38755, 40053]

               #w
criteria_w =  [0.05,      #area
               0.1,       #off-nadir angle
               0.1,       #sun elevation
               0.2,       #cloud coverage 
               0.2,       #priority
               0.1,       #price
               0.2,       #age
               0.05]      #uncertainty

       #q,  p,   v
qpv = [[0,  30,  1000],        #area
       [0,  2,   40],          #off-nadir angle
       [0,  10,  40],          #sun elevation
       [0,  2,   15],          #cloud coverage 
       [0,  1,   4],           #priority
       [0,  100, 20000],       #price
       [0,  4,   10],          #age
       [0,  0.5,   1]]         #uncertainty


#create db
database, map_file = customer_db(number_of_requests_0 = 250)
print(database)
print(database.info())
#Note, if map_generation is True, the database can be inspected via the interactive all_requests.html file!

#create scenario
x_data = scenario(customer_database = database, m = map_file, seconds_gran=10, NORAD_ids=sat_TLEs, weather_real = False)

#generate a solution
x_res1 = solve(x_data, scoring_method=2, solution_method = "DAG", criteria_weights_l = criteria_w, threshold_parameters_l= qpv)
#Note, the solution method can be either: DAG, GLPK, gurobi, PuLP  - make sure to have the right capitulazation!

visualize(x_data, x_res1, 'EOS_example')

df = evaluate(x_data, x_res1)

print(df.solution)
print(df.scenario)



