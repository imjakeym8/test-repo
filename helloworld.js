//This is a variable
let statement = 'Hello, ex';

// If i put another let statement, it would result to an error. So only put one
//let statement = 'Fuck you, ex';

//First JavaScript code
//console.log(statement);

//Pop up
alert("I love you, ex");

//Python equivalents:
// print(x) is the same as let x = 'name'; or var x ='name'; 
// Strings are also single-quoted 'Jakey', similar to Python;
// 
//
//
//
//

function addtwo(x) {
   return x + 2;
}


function today() {
   document.getElementById("last").innerHTML = Date();
 }

function currenttime() {
   document.getElementById("very-last").innerHTML = new Date().toLocaleString();
}
setInterval(currenttime, 1000);


