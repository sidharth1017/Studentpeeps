
// async function Names(){
//     url="http://universities.hipolabs.com/search?country=india";

//     var response=await fetch(url);

//     var data=await response.json();

//     for(var i=0;i<data.length;i++){
 
//         var UniversityName=data[i]['name'];

//         var OptionItem=document.createElement('option');
//         OptionItem.appendChild(document.createTextNode(UniversityName));
//         OptionItem.setAttribute("value",UniversityName);
        
//         document.querySelector('datalist').appendChild(OptionItem);
//     }
// }

async function Names(){
    var Institution = [
        "Adamas University","AIHM Chandigarh","Alliance University","Amity University","Amity University Chhattisgarh","Amity University Gwalior (Madhya Pradesh)","Amity University Mumbai","Amity university, Noida","Anna University, Chennai","Aryabhatta College, University Of Delhi"
    ]
    for(var i=0;i<Institution.length;i++){
        console.log(Institution[i]);
        var INames =Institution[i];
        ul=document.createElement('ul');
           
        OptionItem.appendChild(document.createTextNode(INames));
        OptionItem.setAttribute("value",INames);
        document.querySelector('datalist').appendChild(OptionItem);
    }
}

// var Institution = [
//     "Adamas University","AIHM Chandigarh","Alliance University","Amity University","Amity University Chhattisgarh","Amity University Gwalior (Madhya Pradesh)","Amity University Mumbai","Amity university, Noida","Anna University, Chennai","Aryabhatta College, University Of Delhi"
// ]
// for(var i=0;i<Institution.length;i++){
//     console.log(Institution[i]);
//     var INames =Institution[i];    
//     OptionItem.appendChild(document.createTextNode(INames));
//     OptionItem.setAttribute("value",INames);
//     document.querySelector('datalist').appendChild(OptionItem);
// }



async function EmailVerify(){

    var emailValue=document.getElementById("exampleInputEmail1").value;
    
    var emailString=emailValue.toString();
    
    var afterSlice=emailString.split("@");
    
    var sliceValue=afterSlice[1];
    console.log(sliceValue)

    url="http://universities.hipolabs.com/search?country=india";

    var response=await fetch(url);

    var data=await response.json();

    for(var i=0;i<data.length;i++){

        var UniversityDomain=data[i]['domains'];
        if(UniversityDomain==sliceValue){
            var istrue = 'True';
            console.log("running");
            document.getElementById('check').value=sliceValue;
            
            return istrue;
        }
    }

}










// function Validate(){

//     var UniversityVerify=document.getElementById("exampleDataList").value;

//     var divBox=document.getElementById("verify");

//     // divBox.appendChild(document.createTextNode(" We require applicants of "+ UniversityVerify +"to use one of these school-issued email addresses to apply:- jecrcu.edu.in"));    

//     divBox.innerHTML=" We require applicants of "+ UniversityVerify +"to use one of these school-issued email addresses to apply:- jecrcu.edu.in";
// }