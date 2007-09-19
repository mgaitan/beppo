function isEmailAddress(theElement)
{
var s = theElement.value;
var filter=/^[A-Za-z][A-Za-z0-9_.]*@[A-Za-z0-9_]+\.[A-Za-z0-9_.]+[A-za-z]$/;
// si el campo está vacio (como es requerido) se solicita completarlo y no se muestra 'error de email'
if (s.length == 0 ) return true; 
if (filter.test(s)){
return true;
}else{
return false;
}
}
