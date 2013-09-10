console.log("js loaded... ");


setInterval(function() { inputListener($('.email').val()); },100);


function inputListener(val){
    //console.log("val is "+val);
    if(val) createNDNName(val);
}

function createNDNName(input){
    
    // alexnano@remap.ucla.edu
    
    var input = input;
    var user = ""
    var tld = ""
    var ndnname = ""
    if(input){
        if((input.split("@").length>1) && (input.split("@")[1]!=="")){
            // cool, there is an '@'
            // [alex] [remap.ucla.edu]
            // assign the name
            user = input.split("@")[0];
            // [alex]
        
            // now tld
            suffix = (input.split("@")[1]).split(".");
        
            if(suffix[suffix.length-2]!=undefined){
                   tld = suffix[suffix.length-2]+"."
            }
            
            dot3 = suffix[suffix.length-1]
        
            var prename = "/ndn/"+tld+dot3
            var postname = ""
        
            // reverse-concatenate any extra cnames
        
            for(var i=3;i==suffix.length;i++){
               postname += "/"+suffix[suffix.length-i];
            }
        
            ndnname = prename + postname + "/" + user;
        
             $('#ndnname').html(ndnname);
             $('#ndn_name').val(ndnname);
             $('#nameinfo').show();
           
        }
    }

}
