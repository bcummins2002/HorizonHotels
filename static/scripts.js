//@author Ben Cummins
function checkinDate(){ //Function to check the date for checkin (Adapted from lecture slides)
    var checkin=Date.parse(document.getElementById("sdate").value);
    var checkin=new Date(checkin).setHours(0,0,0,0);
    var checkout=Date.parse(document.getElementById("edate").value);
    var checkout=new Date(checkout).setHours(0,0,0,0);
    var todaysdate=new Date();
    var maxDate=new Date();
    maxDate.setDate(maxDate.getDate()+90);
    if (checkin > checkout){
        alert('The check in date must be before the the check out date.')
        document.getElementById("sdate").value =new Date().setHours(0,0,0,0);
        return false;
    }
    else if (todaysdate > checkin) {
        alert('You check in date must be after today.')
        document.getElementById("sdate").value =new Date().setHours(0,0,0,0);
        return false;
    }
    else if(maxDate < checkin){
        alert('You cannot book more than 90 days in advance.');
        document.getElementById("sdate").value =new Date().setHours(0,0,0,0);
    }
    else{
        return true;
    }
}
function checkoutDate(){ //Function to check the date for checkot (Adapted from lecture slides)
    var checkin=Date.parse(document.getElementById("sdate").value);
    var checkin=new Date(checkin).setHours(0,0,0,0);
    var checkout=Date.parse(document.getElementById("edate").value);
    var checkout=new Date(checkout).setHours(0,0,0,0);
    var todaysdate=new Date();
    if (checkin > checkout)
    {
        alert('Checkout date must be after check in date.')
        document.getElementById("edate").value =new Date().setHours(0,0,0,0);
        return false;
    }
    else if (checkout < todaysdate)
    {
        alert('Checkout date must be after todays date.')
        document.getElementById("edate").value =new Date().setHours(0,0,0,0);
        return false;
    }
    else
    {
        return true;
    }
}
//Function to alert user of use of sessions
function sessions(){
    alert('This website uses sessions to store your data such as your email. By using this website you agree to us storing this data throughs sessions.');
    return true;
}
//Creating function to limit guests per room size
function guestsPerRoom(){
    var roomType=String(document.getElementById("roomtype").value);
    var noOfGuests=document.getElementById("noofguests").value;
    if (noOfGuests==0)
    {
        alert('At least one guest must stay in a room');
        return false;
    }
    if(roomType =="Standard" && noOfGuests >1)
    {
        alert('Only 1 guests maximum can stay in a standard room.');
        return false;
    }
    else if (roomType =="Double" && noOfGuests >2)
    {
        alert('Only 2 guests maximum can stay in a double room');
        return false;
    }
    else if (roomType=="Family" && noOfGuests > 6)
    {
        alert('Only 6 guests maximum can stay in a family room');
        return false;
    }
    else{
        return true;
    }
}
