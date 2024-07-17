window.routes={"route_with_arg":"/<user_id>/","route_with_multiple_args":"/<account_id>/<user_id>/","route_with_typed_arg":"/<int:user_id>/","route_without_arg":"/","static":"/static/<path:filename>"};window.reverseUrl=function(urlName){let url=window.routes[urlName];if(!url){throw new Error("URL "+urlName+" was not found.");}
const args=arguments;const argTokens=url.match(/<(\w+:)?\w+>/g);if(!argTokens&&args[1]!==undefined){throw new Error("Invalid URL lookup: URL "+urlName+" does not expect any arguments.");}
if(typeof(args[1])=='object'&&!Array.isArray(args[1])){argTokens.forEach(function(token){let argName=token.slice(1,-1);if(argName.indexOf(':')>0){argName=argName.split(':')[1]}
const argValue=args[1][argName];if(argValue===undefined){throw new Error("Invalid URL lookup: Argument "+argName+" was not provided.");}
url=url.replace(token,argValue);});}else if(args[1]!==undefined){const argsArray=Array.isArray(args[1])?args[1]:Array.prototype.slice.apply(args,[1,args.length]);if(argTokens.length!==argsArray.length){throw new Error("Invalid URL lookup: Wrong number of arguments ; expected "+
argTokens.length.toString()+
" arguments.");}
argTokens.forEach(function(token,i){const argValue=argsArray[i];url=url.replace(token,argValue);});}
return url;};