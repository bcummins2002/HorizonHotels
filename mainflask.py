#@Ben Cummins 
#Main flask file for routes of the website
import calendar
from distutils.command.upload import upload
import os
import pathlib
from werkzeug.utils import secure_filename
import mysql.connector
from mysql.connector import errorcode
from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps 
from datetime import datetime,date
#Importing functions created in different files for use in project
from BookingChecks import advanceBooking, cancellationfare ,peakCheck,currencyCheck #Importing functions for booking buisness logic
#Start of main file
app = Flask(__name__)   #Instatntiating flask app
app.secret_key = "Secret123" #Creating a secret key for use in sessions

#Creating a connection to the database 
#MYSQL CONFIG VARIABLES
hostname    = "127.0.0.1"
username    = "benjamin2cummins"
passwd  = "Clive312!_"
db="benjamin2cummins_prj"

def getConnection():    
   try:
      conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              database=db
                              )  
   except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
      else:
            print(err)                        
   else:  #will execute if there is no exception raised in try block
      return conn  

#Creating wrappers to use in the website
#Creating a wrapper to recongise if the user is logged in or not
def loginRequired(f):
   @wraps(f)
   def wrap(*args, **kwargs):
      if 'logged_in' in session:
         return f(*args, **kwargs)
      else:            
         print("User must be logged in first")
         return render_template('login.html', error='You must be logged in to perform this action') #Returns the user to a page with the relevant error 
   return wrap

#Creating a wrapper to require the user is an admin user
def adminRequired(f):
   @wraps(f)
   def wrap(*args, **kwargs):
      if ('logged_in' in session) and (session['userType'] == 'adm'):
         return f(*args, **kwargs)
      else:            
         print("User must be logged in as an admin user")
         return render_template('login.html', error='You must be logged in as an admin to perform this action') #Returns the user to the login page with an relevant error    
   return wrap

#Creating a wrapper to require the user to be a standard user
def standardRequired(f):
   @wraps(f)
   def wrap(*args, **kwargs):
      if ('logged_in' in session) and (session['userType'] == 'std'):
         return f(*args, **kwargs)
      else:            
         print("User must be logged in as a standard user")
         return render_template('login.html', error='You must be logged in as a standard user to perform this action') #Returns the user to the login page with relevant error   
   return wrap

#Creating routes for the webpages to connect
#Route to the home page
@app.route('/') 
def home():            
   print ('Homepage is running') #Output for debugging. Console print
   return render_template('home.html') #Return template of home

#Route to the locations page
@app.route('/locations') 
def locations():
   print("locations is running") #Output for debug
   conn = getConnection()
   if conn != None:    #Checking if connection is None         
      print('MySQL Connection is established')                          
      dbcursor = conn.cursor()    #Creating cursor object            
      dbcursor.execute('SELECT DISTINCT hotelLoc FROM hotel;')   		           
      rows = dbcursor.fetchall()                                    
      dbcursor.close()              
      conn.close() #Connection must be closed
      cities = []				#List of all cities where accomodation can be booked
      for city in rows:		#as we used fetchall we must clean the data
         city = str(city).strip("(")
         city = str(city).strip(")")
         city = str(city).strip(",")
         city = str(city).strip("'")
         cities.append(city)
      return render_template('loctest.html',locs=cities) #return template of locations
   else:
      print('DB connection Error')
      return render_template('locations.html') #return template of locations

#Route to the rooms page
@app.route('/rooms') 
def rooms():
   print("rooms is running") #Debug message
   return render_template('rooms.html') #Return template of rooms

#Booking Process adapted from lecture slides
#Route to the booking page
@app.route('/booking') 
def index():	# Gets cities from DB and passes to html template for dynamic web page generation
	conn = getConnection()
	if conn != None:    #Checking if connection is None         
		print('MySQL Connection is established')                          
		dbcursor = conn.cursor()    #Creating cursor object            
		dbcursor.execute('SELECT DISTINCT hotelLoc FROM hotel;')   		           
		rows = dbcursor.fetchall()                                    
		dbcursor.close()              
		conn.close() #Connection must be closed
		cities = []				#List of all cities where accomodation can be booked
		for city in rows:		#as we used fetchall we must clean the data
			city = str(city).strip("(")
			city = str(city).strip(")")
			city = str(city).strip(",")
			city = str(city).strip("'")
			cities.append(city)
		return render_template('booking.html', hotelLoc=cities)
	else:
		print('DB connection Error')
		return render_template('booking.html',  error='DB Connection Error')

#Creating a route for form submission for booking adapted from lecture slides
@app.route('/startbooking', methods=['POST','GET'])
def startBooking():
   if request.method == 'POST':
         print('Select booking initiated')
         hotelLoc = request.form['loc']
         bookingStart = request.form['sdate']
         bookingEnd = request.form['edate']
         noofguests = request.form['noofguests']
         roomType=request.form['roomtype']	
         currency=request.form['currency']			
         noofnights = datetime.strptime(bookingEnd, '%Y-%m-%d') - datetime.strptime(bookingStart, '%Y-%m-%d')
         #print(noofnights.days) #Debug Line to print the numbers of days someone is staying
         bookingCreationDate = date.today() #Saving creation date as today for buisness logic
         #print(bookingCreationDate) #Debug print
         #print(type(bookingCreationDate))#Printing the type for debugging purposes
         lookupdata = [hotelLoc, bookingStart, bookingEnd, noofguests, noofnights.days,roomType,currency]			
         conn = getConnection()
         if conn != None:    #Checking if connection is None         
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object            
            dbcursor.execute('SELECT * FROM hotel WHERE hotelLoc = %s;', (hotelLoc, ))   
            #print('SELECT statement executed successfully(Retrieved hotel database).')             
            rows = dbcursor.fetchall()
            #print(rows)
            for row in rows: #Getting value from tuple for capacity and id
               hotelId=row[0]
               hotelCapacity=row[4]
            datarows=[]		
            datetime.strptime(bookingStart,'%Y-%m-%d')
            #print(bookingStart) #Printing the booking start date for debug
            #Calculating the fare if the booking is on or off peak
            for row in rows:
               data = list(row)
               onpeak=peakCheck(bookingStart) #Checking if the value returned is true
               if onpeak==True:
                  #print(str(row[3])+"is current row") #Printing the price of one night for debug
                  if roomType=="Standard":
                     #print("Room on peak standard")
                     fare=(float(row[3]) * int(noofnights.days)) #Using on peak prices
                  elif roomType=="Double":
                     #print("Room onpeak double")
                     fare=(((float(row[3]/100)*20)+float(row[3]))* int(noofnights.days)) #On peak double room
                     if noofguests=="2":
                     #   #print("Double room tax added for 2 people...")
                        #print("total fare after tax is")
                        fare=fare+((float(row[3]/100)*10)) #Adding tax for 2 people in the double room
                  elif roomType=="Family":
                     #print("Room is on peak family")
                     fare=(((float(row[3]/100)*50)+float(row[3]))* int(noofnights.days)) #On peak family room
               elif onpeak ==False: #Offpeak room prices
                  #print(str(row[2])+"is current row") #Printing the price of one night for debug
                  if roomType=="Standard":
                     #print("Room offpeak standard")
                     fare=(float(row[2])* int(noofnights.days)) #Using off peak prices
                  elif roomType=="Double":
                     #print("Room offpeak double")
                     fare=(((float(row[2]/100)*20)+float(row[2]))* int(noofnights.days)) #On peak double room
                     if noofguests=="2":
                        #print("Double room tax added for 2 people...")
                        #print("total fare after tax is")
                        fare=fare+((float(row[2]/100)*10)) #Adding tax for 2 people in the double room
                  elif roomType=="Family":
                     #print("Room offpeak family")
                     fare=(((float(row[2]/100)*50)+float(row[2]))* int(noofnights.days)) #On peak family room
               discount=advanceBooking(bookingCreationDate,bookingStart,fare) #Calculating the discount from the fare
               #print(str(fare)+"before discount") #Printing fare before discount to console
               totalfare=fare-discount #Taking the advance booking discount off the fare
               #print(totalfare) #Printing fare after discount to console         
               #Calling a function that will calculate the user rates in the selected currency
               float(totalfare)
               print(totalfare)
               totalfare=currencyCheck(currency,totalfare)
               round(totalfare,2)#Rounding the converted fare to 2 decimal points
               
               data.append(totalfare)
               print(totalfare)				
               datarows.append(data)	
               lookupdata.append(totalfare)
            print(roomType)
            #Calculating rooms available
            if roomType=="Standard":
               hotelCapacity= (hotelCapacity/100)*30
            elif roomType=="Double":
               hotelCapacity= (hotelCapacity/100)*50
            elif roomType=="Family":
               hotelCapacity=(hotelCapacity/100)*20
            dbcursor.execute("SELECT * FROM Booking WHERE hotelId=%s AND  roomType=%s;",(hotelId,roomType,))
            bookingData=dbcursor.fetchall()
            for booking in bookingData:
               #print(datetime.strptime(bookingStart, '%Y-%m-%d'))
               if booking[1] <= datetime.date(datetime.strptime(bookingStart, '%Y-%m-%d')) <= booking[2]:
                  #print("booking found in range..")
                  hotelCapacity=hotelCapacity-1
               elif booking[1] <= datetime.date(datetime.strptime(bookingEnd, '%Y-%m-%d')) <= booking[2]:
                  #print("booking found in range...")
                  hotelCapacity=hotelCapacity-1
            #print("Rooms avaialble to book is "+str(hotelCapacity))
            if hotelCapacity==0:
               print("No available rooms to book")
               error="no available rooms to book"
               return render_template('booking.html',error=error)
            dbcursor.close()              
            conn.close() #Connection must be closed			
            #print(datarows)
            return render_template('bookingconfirm.html',resultset=datarows, lookupdata=lookupdata,hotelCapacity=int(hotelCapacity))
         else:
            print('DB connection Error')
            return render_template('booking.html')

#Route to confirm the booking and get the user's payment method.
@app.route ('/bookingpayment', methods = ['POST', 'GET'])
@loginRequired
def bookingPayment():
   if request.method == 'POST' :		
      email = session['email']
      #print('Booking payment is now running') #Debug code	
      hotelLoc = request.form['hotelLoc']		
      checkind = request.form['checkind']
      checkoutd = request.form['checkoutd']
      noofguests = request.form['noofguests']		
      noofnights = datetime.strptime(checkoutd, '%Y-%m-%d') - datetime.strptime(checkind, '%Y-%m-%d')	
      roomType=request.form['roomtype']
      totalfare = request.form['totalfare']
      cardnumber = request.form['cardNo']
      currency=request.form['currency']
      #print(currency)
      expirydate=request.form['expiry']
      cvv=request.form['cvv']
      bookingdata = [roomType, hotelLoc, checkind, checkoutd, noofguests, totalfare, noofnights.days,cardnumber]
      #print(roomType)
      #print("fare is " +totalfare)
		#Now we need to save booking data in DB
      conn = getConnection()
      if conn != None:    #Checking if connection is None         
         print('MySQL Connection is established')
         dbcursor = conn.cursor()    #Creating cursor object
         cardnumber = cardnumber[-4:] 
         #print(cardnumber)#Debug Print       
         dbcursor.execute('SELECT hotelId FROM hotel WHERE hotelLoc = %s;', (hotelLoc, )) #Getting the hotel Id for the selected location
         hotelId=dbcursor.fetchone()
         hotelId=int(hotelId[0]) #Converting hotelId from a tuple to an int to be stored in database
         #print(hotelId)
         dbcursor.execute('SELECT accountId FROM account where email=%s;',(email, )) #Get the user account id from database
         accId=dbcursor.fetchone()
         accId=int(accId[0])#Converting accId from a tuple to an int to be stored in database
         #print(accId)
         dbcursor.execute('INSERT INTO Booking (bookingStart, bookingEnd, roomType, cardNo,currency,hotelId,accountId,totalCost, guestNo ) VALUES \
            (%s, %s, %s, %s, %s,%s,%s,%s,%s);', (checkind, checkoutd,roomType,cardnumber,currency,hotelId,accId,totalfare, noofguests ))   
         print('Booking statement executed successfully.')             
         conn.commit()	

         #As bookingid is autogenerated so we can get it by running following SELECT
         dbcursor.execute('SELECT LAST_INSERT_ID();')			
         rows = dbcursor.fetchone()			
         bookingid = rows[0]
         bookingdata.append(bookingid)

         dbcursor.execute
         dbcursor.close()              
         conn.close() #Connection must be closed
         return render_template('bookingsuccess.html', resultset=bookingdata, cardnumber=cardnumber,currency=currency)
      else:
         print('DB connection Error')
         return render_template('booking.html')

@app.route('/bookingsuccess', methods = ['POST', 'GET'])
def bookingSuccess():
   print("bookingsuccess is running")
   return render_template('bookingsuccess.html')


#Route to the about us page
@app.route('/aboutus') 
def aboutus():
   print("About us page is running") #Debug
   return render_template('aboutus.html') #Returns template of aboutus

#Creating a route for registering to the webstie
@app.route('/register', methods=['POST', 'GET'])
def register():
   error = ''
   print('Register start')
   try:
      if request.method == "POST":         
            firstName = request.form['fname']
            lastName=request.form['lname']
            password = request.form['password']
            email = request.form['email']                      
            if firstName != None and lastName != None and password != None and email != None:           
               conn = getConnection()
               if conn != None:    #Checking if connection is None           
                  if conn.is_connected(): #Checking if connection is established
                        print('MySQL Connection is established: '+db)                          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #Hashing the password for security purposes
                        password = sha256_crypt.hash((str(password)))           
                        Verify_Query = "SELECT * FROM account WHERE email = %s;"  
                        dbcursor.execute(Verify_Query,(email,))
                        rows = dbcursor.fetchall()           
                        if dbcursor.rowcount > 0:   #this means there is a user with same email
                           print('email already taken, please choose another')
                           error = "Email is already taken, please choose another"
                           return render_template("register.html", error=error)    
                        else:   #Passes the check for the same email  
                           print("Thanks for registering! "+email +password +firstName +lastName)         
                           dbcursor.execute("INSERT INTO account (email, accPassword, \
                                 firstName, lastName) VALUES (%s, %s, %s, %s)", (email, password, firstName, lastName))                
                           conn.commit()  #saves data in database            
                           dbcursor.close()
                           conn.close()
                           gc.collect()                        
                           session['logged_in'] = True     #session variables
                           session['email'] = email
                           session['userType'] = 'std'   #default all users are standard
                           return render_template("account.html",\
                           message='User registered successfully and logged in.')
                  else:                        
                        print('Connection error')
                        return 'DB Connection Error'
               else:                    
                  print('Connection error')
                  return 'DB Connection Error'
            else:                
               print('empty parameters')
               return render_template("register.html", error=error)
      else:            
            return render_template("register.html", error=error)        
   except Exception as e:                
      return render_template("register.html", error=e)    

@app.route('/login', methods=["GET","POST"])
def login():
   form={}
   print("Login start")
   error = ''
   try:	
      if request.method == "POST":            #Taking user data from the form
            email = request.form['email']
            password = request.form['password']         
            #print(type(password))   
            form = request.form
            #print('Login Starting') #Printing to console for developing
            if email != None and password != None:  #Checking the user has entered their email and password 
               conn = getConnection()
               if conn != None:    #Checking if connection is None                    
                  if conn.is_connected(): #Checking if connection is established                        
                        print('MySQL Connection is established')#Printing to console for developing          
                        dbcursor = conn.cursor()    #Creating cursor object          
                        #print(email)                                       
                        dbcursor.execute("SELECT accPassword, userType \
                           FROM account WHERE email = %s;", (email,))                                                
                        data = dbcursor.fetchone()
                        #print(type(data[0]))
                        if dbcursor.rowcount < 1: #Checking to ensure the combination entered exsists                        
                           error = "Email and password does not exist, login again"
                           #print(error) #Debug line for console
                           return render_template("login.html", error=error)
                           
                        else:                       
                           #print("Password check")     
                           #data = dbcursor.fetchone()[0] #extracting password   
                           # Verify passowrd hash and password received from user                                                             
                           if sha256_crypt.verify(request.form['password'], str(data[0])):   
                              #print("password check complete")                             
                              session['logged_in'] = True     #set session variables
                              session['email'] = request.form['email']
                              #print(type(data[1]))
                              session['userType'] = str(data[1])  
                              #print(session['userType'])                      
                              print("You are now logged in")  
                              message="You have been successfully logged in"                              
                              return render_template('account.html', \
                                 email=email,message=message, data='This is user specific data',\
                                       userType=session['userType'])
                           else:
                              error = "Invalid credentials username/password, try again."                               
                  gc.collect()
                  return render_template("login.html", form=form, error=error)
   except Exception as e:                
      error = str(e)+"Invalid login details."
      return render_template("login.html", form=form, error = error)   
   return render_template("login.html", form=form, error = error)
#Creating a route for the user to logout
#Using loginRequired wrapper to ensure the user is logged in
@app.route('/logout', methods=["GET","POST"])
@loginRequired
def logout():
   session.clear()
   print("logout succesful") #Debug print
   gc.collect()
   return render_template('login.html',error="You have succesfully been logged out.")
#Creating a route for account management which allows a user to cancel a booking etc
#Using loginRequired wrapper and checking the user type with the associated wrappers
@app.route('/account',methods=["GET","POST"])
@loginRequired
def account():
   print("account is running")
   return render_template('account.html')

#Routes for admin features adding a hotel and generating a booking report

#Report Generation Routes
@app.route("/report",methods=["GET","POST"])
@loginRequired
@adminRequired
def generatereport():
	conn = getConnection()
	if conn != None:    #Checking if connection is None         
		print('MySQL Connection is established')                          
		dbcursor = conn.cursor()    #Creating cursor object            
		dbcursor.execute('SELECT DISTINCT hotelLoc FROM hotel;')   		           
		rows = dbcursor.fetchall()                                    
		dbcursor.close()              
		conn.close() #Connection must be closed
		cities = []				#List of all cities where accomodation can be booked
		for city in rows:		#as we used fetchall we must clean the data
			city = str(city).strip("(")
			city = str(city).strip(")")
			city = str(city).strip(",")
			city = str(city).strip("'")
			cities.append(city)
		return render_template('report.html', hotelLoc=cities)
	else:
		print("DB connection Error")
		return render_template('report.html', error="Database connection error")
#Route to display report details
@app.route('/reportdata', methods=["GET","POST"])
@loginRequired
@adminRequired
def report():
   month=request.form['rmonth'] #Getting month selected
   locations=request.form.getlist('rhotel') #Getting checkbox as list
   displayMonth=calendar.month_name[int(month)]
   #print(displayMonth)
   try:  
      conn=getConnection()
      if conn !=None:
         if conn.is_connected():
            print("Mysql connection working")
            dbcursor=conn.cursor()
            reportList=[]
            for location in locations:
               dbcursor.execute("SELECT hotelId From hotel WHERE hotelLoc=%s;",(location,))
               hotelId=dbcursor.fetchone()
               #print(hotelId)
               hotelId=int(hotelId[0])
               dbcursor.execute("SELECT bookingNumber,hotelId,totalCost,bookingStart,bookingEnd FROM Booking WHERE hotelId = %s;", (hotelId,))
               reportDetails=dbcursor.fetchall() #Saving all booking details as a list
               reportDetails=list(reportDetails)
               for detail in reportDetails:
                  #print((detail[3].month))
                  if (detail[3].month)==int(month):
                     reportList.append(detail)
               if reportList==[]:
                  error="No available bookings"
                  #print(error)
                  return render_template("account.html",error=error)
               finalReport=[]
               for detail in reportList:
                     detail=list(detail)
                     hotelId=str(detail[1]) #Converting hotelId to str for db arguement
                     dbcursor.execute('SELECT hotelLoc from hotel where hotelid=%s;',(hotelId,)) #Selecting locationf or user experience
                     hotelLoc=dbcursor.fetchone() #Saving hotelLoc as new variable
                     #print(hotelLoc)
                     detail[1]=str(hotelLoc).strip("(,)").replace("'"," ") #Formatting and replacing for user friendly look
                     finalReport.append(detail) #Appending to bookingList for display
               #print(finalReport)
            dbcursor.close()
            conn.close()
            gc.collect()   
            return render_template("reportfinal.html",finalReport=finalReport,month=displayMonth)
         else:
            error="Could not connect to database try again"
            return render_template("account.html", error=error)
      else:
         error="No database connection"
         return render_template("account.html", error=error)
   except Exception as e:
      error="Exception"+str(e)
      return render_template("account.html", error=error)
#New Hotel Route
@app.route('/newhotel',methods=["GET","POST"])
@loginRequired
@adminRequired
def newHotel():
   print("New hotel is running")
   return render_template("newhotel.html")

@app.route('/newhotelsubmit',methods=["GET","POST"])
@loginRequired
@adminRequired
def newHotelSuccess():
   print("Adding new hotel process starting")
   try:
      if request.method=="POST": #Saving the values into the form
         newHotelLoc=request.form['newHotelLoc']
         newCapacity=request.form['hotelCapacity']
         newOnPeak=request.form['onPeakPrice']
         newOffPeak=request.form['offPeakPrice']
         if newHotelLoc != None and newCapacity != None and newOnPeak != None and newOffPeak != None:
               conn = getConnection()
               if conn != None:    #Checking if connection is None           
                  if conn.is_connected(): #Checking if connection is established
                        print('MySQL Connection is established: '+db)                          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #Inserting the new hotel data into the database
                        #print("Fetching database")
                        #print("Adding the new hotel into the database")
                        dbcursor.execute("INSERT INTO hotel (hotelLoc, \
                              stdRoomPrice, stdRoomPeakPrice,capacity) VALUES (%s, %s, %s, %s)", (newHotelLoc, newOffPeak, newOnPeak, newCapacity))                   
                        conn.commit()  #saves data in database            
                        dbcursor.close()
                        conn.close()
                        gc.collect()    
                        print("Hotel added succesfully")
                        message="Hotel succesfully added"
                        return render_template("account.html",message=message)
                  else:
                     error="Database connection error"
                     return render_template("account.html",error=error)
               else:
                  error="Database error"
                  return render_template("account.html",error=error)
   except Exception as e:
      error=str(e)
      return render_template("account.html",error=error)

#Removing a hotel routes
@app.route("/removehotel")
@loginRequired
@adminRequired
def removeHotel():
   #Getting a list of all the hotel
   conn = getConnection()
   if conn != None:    #Checking if connection is None         
      print('MySQL Connection is established')                          
      dbcursor = conn.cursor()    #Creating cursor object            
      dbcursor.execute('SELECT DISTINCT hotelLoc FROM hotel;')   		           
      rows = dbcursor.fetchall()                                    
      dbcursor.close()              
      conn.close()         #Connection must be closed
      cities = []				#List of all cities where accomodation can be booked
      for city in rows:		#as we used fetchall we must clean the data
         city = str(city).strip("(")
         city = str(city).strip(")")
         city = str(city).strip(",")
         city = str(city).strip("'")
         cities.append(city)
      return render_template('removehotel.html', hotelLoc=cities)
   else:
      print('DB connection Error')
      return 'DB Connection Error'

@app.route("/removehotelconfirm",methods=["GET","POST"])
@loginRequired
@adminRequired
def removeHotelConfirm():
   print("Removing hotel")
   try:
      if request.method=="POST": #Saving the values from the form
         selectedHotel=request.form['selectedHotel']
         #print(selectedHotel)
         if selectedHotel != None:           
               conn = getConnection()
               if conn != None:    #Checking if connection is None           
                  if conn.is_connected(): #Checking if connection is established
                        print('MySQL Connection is established: '+db)                          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #Removing old hotel data into the database
                        #print("Removing the hotel details from the database")
                        dbcursor.execute("DELETE FROM hotel WHERE hotelLoc =%s;", (selectedHotel,))           
                        #print("hotel removed...")     
                        conn.commit()  #Commits the delete          
                        dbcursor.close()
                        conn.close()
                        gc.collect()    
                        #print("Hotel removed succesfully")
                        message="Removal sucessful"
                        return render_template("account.html",message=message)
                  else:
                     error="Database connection error"
                     return render_template("account.html",error=error)
               else:
                  error="Database error"
                  return render_template("account.html",error=error)
   except Exception as e:
      error=str(e)
      return render_template("account.html",error=error)

#Creating routes for standard users
#Cancel booking route
@app.route("/cancelbooking",methods=["POST","GET"])
@loginRequired
def cancelbooking():
   email=session['email']
   print("Booking cancellation is running")
   try:
      conn=getConnection()
      if conn !=None:
         if conn.is_connected():
            print("Mysql connection working")
            dbcursor=conn.cursor()
            dbcursor.execute('SELECT accountId FROM account where email=%s;',(email, )) #Get the user account id from database
            accId=dbcursor.fetchone()
            accId=int(accId[0])#Converting accId from a tuple to a int
            #print(accId)#Debug print
            dbcursor.execute("SELECT bookingNumber,hotelId,totalCost,bookingStart,bookingEnd FROM Booking WHERE accountId = %s;" %   (accId,))
            booking_details=dbcursor.fetchall() #Saving all booking details as a list
            booking_details=list(booking_details)
            if len(booking_details)!=0:  
               bookingList=[] #Creating empty list to change value for user friendly 
               cancelList=[] #Creating empty list to append cancellation list
               for detail in booking_details:
                  if detail[3] > date.today():
                     #print("Valid cancellation")
                     cancelList.append(detail)
                  elif detail[3]< date.today():
                     print("Past booking")
               if cancelList==[]: #If there are no available bookings
                  error="No bookings available to cancel"
                  return render_template("account.html",error=error)
               else:
                  #print(cancelList)
                  for detail in cancelList:
                     detail=list(detail)
                     hotelId=str(detail[1]) #Converting hotelId to str for db arguement
                     dbcursor.execute('SELECT hotelLoc from hotel where hotelid=%s;',(hotelId,)) #Selecting locationf or user experience
                     hotelLoc=dbcursor.fetchone() #Saving hotelLoc as new variable
                     #print(hotelLoc)
                     detail[1]=str(hotelLoc).strip("(,)").replace("'"," ") #Formatting and replacing for user friendly look
                     bookingList.append(detail) #Appending to bookingList for display
                  print("Booking details got")
                  dbcursor.close()
                  conn.close()
                  gc.collect() 
                  return render_template("bookingcancell.html",booking_list=bookingList)
            else:
               error="No bookings created"
               return render_template("account.html", error=error)
         else:
            error="Could not connect to database try again"
            return render_template("account.html", error=error)
      else:
         error="No database connection"
         return render_template("account.html", error=error)
   except Exception as e:
      error="Exception"+str(e)
      return render_template("account.html", error=error)

@app.route("/cancelpayment",methods=["POST","GET"])
@loginRequired
def cancelpayment():
   print("Booking Cancellation confirmed")
   bookingSelection=request.form["bookingsel"]
   #print(bookingSelection)
   try:
      conn=getConnection()
      if conn !=None:
         if conn.is_connected():
            print("Mysql connection working")
            dbcursor=conn.cursor()
            dbcursor.execute("SELECT totalCost,bookingStart,cardNo FROM Booking WHERE bookingNumber = %s;",(bookingSelection,)) #Delete booking
            bookingInformation=dbcursor.fetchone()         
            dbcursor.close()  
            conn.close()
            gc.collect()
            #print(bookingInformation)
            bookingcharge=cancellationfare(bookingInformation[0],bookingInformation[1])
            #print(bookingcharge)
            return render_template("cancelpay.html",bookingsel=bookingSelection,bookingcharge=bookingcharge, cardNo=bookingInformation[2])
         else:
            error="Could not connect to database try again"
            return render_template("account.html", bookingsel=bookingSelection,error=error)
      else:
         error="No database connection"
         return render_template("account.html", error=error)
   except Exception as e:
      error="Exception"+str(e)
      return render_template("account.html", error=error)


@app.route("/cancelsuccess",methods=["POST","GET"])
@loginRequired
def cancelsuccess():
   print("Booking Cancellation confirmed")
   bookingsel=request.form['bookingcid']
   #print(bookingsel)
   try:
      conn=getConnection()
      if conn !=None:
         if conn.is_connected():
            print("Mysql connection working")
            dbcursor=conn.cursor()
            dbcursor.execute('DELETE FROM Booking where bookingNumber=%s;',(bookingsel, )) #Delete booking
            message="Booking deleted succesfully"
            conn.commit()  #Commits the delete          
            dbcursor.close()
            conn.close()
            gc.collect() 
            return render_template("account.html",message=message)
         else:
            error="Could not connect to database try again"
            return render_template("account.html", error=error)
      else:
         error="No database connection"
         return render_template("account.html", error=error)
   except Exception as e:
      error="Exception"+str(e)
      return render_template("account.html", error=error)

#View bookings
@app.route("/viewbookings",methods=["GET","POST"])
@loginRequired
def viewbookings():
   email=session['email']
   print("Booking cancellation is running")
   try:
      conn=getConnection()
      if conn !=None:
         if conn.is_connected():
            print("Mysql connection working")
            dbcursor=conn.cursor()
            dbcursor.execute('SELECT accountId FROM account where email=%s;',(email, )) #Get the user account id from database
            accId=dbcursor.fetchone()
            accId=int(accId[0])#Converting accId from a tuple to a int
            #print(accId)#Debug print
            dbcursor.execute("SELECT bookingNumber,hotelId,currency,totalCost,bookingStart,bookingEnd FROM Booking WHERE accountId = %s;" %   (accId,))
            booking_details=dbcursor.fetchall() #Saving all booking details as a list
            booking_details=list(booking_details)
            #print(booking_details)
            #print(len(booking_details))
            if len(booking_details)!=0:  
               bookingList=[] #Creating empty list to change value for user friendly 
               for detail in booking_details:
                  detail=list(detail)
                  hotelId=str(detail[1]) #Converting hotelId to str for db arguement
                  dbcursor.execute('SELECT hotelLoc from hotel where hotelid=%s;',(hotelId,)) #Selecting locationf or user experience
                  hotelLoc=dbcursor.fetchone() #Saving hotelLoc as new variable
                  #print(hotelLoc)
                  detail[1]=str(hotelLoc).strip("(,)").replace("'"," ") #Formatting and replacing for user friendly look
                  bookingList.append(detail) #Appending to bookingList for display
                  print("Booking details got")
               dbcursor.close()
               conn.close()
               gc.collect() 
               print("render template")
               return render_template("viewbookings.html",booking_list=bookingList)
            else:
               error="No bookings created"
               return render_template("account.html", error=error)
         else:
            error="Could not connect to database try again"
            return render_template("account.html", error=error)
      else:
         error="No database connection"
         return render_template("account.html", error=error)
   except Exception as e:
      error="Exception"+str(e)
      return render_template("account.html", error=error)

#Password change 
@app.route("/changepassword")
@loginRequired
def passwordchange():
   print("Password change page is running")
   return render_template("changepassword.html")

@app.route("/passwordchangeconfirm",methods=["GET","POST"])
@loginRequired
def passwordchangeconfirm():
   try:	
      if request.method == "POST":            #Taking user data from the form
            oldpassword = request.form['oldpassword']
            newpassword = request.form['newpassword']  
            newpassword= sha256_crypt.hash((str(newpassword)))          
            form = request.form
            #print('Password Change Begin') #Printing to console for developing
            if oldpassword != None and newpassword != None:  #Checking the forms are not empty
               conn = getConnection()
               if conn != None:#Checking if connection is None                    
                  if conn.is_connected():                         #Checking if connection is established                        
                        print('MySQL Connection is established')  #Printing to console for developing          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #print(session['email'])  
                        email=session['email']                                              
                        dbcursor.execute("SELECT accPassword \
                           FROM account WHERE email = %s;", (email,))                                                 
                        data = dbcursor.fetchone()
                        #print(type(data[0]))                    
                        #print("Password check")     
                        #data = dbcursor.fetchone()[0] #extracting password   
                        # Verify the current password the with the password user has entered                                                           
                        if sha256_crypt.verify(request.form['oldpassword'], str(data[0])):  
                           #print("passwords match")                   
                           dbcursor.execute("UPDATE account SET accPassword = %s \
                              WHERE email = %s;", (newpassword,email,)) #Passwords Match so update value in table
                           conn.commit()  #saves data in database            
                           dbcursor.close()
                           conn.close()
                           gc.collect()
                           message="Password Succesfully Changed" 
                           print(message)                             
                           return render_template('account.html', \
                              message=message)
                        else:
                           error = "Passwords do not match, try again."                               
                  gc.collect()
                  return render_template("changepassword.html", form=form, error=error)
   except Exception as e:                
      error = str(e)+"Passwords do not match."
      return render_template("changepassword.html", form=form, error = error)   
   return render_template("changepassword.html", form=form)

#if __name__ == '__main__':   
#   app.run(debug = True)
if __name__ == '__main__':
   for i in range(13000, 18000):
      try:
         app.run(debug = True, port = i)
         break
      except OSError as e:
         print("Port {i} not available".format(i))
