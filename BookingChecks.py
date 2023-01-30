#BookingChecks.py @author Ben Cummins
#A group of functions that perfrom the required checkss for the buisness logic in booking
#For use in MainFlask.py
from datetime import datetime,date

#Debug
#bookingCreationDate = date.today()
#bookingStart=date(2022,5,31)
#totalfare=154.79
#Creating a function to calculate discount on a booking taking required values
def advanceBooking(bookingCreationDate,bookingStart,totalfare):
    #Finding the difference between the two bookings
    bookingStart=datetime.strptime(bookingStart,'%Y-%m-%d') #Changing bookingStart from a string to a datetime for conversion
    bookingStart=datetime.date(bookingStart) #Making the booking start in date form
    difference=bookingStart-bookingCreationDate #Calculating the difference
    #Converting the difference into days
    difference=(difference.days)
    #Debug Print
    print("The difference of days is "+str(difference))
    #Simple if statement which calculates the per
    if difference >=80 and difference <=90:
        discount = totalfare/100 * 20
    elif difference >=60 and difference <=79:
        discount = totalfare/100 *10
        print(discount)
    elif difference >=45 and difference <=59:
        discount = totalfare/100*5
    else:
        discount=0#Setting default discount of 0 for when there is no discount
    return round(discount,2)
    
#discount=advanceBooking(bookingCreationDate,bookingStart,totalfare)
#print("Discount is "+str(discount))


#Creating new function for checking if it is on peak or not
#Testing variables for debug
#bookingStart=date(2022,10,30)
#Defining a function for use in mainflask.py, take arguments for check in date
def peakCheck(checkindate):
    checkindate=datetime.strptime(checkindate,'%Y-%m-%d') #Making sure the check in date is of type datetime in the correct format
    #If statement checking if the date is in range
    if checkindate.month >= 4 and checkindate.month <= 9:
        print("Booking is on peak")
        onpeak=True
    else: #If the booking doesnt fall in the peak months, return value of false
        print("Booking is off peak")
        onpeak=False
    #Return the bool value of onpeak if it true or false
    return onpeak

#Testing function
#onpeak=peakCheck(bookingStart)
#print(onpeak)
#Function for calculating the currency exchange rate
def currencyCheck(currency,totalfare):
    #Converting the toal fare to a float for multiplicaiton
    totalfare=float(totalfare)
    if currency=="GBP": #If the selected currency is pounds, return fare as it was
        return totalfare
    elif currency=="EUR": #If euros, multiply by the set exchange rate
        totalfare=totalfare * 1.2
        return totalfare
    elif currency=="USD": #If dollars, multiply by the set exchange rate
        totalfare=totalfare * 1.6
        return totalfare
    else:
        error=("Unkown error occured")
        return error


#Creating new function for booking cancellation
#Generates how much you are required to paybaack when cancelling a booking
def cancellationfare(totalFare,bookingStart):
    todaysDate= date.today()
    print(todaysDate)
    print(bookingStart)
    difference=bookingStart-todaysDate
    difference=(difference.days)
    print("difference is")
    print(difference)
    if difference >= 60:
        print("Full refund")
        refund=100
        return refund
    elif difference >=30 and difference < 60:
        print("50 refund")
        refund = 50
        return refund
    elif difference >=0 and difference <30:
        refund = 0
        print("No refund")
        return refund