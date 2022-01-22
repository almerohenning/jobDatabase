# function prompts the user for job details and creates a dictionary with the job attributes
# @param dbcursor: dbcursor
# @param company_id: company id that enters the job as an int
# returns the preferences as a dictionary ["title", "degree", "city", "state", "field", "company", "salary"]

from mysql import connector

def defineJob(dbcursor, company_id):
	job_title = input("\nPlease enter the job title for the job: ")
	degree_input = input("\nPlease enter the degree necessary for the job? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
	
	while degree_input != "0" and degree_input != "1" and degree_input != "2" and degree_input != "3" and degree_input != "4":
		degree_input = input("\nPlease enter a valid degree. (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
		
	city_input = input("Enter the city: ")	
	state_input = input("Enter the state(s): ")
	field_input = input("Enter your preferred field(s). (click enter to see options): ")
	if field_input == "":
		printFieldOptions()
		field_input = input("\nEnter your preferred field(s): ")
	salary_input = input("Enter your minimum salary. (click enter to skip): ")
	preferences = {
		"title": job_title,
		"degree": degree_input,
		"city" : city_input,
		"state": state_input,
		"field": field_input,
		"company": company_id,
		"salary": salary_input
	}
	return preferences
	
def printFieldOptions():
	print("\n\n1016 | Insurance\n1019 | Business Services\n1022 | Manufacturing\n1025 | Information Technology\n1028 | Biotech & Pharmaceuticals\n1031 | Retail\n1034 | Oil, Gas, Energy & Utilities")
	print("1037 | Government\n1040 | Health Care\n1043 | Finance\n1046 | Aerospace & Defense\n1049 | Transportation & Logistics\n1052 | Media\n1055 | Telecommunications\n1058 | Real Estate")
	print("1061 | Travel & Tourism\n1064 | Agriculture & Forestry\n1067 | Education\n1070 | Accounting & Legal\n1073 | Non-Profit\n1076 | Construction, Repair & Maintenance\n1079 | Consumer Services\n")
	  
# function prompts the user for job preferences and returns a dictionary with set preferences 
# 
def preferenceSetting(dbcursor):
	degree_input = input("\nWhat is your highest degree earned? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
	while degree_input != "0" and degree_input != "1" and degree_input != "2" and degree_input != "3" and degree_input != "4" and degree_input != "":
		degree_input = input("\nPlease enter a valid degree. (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
	city_input = input("Enter your preferred city. (click enter to skip): ")
	
	inTable = CheckIfInTable(dbcursor, "city_name", city_input, "city_name", "location", identifier_is_string = True)
	
	city_inputCheck = city_input.split(" ")
	
	if len(city_inputCheck) > 1:
		while (not city_inputCheck[0].isalpha() or city_inputCheck[1].isalpha() or inTable == 0) and city_input != "":
			city_input = input("This city does not have any listings, enter another city (click enter to skip city): ")
			inTable = CheckIfInTable(dbcursor,"city_name", city_input, "city_name", "location", identifier_is_string = True)
	else:
		
		while (not city_input.isalpha() or inTable == 0) and city_input != "":
			if city_input == "":
				break
			city_input = input("This city does not have any listings, enter another city (click enter to skip city): ")
			inTable = CheckIfInTable(dbcursor,"city_name", city_input, "city_name", "location", identifier_is_string = True)
			
	state_input = input("Enter your preferred state(s). (click enter to skip): ")
	while city_input != "" and state_input =="":
		print("\n  ---Error, Please enter a State for your previous city ---\n")
		state_input = input("Enter your preferred state(s). (click enter to skip): ")
	field_input = input("Enter your preferred field(s). (click enter to skip or enter 'option' to see field options)): ")
	if field_input == "option":
		printFieldOptions()
		field_input = input("Enter your preferred field(s). (click enter to skip or enter 'option' to see field options)): ")
	company_input = input("Enter your preferred company. (click enter to skip): ") 
	
	while CheckIfInTable(dbcursor,"company_name", company_input, "company_name", "company", identifier_is_string = True) == 0 and company_input != "":
		company_input = input("The company does not have any job listings, try again: ")
	
	if company_input != "":
		companyInID = fetch_company_id(dbcursor, str(company_input))
	else:
		companyInID = ""
	
	salary_input = input("Enter your minimum salary, in thousands. (click enter to skip): ")
	preferences = {
		"degree": degree_input,
		"city" : city_input,
		"state": state_input,
		"field": field_input,
		"company": companyInID,
		"salary": salary_input
	}
	
	return preferences

	  
def SearchJobs(dbcursor, preferences):
	command = "SELECT job_id, job_title, city_name, state_name, company_name, salary from "
	command = command + "((jobs NATURAL JOIN location) NATURAL JOIN company) "
	counter = 0
	
	if preferences["degree"]:	
		command = command + " WHERE education_level <= " + str(preferences["degree"])
		counter = counter + 1
		
	if preferences["city"]:	
		location_id = fetch_location_id(dbcursor, preferences["city"], preferences["state"])
		
		if counter >0:
			command = command + " and location_id = " + str(location_id)
		else:
			command = command + " WHERE location_id = " + str(location_id)
		counter = counter + 1
		
	
	if not preferences["city"] and preferences["state"]:	
		# fetch location ID state 
		command_to_fetch_location_id = "SELECT location_id from location WHERE state_name = '" + preferences["state"] + "';"
		dbcursor.execute(command_to_fetch_location_id)
		location_ids_list = dbcursor.fetchall()[0]
		#print(location_ids_list)
		
		possible_ids = "("
		for number in location_ids_list:
			if number != location_ids_list[-1]:
				possible_ids = possible_ids + str(number) + ","
			else:
				possible_ids = possible_ids + str(number) + ")"
		
		if counter >0:
			command = command + " and location_id in " + possible_ids
		else:
			command = command + " WHERE location_id in " + possible_ids
		counter = counter + 1
	
	if preferences["salary"]:	
		if counter >0:
			command = command + " and salary >= " + str(preferences["salary"])
		else:
			command = command + " WHERE salary >= " + str(preferences["salary"])
		counter = counter + 1
		
	if preferences["company"]:	
		if counter >0:
			command = command + " and company_id = '" + str(preferences["company"]) + "'"
		else:
			command = command + " WHERE company_id = '" + str(preferences["company"]) + "'"
		counter = counter + 1
		
	if preferences["field"]:	
		if counter >0:
			command = command + " and field_id = " + str(preferences["field"])
		else:
			command = command + " WHERE field_id = " + str(preferences["field"])
		counter = counter + 1
	
	
	command = command + ";"
		
	dbcursor.execute(command)
	jobsTable = dbcursor.fetchall()
	
	return jobsTable
	
def printJobsTable(jobsTable):
	
	if len(jobsTable) == 0:
		print("\n--- No jobs available for the specified preferences. ---")
		return False
	
	else:	
		print("\n %-5s   %-80s    %-15s   %-5s   %-30s      %3s" % ("job id", "title", "city", "state", "company", "salary"))
		print("-" * 170)
		for record in jobsTable :
			print(" %-6d   %-78s      %-17s  %-5s  %-30s      $ %3d,000" % record)
		print("-" * 170)
		return True

# fetches the location id from city name and state name
# @param city: city as string
# @param state: state abbreviation as string
def fetch_location_id(dbcursor, city, state):
	command_to_fetch_location_id = "SELECT location_id from location WHERE city_name = '" + city + "' and state_name = '" + state + "';"
	dbcursor.execute(command_to_fetch_location_id)
	location_id = dbcursor.fetchall()[0][0]
	return location_id
	
# fetches the company id from company name
def fetch_company_id(dbcursor, company):
	command_to_fetch_company_id = "SELECT company_id from company WHERE company_name = '" + str(company) + "';"
	dbcursor.execute(command_to_fetch_company_id)
	company_id = dbcursor.fetchall()[0][0]
	return company_id
	
def signal_handler(sig, frame):
    print('\n\n--- You exited the program. See you soon! ---\n')
    exit(0)
    
# @param table: name of table as string
# @param attributeList: list with all attribute names, primary key must be first attribute
# @param valueList: list with all values to fill attributes
def UpdateEntry(dbcursor, table, attributeList, valueList, primary_key_attribute, primary_key_value):
	valueIndex = 0
	for attribute in attributeList:
		command = "UPDATE " + table + " SET "+ attribute + " = " + valueList[valueIndex] + " WHERE " + primary_key_attribute +  " = " + primary_key_value + ";"
		valueIndex += 1
		dbcursor.execute(command)
	
		# save the updates
		command = "commit;"
		dbcursor.execute(command)
	print("\nAll updates have been made.\n ")

def CheckIfInTable(dbcursor, attribute_to_select, identifier, identifier_column_name, table, identifier_is_string = True):
	if identifier_is_string:
		command = "SELECT " + attribute_to_select + " from " + table + " WHERE " + identifier_column_name  + "= '" + identifier + "';"
	else:
		command = "SELECT " + attribute_to_select + " from " + table + " WHERE " + identifier_column_name  + "= " + identifier + ";"
		
	dbcursor.execute(command)
	nameList = dbcursor.fetchall()
	
	if len(nameList) == 0 or len(nameList) > 1:
		return 0
	else:
		return nameList[0][0]

def connectToDB():
	cnx = connector.connect(
		host="jobdatabase.cvp2qzu8xnov.us-east-1.rds.amazonaws.com",
		port=3306,
		user="admin",
		password="vywdyg-7cusry-sUkqak")

    # Get a cursor
	dbcursor = cnx.cursor()
	dbcursor.execute("USE Job_listing;")

def job_database_app_simulator():
	cnx = connector.connect(
		host="jobdatabase.cvp2qzu8xnov.us-east-1.rds.amazonaws.com",
		port=3306,
		user="admin",
		password="vywdyg-7cusry-sUkqak")

    # Get a cursor
	dbcursor = cnx.cursor()
	dbcursor.execute("USE Job_listing;")


	# database introduction and instructions
	print("\n--- WELCOME TO THE JOB DATABASE! ---")
	print("---      APPLICANT SEGMENT       ---\n")
	print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
	
	option = (input("\nPlease enter your option (ctrl-c to exit): "))
	if option != "":
		option = int(option)
	else:
		option = int(input("\nPlease enter your option (ctrl-c to exit): "))
	
	while True:
		
		# create new profile
		if option == 1:
			full_name = input("\nPlease enter your full name: ")
			
			nameParts = full_name.split(" ")
			
			nameNotOK = False
			
			for i in range(len(nameParts)):
					if not nameParts[i].isalpha():
						nameNotOK = True
			
			while nameNotOK:
				nameNotOK = False
				print("Invalid entry")
				full_name = input("\nPlease enter your full name (only letters): ")
				nameParts = full_name.split(" ")
				
				for i in range(len(nameParts)):
					if not nameParts[i].isalpha():
						nameNotOK = True

			preferences = preferenceSetting(dbcursor)
						
			# look up largest userId and create new userid
			command = "SELECT MAX(applicant.applicant_id) FROM applicant"
			dbcursor.execute(command)
			listApplicant = dbcursor.fetchall()
			number = listApplicant[0][0]
			
			# first applicant
			if number == None:
				number = 0
			new_id = number+1
			user_id = new_id
			logged_in = True
			current_user = new_id
			
			# add new applicant to table (name, id, preferences)
			command = "INSERT INTO applicant (applicant_name, applicant_id"
			entry = "'" + full_name + "'," + str(new_id) 
			if preferences["city"] != "":
				location_id = fetch_location_id(dbcursor, preferences["city"], preferences["state"])
				command = command + ",location_id"
				entry = entry + "," + str(location_id)
			if preferences["salary"] != "":
				command = command + ",salary"
				entry = entry + "," + str(preferences["salary"])
			if preferences["field"] != "":
				command = command + ",field_id"
				entry = entry + ","+ str(preferences["field"])
			if preferences["company"] != "":
				
				
				command = command + ",company_id"
				entry = entry + ","+ str(preferences["company"]) 
			if preferences["degree"] != "":
				command = command + ",education_level"
				entry = entry + ","+ str(preferences["degree"])
		
			command = command + ") VALUES (" + entry +");"
			dbcursor.execute(command)
			
			# save the updates
			command = "commit;"
			dbcursor.execute(command)
			string = "\nHello " + full_name + ", your user-id is " + str(new_id) + ". Please save this for future reference. "
			print(string)
			
			print("-"*40)
			print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
			option = int(input("\nPlease enter your option (ctrl-c to exit):"))
		
		# log in 
		elif option == 2:
			
			user_id = input("\nEnter your user id: ")
			
			while CheckIfInTable(dbcursor,"applicant_id", user_id, "applicant_id", "applicant", identifier_is_string = True) == 0:
				user_id = input("The id entered does not match an existing user, try again: ")
			
			# search for user_id and check if valid
			command = "SELECT applicant_name from applicant WHERE applicant_id =" + user_id +";"
			dbcursor.execute(command)
			list = dbcursor.fetchall()
			applicant_name = list[0][0]
			print("\nHello ", applicant_name.strip() , "! You have successfully logged in.\n", sep="")
			logged_in = True
			
			command = "SELECT education_level, location_id, field_id, company_id, salary from applicant WHERE applicant_id =" + user_id +";"
			dbcursor.execute(command)
			preference_list = dbcursor.fetchall()
			
			degree = preference_list[0][0]
			location_id = preference_list[0][1]
			
			if location_id:
				command = "SELECT state_name, city_name from location WHERE location_id =" + str(location_id) +";"
				dbcursor.execute(command)
				location_id_list = dbcursor.fetchall()
				state = location_id_list[0][0]
				city = location_id_list[0][1]
			else:
				state = None
				city = None
				
			field = preference_list[0][2]
			company = preference_list[0][3]
			salary = preference_list[0][4]
			
			preferences = {
				"degree": degree,
				"city" : city,
				"state": state,
				"field": field,
				"company": company,
				"salary": salary
				}
			
			print("-"*40)
			print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
			option = int(input("\nPlease enter your option (ctrl-c to exit): "))
			
		# search database
		elif option ==3:
			if not logged_in:
				continue_to_login = input("You are currently logged in as a guest user, would you like to log in? y/n: ")
				if continue_to_login == "y":
					print("switching to login")
					option = 2
				else:
					print("\n you will continue as a guest user. \n")
			
					preferences = preferenceSetting(dbcursor)
					jobsTable = SearchJobs(dbcursor, preferences)
					printJobsTable(jobsTable)
					
					print("-"*40)
					print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
					option = int(input("\nPlease enter your option (ctrl-c to exit): "))
			else:
				jobsTable = SearchJobs(dbcursor, preferences)
				if printJobsTable(jobsTable):
					
				
					save_input = input("\nWould you like to save any of these jobs? y/n: ")
					
					if save_input == "y":
						job_ids = input("Please enter the job id numbers you want to save (comma-separated): ")
						job_list = job_ids.split(",")
						for job in job_list:
							command = "INSERT INTO saved_jobs (job_id, applicant_id) VALUES ("+ job + "," + str(user_id) + ");"
							dbcursor.execute(command)
							# save the updates
							command = "commit;"
							dbcursor.execute(command)
				
				print()
				print("-"*40)
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = int(input("\nPlease enter your option (ctrl-c to exit): "))
				
		# Show saved jobs
		elif option ==4:
			if not logged_in:
				option = 2
			else:
				command = "CREATE TEMP TABLE saved_jobs as SELECT job_id from saved_jobs WHERE applicant_id = " + str(user_id) + ";"
				dbcursor.execute(command)
				command = "commit;"
				dbcursor.execute(command)
				command = "SELECT job_id, job_title, city_name, state_name, company_name, salary from (((jobs NATURAL JOIN saved_jobs)  NATURAL JOIN location) NATURAL JOIN company) where applicant_id = " + str(user_id) + ";"
				dbcursor.execute(command)
				job_list = dbcursor.fetchall()
				
				print("\n %-5s   %-80s    %-15s   %-5s   %-30s      %3s" % ("job #", "title", "city", "state", "company", "salary"))
				print("-" * 170)
				for record in job_list :
					print(" %-6d   %-78s      %-17s  %-5s  %-30s      $ %3d,000" % record)
				print("-" * 170)

				print()			
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = int(input("\nPlease enter your option (ctrl-c to exit): "))
			
		# change preferences
		elif option ==5:
			if not logged_in:
				option = 2
			else:
				attributeList = []
				valueList = []
				
				update = input("\n Would you like to update your degree? y/n: ")
				if update == "y":		
					degree = input("\nWhat is your highest degree earned? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
					if degree != "":
						attributeList.append("education_level")
						valueList.append(str(degree))
					else:
						command = "UPDATE " + "applicant" + " SET "+ "education_level" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
					
				update = input("\n Would you like to update your field? y/n (enter 'option' to see field options): ")
				if update == "option":				
					print("\n\n1016 | Insurance\n1019 | Business Services\n1022 | Manufacturing\n1025 | Information Technology\n1028 | Biotech & Pharmaceuticals\n1031 | Retail\n1034 | Oil, Gas, Energy & Utilities")
					print("1037 | Government\n\n1040 | Health Care\n1043 | Finance\n1046 | Aerospace & Defense\n1049 | Transportation & Logistics\n1052 | Media\n1055 | Telecommunications\n1058 | Real Estate")
					print("1061 | Travel & Tourism\n1064 | Agriculture & Forestry\n1067 | Education\n1070 | Accounting & Legal\n1073 | Non-Profit\n1076 | Construction, Repair & Maintenance\n1079 | Consumer Services\n")
				if update == "y":	
					field_input = input("Enter your preferred field: ")
					if field_input != "":
						attributeList.append("field_id")
						valueList.append(str(field_input))
					else:
						command = "UPDATE " + "applicant" + " SET "+ "field_id" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
				
				update = input("\n Would you like to update your company? y/n: ")
				if update == "y":	
					company_input = input("Enter your preferred company: ")
					if company_input != "":
						attributeList.append("company_id")
						valueList.append(str(company_input))
					else:
						command = "UPDATE " + "applicant" + " SET "+ "company_id" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
					
				update = input("\n Would you like to update your salary? y/n: ")
				if update == "y":
					salary_input = input("Enter your minimum salary: ")
					if salary_input != "":
						attributeList.append("salary")
						valueList.append(str(salary_input))
					else:
						command = "UPDATE " + "applicant" + " SET "+ "salary" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")

				update = input("\n Would you like to update your city? y/n: ")
				if update == "y":
					
					state_input = ""
					
					city_input = input("Enter your preferred city: ")
					if city_input != "":
						state_input = input("Enter the associated state: ")
					while city_input != "" and state_input =="":
						print("\n  ---Error, Please enter a State for your previous city ---\n")
						state_input = input("Enter the associated state: ")
					
					if city_input != "":
						location_id = fetch_location_id(dbcursor, city_input, state_input)
						attributeList.append("location_id")
						valueList.append(str(location_id))
					else:
						command = "UPDATE " + "applicant" + " SET "+ "location_id" + " = " + 'NULL' + " WHERE " + "applicant_id" +  " = " + str(user_id) + ";"
						dbcursor.execute(command)
						dbcursor.execute("commit;")
				else:
					update = input("\n Would you like to update your state? y/n: ")
					if update == "y":
						state_input = input("Enter your preferred state: ")
						city_input = None
						if state_input != "":
							location_id = fetch_location_id(dbcursor, city_input, state_input)
							attributeList.append("location_id")
							valueList.append(str(location_id))
				
				
				UpdateEntry(dbcursor, "applicant", attributeList, valueList, "applicant_id", str(user_id))
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = int(input("\nPlease enter your option (ctrl c to exit): "))
			
		else:
			
			print("Invalid input, try again.")
			print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
			option = (input("\nPlease enter your option (ctrl c to exit): "))
			
			while not option.isnumeric():
				print("Invalid input, try again.")
				print("OPTION 1: Create a profile\nOPTION 2: Log in to an existing account\nOPTION 3: Job search\nOPTION 4: Show saved jobs\nOPTION 5: Change Job preferences")
				option = (input("\nPlease enter your option (ctrl c to exit): "))

			option = int(option)
            
def job_database_comp_simulator():
	
	cnx = connector.connect(
		host="jobdatabase.cvp2qzu8xnov.us-east-1.rds.amazonaws.com",
		port=3306,
		user="admin",
		password="vywdyg-7cusry-sUkqak")

    # Get a cursor
	dbcursor = cnx.cursor()
	dbcursor.execute("USE Job_listing;")
	
	# database introduction and instructions
	print("\n--- WELCOME TO THE JOB DATABASE! ---")
	print("---         COMPANY SEGMENT        ---\n")
	
	companyIn = str(input("Enter the company name: "))
	
	command = "SELECT company_id from company WHERE company_name = '" + str(companyIn) + "';"
	dbcursor.execute(command)
	nameList = dbcursor.fetchall()
	
	while len(nameList) == 0 or len(nameList) > 1:
		print("\nInvalid company name\n")
		companyIn = str(input("Enter the company name: "))
	
		command = "SELECT company_id from company WHERE company_name = '" + str(companyIn) + "';"
		dbcursor.execute(command)
		nameList = dbcursor.fetchall()
	
	company_id = nameList[0][0]
	
	print("\nWelcome " + str(companyIn) + "!")
	print()
	
	print("This database can be used for creating or updating job listings and to create job interest reports\nOPTION 1: Create a job listing\nOPTION 2: Update a job listing\nOPTION 3: Create job interest reports")
	userInAvailable = [1,2,3]
	
	userIn = int(input("\nChoose option: "))
	
	while True:
		while userIn not in userInAvailable:
			print("\nInvalid option\n")
			userIn = int(input("Choose option: "))
		
		# Create Job Listing
		if userIn == 1:
			optionOne(dbcursor, company_id)
			
		# Update Job listing
		elif userIn == 2:
			optionTwo(dbcursor, company_id, companyIn)
		elif userIn == 3:
			optionThree(dbcursor, company_id, companyIn)
		
		print("\nThis database can be used for creating or updating job listings and to create job interest reports\nOPTION 1: Create a job listing\nOPTION 2: Update a job listing\nOPTION 3: Create job interest reports")
	
		userIn = int(input("\nChoose option: "))
	
		
# New Job Listing
def optionOne(dbcursor, company_id):
	
	job = defineJob(dbcursor, company_id)
	
	# if city not in table, add it 
	
	location_id = CheckIfInTable(dbcursor,"location_id", job["city"], "city_name", "location", identifier_is_string = True)
	if location_id == 0:
		command = "SELECT MAX(location.location_id) FROM location"
		dbcursor.execute(command)
		listApplicant = dbcursor.fetchall()
		number = listApplicant[0][0]
		newID = int(number) + 6
		command = "INSERT INTO location (location_id, state_name, city_name) VALUES ("+ str(newID) + ",'" + str(job["state"]) + "','" + str(job["city"]) + "');"
		dbcursor.execute(command)
		
		command = "commit;"
		dbcursor.execute(command)
		
		location_id = newID
		
	command = "SELECT MAX(jobs.job_id) FROM jobs"
	dbcursor.execute(command)
	jobList = dbcursor.fetchall()
	jobNumber = jobList[0][0]
	
	newJobNum = int(jobNumber) + 6
	command = "INSERT INTO jobs (job_id, job_title, location_id, salary, company_id, field_id, education_level) VALUES ("+ str(newJobNum) + ",'" + str(job["title"]) + "'," + str(location_id) + "," + str(job["salary"]) + "," + str(job["company"]) + "," + str(job["field"]) + "," + str(job["degree"]) + ");"
	dbcursor.execute(command)
	
	command = "commit;"
	dbcursor.execute(command)
	
	
		
# Update Job Listing
def optionTwo(dbcursor, company_id, companyIn):
	
	attributeList = []
	valueList = []
	
	# list all current jobs by this company

	command = "SELECT job_id, job_title, city_name, state_name, company_name, salary from ((jobs NATURAL JOIN location) NATURAL JOIN company) WHERE company_id = " + str(company_id) + ";"
	dbcursor.execute(command)
	nameList = dbcursor.fetchall()
	print("\n Current jobs: ")
	
	printJobsTable(nameList)
	
	job_id = input("Please enter the job id # of the job you would like to update: ")
	while CheckIfInTable(dbcursor, "job_id", job_id, "job_id", "jobs", identifier_is_string = False) == 0:
		job_id = input("Invalid job ID, please enter the job id # : ")
	
	update = input("\n Would you like to update the required degree? y/n: ")
	if update == "y":		
		degree = input("\nWhat is the job's degree required? (None = 0, High school = 1, Bachelor = 2, Master = 3, PhD = 4): ")
		attributeList.append("education_level")
		valueList.append(str(degree))
		
	update = input("\n Would you like to update the job's field? y/n: ")
	if update == "y":
		field_input = input("Enter the field: ")
		attributeList.append("field_id")
		valueList.append(str(field_input))
		
	update = input("\n Would you like to update your job's salary? y/n: ")
	if update == "y":
		salary_input = input("Enter the minimum salary: ")
		attributeList.append("salary")
		valueList.append(str(salary_input))

	update = input("\n Would you like to update the city? y/n: ")
	if update == "y":
		city_input = input("Enter the city: ")
		state_input = input("Enter the associated state: ")
		while city_input != "" and state_input =="":
			print("\n  ---Error, Please enter a State for your previous city ---\n")
			state_input = input("Enter the associated state: ")
		location_id = fetch_location_id(dbcursor, city_input, state_input)
		attributeList.append("location_id")
		valueList.append(str(location_id))
	
	
	UpdateEntry(dbcursor, "jobs", attributeList, valueList, "job_id", job_id)
	#option = int(input("\nPlease enter your option (ctrl c to exit): "))

	
def optionThree(dbcursor, company_id, companyIn):
	print("\n--- JOB INTEREST REPORT for " + companyIn + " ---\n")
	
	command = "select location_id from jobs where company_id =  " + str(company_id) + ";"
	dbcursor.execute(command)
	locIDtemp = dbcursor.fetchall()
	loc_id = (locIDtemp[0][0])
	
	command = "select count(*) from applicant where location_id =  " + str(loc_id) + ";"
	dbcursor.execute(command)
	countJobtemp = dbcursor.fetchall()
	countJobInterest = (countJobtemp[0][0])

	print("Total number of prospective job seekers in your area is " + str(countJobInterest))

	
	command = "select count(company_id) from saved_jobs Natural join jobs where company_id = " + str(company_id) + ";"
	dbcursor.execute(command)
	jobCountList = dbcursor.fetchall()
	jobCount = (jobCountList[0][0])
	
	print("Total number of jobs saved for " + str(companyIn) + " is " + str(jobCount)) 
	
	command = "select distinct job_id, job_title from saved_jobs Natural join jobs where company_id = " + str(company_id) + ";"
	dbcursor.execute(command)
	jobList = dbcursor.fetchall()
	print()
	print("%-5s  %-70s %-5s" %  ("Job ID", "Job Title", "Number of Saves"))
	print("-" * 120)
	for i in range(len(jobList)):
		
		jobID = (jobList[i][0])
		jobTitle = (jobList[i][1])
		
		command = "select count(job_id) from saved_jobs where job_id =  " + str(jobID) + ";"
		dbcursor.execute(command)
		jobCountList = dbcursor.fetchall()
		jobCount = (jobCountList[0][0])
		
		print("%-5s   %-70s %-5s" %  (str(jobID), str(jobTitle), str(jobCount)))
	
	print("-" * 120)

def signal_handler(sig, frame):
    print('\n\n--- You exited the program. See you soon! ---\n')
    sys.exit(0)

def CheckIfInTable(dbcursor, attribute_to_select, identifier, identifier_column_name, table, identifier_is_string = True):
	if identifier_is_string:
		command = "SELECT " + attribute_to_select + " from " + table + " WHERE " + identifier_column_name  + "= '" + identifier + "';"
	else:
		command = "SELECT " + attribute_to_select + " from " + table + " WHERE " + identifier_column_name  + "= " + identifier + ";"
		
	dbcursor.execute(command)
	nameList = dbcursor.fetchall()
	
	if len(nameList) == 0 or len(nameList) > 1:
		return 0
	else:
		return nameList[0][0]
		
# @param table: name of table as string
# @param attributeList: list with all attribute names, primary key must be first attribute
# @param valueList: list with all values to fill attributes
def UpdateEntry(dbcursor, table, attributeList, valueList, primary_key_attribute, primary_key_value):
	valueIndex = 0
	for attribute in attributeList:
		command = "UPDATE " + table + " SET "+ attribute + " = " + valueList[valueIndex] + " WHERE " + primary_key_attribute +  " = " + primary_key_value + ";"
		valueIndex += 1
		dbcursor.execute(command)
	
		# save the updates
		command = "commit;"
		dbcursor.execute(command)
	print("\nAll updates have been made. ")