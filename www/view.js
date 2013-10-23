console.log("js loaded... ");

$(document).ready(function () {
console.log("jquery ready... ");
    $('#input').validate({ // initialize the plugin
        rules: {
            email: {
                required: true,
                email: true
            },
            fullname: {
                required: true
            },
            homeurl: {
                required: true,
                url: true
            }
        }
    });

});


setInterval(function() { inputListener($('#email').val()); },100);


function inputListener(val){
    if(val) createNDNName(val);
}

function createNDNName(input){
   // input is email - ie, alexnano@remap.ucla.edu
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
            var cname = ""
            // reverse-concatenate any extra cnames
            for(var i=3;i==suffix.length;i++){
               cname += suffix[suffix.length-i];
               postname += "/"+suffix[suffix.length-i];
            }
            ndnname = prename + postname + "/" + user;
            // present to user
             $('#ndnname').html(ndnname);
             $('#ndn_name').val(ndnname);
             $('#nameinfo').show();
             if(cname!=""){
             //$('.group').val( cname +" at "+tld.match(/(.*).$/)[1]);
            } else{
             //$('.group').val(tld.match(/(.*).$/)[1]);
            }
        }
    }

}
